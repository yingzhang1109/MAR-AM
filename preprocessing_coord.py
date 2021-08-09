# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 13:09:34 2019

@author: ADML
"""
import numpy as np
import pandas as pd
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
import json
import serialize_sk as sr

def serialize_class(cls_):
    return sr.data_to_json({'mod': cls_.__module__,
                            'name': cls_.__class__.__name__,
                            'attr': cls_.__dict__})

def preprocessing(dataset,vec,testornot = 1):
    coords = dataset['coords'].values
    feats = dataset['feats'].values
    #obj=np.concatenate(obj).astype(None).reshape(dataset.shape[0],128,128,128)
#obj = obj[:,0:x,0:y,0:z]
# =============================================================================
# parameters_text  = dataset[['lattice_type','material','machine']]
# parameters_value = dataset[['strut_radius','cell_size','internal_density','density']].values
# =============================================================================
# =============================================================================
#     parameters  = dataset[['material','material_brand','machine_brand',
#                            'machine_type','material density']]
# =============================================================================
    parameters  = dataset[['Type','Density', 'PrintingSpeed', 'LayerThinkness', 'InfillPercent',
                       'Support', 'AdhensionType', 'NozzleTemp', 'BedTemp', 'scale']]
    parameters = parameters.to_dict('records')
    if vec ==0:
        vec = DictVectorizer()
        
        p = vec.fit_transform(parameters).toarray()
        p = np.int8(p)
        #coords = np.int8(coords)
        #feats = np.int8(feats)
        cls_str = serialize_class(vec)
        json.dump(cls_str, open('./vec_class.json', 'w'))
        return vec
    else:
        p = vec.transform(parameters).toarray()
        p = np.int8(p)
        #coords = np.int8(coords)
        #feats = np.int8(feats)
    if testornot == 0:
        return p,coords,feats
    else:
        label = dataset['Success'].values
        label = np.int8(label)
        return p,coords,feats,label,vec