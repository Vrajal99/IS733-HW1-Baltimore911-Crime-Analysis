#!/usr/bin/env python
# coding: utf-8

# In[2]:


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the dataset
df = pd.read_csv('data/Baltimore911.csv', low_memory=False)

# Convert relevant columns to appropriate data types
df['CrimeDate'] = pd.to_datetime(df['CrimeDate'])
df['CrimeTime'] = pd.to_datetime(df['CrimeTime'], format='%H:%M:%S')

# Create a Dash web application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Crime Patterns Dashboard"),
    
    # Dropdown for selecting location
    dcc.Dropdown(
        id='location-dropdown',
        options=[
            {'label': location, 'value': location}
            for location in df['Location'].unique()
        ],
        value=df['Location'].unique()[0],  # Set default value
        multi=False
    ),
    
    # Line plot for temporal patterns (Incidents per year)
    dcc.Graph(id='temporal-patterns'),
    
    # Bar plot for crime type distribution
    dcc.Graph(id='crime-type-distribution'),
    
    # Heatmap for week vs hour of crime incidents
    dcc.Graph(id='heatmap-week-hour'),
    
    # Heatmap for week vs month of crime incidents
    dcc.Graph(id='heatmap-week-month'),
    
    # Heatmap for month vs year of crime incidents
    dcc.Graph(id='heatmap-month-year'),
    
    # Frequency of top 5 crimes based on location
    dcc.Graph(id='top-5-crimes-location'),
    
    # Density map of crime incidents per location
    dcc.Graph(id='density-map'),
])

# Callbacks to update plots based on user input
@app.callback(
    [Output('temporal-patterns', 'figure'), Output('crime-type-distribution', 'figure'),
     Output('heatmap-week-hour', 'figure'), Output('heatmap-week-month', 'figure'),
     Output('heatmap-month-year', 'figure'), Output('top-5-crimes-location', 'figure'),
     Output('density-map', 'figure')],
    [Input('location-dropdown', 'value')]
)
def update_plots(selected_location):
    # Filter data based on the selected location
    filtered_df = df[df['Location'] == selected_location]
    
    # Create temporal patterns plot (Incidents per year)
    temporal_plot = px.line(
        filtered_df.groupby(filtered_df['CrimeDate'].dt.year).size().reset_index(name='Incidents'),
        x='CrimeDate', y='Incidents',
        title=f'Temporal Patterns for {selected_location}',
        labels={'Incidents': 'Number of Incidents'},
    )
    
    # Create crime type distribution plot
    crime_type_plot = px.bar(
        filtered_df['Description'].value_counts().reset_index(name='Count'),
        x='index', y='Count',
        title=f'Crime Type Distribution for {selected_location}',
        labels={'index': 'Crime Type', 'Count': 'Number of Incidents'},
    )
    
    # Create heatmap for week vs hour of crime incidents
    heatmap_week_hour = px.density_heatmap(
        filtered_df, x=filtered_df['CrimeTime'].dt.hour, y=filtered_df['CrimeTime'].dt.strftime('%A'),
        title=f'Week vs Hour Heatmap for {selected_location}',
        labels={'x': 'Hour of Day', 'y': 'Day of Week'},
        nbinsx=24, nbinsy=7
    ).update_xaxes(categoryorder='total ascending')
    
    # Create heatmap for week vs month of crime incidents
    heatmap_week_month = px.density_heatmap(
        filtered_df, x=filtered_df['CrimeDate'].dt.month, y=filtered_df['CrimeDate'].dt.strftime('%A'),
        title=f'Week vs Month Heatmap for {selected_location}',
        labels={'x': 'Month', 'y': 'Day of Week'},
        nbinsx=12, nbinsy=7
    ).update_xaxes(categoryorder='total ascending')
    
    # Create heatmap for month vs year of crime incidents
    heatmap_month_year = px.density_heatmap(
        filtered_df, x=filtered_df['CrimeDate'].dt.year, y=filtered_df['CrimeDate'].dt.month,
        title=f'Month vs Year Heatmap for {selected_location}',
        labels={'x': 'Year', 'y': 'Month'},
        nbinsx=df['CrimeDate'].dt.year.nunique(), nbinsy=12
    ).update_xaxes(categoryorder='total ascending')
    
    # Frequency of top 5 crimes based on location
    top_5_crimes_location = px.bar(
        filtered_df['Description'].value_counts().head(5).reset_index(name='Count'),
        x='index', y='Count',
        title=f'Top 5 Crimes in {selected_location}',
        labels={'index': 'Crime Type', 'Count': 'Number of Incidents'},
    )
    
    # Density map of crime incidents per location (using latitude and longitude)
    density_map = px.density_mapbox(
        df, lat='Latitude', lon='Longitude', z='Total Incidents',
        title=f'Density Map of Crime Incidents in Baltimore',
        labels={'Total Incidents': 'Number of Incidents'},
        center={'lat': 39.29, 'lon': -76.61},
        zoom=10,
    )
    
    density_map.update_layout(mapbox_style="stamen-terrain")
    
    return temporal_plot, crime_type_plot, heatmap_week_hour, heatmap_week_month, heatmap_month_year, top_5_crimes_location, density_map

if __name__ == '__main__':
    app.run_server(port=4741)


# In[ ]:




