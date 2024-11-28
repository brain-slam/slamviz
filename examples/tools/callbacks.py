from dash.dependencies import Input, Output, State
from .functions import load_mesh, read_gii_file, plot_mesh_with_colorbar, get_colorscale_names
import numpy as np

def register_callbacks(app, mesh_path, texture_path):
    # Charger le mesh
    mesh = load_mesh(mesh_path)
    vertices = mesh.vertices
    faces = mesh.faces

    # Charger la texture (si fournie)
    scalars = read_gii_file(texture_path) if texture_path else None

    color_min_default, color_max_default = (np.min(scalars), np.max(scalars)) if scalars is not None else (0, 1)

    @app.callback(
        Output('3d-mesh', 'figure'),
        [Input('range-slider', 'value'),
         Input('toggle-contours', 'value'),
         Input('toggle-black-intervals', 'value'),
         Input('colormap-dropdown', 'value'),
         Input('toggle-center-colormap', 'value')],
        [State('3d-mesh', 'relayoutData')]
    )
    def update_figure(value_range, toggle_contours, toggle_black_intervals, selected_colormap, center_colormap, relayout_data):
        min_value, max_value = value_range
        camera = relayout_data['scene.camera'] if relayout_data and 'scene.camera' in relayout_data else None
        show_contours = 'on' in toggle_contours
        use_black_intervals = 'on' in toggle_black_intervals
        center_on_zero = 'on' in center_colormap

        fig = plot_mesh_with_colorbar(
            vertices, faces, scalars, color_min=min_value, color_max=max_value,
            camera=camera, show_contours=show_contours, colormap=selected_colormap,
            use_black_intervals=use_black_intervals, center_colormap_on_zero=center_on_zero
        )
        return fig

    # Callback pour mettre à jour la liste des colormaps en fonction du type choisi
    @app.callback(
        Output('colormap-dropdown', 'options'),
        [Input('colormap-type-dropdown', 'value')]
    )
    def update_colormap_options(selected_type):
        return [{'label': cmap, 'value': cmap} for cmap in get_colorscale_names(selected_type)]
