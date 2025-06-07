import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests

st.set_page_config(page_title="Crautos Listings", layout="wide")
st.title("🚗 Crautos Used Car Listings")

# --- Configuration ---
CRAUTOS_URL = "https://crautos.com/autosusados/searchresults.cfm?p=1&c=06060"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# --- Fetch Data ---
@st.cache_data(ttl=600)
def fetch_listings():
    response = requests.get(CRAUTOS_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    cars = []
    for listing in soup.find_all("table", attrs={"bgcolor": "#EFEFEF"}):
        try:
            title_elem = listing.find("td", class_="brandtitle")
            if not title_elem:
                title_elem = listing.find("td", class_="brandtitle-sm")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            link_elem = title_elem.find("a") if title_elem else None
            detail_link = "https://crautos.com/" + link_elem["href"] if link_elem else "N/A"
            price_colones = listing.find("span", class_="precio") or listing.find("span", class_="precio-sm")
            price_colones = price_colones.get_text(strip=True) if price_colones else "N/A"
            price_usd = listing.find("span", class_="preciodolares") or listing.find("span", class_="preciodolares-sm")
            price_usd = price_usd.get_text(strip=True) if price_usd else "N/A"
            desc_elem = listing.find("marquee")
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            image_elem = listing.find("img")
            image_url = image_elem["src"] if image_elem and "src" in image_elem.attrs else ""
            if image_url.startswith("/"):
                image_url = "https://crautos.com" + image_url
            cars.append({
                "Title": title,
                "Price (CRC)": price_colones,
                "Price (USD)": price_usd,
                "Description": description,
                "Image": image_url,
                "Link": detail_link
            })
        except Exception:
            continue
    return pd.DataFrame(cars)

# --- Load Data ---
df = fetch_listings()

# --- Search and Filters ---
st.sidebar.header("🔍 Filter Listings")
search_query = st.sidebar.text_input("Search title")

if search_query:
    df = df[df["Title"].str.contains(search_query, case=False, na=False)]

# --- Display Listings ---
for _, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            if row["Image"]:
                st.image(row["Image"], width=200)
        with cols[1]:
            st.markdown(f"### [{row['Title']}]({row['Link']})")
            st.markdown(f"**Price (CRC):** {row['Price (CRC)']}  ")
            st.markdown(f"**Price (USD):** {row['Price (USD)']}")
            if row['Description']:
                st.markdown(f"_Description:_ {row['Description']}")
        st.markdown("---")
