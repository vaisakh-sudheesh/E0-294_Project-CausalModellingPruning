from torch.utils.data import DataLoader
from torchvision import transforms
import torch
import torchvision
from tqdm import tqdm
import os
from imagenet_dataset import *

optimizer = None
loss_fn = None
BASE_DIR = os.getcwd()

device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

def load_model(model_name):
    supported_models = ['resnet', 'alexnet', 'googlenet', 'vgg16', 'lenet']
    if model_name.lower() not in supported_models:
        raise ValueError(f"Unsupported model: {model_name}. Supported models are: {supported_models}")
    model=None
    if model_name.lower() == 'resnet':
        model = torchvision.models.resnet50(weights="DEFAULT")
        print("resnet")
    elif model_name.lower() == 'alexnet':
        model =torchvision.models.alexnet(weights="DEFAULT")
    elif model_name.lower() =='googlenet':
        model=torchvision.models.googlenet(weights="DEFAULT")
    elif model_name.lower() =='vgg16':
        model = torchvision.models.vgg16(weights="DEFAULT")
    model.to(device)
    model.eval()  
    return model





def test (model,model_name)-> float:
    
        acc = 0
        total = 0
        with torch.no_grad():
            for x, y in tqdm(dataloader):
                x= x.to(device)
                y=y.to(device)
                y_pred = model(x)
                acc += (torch.argmax(y_pred, 1) == y).float().sum()
                total += len(y)
        acc=acc / total
        acc__=acc.cpu()
        return acc__.numpy()*100


    