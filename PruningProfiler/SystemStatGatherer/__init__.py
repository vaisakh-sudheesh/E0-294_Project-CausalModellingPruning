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
    
