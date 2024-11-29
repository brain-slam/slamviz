"""test
.. _example_with_freesurfer_outputs:

===================================
example visualizations of freesurfer recon-all outputs
===================================
"""

# Authors: Guillaume Auzias <guillaume.auzias@univ-amu.fr>
#          Julien Barrès <julien.barres@etu.univ-amu.fr>
#          Marco Bedini <marco.bedini@univ-amu.fr>

# License: BSD (3-clause)
# sphinx_gallery_thumbnail_number = 2

import nibabel as nib
import slam.io as sio
import slam.texture as stex
import slam.curvature as scurv

import sys, os
# from shutil import copy
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import app
from tools import functions

###############################################################################
# Try downloading an example output from the Human Connectome Project extended preproc
# folder e.g., subject 100307. Make sure you copy the data in the folder

mesh_file = 'examples/data/lh.white.surf.gii'
mesh = nib.load(mesh_file)

# Copy and rename the file you want to look at if it doesn't have the .gii extension
# src_path = 'examples/data/lh.white'
# destination_path = 'examples/data/lh.white.gii'
# copy(src_path, destination_path)

# Get the number of vertices
num_vertices = mesh.darrays[0].data.shape[0]

print("Number of vertices:", num_vertices)

# Read the header and print the basic info
header = mesh.header
print("GIFTI Header Information:", header)

# Summarize key details
print("\nSummary of the GIFTI File:")
print(f"Number of Data Arrays: {len(mesh.darrays)}")

# Access the metadata for the GIFTI image
image_metadata = mesh.meta
print("Image Metadata:", image_metadata)

## Read more stuff
triangles = mesh.agg_data('triangle')
print("Triangles:")
print(triangles)

print("\n")

## Compare with the functions based on trimesh
mesh1 = sio.load_mesh('examples/data/lh.white.surf.gii')
print("Trimesh object")
print(mesh1)

mesh_read = functions.read_gii_file('examples/data/lh.white.surf.gii')
print("Trimesh read info")
print(mesh_read)

## You could also load the curv files as texture from freesurfer
# src_file = 'examples/data/lh.avg_curv'
# curv_fname = 'examples/data/lh.avg_curv.gii'
# copy(src_path, curv_fname)
# mean_curv_path = "examples/data/lh.avg_curv.gii"

# Recompute the curv using slam functions
mesh = sio.load_mesh(mesh_file)
print(mesh.principal_inertia_transform)
mesh.apply_transform(mesh.principal_inertia_transform)
print(mesh.principal_inertia_transform)

###############################################################################
# Compute estimations of principal curvatures
PrincipalCurvatures, PrincipalDir1, PrincipalDir2 = \
    scurv.curvatures_and_derivatives(mesh)

###############################################################################
# Compute Gauss curvature from principal curvatures
gaussian_curv = PrincipalCurvatures[0, :] * PrincipalCurvatures[1, :]

###############################################################################
# Compute mean curvature from principal curvatures
mean_curv = 0.5 * (PrincipalCurvatures[0, :] + PrincipalCurvatures[1, :])

###############################################################################
# Decomposition of the curvatures into ShapeIndex and Curvedness
# Based on 'Surface shape and curvature scales
#           Jan JKoenderink & Andrea Jvan Doorn'
shapeIndex, curvedness = scurv.decompose_curvature(PrincipalCurvatures)

###############################################################################
# save the computed maps on the disc
mean_curv_path = "examples/data/lh.white_mean_curv.gii"
gaussian_curv_path = "examples/data/lh.white_gaussian_curv.gii"
shape_index_curv_path = "examples/data/lh.white_shape_index.gii"
tmp_tex = stex.TextureND(mean_curv)
sio.write_texture(tmp_tex, mean_curv_path)
tmp_tex = stex.TextureND(gaussian_curv)
sio.write_texture(tmp_tex, gaussian_curv_path)
tmp_tex = stex.TextureND(shapeIndex)
sio.write_texture(tmp_tex, shape_index_curv_path)

###############################################################################
# run the visualization app
app.run_dash_app(mesh_file, texture_paths=[mean_curv_path, gaussian_curv_path, shape_index_curv_path])

exit()



