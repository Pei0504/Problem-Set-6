from shiny import App, ui, render

# Sample data based on your crosswalk table
crosswalk_data = [
    {"type": "JAM", "subtype": "Unclassified", "updated_type": "Traffic Jam", "updated_subtype": "Unclassified"},
    {"type": "JAM", "subtype": "JAM_HEAVY_TRAFFIC", "updated_type": "Traffic Jam", "updated_subtype": "Heavy Traffic"},
    {"type": "JAM", "subtype": "JAM_MODERATE_TRAFFIC", "updated_type": "Traffic Jam", "updated_subtype": "Moderate Traffic"},
    {"type": "JAM", "subtype": "JAM_STAND_STILL_TRAFFIC", "updated_type": "Traffic Jam", "updated_subtype": "Standstill Traffic"},
    {"type": "JAM", "subtype": "JAM_LIGHT_TRAFFIC", "updated_type": "Traffic Jam", "updated_subtype": "Light Traffic"},
    {"type": "ACCIDENT", "subtype": "Unclassified", "updated_type": "Accident", "updated_subtype": "Unclassified"},
    {"type": "ACCIDENT", "subtype": "ACCIDENT_MAJOR", "updated_type": "Accident", "updated_subtype": "Major Accident"},
    {"type": "ACCIDENT", "subtype": "ACCIDENT_MINOR", "updated_type": "Accident", "updated_subtype": "Minor Accident"},
    {"type": "ROAD_CLOSED", "subtype": "Unclassified", "updated_type": "Road Closure", "updated_subtype": "Unclassified"},
    {"type": "ROAD_CLOSED", "subtype": "ROAD_CLOSED_EVENT", "updated_type": "Road Closure", "updated_subtype": "Event Closure"},
    {"type": "ROAD_CLOSED", "subtype": "ROAD_CLOSED_CONSTRUCTION", "updated_type": "Road Closure", "updated_subtype": "Construction Closure"},
    {"type": "ROAD_CLOSED", "subtype": "ROAD_CLOSED_HAZARD", "updated_type": "Road Closure", "updated_subtype": "Hazard Closure"},
    {"type": "HAZARD", "subtype": "Unclassified", "updated_type": "Hazard", "updated_subtype": "Unclassified"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD", "updated_type": "Hazard", "updated_subtype": "Road Hazard"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_CAR_STOPPED", "updated_type": "Hazard", "updated_subtype": "Stopped Car"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_CONSTRUCTION", "updated_type": "Hazard", "updated_subtype": "Construction Hazard"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_EMERGENCY_VEHICLE", "updated_type": "Hazard", "updated_subtype": "Emergency Vehicle"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_ICE", "updated_type": "Hazard", "updated_subtype": "Icy Road"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_OBJECT", "updated_type": "Hazard", "updated_subtype": "Object on Road"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_POT_HOLE", "updated_type": "Hazard", "updated_subtype": "Pothole"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_TRAFFIC_LIGHT_FAULT", "updated_type": "Hazard", "updated_subtype": "Traffic Light Fault"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_SHOULDER", "updated_type": "Hazard", "updated_subtype": "General Shoulder Hazard"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_SHOULDER_CAR_STOPPED", "updated_type": "Hazard", "updated_subtype": "Stopped Car on Shoulder"},
    {"type": "HAZARD", "subtype": "HAZARD_WEATHER", "updated_type": "Hazard", "updated_subtype": "General Weather Hazard"},
    {"type": "HAZARD", "subtype": "HAZARD_WEATHER_FLOOD", "updated_type": "Hazard", "updated_subtype": "Flood"},
    {"type": "HAZARD", "subtype": "HAZARD_WEATHER_FOG", "updated_type": "Hazard", "updated_subtype": "Fog"},
    {"type": "HAZARD", "subtype": "HAZARD_WEATHER_HEAVY_SNOW", "updated_type": "Hazard", "updated_subtype": "Heavy Snow"},
    {"type": "HAZARD", "subtype": "HAZARD_WEATHER_HAIL", "updated_type": "Hazard", "updated_subtype": "Hail"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_SHOULDER_ANIMALS", "updated_type": "Hazard", "updated_subtype": "Animals on Shoulder"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_SHOULDER_MISSING_SIGN", "updated_type": "Hazard", "updated_subtype": "Missing Sign"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_LANE_CLOSED", "updated_type": "Hazard", "updated_subtype": "Lane Closure"},
    {"type": "HAZARD", "subtype": "HAZARD_ON_ROAD_ROAD_KILL", "updated_type": "Hazard", "updated_subtype": "Road Kill"}
]

# Generate the choices for the dropdown (type x subtype combinations)
choices = [f"{entry['updated_type']} - {entry['updated_subtype']}" for entry in crosswalk_data]

# UI definition
app_ui = ui.page_fluid(
    ui.panel_title("Shiny-like Dropdown Menu Example"),
    ui.input_select("selected_combination", "Select Type and Subtype", choices=choices),
    ui.output_text_verbatim("output_selection"),
    ui.output_text_verbatim("output_summary"),
)

# Server logic
def server(input, output, session):
    @output
    @render.text
    def output_selection():
        return f"You selected: {input.selected_combination()}"

    @output
    @render.text
    def output_summary():
        return (
            f"Total number of unique type x subtype combinations: {len(choices)}\n"
            f"Unique combinations:\n{', '.join(choices)}"
        )

# Create the Shiny App
app = App(app_ui, server)
