from shiny import App, ui, render
import pandas as pd
import altair as alt
import json
import os
import itertools

# File paths
geojson_path = r"C:\Users\Pei-Chin\Dropbox (1)\Boundaries - Neighborhoods.geojson"
data_path = r"C:\Users\Pei-Chin\Documents\GitHub\Problem-Set-6\top_alerts_map_byhour\original_with_hour.csv"

# Load the merged dataset
merged_data = pd.read_csv(data_path)

# Preprocessing: Ensure 'type' and 'subtype' columns are present
if 'type' not in merged_data.columns or 'subtype' not in merged_data.columns:
    raise KeyError("Columns 'type' and 'subtype' are missing in the dataset.")

# Create 'type_subtype_combo' column
merged_data['type_subtype_combo'] = merged_data['type'].astype(str) + " - " + merged_data['subtype'].astype(str)

# Ensure 'hour' column is numeric
merged_data['hour'] = pd.to_datetime(merged_data['ts']).dt.hour

# Ensure latitude and longitude have no missing values
merged_data = merged_data.dropna(subset=['latitude', 'longitude'])

# Get unique combinations of 'type' and 'subtype'
unique_combos = merged_data['type_subtype_combo'].unique().tolist()

# Load GeoJSON file for the map
with open(geojson_path) as f:
    chicago_geojson = json.load(f)

geo_data = alt.Data(values=chicago_geojson["features"])

# Define the UI
app_ui = ui.page_fluid(
    ui.h3("Jam - Heavy Traffic Plot"),
    ui.input_select(
        "type_subtype",
        "Select Alert Type and Subtype:",
        choices=unique_combos,
        selected=unique_combos[0]
    ),
    ui.input_slider(
        "hour",
        "Select Hour:",
        min=0,
        max=23,
        value=12,
        step=1
    ),
    ui.output_image("traffic_plot")  # Output for the scatter plot as an image
)

# Define the server logic
def server(input, output, session):
    @output
    @render.image
    def traffic_plot():
        # Filter data based on user input
        selected_combo = input.type_subtype()
        selected_hour = input.hour()

        # Filter merged_data for the selected combo and hour
        filtered_data = merged_data[
            (merged_data['type_subtype_combo'] == selected_combo) &
            (merged_data['hour'] == selected_hour)
        ]

        # If no data is available, return None
        if filtered_data.empty:
            print(f"No data available for combo '{selected_combo}' at hour {selected_hour}.")
            return None

        # Group by latitude, longitude, and count the alerts
        grouped_data = (
            filtered_data.groupby(['latitude', 'longitude'])
            .size()
            .reset_index(name='alert_count')
            .nlargest(10, 'alert_count')  # Top 10 locations
        )

        # Create map layer
        map_layer = alt.Chart(geo_data).mark_geoshape(
            fillOpacity=0.1,
            stroke="black",
            strokeWidth=0.5
        ).properties(
            width=800,
            height=600
        ).project("mercator")

        # Create scatter plot layer
        scatter_plot = alt.Chart(grouped_data).mark_circle(size=200).encode(
            longitude='longitude:Q',
            latitude='latitude:Q',
            size=alt.Size('alert_count:Q', title="Number of Alerts"),
            tooltip=['latitude', 'longitude', 'alert_count']
        ).properties(
            title=f"Top 10 Locations for '{selected_combo}' at {selected_hour}:00"
        )

        # Combine map and scatter plot
        combined_chart = map_layer + scatter_plot

        # Save the chart to a PNG file
        file_path = os.path.abspath("temp_alert_map.png")

        # Save chart using Altair's built-in saving mechanism
        try:
            combined_chart.save(file_path, format="png")
            print(f"Chart saved successfully: {file_path}")
        except Exception as e:
            print(f"Error saving chart: {e}")
            return None

        # Return the image path for rendering
        if os.path.exists(file_path):
            return {"src": file_path, "alt": "Traffic Plot"}
        else:
            print("File not found after saving.")
            return None

# Create the app
app = App(app_ui, server)
