import json
import os
import re

import openai
from dotenv import load_dotenv
from tqdm import tqdm

# 載入 .env 文件中的環境變量
load_dotenv()

# 從環境變量中獲取 OpenAI API 金鑰
api_key = os.getenv('OPENAI_API_KEY')
# 設置您的OpenAI API密鑰
client = openai.OpenAI(
    api_key=api_key)

def preprocess_and_parse_json(json_string):
    # 移除可能的前綴（如 "json", "JSON:", "```json" 等）
    json_string = re.sub(r'^(json|JSON:?|```json?)\s*', '',
                         json_string, flags=re.IGNORECASE)

    # 移除可能的後綴（如 "```"）
    json_string = re.sub(r'\s*```$', '', json_string)

    # 嘗試找到 JSON 對象的開始和結束
    match = re.search(r'\{.*\}', json_string, re.DOTALL)
    if match:
        json_string = match.group(0)

    # 移除多餘的轉義字符
    json_string = json_string.replace('\\n', '\n').replace('\\"', '"')

    # 移除註釋（如果有的話）
    json_string = re.sub(r'//.*?\n|/\*.*?\*/', '',
                         json_string, flags=re.DOTALL)

    # 解析 JSON
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        print(f"問題字符串: {json_string}")
        return None


def validate_tags(tags):
    if not isinstance(tags, dict):
        return False
    required_keys = ["模特", "上半身", "下半身"]
    return all(key in tags for key in required_keys)

prompt1 = """
仔細觀察這張圖片中的人物，精確且細膩地描述他的外貌和穿著的所有服飾及配件，提供一個詳細的 multi-tags 列表。確保涵蓋每一個細節，包括顏色、材質、設計、功能和搭配。每類 tag 可有多個以涵蓋所有細節。回覆時按以下格式分別描述模特、上半身、下半身，不可包含多餘內容。
json
{
    "模特": "膚色:顏色, 種族:類型, 髮型:描述, 髮色:描述, 身材:描述, 面部特徵:描述, 其他特徵:描述，如無法識別則回答無法識別",
    "上半身": "顏色:顏色, 服裝類型:類型, 剪裁版型: 描述, 設計特點:描述, 材質:材質, 細節:描述, 領子:描述, 袖子:描述",
    "下半身": "顏色:顏色, 服裝類型:類型, 剪裁版型: 描述, 設計特點:描述, 材質:材質, 細節:描述, 褲管:描述"
}
"""

prompt2 = """
仔細觀察這張圖片中的人物，精確且細膩地描述他的外貌和穿著的所有服飾及配件，提供一個詳細的 multi-tags 列表。確保涵蓋每一個細節，包括顏色、材質、設計、功能和搭配等等。可以使用多個 tag 以涵蓋所有細節。回覆時按以下格式分別描述模特、上半身、下半身，不必包含多餘內容。
json
{
    "模特": "描述",
    "上半身": "描述",
    "下半身": "描述"
}
"""

prompt2_1 = """
仔細觀察這張圖片中的人物，精確且細膩地描述他的外貌和穿著的所有服飾及配件，提供一個詳細的 multi-tags 列表。確保涵蓋每一個細節，包括顏色、材質、設計、功能和搭配等等。可以使用多個 tag 以涵蓋所有細節。回覆時按以下格式分別描述模特、上半身、下半身，不必包含多餘內容。
json
{
    "模特": "對模特的性別、膚色、身材、身形比例、氣質等方面進行描述",
    "上半身": "描述上半身穿著",
    "下半身": "描述下半身穿著，不需包含鞋子"
}
"""

prompt3 = """
仔細觀察這張圖片中的人物，精確且細膩地描述他的外貌和穿著的所有服飾，提供一個詳細的 multi-tags 列表。確保涵蓋每一個細節，包括顏色、材質、設計、功能和搭配等等。可以使用多個 tag 以涵蓋所有細節。回覆時按以下格式分別描述模特、上半身服飾、下半身服飾，不必包含多餘內容。
json
{
    "模特": "對模特的性別、膚色、身材、身形比例、氣質等方面進行描述，請使用繁體中文，並用半形逗號隔開（無法識別的話請回答無法識別），例如：皮膚白皙, 身材微胖",
    "上半身": "描述上半身服飾的 multi-tags，請使用繁體中文，並用半形逗號隔開，例如：顏色:顏色, 服裝類型:類型, 設計特點:描述, 材質:材質, 領子:類型, 袖長:描述, 細節:其他描述,
    "下半身": "描述下半身服飾的 multi-tags，請使用繁體中文，並用半形逗號隔開，不需包含鞋子，例如：顏色:淺米色, 服裝類型:寬鬆工裝褲, 材質:混紡棉, 設計:多口袋風格, 細節:口袋位置偏側、帶有一條橙色鏈條裝飾"
}
"""


def generate_tags(image_url, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=300
        )
        tags_string = response.choices[0].message.content
        print("tags_string =", tags_string)
        tags = preprocess_and_parse_json(tags_string)

        if tags and validate_tags(tags):
            return tags
        else:
            print(f"生成的標籤無效或格式不正確: {tags_string}")
            return None
    except Exception as e:
        print(f"生成標籤時發生錯誤: {e}")
        return None


def load_processed_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_processed_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main(prompt, prompt_name):
    print("Your project api key is", api_key)
    print("The tested prompt is", prompt)
    input_file = 'cleansed_output.json'
    output_file = f'{prompt_name}_processed_data.json'
    batch_size = 10  # 每10張圖片保存一次

    # 讀取原始數據
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 加載已處理的數據
    processed_data = load_processed_data(output_file)

    # 找出尚未處理的項目
    processed_urls = set(item['image_url'] for item in processed_data)
    to_process = [item for item in data if item['image_url']
                  not in processed_urls]

    # 處理每個未處理的項目
    for i, item in enumerate(tqdm(to_process, desc="Processing images"), 1):
        new_item = item.copy()  # 創建原始項目的副本
        image_url = new_item['image_url']
        print(image_url)
        tags = generate_tags(image_url=image_url, prompt=prompt)

        if tags:
            new_item['tags'] = tags
        else:
            print(f"無法為圖片生成有效標籤: {image_url}")
            tags = generate_tags(image_url=image_url, prompt=prompt)
            if tags:
                new_item['tags'] = tags
                print("Second attempt to generate tags successful")
            else:
                new_item['tags'] = None
                print("Second attempt to generate tags failed")

        processed_data.append(new_item)

        # 每處理完 batch_size 個項目就保存一次
        if i % batch_size == 0:
            save_processed_data(processed_data, output_file)
            print(f"已處理 {i} 張圖片，數據已保存")

    # 處理完所有項目後，再保存一次以確保所有數據都被保存
    if len(to_process) % batch_size != 0:
        save_processed_data(processed_data, output_file)

    print(f"處理完成。共處理 {len(to_process)} 個新項目。最終數據已保存到 {output_file}")


if __name__ == "__main__":
    main(prompt=prompt1, prompt_name="prompt1")
    # main(prompt=prompt3_1, prompt_name="prompt3_1")
