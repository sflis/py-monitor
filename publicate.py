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
import inspect
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
        self.image_output_path = parse(self.configfile,"image_outputpath")
        self.data = dict()
        self.hold_output = False
        self.fig = plt.figure(figsize=(20, 10))
        self.ax = self.fig.add_subplot(111)
        Daemon.__init__(self,'/tmp/py-monitor-publicate-daemon.pid',
            stdout=self.log_path+"publicate.log",
            stderr=self.log_path+"publicate.log"
        )
        mpl.rcParams['legend.fontsize']  = 'medium'
        mpl.rcParams['axes.labelsize']   = 'large'
        mpl.rcParams['xtick.labelsize']  = 'medium'
        mpl.rcParams['ytick.labelsize']  = 'medium'
        
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
        while(True):
            self.read_data()
            self.default_temp_plot()
            self.publicate_current_temp()
            self.free_data()
            sys.stdout.flush()
            time.sleep(self.interval)
#___________________________________________________________________________________________________
    def read_data(self):
        self.log("Reading monitoring data")
        f = open(self.data_file,'rb')
        #print(self.data_file)
        data = list()
        while 1:
            try:
                data.append(pickle.load(f))
            except:
                break
        time = list()
        #temp_indoor = list()
        #temp_outdoor = list()
        temp_indoor2 = {'time':list(),'temp':list()}
        temp_outdoor2 = {'time':list(),'temp':list()}
        
        for d in data:
            time.append(d['time']['datetime'])
            #temp_indoor.append(d['temp_sens']['indoor1'])
            #temp_outdoor.append(d['temp_sens']['outdoor1'])
            if('indoor1' in d['temp_sens'].keys()):

                #print('indoor1: %f'%d['temp_sens']['indoor1'])
                temp_indoor2['time'].append(d['time']['datetime'])
                temp_indoor2['temp'].append(d['temp_sens']['indoor1'])

            if('outdoor1' in d['temp_sens'].keys()):
                temp_outdoor2['time'].append(d['time']['datetime'])
                temp_outdoor2['temp'].append(d['temp_sens']['outdoor1'])
        self.data['time'] = time
        #self.data['temp_indoor1'] = temp_indoor
        #self.data['temp_outdoor1'] = temp_outdoor
        self.data['temp_outdoor2'] = temp_outdoor2
        self.data['temp_indoor2'] = temp_indoor2
#___________________________________________________________________________________________________
    def free_data(self):
        for k in self.data.keys():
           del self.data[k]
#___________________________________________________________________________________________________
    def default_temp_plot(self):
        self.log("Generating temperature plot")
        temp_indoor = self.data['temp_indoor2']['temp']
        temp_outdoor = self.data['temp_outdoor2']['temp']
        time = self.data['temp_indoor2']['time']
        
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)
        
        step = 5
        # Plot the data
        ax.plot(time[::step],  temp_indoor[::step], 'or-', label='Inomhustemperatur')
        time = self.data['temp_outdoor2']['time']
        ax.plot(time[::step], temp_outdoor[::step], 'ob-', label='Utomhustemperatur')
        time = self.data['time']
        # Define xtick locations and labels.
        st = time[0]
        #st += dt.timedelta(hours=24-st.hour,minutes = -st.minute,seconds = -st.second)
        xticks = list()
        delta  = time[-1]-st
        end = int((delta.days+1) * 24 )
        for t in range(0,end,2):
            xticks.append(st + dt.timedelta(hours=t))
            print(st + dt.timedelta(hours=t),t)
        # Set xtick locations.
        ax.set_xticks(xticks)
        # Set xticklables.
        ax.set_xticklabels(
            [date.strftime(" %H:%M") for date in xticks]#"%m-%d %H:%M"
            )

        ax.set_ylim( -5, 30 )
        ax.set_xlim(time[0],time[-1])
        ax.legend(loc='best')

        #setting grid
        ax.yaxis.grid(True)
        ax.xaxis.grid(True)

        #setting axis labels
        ax.set_xlabel("Tid", fontsize = 45)
        ax.set_ylabel("Temperatur C$^\circ$", fontsize = 45)

        #save image 
        fig.savefig( self.image_output_path+'/temperature.png', dpi=300 )
        #Important to close the figure so that the memory is released.
        plt.close()
#___________________________________________________________________________________________________
    def publicate_current_temp(self):
        self.log("Writing html file.")
        f = open(self.output_path+"/temperature.html",'w')
        
        f.write("<b>%s: %03.2fC&deg</b> <br>"%('Inomhus', self.data['temp_indoor2']['temp'][-1]))
        if(len(self.data['temp_outdoor2']['temp'])>1):
            f.write("<b>%s: %03.2fC&deg</b> <br>"%('Utomhus', self.data['temp_outdoor2']['temp'][-1]))

if __name__ == "__main__":
        from os.path import expanduser
        home = expanduser("~")    
        py_monitor_conf=  os.path.join(home,".py-monitor","moni.conf")
        daemon = PublicateDaemon(py_monitor_conf)
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
