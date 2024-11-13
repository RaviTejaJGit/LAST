import dash
from dash import dcc, html, Input, Output, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
import subprocess
from flask import send_from_directory
from datetime import datetime, timedelta

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

def register_callbacks(app):

    @app.callback(
        Output('modal', 'is_open'),
        Output('textarea-content', 'value'),
        [Input('open-popup', 'n_clicks'),
        Input('submit-button', 'n_clicks')],
        [State('modal', 'is_open'),
        State('textarea-content', 'value')]
    )
    def update_modal(open_clicks, submit_clicks, is_open, textarea_value):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, textarea_value

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_id == 'open-popup':
            # Open the modal and load the content
            return True, read_file()
        elif triggered_id == 'submit-button':
            # Save the content and close the modal
            save_file(textarea_value)
            return False, textarea_value

        return is_open, textarea_value

    #CSV callback
    @app.callback(
        Output('download-file', 'data'),
        Input('excel-logo', 'n_clicks'),
        prevent_initial_call=True
    )
    def download_csv_file(n_clicks):
        if n_clicks:
            file_path = 'screenshots/responses.csv'
            return dcc.send_file(file_path)
        return None

    # Callback to control the visibility of the input fields based on dropdown selection
    @app.callback(
        [Output('url-div', 'style'), Output('depth-div', 'style')],
        [Input('dropdown', 'value')]
    )
    def toggle_input_fields(dropdown_value):
        if dropdown_value == 'remote':
            return [{'flex': '1', 'display': 'block', 'marginRight': '10px'}, {'flex': '1', 'display': 'block'}]
        else:
            return [{'flex': '1', 'display': 'none'}, {'flex': '1', 'display': 'none'}]
        
    @app.callback(
        Output('play-button', 'src'),
        Output('button-state', 'data'),
        Output('script-executed', 'data'),
        Input('play-button', 'n_clicks'),
        Input('dropdown', 'value'),
        State('button-state', 'data'),
        State('script-executed', 'data'),
        State('url-input', 'value'),  # Capture URL input
        State('depth-input', 'value')  # Capture Depth input
    )
    def toggle_play_pause(n_clicks, dropdown_value, current_state, script_executed, url, depth):
        global prev_dropdown_value

        if n_clicks is None:
            return '/assets/play.png', 'play', script_executed

        #print("Line 59",dropdown_value, prev_dropdown_value)

        if dropdown_value != prev_dropdown_value:
            #print(f"line 62 Dropdown value changed from {prev_dropdown_value} to {dropdown_value}")
            new_image = '/assets/play.png'
            new_state = 'play'
            with open('signal.txt', 'r+') as file:
                lines = file.readlines()

                while len(lines) < 2:
                    lines.append('False\n')
                # Reset both the first and second lines
                lines[0] = 'False\n'
                lines[1] = 'False\n'

                file.seek(0)
                file.writelines(lines)
                file.truncate()
            prev_dropdown_value = dropdown_value
        else:
            new_state = 'pause' if current_state == 'play' else 'play'
            new_image = '/assets/pause.png' if new_state == 'pause' else '/assets/play.png'
        
        if new_state == 'pause':
            if dropdown_value == 'local':
                print("Starting livemain.py...")
                subprocess.Popen(['python', 'livemain.py'], shell=True)
                script_executed = True
            elif dropdown_value == 'remote':
                print(f"Starting lasttrigger.py with URL: {url} and Depth: {depth}")
                subprocess.Popen(['python', 'lasttrigger.py', url, str(depth)], shell=True)
                script_executed = True

            with open('signal.txt', 'r+') as file:
                lines = file.readlines()
                while len(lines) < 2:
                    lines.append('False\n')
                # Modify only the necessary line based on the dropdown value
                if dropdown_value == 'local':
                    lines[0] = 'True\n'  # Set first line to True
                elif dropdown_value == 'remote':
                    lines[1] = 'True\n'  # Set second line to True

                file.seek(0)
                file.writelines(lines)
                file.truncate()

        elif new_state == 'play':
            script_executed = False
            with open('signal.txt', 'r+') as file:
                lines = file.readlines()

                # Modify only the necessary line based on the dropdown value
                if dropdown_value == 'local':
                    lines[0] = 'False\n'  # Set first line to False
                elif dropdown_value == 'remote':
                    lines[1] = 'False\n'  # Set second line to False

                file.seek(0)
                file.writelines(lines)
                file.truncate()

        return new_image, new_state, script_executed


    @app.callback(
        Output('image-container', 'children'),
        Output('selected-pdf', 'data'),
        Input('interval-component', 'n_intervals')
    )


    def update_images(n_intervals):

        # Get all screenshot images
        image_files = sorted(
            [f for f in os.listdir('screenshots') if f.endswith('.png')],
            key=lambda x: os.path.getmtime(os.path.join('screenshots', x)),
            reverse=True
        )

        pdf_files = [f for f in os.listdir('screenshots') if f.endswith('.pdf')]

        rows = []
        pdf_data = None
        num_images = len(image_files)
        
        def get_percentage_from_signal():
            try:
                with open('signal.txt', 'r') as file:
                    lines = file.readlines()
                    if len(lines) >= 3:
                        parts = lines[2].strip().split()
                        if len(parts) == 2:
                            image_name = parts[0]
                            percentage = parts[1]
                        return image_name, percentage
            except Exception as e:
                print(f"Error reading signal.txt: {e}")
            return None,None
        
        def create_progress_bar(progress_value, total_length=50):
            filled_length = int(total_length * progress_value // 100)  # Calculate filled portion
            bar = '█' * filled_length + '-' * (total_length - filled_length)  # Create the bar
            return f'[{bar}] {progress_value}%'

        for index, image_file in enumerate(image_files):
            base_name = os.path.splitext(image_file)[0]  # Get base name without extension

        # Check if there's a matching PDF file
            matching_pdf = next((pdf for pdf in pdf_files if base_name in pdf), None)

            if matching_pdf:
                pdf_data = f'/screenshots/{matching_pdf}'
                pdf_display = html.Iframe(
                    src=pdf_data,
                    style={'width': '100%', 'height': '400px'})
                processing_message = pdf_display
            else:
                image_name_from_signal, percentage_from_signal = get_percentage_from_signal()

                if percentage_from_signal and base_name + '.png' == image_name_from_signal:
                    progress_value = int(percentage_from_signal.strip('%'))
                    processing_message = create_progress_bar(progress_value)
                    
                else:
                    processing_message = html.Img(
                        src="/assets/rotatinghourglass.gif.url",  # Path to the GIF
                        style={
                            'height': '100px',  # Adjust the size as needed
                            'width': '100px'
                        }
                    )
            # Calculate row number: bottom image is 1
            row_number = num_images - index

            row = html.Div(
                style={
                    'display': 'flex', 
                    'alignItems': 'center', 
                    'marginBottom': '10px', 
                    'border': '1px solid black',  # Add border for grid lines
                    'padding': '10px'  # Add padding for spacing
                }, 
                children=[
                    html.Div(f'{row_number}', style={'flex': '0 0 10%', 'textAlign': 'center','fontSize': '24px'}),
                    html.Img(
                        src=f'/screenshots/{image_file}', 
                        style={
                            'flex': '0 0 40%',
                            'width': 'auto',  # Adjust width to 100% of container
                            'height': '400px',  # Keep aspect ratio
                            'marginRight': '10px'
                        }
                    ),
                    html.Div(processing_message,
                            style={
                            'flex': '0 0 40%',  # 40% width for PDF or processing message
                            'display': 'flex',  # Use flexbox for centering
                            'justifyContent': 'center',  # Center horizontally
                            'alignItems': 'center',  # Center vertically
                            'height': '100%'
                        }),  # Add processing message
                ]
            )
            rows.append(row)
        
        return rows, pdf_data