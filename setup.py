#!/usr/bin/env python
## coding: latin-1
import os, sys

#function to create directory that check if the directory alread have been created.
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def create_dir(f):
    ensure_dir(f)
    print("created directory '%s'"%f)

def main(opt = None): 
    from os.path import expanduser
    home = expanduser("~")    
    py_monitor_data_path =  os.path.join(home,".py-monitor/")
    create_dir(py_monitor_data_path)
    
    f = open((os.path.join(py_monitor_data_path,"moni.conf")),'w')
    if(opt == None):
        f.write("moniinterval:                                 120\n")
        f.write("pubinterval:                                  900\n")
        f.write("datafile:                                     %s\n"%os.path.join(py_monitor_data_path,"moni-data.pkl"))
        f.write("logpath:                                      %s/\n"%py_monitor_data_path)
        f.write("outputpath:                                   /var/www/\n")
    elif(opt == '-d'):
        
        path_here = os.path.dirname(os.path.realpath(__file__))
        create_dir(os.path.join(path_here,"figures/"))
        f.write("moniinterval:                                 120\n")
        f.write("pubinterval:                                  10\n")
        f.write("datafile:                                     %s\n"%os.path.join(path_here,"moni-data.pkl"))
        f.write("logpath:                                      %s/\n"%path_here)
        f.write("outputpath:                                       %s\n"%os.path.join(path_here,"figures/"))
        
if(__name__ == '__main__'):
    narg = len(sys.argv)
    if(narg ==2):
        main(sys.argv[1])
    elif(narg == 1):
        main()
        
