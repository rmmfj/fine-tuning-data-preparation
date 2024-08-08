import json

file_path = "prompt1_processed_data.json"
# 從 data.json 讀取數據
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

training_data = []

for item in data:

    # common_info = f"性別: {item['gender']}, 身高: {item['height']} cm, 模特: {item['tags']['模特']}"
    # print("common_info:", common_info)

    # 已知上半身，推薦下半身
    training_data.append(
        {
            "messages": [
                {
                    "role": "system",
                    "content": "This is a chatbot born to be a stylist",
                },
                {
                    "role": "user",
                    "content": f'你現在是我的造型師。請你根據這件上衣的描述：{item['tags']['上半身']}，推薦我與之搭配的下身，請仿照以下格式，回答無需包含其他資訊："顏色:[顏色], 服裝類型:[類型], 剪裁版型:[描述], 設計特點:[描述], 材質:[材質], 配件:[描述]（無的話可略）, 細節:[描述], 褲管:[描述]"',
                },
                {
                    "role": "assistant",
                    "content": f"{item['tags']['下半身']}"
                }
            ]
        }
    )
    # 已知下半身，推薦上半身
    training_data.append(
                {
            "messages": [
                {
                    "role": "system",
                    "content": "This is a chatbot born to be a stylist",
                },
                {
                    "role": "user",
                    "content": f'你現在是我的造型師。請你根據這件下身的描述：{item['tags']['下半身']}，推薦我與之搭配的上衣，請仿照以下格式，回答無需包含其他資訊："顏色:[顏色], 服裝類型:[類型], 剪裁版型:[描述], 設計特點:[描述], 材質:[材質], 配件:[描述]（無的話可略）, 細節:[描述], 領子:[描述], 袖子:[描述]"',
                },
                {
                    "role": "assistant",
                    "content": f"{item['tags']['下半身']}"
                }
            ]
        }
    )


# 保存訓練數據為 training_data.jsonl
with open("training_data.jsonl", "w", encoding="utf-8") as f:
    for entry in training_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("Training data has been generated and saved to 'training_data.jsonl'")
