from bs4 import BeautifulSoup
import pandas as pd

def parse(items):
    rows = []

    for item in items:
        name = item.find("h3").find("a")["title"]
        price = item.find("p", class_="price_color").text.strip()
        sku_raw = item.find("h3").find("a")["href"]
        sku = sku_raw.split("/")[-2]
        rows.append({"name": name, "price": price, "sku": sku})

    return pd.DataFrame(rows)
