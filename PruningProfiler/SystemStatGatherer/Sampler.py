import numpy as np
import pandas as pd
import datetime, time,threading, psutil
import os, subprocess, re

class SystemStatsGatherer:
    def __init__(self,  interval=2):
        self.temp_dict = {}
        self.not_firstime = False
        self.diskio_fieldname = ['read_count', 'write_count','read_bytes', 'write_bytes', 'read_time', 'write_time', 'read_merged_count', 'write_merged_count', 'busy_time']
        self.diskio_fieldvals = [0.0 , 0.0, 0.0, 0.0 , 0.0, 0.0, 0.0 , 0.0, 0.0]
        self.swap_mem_fieldname = ['total', 'used', 'free', 'percent', 'sin', 'sout']
        self.swap_mem_fieldvals = [0.0 , 0.0, 0.0, 0.0 , 0.0, 0.0]
        self.virtual_mem_fieldname = ['total', 'available','percent', 'used', 'free', 'active', 'inactive', 'buffers', 'cached', 'shared', 'slab']
        self.virtual_mem_fieldvals = [0.0 , 0.0, 0.0, 0.0 , 0.0, 0.0, 0.0 , 0.0, 0.0, 0.0, 0.0]
        self.tempsensor_fieldname = ['current','high', 'critical']
        self.tempsensor_fieldvals = [0.0 , 0.0, 0.0]
        self.samplerThread = threading.Thread(target=self.samplerThread)
        self.samplingInterval = interval
        self.stopThread = False


    def SampleTemp(self):

        tempsensor_name = ""
        res_temp = psutil.sensors_temperatures()
        res_diskio = psutil.disk_io_counters(perdisk=False, nowrap=True)
        res_swapmem = psutil.swap_memory()
        res_virtmem = psutil.virtual_memory()
        res_cpufreq = self.get_cpu_frequencies()
        res_psicpu = self.read_psi_info("cpu")
        res_psimem = self.read_psi_info("memory")
        res_psicio = self.read_psi_info("io")
        res_gpustat = self.get_gpu_load_and_memory_used()

        ctr = 0
        global not_firstime
        ts = datetime.datetime.now()
        if (self.not_firstime == False):
            self.temp_dict['time'] = [str(ts)]
        else:
            self.temp_dict['time'] += [str(ts)]

        ##get CPU frequencies
        if (self.not_firstime == False):
            for key, value in res_cpufreq.items():
                self.temp_dict[f'cpu_{key}'] = float(value)
        else:
            for key, value in res_cpufreq.items():
                self.temp_dict[f'cpu_{key}'] += float(value)

         ##get CPU PSI
        if (self.not_firstime == False):
            for key, value in res_psicpu.items():
                self.temp_dict[f'cpu_psi_{key}'] = value
        else:
            for key, value in res_psicpu.items():
                self.temp_dict[f'cpu_psi_{key}'] += value

         ##get Memory PSI
        if (self.not_firstime == False):
            for key, value in res_psimem.items():
                self.temp_dict[f'mem_psi_{key}'] = value
        else:
            for key, value in res_psimem.items():
                self.temp_dict[f'mem_psi_{key}'] += value

        ##get IO PSI
        if (self.not_firstime == False):
            for key, value in res_psicio.items():
                self.temp_dict[f'io_psi_{key}'] = value
        else:
            for key, value in res_psicio.items():
                self.temp_dict[f'io_psi_{key}'] += value

        ##get GPU stats
        # print ('res_gpustat ==> ',res_gpustat)
        for i, gpu_info in enumerate(res_gpustat):
            for key, value in gpu_info.items():
                column_name = f'{key}_{i+1}'
                if (self.not_firstime == False):
                    self.temp_dict[f'gpu_{column_name}'] = value
                else:
                    self.temp_dict[f'gpu_{column_name}'] = value
                
        ## get CPU Load averages
        loadavgs = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
        if (self.not_firstime == False):
            self.temp_dict['cpuloadavg_1min'] = loadavgs[0]
            self.temp_dict['cpuloadavg_5min'] = loadavgs[1]
            self.temp_dict['cpuloadavg_15min'] = loadavgs[2]
        else:
            self.temp_dict['cpuloadavg_1min'] += loadavgs[0]
            self.temp_dict['cpuloadavg_5min'] += loadavgs[1]
            self.temp_dict['cpuloadavg_15min'] += loadavgs[2]


        ## Process the Virtual Memory readings
        ctr = 0
        for val in res_virtmem:
            if (self.not_firstime == False):
                self.temp_dict['vm_'+self.virtual_mem_fieldname[ctr]] = [val]
            else:
                self.temp_dict['vm_'+self.virtual_mem_fieldname[ctr]] += [val]
            ctr += 1
        ## Process the Swap Memory readings
        ctr = 0
        for val in res_swapmem:
            if (self.not_firstime == False):
                self.temp_dict['swap_'+self.swap_mem_fieldname[ctr]] = [val]
            else:
                self.temp_dict['swap_'+self.swap_mem_fieldname[ctr]] += [val]
            ctr += 1
        ## Process the DiskIO readings
        ctr = 0
        for val in res_diskio:
            if (self.not_firstime == False):
                self.temp_dict['diskio_'+self.diskio_fieldname[ctr]] = [val]
            else:
                self.temp_dict['diskio_'+self.diskio_fieldname[ctr]] += [val]
            ctr += 1
        # Process the Temperature readings
        for key,values in res_temp.items():
            # print (key,' => ',values)
            for temp_elems in values:
                # print (temp_elems)
                tempsensor_name = key
                ctr = 0;title_field = True
                for val in temp_elems:
                    if (title_field == True):
                        tempsensor_name +=  '-'+str(val)
                        title_field = False
                    else:
                        self.tempsensor_fieldvals[ctr] = val
                        ctr += 1
                        
                    # print(key,'-', '=>',tempsensor_fieldname[ctr],'-->',sensor_val)
                # print (tempsensor_name,'=>',tempsensor_fieldvals)
                ctr = 0
                for elems in self.tempsensor_fieldvals:
                    # print (tempsensor_name+'-'+tempsensor_fieldname[ctr],'=>',elems)
                    if (self.not_firstime == False):
                        self.temp_dict[tempsensor_name+'-'+self.tempsensor_fieldname[ctr]] = [elems]
                    else:
                        self.temp_dict[tempsensor_name+'-'+self.tempsensor_fieldname[ctr]] += [elems]
                    ctr += 1
        self.not_firstime = True

    def getReadings(self):
        return self.temp_dict
    
    def samplerThread(self):
        while (self.stopThread != True):
            self.SampleTemp()
            time.sleep(self.samplingInterval)
        return
    
    def startSampling(self):
        self.stopThread = False
        self.samplerThread.start()
        return 

    def stopSampling(self):
        self.stopThread = True
        self.samplerThread.join()
        return 
    
    #Dynamic Info
    def get_cpu_frequencies(self):
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

    def get_gpu_load_and_memory_used(self):
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

    def read_psi_info(self, subsystem):
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

