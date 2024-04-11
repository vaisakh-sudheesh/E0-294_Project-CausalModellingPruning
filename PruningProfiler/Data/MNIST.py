import torch
import torchvision

class MNIST:
    def __init__(self):
        transform = torchvision.transforms.Compose([
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize((0,), (128,)),
        ])
        self.train = torchvision.datasets.MNIST('Data/dataset', train=True, download=True, transform=transform)
        self.test = torchvision.datasets.MNIST('Data/dataset', train=False, download=True, transform=transform)
        self.trainloader = torch.utils.data.DataLoader(self.train, shuffle=True, batch_size=100)
        self.testloader = torch.utils.data.DataLoader(self.test, shuffle=True, batch_size=100)
    
    def get_trainloader(self):
        return self.trainloader
    
    def get_testloader(self):
        return self.testloader