import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

data = pd.read_csv("avocado.csv")
data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
data.sort_values("Date", inplace=True)

region_labels = [
                    {"label": region, "value": region}
                    for region in np.sort(data.region.unique())
                ]
region_labels.insert(0,{'label': 'All Regions', 'value': 'All Regions'})

avocado_type_labels = [
                        {"label": avocado_type, "value": avocado_type}
                        for avocado_type in data.type.unique()
                    ]
avocado_type_labels.insert(0,{'label': 'All Types', 'value': 'All Types'})

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Avocado Analytics: Understand Your Avocados!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥑", className="header-emoji"),
                html.H1(
                    children="Avocado Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the behavior of avocado prices"
                    " and the number of avocados sold in the US"
                    " between 2015 and 2018",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Region", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=region_labels,
                            value="Albany",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=avocado_type_labels,
                            value="organic",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("region-filter", "value"),
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(region, avocado_type, start_date, end_date):
    mask = (
        (data.Date >= start_date)
        & (data.Date <= end_date)
    )

    if region != 'All Regions' and avocado_type != 'All Types':
        mask = mask & (data.region == region) & (data.type == avocado_type)
    elif region != 'All Regions' and avocado_type == 'All Types':
        mask = mask & (data.region == region)
    elif region == 'All Regions' and avocado_type != 'All Types':
        mask = mask & (data.type == avocado_type)

    filtered_data = data.loc[mask, :]

    if region != 'All Regions' and avocado_type != 'All Types':
        date_price_x = filtered_data["Date"]
        avg_price_y = filtered_data["AveragePrice"]
    else:
        date_price_x = filtered_data["Date"].unique()
        avg_price_y = filtered_data.groupby('Date')["AveragePrice"].mean()

    price_chart_figure = {
        "data": [
            {
                "x": date_price_x,
                "y": avg_price_y,
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Average Price of Avocados",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    if region != 'All Regions' and avocado_type != 'All Types':
        date_volume_x = filtered_data["Date"]
        total_volume_y = filtered_data["Total Volume"]
    else:
        date_volume_x = filtered_data["Date"].unique()
        total_volume_y = filtered_data.groupby('Date')["Total Volume"].sum()

    volume_chart_figure = {
        "data": [
            {
                "x": date_volume_x,
                "y": total_volume_y,
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Avocados Sold", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)