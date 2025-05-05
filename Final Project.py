"""
Tyler Franklin
CS230-5
Data: NY-Housing-Dataset

"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt


st.markdown("# New York Housing Market")
st.markdown("### Tyler Franklin - Final Project")

# I used st.markdown to format the title. Opposed to st.write, st.markdown allows easy way
# format the words.


def load_data():
    file_path = "NY-House-Dataset.csv"  # Adjust if needed
    df_main = pd.read_csv(file_path)
    df_main.columns = [col.strip().lower().replace("_", " ") for col in df_main.columns]
    return df_main

df_main = load_data()



##############################################################

# Pie Chart code

localities = sorted(df_main["locality"].dropna().unique())
selected_locality = st.selectbox("Select a locality:", localities)

sublocalities = sorted(df_main[df_main["locality"] == selected_locality]["sublocality"].dropna().unique())
selected_sublocality = st.selectbox("Select a sublocality:", sublocalities)


df_filtered = df_main[
    (df_main["locality"] == selected_locality) &
    (df_main["sublocality"] == selected_sublocality)
]


df_filtered = df_filtered[df_filtered["price"].notnull()]


ranges = {
    "0–100k": 0,
    "100k–200k": 0,
    "200k–300k": 0,
    "300k–400k": 0,
    "400k–500k": 0,
    "500k–600k": 0,
    "600k–700k": 0,
    "700k–800k": 0,
    "800k–900k": 0,
    "900k–1M": 0,
    "1M+": 0
}


for price in df_filtered["price"]:
    if price < 100000:
        ranges["0–100k"] += 1
    elif price < 200000:
        ranges["100k–200k"] += 1
    elif price < 300000:
        ranges["200k–300k"] += 1
    elif price < 400000:
        ranges["300k–400k"] += 1
    elif price < 500000:
        ranges["400k–500k"] += 1
    elif price < 600000:
        ranges["500k–600k"] += 1
    elif price < 700000:
        ranges["600k–700k"] += 1
    elif price < 800000:
        ranges["700k–800k"] += 1
    elif price < 900000:
        ranges["800k–900k"] += 1
    elif price < 1000000:
        ranges["900k–1M"] += 1
    else:
        ranges["1M+"] += 1


labels = []
sizes = []

#Displaying the ranges that have more than 0 entries

for label, count in ranges.items():
    if count > 0:
        labels.append(label)
        sizes.append(count)


fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(sizes, labels=labels, autopct='%.1f%%', startangle=140)
ax.set_title(f"Listing Distribution in {selected_sublocality}, {selected_locality}")

st.pyplot(fig)

#####################################################################


# MAP CODE

df_main.rename(columns={"latitude": "lat", "longitude": "lon"}, inplace=True)

price_ranges = {
    "0 - 100k": (0, 100000),
    "100k - 200k": (100000, 200000),
    "200k - 300k": (200000, 300000),
    "300k - 400k": (300000, 400000),
    "400k - 500k": (400000, 500000),
    "500k - 600k": (500000, 600000),
    "600k - 700k": (600000, 700000),
    "700k - 800k": (700000, 800000),
    "800k - 900k": (800000, 900000),
    "900k - 1M": (900000, 1000000),
    "1M+": (1000000, float('inf'))  # 1 million +
}


st.sidebar.markdown("### Filter by Price Range")
selected_bucket = st.sidebar.radio("Select a price range:", list(price_ranges.keys()))

zoom_level = st.sidebar.slider("Select zoom level:", 0.0, 15.0, 10.0)

# Filter data these ranges
low, high = price_ranges[selected_bucket]
df_filtered = df_main[
    (df_main["locality"] == selected_locality) &
    (df_main["sublocality"] == selected_sublocality) &
    (df_main["price"] >= low) &
    (df_main["price"] < high) &
    (df_main["lat"].notnull()) &
    (df_main["lon"].notnull())
].copy()

# .notnull is just making sure the data point are able to be plotted on a map
# .copy() is preventing a warning that would come up had it not been there (I had to troubleshoot this)
# This is basically just a large boolean operator that will make sure the map shows proper data based
# on inputs

st.title("NYC Housing Map")

view_state = pdk.ViewState(
    latitude=df_filtered["lat"].mean() if not df_filtered.empty else 40.7128,
    longitude=df_filtered["lon"].mean() if not df_filtered.empty else -74.0060,
    zoom=zoom_level,
    pitch=0
)

# This is how we create the map and if no input is selected we will be viewing the center of NYC
# .empty is checking for data in the selected area


APPLE_ICON_URL = "https://cdn-icons-png.flaticon.com/512/415/415733.png"



icon_data = {
    "url": APPLE_ICON_URL,
    "width": 64,
    "height": 64,
    "anchorY": 64
}


df_filtered["icon_data"] = None
for i in df_filtered.index:
    df_filtered.at[i, "icon_data"] = icon_data



layer = pdk.Layer(
    "IconLayer",
    data=df_filtered,
    get_icon="icon_data",
    get_position='[lon, lat]',
    get_size=2,
    size_scale=5,
    pickable=True
)


tooltip = {
    "html": "<b>{formatted address}</b><br/>Price: ${price}",
    "style": {"backgroundColor": "black", "color": "white"}
}


map_view = pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v10',
    initial_view_state=view_state,
    layers=[layer],
    tooltip=tooltip
)

st.pydeck_chart(map_view)

################################################################################

st.markdown("## Listing Statistics (Choose From Map): ")


available_addresses = df_filtered["formatted address"].dropna().unique()
selected_address = st.selectbox("Select an address from the map:", sorted(available_addresses))

if selected_address:
    match = df_filtered[df_filtered["formatted address"] == selected_address]

    if not match.empty:
        sublocal = match.iloc[0]["sublocality"]
        local = match.iloc[0]["locality"]

        comparison_df = df_main[
            (df_main["sublocality"] == sublocal) &
            (df_main["locality"] == local)
        ]

        avg_price = comparison_df["price"].mean()
        avg_sqft = comparison_df["propertysqft"].mean()
        avg_beds = comparison_df["beds"].mean()
        avg_baths = comparison_df["bath"].mean()

        listing_price = match.iloc[0]["price"]
        listing_sqft = match.iloc[0]["propertysqft"]
        listing_beds = match.iloc[0]["beds"]
        listing_baths = match.iloc[0]["bath"]

#####################################################################################

#Comparisons to average

        st.markdown("### Price and Size Comparison")

        st.write(f"**Price:** $ {listing_price:,.0f} vs Avg $ {avg_price:,.0f}")
        st.write(f"**Square Feet:** {listing_sqft:,.0f} sqft vs Avg {avg_sqft:,.0f} sqft")


        st.markdown("###  Bedrooms and Bathrooms Comparison")


        categories = ["Bedrooms", "Bathrooms"]
        selected_values = [listing_beds, listing_baths]
        average_values = [avg_beds, avg_baths]
        x = range(len(categories)) # alignment for x axis
        bar_width = 0.35 # manually set length

        fig, ax = plt.subplots(figsize=(6, 4))

        # Two different bars
        ax.bar(x, selected_values, width=bar_width, label="Selected", color="blue")
        ax.bar([i + bar_width for i in x], average_values, width=bar_width, label="Avg", color="gray")

        ax.set_ylabel("Count")
        ax.set_title(f"Beds/Baths: {selected_address}")
        ax.set_xticks([i + bar_width / 2 for i in x]) # positioning the bars
        ax.set_xticklabels(categories)
        ax.legend() # used to label bar types

        st.pyplot(fig)



##################################################################################3

# Comparison pie chart

st.markdown("## Compare Two Properties Head-to-Head")


all_addresses = sorted(df_main["formatted address"].dropna().unique())


col1, col2 = st.columns(2)
with col1:
    addr1 = st.selectbox("Select Address 1", all_addresses, key="addr1")
with col2:
    addr2 = st.selectbox("Select Address 2", all_addresses, key="addr2")

# Checking that both addresses are selected and different
# Later it will show an error with instruction to fix if not true

if addr1 and addr2 and addr1 != addr2:
    prop1 = df_main[df_main["formatted address"] == addr1].iloc[0]
    prop2 = df_main[df_main["formatted address"] == addr2].iloc[0]


    score = {"Address 1": 0, "Address 2": 0}
    categories = ["Price", "Beds", "Baths", "Sqft"]


    if prop1["price"] < prop2["price"]:
        score["Address 1"] += 1
    else:
        score["Address 2"] += 1


    if prop1["beds"] > prop2["beds"]:
        score["Address 1"] += 1
    else:
        score["Address 2"] += 1

    if prop1["bath"] > prop2["bath"]:
        score["Address 1"] += 1
    else:
        score["Address 2"] += 1

    if prop1["propertysqft"] > prop2["propertysqft"]:
        score["Address 1"] += 1
    else:
        score["Address 2"] += 1


    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(
        score.values(),
        labels=[f"{addr1}", f"{addr2}"],
        autopct="%.0f%%",
        colors=["blue", "red"],
        startangle=140
    )
    ax.set_title("Category Wins (Lower Price, More Beds/Baths/Sqft)")
    st.pyplot(fig)

else:
    st.info("Please select two different addresses to compare.")


if addr1 and addr2 and addr1 != addr2:
    prop1 = df_main[df_main["formatted address"] == addr1].iloc[0]
    prop2 = df_main[df_main["formatted address"] == addr2].iloc[0]

    st.markdown("### Detailed Comparison")

    comparison_data = {
        "Metric": ["Price ($)", "Bedrooms", "Bathrooms", "Square Footage"],
        addr1: [
            f"${prop1['price']:,.0f}",
            f"{prop1['beds']}",
            f"{prop1['bath']}",
            f"{int(prop1['propertysqft']) if not pd.isna(prop1['propertysqft']) else 'N/A'}"
        ],
        addr2: [
            f"${prop2['price']:,.0f}",
            f"{prop2['beds']}",
            f"{prop2['bath']}",
            f"{int(prop2['propertysqft']) if not pd.isna(prop2['propertysqft']) else 'N/A'}"
        ]
    }

    df_compare = pd.DataFrame(comparison_data).set_index("Metric")
    st.table(df_compare)

else:
    st.info("Comparison table will appear when two different addresses are selected.")

