from torch.utils.data import DataLoader
from torchvision import transforms
import torch
import torchvision
from tqdm import tqdm
import os
from model import LeNet5
import torch.nn as nn
from lenet_data import *
import torch.optim as optim

optimizer = None
loss_fn = None
BASE_DIR = os.getcwd()

device = (
    "cuda:2" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

def load_model():
    global model, optimizer, loss_fn
    print (os.path.curdir)
    model = LeNet5().to(device)
    optimizer = optim.Adam(model.parameters())
    loss_fn = nn.CrossEntropyLoss()
    
    MODEL_FILENAME='/raid/home/anishkar/E0-294_Project-CausalModellingPruning/model.sav'
    if (os.path.isfile(MODEL_FILENAME) != True):
        __train__(model, 10)
        torch.save(model.state_dict(),MODEL_FILENAME)
        print (f'Model saved to {MODEL_FILENAME}')
    else:
        model.load_state_dict(torch.load(MODEL_FILENAME))
        model.to(device)
        model.eval()
        return model

def __test__ (model__)-> float:
    model__.eval()
    acc = 0
    count = 0
    for X_batch, y_batch in testloader:
        X_batch = X_batch.to(device); y_batch = y_batch.to(device)
        y_pred = model__(X_batch)
        acc += (torch.argmax(y_pred, 1) == y_batch).float().sum()
        count += len(y_batch)
    acc = acc / count
    acc__ = acc.cpu()
    return acc__.numpy()*100
    

def __train__ (model__, n_epochs=10):
    for epoch in range(n_epochs):
        model__.train()
        for X_batch, y_batch in trainloader:
            X_batch = X_batch.to(device); y_batch = y_batch.to(device)
            y_pred = model__(X_batch)
            loss = loss_fn(y_pred, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print("Epoch %d: model accuracy %.2f%%" % (epoch, __test__(model__)))
