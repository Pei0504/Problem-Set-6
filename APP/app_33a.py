from shiny import App, ui, render
import pandas as pd
import altair as alt
import json
import os

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
    ui.h3("Dynamic Traffic Plot"),
    ui.input_select(
        "type_subtype",
        "Select Alert Type and Subtype:",
        choices=unique_combos,
        selected=unique_combos[0]
    ),
    ui.input_slider(
        "hour_range",
        "Select Hour Range:",
        min=0,
        max=23,
        value=(6, 9),  # Default range: 6AM to 9AM
        step=1
    ),
    ui.input_switch(
        "switch_button",
        "Toggle to switch to range of hours:",
        value=False  # Default is False (off)
    ),
    ui.output_image("traffic_plot")  # Output for the scatter plot as an image
)

# Define the server logic
def server(input, output, session):
    @output
    @render.image
    def traffic_plot():
        try:
            # Get user inputs
            selected_combo = input.type_subtype()
            hour_min, hour_max = input.hour_range()
            switch_state = input.switch_button()  # Retrieve the switch state (True/False)

            # Debugging switch state
            print(f"Switch state: {switch_state}")

            # Filter data for the selected combination and hour range
            filtered_data = merged_data[
                (merged_data['type_subtype_combo'] == selected_combo) &
                (merged_data['hour'] >= hour_min) &
                (merged_data['hour'] <= hour_max)
            ]

            # If no data is available, return None
            if filtered_data.empty:
                print(f"No data available for combo '{selected_combo}' in range {hour_min}-{hour_max}.")
                return None

            # Group by latitude, longitude, and count the alerts
            grouped_data = (
                filtered_data.groupby(['latitude', 'longitude'], as_index=False)
                .agg(alert_count=('type_subtype_combo', 'count'))  # Count occurrences of type_subtype_combo
            )

            # Ensure alert_count is an integer
            grouped_data['alert_count'] = grouped_data['alert_count'].astype(int)

            # Calculate total alerts for the selected period
            total_alerts = grouped_data['alert_count'].sum()

            # Create the map layer
            map_layer = alt.Chart(geo_data).mark_geoshape(
                fillOpacity=0.1,
                stroke="black",
                strokeWidth=0.5
            ).properties(
                width=800,
                height=600
            ).project("mercator")

            # Create scatter plot layer
            scatter_plot = alt.Chart(grouped_data).mark_circle().encode(
                longitude='longitude:Q',
                latitude='latitude:Q',
                size=alt.Size('alert_count:Q', title="Number of Alerts", 
                              scale=alt.Scale(domain=[1, grouped_data['alert_count'].max()], range=[50, 500])),
                tooltip=['latitude', 'longitude', 'alert_count']
            ).properties(
                title=f"Total Alerts for '{selected_combo}' ({hour_min}-{hour_max}): {total_alerts}"
            )

            # Combine map and scatter plot
            combined_chart = map_layer + scatter_plot

            # Generate a unique file name based on selected combo and time range
            file_name = f"temp_alert_map_{selected_combo.replace(' ', '_')}_{hour_min}_{hour_max}.png"
            file_path = os.path.abspath(file_name)

            # Save the chart to a PNG file
            combined_chart.save(file_path, format="png")

            # Return the image path for rendering
            if os.path.exists(file_path):
                return {"src": file_path, "alt": f"Traffic Plot for {selected_combo} ({hour_min}-{hour_max})"}
            else:
                print("File not found after saving.")
                return None

        except Exception as e:
            print(f"Error generating plot: {e}")
            return None

# Create the app
app = App(app_ui, server)
