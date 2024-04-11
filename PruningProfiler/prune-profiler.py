import subprocess, argparse
import platform
import re
import os
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

# File names for tool outputs
perf_output_file = 'perf.out'
nvprof_output_file = 'prof.out'

# Individual commands for each tool
## NVPROF for NVidia profiler
nvprof_cmd = ['nvprof', '-m' , nvprof_metrics, '--quiet', '--log-file',nvprof_output_file, '--system-profiling', 'on', '--csv']
## Perf for Intel & AMDprofiler
perf_cmd_intel = ['perf', 'stat', '-e', 'instructions,cycles,cache-references,cache-misses,branches,branch-misses', '-o',  perf_output_file , '-x', ',']
perf_cmd_amd = ['perf', 'stat', '-e', 'instructions,cycles,cache-references,cache-misses,branches,branch-misses', '-o', 'perf.out' , '-x', ',']
## The workload command to be profiled
prune_ratio = 0.0
prune_config = 'global_unstructured'
workload_cmd= ['python', 'prune-runner.py', '--model_name', 'lenet', '--pruning_method', prune_config, '--pruning_ratio', str(prune_ratio), '--filename', 'lenet.prof']

# Header fields for perf command output file
perf_data_headers = ["counter-value" , "unit", "event" , "event-runtime", "pcnt-running" , "metric-value", "metric-unit" ]


def parse_arguments():
    parser = argparse.ArgumentParser(description='Model pruning profiler/runner automation script for PyTorch models')
    parser.add_argument('--result_dir', type=str, required=True, default="output", help="Directory to store the profiling results")
    return parser.parse_args()

def prune_profiler():
    try:
        args = parse_arguments()
        results_dir = args.result_dir
        results_dir__ = os.path.join(os.getcwd(), results_dir)
        if not os.path.exists(results_dir__):
            os.mkdir(results_dir__)

        combined_cmd = []
        combined_cmd = perf_cmd_amd + nvprof_cmd + workload_cmd

        print (combined_cmd)

        statsMon = sysstat.SystemStatsGatherer()
        statsMon.startSampling()
        output,stderr = subprocess.check_output(combined_cmd).decode("utf-8")
        statsMon.stopSampling()
        print ("OUTPUT ==> ",output)
        print ("STDERR ==> ",stderr)

        # Parse the output files
        df_nvprof_data = pd.read_csv('prof.out', comment='=')
        df_perf_data = pd.read_csv('perf.out', skip_blank_lines=True, skiprows=2, names=perf_data_headers)
        df_stats = pd.DataFrame.from_dict(statsMon.getReadings())
        agg_df = df_stats
        agg_df__ =  agg_df.mean()
        # agg_df__['acc'] = acc
        agg_df__['prune_config'] = prune_config
        agg_df__['prune_ratio'] = prune_ratio
        agg_df__['chipset_name'] = sysinfo.get_chipset_info()
        agg_df__['arch'] = sysinfo.get_arch()
        l1_size, l2_size = sysinfo.get_cache_sizes()
        agg_df__['l1_size'] = l1_size
        agg_df__['l2_size'] = l2_size

        # Save the parsed data to the results directory
        df_nvprof_data.to_csv(os.path.join(results_dir__, 'nvprof_data.csv'))
        df_perf_data.to_csv(os.path.join(results_dir__, 'perf_data.csv'))
        agg_df.to_csv(os.path.join(results_dir__, 'system_stats.csv'))

    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    args = parse_arguments()
    prune_profiler()