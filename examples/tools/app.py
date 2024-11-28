import dash
import argparse
from .layout import create_layout
from .callbacks import register_callbacks

# Fonction principale pour exécuter l'application
def run_dash_app(mesh_path, texture_paths=None):
    # Créer l'application Dash
    app = dash.Dash(__name__)

    # Ajouter le layout
    app.layout = create_layout(mesh_path, texture_paths=texture_paths)

    # Enregistrer les callbacks
    register_callbacks(app, mesh_path, texture_paths)

    # Lancer l'application
    app.run_server(debug=True)

