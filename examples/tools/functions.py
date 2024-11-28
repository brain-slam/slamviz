import numpy as np
import plotly.colors as pc
import nibabel as nib
import trimesh
import plotly.graph_objects as go


def load_mesh(gifti_file):
    """
    load gifti_file and create a trimesh object
    :param gifti_file: str, path to the gifti file on the disk
    :return: the corresponding trimesh object
    """
    g = nib.load(gifti_file)
    coords, faces = g.get_arrays_from_intent(
        nib.nifti1.intent_codes['NIFTI_INTENT_POINTSET'])[0].data, \
        g.get_arrays_from_intent(
            nib.nifti1.intent_codes['NIFTI_INTENT_TRIANGLE'])[0].data
    metadata = g.meta.metadata
    metadata['filename'] = gifti_file
    return trimesh.Trimesh(faces=faces, vertices=coords,
                           metadata=metadata, process=False)

# Fonction pour lire un fichier GIFTI (scalars.gii)
def read_gii_file(file_path):
    try:
        gifti_img = nib.load(file_path)
        scalars = gifti_img.darrays[0].data
        return scalars
    except Exception as e:
        print(f"Erreur lors du chargement de la texture : {e}")
        return None

# Fonction pour convertir des couleurs RGB en hexadécimal
def convert_rgb_to_hex_if_needed(colormap):
    hex_colormap = []
    for color in colormap:
        if color.startswith('rgb'):
            rgb_values = [int(c) for c in color[4:-1].split(',')]
            hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb_values)
            hex_colormap.append(hex_color)
        else:
            hex_colormap.append(color)
    return hex_colormap

# Création d'une colormap avec des traits noirs
def create_colormap_with_black_stripes(base_colormap, num_intervals=10, black_line_width=0.01):
    temp_c = pc.get_colorscale(base_colormap)
    temp_c_2 = [ii[1] for ii in temp_c]
    old_colormap = convert_rgb_to_hex_if_needed(temp_c_2)
    custom_colormap = []
    base_intervals = np.linspace(0, 1, len(old_colormap))

    for i in range(len(old_colormap) - 1):
        custom_colormap.append([base_intervals[i], old_colormap[i]])
        if i % (len(old_colormap) // num_intervals) == 0:
            black_start = base_intervals[i]
            black_end = min(black_start + black_line_width, 1)
            custom_colormap.append([black_start, 'rgb(0, 0, 0)'])
            custom_colormap.append([black_end, old_colormap[i]])
    custom_colormap.append([1, old_colormap[-1]])
    return custom_colormap

def get_colorscale_names(colormap_type):
    if colormap_type == 'sequential':
        return [name for name in pc.sequential.__dict__.keys() if '__' not in name and 'swatches' not in name]
    elif colormap_type == 'diverging':
        return [name for name in pc.diverging.__dict__.keys() if '__' not in name and 'swatches' not in name]
    elif colormap_type == 'cyclical':
        return [name for name in pc.cyclical.__dict__.keys() if '__' not in name and 'swatches' not in name]
    return []

# Créer des ticks clairs pour le slider
def create_slider_marks(color_min_default, color_max_default):
    return {str(i): f'{i:.2f}' for i in np.linspace(color_min_default, color_max_default, 10)}


def plot_mesh_with_colorbar(vertices, faces, scalars=None, color_min=None, color_max=None, camera=None, show_contours=False, colormap='jet', use_black_intervals=False, center_colormap_on_zero=False):
    fig_data = dict(
        x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        flatshading=False, hoverinfo='text', showscale=False
    )

    if scalars is not None:
        color_min = color_min if color_min is not None else np.min(scalars)
        color_max = color_max if color_max is not None else np.max(scalars)

        if center_colormap_on_zero:
            max_abs_value = max(abs(color_min), abs(color_max))
            color_min, color_max = -max_abs_value, max_abs_value

        if use_black_intervals:
            colorscale = create_colormap_with_black_stripes(colormap)
        else:
            colorscale = colormap

        fig_data.update(
            intensity=scalars,
            intensitymode='vertex',
            cmin=color_min,
            cmax=color_max,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(
                title="Scalars",
                tickformat=".2f",
                thickness=30,
                len=0.9
            ),
            hovertext=[f'Scalar value: {s:.2f}' for s in scalars]
        )

    fig = go.Figure(data=[go.Mesh3d(**fig_data)])
    if show_contours:
        fig.data[0].update(contour=dict(show=True, color='black', width=2))

    fig.update_layout(scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        camera=camera
    ),
    height=900,
    width=1000,
    margin=dict(l=10, r=10, b=10, t=10))

    return fig