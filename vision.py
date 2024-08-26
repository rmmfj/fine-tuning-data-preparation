import pandas as pd
import openai
from tqdm import tqdm
import json
from dotenv import load_dotenv
import os
import re
import ast
import csv
from IPython.display import display

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Set your OpenAI API key
client = openai.OpenAI(api_key=api_key)


def make_prompt_for_image_labeling(clothing_type: str, gender: str) -> str:
    gender_description = ("男性" if gender == "man" else "女性") if gender else ""
    prompt = f"""
    仔細觀察這張圖片中的{gender_description}{'上衣' if clothing_type == 'top' else '下身'}後，提供一個詳細的 multi-tags 列表來描述這件衣物。
    確保涵蓋每一個細節，包括顏色、材質、設計、功能等。
    每類可有多個標籤以涵蓋所有細節。需要的話，你可以使用規範以外的標籤來完成你的任務。
    請使用下方 JSON 格式回覆，回答無需包含其他資訊：
    {{
      "顏色": "[顏色]",
      "服裝類型": "[類型]",
      "剪裁版型": "[描述]",
      "設計特點": "[描述]",
      "材質": "[材質]",
      "細節": "[描述]",
      {', '.join(['"領子": "[描述]", "袖子": "[描述]"'] if clothing_type == 'top' else ['"褲管": "[描述]", "裙擺": "[描述]"'])}
    }}
    
    可以參考以下範例：
    範例一：
    {{
      "顏色": "藍色",
      "服裝類型": "襯衫",
      "剪裁版型": "修身剪裁",
      "設計特點": "有口袋",
      "材質": "羊毛混紡",
      "細節": "有條紋",
      "領子": "翻領",
      "袖子": "長袖"
    }}
    範例二：
    {{
      "顏色": "黑色",
      "服裝類型": "長褲",
      "剪裁版型": "寬鬆剪裁",
      "設計特點": "高腰",
      "材質": "可能為棉質或混紡面料",
      "細節": "有褶皺設計",
      "褲管": "緊縮褲腳",
      "裙擺": "無"
    }}
    """
    return prompt


def json_to_string(json_string: str) -> dict:
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


def format_dict_string(dict_obj: dict) -> str:
    """Convert a dictionary to a formatted string."""
    try:
        if isinstance(dict_obj, dict):
            # Format the dictionary into the desired string
            return ", ".join(f"{key}: {value}" for key, value in dict_obj.items())
        else:
            raise ValueError("Input is not a dictionary")
    except (SyntaxError, ValueError) as e:
        print(f"Error: {e}")
        return "Invalid input"


def generate_label_string(prompt: str, image_url: str):

    try:
        # Make a request to OpenAI API for every row
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
        label_string = response.choices[0].message.content
        label_string_dict = json_to_string(label_string)
        print("Label String:", label_string_dict)

        # Convert the JSON-like response to the desired string format
        label_string_formatted = format_dict_string(label_string_dict)
        print("Formatted Label String:", label_string_formatted)
        return label_string_formatted

    except openai.OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return None


# File paths
items_file = "/Users/chenyuhan/Downloads/codingdata/item.csv"
series_file = "/Users/chenyuhan/Downloads/codingdata/series.csv"
item_to_series_file = "/Users/chenyuhan/Downloads/codingdata/item_to_series.csv"
output_file = "/Users/chenyuhan/Downloads/codingdata/items_with_label_2.csv"
failed_file = "/Users/chenyuhan/Downloads/codingdata/failed_items.csv"
processed_file = "/Users/chenyuhan/Downloads/codingdata/processed_items.txt"


def main():

    # Load processed item IDs
    if os.path.exists(processed_file):
        print("processed file already exists.")
        with open(processed_file, "r", encoding="utf-8") as f:
            processed_ids = set(line.strip() for line in f)
    else:
        processed_ids = set()

    # Open the output CSV file in write mode and write the header
    with open(output_file, "w", encoding="utf-8", newline="") as f_output, open(failed_file, "w", encoding="utf-8", newline="") as failed_output:
        writer = csv.writer(f_output)
        writer.writerow(["item_id", "image_url", "label_string", "color"])
        failed_writer = csv.writer(failed_output)
        failed_writer.writerow(["item_id", "image_url", "color"])

        # Load the series data and item_to_series data into memory
        series_df = pd.read_csv(series_file)
        item_to_series_df = pd.read_csv(item_to_series_file)

        # Determine the total number of rows to process
        total_rows = sum(1 for _ in open(items_file)) - 1  # Subtract 1 for the header

        # Process items.csv in chunks
        chunk_size = 50  # Adjust this size based on memory and performance needs

        for items_chunk in pd.read_csv(items_file, chunksize=chunk_size):
            rows_to_save = []  # Buffer to hold rows before saving
            failed = []
            # Perform the merge operation
            merged_chunk = pd.merge(
                item_to_series_df, items_chunk, on="item_id", how="right"
            )
            print("number of items processing:", merged_chunk.shape[0])
            merged_chunk = pd.merge(merged_chunk, series_df, on="series_id", how="left")
            print("number of items processing:", merged_chunk.shape[0])

            # Handle missing data
            merged_chunk.fillna(
                {"clothing_type": "unknown", "gender": "unknown"}, inplace=True
            )

            # Generate prompts for each row in the chunk with progress bar
            for i, row in tqdm(
                merged_chunk.iterrows(),
                total=len(merged_chunk),
                desc="Processing items",
                unit="item",
            ):
                item_id = row["item_id"]
                image_url = row["image_url"]
                color = row["color"]
                clothing_type = row["clothing_type"]
                gender = row["gender"]

                if item_id in processed_ids:
                    continue

                prompt = make_prompt_for_image_labeling(clothing_type, gender)
                print("Image URL:", image_url)

                label_string_formatted = generate_label_string(prompt, image_url)

                if label_string_formatted:
                    # Accumulate the results
                    rows_to_save.append(
                        [item_id, image_url, label_string_formatted, color]
                    )
                else:
                    failed.append(
                        [item_id, image_url, color]
                    )

                # Mark item_id as processed
                processed_ids.add(item_id)
                # Save to the output file every 10 rows
                if (i + 1) % 10 == 0:
                    writer.writerows(rows_to_save)
                    rows_to_save = []  # Clear the buffer
                    failed_writer.writerow(failed)
                    failed = []
                    # Save the processed IDs
                    with open(processed_file, "a", encoding="utf-8") as f:
                        f.write("\n".join(processed_ids) + "\n")
                    processed_ids = set()

            # After processing a chunk, check if there are any remaining rows to save
            if rows_to_save:
                writer.writerows(rows_to_save)
            if failed:
                failed_writer.writerows(failed)
            with open(processed_file, "a", encoding="utf-8") as f:
                f.write("\n".join(processed_ids) + "\n")
                processed_ids = set()

    print(f"Results saved to {output_file}")

def generate_remains():
    with open(output_file, "w", encoding="utf-8", newline="") as f_output, open(
        failed_file, "w", encoding="utf-8", newline=""
    ) as failed_output:
        writer = csv.writer(f_output)
        writer.writerow(["item_id", "image_url", "label_string", "color"])
        failed_writer = csv.writer(failed_output)
        failed_writer.writerow(["item_id", "image_url", "color"])

        # Load the series data and item_to_series data into memory
        series_df = pd.read_csv(series_file)
        item_to_series_df = pd.read_csv(item_to_series_file)
        all_items = pd.read_csv(items_file)
        items_with_label = pd.read_csv("/Users/chenyuhan/Downloads/codingdata/items_with_label.csv")
        processed_ids = items_with_label["item_id"]
        undealt_items = all_items[~all_items["item_id"].isin(processed_ids)]
        
        # return display(undealt_items)
        merged_chunk = pd.merge(
            item_to_series_df, undealt_items, on="item_id", how="right"
        )
        print("number of items processing:", merged_chunk.shape[0])
        merged_chunk = pd.merge(merged_chunk, series_df, on="series_id", how="left")
        print("number of items processing:", merged_chunk.shape[0])

        # Handle missing data
        merged_chunk.fillna(
            {"clothing_type": "unknown", "gender": "unknown"}, inplace=True
        )
        
        rows_to_save = []
        for index, row in merged_chunk.iterrows():
            item_id = row["item_id"]
            image_url = row["image_url"]
            color = row["color"]
            clothing_type = row["clothing_type"]
            gender = row["gender"]
            prompt = make_prompt_for_image_labeling(gender=gender, clothing_type=clothing_type)
            label_string_formatted = generate_label_string(image_url=image_url, prompt=prompt)
            rows_to_save.append([item_id, image_url, label_string_formatted, color])
        writer.writerows(rows_to_save)
        return

if __name__ == "__main__":
    # main()
    generate_remains()
