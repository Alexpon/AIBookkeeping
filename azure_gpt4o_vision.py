import os
import base64
from typing import List, Dict, Any
from openai import AzureOpenAI


def _file_to_data_url(file_path: str) -> str:
    """Return a data URL for the given file."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        mime = "application/pdf"
    elif ext in {".jpg", ".jpeg"}:
        mime = "image/jpeg"
    else:
        mime = "image/png"

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def analyze_file_with_gpt4o(file_path: str, prompt: str) -> str:
    """Send a file (image or PDF) to GPT-4o and return the text response."""
    data_url = _file_to_data_url(file_path)

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-05-13",  # API version supporting GPT-4o
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    deployment = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT", "gpt-4o")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]

    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
    )

    return response.choices[0].message.content


def analyze_image_with_gpt4o(image_path: str, prompt: str = "Describe this image:") -> str:
    """Analyze an image with Azure OpenAI GPT-4o and return the textual response.

    The function expects the following environment variables to be set:
    - AZURE_OPENAI_API_KEY: API key for your Azure OpenAI resource.
    - AZURE_OPENAI_ENDPOINT: Endpoint URL for your Azure OpenAI resource.
    - AZURE_OPENAI_GPT4O_DEPLOYMENT: (optional) Name of your GPT-4o deployment. Defaults to "gpt-4o".

    Parameters
    ----------
    image_path: str
        Path to the image file to analyze.
    prompt: str, optional
        Text prompt to send along with the image. Defaults to "Describe this image:".
    Returns
    -------
    str
        The GPT-4o textual response describing the image.
    """
    return analyze_file_with_gpt4o(image_path, prompt)


def extract_transactions_from_statement(file_path: str) -> str:
    """Extract credit card transactions using GPT-4o.

    The function accepts an image or PDF of a credit card statement and returns
    GPT-4o's response. The model is prompted to list each transaction with
    date, amount, item and details in JSON format.
    """

    prompt = (
        "Please read the attached credit card statement and return a JSON array "
        "of transactions. Each transaction should have the fields 'date', "
        "'amount', 'item' and 'detail'."
    )

    return analyze_file_with_gpt4o(file_path, prompt)
