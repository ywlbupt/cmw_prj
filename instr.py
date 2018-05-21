#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, visa, threading, time, string
from datetime import datetime

# instr 为 visa.ResourceManger() Type
# if "dev_ip" in config:
    # m = handle_instr_cmw500("TCPIP0::{0}::inst0::INSTR".format(config["dev_ip"]))
# elif "gpib" in config:
    # m = handle_instr_cmw500("GPIB0::{0}::INSTR"".format(config["gpib"]))

class handle_instr():
    def __init__(self, instr_socall_addr, phone_hd=None):
        self.rm = visa.ResourceManager()
        self.instr=self.rm.open_resource(instr_socall_addr)
        self.phone_hd=phone_hd

    def instr_write(self, *args, **kwargs):
        try:
            self.instr.write(*args, **kwargs)
        except:
            print("write error ",args)
            time.sleep(4)
            self.instr.write(*args, **kwargs)

    def instr_query(self, *args, **kwargs):
        try:
            m = self.instr.query(*args,**kwargs)
        # return self.instr.query(cmd)
        except:
            print("query error {0}",args)
            time.sleep(4)
            m = self.instr.query(*args,**kwargs)
        return m

    def instr_close(self):
        self.instr.close()
        self.rm.close()
