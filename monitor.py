#!/usr/bin/env python
## coding: latin-1
import os, sys

import sys, time
from daemon.daemon import Daemon
from time import gmtime, strftime
from datetime import datetime
import inspect



#class Monitor(object):
    

#    class MeasureCPUTemp(object):
#	"""
#	This function reads from the CPU temperature from the temp log in 
#	thermal/thermal_zone0/. It returns the temperature in deg C. 
#	"""
#	def __init__(self, thermalfiles = ["/sys/class/thermal/thermal_zone0/temp",] ):
#	    self.thermalfiles = thermalfiles
#	
#	def monitor(self):
#	    t = list()
#	    for tf in self.thermalfiles: 
#		f = open(tf, 'r')
#		t += [float(f.read()) / 1000.0]
#	    return t
#	    
#	def __str__(self):
#	    temp_str = r""
#	    for t in self.monitor():
#		temp_str += r" %s°C "%t
#	    return temp_str
#	    
#    def __init__(self, monitorlogfile, thermal_logfile_list =["/sys/class/thermal/thermal_zone0/temp"] ):
#	self.temp_monitor = Monitor.MeasureCPUTemp(thermal_logfile_list)
#	#self.cpu_temp_conv_fact = 1.0/1000.0
#	self.loadavg_file = "/proc/loadavg"
#	self.monitorlogfile = monitorlogfile
#	self.start_time = datetime.now()
#	self.n_reads = 0
#	
#    def read_load_av(self):
#	"""
#	Reads and returns the load averages from '/proc/loadavg' 
#	"""
#	f = open(self.loadavg_file,'r')
#	line = f.read()
#	line = line.split()
#	return (float(line[0]),float(line[1]),float(line[2]))
#	
#    def monitor(self):
#	self.n_reads += 1
#	temp = self.temp_monitor.monitor()
#	loadav = self.read_load_av()
#	tnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#	f = open(self.monitorlogfile,'a')
#	f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+" {\n")
#	
#	tline = "Temp: "
#	for t in temp:
#	    tline += str(t)+" "
#	tline += "\n"    
#	f.write(tline)
#	
#	laline = "Loadav: "
#	for l in loadav:
#	    laline += str(l)+" "
#	laline += "\n"
#	f.write(laline)
#	
#	f.write("}\n")
	
class MonitorDaemon(Daemon):
    def __init__(self, configfile = "moni.conf"):
        
        self.configfile = configfile
        self.interval = int(parse(self.configfile, "moniinterval"))
        self.data_file = parse(self.configfile,"datafile")
        self.log_path = parse(self.configfile,"logpath")
        self.hold_output = False
        Daemon.__init__(self,'/tmp/py-monitor-daemon.pid',
            stdout=self.log_path+"monitor.log", 
            stderr=self.log_path+"monitor.log"
        )
        print(self.log_path+"/monitor.log")

        self.loadavg_file = '/proc/loadavg'
        self.device_temp_sens = {'zone0':"/sys/class/thermal/thermal_zone0/temp"}
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        self.devices = {
            "outdoor2":"/sys/bus/w1/devices/28-00000574599b/w1_slave",
            "outdoor1":"/sys/bus/w1/devices/28-0000057a2cf4/w1_slave",
            "indoor1":"/sys/bus/w1/devices/28-0000051a9026/w1_slave"
            }
    
#___________________________________________________________________________________________________
    def log(self, msg):
        
        frame,filename,line_number,function_name,lines,index=\
        inspect.getouterframes(inspect.currentframe())[1]
        s = datetime.now().strftime('%Y-%m-%d %H:%M:%S')+" %s:%d in %s :  %s"%(filename,line_number,function_name,msg)
        if(self.hold_output):
            self.log_output += s+"\n"
        else:
            print(s)
#___________________________________________________________________________________________________
    def run(self):
        import pickle
        import os.path

        while(True):
            #print(datetime.now)
            n_exceptions = 0
            notread = True
            while(notread):
                try:
                    r = self.monitor()
                    notread = False
                except:
                    e = sys.exc_info()[0]
                    self.log("Caught an exception: %s"%e)
                    n_exceptions += 1
                    notread = True
                    if(n_exceptions>2):
                        break
                    else:
                        continue
            
            if(not os.path.isfile(self.data_file)):
                f = open(self.data_file,'wb')
            else:
                f = open(self.data_file,'a+b')
            pickle.dump(r,f)
            f.close()
            time.sleep(self.interval)
            
#___________________________________________________________________________________________________
    def monitor(self):
        entry = dict()
        entry['time'] = {'datetime':datetime.now(),'time':time.time()}
        entry['load_av'] = self.read_load_av()
        entry['device_temp'] = self.read_device_temp()
        entry['temp_sens'] = self.read_temperature()
        return entry
#___________________________________________________________________________________________________
    def read_load_av(self):                                                                                                                                                                   
        """                   
        Reads and returns the load averages from '/proc/loadavg'
        """           
        self.log("Reading load av")
        f = open(self.loadavg_file,'r')                                                                                                                                                       
        line = f.read()                                                                                                                                                                       
        line = line.split()                                                                                                                                                                  
        return (float(line[0]),float(line[1]),float(line[2]))      
#___________________________________________________________________________________________________
    def read_device_temp(self):
        self.log("Reading Device Temp")
        t = dict()                                                                                                                                                                         
        for tf in self.device_temp_sens.keys():
            #print(self.device_temp_sens[tf])
            f = open(self.device_temp_sens[tf], 'r') 
            t[tf] = [float(f.read()) / 1000.0] 
        return t
#___________________________________________________________________________________________________
    def read_temperature(self):
        self.log("Reading temperature sensors")
        temps = dict()
        for d in self.devices.keys():
            try:
                f = open(self.devices[d], 'r')
            except:
                self.log("Caught exception wile reading device: %s"%d) 
                continue
            lines = f.readlines()
            f.close()
            while (lines[0].strip()[-3:] != 'YES' ):                                                                                                              
                time.sleep(0.2)
                f = open(self.devices[d], 'r')
                lines = f.readlines()
                f.close()
                
            equals_pos = lines[1].find('t=')                                                                                                                                     
            temps[d] = float(lines[1][equals_pos+2:])/1000                                                                                                        
        return temps

     
#Simple stupid parser....
def parse(file_name, key_word):
    """
    A simple parser that returns the text string value associated
    with the key_word. Can be used for parsing simple configure files.
    
    format is:
    '<key_word>: <value>'
    """
    f = open(file_name)
    for line in f:
        line = line.split(':')
        if(line[0] == key_word):
            el = line[1].split()
            return el[0]
    return None

if __name__ == "__main__":
    from os.path import expanduser
    home = expanduser("~")    
    py_monitor_conf =  os.path.join(home,".py-monitor","moni.conf")
    daemon = MonitorDaemon(py_monitor_conf)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
        
        

