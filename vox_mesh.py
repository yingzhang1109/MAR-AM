#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 14:04:20 2021

@author: ying
"""


import numpy as np
import trimesh

from lxml import etree

filename = 'OrganizadorHexagonal_demo.vxc'
parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(filename,parser)
root = tree.getroot()

alldata = root.findall("Structure/Data/Layer")
matrix = []
for data in alldata:
    for num in data.text:
        matrix.append(int(num))

matrix =np.array(matrix)
final = np.resize(matrix,(128,128,128))
final = np.transpose(final,(2,1,0))
final[final<2] =0
final[final==2] =1
voxel = trimesh.voxel
v = voxel.VoxelGrid(final)
mesh = v.as_boxes()
mesh.export('try.stl')