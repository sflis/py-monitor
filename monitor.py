#!/usr/bin/env python
## coding: latin-1
import os, sys

import sys, time
from daemon import Daemon
from time import gmtime, strftime
from datetime import datetime




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
    def __init__(self, configfile = "/home/sflis/scripts/Monitor/moni.conf"):
	Daemon.__init__(self,'/tmp/py-monitor-daemon.pid')
	self.configfile = configfile
	self.monitorlogfile = parse(self.configfile, "monilogfile") 
	self.interval = int(parse(self.configfile, "moniinterval"))
	self.monitor = Monitor(self.monitorlogfile)
	
        self.loadavg_file = '/proc/loadavg'
        self.device_temp_sens = {'zone0':"/sys/class/thermal/thermal_zone0/temp"}
    def run(self):
        import os.path
os.path.isfile(fname)
	while(True):
	    self.monitor.monitor()
	    time.sleep(self.interval)

    
    def monitor(self):
        
    def read_load_av(self):                                                                                                                                                                   
        """                   
        Reads and returns the load averages from '/proc/loadavg'
        """                                                                                                                                                                                   
        f = open(self.loadavg_file,'r')                                                                                                                                                       
        line = f.read()                                                                                                                                                                       
        line = line.split()                                                                                                                                                                  
        return (float(line[0]),float(line[1]),float(line[2]))      
	
    def read_device_temp(self):
        t = dict()                                                                                                                                                                         
        for tf in self.device_temp_sens.keys():
            f = open(device_temp_sens.keys[tf], 'r') 
            t[tf] = [float(f.read()) / 1000.0] 
        return t

     
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
	daemon = MonitorDaemon()
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
		
		

