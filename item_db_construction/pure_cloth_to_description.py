import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
import pandas as pd

# Initialize the OpenAI client with your API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

prompt = """
仔細觀察這張圖片中的衣物，首先請你先判斷屬於上身還是下身衣物。
接下來，精確且細膩地描述，提供一個詳細的 multi-tags 列表。確保涵蓋每一個細節，包括顏色、材質、設計、功能等。每類可有多個標籤以涵蓋所有細節。需要的話，你可以使用規範以外的標籤來完成你的任務。
如果是上衣，請仿造下方格式回覆：
json {
    "clothing_type": "top",
    "description": "顏色:顏色, 服裝類型:類型, 剪裁版型: 描述, 設計特點:描述, 材質:材質, 細節:描述, 領子:描述, 袖子:描述"
}
反之，如果是下身，請仿造下方格式回覆：
json {
    "clothing_type": "bottom", 
    "description": "顏色:顏色, 服裝類型:類型, 剪裁版型: 描述, 設計特點:描述, 材質:材質, 細節:描述, 褲管:描述"
}
"""


def analyze_image(image_url):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    file_path = "/Users/chenyuhan/Downloads/tops.csv"
    df = pd.read_csv(file_path)
    image_urls = df["image_urls"]

    descriptions = []
    for url in tqdm(image_urls, desc="Processing images"):
        print(url)
        description = analyze_image(url)
        print(description)
        descriptions.append(description)

    df["descriptions"] = descriptions
    file_name = os.path.basename(file_path)
    clean_file_name = os.path.splitext(file_name)[0]
    df.to_csv(f"{clean_file_name}_descriptions.csv", index=False)
