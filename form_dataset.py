import json

# 從 data.json 讀取數據
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

training_data = []

for item in data:
    common_info = f"性別: {item['gender']}, 身高: {
        item['height']}, 風格: {item['profile']}, 模特: {item['model']}"

    # 已知上半身，推薦下半身
    training_data.append({
        "prompt": f"{common_info}, 上衣: {item['upper']}",
        "completion": f"下身: {item['lower']}"
    })
    # 已知上半身，推薦鞋子
    training_data.append({
        "prompt": f"{common_info}, 上衣: {item['upper']}",
        "completion": f"鞋子: {item['shoes']}"
    })
    # 已知下半身，推薦上半身
    training_data.append({
        "prompt": f"{common_info}, 下身: {item['lower']}",
        "completion": f"上衣: {item['upper']}"
    })
    # 已知下半身，推薦鞋子
    training_data.append({
        "prompt": f"{common_info}, 下身: {item['lower']}",
        "completion": f"鞋子: {item['shoes']}"
    })
    # 已知鞋子，推薦上半身
    training_data.append({
        "prompt": f"{common_info}, 鞋子: {item['shoes']}",
        "completion": f"上衣: {item['upper']}"
    })
    # 已知鞋子，推薦下半身
    training_data.append({
        "prompt": f"{common_info}, 鞋子: {item['shoes']}",
        "completion": f"下身: {item['lower']}"
    })

# 保存訓練數據為 training_data.jsonl
with open('training_data.jsonl', 'w', encoding='utf-8') as f:
    for entry in training_data:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print("Training data has been generated and saved to 'training_data.jsonl'")
