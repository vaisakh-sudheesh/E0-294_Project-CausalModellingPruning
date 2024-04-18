import subprocess, argparse
import platform
import re
import os, pathlib
import pandas as pd
import numpy as np

import SystemStatGatherer.Sampler as sysstat
import SystemStatGatherer as sysinfo


# Metrics to be collected by NVPROF
nvprof_metrics = (
    'inst_per_warp,'+
    'branch_efficiency,warp_execution_efficiency,'+
    'global_hit_rate,local_hit_rate,'+
    'flop_count_dp,flop_count_sp,'+
    'inst_executed,inst_issued,'+
    'sysmem_utilization,'+
    'stall_sync,stall_other,stall_memory_dependency,stall_pipe_busy,stall_constant_memory_dependency,'+
    'inst_fp_32,inst_fp_64,'+
    'inst_integer,inst_bit_convert,inst_control,inst_compute_ld_st,inst_misc,inst_inter_thread_communication,'+
    'cf_issued,cf_executed,'+
    'ldst_issued,ldst_executed,'+
    'flop_count_hp,'+
    'inst_fp_16,'+
    'ipc,issued_ipc,'+
    'flop_hp_efficiency,flop_sp_efficiency,flop_dp_efficiency,'+
    'dram_read_transactions,dram_read_transactions,dram_read_throughput,dram_write_throughput,dram_utilization'
)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Model pruning profiler/runner automation script for PyTorch models')
    parser.add_argument('--result_dir', type=str, required=True, default="output", help="Directory to store the profiling results")
    return parser.parse_args()

def prune_profiler(results_dir, model_name = 'lenet', prune_ratio = 0.0, prune_config = 'l1_unstructured'):
    results_dir__ = os.path.join(os.getcwd(), results_dir)
    if not os.path.exists(results_dir__):
        results_dir_path = pathlib.Path(results_dir__)
        results_dir_path.mkdir(parents=True, exist_ok=True)


    # File names for tool outputs
    perf_output_file = os.path.join(results_dir__,  'perf.out')
    nvprof_output_file = os.path.join(results_dir__,  'prof.out')

    # Individual commands for each tool
    ## NVPROF for NVidia profiler
    nvprof_cmd = ['nvprof', '-m' , nvprof_metrics, '--quiet', '--log-file',nvprof_output_file, '--system-profiling', 'on', '--csv']
    ## Perf for Intel & AMDprofiler
    perf_cmd_intel = ['perf', 'stat', '-e', 'instructions,cycles,cache-references,cache-misses,branches,branch-misses', '-o',  perf_output_file , '-x', ',']
    perf_cmd_amd = ['perf', 'stat', '-e', 'instructions,cycles,cache-references,cache-misses,branches,branch-misses', '-o', perf_output_file , '-x', ',']
    ## The workload command to be profiled
    #workload_cmd= ['python', 'prune-runner.py', '--model_name', 'lenet', '--pruning_method', prune_config, '--pruning_ratio', str(prune_ratio)]
    workload_cmd= ['python', 'prune-runner.py', '--model_name', model_name, '--pruning_method', prune_config, '--pruning_ratio', str(prune_ratio)]

    # Header fields for perf command output file
    perf_data_headers = ["counter-value" , "unit", "event" , "event-runtime", "pcnt-running" , "metric-value", "metric-unit" ]

    # Pruning configurations
    combined_cmd = []
    #combined_cmd = perf_cmd_amd + nvprof_cmd + workload_cmd
    combined_cmd = workload_cmd
    print (combined_cmd)

    try:
        statsMon = sysstat.SystemStatsGatherer()
        statsMon.startSampling()
        #output,stderr = subprocess.check_output(combined_cmd).decode("utf-8")
        process = subprocess.Popen(combined_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, stderr = process.communicate()
        output = output.decode("utf-8")
        stderr = stderr.decode("utf-8")
        rc = process.returncode

        if rc != 0:
            print ("Iteration not completed due to error..")
            acc = 'DNF'
            for line in stderr.splitlines():
                if "torch.cuda.OutOfMemoryError" in line:
                    acc = 'NDF-OOM'
                    print ("!! OOM")
                elif "torch.cuda.OutOfMemoryError" in line:
                    acc = 'DNF-DATA_ERROR'
                    print ("!! Data Error")
        else:
            acc = ''
            for line in output.splitlines():
                if "Done - Accuracy after pruning:" in line:
                    acc = line.split(":", 1)[1].strip()

        statsMon.stopSampling()

    except Exception as e:
        return f"Error: {e}"

    print(f'Completed profiling run with accuracy = {acc}...')
    # Parse the output files
    print(f'Processing results...')
    # df_nvprof_data = pd.read_csv( nvprof_output_file, comment='=')
    # df_perf_data = pd.read_csv(perf_output_file , skip_blank_lines=True, skiprows=2, names=perf_data_headers)
    dicts= statsMon.getReadings()
    df_stats = pd.DataFrame.from_dict(dicts)
    agg_df = df_stats[['vm_percent','swap_percent','cpuloadavg_1min', 'cpuloadavg_5min', 'cpu_0', 'cpu_1', 'cpu_psi_total', 'mem_psi_total', 'io_psi_total']]
    agg_df__ =  agg_df.mean()
    agg_df__['acc'] = acc
    agg_df__['prune_config'] = prune_config
    agg_df__['prune_ratio'] = prune_ratio
    agg_df__['chipset_name'] = sysinfo.get_chipset_info()
    agg_df__['arch'] = sysinfo.get_arch()
    l1_size, l2_size = sysinfo.get_cache_sizes()
    agg_df__['l1_size'] = l1_size
    agg_df__['l2_size'] = l2_size

    # Save the parsed data to the results directory
    print("Saving results dataframes...")
    # res_csv_nvprof = os.path.join(results_dir__, 'nvprof_data.csv')
    # print("\tNVPROF: ",res_csv_nvprof)
    # df_nvprof_data.to_csv(res_csv_nvprof)

    # res_csv_perf = os.path.join(results_dir__, 'perf_data.csv')
    # print("\tPERF: ",res_csv_perf)
    # df_perf_data.to_csv(res_csv_perf)

    res_csv_sysstat = os.path.join(results_dir__, 'system_stats.csv')
    print("\tSysStat Summary: ",res_csv_sysstat)
    agg_df__.to_csv(res_csv_sysstat)

    res_csv_fullsysstat = os.path.join(results_dir__, 'full_system_stats.csv')
    print("\tFull System Stats: ",res_csv_fullsysstat)
    df_stats.to_csv(res_csv_fullsysstat)

    # df_stats

def lenet():
    model_name_list = ['lenet']
    pruning_config = ['global_unstructured']
    for modelname in model_name_list:
        for pruneconf in pruning_config:
            for ratio in np.arange(0.0,0.8,0.1):
                results_dir = 'output/'+modelname+'-'+pruneconf+'-'+str(ratio)
                print ('>>> Iteration Config',modelname+'-'+pruneconf+'-'+str(ratio))
                prune_profiler(results_dir, model_name = modelname, prune_ratio = ratio, prune_config = pruneconf)

def resnetRun():
    model_name_list = [
           'resnet',
           'alexnet',
           'vgg16',
           'googlenet'
         ]
    pruning_config = ['l1_unstructured', 'ln_structured', 'random_unstructured']
    for modelname in model_name_list:
        for pruneconf in pruning_config:
            for ratio in np.arange(0.0,0.8,0.1):
                results_dir = 'output/'+modelname+'-'+pruneconf+'-'+str(ratio)
                print ('=== Iteration Config',modelname+'-'+pruneconf+'-'+str(ratio))
                prune_profiler(results_dir, model_name = modelname, prune_ratio = ratio, prune_config = pruneconf)


if __name__ == '__main__':
    # args = parse_arguments()

    # lenet()
    resnetRun()

    # results_dir = args.result_dir
    # args = parse_arguments(results_dir)
    # prune_profiler()
