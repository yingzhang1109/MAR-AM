import os
import torch
import torch.optim as optim
import MinkowskiEngine as ME
import MinkowskiEngine.MinkowskiFunctional as MF
from time import time
import argparse

#from test_load_data import data_loader
from torch.utils.data import  Dataset,DataLoader
import pandas as pd
from sklearn.model_selection import train_test_split
from preprocessing_coord import preprocessing
import numpy as np

class SimpleNet(ME.MinkowskiNetwork):

    def __init__(self, in_nchannel,in_nfeature2, out_nchannel, D):
        super(SimpleNet, self).__init__(D)
        self.block1 = torch.nn.Sequential(
            ME.MinkowskiConvolution(
                in_channels=in_nchannel,
                out_channels=16,
                kernel_size=3,
                stride=1,
                dimension=D),
            ME.MinkowskiBatchNorm(16))

        self.block2 = torch.nn.Sequential(
            ME.MinkowskiConvolution(
                in_channels=16,
                out_channels=32,
                kernel_size=3,
                stride=1,
                dimension=D),
            ME.MinkowskiBatchNorm(32))

        self.block3 = torch.nn.Sequential(
            ME.MinkowskiConvolution(
                in_channels=32,
                out_channels=64,
                kernel_size=3,
                stride=1,
                dimension=D),
            ME.MinkowskiBatchNorm(64))
        self.features2 = torch.nn.Sequential(
            torch.nn.Linear(in_nfeature2, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64,128),
            torch.nn.ReLU()
            )
        
        self.maxpool = ME.MinkowskiMaxPooling(kernel_size=2, stride=2, dimension=D)
        self.glob_avg = ME.MinkowskiGlobalMaxPooling()
        self.dense1 = torch.nn.Linear(192, 256, bias=True)
        self.dense2 = torch.nn.Linear(256, 512, bias=True)
        self.final = torch.nn.Linear(512, out_nchannel, bias=True)

    def forward(self, x1,x2):
        out_s1 = self.block1(x1)
        out1 = MF.relu(out_s1)
        out1 = self.maxpool(out1)

        out_s2 = self.block2(out1)
        out1 = MF.relu(out_s2)
        out1 = self.maxpool(out1)

        out_s3 = self.block3(out1)
        out1 = MF.relu(out_s3)
        out1 = self.glob_avg(out1)
        out2 = self.features2(x2)
        
        out = torch.cat((out1.F,out2),dim=1)
        out = self.dense1(out)
        out = torch.nn.functional.relu(out)
        out = torch.nn.functional.dropout(out, p=0.5)
        out = self.dense2(out)
        out = torch.nn.functional.relu(out)
        out = torch.nn.functional.dropout(out, p=0.5)
        out = self.final(out)
        out = torch.nn.functional.softmax(out)
        return out
    