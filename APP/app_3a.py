from shiny import App, ui, render
import pandas as pd

# Load dataset
data_path = r"C:\Users\Pei-Chin\Documents\GitHub\Problem-Set-6\waze_data\waze_data.csv"
waze_data = pd.read_csv(data_path)

# Create a new column combining 'type' and 'subtype'
waze_data['type_subtype_combo'] = waze_data['type'] + " - " + waze_data['subtype']

# Extract unique type-subtype combinations for the dropdown
unique_combinations = waze_data['type_subtype_combo'].drop_duplicates().tolist()

# UI definition
app_ui = ui.page_fluid(
    ui.panel_title("Dropdown and Hour Range Slider"),
    ui.input_select(
        "type_subtype",
        "Select Type and Subtype:",
        choices=unique_combinations,
        selected=unique_combinations[0]
    ),
    ui.input_slider(
        "hour_range",
        "Select Hour Range:",
        min=0,
        max=23,
        value=(6, 9)  # Default range
    ),
    ui.output_text_verbatim("selected_combination"),
    ui.output_text_verbatim("selected_hour_range")
)

# Server logic
def server(input, output, session):
    @output
    @render.text
    def selected_combination():
        # Display the selected type and subtype combination
        return f"Selected Combination: {input.type_subtype()}"

    @output
    @render.text
    def selected_hour_range():
        # Display the selected hour range
        hour_min, hour_max = input.hour_range()
        return f"Selected Hour Range: {hour_min:02}:00 - {hour_max:02}:00"

# Create the app
app = App(app_ui, server)
