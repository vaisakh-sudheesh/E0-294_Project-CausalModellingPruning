import Data.MNIST as MNIST
from Models.BaseModel import BaseModel


import torch
import torch.nn as nn
import torch.optim as optim
import torchvision

class __LeNet5__(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5, stride=1, padding=2)
        self.act1 = nn.Tanh()
        self.pool1 = nn.AvgPool2d(kernel_size=2, stride=2)

        self.conv2 = nn.Conv2d(6, 16, kernel_size=5, stride=1, padding=0)
        self.act2 = nn.Tanh()
        self.pool2 = nn.AvgPool2d(kernel_size=2, stride=2)

        self.conv3 = nn.Conv2d(16, 120, kernel_size=5, stride=1, padding=0)
        self.act3 = nn.Tanh()

        self.flat = nn.Flatten()
        self.fc1 = nn.Linear(1*1*120, 84)
        self.act4 = nn.Tanh()
        self.fc2 = nn.Linear(84, 10)
        
    def forward(self, x):
        # input 1x28x28, output 6x28x28
        x = self.act1(self.conv1(x))
        # input 6x28x28, output 6x14x14
        x = self.pool1(x)
        # input 6x14x14, output 16x10x10
        x = self.act2(self.conv2(x))
        # input 16x10x10, output 16x5x5
        x = self.pool2(x)
        # input 16x5x5, output 120x1x1
        x = self.act3(self.conv3(x))
        # input 120x1x1, output 84
        x = self.act4(self.fc1(self.flat(x)))
        # input 84, output 10
        x = self.fc2(x)
        return x

class LeNet(BaseModel):
    def __init__(self):
        self.__MODEL_FILENAME = "Models/LeNet5.pth"

        # Initialize the dataset
        self.mnist = MNIST.MNIST()
        trainloader = self.mnist.get_trainloader()
        testloader = self.mnist.get_testloader()
        
        # Initialize the base class 
        super().__init__(trainloader, testloader)

        # Setup the model
        self.model = __LeNet5__().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters())
        self.loss_fn = nn.CrossEntropyLoss()

    def get_model(self):
        return self.model
    
    def load_model(self):
        return super().load_model(self.__MODEL_FILENAME)
    
    def save_model(self):
        return super().save_model(self.__MODEL_FILENAME)
    
    def test(self):
        return super().test()
    
    def train(self, n_epochs=10):
        return super().train(n_epochs)
