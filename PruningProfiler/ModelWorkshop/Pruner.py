import torch.nn.utils.prune as prune
import numpy as np
import pandas as pd
import io
import torch

class Pruner:
    def __init__(self, model):
        self.model = model
        self.fc_layers_to_prune = []
        self.conv_layers_to_prune = []

    ## TODO: Messy handlng of model specific layer identification, please clean it up :D

    def prune(self, ratio, method):
        # Invoke appropriate pruning method
        if method == 'global_unstructured':
            self.global_unstructured(ratio)
        else :
            for name, module in self.model.named_modules():
                if isinstance(module, torch.nn.Linear):
                    self.fc_layers_to_prune.append((module, name))

            for name, module in self.model.named_modules():
                if isinstance(module, torch.nn.Conv2d):
                    if 'layer' in name:
                        self.conv_layers_to_prune.append((module, name))
            if method == 'l1_unstructured':
                self.l1_unstructured(ratio)
            elif method == 'random_unstructured':
                self.random_unstructured(ratio)
            elif method == 'ln_structured':
                self.ln_structured(ratio)
            elif method == 'ln_unstructured':
                self.ln_unstructured(ratio)
            else:
                raise ValueError('Invalid pruning method')

        for layer, name in self.conv_layers_to_prune:
            prune.remove(layer, name='weight')

        

    #### Helper methods for pruning strategies ####

    def l1_unstructured(self, ratio):
        for layer, name in self.conv_layers_to_prune:
            prune.l1_unstructured(layer, name='weight', amount=ratio)
        for layer, name in self.fc_layers_to_prune:
            prune.l1_unstructured(layer, name='weight', amount=ratio)

    def random_unstructured(self, ratio):
        for layer, name in self.conv_layers_to_prune:
            prune.random_unstructured(layer, name='weight', amount=ratio)
        for layer, name in self.fc_layers_to_prune:
            prune.random_unstructured(layer, name='weight', amount=ratio)

    def random_structured(self, ratio):
        for layer, name in self.conv_layers_to_prune:
            prune.random_structured(layer, name='weight', amount=ratio)
        for layer, name in self.fc_layers_to_prune:
            prune.random_structured(layer, name='weight', amount=ratio)


    def ln_structured(self, ratio):
        for layer, name in self.conv_layers_to_prune:
            prune.ln_structured(layer, name='weight', amount=ratio,n=2)
        for layer, name in self.fc_layers_to_prune:
            prune.ln_structured(layer, name='weight', amount=ratio,n=2)

    def global_unstructured(self, ratio):
        parameters = ((self.model.conv1, "weight"),(self.model.conv2, "weight"),(self.model.fc1, "weight"),(self.model.fc2, "weight"),)
        prune.global_unstructured(parameters,pruning_method=prune.L1Unstructured,amount=ratio)