import json
import pandas as pd
import ast
import os
import argparse


# Function to extract URLs ending with sub14.jpg
def extract_sub14_urls(images_url_str):
    urls = []
    images_dict = ast.literal_eval(images_url_str)
    for key in images_dict:
        for item in images_dict[key]:
            if item['url'].endswith('sub14.jpg'):
                urls.append(item['url'])
    return urls



def get_url_from_csv(file_path):
    data = pd.read_csv(file_path)
    # Apply the function to extract URLs from the 'images_url' column
    data['sub14_urls'] = data['images_url'].apply(extract_sub14_urls)
    # Flatten the list of URLs
    sub14_urls = [url for sublist in data['sub14_urls'] for url in sublist]
    return sub14_urls

def main(file_path):
    image_urls = get_url_from_csv(file_path=file_path)
    df = pd.DataFrame({
        "image_urls": image_urls
    })
    # Extract the base name of the file
    file_name = os.path.basename(file_path)
    # Remove the file extension to get the clean file name
    clean_file_name = os.path.splitext(file_name)[0]
    df.to_csv(f'{clean_file_name}_simple_list.csv', index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process file path.')
    parser.add_argument('file_path', type=str, help='The path of the file')
    args = parser.parse_args()
    main(args.file_path)