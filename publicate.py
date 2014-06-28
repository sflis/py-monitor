#!/usr/bin/env python                                                                                                                                                                         
## coding: latin-1  
import os, sys

import sys, time
from daemon.daemon import Daemon
from time import gmtime, strftime
from datetime import datetime
import datetime as dt
from monitor import parse
import pickle
import matplotlib as mpl

# Force matplotlib to not use any Xwindows backend.
mpl.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
class PublicateDaemon(Daemon):
    def __init__(self, configfile = "moni.conf"):


        self.configfile = configfile
        self.interval = int(parse(self.configfile, "pubinterval"))
        self.data_file = parse(self.configfile,"datafile")
        self.log_path = parse(self.configfile,"logpath")
        self.output_path = parse(self.configfile,"outputpath")
        self.data = dict()
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
            #self.publicate()
            self.read_data()
            self.default_temp_plot()
            self.publicate_current_temp()
            self.free_data()
            sys.stdout.flush()
            time.sleep(self.interval)
    
    def read_data(self):
        print("Reading monitoring data")
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
        self.data['time'] = time
        self.data['temp_indoor1'] = temp_indoor
        self.data['temp_outdoor1'] = temp_outdoor
    
    def free_data(self):
        for k in self.data.keys():
           del self.data[k]
    
    def default_temp_plot(self):
        temp_indoor = self.data['temp_indoor1']
        temp_outdoor = self.data['temp_outdoor1']
        time = self.data['time']
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)
        
        step = 5
        # Plot the data
        ax.plot(time[::step],temp_indoor[::step], 'r-', label='Inomhustemperatur')
        ax.plot(time[::step],temp_outdoor[::step], 'b-',label='Utomhustemperatur')

        # Set the xtick locations.
        tick_steps = 720/2
        ax.set_xticks(time[277::tick_steps])
        st = time[0]
        st += dt.timedelta(hours=24-st.hour,minutes = -st.minute,seconds = -st.second)
        # Set the xtick labels.
        xticks = list()
        delta  = time[-1]-st
        end = int((delta.days+1) * 24 )
        print(end)
        print(delta)
        print(time[-1])
        for t in range(0,end,12):
            xticks.append(st + dt.timedelta(hours=t))
            print(st + dt.timedelta(hours=t),t)
        ax.set_xticklabels(
            [date.strftime("%m-%d %H:%M") for date in xticks]
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
        del ax
        del fig
    def publicate_current_temp(self):
        f = open("/var/www/temperature.html",'w')
        
        f.write("<b>%s: %03.2fC&deg</b> <br>"%('Inomhus', self.data['temp_indoor1'][-1]))
        f.write("<b>%s: %03.2fC&deg</b> <br>"%('Utomhus', self.data['temp_outdoor1'][-1]))

    def publicate(self):
        pass

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
