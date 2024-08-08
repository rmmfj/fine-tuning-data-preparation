import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


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
        # Increment month
        next_month = current_date + timedelta(days=31)
        current_date = datetime(next_month.year, next_month.month, 1)
    return urls


def scrape_page(url):
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
                image_url = image_tag["src"]
                description = description_tag.text.strip()
                model_name = model_tag.text.strip()
                model_url = "https://wear.jp" + model_tag["href"]

                # Scrape model's details
                model_details = scrape_model_details(model_url)

                data.append(
                    {
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


# def scrape_model_details(model_url):
#     try:
#         response = requests.get(model_url)
#         if response.status_code != 200:
#             print(f"Failed to retrieve {model_url}: {response.status_code}")
#             return {"gender": "Unknown", "height": None, "age": None, "bio": ""}

#         soup = BeautifulSoup(response.content, "html.parser")

#         # Safely find gender
#         gender_tag = soup.find("li", text=lambda x: x and ("MEN" in x or "WOMEN" in x))
#         gender = gender_tag.text.strip() if gender_tag else "Unknown"

#         # Safely find height
#         height_tag = soup.find("li", text=lambda x: x and "cm" in x)
#         height = int(height_tag.text.strip().replace("cm", "")) if height_tag else None

#         # Safely find age
#         age_tag = soup.find("li", text=lambda x: x and "歳" in x)
#         age = int(age_tag.text.strip().replace("歳", "")) if age_tag else None

#         # Safely find bio
#         bio_section = soup.find("section", class_="profile")
#         bio_tag = bio_section.find("p", class_="txt") if bio_section else None
#         bio = bio_tag.text.strip() if bio_tag else ""

#         return {"gender": gender, "height": height, "age": age, "bio": bio}

#     except Exception as e:
#         print(f"Error scraping model details: {e}")
#         return {"gender": "Unknown", "height": None, "age": None, "bio": ""}


def scrape_model_details(model_url):
    try:
        response = requests.get(model_url)
        if response.status_code != 200:
            print(f"Failed to retrieve {model_url}: {response.status_code}")
            return {"gender": "Unknown", "height": None, "age": None, "bio": ""}

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the text containing the gender and height
        info_div = soup.find(
            "div", class_="text-xs leading-[1.8] text-white xl:text-black-400"
        )
        if info_div:
            info_text = info_div.text.strip().split(" / ")
            if len(info_text) == 3:
                username = info_text[0]  # Not used, but can be stored if needed
                height = int(info_text[1].replace("cm", "").strip())  # Extract height
                gender = info_text[2].strip()  # Extract gender (e.g., MEN or WOMEN)
            else:
                height = None
                gender = "Unknown"
        else:
            height = None
            gender = "Unknown"

        # Extract bio
        bio = ""
        bio_tags = soup.find_all(
            "p",
            class_="whitespace-pre-wrap text-[13px] text-white xl:leading-[1.6] xl:text-black-400",
        )
        if bio_tags:
            bio = "\n\n".join([tag.text.strip() for tag in bio_tags])

        return {"gender": gender, "height": height, "age": None, "bio": bio}

    except Exception as e:
        print(f"Error scraping model details: {e}")
        return {"gender": "Unknown", "height": None, "age": None, "bio": ""}


def main():
    start_date = datetime(2024, 4, 1)
    end_date = datetime(2024, 6, 1)
    urls = generate_urls(start_date, end_date)

    all_data = []
    for url, date_str in tqdm(urls, desc="Scraping pages"):
        tqdm.write(f"Scraping monthly top 100 for {date_str}")
        page_data = scrape_page(url)
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
