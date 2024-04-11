import subprocess
import platform
import re
import os

#Static Info
def get_chipset_info():
    try:
        output = subprocess.check_output(["lscpu"]).decode("utf-8")
        for line in output.splitlines():
            if "Model name:" in line:
                chipset_name = line.split(":", 1)[1].strip()
                return chipset_name
    except Exception as e:
        return f"Error: {e}"
    

def get_arch():
    # Get system platform information
    return platform.machine()

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
                ddr_info.append({"DDR_Name": ddr_name, "DDR_Brand": ddr_brand, "DDR_Speed": ddr_speed})
                ddr_name = None
                ddr_brand = None
                ddr_speed = None

        if ddr_info:
            return ddr_info
        else:
            return "DDR information not found"
    except Exception as e:
        return f"Error: {e}"
    
#Dynamic Info
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
                gpu_name = parts[0].strip()
                gpu_load = parts[1].strip().split(",")[1].strip().split(" ")[0]
                gpu_memory_used = parts[2].strip().split("/")[0].strip()
                gpu_memory_total = parts[2].strip().split("/")[1].strip().split(" ")[0]
                gpu_info.append({"GPU_Load": gpu_load, "GPU_Memory_Used": gpu_memory_used, "GPU_Total_Memory": gpu_memory_total})
        
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
