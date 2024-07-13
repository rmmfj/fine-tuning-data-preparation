import json

# Load data from output.json
with open('output.json', 'r', encoding='utf-8') as infile:
    data_a = json.load(infile)

# cleanse function


def cleanse(data):
    cleansed_data = []
    for item in data:
        cleanseed_item = {
            "image_url": "http:" + item["image_url"],
            "gender": item["gender"],
            "height": int(item["height"]) if item["height"] else None,
            "bio": item["bio"]
        }
        cleansed_data.append(cleanseed_item)
    return cleansed_data


# cleanse the data
data_b = cleanse(data_a)

# Save the cleanseed data to cleanseed_output.json
with open('cleanseed_output.json', 'w', encoding='utf-8') as outfile:
    json.dump(data_b, outfile, ensure_ascii=False, indent=2)
