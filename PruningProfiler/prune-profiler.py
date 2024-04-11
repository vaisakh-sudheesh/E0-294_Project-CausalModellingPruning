import subprocess
import platform
import re
import os




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
nvprof_cmd = ['nvprof', '-m' , nvprof_metrics, '--quiet', '--log-file','prof.out', '--system-profiling', 'on', '--csv']
perf_cmd_intel = ['perf', 'stat', '-e', 'instructions,cycles,cache-references,cache-misses,branches,branch-misses', '-o', 'perf.out' , '-X', ',']
perf_cmd_amd = ['perf', 'stat', '-e', 'instructions,cycles,cache-references,cache-misses,branches,branch-misses', '-o', 'perf.out' , '-X', ',']

def prune_profiler():
    try:
        output = subprocess.check_output(["python"]).decode("utf-8")
        for line in output.splitlines():
            if "Model name:" in line:
                chipset_name = line.split(":", 1)[1].strip()
                return chipset_name
    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    prune_profiler()