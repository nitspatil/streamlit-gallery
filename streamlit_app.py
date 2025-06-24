import dash
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_iconify import DashIconify

# --- 1. DATA LOADING AND PREPARATION ---
# TODO: PULL IN YOUR MASTER DATA SHEET HERE
# Instead of using this mock dictionary, you can load your data from an Excel or CSV file.
# For example, if your data is in 'master_data.xlsx':
#
# 1. Load the relevant sheets into pandas DataFrames:
#    df_servicelines = pd.read_excel('master_data.xlsx', sheet_name='ServiceLines')
#    df_forecast = pd.read_excel('master_data.xlsx', sheet_name='BenchForecast')
#    df_funnel = pd.read_excel('master_data.xlsx', sheet_name='InterviewFunnel')
#    df_allocations = pd.read_excel('master_data.xlsx', sheet_name='RecentAllocations')
#    df_talent = pd.read_excel('master_data.xlsx', sheet_name='TalentPool')
#
# 2. Then, use these DataFrames below instead of the MOCK_DATA dictionary.
#    For example, for service lines, you would iterate over df_servicelines.iterrows().

MOCK_DATA = {
    'serviceLines': {
        'dpe': {'name': "DPE", 'fullName': "Digital Process Engineering", 'total': 850, 'billed': 710, 'bench': 95, 'enablement': 45},
        'cx': {'name': "CX", 'fullName': "Customer Experience", 'total': 620, 'billed': 550, 'bench': 40, 'enablement': 30},
        'ci': {'name': "CI", 'fullName': "Cloud & Infrastructure", 'total': 480, 'billed': 410, 'bench': 55, 'enablement': 15},
        'da': {'name': "DA", 'fullName': "Data & Analytics", 'total': 350, 'billed': 290, 'bench': 35, 'enablement': 25},
    },
    'benchForecast': {
        'under15': 18,
        'between16and30': 25,
        'between31and45': 32,
    },
    'interviewFunnel': [65, 55, 35, 25],
    'recentAllocations': [
        {'id': 1, 'name': 'Ananya Sharma', 'prevClient': 'On Bench', 'newClient': 'CVS', 'role': 'Sr. Java Developer', 'recruiter': 'Rohan Gupta'},
        {'id': 2, 'name': 'Ben Carter', 'prevClient': 'Walmart', 'newClient': 'Walmart (New POD)', 'role': 'Data Engineer', 'recruiter': 'Priya Singh'},
        {'id': 3, 'name': 'Chloe Davis', 'prevClient': 'On Bench', 'newClient': 'United Health', 'role': 'Cloud Architect', 'recruiter': 'Rohan Gupta'},
    ],
    'talentPool': [
        {'id': 1, 'name': 'Vikram Rathore', 'eid': '10234', 'status': 'On Bench', 'client': 'Walmart', 'skills': ['Java', 'Spring', 'Kafka'], 'availability': 'Immediate', 'benchSince': 'June 5', 'process': 'Interviewing w/ CVS', 'recruiter': 'Priya Singh'},
        {'id': 2, 'name': 'Samantha Lee', 'eid': '10567', 'status': 'Billed', 'client': 'United Health', 'skills': ['AWS', 'Terraform', 'Kubernetes'], 'availability': 'Project Ends: July 15', 'benchSince': None, 'process': 'Not in process', 'recruiter': 'Rohan Gupta'},
        {'id': 3, 'name': 'Rajesh Kumar', 'eid': '10112', 'status': 'On Bench', 'client': 'Morgan Stanley', 'skills': ['Python', 'Spark', 'SQL'], 'availability': 'Immediate', 'benchSince': 'May 20', 'process': 'Offer from Walmart', 'recruiter': 'Priya Singh'},
    ]
}

# --- 2. REUSABLE COMPONENT FUNCTIONS ---

def create_service_line_card(data):
    """Generates a Doughnut chart card for a service line."""
    chart_figure = go.Figure(
        data=[go.Pie(
            labels=['Billed', 'Bench', 'Enablement'],
            values=[data['billed'], data['bench'], data['enablement']],
            hole=0.7,
            marker_colors=['#4f46e5', '#f97316', '#a8a29e'],
            textinfo='none',
            hoverinfo='label+percent+value'
        )]
    )
    chart_figure.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[dict(text=str(data['total']), x=0.5, y=0.5, font_size=28, showarrow=False)],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return dbc.Card(
        dbc.CardBody([
            html.H2(data['name'], className="text-lg font-bold text-slate-800"),
            html.P(data['fullName'], className="text-sm text-slate-500 mb-2"),
            dcc.Graph(figure=chart_figure, config={'displayModeBar': False}, style={'height': '200px'})
        ]),
        className="shadow-sm hover-lift"
    )

def create_funnel_chart(data):
    """Generates a horizontal Bar chart to act as a funnel."""
    labels = ['New', 'Interviewed', 'Offered', 'Allocated']
    chart_figure = go.Figure(go.Bar(
        y=labels,
        x=data,
        orientation='h',
        marker=dict(color=['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe'], line=dict(width=0)),
        text=data,
        textposition='auto',
    ))
    chart_figure.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=True, showgrid=False),
        margin=dict(t=20, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#1e293b", weight="bold")
    )
    return dcc.Graph(figure=chart_figure, config={'displayModeBar': False})

def create_skill_tag(skill):
    """Creates a colored badge for a skill."""
    colors = ["primary", "success", "info", "warning", "danger", "secondary"]
    color_class = colors[len(skill) % len(colors)]
    return dbc.Badge(skill, color=color_class, className="me-1")

# --- 3. DASH APP INITIALIZATION ---

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
# Add a class for the hover-lift effect
app.clientside_callback(
    """
    function(id) {
        // This is just to make the CSS available, no actual callback logic needed
        return '';
    }
    """,
    dash.dependencies.Output('dummy-output-for-css', 'children'),
    [dash.dependencies.Input('dummy-output-for-css', 'id')]
)
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .hover-lift {
                transition: all 0.2s ease-in-out;
            }
            .hover-lift:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
            }
        </style>
    </head>
    <body style="background-color: #f1f5f9; font-family: sans-serif;">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div id="dummy-output-for-css"></div>
    </body>
</html>
"""

# --- 4. LAYOUT DEFINITION ---

# Header
header = html.Header([
    html.H1("Internal Talent & Bench Management Hub", className="text-3xl font-bold text-slate-800"),
    html.P("A single source of truth for our internal talent landscape.", className="mt-1 text-slate-500"),
], className="mb-4")

# Filters
filters = dbc.Card(dbc.CardBody(
    dbc.Row([
        dbc.Col([
            DashIconify(icon="lucide:layers", width=20, className="text-slate-500 me-2"),
            html.Span("Service Line:", className="font-semibold text-slate-700 me-3"),
            dbc.Checklist(
                options=[{"label": sl['name'], "value": sl['name']} for sl in MOCK_DATA['serviceLines'].values()],
                value=[sl['name'] for sl in MOCK_DATA['serviceLines'].values()],
                inline=True,
                id="sl-filter"
            )
        ], width="auto"),
        dbc.Col(html.Div(className="vr"), width="auto", className="d-none d-md-block"),
        dbc.Col([
             DashIconify(icon="lucide:calendar", width=20, className="text-slate-500 me-2"),
             html.Span("Date Range:", className="font-semibold text-slate-700 me-2"),
             dbc.Select(
                 options=[
                     {"label": "Last 30 Days", "value": "30"},
                     {"label": "Last Quarter", "value": "90"},
                 ],
                 value="30",
                 size="sm",
                 style={"width": "150px"}
             )
        ], width="auto")
    ], align="center")
), className="mb-4 shadow-sm")

# Command Center - Service Line Cards
command_center = dbc.Row(
    [dbc.Col(create_service_line_card(sl_data), width=12, md=6, lg=3) for sl_data in MOCK_DATA['serviceLines'].values()],
    className="mb-4"
)

# Bench Forecast Cards
bench_forecast = dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P("Coming to Bench (<15 Days)", className="font-semibold text-slate-600"),
        html.P(f"{MOCK_DATA['benchForecast']['under15']}", className="text-4xl font-bold text-danger mt-2")
    ]), className="shadow-sm hover-lift")),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P("Coming to Bench (16-30 Days)", className="font-semibold text-slate-600"),
        html.P(f"{MOCK_DATA['benchForecast']['between16and30']}", className="text-4xl font-bold text-warning mt-2")
    ]), className="shadow-sm hover-lift")),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P("Coming to Bench (31-45 Days)", className="font-semibold text-slate-600"),
        html.P(f"{MOCK_DATA['benchForecast']['between31and45']}", className="text-4xl font-bold text-success mt-2")
    ]), className="shadow-sm hover-lift")),
], className="mb-4")

# Talent Pipeline Section
talent_pipeline = dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([
        html.H3("Bench Candidate Interview Funnel", className="text-xl font-bold text-slate-800"),
        html.P("Internal mobility pipeline.", className="text-sm text-slate-500 mb-4"),
        html.Div(create_funnel_chart(MOCK_DATA['interviewFunnel']), style={'height': '256px'})
    ]), className="shadow-sm"), lg=5),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.H3("Recent Allocations", className="text-xl font-bold text-slate-800"),
        html.P("Successful placements in the last 30 days.", className="text-sm text-slate-500 mb-4"),
        dbc.Table.from_dataframe(
            pd.DataFrame(MOCK_DATA['recentAllocations']).rename(columns={
                'name': 'Name',
                'role': 'Role',
                'recruiter': 'Recruiter'
            }).assign(Movement=lambda x: x['prevClient'] + " → " + x['newClient'])[['Name', 'Movement', 'Role', 'Recruiter']],
            striped=True,
            hover=True,
            responsive=True,
            bordered=False,
            className="text-sm"
        )
    ]), className="shadow-sm"), lg=7)
], className="mb-4")

# Talent Pool Explorer Table
talent_pool_table_header = html.Thead(html.Tr([
    html.Th("Profile"), html.Th("Status"), html.Th("Skills"), html.Th("Availability"), html.Th("Process")
]))

talent_pool_table_body = html.Tbody([
    html.Tr([
        html.Td([html.Div(c['name'], className="font-medium text-slate-900"), html.Div(f"EID: {c['eid']}", className="text-slate-400")]),
        html.Td([
            html.Span([
                DashIconify(icon="lucide:sofa", className="text-warning me-2"), " On Bench"
            ], className="d-flex align-items-center") if c['status'] == 'On Bench' else html.Span([
                DashIconify(icon="lucide:briefcase", className="text-primary me-2"), " Billed"
            ], className="d-flex align-items-center"),
            html.Div(f"(Ex: {c['client']})" if c['status'] == 'On Bench' else f"Client: {c['client']}", className="text-slate-400")
        ]),
        html.Td([create_skill_tag(skill) for skill in c['skills']]),
        html.Td([
            html.Div(c['availability'], className="font-semibold"),
            html.Div(f"Since: {c['benchSince']}", className="text-slate-400") if c.get('benchSince') else ""
        ]),
        html.Td(c['process'])
    ]) for c in MOCK_DATA['talentPool']
])

talent_explorer = dbc.Card(dbc.CardBody([
    html.H3("Talent Pool Explorer", className="text-xl font-bold text-slate-800"),
    dbc.Table([talent_pool_table_header, talent_pool_table_body], hover=True, responsive=True, className="mt-4 text-sm align-middle")
]), className="shadow-sm")

# Main App Layout
app.layout = dbc.Container([
    header,
    filters,
    command_center,
    bench_forecast,
    talent_pipeline,
    talent_explorer
], fluid=True, className="p-4 md:p-6 lg:p-8")


# --- 5. RUN THE APP ---
if __name__ == '__main__':
    app.run_server(debug=True)
