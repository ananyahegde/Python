from bs4 import BeautifulSoup
import pandas as pd
import re

def parse(items):
    rows = []

    for item in items:
        name = item.find("h3").find("a")["title"]

        price_raw = item.find("p", class_="price_color").text.strip()
        price = float(re.sub(r'[^\d.]', '', price_raw))

        sku_raw = item.find("h3").find("a")["href"]
        sku = sku_raw.split("/")[-2]

        rows.append({"name": name, "price": price, "sku": sku})

    return pd.DataFrame(rows)
