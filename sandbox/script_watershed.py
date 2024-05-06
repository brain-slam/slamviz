import numpy as np
import slam.geodesics as slg
import slam.topology as slt
import slam.io as sio
import slam.differential_geometry as sldg
import slam.curvature as scurv
import slam.texture as stex
import slam.topology as slto
import os
import pandas as pd
import trimesh
import time
import itertools
import math
import copy

# Changes by me on the original algo of Lucile:
# refractor rename argument 'white' en 'mesh'
# add Nbv for Number of vertex. initialy express as (vert.size) / 3, changed by mesh.vertices.shape[0]
# change "ridges = np.zeros((1, 1), dtype=np.int)" to "ridges = np.zeros((1, 1), dtype=np.int) - 1" : ridge are initialized
# to -1 and same for upload of ridge in case 1
# use of slam.geodesic shortest path function to compute the shortest past between two pits
# use of slam.topology neighboo to get the neighboored nodes

def minimum_sulci_path(mesh):
    adj_matrix = slt.adjacency_matrix(mesh)

def compute_curv(mesh, output_folder, fname):
    print('compute Rusin curv')
    PrincipalCurvatures, PrincipalDir1, PrincipalDir2 = scurv.curvatures_and_derivatives(mesh)
    curv = 0.5 * (PrincipalCurvatures[0, :] + PrincipalCurvatures[1, :])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    sio.write_texture(stex.TextureND(darray=curv), os.path.join(output_folder, fname))

def compute_dpf(mesh, curv):
    print('compute DPF')
    alpha = [0.03]
    dpf = sldg.depth_potential_function(mesh, curv, alphas=alpha)
    dpf = np.array(dpf)
    dpf = dpf.flatten()
    return -dpf


if __name__ == '__main__':
    start_time= time.time()
    ##

    # mesh
    #sub = "CC00964XX16"
    #ses = "21430"
    sub = "CC00694XX19"
    ses = "201800"
    #sub = "CC00569XX17"
    #ses = "158300"
    main_path = "/home/INT/leroux.b/Documents/Subj0001/maxime/"

    """
    wd = '/home/maxime/callisto/repo/repo2024/external-vertices-detection'
    folder_curvature_rel3 = '/home/maxime/callisto/repo/paper_sulcal_depth/data/rel3/curvature'
    folder_mesh_rel3 = '/media/maxime/Expansion/rel3_dHCP'
    folder_output = os.path.join('/home/maxime/callisto/repo/paper_sulcal_depth/data/rel3/detection_external_v2',
                                 "sub_" + sub, "ses_" + ses)
    if not os.path.exists(folder_output):
        os.makedirs(folder_output)
    mesh_name = "sub-" + sub + "_ses-" + ses + "_hemi-left_wm.surf.gii"
    mesh_path = os.path.join(folder_mesh_rel3, "sub-" + sub, "ses-" + ses, "anat", mesh_name)
    mesh = sio.load_mesh(mesh_path)
    """

    mesh_path = os.path.join(main_path, "example_mesh.gii")
    mesh = sio.load_mesh(mesh_path)

    ## name
    """
    name_meanCurv = sub + '_' + ses + '_meanCurv.gii'
    name_K1 = sub + '_' + ses + '_K1.gii'
    name_K2 = sub + '_' + ses + '_K2.gii'
    """
    mean_curv_path = os.path.join(main_path, "curv.gii")

    # watershed_name = sub + '_' + ses + '_watershed_dpf.gii'
    watershed_name = "watershed_dpf.gii"
    # depth_name = 'sub-' + sub + '_ses-' + ses + '_hemi-left_sulc.shape.gii'

    # curv
    # K1 = sio.load_texture(os.path.join(folder_curvature_rel3, name_K1)).darray[0]
    # K2 = sio.load_texture(os.path.join(folder_curvature_rel3, name_K2)).darray[0]
    # curv = 0.5 * (K1 + K2)
    curv = sio.load_texture(mean_curv_path)

    # dpf
    # dpf_name = sub + '_' + ses + '_dpf.gii'
    dpf = compute_dpf(mesh, curv.darray[0])
    sio.write_texture(stex.TextureND(darray=dpf), os.path.join(main_path, "dpf.gii"))

    #depth_array = sio.load_texture(os.path.join(folder_mesh_rel3, 'sub-' + sub,
    #                                            'ses-' + ses, 'anat', depth_name)).darray[0]

    depth_array = copy.deepcopy(dpf)
    print('compute watershed')
    adj_matrix = slt.adjacency_matrix(mesh)
    #######  wartershed
    print('compute Watershed')
    # mask = []
    # depthArray = depth_array.darray[0].flatten()
    threshDist = 20
    threshRidge = 1.5

    Nbv = mesh.vertices.shape[0]  # number of vertex
    idx = np.arange(Nbv)  # vertices index
    labels = np.zeros((Nbv), dtype=np.int32) - 1
    pits = [False] * Nbv
    ridge = np.zeros((Nbv), dtype=np.int32) - 1
    isridge = [False] * Nbv
    nodes = pd.DataFrame(
        dict(index=idx, depth_array=depth_array, labels=labels, pits=pits, isridge=isridge, ridge=ridge))

    ## Apply exclusion mask
    # All nodes included in the exclusion mask are not taken into acount in the watershed process
    # maskIndices = np.where(mask == 1)[0]
    # nodes = np.delete(nodes, maskIndices, axis=0)

    ## Sorting step
    sorted_nodes = nodes.sort_values('depth_array', ascending=True, ignore_index=True)
    sorted_nodes['ridge'] = sorted_nodes['ridge'].astype('object')
    lab = 0
    Thr = 1.5
    Thd = 20
    for i, node in sorted_nodes.iterrows():
        # for i,node in enumerate(sorted_nodes[1:]):
        print(i)
        nind = node['index']
        # neigh = slt.k_ring_neighborhood(mesh, nind, k=1) # indices of neighbors
        # neighbors = nodes[:,0][np.array(neigh).flatten()==1]
        # neighbors = np.array(neighbors, dtype=int)
        neigh_nodes = adj_matrix.indices[
                      adj_matrix.indptr[int(node['index'])]:adj_matrix.indptr[int(node['index']) + 1]]
        neigh_nodes = neigh_nodes.astype(int)
        """
        dflabels = pd.DataFrame(labels)
        neigh_labels = dflabels[dflabels.index.isin(neigh_nodes)].values.flatten()

        neigh_nodes = neigh_nodes[neigh_labels != -1]
        neigh_labels = np.unique(neigh_labels)
        NL = np.delete(neigh_labels, np.where(neigh_labels == -1))
        """
        neigh_df = sorted_nodes[(sorted_nodes['index'].isin(neigh_nodes)) & (sorted_nodes['labels'] != -1)]
        neigh_labels = neigh_df['labels']
        NL = np.unique(neigh_labels.values.flatten())
        if (len(NL) == 0):
            # node['labels'] = lab
            sorted_nodes.loc[i, 'labels'] = lab
            sorted_nodes.loc[i, 'pits'] = True
            lab = lab + 1

        elif (len(NL) == 1):
            sorted_nodes.loc[i, 'labels'] = neigh_df.iloc[0]['labels']

        else:
            sorted_nodes.loc[i, 'labels'] = neigh_df.iloc[0]['labels']
            sorted_nodes.loc[i, 'isridge'] = True
            sorted_nodes.at[i, 'ridge'] = list(NL)

    # merge area


    # merge table ridge

    merge_df = sorted_nodes[sorted_nodes['isridge'] == True].reset_index(drop=True)

    Nbr = merge_df.shape[0]

    comb = np.array([list(itertools.combinations(merge_df.loc[i, 'ridge'], 2)) for i in range(Nbr)],
                    dtype=object).flatten()
    nb_comb = [len(comb[i]) for i in np.arange(len(comb))]
    comb2 = list(itertools.chain(*comb))

    tu = [[i, nb_comb[i]] for i in np.arange(Nbr)]
    ridge_df = [np.repeat([merge_df.loc[tu[i][0], 'index']], tu[i][1]) for i in np.arange(Nbr)]
    ridge_df = np.concatenate(ridge_df).ravel()
    comb3 = np.array(comb2)

    df = pd.DataFrame(dict(index_ridge=ridge_df, Pi=comb3[:, 0], Pj=comb3[:, 1]))
    df_ridge = df.drop_duplicates(subset=['Pi', 'Pj'], keep='first')

    df_pits = sorted_nodes[sorted_nodes['pits'] == True].reset_index(drop=True)
    df_pits = df_pits[['index', 'depth_array', 'labels']]
    df_pits.to_csv(os.path.join(main_path, 'table_pits.csv'))

    # Add depth table ridge
    pi_depth = pd.Series(np.array([ df_pits[df_pits['labels']==lab]['depth_array'].values for lab in df_ridge['Pi'].values]).flatten())
    pj_depth = pd.Series(np.array([df_pits[df_pits['labels'] == lab]['depth_array'].values for lab in df_ridge['Pj'].values]).flatten())
    print(pi_depth)
    df_ridge.insert(len(df_ridge.columns), 'Pi_depth', pi_depth.values)
    df_ridge.insert(len(df_ridge.columns), 'Pj_depth', pj_depth.values)
    df_ridge = df_ridge.sort_values(['Pi', 'Pj'])
    df_ridge.to_csv(os.path.join(main_path, 'aatable_ridge.csv'))

    """
    for i, row in df.iterrows():
        print(i)
        DPFr = sorted_nodes[sorted_nodes['index'] == row['index_ridge'] ]['depth_array'].values
        DPFj = sorted_nodes[sorted_nodes['index'] == row['Pj']]['depth_array'].values
        v_tex = slg.compute_gdist(mesh, row['Pi'])
        v = v_tex[int(row['Pi'])]
        if (abs(DPFr - DPFj) < Thr) & (v < Thd):
            df[['Pi','Pj']] = df[['Pi','Pj']].replace(row['Pj'], row['Pi'])
            df = df.drop_duplicates(subset=['Pi', 'Pj'], keep='first')


    """
    # save
    re_sorted_nodes = sorted_nodes.sort_values('index')
    sio.write_texture(stex.TextureND(darray=re_sorted_nodes['labels'].values.flatten()),
                      os.path.join(main_path, watershed_name))

    end_time = time.time()
    print(f"The execution time is: {end_time - start_time}")








