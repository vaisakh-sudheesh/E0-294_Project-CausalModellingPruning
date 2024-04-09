import os
import subprocess
import re
import pandas as pd
from IPython.display import display


def get_chipset_info():
    try:
        output = subprocess.check_output(["lscpu"]).decode("utf-8")
        for line in output.splitlines():
            if "Model name:" in line:
                chipset_name = line.split(":", 1)[1].strip()
                return chipset_name
    except Exception as e:
        return f"Error: {e}"

def get_cache_info():
    try:
        cache_info = {}
        cache_info["L1_Miss_Rate"] = "N/A"
        cache_info["L2_Miss_Rate"] = "N/A"

        output = subprocess.check_output(["lscpu"]).decode("utf-8")
        for line in output.splitlines():
            if "L1d cache:" in line:
                cache_info["L1_Size"] = line.split(":", 1)[1].strip()

        output = subprocess.check_output(["lscpu"]).decode("utf-8")
        for line in output.splitlines():
            if "L2 cache:" in line:
                cache_info["L2_Size"] = line.split(":", 1)[1].strip()

        perf_command = ["timeout", "5m", "perf", "stat","-I", "1000", "-e", "L1-dcache-load-misses,L1-dcache-loads,L1-dcache-stores,L1-dcache-store-misses,l2_rqsts.all_demand_miss,l2_rqsts.all_demand_references"]
        pipe = subprocess.Popen(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pipe.terminate()
        output, stderr = pipe.communicate()

        for line in output.splitlines():
            if "L1-dcache-load-misses" in line:
                L1_dcache_load_misses = int(line.split(",")[1].strip())
            elif "L1-dcache-loads" in line:
                L1_dcache_loads = int(line.split(",")[1].strip())
            elif "L1-dcache-store-misses" in line:
                L1_dcache_store_misses = int(line.split(",")[1].strip())
            elif "L1-dcache-store" in line:
                L1_dcache_stores = int(line.split(",")[1].strip())
            elif "l2_rqsts.all_demand_miss" in line:
                L2_all_demand_misses = int(line.split(",")[1].strip())
            elif "l2_rqsts.all_demand_references" in line:
                L2_all_demand_references = int(line.split(",")[1].strip())
        if L1_dcache_load_misses and L1_dcache_loads:
            cache_info["L1_Miss_Rate"] = L1_dcache_load_misses / L1_dcache_loads
        if L1_dcache_store_misses and L1_dcache_stores:
            cache_info["L1_Miss_Rate"] += L1_dcache_store_misses / L1_dcache_stores
        if L2_all_demand_misses and L2_all_demand_references:
            cache_info["L2_Miss_Rate"] = L2_all_demand_misses / L2_all_demand_references 

        return cache_info
    except Exception as e:
        return f"Error: {e}"

def get_ddr_info():
    try:
        output = subprocess.check_output(["sudo", "dmidecode", "--type", "memory"]).decode("utf-8")
        
        ddr_name = None
        ddr_brand = None
        ddr_speed = None
        ddr_info = []

        for line in output.splitlines():
            if "Memory Device" in line:
                ddr_name = None
                ddr_brand = None
                ddr_speed = None
            elif "Manufacturer:" in line:
                ddr_brand = line.split(":", 1)[1].strip()
            elif "Type:" in line:
                ddr_name = line.split(":", 1)[1].strip()
            elif "Speed:" in line:
                ddr_speed = line.split(":", 1)[1].strip()
            if ddr_name and ddr_brand and ddr_speed:
                ddr_info.append({"Name": ddr_name, "Brand": ddr_brand, "Speed": ddr_speed})
                ddr_name = None
                ddr_brand = None
                ddr_speed = None

        if ddr_info:
            return ddr_info
        else:
            return "DDR information not found"
    except Exception as e:
        return f"Error: {e}"

def get_cpu_frequencies():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()

        cpu_frequencies = {}
        current_core = None

        for line in cpuinfo.splitlines():
            if line.startswith('processor'):
                current_core = line.split(':')[1].strip()
            elif line.startswith('cpu MHz'):
                if current_core:
                    freq = line.split(':')[1].strip()
                    cpu_frequencies[current_core] = freq

        return cpu_frequencies

    except Exception as e:
        return f"Error: {e}"

def get_gpu_load_and_memory_used():
    try:
        output = subprocess.check_output(["gpustat"]).decode("utf-8")
        
        gpu_info = []

        for line in output.splitlines():
            if "|" in line:
                parts = line.strip().split("|")
                gpu_name = parts[0].strip().split(" ")[1] + parts[0].strip().split(" ")[2]
                gpu_load = parts[1].strip().split(",")[1].strip().split(" ")[0]
                gpu_memory_used = parts[2].strip().split("/")[0].strip()
                gpu_memory_total = parts[2].strip().split("/")[1].strip()
                gpu_info.append({"Name": gpu_name, "Load": gpu_load, "Memory Used": gpu_memory_used, "Total Memory": gpu_memory_total})
        
        return gpu_info

    except Exception as e:
        return f"Error: {e}"

def read_psi_info(subsystem):
    psi_file = f"/proc/pressure/{subsystem}"
    if not os.path.exists(psi_file):
        print(f"Error: {psi_file} does not exist")
        return None

    with open(psi_file, 'r') as file:
        line = file.read().strip()
        total_match = re.search(r'total=(\d+)', line)
        if total_match:
            total_value = float(total_match.group(1))
        else:
            total_value = None
        
        avg10_match = re.search(r'avg10=(\d+\.\d+)', line)
        avg60_match = re.search(r'avg60=(\d+\.\d+)', line)
        avg300_match = re.search(r'avg300=(\d+\.\d+)', line)

        psi_info = {
            "total": total_value,
            "avg10": float(avg10_match.group(1)) if avg10_match else None,
            "avg60": float(avg60_match.group(1)) if avg60_match else None,
            "avg300": float(avg300_match.group(1)) if avg300_match else None
        }
        
        return psi_info

def main():
    print("Chipset Info:", get_chipset_info())
    print("Cache Info:", get_cache_info())
    # print("DDR Info:", get_ddr_info())
    print("CPU Frequencies:", get_cpu_frequencies())
    print("GPU Load and Memory Used:", get_gpu_load_and_memory_used())
    print("CPU PSI:", read_psi_info("cpu"))
    print("IO PSI:", read_psi_info("io"))
    print("Memory PSI:", read_psi_info("memory"))

if __name__ == "__main__":
    main()

import psutil
import platform

def get_chipset_info():
    # Get system platform information
    return platform.machine()

# Get chipset info
chipset_name = get_chipset_info()
print("Chipset Name/Identifier:", chipset_name)

import pandas as pd

# Example existing DataFrame
existing_df = pd.DataFrame({'ExistingColumn': [1]})

# Example DDR Info
ddr_info = [{'Name': 'DDR4', 'Brand': 'OM Nanotech Pvt. Ltd', 'Speed': '2667 MT/s'},
            {'Name': 'DDR4', 'Brand': 'Samsung', 'Speed': '2667 MT/s'}]

# Create lists to store values from dictionaries
data = {}
for i, info in enumerate(ddr_info):
    for key, value in info.items():
        data.setdefault(key + str(i+1), []).append(value)

# Create DataFrame from DDR info
df_combined = pd.DataFrame(data)

# Concatenate existing DataFrame and DDR DataFrame along columns axis
df_concatenated = pd.concat([existing_df, df_combined], axis=1)

# Display the concatenated DataFrame
print(df_concatenated)

import subprocess

def get_cache_sizes():
    cache_info = {}

    # Get L1 cache size
    output = subprocess.check_output(["lscpu"]).decode("utf-8")
    for line in output.splitlines():
        if "L1d cache:" in line:
            cache_info["L1_Size"] = line.split(":", 1)[1].strip()

    # Get L2 cache size
    output = subprocess.check_output(["lscpu"]).decode("utf-8")
    for line in output.splitlines():
        if "L2 cache:" in line:
            cache_info["L2_Size"] = line.split(":", 1)[1].strip()

    # Return L1 and L2 cache sizes
    return cache_info.get("L1_Size"), cache_info.get("L2_Size")