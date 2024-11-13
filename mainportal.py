import dash
from dash import dcc, html, Input, Output, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
import subprocess
from flask import send_from_directory
from datetime import datetime, timedelta
from callback import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize global variable for tracking process
prev_dropdown_value = 'local'

def read_file():
    file_path = 'queries.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    return ''

# Function to save content to queries.txt
def save_file(content):
    file_path = 'queries.txt'
    with open(file_path, 'w') as file:
        file.write(content)

app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'}, children=[
    # Top half
    html.Div(style={'flex': '0 0 20%', 'borderBottom': '2px solid black', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}, children=[
        html.Img(src='/assets/logo.png', style={'height': '60px', 'marginBottom': '10px'}),  # Replace Tektronix with logo.png
        html.Div(style={'width': '80%', 'display': 'flex', 'alignItems': 'center'}, children=[
            dcc.Dropdown(
                id='dropdown',
                options=[
                    {'label': 'Local', 'value': 'local'},
                    {'label': 'Remote', 'value': 'remote'}
                ],
                placeholder='Select an option',
                value='local',  # Set default value to 'local'
                style={'flex': '1'}
            ),
            html.Img(src='/assets/play.png', id='play-button', style={'width': '80px', 'height': '80px', 'marginLeft': '10px', 'cursor': 'pointer'}),
            html.Button(
                html.Img(src='/assets/queries.jpg', style={'width': '100px', 'height': '100px'}),
                id='open-popup',
                style={'border': 'none', 'background': 'none'}
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader("Queries",style={'fontWeight': 'bold','fontSize': '1.5rem'}),
                    dbc.ModalBody(
                        dcc.Textarea(
                            id='textarea-content',
                            style={'width': '100%', 'height': '500px','backgroundColor': '#6c757d','color': 'white'}
                        )
                    ),
                    dbc.ModalFooter(
                        html.Button("Submit", id='submit-button', className='ml-auto')
                    )
                ],
                id='modal',
                is_open=False,
                centered=True,  # Ensure the modal is   centered
                backdrop=False,
                style={
                    'width': '75vw',
                    'display': 'flex',
                    'alignItems': 'center',  # Vertical alignment
                    'justifyContent': 'center',  # Horizontal alignment
                    'zIndex': '1050',  # Ensure the modal is always on top
                    'position': 'fixed',  # Fixed positioning
                    'top': '50%',  # Center vertically
                    'left': '50%',  # Center horizontally
                    'transform': 'translate(-50%, -50%)'  # Offset by half width/height
                },
            ),

            html.Img(src='/assets/excel.jpg', id='excel-logo', style={'width': '80px', 'height': '80px', 'marginLeft': '10px'}),
            html.Button('Open responses.csv', id='open-csv', style={'display': 'none'}),  # Hidden button
            dcc.Download(id='download-file'),  # Hidden download component
            dcc.Store(id='button-state', data='play'),  # Store component to keep track of the button state
            dcc.Store(id='script-executed', data=False)  # Store to track if the script has been executed
        ]),
        
        # URL and Depth inputs, conditionally displayed
        html.Div(style={'width': '80%', 'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'}, children=[
            html.Div([
                html.Label('URL:'),
                dcc.Input(id='url-input', type='text', placeholder='Example: https://134.64.246.152:4200/login', style={'width': '100%', 'height': '35px'})
            ], style={'flex': '1', 'display': 'none'}, id='url-div'),  # Initially hidden
            html.Div([
                html.Label('Depth:'),
                dcc.Input(id='depth-input', type='number', placeholder='Enter Depth', style={'width': '100%', 'height': '35px'})
            ], style={'flex': '1', 'display': 'none'}, id='depth-div')  # Initially hidden
        ]),

        html.Div(id='output-div', style={'marginTop': '10px', 'width': '80%'})
    ]),

    # Bottom half: scrollable image container
    html.Div(style={'flex': '1', 'overflowY': 'scroll', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}, children=[
        html.Div(id='image-container', style={'display': 'flex', 'flexDirection': 'column'}),
        dcc.Store(id='selected-pdf', data=None),  # Store to track selected PDF

        # Interval component to trigger image updates
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # Update every 5 seconds
            n_intervals=0  # Start the interval
        )
    ]),

])

register_callbacks(app)

# Serve the screenshots directory as a static folder
@app.server.route('/screenshots/<path:filename>')
def serve_screenshots(filename):
    return send_from_directory('screenshots', filename)

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=1111)