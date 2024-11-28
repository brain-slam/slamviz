from dash import dcc, html
import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
from .functions import load_mesh, read_gii_file, create_slider_marks, get_colorscale_names


def create_layout(mesh_path, texture_path=None):
    # Charger le mesh
    mesh = load_mesh(mesh_path)
    vertices = mesh.vertices
    faces = mesh.faces

    # Charger la texture (si fournie)
    scalars = read_gii_file(texture_path) if texture_path else None

    # Définir l'intervalle min et max par défaut des scalaires si disponibles
    color_min_default, color_max_default = (np.min(scalars), np.max(scalars)) if scalars is not None else (0, 1)

    layout = html.Div([
        html.H1("Visualisation de maillage 3D avec color bar interactive", style={'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.Label("Sélectionner le type de colormap"),
                dcc.Dropdown(
                    id='colormap-type-dropdown',
                    options=[
                        {'label': 'Sequential', 'value': 'sequential'},
                        {'label': 'Diverging', 'value': 'diverging'},
                        {'label': 'Cyclical', 'value': 'cyclical'}
                    ],
                    value='sequential',
                    clearable=False
                ),
                html.Label("Sélectionner une colormap"),
                dcc.Dropdown(
                    id='colormap-dropdown',
                    options=[{'label': cmap, 'value': cmap} for cmap in get_colorscale_names('sequential')],
                    value='Viridis',
                    clearable=False
                ),
                html.Label("Afficher les isolignes"),
                dcc.Checklist(
                    id='toggle-contours',
                    options=[{'label': 'Oui', 'value': 'on'}],
                    value=[],
                    inline=True
                ),
                html.Label("Activer traits noirs"),
                dcc.Checklist(
                    id='toggle-black-intervals',
                    options=[{'label': 'Oui', 'value': 'on'}],
                    value=[],
                    inline=True
                ),
                html.Label("Centrer la colormap sur 0"),
                dcc.Checklist(
                    id='toggle-center-colormap',
                    options=[{'label': 'Oui', 'value': 'on'}],
                    value=[],
                    inline=True
                ),
                dcc.RangeSlider(
                    id='range-slider',
                    min=color_min_default,
                    max=color_max_default,
                    step=0.01,
                    value=[color_min_default, color_max_default],
                    marks=create_slider_marks(color_min_default, color_max_default),
                    vertical=True,
                    verticalHeight=640,
                    tooltip={"placement": "right", "always_visible": True}
                )
            ], style={'height': '640px', 'display': 'inline-block', 'margin-right': '10px'}),
            html.Div([
                dcc.Graph(id='3d-mesh')
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'textAlign': 'center'}),
        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'})
    ])
    return layout
