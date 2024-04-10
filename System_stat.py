
import pandas as pd
import datetime, time,threading, psutil

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
        # res_temp = psutil.sensors_temperatures()
        res_diskio = psutil.disk_io_counters(perdisk=False, nowrap=True)
        res_swapmem = psutil.swap_memory()
        res_virtmem = psutil.virtual_memory()
        ctr = 0
        global not_firstime
        ts = datetime.datetime.now()
        if (self.not_firstime == False):
            self.temp_dict['time'] = [str(ts)]
        else:
            self.temp_dict['time'] += [str(ts)]

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
        ## Process the Temperature readings
        # for key,values in res_temp.items():
        #     # print (key,' => ',values)
        #     for temp_elems in values:
        #         # print (temp_elems)
        #         tempsensor_name = key
        #         ctr = 0;title_field = True
        #         for val in temp_elems:
        #             if (title_field == True):
        #                 tempsensor_name +=  '-'+str(val)
        #                 title_field = False
        #             else:
        #                 self.tempsensor_fieldvals[ctr] = val
        #                 ctr += 1
                        
                    # print(key,'-', '=>',tempsensor_fieldname[ctr],'-->',sensor_val)
                # print (tempsensor_name,'=>',tempsensor_fieldvals)
                # ctr = 0
                # for elems in self.tempsensor_fieldvals:
                #     # print (tempsensor_name+'-'+tempsensor_fieldname[ctr],'=>',elems)
                #     if (self.not_firstime == False):
                #         self.temp_dict[tempsensor_name+'-'+self.tempsensor_fieldname[ctr]] = [elems]
                #     else:
                #         self.temp_dict[tempsensor_name+'-'+self.tempsensor_fieldname[ctr]] += [elems]
                #     ctr += 1
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
