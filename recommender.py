#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 08:19:20 2021

@author: ying
"""

import pandas as pd
import numpy as np
import trimesh
from ml_prediction import ml_prediction
from main_functions import process_data_generation
from tweaker3 import FileHandler
from tweaker3 import Tweaker
import math
import os

#dataset = pd.read_pickle('sparse_FDM_v2.pickle')
#data = dataset.head(1)
path = 'static/saved/'
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
        

# =============================================================================
# def make_prediction(design_filename,process_filename):
#     
#     return pred_class.numpy(), pred.numpy(),data
# =============================================================================

def feedback_process(process_data,design_data):  
#first, define all the common variations
    data = pd.concat([process_data,design_data],axis=1)
    pla_default = pd.DataFrame([{'Type':'PLA','Density':1.24, 'PrintingSpeed':80,
                                   'LayerThinkness':0.15, 'InfillPercent':20,
                                   'Support':0, 'AdhensionType':'Brim',
                                   'NozzleTemp':200, 'BedTemp':60}])
    abs_default = pd.DataFrame([{'Type':'ABS','Density':1.04, 'PrintingSpeed':60,
                                   'LayerThinkness':0.15, 'InfillPercent':20,
                                   'Support':0, 'AdhensionType':'Brim',
                                   'NozzleTemp':235, 'BedTemp':80}])
    pc_default = pd.DataFrame([{'Type':'PC','Density':1.19, 'PrintingSpeed':50,
                                   'LayerThinkness':0.15, 'InfillPercent':20,
                                   'Support':0, 'AdhensionType':'Raft with gap of 0.25mm',
                                   'NozzleTemp':280, 'BedTemp':107}])
    nylon_default = pd.DataFrame([{'Type':'NYLON','Density':1.14, 'PrintingSpeed':70,
                                   'LayerThinkness':0.15, 'InfillPercent':20,
                                   'Support':0, 'AdhensionType':'Brim',
                                   'NozzleTemp':250, 'BedTemp':60}])
    infill_percent_variation = np.linspace(20,100, 5).T
    adh_type_variation = np.array(['Brim','Raft with gap of 0.25mm', 
                                   'Raft with gap of 0.15mm','Raft with gap of 0.05mm']).T
    layer_thickness_varation = np.array([0.15, 0.1, 0.2, 0.06]).T
    
    print('analyzing default value')
    if process_data['Type'].iloc[0] == 'PLA':
        bed_temp_variation = np.linspace(40,75, 8).T
        nozzle_temp_variation = np.linspace(180,230, 11).T
        printing_speed_variation = np.linspace(40,100,7).T
        #try default value with prediction first
        if ((process_data!=pla_default).all()).all():
            print('Recommendations: Try default settings')
            data_try = pd.concat([pla_default, design_data],axis=1)
            pred_class_try,pred_try = ml_prediction(data_try)
        
    elif process_data['Type'].iloc[0] == 'ABS':
        bed_temp_variation = np.linspace(80,110, 7).T
        nozzle_temp_variation = np.linspace(210,250, 9).T
        printing_speed_variation = np.linspace(40,80,5).T
        if ((process_data!=abs_default).all()).all():
            print('Recommendations: Try default settings')
            data_try = pd.concat([abs_default, design_data],axis=1)
            pred_class_try,pred_try = ml_prediction(data_try)
        
    elif process_data['Type'].iloc[0] == 'PC':
        bed_temp_variation = np.linspace(80,120, 9).T
        nozzle_temp_variation = np.linspace(260,290, 7).T
        printing_speed_variation = np.linspace(30,70,5).T
        if ((process_data!=pc_default).all()).all():
            print('Recommendations: Try default settings')
            data_try = pd.concat([pc_default, design_data],axis=1)
            pred_class_try,pred_try = ml_prediction(data_try)
        
    elif process_data['Type'].iloc[0] == 'NYLON':
        bed_temp_variation = np.linspace(70,100, 7).T
        nozzle_temp_variation = np.linspace(240,260, 5).T
        printing_speed_variation = np.linspace(40,90,6).T
        if ((process_data!=nylon_default).all()).all():
            print('Recommendations: Try default settings')
            data_try = pd.concat([nylon_default, design_data],axis=1)
            pred_class_try,pred_try = ml_prediction(data_try)
        
    #then, try to vary bed temp
    print('analyzing bed temp')
    N = len(bed_temp_variation)   
    bed_temp_data = pd.concat([data]*N, ignore_index=True)
    bed_temp_data['BedTemp'] = bed_temp_variation
    for index, row in bed_temp_data.iterrows():
        #data_try = pd.concat([row, design_data],axis=1)
        data_try = row.to_frame().T
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try to change bed temperature to ' + target['BedTemp']
    #try nozzle temp
    N = len(nozzle_temp_variation)   
    nozzle_temp_data = pd.concat([data]*N, ignore_index=True)
    nozzle_temp_data['NozzleTemp'] = nozzle_temp_variation
    print('analyzing nozzle temp')
    for index, row in nozzle_temp_data.iterrows():
        #data_try = pd.concat([row, design_data],axis=1)
        data_try = row.to_frame().T
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try to change nozzle temperature to' + target['NozzleTemp']
    #try adhesion type
    N = len(adh_type_variation)   
    adh_type_data = pd.concat([data]*N, ignore_index=True)
    adh_type_data['AdhensionType'] = adh_type_variation
    print('analyzing adhesion type')
    for index, row in adh_type_data.iterrows():
        #data_try = pd.concat([row, design_data],axis=1)
        data_try = row.to_frame().T
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try to change adhesion type to' +target['AdhensionType']
    #try printing speed
    N = len(printing_speed_variation)   
    printing_speed_data = pd.concat([data]*N, ignore_index=True)
    printing_speed_data['PrintingSpeed'] = printing_speed_variation
    print('analyzing printing speed')
    for index, row in printing_speed_data.iterrows():
        #data_try = pd.concat([row, design_data],axis=1)
        data_try = row.to_frame().T
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try to change printing speed to ' + target['PrintingSpeed']
    #try infill percent
    N = len(infill_percent_variation)   
    infill_percent_data = pd.concat([data]*N, ignore_index=True)
    infill_percent_data['InfillPercent'] = infill_percent_variation
    print('analyzing infill percent')
    for index, row in infill_percent_data.iterrows():
        #data_try = pd.concat([row, design_data],axis=1)
        data_try = row.to_frame().T
        pred_class_try,pred_try = ml_prediction(data_try)
        print('done')
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try to change infill percentage' + target['InfillPercent']
    #try layer thickness
    N = len(layer_thickness_varation)   
    layer_thickness_data = pd.concat([data]*N, ignore_index=True)
    layer_thickness_data['LayerThinkness'] = layer_thickness_varation
    print('analyzing layer layer thickness')
    for index, row in layer_thickness_data.iterrows():
        #data_try = pd.concat([row, design_data],axis=1)
        data_try = row.to_frame().T
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try to change layer thickness' + target['LayerThinkness']
    #try material type
    print('analyzing material type')
    if process_data['Type'].iloc[0] == 'PLA':
        data_try = pd.concat([abs_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try ABS'
        data_try = pd.concat([pc_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try PC'
        data_try = pd.concat([nylon_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try NYLON'
    if process_data['Type'].iloc[0] == 'ABS':
        data_try = pd.concat([pla_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try PLA'
        data_try = pd.concat([pc_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try PC'
        data_try = pd.concat([nylon_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try NYLON'
    if process_data['Type'].iloc[0] == 'PC':
        data_try = pd.concat([abs_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try ABS'
        data_try = pd.concat([pla_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try PLA'
        data_try = pd.concat([nylon_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try NYLON'
    if process_data['Type'].iloc[0] == 'NYLON':
        data_try = pd.concat([abs_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try ABS'
        data_try = pd.concat([pc_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try PC'
        data_try = pd.concat([pla_default, design_data],axis=1)
        pred_class_try,pred_try = ml_prediction(data_try)
        if pred_class_try.numpy()==1:
            target = data_try
            print('find')
            return 'Recommendations: Try PLA'
    #if none of them is working
    return False
 
# =============================================================================
# design_filename = 'OrganizadorHexagonal.stl'
# process_filename = design_filename.rsplit('.', 1)[0] + '.json'
# =============================================================================

def design_opt_min_sur(design_filename):
    path,filename = os.path.split(design_filename)
    file_handler = FileHandler.FileHandler()

    objs = file_handler.load_mesh(design_filename)
    info = dict()
    output_filename = 'min_sur_' + filename
    for part, content in objs.items():
        info[part] = dict()
        mesh = content["mesh"]
        kwargs = dict({"min_volume":False})
        x = Tweaker.Tweak(mesh, **kwargs)
        info[part]["matrix"] = x.matrix
        info[part]["tweaker_stats"] = x
        
    file_handler.write_mesh(objs, info, path+'/'+output_filename)
    
    
    return output_filename

def design_opt_most_contact(design_filename):
    path,filename = os.path.split(design_filename)
    output_filename = 'most_contact_' + filename
    mesh = trimesh.load(design_filename)    
    scale = np.max(mesh.extents)
    voxelized_mesh = mesh.voxelized(scale/64)
    
    obj = voxelized_mesh.matrix
    a = [sum(sum(obj[0,:,:])),sum(sum(obj[-1,:,:])),sum(sum(obj[:,0,:])),
               sum(sum(obj[:,-1,:])),sum(sum(obj[:,:,0])),sum(sum(obj[:,:,-1]))]
    
    new = a.index(max(a))
    angle = [-math.pi/2,math.pi/2,math.pi/2,-math.pi/2,0,math.pi]
    direction = [[0,1,0],[0,1,0],[1,0,0],[1,0,0],[1,0,0],[1,0,0]]
    rot = trimesh.transformations.rotation_matrix(angle[new],direction[new],[0,0,0])
    new_mesh = mesh.apply_transform(rot)
    new_mesh.export(path+'/'+output_filename)  
    return output_filename

def feedback_design(design_filename, process_data):
    coords,feats,scale,obj = design_data_generation(design_filename)
    design_data = pd.DataFrame()
    design_data['coords'] = [coords]
    design_data['feats'] = [feats]
    design_data['scale'] = [scale]
    data_try = pd.concat([process_data,design_data],axis=1)
    pred_class_try,pred_try = ml_prediction(data_try)
    if pred_class_try.numpy()==1:
        print('find')
        return 'Recommendations: Try different build orientation as the viewer shows'
    else:
        return False

def recommender(design_filename,process_filename):
    path,filename = os.path.split(design_filename)
    coords,feats,scale,obj = design_data_generation(design_filename)
    process_data = process_data_generation(process_filename)
    design_data = pd.DataFrame()
    design_data['coords'] = [coords]
    design_data['feats'] = [feats]
    design_data['scale'] = [scale]
    #data = pd.concat([process_data,design_data],axis=1)
    #pred_class,pred = ml_prediction(data)  
    most_contact_filename = design_opt_most_contact(design_filename)
    design_suggestion_most_contact = feedback_design(path+'/'+most_contact_filename,process_data)
    #process variation
    if design_suggestion_most_contact != False:
        return design_suggestion_most_contact,most_contact_filename
    
    
    min_sur_filename = design_opt_min_sur(design_filename)
    design_suggestion_min_sur = feedback_design(path+'/'+min_sur_filename,process_data)
    #process variation
    if design_suggestion_min_sur != False:
        return design_suggestion_min_sur,min_sur_filename
    
    
    #try process variation
    process_suggestion = feedback_process(process_data,design_data)
    if process_suggestion !=False:
        return process_suggestion,design_filename
    #if not, try design variation
    #two strategy: 1, most contacting face 2, least overhang
    #rotate for placing other five faces to platform
    #if suggestion == False:
    
    # =====================================
    # #3d plot in python
    # import matplotlib.pyplot as plt
    # from mpl_toolkits.mplot3d import Axes3D
    # 
    # def make_ax(grid=False):
    #     fig = plt.figure()
    #     ax = fig.gca(projection='3d')
    #     ax.set_xlabel("x")
    #     ax.set_ylabel("y")
    #     ax.set_zlabel("z")
    #     ax.grid(grid)
    #     return ax
    # 
    # ax = make_ax(True)
    # ax.voxels(obj[0], edgecolors='gray', shade=False)
    # plt.show()    
    # =============================================================================
        
    #test1.obj --> not printable
    return 'Please see the printability map for potential design modification', design_filename