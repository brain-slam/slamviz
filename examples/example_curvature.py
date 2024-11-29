"""test
.. _example_curvature:

===================================
example of curvature estimation in slam
===================================
"""

# Authors: Guillaume Auzias <guillaume.auzias@univ-amu.fr>
#          Julien Barrès <julien.barres@etu.univ-amu.fr>

# License: BSD (3-clause)
# sphinx_gallery_thumbnail_number = 2


###############################################################################
# importation of slam modules
import slam.io as sio
import slam.texture as stex
import slam.curvature as scurv

# importation for the viz
import sys, os
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import app

###############################################################################
# load and reorient an examplar mesh
mesh_file = 'examples/data/example_mesh.gii'
mesh = sio.load_mesh(mesh_file)
print(mesh.principal_inertia_transform)
mesh.apply_transform(mesh.principal_inertia_transform)
print(mesh.principal_inertia_transform)

###############################################################################
# Comptue estimations of principal curvatures
PrincipalCurvatures, PrincipalDir1, PrincipalDir2 = \
    scurv.curvatures_and_derivatives(mesh)

###############################################################################
# Comptue Gauss curvature from principal curvatures
gaussian_curv = PrincipalCurvatures[0, :] * PrincipalCurvatures[1, :]

###############################################################################
# Comptue mean curvature from principal curvatures
mean_curv = 0.5 * (PrincipalCurvatures[0, :] + PrincipalCurvatures[1, :])

###############################################################################
# Decomposition of the curvatures into ShapeIndex and Curvedness
# Based on 'Surface shape and curvature scales
#           Jan JKoenderink & Andrea Jvan Doorn'
shapeIndex, curvedness = scurv.decompose_curvature(PrincipalCurvatures)

###############################################################################
# save the computed maps on the disc
mean_curv_path = "examples/data/mean_curv.gii"
gaussian_curv_path = "examples/data/gaussian_curv.gii"
shape_index_curv_path = "examples/data/shape_index.gii"
tmp_tex = stex.TextureND(mean_curv)
sio.write_texture(tmp_tex, mean_curv_path)
tmp_tex = stex.TextureND(gaussian_curv)
sio.write_texture(tmp_tex, gaussian_curv_path)
tmp_tex = stex.TextureND(shapeIndex)
sio.write_texture(tmp_tex, shape_index_curv_path)

###############################################################################
# run the visualization app
app.run_dash_app(mesh_path=mesh_file, texture_paths=[mean_curv_path, gaussian_curv_path, shape_index_curv_path])

exit()



###############################################################################
# Estimation error on the principal curvature length
K = [1, 0]

quadric = sgps.generate_quadric(
    K,
    nstep=[
        20,
        20],
    ax=3,
    ay=3,
    random_sampling=False,
    ratio=0.3,
    random_distribution_type='gamma', equilateral=True)

###############################################################################
# Estimated computation of the Principal curvature, K_gauss, K_mean
p_curv, d1_estim, d2_estim = scurv.curvatures_and_derivatives(
    quadric)

k1_estim, k2_estim = p_curv[0, :], p_curv[1, :]

k_gauss_estim = k1_estim * k2_estim

k_mean_estim = .5 * (k1_estim + k2_estim)

###############################################################################
# Analytical computation of the curvatures

k_mean_analytic = sgps.quadric_curv_mean(K)(
    np.array(quadric.vertices[:, 0]), np.array(quadric.vertices[:, 1]))

k_gauss_analytic = sgps.quadric_curv_gauss(K)(
    np.array(quadric.vertices[:, 0]), np.array(quadric.vertices[:, 1]))

k1_analytic = np.zeros((len(k_mean_analytic)))
k2_analytic = np.zeros((len(k_mean_analytic)))

for i in range(len(k_mean_analytic)):
    a, b = np.roots(
        (1, -2 * k_mean_analytic[i], k_gauss_analytic[i]))
    k1_analytic[i] = min(a, b)
    k2_analytic[i] = max(a, b)


###############################################################################
# Error computation

k_mean_relative_change = abs(
    (k_mean_analytic - k_mean_estim) / k_mean_analytic)
k_mean_absolute_change = abs((k_mean_analytic - k_mean_estim))

k1_relative_change = abs((k1_analytic - k1_estim) / k1_analytic)
k1_absolute_change = abs((k1_analytic - k1_estim))

###############################################################################
# Error plot

visb_sc = splt.visbrain_plot(mesh=quadric, tex=k_mean_absolute_change,
                             caption='K_mean absolute error',
                             cblabel='K_mean absolute error',)
visb_sc.preview()

###############################################################################
# Estimation error on the curvature directions
# commented because there is a bug:
# ValueError: shapes (3,2) and (3,2) not aligned: 2 (dim 1) != 3 (dim 0)
# actually, vec1.shape=(3,) while vec2.shape=(3,2)

K = [1, 0]

quadric = sgps.generate_quadric(
    K,
    nstep=[
        20,
        20],
    ax=3,
    ay=3,
    random_sampling=False,
    ratio=0.3,
    random_distribution_type='gamma', equilateral=True)

###############################################################################
# Estimated computation of the Principal curvature, Direction1, Direction2
p_curv_estim, d1_estim, d2_estim = scurv.curvatures_and_derivatives(quadric)

###############################################################################
# Analytical computation of the directions
analytical_directions = sgps.compute_all_principal_directions_3D(
    K, quadric.vertices)

estimated_directions = np.zeros(analytical_directions.shape)
estimated_directions[:, :, 0] = d1_estim
estimated_directions[:, :, 1] = d2_estim

angular_error_0, dotprods = ut.compare_analytic_estimated_directions(
    analytical_directions[:, :, 0], estimated_directions[:, :, 0])
angular_error_0 = 180 * angular_error_0 / np.pi

angular_error_1, dotprods = ut.compare_analytic_estimated_directions(
    analytical_directions[:, :, 1], estimated_directions[:, :, 1])
angular_error_1 = 180 * angular_error_1 / np.pi

###############################################################################
# Error plot

visb_sc = splt.visbrain_plot(mesh=quadric, tex=angular_error_0,
                             caption='Angular error 0',
                             cblabel='Angular error 0',)
visb_sc.preview()

visb_sc = splt.visbrain_plot(mesh=quadric, tex=angular_error_1,
                             caption='Angular error 1',
                             cblabel='Angular error 1',)
visb_sc.preview()
