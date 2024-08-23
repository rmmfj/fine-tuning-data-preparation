import json
import os
import re

import openai
from dotenv import load_dotenv
from tqdm import tqdm

# 載入 .env 文件中的環境變量
load_dotenv()

# 從環境變量中獲取 OpenAI API 金鑰
api_key = os.getenv("OPEN_API_KEY")

# 設置您的OpenAI API密鑰
client = openai.OpenAI(api_key=api_key)


def preprocess_and_parse_json(json_string):
    # 移除可能的前綴（如 "json", "JSON:", "```json" 等）
    json_string = re.sub(
        r"^(json|JSON:?|```json?)\s*", "", json_string, flags=re.IGNORECASE
    )

    # 移除可能的後綴（如 "```"）
    json_string = re.sub(r"\s*```$", "", json_string)

    # 嘗試找到 JSON 對象的開始和結束
    match = re.search(r"\{.*\}", json_string, re.DOTALL)
    if match:
        json_string = match.group(0)

    # 移除多餘的轉義字符
    json_string = json_string.replace("\\n", "\n").replace('\\"', '"')

    # 移除註釋（如果有的話）
    json_string = re.sub(r"//.*?\n|/\*.*?\*/", "", json_string, flags=re.DOTALL)

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
    required_keys = ["model", "top", "bottom"]
    return all(key in tags for key in required_keys)


def generate_tags(image_url):
    prompt = """
    仔細觀察我的這張圖片，精確且細膩地提供一個詳細的 multi-tags 列表來描述我的特徵，我想跟我的朋友介紹我。
    確保涵蓋每一個細節，包括顏色、材質、設計、功能和搭配。每類 tag 可有多個以涵蓋所有細節。
    回覆時按以下格式分別描述 model、top、bottom，不可包含多餘內容。
    請使用下方 JSON 格式，如有無法辨識的標籤，可以回答無法辨識。
    可以參考以下範例：
    {
        "model": {
            "膚色": "中等膚色"
            "種族": "不明"
            "髮型": "短髮，側邊略微梳向一邊"
            "髮色": "深色"
            "身材": "中等身材"
            "面部特徵": "有著整齊的胡子，友善的笑容"
        },
        "top": {
            "顏色": "藍色",
            "服裝類型": "襯衫",
            "剪裁版型": "修身剪裁",
            "設計特點": "有口袋",
            "材質": "羊毛混紡",
            "配件": "無",
            "細節": "有條紋",
            "領子": "翻領",
            "袖子": "長袖"
        },
        "bottom": {
            "顏色": "黑色",
            "服裝類型": "長褲",
            "剪裁版型": "寬鬆剪裁",
            "設計特點": "高腰",
            "材質": "可能為棉質或混紡面料",
            "配件": "無",
            "細節": "有褶皺設計",
            "褲管": "緊縮褲腳",
            "裙擺": "無"
        }
    }
    """
    try:
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
            max_tokens=500,
        )
        tags_string = response.choices[0].message.content
        tags = preprocess_and_parse_json(tags_string)
        print("tags_string:\n", tags_string)
        print("tags:\n", tags)
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
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_processed_data(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    input_file = "failed_2.json"
    output_file = "vision.json"
    failed_file = "failed_3.json"
    # input_file = "scraped.json"
    # output_file = "vision.json"
    # failed_file = "failed.json"
    batch_size = 10  # 每10張圖片保存一次

    # 讀取原始數據
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 加載已處理的數據
    processed_data = load_processed_data(output_file)
    failed_data_3 = load_processed_data(failed_file)

    # 找出尚未處理的項目
    processed_urls = set(item["image_url"] for item in processed_data)
    to_process = [item for item in data if item["image_url"] not in processed_urls]
    failed_process = []

    # 處理每個未處理的項目
    for i, item in enumerate(tqdm(to_process, desc="Processing images"), 1):
        new_item = item.copy()  # 創建原始項目的副本
        image_url = new_item["image_url"]
        tags = generate_tags(image_url)

        if tags:
            new_item["tags"] = tags
            processed_data.append(new_item)
        else:
            print(f"無法為圖片生成有效標籤: {image_url}")
            new_item["tags"] = None
            failed_process.append(new_item)


        # 每處理完 batch_size 個項目就保存一次
        if i % batch_size == 0:
            save_processed_data(processed_data, output_file)
            save_processed_data(failed_process, failed_file)
            print(f"已處理 {i} 張圖片，數據已保存")

    # 處理完所有項目後，再保存一次以確保所有數據都被保存
    if len(to_process) % batch_size != 0:
        save_processed_data(processed_data, output_file)
        save_processed_data(failed_process, failed_file)

    print(
        f"處理完成。共處理 {len(to_process)} 個新項目。最終數據已保存到 {output_file}"
    )


if __name__ == "__main__":
    main()
