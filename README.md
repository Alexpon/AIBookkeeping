# AIBookkeeping

This repository contains utilities related to AI bookkeeping.

## Azure GPT-4o Vision Example

The file `azure_gpt4o_vision.py` defines helper functions for interacting with an
Azure OpenAI GPT-4o deployment.

- `analyze_image_with_gpt4o` – send an image to GPT‑4o
- `extract_transactions_from_statement` – send an image or PDF of a credit card
  statement and receive the extracted transactions in JSON format

### Requirements
- Python 3.8+
- The `openai` Python package
- An Azure OpenAI resource with a GPT-4o deployment

Environment variables expected by the script:
- `AZURE_OPENAI_API_KEY` – your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` – the endpoint URL for your Azure OpenAI resource
- `AZURE_OPENAI_GPT4O_DEPLOYMENT` – *(optional)* name of your GPT-4o deployment. Defaults to `gpt-4o`.

### Example Usage
```python
from azure_gpt4o_vision import analyze_image_with_gpt4o, extract_transactions_from_statement

result = analyze_image_with_gpt4o("path/to/image.png", prompt="What's in this image?")
print(result)

# Extract transactions from a statement
transactions = extract_transactions_from_statement("statement.pdf")
print(transactions)
```
