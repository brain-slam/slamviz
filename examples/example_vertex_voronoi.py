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
# import slam.plot as splt
import slam.vertex_voronoi as svv
import numpy as np
import trimesh

# importation for the viz
import sys, os
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import app

###############################################################################
#
mesh_file = 'examples/data/example_mesh.gii'
mesh = sio.load_mesh(mesh_file)
mesh.apply_transform(mesh.principal_inertia_transform)

###############################################################################
#
vert_vor = svv.vertex_voronoi(mesh)
print(mesh.vertices.shape)
print(vert_vor.shape)
print(np.sum(vert_vor) - mesh.area)

###############################################################################

vert_vor_path = "examples/data/vert_vox.gii"

mesh_vor = trimesh.Trimesh(
        faces=mesh.faces,
        vertices=vert_vor,
        process=False)

sio.write_mesh(mesh_vor, vert_vor_path)

app.run_dash_app(mesh_file, texture_paths=[vert_vor_path])

exit()


###############################################################################
# Visualization
visb_sc = splt.visbrain_plot(mesh=mesh, tex=vert_vor,
                             caption='vertex voronoi',
                             cblabel='vertex voronoi')
visb_sc.preview()
