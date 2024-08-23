import json
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

def increment_month(current_date):
    year = current_date.year
    month = current_date.month

    # Handle year increment if month is December
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1

    # Return the first day of the next month
    return datetime(year, month, 1)

def generate_urls(start_date, end_date):
    urls = []
    current_date = start_date
    while current_date <= end_date:
        url = (
            f"https://wear.jp/ranking/?date="
            + current_date.strftime("%Y%m")
            + "&kind_id=2"
        )
        urls.append((url, current_date.strftime("%Y/%m")))
        # Increment month using the correct method
        current_date = increment_month(current_date)
    return urls

def scrape_page(url, date_str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all("li", class_=["first-line-item", "other-line-item"])

    data = []
    for item in tqdm(items, desc="Scraping items", leave=False):
        try:
            image_tag = item.find("div", class_="image").find("img")
            description_tag = item.find("div", class_="profile").find("p", class_="txt")
            model_tag = item.find("div", class_="profile").find("a", class_="over")

            if image_tag and description_tag and model_tag:
                image_url = "https:" + image_tag["src"]
                description = description_tag.text.strip()
                model_name = model_tag.text.strip()
                model_url = "https://wear.jp" + model_tag["href"]

                # Scrape model's details
                model_details = scrape_model_details(model_url)

                if model_details:  # Only append if model details were successfully scraped
                    data.append(
                        {
                            "date": date_str,
                            "image_url": image_url,
                            "description": description,
                            "model_name": model_name,
                            "model_url": model_url,
                            **model_details,
                        }
                    )
        except Exception as e:
            print(f"Error scraping item: {e}")
    return data

def scrape_model_details(model_url):
    def is_age(text):
        return bool(re.match(r'^\d{1,2}歳$', text))

    # Function to extract details from the <a> tag
    def extract_details(a_tag_text):
        parts = a_tag_text.split(' / ')
        
        # Initialize the result dictionary with None values
        details = {
            "height": None,
            "sex": None,
            "age": None,
            "model_description": None
        }
        
        # Parsing logic based on the order and what each part could represent
        if len(parts) > 0:
            # First part could be height
            if re.match(r'^\d+cm$', parts[0]):
                details['height'] = parts.pop(0)
        
        if len(parts) > 0:
            # Second part could be sex
            if parts[0] in ['MEN', 'WOMEN']:
                details['sex'] = parts.pop(0)
        
        if len(parts) > 0:
            # Third part could be age
            if is_age(parts[0]):
                details['age'] = re.findall(r'\d+', parts.pop(0))[0]
        
        if len(parts) > 0:
            # Any remaining part is the model description
            details['model_description'] = ' / '.join(parts)
        
        return details

    try:
        response = requests.get(model_url)
        if response.status_code != 200:
            print(f"Failed to retrieve {model_url}: {response.status_code}")
            return {}

        soup = BeautifulSoup(response.content, "html.parser")

        # Find all <a> tags that match the specific class
        a_tags = soup.find_all('a', class_='inline-block rounded-[4px] border-gray-300 bg-gray-50 px-2 py-[6px] text-[11px] leading-[1.2] xl:rounded-[2px] xl:border xl:bg-white xl:px-3 xl:text-[12px] xl:tracking-wider xl:hover:bg-gray-60 bg-white')

        # Extract details from the first matching <a> tag (if available)
        if a_tags:
            return extract_details(a_tags[0].text)
        else:
            print(f"No matching details found on model page: {model_url}")
            return {}
    except Exception as e:
        print(f"Error scraping model details from {model_url}: {e}")
        return {}

def main():
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 7, 31)
    urls = generate_urls(start_date, end_date)

    all_data = []
    for url, date_str in tqdm(urls, desc="Scraping pages"):
        tqdm.write(f"Scraping monthly top 100 for {date_str}")
        page_data = scrape_page(url, date_str)
        all_data.extend(page_data)

    # Save results to JSON file
    if all_data:
        with open("scraped.json", "w", encoding="utf-8") as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=4)
        print("Data has been scraped and saved to scraped.json")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    main()
