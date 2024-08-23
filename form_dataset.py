import json

file_path = "clean_data.json"
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
                    "content": f'你現在是我的造型師。請你根據這件上衣的描述：{item['top']}，還有我這個人的一些資訊：{item['model_info']}，推薦我與之搭配的下身，請仿照以下範例格式：\
{{\
"顏色": "黑色",\
"服裝類型": "寬鬆長褲",\
"剪裁版型": "寬鬆剪裁",\
"設計特點": "高腰",\
"材質": "棉質或混紡面料",\
"配件": "無",\
"細節": "無",\
"褲管": "直筒褲管",\
"裙擺": "無"\
}}',
                },
                {
                    "role": "assistant",
                    "content": f'{item['bottom']}'
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
                    "content": f'你現在是我的造型師。請你根據這件下身的描述：{item['bottom']}，還有我這個人的一些資訊：{item['model_info']}，推薦我與之搭配得上衣，請仿照以下範例格式：\
{{\
"顏色": "黑色",\
"服裝類型": "高領毛衣",\
"剪裁版型": "貼身剪裁",\
"設計特點": "無花紋",\
"材質": "針織",\
"配件": "無",\
"細節": "無",\
"領子": "高領",\
"袖子": "長袖"\
}}',\
                },
                {
                    "role": "assistant",
                    "content": f'{item['top']}'
                }
            ]
        }
    )


# 保存訓練數據為 training_data.jsonl
with open("training_data.jsonl", "w", encoding="utf-8") as f:
    for entry in training_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("Training data has been generated and saved to 'training_data.jsonl'")
