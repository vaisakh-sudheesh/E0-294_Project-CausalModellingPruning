import argparse
import pandas as pd
from IPython.display import display
from utils import *
from pruning import *
from System_stat import *
from torch.utils.data import DataLoader
from torchvision import transforms
import torch
import torchvision
from tqdm import tqdm
from lenet_data import *
from lenet_pruning import *
import os
def parse_arguments():
    parser = argparse.ArgumentParser(description='Model Pruning Profiler')
    parser.add_argument('--pruning_method', type=str, required=True, default="l1_unstructured")
    parser.add_argument('--filename', type=str, required=True)
    return parser.parse_args()

def LenNetModelPruner():
    args = parse_arguments()


    df_final = pd.DataFrame()
    for ratio in np.arange(0.0, 1.0, 0.1):
        stats_mon = SystemStatsGatherer()
        stats_mon.startSampling()
        acc ,prof_result,model= lenet_pruning(args.pruning_method,ratio)
        stats_mon.stopSampling()
        print('Collecting System Stats')
        df_stats = pd.DataFrame.from_dict(stats_mon.getReadings())
        agg_df = df_stats[['vm_percent','swap_percent','cpuloadavg_1min', 'cpuloadavg_5min']]
        agg_df__ =  agg_df.mean()
        agg_df__['ratio'] = ratio
    
        agg_df__['acc'] = acc
        agg_df__['prune_config'] = f'{args.pruning_method}-ratio-{ratio}'
        agg_df__['prune_ratio'] = ratio
   
    
        display(agg_df__)
        df_final = pd.concat([df_final,agg_df__], axis=1)
        print('Aggregated stats')
        display(df_final)
        del prof_result
    del model

    SAVE_DIR = os.getcwd()

    DF_SAVEFILENAME = os.path.join(SAVE_DIR, args.filename)
    df_final_transpose = df_final.transpose().reset_index(drop=True)
    display(df_final_transpose)
    df_final_transpose.to_csv(DF_SAVEFILENAME, encoding='utf-8', sep=',')
    


if __name__ == "__main__":
    LenNetModelPruner()
