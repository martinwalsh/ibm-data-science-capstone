# Import required libraries
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df["outcome"] = spacex_df["class"].apply(
    lambda x: "Failure" if x == 0 else "Success"
)
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

dropdown_options = [{"label": "All Sites", "value": "ALL"}]
for site in spacex_df["Launch Site"].unique():
    dropdown_options.append({"label": site, "value": site})

default_style = {"font-family": '"Open Sans", verdana, arial, sans-serif'}

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "font-size": 40,
            },
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        # dcc.Dropdown(id='site-dropdown',...)
        dcc.Dropdown(
            id="site-dropdown",
            options=dropdown_options,
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        # dcc.RangeSlider(id='payload-slider',...)
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            # marks={
            #     q: str(q)
            #     for q in list(
            #         spacex_df["Payload Mass (kg)"].quantile([0.25, 0.5, 0.75])
            #     )
            # },
            value=[min_payload, max_payload],
        ),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ],
    style=default_style,
)


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def update_pie_chart(selected_site):
    if selected_site == "ALL":
        fig = px.pie(
            spacex_df[spacex_df["class"] == 1],
            names="Launch Site",
            title="Total Successful Launches by Site",
            color_discrete_sequence=["gold", "lightblue", "tomato", "lightgreen"],
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#000000", width=2)),
        )
        fig.update_layout(hovermode=False)
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == selected_site]
        fig = px.pie(
            filtered_df.sort_values("class"),
            names="outcome",
            title=f"Launch Success vs Failure for site {selected_site}",
            hover_data=["class"],
            color="outcome",
            color_discrete_map={"Success": "lightblue", "Failure": "tomato"},
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="%{label}: %{value}",
            marker=dict(line=dict(color="#000000", width=2)),
        )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= payload_range[0])
        & (spacex_df["Payload Mass (kg)"] <= payload_range[1])
    ]
    if selected_site == "ALL":
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Payload Success Rate for All Sites",
        )
    else:
        filtered_df = filtered_df[spacex_df["Launch Site"] == selected_site]
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=f"Payload Success Rate for site {selected_site}",
        )
    fig.update_layout(yaxis_tickvals=[0, 1])
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
