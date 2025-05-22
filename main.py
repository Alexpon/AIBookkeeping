import os
import io
import glob
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd
from pdf2image import convert_from_path


def get_file_list():
    billing_dir = 'billing'
    supported_exts = ['.pdf', '.png', '.jpg', '.jpeg']
    files = []
    for ext in supported_exts:
        files.extend(glob.glob(os.path.join(billing_dir, f'*{ext}')))
    return files


def encode_image_to_base64(image):
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def call_gpt4o_vision(client, prompt, image_b64):
    from schema import TransactionRecords
    response = client.beta.chat.completions.parse(
        model=os.getenv('AZURE_OPENAI_DEPLOYMENT'),
        messages=[
            {"role": "system", "content": "你是一個專業的財務記帳助理。"},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]}
        ],
        temperature=0.1,
        max_tokens=1500,
        response_format=TransactionRecords
    )
    return response.choices[0].message.parsed


def gpt4o_extract_records(file_path, client):
    prompt = (
        "請根據上傳的帳單或銀行交易紀錄圖片，抽取所有消費、交易、轉帳紀錄，格式如下：\n"
        "[\n  {\"date\": \"YYYY-MM-DD\", \"description\": \"消費明細\", \"amount\": 金額, \"type\": \"消費|交易|轉帳\"}\n]\n"
        "請務必以JSON array格式回傳，不要有多餘說明。日期請用YYYY-MM-DD格式。若無法辨識請回傳空array。"
    )
    ext = os.path.splitext(file_path)[1].lower()
    all_records = []
    try:
        if ext == '.pdf':
            images = convert_from_path(file_path, fmt='png', thread_count=4)[:10]
            for img in images:
                file_b64 = encode_image_to_base64(img)
                response = call_gpt4o_vision(client, prompt, file_b64)
                all_records.extend(response)
        else:
            from PIL import Image
            img = Image.open(file_path)
            file_b64 = encode_image_to_base64(img)
            response = call_gpt4o_vision(client, prompt, file_b64)
            all_records.extend(response)
    except Exception as e:
        print(f"處理檔案 {file_path} 時發生錯誤: {str(e)}")
    return all_records


def records_to_dataframe(records):
    all_dicts = []
    for tup in records:
        if isinstance(tup, tuple) and tup[0] == 'records':
            for rec in tup[1]:
                if hasattr(rec, 'model_dump'):
                    all_dicts.append(rec.model_dump())
                elif hasattr(rec, 'dict'):
                    all_dicts.append(rec.dict())
                elif isinstance(rec, dict):
                    all_dicts.append(rec)
    columns = ["date", "description", "amount", "type", "category"]
    df = pd.DataFrame([{k: d.get(k, None) for k in columns} for d in all_dicts])
    return df


def main():
    load_dotenv()
    client = AzureOpenAI(
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    )
    files = get_file_list()
    all_records = []
    for file_path in files:
        print(f"處理檔案: {file_path}")
        records = gpt4o_extract_records(file_path, client)
        all_records.extend(records)
    if all_records:
        df = records_to_dataframe(all_records)
        df.to_csv('output.csv', index=False)
        print(f"已儲存 {len(df)} 筆紀錄到 output.csv")
    else:
        print("沒有抽取到任何紀錄。")


if __name__ == "__main__":
    main()
