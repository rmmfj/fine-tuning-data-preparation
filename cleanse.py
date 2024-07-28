import json

# Load data from output.json
with open('output.json', 'r', encoding='utf-8') as infile:
    data_a = json.load(infile)

# cleanse function


def cleanse(data):
    cleansed_data = []
    for item in data:
        cleansed_item = {
            "image_url": "https:" + item["image_url"],
            "gender": item["gender"],
            "age": item["age"],
            "height": int(item["height"]) if item["height"] else None,
            "bio": item["bio"]
        }
        cleansed_data.append(cleansed_item)
    return cleansed_data


# cleanse the data
data_b = cleanse(data_a)

# Save the cleansed data to cleanseed_output.json
with open('cleansed_output.json', 'w', encoding='utf-8') as outfile:
    json.dump(data_b, outfile, ensure_ascii=False, indent=2)
