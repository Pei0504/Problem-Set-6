import os
from shiny import App, ui, render
import altair as alt
import pandas as pd
import json

# File paths
geojson_path = r"C:\Users\Pei-Chin\Dropbox (1)\Boundaries - Neighborhoods.geojson"
data_path = r"C:\Users\Pei-Chin\Documents\GitHub\Problem-Set-6\top_alerts_map_byhour\original_with_hour.csv"

if not os.path.exists(geojson_path) or not os.path.exists(data_path):
    raise FileNotFoundError("GeoJSON or CSV file not found. Please check the paths.")

# Load GeoJSON data
with open(geojson_path) as f:
    chicago_geojson = json.load(f)

geo_data = alt.Data(values=chicago_geojson["features"])

# Load Waze data
waze_data = pd.read_csv(data_path)

# Extract unique combinations dynamically
unique_combinations = (
    waze_data[['type', 'subtype']]
    .drop_duplicates()
    .assign(
        updated_type=lambda df: df['type'].str.replace("_", " ").str.title(),
        updated_subtype=lambda df: df['subtype'].str.replace("_", " ").str.title()
    )
    .to_dict(orient='records')
)

# Generate dropdown choices
choices = [f"{entry['updated_type']} - {entry['updated_subtype']}" for entry in unique_combinations]

# Precompute grouped data for lat/lon bins
preprocessed_data = (
    waze_data.assign(
        latitude=waze_data['geo'].str.extract(r'POINT\(-?\d+\.\d+ (-?\d+\.\d+)\)').astype(float, errors='ignore').round(2),
        longitude=waze_data['geo'].str.extract(r'POINT\((-?\d+\.\d+) -?\d+\.\d+\)').astype(float, errors='ignore').round(2)
    )
    .groupby(['type', 'subtype', 'latitude', 'longitude'])
    .size()
    .reset_index(name='alert_count')
)

# UI definition
app_ui = ui.page_fluid(
    ui.panel_title("Shiny-like Dropdown Menu with Map Visualization"),
    ui.input_select("selected_combination", "Select Type and Subtype", choices=choices),
    ui.output_text_verbatim("output_selection"),
    ui.output_image("alert_map")  # Output for the scatter plot as an image
)

# Server logic
def server(input, output, session):
    @output
    @render.text
    def output_selection():
        return f"You selected: {input.selected_combination()}"

    @output
    @render.image
    def alert_map():
        selected = input.selected_combination()
        if not selected or " - " not in selected:
            return None

        # Parse selection
        selected_type, selected_subtype = selected.split(" - ")
        match = next(
            (entry for entry in unique_combinations if entry['updated_type'] == selected_type and entry['updated_subtype'] == selected_subtype),
            None
        )

        if not match:
            return None

        original_type = match["type"]
        original_subtype = match["subtype"]

        # Filter data for the selected type and subtype
        filtered_data = preprocessed_data[
            (preprocessed_data['type'] == original_type) & (preprocessed_data['subtype'] == original_subtype)
        ]

        if filtered_data.empty:
            return None

        # Select top 10 bins
        top_10_bins = filtered_data.nlargest(10, 'alert_count')

        # Create the Altair chart
        map_layer = alt.Chart(geo_data).mark_geoshape(
            fillOpacity=0.1,
            stroke="black",
            strokeWidth=0.5
        ).properties(
            width=800,
            height=600
        ).project("mercator")

        scatter_plot = alt.Chart(top_10_bins).mark_circle().encode(
            longitude='longitude:Q',
            latitude='latitude:Q',
            size=alt.Size('alert_count:Q', title="Number of Alerts"),
            tooltip=['latitude', 'longitude', 'alert_count']
        ).properties(
            title=f"Top 10 Latitude-Longitude Bins with the Highest '{selected}' Alerts"
        )

        # Save the chart to a PNG file
        file_path = "temp_alert_map.png"
        (map_layer + scatter_plot).save(file_path, format="png")

        # Return the image path for rendering
        return {"src": file_path, "alt": "Alert Map"}

# Create the Shiny App
app = App(app_ui, server)
