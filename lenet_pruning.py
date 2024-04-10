import torch.nn.utils.prune as prune
import numpy as np
import copy
from utils_lenet import __test__, __train__, load_model
from System_stat import*
import pandas as pd
from lenet_data import *
from IPython.display import display
import io
from torch.profiler import profile, record_function, ProfilerActivity


# COLUMN_NAMES = ['prune-config', 'prune-ratio','vm-percent','swap-percent','cpuloadavg-1min', 'cpuloadavg-5min', 'ratio','memory_consumption','acc']






def lenet_pruning(pruning_method,ratio):
    model =load_model()
    if pruning_method == 'l1_unstructured':
        conv_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Conv2d):
                if 'layer' in name:
                    conv_layers_to_prune.append((module, name))
        fc_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear):
                fc_layers_to_prune.append((module, name))

        for layer, name in conv_layers_to_prune:
            prune.l1_unstructured(layer, name='weight', amount=ratio)
        for layer, name in fc_layers_to_prune:
            prune.l1_unstructured(layer, name='weight', amount=ratio)

        for layer, name in conv_layers_to_prune:
            prune.remove(layer, name='weight')

    elif pruning_method == 'random_unstructured':
        fc_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear):
                fc_layers_to_prune.append((module, name))
        conv_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Conv2d):

                if 'layer' in name:
                    conv_layers_to_prune.append((module, name))


        for layer, name in conv_layers_to_prune:
            prune.random_unstructured(layer, name='weight', amount=ratio)
        for layer, name in fc_layers_to_prune:
            prune.random_unstructured(layer, name='weight', amount=ratio)
        for layer, name in conv_layers_to_prune:
            prune.remove(layer, name='weight')
    elif pruning_method == 'random_structured':
        fc_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear):
                fc_layers_to_prune.append((module, name))
        conv_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Conv2d):
                if 'layer' in name:
                    conv_layers_to_prune.append((module, name))
        for layer, name in conv_layers_to_prune:
            prune.random_structured(layer, name='weight', amount=ratio)
        for layer, name in fc_layers_to_prune:
            prune.random_structured(layer, name='weight', amount=ratio)
        for layer, name in conv_layers_to_prune:
            prune.remove(layer, name='weight')
    elif pruning_method == 'ln_structured':
        fc_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear):
                fc_layers_to_prune.append((module, name))
        conv_layers_to_prune = []
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Conv2d):
                if 'layer' in name:
                    conv_layers_to_prune.append((module, name))
        for layer, name in conv_layers_to_prune:
            prune.ln_structured(layer, name='weight', amount=ratio,n=2)
        for layer, name in fc_layers_to_prune:
            prune.ln_structured(layer, name='weight', amount=ratio,n=2)
        for layer, name in conv_layers_to_prune:
            prune.remove(layer, name='weight')
    


    prof = torch.profiler.profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA, torch.profiler.ProfilerActivity],profile_memory=True, record_shapes=True,with_flops=True)
    print ('Profiling run completed.\nCompiling result table')
    prof.start()
    acc = __test__(model)
    prof.stop()

    print ('Profiling run completed.\nCompiling result table')
    prof_result = prof.key_averages().table(sort_by='cpu_memory_usage', row_limit=100)
    prof_result_back = prof_result

        #Trim off the header and footer of the results
    prof_result_back = prof_result_back.rsplit("\n",3)[0]
    prof_result__ = ""
    for line in prof_result_back:
        if "-" not in line.split():
            prof_result__ += line 
    prof_result_back = prof_result__
    # print (prof_result_back)
    df = pd.read_csv(io.StringIO(prof_result_back), sep="\s\s+")

    # pd.set_option('display.max_rows', 500)
    # display(df)
    # # Filter DataFrame based on condition
    # filtered_df = df[df['Name'] == '[memory]']

    # # Check if filtered DataFrame is empty
    # if not filtered_df.empty:
    #     # If not empty, access the first element
    #     memory_consumption_str = filtered_df['CPU Mem'].iloc[0]
    # else:
    #     # Handle case where DataFrame is empty
    #     print("No data found for memory consumption.")
    #     memory_consumption_str = None  # or any appropriate default value
    #     memory_consumption_str = df[(df['Name']=='[memory]')]['CPU Mem'].iloc[1]
    

    # memory_consumption = 0
    # if ('Gb' in memory_consumption_str):
    #     memory_consumption =  float(memory_consumption_str.split()[0])*1024*1024*1024
    # elif ('Mb' in memory_consumption_str):
    #     memory_consumption =  float(memory_consumption_str.split()[0])*1024*1024
    # elif ('Kb' in memory_consumption_str):
    #     memory_consumption =  float(memory_consumption_str.split()[0])*1024
    # elif ('b' in memory_consumption_str):
    #     memory_consumption =  float(memory_consumption_str.split()[0])

    print(ratio, acc)
    return acc,prof_result,model

        

