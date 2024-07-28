import json

file_path = "prompt2_1_processed_data.json"
# 從 data.json 讀取數據
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

training_data = []

for item in data:
    common_info = f"性別: {item['gender']}, 身高: {item['height']} cm, 模特: {item['tags']['模特']}"
    print("common_info:", common_info)

    # 已知上半身，推薦下半身
    training_data.append({
        "prompt": f"{common_info}, 上衣: {item['tags']['上半身']}",
        "completion": f"下身: {item['tags']['下半身']}"
    })
    # 已知下半身，推薦上半身
    training_data.append({
        "prompt": f"{common_info}, 下身: {item['tags']['下半身']}",
        "completion": f"上衣: {item['tags']['上半身']}"
    })


# 保存訓練數據為 training_data.jsonl
with open('training_data.jsonl', 'w', encoding='utf-8') as f:
    for entry in training_data:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print("Training data has been generated and saved to 'training_data.jsonl'")
