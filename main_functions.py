#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 09:50:54 2021

@author: ying
"""

import pandas as pd
import numpy as np
import trimesh
import json
from ml_prediction import ml_prediction
#dataset = pd.read_pickle('sparse_FDM_v2.pickle')
#data = dataset.head(1)

def get_coords(data):
    coords = []
    truth =[]
    for i, row in enumerate(data):
        for j, col in enumerate(row):
            for k, dep in enumerate(col):
                if dep == 1:
                    coords.append([i, j, k])
                    truth.append([1])
                elif dep == 2:
                    coords.append([i, j, k])
                    truth.append([0])
    return np.array(coords),np.array(truth)

def design_data_generation(design_filename):
    mesh = trimesh.load(design_filename)    
    scale = np.max(mesh.extents)
    voxelized_mesh = mesh.voxelized(scale/128)
    v = voxelized_mesh.copy().fill()
    voxel1 = v.matrix
    voxel2 = np.zeros((129,129,129))
    voxel2[:voxel1.shape[0],:voxel1.shape[1],:voxel1.shape[2]] = voxel1
    obj = [voxel2[:-1, :-1, :-1].astype('uint8')]
    
    
    for data in obj:
        coords,truth = get_coords(data)
        N = len(coords)
        feats = np.ones((N, 1))
        
        return coords, feats, scale,obj
        
def process_data_generation(process_filename):
    with open(process_filename) as json_file:
        data = json.load(json_file)
        process_data = pd.DataFrame([data])

        process_data['Density'] = process_data['Density'].astype(float)
        process_data['LayerThinkness'] = process_data['LayerThinkness'].astype(float)
        process_data['InfillPercent'] = process_data['InfillPercent'].astype(float)
        process_data['NozzleTemp'] = process_data['NozzleTemp'].astype(float)
        process_data['BedTemp'] = process_data['BedTemp'].astype(float)
        process_data['PrintingSpeed'] = process_data['PrintingSpeed'].astype(float)
        process_data['Support'] = 0
        new_process_data  = process_data[['Type','Density', 'PrintingSpeed', 'LayerThinkness', 'InfillPercent',
                       'Support', 'AdhensionType', 'NozzleTemp', 'BedTemp']]
    return new_process_data

def make_prediction(design_filename,process_filename):
    #design_filename = 'test2.obj'
    #process_filename = 'test1.JSON'
    coords,feats,scale,obj = design_data_generation(design_filename)
    process_data = process_data_generation(process_filename)
    design_data = pd.DataFrame()
    design_data['coords'] = [coords]
    design_data['feats'] = [feats]
    design_data['scale'] = [scale]
    data = pd.concat([process_data,design_data],axis=1)
    pred_class,pred = ml_prediction(data)
    return pred_class.numpy()
