# -*- coding: utf-8 -*-
"""AlexNet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1k4UxfQaidO6cD17y2P6KhJ9U4Pmla2RZ
"""

import os
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.utils.data.dataset import Subset

from torchvision import datasets
from torchvision import transforms

import matplotlib.pyplot as plt
from PIL import Image

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline

randomseed = 1
learning_rate= 0.002
BATCH_SIZE= 128
NUM_EPOCHS= 20
NUM_CLASSES = 10

DEVICE = "cuda:0"

train_indices = torch.arange(0, 48000)
valid_indices = torch.arange(48000, 50000)


train_transform = transforms.Compose([transforms.Resize((70, 70)),
                                      transforms.RandomCrop((64, 64)),
                                      transforms.ToTensor()])

test_transform = transforms.Compose([transforms.Resize((70, 70)),
                                     transforms.CenterCrop((64, 64)),
                                     transforms.ToTensor()])

train_and_valid = datasets.CIFAR10(root='data', 
                                   train=True, 
                                   transform=train_transform,
                                   download=True)

train_dataset = Subset(train_and_valid, train_indices)
valid_dataset = Subset(train_and_valid, valid_indices)
test_dataset = datasets.CIFAR10(root='data', 
                                train=False, 
                                transform=test_transform,
                                download=False)




train_loader = DataLoader(dataset=train_dataset, 
                          batch_size=BATCH_SIZE,
                          num_workers=4,
                          shuffle=True)

valid_loader = DataLoader(dataset=valid_dataset, 
                          batch_size=BATCH_SIZE,
                          num_workers=4,
                          shuffle=False)

test_loader = DataLoader(dataset=test_dataset, 
                         batch_size=BATCH_SIZE,
                         num_workers=4,
                         shuffle=False)



torch.manual_seed(0)

# Check that shuffling works properly
# i.e., label indices should be in random order.
# Also, the label order should be different in the second
# epoch.

for images, labels in train_loader:  
    pass
print(labels[:10])

for images, labels in train_loader:  
    pass
print(labels[:10])

# Check that validation set and test sets are diverse
# i.e., that they contain all classes

for images, labels in valid_loader:  
    pass
print(labels[:10])

for images, labels in test_loader:  
    pass
print(labels[:10])

class AlexNet(nn.Module):
  def __init__(self,num_classes):
    super(AlexNet,self).__init__()
    self.features = nn.Sequential(
        nn.Conv2d(3,64,kernel_size = 11, stride = 4, padding=2 ),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(kernel_size = 3,stride= 2) ,

        nn.Conv2d(64,192,kernel_size = 5, padding=2 ),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(kernel_size = 3,stride= 2),

        nn.Conv2d(192,384,kernel_size = 3, padding=1 ),
        nn.ReLU(inplace=True),

        nn.Conv2d(384,256,kernel_size = 3, padding=1 ),
        nn.ReLU(inplace=True),
        
        nn.Conv2d(256,256,kernel_size = 3, padding=1),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(kernel_size = 3,stride= 2),
        )
    self.avgpool = nn.AdaptiveAvgPool2d((6,6))
    self.classifier = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(256*6*6,4096),
        nn.ReLU(inplace=True),
        nn.Dropout(0.5),
        nn.ReLU(inplace= True),
        nn.Linear(4096,4096),
        nn.ReLU(inplace=True),
        nn.Linear(4096,num_classes)

    )

  def forward(self,x):
    x = self.features(x)
    x = self.avgpool(x)
    x = x.view(x.size(0), 256 * 6 * 6)
    logits = self.classifier(x)
    probas = F.softmax(logits, dim=1)
    return logits, probas

torch.manual_seed(randomseed)

model = AlexNet(NUM_CLASSES)
model.to(DEVICE)

optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

def compute_acc(model,data_loader,device):
  correct_pred,num_examples = 0,0
  model.eval()
  for i,(features,targets) in enumerate(data_loader):
    features = features.to(device)
    targets=targets.to(device)

    logits, probas = model(features)
    _, predicted_labels = torch.max(probas, 1)
    num_examples += targets.size(0)
    assert predicted_labels.size() == targets.size()
    correct_pred += (predicted_labels == targets).sum()
  return correct_pred.float()/num_examples * 100

start_time = time.time()

cost_list = []
train_acc_list, valid_acc_list = [], []


for epoch in range(epochs):
    
    model.train()
    for batch_idx, (features, targets) in enumerate(train_loader):
        
        features = features.to(DEVICE)
        targets = targets.to(DEVICE)
            
        ### FORWARD AND BACK PROP
        logits, probas = model(features)
        cost = F.cross_entropy(logits, targets)
        optimizer.zero_grad()
        
        cost.backward()
        
        ### UPDATE MODEL PARAMETERS
        optimizer.step()
        
        #################################################
        ### CODE ONLY FOR LOGGING BEYOND THIS POINT
        ################################################
        cost_list.append(cost.item())
        if not batch_idx % 150:
            print (f'Epoch: {epoch+1:03d}/{NUM_EPOCHS:03d} | '
                   f'Batch {batch_idx:03d}/{len(train_loader):03d} |' 
                   f' Cost: {cost:.4f}')

        

    model.eval()
    with torch.set_grad_enabled(False): # save memory during inference
        
        train_acc = compute_acc(model, train_loader, device=DEVICE)
        valid_acc = compute_acc(model, valid_loader, device=DEVICE)
        
        print(f'Epoch: {epoch+1:03d}/{NUM_EPOCHS:03d}\n'
              f'Train ACC: {train_acc:.2f} | Validation ACC: {valid_acc:.2f}')
        
        train_acc_list.append(train_acc)
        valid_acc_list.append(valid_acc)
        
    elapsed = (time.time() - start_time)/60
    print(f'Time elapsed: {elapsed:.2f} min')
  
elapsed = (time.time() - start_time)/60
print(f'Total Training Time: {elapsed:.2f} min')

if torch.cuda.is_available():
    torch.backends.cudnn.deterministic = True

