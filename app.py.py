import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import plotly.graph_objects as go
import json

# --- BACKEND ENGINES ---
class AISynthesisFlightEngine:
    def __init__(self):
        self.scenarios = {
            "SCENARIO_CONFLICT": {
                "id": "SCENARIO_CONFLICT",
                "name": "Scenario A: ATC Climb vs. Active CDO & RTA",
                "atc_uplink": "CLIMB AND MAINTAIN FL360 DUE TO TRAFFIC",
                "ai_analysis": {
                    "conflict_detected": True,
                    "penalties": {
                        "cdo_impact": "Terminates idle-thrust Continuous Descent Operation",
                        "rta_delta_sec": 22,
                        "fuel_penalty_kg": 45
                    },
                    "counter_proposal": "Counter-Proposal: Request level-off at FL340 or delay climb initiation by 2 NM to preserve RTA and idle descent.",
                    "confidence": 0.96
                }
            },
            "SCENARIO_COMPATIBLE": {
                "id": "SCENARIO_COMPATIBLE",
                "name": "Scenario B: Compatible Direct Routing",
                "atc_uplink": "PROCEED DIRECT TO FIX_BETA, MAINTAIN 280 KTS",
                "ai_analysis": {
                    "conflict_detected": False,
                    "penalties": None,
                    "counter_proposal": "Clearance fully compatible with 4D-TBO profile. Optimal fuel efficiency maintained.",
                    "confidence": 0.99
                }
            }
        }
    def get_scenario_data(self, scenario_id):
        return self.scenarios.get(scenario_id, self.scenarios["SCENARIO_CONFLICT"])

engine = AISynthesisFlightEngine()

# --- DASH APP INITIALIZATION ---
app = dash.Dash(__name__)
server = app.server  # Required for Gunicorn cloud deployment

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#121212', 'color': '#E0E0E0', 'padding': '20px'}, children=[
    
    # Header Bar
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'borderBottom': '1px solid #333', 'paddingBottom': '15px', 'marginBottom': '20px'}, children=[
        html.H2("COCKPIT HMI // AI-ENHANCED 4D-TBO", style={'margin': '0', 'color': '#4CAF50'}),
        html.Div(style={'width': '350px'}, children=[
            html.Label("Select Flight Scenario Simulation:", style={'fontSize': '11px', 'color': '#B0B0B0', 'display': 'block', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='scenario-selector',
                options=[
                    {'label': 'Scenario A: ATC Climb vs CDO/RTA Conflict', 'value': 'SCENARIO_CONFLICT'},
                    {'label': 'Scenario B: Compatible Route Clearance', 'value': 'SCENARIO_COMPATIBLE'}
                ],
                value='SCENARIO_CONFLICT',
                clearable=False,
                style={'backgroundColor': '#2A2A2A', 'color': '#000'}
            )
        ])
    ]),

    # Main Grid Interface
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '2fr 1.2fr', 'gap': '20px'}, children=[
        
        # Left Column: Trajectory Map
        html.Div(children=[
            html.Div(style={'backgroundColor': '#1E1E1E', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'}, children=[
                html.H4("Horizontal Trajectory Map", style={'marginTop': '0', 'color': '#90CAF9'}),
                dcc.Graph(
                    id='hmi-map-display',
                    figure=go.Figure(
                        data=[
                            go.Scattermapbox(lat=[52.1, 52.2, 52.3, 52.5], lon=[10.0, 10.5, 11.0, 11.5], mode='lines+markers', name='Active 4D Route', line=dict(color='#2196F3', width=3)),
                        ],
                        layout=go.Layout(
                            mapbox=dict(style='carto-darkmatter', center=dict(lat=52.3, lon=10.8), zoom=8),
                            paper_bgcolor='#1E1E1E', plot_bgcolor='#1E1E1E', font=dict(color='#E0E0E0'),
                            margin=dict(l=0, r=0, t=0, b=0), height=300
                        )
                    )
                )
            ])
        ]),

        # Right Column: CPDLC & AI Advisory Panel
        html.Div(children=[
            html.Div(style={'backgroundColor': '#1E1E1E', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #1565C0'}, children=[
                html.H4("CPDLC Uplink & AI Synthesis", style={'marginTop': '0', 'color': '#90CAF9'}),
                
                html.Div(style={'backgroundColor': '#252525', 'padding': '10px', 'borderRadius': '4px', 'marginBottom': '15px'}, children=[
                    html.Span("INCOMING ATC UPLINK", style={'fontSize': '10px', 'color': '#FFC107', 'fontWeight': 'bold'}),
                    html.Div(id='atc-text-display', style={'fontSize': '14px', 'fontWeight': 'bold', 'marginTop': '5px'})
                ]),

                html.Div(id='ai-synthesis-card', style={'backgroundColor': '#2A2A2A', 'padding': '12px', 'borderRadius': '6px', 'marginBottom': '15px'})
            ])
        ])
    ])
])

@app.callback(
    [Output('atc-text-display', 'children'),
     Output('ai-synthesis-card', 'children')],
    [Input('scenario-selector', 'value')]
)
def update_hmi_scenario(scenario_id):
    data = engine.get_scenario_data(scenario_id)
    analysis = data['ai_analysis']
    
    if analysis['conflict_detected']:
        card_border = '#C62828'
        badge_color = '#C62828'
        badge_text = "CONFLICT DETECTED"
        penalties_div = html.Div(style={'fontSize': '12px', 'color': '#FF9800', 'margin': '10px 0', 'lineHeight': '1.5'}, children=[
            html.Div(f"• CDO Impact: {analysis['penalties']['cdo_impact']}"),
            html.Div(f"• RTA Deviation Error: +{analysis['penalties']['rta_delta_sec']} seconds"),
            html.Div(f"• Estimated Extra Fuel Burn: +{analysis['penalties']['fuel_penalty_kg']} kg")
        ])
    else:
        card_border = '#4CAF50'
        badge_color = '#4CAF50'
        badge_text = "OPTIMIZED & COMPATIBLE"
        penalties_div = html.Div("• No hidden trajectory or energy penalties calculated.", style={'fontSize': '12px', 'color': '#4CAF50', 'margin': '10px 0'})

    card_content = [
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
            html.Span(badge_text, style={'backgroundColor': badge_color, 'color': 'white', 'padding': '2px 6px', 'borderRadius': '3px', 'fontSize': '10px', 'fontWeight': 'bold'}),
            html.Span(f"AI Conf: {int(analysis['confidence']*100)}%", style={'fontSize': '11px', 'color': '#B0B0B0'})
        ]),
        penalties_div,
        html.Hr(style={'borderColor': '#444', 'margin': '10px 0'}),
        html.P(analysis['counter_proposal'], style={'fontSize': '12px', 'color': '#E0E0E0', 'lineHeight': '1.4', 'margin': '0 0 12px 0'}),
        html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
            html.Button("EXECUTE COUNTER-PROPOSAL", style={'flex': '1', 'backgroundColor': '#1565C0', 'color': 'white', 'border': 'none', 'padding': '8px', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '11px', 'fontWeight': 'bold'}),
            html.Button("ACCEPT RAW UPLINK", style={'flex': '1', 'backgroundColor': '#424242', 'color': 'white', 'border': 'none', 'padding': '8px', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '11px'})
        ])
    ]
    
    return data['atc_uplink'], html.Div(style={'borderLeft': f'4px solid {card_border}', 'paddingLeft': '10px'}, children=card_content)

if __name__ == '__main__':
    app.run(debug=True, port=8050)