#!/usr/bin/env python                                                                                                                                                                          
## coding: latin-1                                                                                                                                                                             
import os, sys

import sys, time
from daemon.daemon import Daemon
from time import gmtime, strftime
from datetime import datetime
from monitor import parse
import pickle
import matplotlib
import matplotlib as mpl
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
class PublicateDaemon(Daemon):
    def __init__(self, configfile = "moni.conf"):


        self.configfile = configfile
        self.interval = int(parse(self.configfile, "moniinterval"))
        self.data_file = parse(self.configfile,"datafile")
        self.log_path = parse(self.configfile,"logpath")
        self.output_path = parse(self.configfile,"outputpath")
        Daemon.__init__(self,'/tmp/py-monitor-publicate-daemon.pid',
            stdout=self.log_path+"publicate.log",
            stderr=self.log_path+"publicate.log"
        )
        mpl.rcParams['legend.fontsize'] = 'medium'
        mpl.rcParams['axes.labelsize']    = 'large'
        mpl.rcParams['xtick.labelsize']  = 'medium'
        mpl.rcParams['ytick.labelsize']  = 'medium'
    def run(self):
        import pickle
        while(True):
            self.publicate()
            time.sleep(self.interval)
    
    def get_data(self):
        f = open(self.data_file,'rb')
        print(self.data_file)
        data = list()
        while 1:
            try:
                data.append(pickle.load(f))
            except:
                break
        time = list()
        temp_indoor = list()
        temp_outdoor = list()
        for d in data:
            time.append(d['time']['datetime'])
            temp_indoor.append(d['temp_sens']['indoor1'])
            temp_outdoor.append(d['temp_sens']['outdoor1'])

    def publicate(self):
       from matplotlib import pyplot as plt
       from matplotlib.dates import date2num
       f = open(self.data_file,'rb')
       print(self.data_file)
       data = list()
       while 1:
           try:
               data.append(pickle.load(f))
           except:
               break
       time = list()
       temp_indoor = list()
       temp_outdoor = list()
       for d in data:
           
           time.append(d['time']['datetime'])
           temp_indoor.append(d['temp_sens']['indoor1'])
           temp_outdoor.append(d['temp_sens']['outdoor1'])
       

       fig = plt.figure(figsize=(20, 10))

       ax = fig.add_subplot(111)
       
       step = 5
       # Plot the data as a red line with round markers
       ax.plot(time[::step],temp_indoor[::step], 'r-o', label='Inomhustemperatur')
       ax.plot(time[::step],temp_outdoor[::step], 'b-o',label='Utomhustemperatur')
       
       # Set the xtick locations to correspond to just the dates you entered.
       tick_steps = 720
       ax.set_xticks(time[277::tick_steps])
       
       # Set the xtick labels to correspond to just the dates you entered.
       ax.set_xticklabels(
           [date.strftime("%Y-%m-%d") for date in time[277::tick_steps]]
        )

       ax.set_ylim( -10, 25 )
       ax.legend(loc='best')
       
       #setting grid
       ax.yaxis.grid(True)
       ax.xaxis.grid(True)
       
       #setting axis labels
       ax.set_xlabel("Tid", fontsize = 45)
       ax.set_ylabel("Temperatur C$^\circ$", fontsize = 45)
       
       #save image
       fig.savefig( self.output_path+'/temperature.png', dpi=300 )
       f = open("/var/www/temperature.html",'w')


       f.write("<b>%s: %03.2fC&deg</b> <br>"%('indoor1', temp_indoor[-1]))
       f.write("<b>%s: %03.2fC&deg</b> <br>\n"%('outdoor1', temp_outdoor[-1]))

if __name__ == "__main__":
        daemon = PublicateDaemon()
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
