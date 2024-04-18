import os
from torch.utils.data import DataLoader
import torch
from torchvision import transforms
from torch.utils.data import Dataset
from PIL import Image
import json
BASE_DIR = os.getcwd()


class ImageNetKaagle:
    def __init__(self):
        self.imagenet_path = os.path.join(BASE_DIR, 'Data/imagenet')
        self.mean = (0.485, 0.456, 0.406)
        self.std = (0.229, 0.224, 0.225)
        self.val_transform = transforms.Compose(
                    [
                        transforms.Resize(256),
                        transforms.CenterCrop(224),
                        transforms.ToTensor(),
                        transforms.Normalize(self.mean, self.std),
                    ]
                )
        self.dataset = self.__ImageNetKaggle(self.imagenet_path, "val", self.val_transform)
        self.dataloader = DataLoader(
                    self.dataset,
                    batch_size=64, # may need to reduce this depending on your GPU 
                    num_workers=8, # may need to reduce this depending on your num of CPUs and RAM
                    shuffle=False,
                    drop_last=False,
                    pin_memory=True
                )
    
    class __ImageNetKaggle(Dataset):
        def __init__(self, root, split, transform=None, num_samples=500):
            self.samples = []
            self.targets = []
            self.transform = transform
            self.syn_to_class = {}
            with open(os.path.join(root, "imagenet_class_index.json"), "rb") as f:
                        json_file = json.load(f)
                        for class_id, v in json_file.items():
                            self.syn_to_class[v[0]] = int(class_id)
            with open(os.path.join(root, "ILSVRC2012_val_labels.json"), "rb") as f:
                        self.val_to_syn = json.load(f)
            samples_dir = os.path.join(root, "", split)
            for entry in os.listdir(samples_dir)[:num_samples]:
                syn_id = self.val_to_syn[entry]
                target = self.syn_to_class[syn_id]
                sample_path = os.path.join(samples_dir, entry)
                self.samples.append(sample_path)
                self.targets.append(target)

        def __len__(self):
                return len(self.samples)
        def __getitem__(self, idx):
                x = Image.open(self.samples[idx]).convert("RGB")
                if self.transform:
                    x = self.transform(x)
                return x, self.targets[idx]
    
    def get_trainloader(self):
        return self.dataloader
    
    def get_testloader(self):
        return self.dataloader
    
