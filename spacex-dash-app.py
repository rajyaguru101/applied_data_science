# spacex-dash-app.py

# ----- Imports -----
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# ----- Data -----
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = float(spacex_df['Payload Mass (kg)'].min())
max_payload = float(spacex_df['Payload Mass (kg)'].max())

# ----- App -----
app = Dash(__name__)

# ----- Layout (Tasks 1 & 3 components included here) -----
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}
    ),

    # TASK 1: Launch Site Drop-down
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # TASK 2 output: Pie chart
    dcc.Graph(id='success-pie-chart'),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[int(min_payload), int(max_payload)]
    ),

    html.Br(),

    # TASK 4 output: Scatter chart
    dcc.Graph(id='success-payload-scatter-chart'),
])

# ----- Callbacks -----

# TASK 2: Pie chart callback (site-dropdown -> success-pie-chart)
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        # successes per site = sum of class (1=success, 0=failure)
        df_all = (spacex_df.groupby('Launch Site', as_index=False)['class']
                  .sum()
                  .rename(columns={'class': 'Successes'}))
        fig = px.pie(df_all, values='Successes', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = (df_site['class']
                  .value_counts()
                  .rename(index={1: 'Success', 0: 'Failure'})
                  .reset_index()
                  .rename(columns={'index': 'Outcome', 'class': 'Count'}))
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Launch Outcomes for {selected_site}')
    return fig

# TASK 4: Scatter chart callback ([site-dropdown, payload-slider] -> success-payload-scatter-chart)
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                   (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)', y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=('Payload vs. Outcome (ALL Sites)'
               if selected_site == 'ALL'
               else f'Payload vs. Outcome — {selected_site}')
    )
    return fig

# ----- Run -----
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)

