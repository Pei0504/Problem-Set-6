from shiny import App, ui, render
import pandas as pd

# Load dataset
data_path = r"C:\Users\Pei-Chin\Documents\GitHub\Problem-Set-6\waze_data\waze_data.csv"
waze_data = pd.read_csv(data_path)

# Extract unique type-subtype combinations for the dropdown
unique_combinations = (
    waze_data[['type', 'subtype']]
    .drop_duplicates()
    .assign(
        formatted=lambda df: df['type'] + " - " + df['subtype']
    )
    ['formatted']
    .tolist()
)

# UI definition
app_ui = ui.page_fluid(
    ui.panel_title("Dropdown and Slider Example"),
    ui.input_select(
        "type_subtype",
        "Select Type and Subtype:",
        choices=unique_combinations,
        selected=unique_combinations[0]
    ),
    ui.input_slider(
        "hour",
        "Select Hour:",
        min=0,
        max=23,
        value=12
    ),
    ui.output_text_verbatim("selected_combination"),
    ui.output_text_verbatim("selected_hour")
)

# Server logic
def server(input, output, session):
    @output
    @render.text
    def selected_combination():
        return f"Selected Combination: {input.type_subtype()}"

    @output
    @render.text
    def selected_hour():
        return f"Selected Hour: {input.hour()}"

# Create the app
app = App(app_ui, server)
