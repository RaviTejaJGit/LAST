import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Function to read content from queries.txt
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

app.layout = html.Div([
    html.Button(
        html.Img(src='/assets/queries.jpg', style={'width': '100px', 'height': '100px'}),
        id='open-popup',
        style={'border': 'none', 'background': 'none'}
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("Queries"),
            dbc.ModalBody(
                dcc.Textarea(
                    id='textarea-content',
                    style={'width': '100%', 'height': '400px'}
                )
            ),
            dbc.ModalFooter(
                html.Button("Submit", id='submit-button', className='ml-auto')
            )
        ],
        id='modal',
        is_open=False
    ),
    html.Div(id='output-div', style={'marginTop': '10px', 'width': '80%'})

])

#chek

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

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8080)