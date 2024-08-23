import json

# Load the JSON data
with open('formatted_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Process the data
for entry in data:
    # Remove "配件" from "top" and "bottom"
    if "top" in entry and "配件" in entry["top"]:
        del entry["top"]["配件"]
    if "bottom" in entry and "配件" in entry["bottom"]:
        del entry["bottom"]["配件"]

    # Rename keys and consolidate them into "model_info"
    entry["model_info"] = entry.pop("model")
    entry["model_info"]["髮型自述"] = entry.pop("model_description", None)
    entry["model_info"]["身高"] = entry.pop("height", None)
    entry["model_info"]["性別"] = entry.pop("gender", None)
    entry["model_info"]["年紀"] = entry.pop("age", None)

# Save the modified data back to JSON
with open('clean_data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Task completed, and data saved to clean_data.json.")
