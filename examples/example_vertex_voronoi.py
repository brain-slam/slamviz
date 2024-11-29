"""
.. _example_vertex_voronoi:

===================================
Vertex voronoi example in slam
===================================
"""

# Authors:
# Guillaume Auzias <guillaume.auzias@univ-amu.fr>
# Julien Barrès <julien.barres@etu.univ-amu.fr>

# License: BSD (3-clause)
# sphinx_gallery_thumbnail_number = 2


###############################################################################
# Importation of slam modules
import slam.io as sio
import slam.texture as stex
import slam.vertex_voronoi as svv
import numpy as np
import trimesh

# importation for the viz
import sys, os
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import app

###############################################################################
# load and reorient the mesh
mesh_file = 'examples/data/example_mesh.gii'
mesh = sio.load_mesh(mesh_file)
mesh.apply_transform(mesh.principal_inertia_transform)

###############################################################################
# compute the vornoi of vertice
vert_vor = svv.vertex_voronoi(mesh)
print(mesh.vertices.shape)
print(vert_vor.shape)

###############################################################################
# the sum of the voronoi from all vertices should be equal to the surface area
print(np.sum(vert_vor) - mesh.area)

###############################################################################
# Visualization
vert_vor_path = "examples/data/vert_vox.gii"
tmp_tex = stex.TextureND(vert_vor)
sio.write_texture(tmp_tex, vert_vor_path)

app.run_dash_app(mesh_file, texture_paths=[vert_vor_path])

exit()

