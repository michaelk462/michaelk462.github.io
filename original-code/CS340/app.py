# *****CODE INFORMATION*****
# Name: Michael King
# File: app.py
# Assignment: CS 340 Animal Shelter Dashboard (Original)
# University: SNHU


# ***Imports***
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_leaflet as dl
import plotly.express as px
import base64
import os
import numpy as np
import pandas as pd


#### FIX ME #####
# change animal_shelter and AnimalShelter to match your CRUD Python module file name and class name
from animalshelter import AnimalShelter

###########################
# Data Manipulation / Model
###########################
# FIX ME update with your username and password and CRUD Python module name

username = "aacuser"
password = "password1" # changed password

# Connect to database via CRUD Module
db = AnimalShelter(username, password)

# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
df = pd.DataFrame.from_records(db.read({}))

# MongoDB v5+ is going to return the '_id' column and that is going to have an 
# invalid object type of 'ObjectID' - which will cause the data_table to crash - so we remove
# it in the dataframe here. The df.drop command allows us to drop the column. If we do not set
# inplace=True - it will return a new dataframe that does not contain the dropped column(s)
df.drop(columns=['_id'],inplace=True)

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)


#########################
# Dashboard Layout / View
#########################
app = Dash(__name__)

# Grazioso Salvare’s logo
image_filename = 'Grazioso Salvare Logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


# Unique Identifier
app.layout = html.Div([
        html.Center([
        html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),height=150),
        html.B(html.H1('CS-340 Animal Shelter Dashboard')),
        html.P('Created by Michael King / Date: 2/22/2026'),
    ]),
    html.Hr(),
    
    #Filter Radio Buttons
    html.Div(
        children=[
        html.Label("Filter by Rescue Type:"),
        dcc.RadioItems(
            id='filter-type',
            options=[
                {'label': 'Water Rescue', 'value': 'Water Rescue'},
                {'label': 'Mountain/Wilderness', 'value': 'Mountain Rescue'},
                {'label': 'Disaster/Tracking', 'value': 'Disaster Rescue'},
                {'label': 'Reset All Animals', 'value': 'Reset'},
            ],
            value='Reset',
            labelStyle={'display': 'inline-block', 'margin': '10px'}
        ) 
        ],
    style={'textAlign': 'center'}
    ),
    
    # Dash Table with Features
    dash_table.DataTable(id='datatable-id',
                         columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
                         data=df.to_dict('records'),
                         #Interactive Features
                         #Features for interactive data table to make it user-friendly for client
                        row_selectable = "single", # makes single rows selectable
                        selected_rows=[1], # selects row 1 by default
                        page_action="native", # page action is native
                        page_current=0, # starts at page 0
                        page_size=10, # 10 rows are visible in one page
                        sort_action="native", # sorting is native
                        sort_mode="multi", # multi-sort mode
                        filter_action="native", # filtering is native
                         #Features for each table cell
                        style_cell={
                            'textAlign': 'left', # text is aligned to the left
                            'minWidth': '100px', # minimum width
                            'width': '150px', # width
                            'maxWidth': '300px', # maximum widtg
                            'overflow': 'hidden', # hidden cell overflow
                            'textOverflow': 'ellipsis', # ellipsis text overflow
                        },

                        #Features for the header
                        style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                        },

                        #Data Features
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }
                        ]
    ),
    html.Br(),
    html.Hr(),
#This sets up the dashboard so that your chart and your geolocation chart are side-by-side
    html.Div(
        className='row',
        style={'display' : 'flex'},
        children=[
            html.Div(id='graph-id', className='col s12 m6'),
            html.Div(id='map-id',className='col s12 m6')
        ]
    )
])

#############################################
# Interaction Between Components / Controller
#############################################



    
@app.callback(
    Output('datatable-id','data'),
    [Input('filter-type', 'value')]
)
def update_dashboard(filter_type):
    # Define breed/sex filters per rescue type
    # These match the Grazioso Salvare preferred breeds
    
    # Filters Water Rescue Dog Breeds from 26-156 weeks
    if filter_type == 'Water Rescue':
        filtered = df[
            (df['breed'].isin(['Labrador Retriever Mix',
                               'Chesapeake Bay Retriever',
                               'Newfoundland'])) &
            (df['sex_upon_outcome'] == 'Intact Female') &
            (df['age_upon_outcome_in_weeks'] >= 26) &
            (df['age_upon_outcome_in_weeks'] <= 156)
        ]
        
    # Filters Mountain Rescue Dog Breeds from 26-156 weeks
    elif filter_type == 'Mountain Rescue':
        filtered = df[
            (df['breed'].isin(['German Shepherd',
                               'Alaskan Malamute',
                               'Old English Sheepdog',
                               'Siberian Husky',
                               'Rottweiler'])) &
            (df['sex_upon_outcome'] == 'Intact Male') &
            (df['age_upon_outcome_in_weeks'] >= 26) &
            (df['age_upon_outcome_in_weeks'] <= 156)
        ]
        
    # Filters Mountain Rescue Dog Breeds from 20-300 weeks
    elif filter_type == 'Disaster Rescue':
        filtered = df[
            (df['breed'].isin(['Doberman Pinscher',
                               'German Shepherd',
                               'Golden Retriever',
                               'Bloodhound',
                               'Rottweiler'])) &
            (df['sex_upon_outcome'] == 'Intact Male') &
            (df['age_upon_outcome_in_weeks'] >= 20) &
            (df['age_upon_outcome_in_weeks'] <= 300)
        ] 
    else:
        filtered = df
    return filtered.to_dict('records')

# Display the breeds of animal based on quantity represented in
# the data table
@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-id', "derived_virtual_data")]
)
def update_graphs(viewData):
    if viewData is None:
        return []
    
    dff = pd.DataFrame.from_dict(viewData)
    
    if dff.empty or 'breed' not in dff.columns:
        return[]
    
    return [
        dcc.Graph(
            figure=px.pie(
                dff,
                names='breed',
                title='Preferred Animals by Breed',
                hole=0.3
            ).update_traces(textinfo='percent+label')
        )
    ]
    
#This callback will highlight a cell on the data table when the user selects it
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    if not selected_columns:
        return []
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# This callback will update the geo-location chart for the selected data entry
# derived_virtual_data will be the set of data available from the datatable in the form of 
# a dictionary.
# derived_virtual_selected_rows will be the selected row(s) in the table in the form of
# a list. For this application, we are only permitting single row selection so there is only
# one value in the list.
# The iloc method allows for a row, column notation to pull data from the datatable
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):  
    if viewData is None:
        return []
    
    dff = pd.DataFrame.from_dict(viewData)
    
    if dff.empty:
        return []
    
    # Default to first row if nothing is selected
    row = index[0] if index and len(index) > 0 else 0
    
    # Guard against row index exceeding dataframe length
    if row >= len(dff):
        row = 0
        
    # Guard Against missing lat/lon data
    try:
        lat = dff.iloc[row, 13]
        lon = dff.iloc[row, 14]
        breed = dff.iloc[row, 4]
        name = dff.iloc [row, 9]
    except (IndexError, KeyError):
        return []
    
        
    # Austin TX is at [30.75,-97.48]
    return [
        dl.Map(style={'width': '1000px', 'height': '500px'}, 
               center=[30.75,-97.48], 
               zoom=10, children=[
            dl.TileLayer(id="base-layer-id"),
            # Marker with tool tip and popup
            # Column 13 and 14 define the grid-coordinates for the map
            # Column 4 defines the breed for the animal
            # Column 9 defines the name of the animal
            dl.Marker(position=[dff.iloc[row,13],dff.iloc[row,14]], children=[
                dl.Tooltip(dff.iloc[row,4]),
                dl.Popup([
                    html.H1("Animal Name"),
                    html.P(dff.iloc[row,9])
                ])
            ])
        ])
    ]


# Run app and display result in jupyterlab mode, note, if you have previously run a prior app, the default port of 8050 may not be available, if so, try setting an alternate port.
if __name__ == '__main__':
    app.run(debug=True)