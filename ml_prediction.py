#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  4 13:37:00 2021

@author: ying
"""
import torch
from ManuNet_combine import SimpleNet
import numpy as np
#import matplotlib as plt
import json
import serialize_sk as sr
import sys
import pandas as pd
from preprocessing_coord import preprocessing
import MinkowskiEngine as ME

def deserialize_class(cls_repr):
    cls_repr = sr.json_to_data(cls_repr)
    cls_ = getattr(sys.modules[cls_repr['mod']], cls_repr['name'])
    cls_init = cls_()
    for k, v in cls_repr['attr'].items():
        setattr(cls_init, k, v)
    return cls_init


def ml_prediction(data):
    
    cls_js = json.load(open('./vec_class.json'))
    vec = deserialize_class(cls_js)
    
    #dataset = pd.read_pickle('sparse_FDM_v2.pickle')
    #data = dataset.head(1)
    #data = dataset[5:6]
    p,c,f = preprocessing(data,vec,0)
    
    #true_target = data['Success']
    # Disable grad
    with torch.no_grad():
       
        # Loading the saved model
        save_path = 'state_dict_model.pt'     
        net = SimpleNet(1, 16, 2, D=3)
        
        # Set the parameters
        net.load_state_dict(torch.load(save_path))
        #device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        device = torch.device('cpu')
        net = net.to(device)
        net.eval()
        # Generate prediction
        c = torch.IntTensor(c[0])
        f = torch.FloatTensor(f[0])
        #p =np.array(p,dtype=np.float32)
        #p = torch.from_numpy(p)
        p = torch.FloatTensor(p)
        coords, feats = ME.utils.sparse_collate(coords=[c], feats=[f])
        d = ME.SparseTensor(feats, coords, device = device)
        #d = ME.SparseTensor(f.float(), c, device = device)
        p = p.to(device)
        prediction = net(d,p)
          
        # Predicted class value using argmax
        predicted_class = np.argmax(prediction)
          
        #print(true_target)
        return predicted_class,prediction

