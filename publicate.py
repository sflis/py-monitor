#!/usr/bin/env python                                                                                                                                                                          
## coding: latin-1                                                                                                                                                                             
import os, sys

import sys, time
from daemon.daemon import Daemon
from time import gmtime, strftime
from datetime import datetime



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


   def run(self):
        import pickle
