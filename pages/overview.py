import dash
from dash import callback, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


from utils import *


dash.register_page(
    __name__,
    path="/",
    title="Financial Overview",
    name="Financial Overview",
    description="Overview financial valuation of an asset in portfolio",
)


assets_df = get_collection_as_df("assets")
assets_collection = get_collection("assets")
patient_schedule_collection = get_collection("patients_schedule")
development_milestones_collection = get_collection("development_milestones")
sales_milestones_collection = get_collection("sales_milestones")
royalty_tiers_collection = get_collection("royalty_tiers")
global_params_collection = get_collection("global_params")

refresh_persists = False

TABLE_WRAPPER_STYLE = {
    "overflowX": "scroll",
    "backgroundColor": "rgba(12, 15, 35, 0.35)",
    "borderRadius": "16px",
    "padding": "6px",
}

TABLE_HEADER_STYLE = {
    "backgroundColor": "rgba(56, 73, 130, 0.75)",
    "color": "#F2F4FF",
    "border": "1px solid rgba(136, 160, 255, 0.35)",
    "fontWeight": "600",
    "fontSize": "14px",
}

TABLE_DATA_STYLE = {
    "backgroundColor": "rgba(17, 22, 46, 0.65)",
    "color": "#D7DBFF",
    "border": "1px solid rgba(86, 108, 171, 0.3)",
    "fontSize": "13px",
    "padding": "10px",
}


def style_figure(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(12, 15, 35, 0.55)",
        plot_bgcolor="rgba(12, 15, 35, 0.0)",
        font=dict(color="#E3E7FF", family="'Inter', 'Segoe UI', sans-serif"),
        hovermode="x unified",
        margin=dict(l=40, r=24, t=48, b=32),
    )
    fig.update_xaxes(gridcolor="rgba(255, 255, 255, 0.05)")
    fig.update_yaxes(gridcolor="rgba(255, 255, 255, 0.08)")
    return fig

asset_selector = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Search Database", className="card-title"),
            dcc.Dropdown(
                options=list(get_collection_as_df("assets")["name"]),
                multi=False,
                placeholder="Select an asset",
                clearable=True,
                id="financial_asset_selector",
                persistence=refresh_persists,
                className="aurora-dropdown",
            ),
        ]
    ),
    id="asset_selector_card",
    className="themed-card glass-panel",
)

net_sales_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Net Sales Forecasts"),
            html.Br(),
            dcc.Dropdown(
                options=["US", "Europe", "Rest of World"],
                multi=True,
                placeholder="Select regions",
                persistence=refresh_persists,
                id="sales_region_selector",
                className="aurora-dropdown",
            ),
            dcc.Checklist(
                ["Separated"],
                persistence=refresh_persists,
                id="separated_net_sales",
                className="aurora-checklist",
            ),
            dash_table.DataTable(
                id="net_sales_table",
                style_table=TABLE_WRAPPER_STYLE,
                style_header=TABLE_HEADER_STYLE,
                style_data=TABLE_DATA_STYLE,
                css=[{"selector": "table", "rule": "background-color: transparent;"}],
            ),
            html.Div(
                id='net_sales_graph_container',
                style={'display': 'none'},
                className="graph-wrapper",
            ),

        ]
    ),
    id="net_sales_card",
    className="themed-card glass-panel",
)


royalty_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Royalty Revenues"),
            html.Br(),
            html.P("Select regions where royalties are applicable"),
            dcc.Dropdown(
                options=["US", "Europe", "Rest of World"],
                multi=True,
                placeholder="Select regions",
                id="royalty_region_selector",
                className="aurora-dropdown",
            ),
            dcc.Checklist(
                ["Separated"],
                id="separated_royalty",
                className="aurora-checklist",
            ),
            dash_table.DataTable(
                id="royalty_table",
                style_table=TABLE_WRAPPER_STYLE,
                style_header=TABLE_HEADER_STYLE,
                style_data=TABLE_DATA_STYLE,
                css=[{"selector": "table", "rule": "background-color: transparent;"}],
            ),
            html.Div(
                id='royalty_graph_container',
                style={'display': 'none'},
                className="graph-wrapper",
            ),

        ]
    ),
    id="royalty_card",
    className="themed-card glass-panel",
)


total_revenues_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Total Revenue"),
            html.Br(),
            dash_table.DataTable(
                id="total_revenue_table",
                style_table=TABLE_WRAPPER_STYLE,
                style_header=TABLE_HEADER_STYLE,
                style_data=TABLE_DATA_STYLE,
                css=[{"selector": "table", "rule": "background-color: transparent;"}],
            ),
            html.Div(
                id='total_revenue_graph_container',
                style={'display': 'none'},
                className="graph-wrapper",
            ),
        ]
    ),
    id="total_revenues_card",
    className="themed-card glass-panel",
)

npv_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Net Present Value"),
            html.Br(),
            dcc.Loading(
                id="npv_table_loading",
                children=dash_table.DataTable(
                    id="npv_table",
                    style_table=TABLE_WRAPPER_STYLE,
                    style_header=TABLE_HEADER_STYLE,
                    style_data=TABLE_DATA_STYLE,
                    css=[{"selector": "table", "rule": "background-color: transparent;"}],
                ),
                color="#84A7FF",
                type="dot",
            ),
            html.Br(),
            html.H6(id="npv_value"),
            html.Div(
                id='npv_graph_container',
                style={'display': 'none'},
                className="graph-wrapper",
            ),
        ]
    ),
    id="npv_card",
    className="themed-card glass-panel",
)

detailed_toggle = daq.BooleanSwitch(
                    on=False,
                    label='Detailed View',
                    labelPosition='top',
                    color='#1F51FF',
                    id='detailed_view_switch',
                    className='detailed-toggle',
                  )

interaction_card = dbc.Card(
    dbc.CardBody(
        [
            html.H6('Cohort Analyst', className='card-title'),
            html.P(
                'Activate detailed mode to surface patient kinetics and scenario overlays for complex mechanisms.',
                className='card-text',
            ),
            html.Div(detailed_toggle, className='toggle-wrapper'),
        ]
    ),
    className='themed-card glass-panel interaction-card',
)


def layout():

    particles = [
        html.Div(
            className='particle',
            style={
                'animationDelay': f"{i * 0.75}s",
                'left': f"{(i * 11) % 100}%",
                'top': f"{(i * 17) % 100}%",
                'animationDuration': f"{14 + (i % 5) * 2}s",
            },
        )
        for i in range(12)
    ]

    signal_band = html.Div(
        className='signal-band glass-panel',
        children=[
            html.Div(
                [
                    html.Span('phase velocity', className='signal-label'),
                    html.Span('0.68 p(approval)', className='signal-value'),
                ],
                className='signal-item',
            ),
            html.Div(
                [
                    html.Span('equity pulse', className='signal-label'),
                    html.Span('+4.2σ momentum', className='signal-value'),
                ],
                className='signal-item',
            ),
            html.Div(
                [
                    html.Span('liquidity runway', className='signal-label'),
                    html.Span('27 mo modeled', className='signal-value'),
                ],
                className='signal-item',
            ),
        ],
    )

    hero_panel = html.Div(
        className='hero-header glass-panel',
        children=[
            html.Div(
                [
                    html.Span('ggsgge', className='brand-name'),
                    html.Span('ets ok ggets', className='brand-tag'),
                ],
                className='brand-mark',
            ),
            html.Div(
                [
                    html.H4('Redmile Biotech Intelligence Hub', className='hero-title'),
                    html.P(
                        'Scenario-ready valuation environment for science-driven public equity strategies.',
                        className='hero-subtitle',
                    ),
                    html.Div(
                        [
                            html.Span('synthetic diligence', className='hero-pill'),
                            html.Span('clinical kinetics', className='hero-pill'),
                            html.Span('equity pulse', className='hero-pill'),
                        ],
                        className='hero-pill-group',
                    ),
                ],
                className='hero-intel',
            ),
        ],
    )

    controls_row = dbc.Row(
        [
            dbc.Col(asset_selector, lg=9, md=8, xs=12),
            dbc.Col(interaction_card, lg=3, md=4, xs=12, className='mt-4 mt-md-0'),
        ],
        className='gy-4 align-items-stretch',
    )

    analytics_grid = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(net_sales_card, lg=6, xs=12),
                    dbc.Col(royalty_card, lg=6, xs=12),
                ],
                className='gy-4',
            ),
            dbc.Row(
                [
                    dbc.Col(total_revenues_card, lg=6, xs=12),
                    dbc.Col(npv_card, lg=6, xs=12),
                ],
                className='gy-4',
            ),
        ],
        className='analytics-grid',
    )

    content = dbc.Container(
        [
            dcc.Store(id='total_revenues_store_table'),
            hero_panel,
            signal_band,
            controls_row,
            analytics_grid,
        ],
        fluid=True,
        className='content-container',
    )

    page = html.Div(
        className='aurora-app',
        children=[
            html.Div(
                className='aurora-background',
                children=[
                    html.Div(className='aurora-gradient gradient-one'),
                    html.Div(className='aurora-gradient gradient-two'),
                    html.Div(className='aurora-gradient gradient-three'),
                ],
            ),
            html.Div(className='particle-field', children=particles),
            content,
        ],
    )
    return page


def get_net_sales(asset_name, regions, separated):
    sales_data = []
    asset_data = assets_collection.find_one({"name": asset_name})

    asset_id = asset_data["_id"]

    for region in regions:
        ps_table = patient_schedule_collection.find({'AssetID': asset_id, 'Region': region})
        sales_by_year = {}

        for entry in ps_table:
            for year, patient_count in entry.items():
                if year != '_id' and year != 'AssetID' and year != 'Region':
                    year = int(year)
                    count = int(patient_count)
                    if region == "US":
                        price = asset_data["pricing_us"]
                    elif region == "Europe":
                        price = asset_data["pricing_eur"]
                    else:
                        price = asset_data["pricing_row"]

                    price = int(price)
                    if year in sales_by_year:
                        sales_by_year[year] += count * price
                    else:
                        sales_by_year[year] = count * price

        if separated:
            sales_data.append((region, sales_by_year))
        else:
            sales_data.extend(sales_by_year.items())
    if separated:
        df = pd.DataFrame({region: sales_by_year for region, sales_by_year in sales_data}).transpose()
        df = df.rename_axis("Region")
        df.columns.name = "Year"
    else:
        series = pd.DataFrame(sales_data, columns=["Year", "Sales"]).groupby("Year")["Sales"].sum()
        df = pd.DataFrame({"Year": series.index, "Sales": series.values}).set_index("Year").transpose()

    return df


def royalty_computation(royalty_table, sales):
    if type(sales) not in (int, float):
        return sales
    # if no royalty table has been provided
    if not royalty_table:
        return sales
    royalty = 0
    remaining_sales = sales
    print(royalty_table)
    for i, tier in enumerate(royalty_table):
        if i == len(royalty_table) - 1:
            royalty += (sales - tier["upto_royalty"]) * tier["royalty_percent"]
        else:
            if sales <= tier["upto_royalty"]:
                royalty += remaining_sales * tier["royalty_percent"]
                break
            else:
                if i == 0:
                    royalty += tier["upto_royalty"] * tier["royalty_percent"]
                    remaining_sales -= tier["upto_royalty"]
                else:
                    royalty += (tier["upto_royalty"] - royalty_table[i - 1]["upto_royalty"]) * tier["royalty_percent"]
                    remaining_sales -= (tier["upto_royalty"] - royalty_table[i - 1]["upto_royalty"])

    return royalty


@callback(Output('net_sales_table', 'columns'),
          Output('net_sales_table', 'data'),
          Output('net_sales_graph_container', 'children'),
          Output('net_sales_graph_container', 'style'),
          Input('financial_asset_selector', 'value'),
          Input('sales_region_selector', 'value'),
          Input('separated_net_sales', 'value'))
def update_net_sales_table(asset_name, regions, separated):

    if asset_name is None or regions is None:
        return [], [], dash.no_update, {"display": "none"}

    df = get_net_sales(asset_name, regions, separated)
    fig = px.line(df.transpose())
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Net Sales'
    )
    fig = style_figure(fig)
    df = df.reset_index()
    df = df.applymap(format_to_millions)
    df = df.replace(np.nan, 0)
    return [{"name": str(i), "id": str(i)} for i in df.columns], df.to_dict('records'), dcc.Graph(figure=fig), {'display': 'block'}


@callback(Output('royalty_table', 'columns'),
          Output('royalty_table', 'data', allow_duplicate=True),
          Output('royalty_graph_container', 'children'),
          Output('royalty_graph_container', 'style'),
          Input('financial_asset_selector', 'value'),
          Input('royalty_region_selector', 'value'),
          Input('separated_royalty', 'value'),
          prevent_initial_call=True)
def update_royalty_table(asset_name, regions, separated):

    if asset_name is None or regions is None:
        return [], [], dash.no_update, {"display": "none"}

    asset_data = assets_collection.find_one({"name": asset_name})
    royalty_table = list(royalty_tiers_collection.find({"AssetID": asset_data["_id"]}))
    # royalty_table = [[value for value in document.values()] for document in r_table]

    df = get_net_sales(asset_name, regions, separated)
    df = df.applymap(lambda x: royalty_computation(royalty_table, x))

    if not separated:
        df.index = ["Royalty"]

    fig = px.line(df.transpose())
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Net Revenue'
    )
    fig = style_figure(fig)
    df = df.reset_index()
    df = df.applymap(format_to_millions)
    df = df.replace(np.nan, 0)
    return [{"name": str(i), "id": str(i)} for i in df.columns], df.to_dict('records'), dcc.Graph(figure=fig), {'display': 'block'}


@callback(Output('sales_region_selector', 'value'),
          Output('royalty_region_selector', 'value'),
          Input('financial_asset_selector', 'value'))
def add_all_regions(asset_name):
    if asset_name:
        return default_regions, default_regions
    else:
        return [], []


@callback(Output('total_revenue_table', 'columns'),
          Output('total_revenue_table', 'data'),
          Output('total_revenues_store_table', 'data'),
          Output('total_revenue_graph_container', 'children'),
          Output('total_revenue_graph_container', 'style'),
          Input('financial_asset_selector', 'value'),
          Input('royalty_region_selector', 'value'))
def update_total_revenue_table(asset_name, royalty_regions):

    if asset_name is None:
        return [], [], dash.no_update, dash.no_update, {"display": "none"}

    asset_data = assets_collection.find_one({"name": asset_name})
    royalty_table = list(royalty_tiers_collection.find({"AssetID": asset_data["_id"]}))

    df = get_net_sales(asset_name, default_regions, True)
    df_filtered = df.loc[royalty_regions]

    # Retrieve sales milestone data for the asset_name from MongoDB
    sm_data = sales_milestones_collection.find({'AssetID': asset_data["_id"]})

    # Retrieve development milestone data for the asset_name from MongoDB
    dm_data = development_milestones_collection.find({'AssetID': asset_data["_id"]})

    development_milestone_row = [None] * len(df.columns)
    for milestone in dm_data:
        milestone_amount = milestone['amount']
        milestone_year = milestone['achievement_year']
        if milestone_year not in df.columns:
            df[milestone_year] = None
            development_milestone_row.extend([None])
        development_milestone_row[df.columns.get_loc(milestone_year)] = milestone_amount
    df.loc['Development Milestones'] = development_milestone_row

    for milestone in sm_data:
        milestone_sales_exceeding = milestone['sales_exceeding']
        milestone_amount = milestone['amount']

        # Check if sales exceed the milestone value for the specified year
        sales_exceeded = False
        milestone_year = None
        for year in df_filtered.columns[1:]:

            if df_filtered[year].sum() >= milestone_sales_exceeding:
                sales_exceeded = True
                milestone_year = year
                break
        # If sales exceed the milestone value, add the milestone amount to the DataFrame
        if sales_exceeded:
            df.loc["Sales Milestones", milestone_year] = milestone_amount
    df = df.sort_index(axis=1)

    # apply royalty to selected regions
    df_copy = df.copy()
    df.loc[df_copy.index.isin(royalty_regions), :] = df_copy.loc[df_copy.index.isin(royalty_regions), :].applymap(lambda x: royalty_computation(royalty_table, x))

    traces = []
    for region in df.index:
        trace = go.Scatter(
            x=df.columns,
            y=df.loc[region],
            mode='lines',
            stackgroup='one',
            # groupnorm='percent',
            name=region
        )
        traces.append(trace)

    # Add a row for the total
    total_row = [df.iloc[:, i].sum() for i in range(0, df.shape[1])]
    df.loc["Total Revenue"] = total_row

    stored_df = df.to_json()

    layout = go.Layout(
        title='Revenue Distribution by Year',
        xaxis={'title': 'Year'},
        yaxis={'title': 'Total Revenue'},
        #barmode='stack'  # For stacked area chart
    )

    fig = go.Figure(data=traces, layout=layout)

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=["groupnorm", "percent"],
                        label="Stacked Percentage",
                        method="restyle"
                    ),
                    dict(
                        args=["groupnorm", None],
                        label="Stacked Total",
                        method="restyle"
                    )
                ]),
                showactive=True,
                pad={"t": -35},
                xanchor="left",
                yanchor="top"
            ),
        ]
    )

    fig = style_figure(fig)

    df = df.replace(np.nan, 0)
    df = df.applymap(format_to_millions)
    df.reset_index(inplace=True)

    return [{"name": str(i), "id": str(i)} for i in df.columns], df.to_dict('records'), stored_df, dcc.Graph(figure=fig), {'display': 'block'}


@callback(Output('npv_table', 'columns'),
          Output('npv_table', 'data'),
          Output('npv_graph_container', 'children'),
          Output('npv_graph_container', 'style'),
          Output('npv_value', 'children'),
          Input('total_revenues_store_table', 'data'))
def update_npv_table(data):
    if data is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    global_params = list(global_params_collection.find())[0]
    df = pd.read_json(data)
    df = df.loc["Total Revenue"].to_frame().T
    df.index = ["Total Revenue"]
    sales_margin = df.loc["Total Revenue"] * global_params["sales_margin"] / 100

    new_df = pd.DataFrame([sales_margin], index=[f"Net Income - {global_params['sales_margin']}%"], columns=df.columns)
    df = pd.concat([df, new_df])

    after_tax = df.loc[f"Net Income - {global_params['sales_margin']}%"] * (1 - (global_params["tax_rate"] / 100))

    new_df = pd.DataFrame([after_tax], index=[f"After Tax - {global_params['tax_rate']}%"], columns=df.columns)
    df = pd.concat([df, new_df])

    df = df.replace(np.nan, 0)
    years = df.columns
    periods = years - 2023
    present_values = df.iloc[2, :] / (1 + (global_params["discount_rate"] / 100)) ** periods
    npv = float(present_values.sum())
    df.loc['Present Value'] = present_values


    fig = px.line(df.transpose())
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Net NPV'
    )
    fig = style_figure(fig)
    df = df.applymap(format_to_millions)
    return [{"name": "Index", "id": "index"}] + [{"name": str(i), "id": str(i)} for i in df.columns]\
        , df.reset_index().to_dict('records'), dcc.Graph(figure=fig), {'display': 'block'}, f"The asset's Net Present Value is {format_to_millions(npv)}"


@callback(
    Output("net_sales_card", "style"),
    Output("royalty_card", "style"),
    Output("total_revenues_card", "style"),
    Input("detailed_view_switch", "on"),
)
def toggle_card_visibility(switch_value):
    if switch_value:
        return {"display": "block"}, {"display": "block"}, {"display": "block"}
    else:
        return {"display": "none"}, {"display": "none"}, {"display": "none"}

# Updates assets in search database dropdown
@callback(
    dash.dependencies.Output('financial_asset_selector', 'options'),
    [dash.dependencies.Input('financial_asset_selector', 'value')]
)
def update_asset_dropdown(name):
    return [{'label': i, 'value': i} for i in list(get_collection_as_df("assets")["name"])]
