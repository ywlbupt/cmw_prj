#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyperclip
#复制内容到剪贴板
#pyperclip.copy("hello world")

import sys, os, visa, threading, time, string
from datetime import datetime
from config_default import config
from main import handle_instr_cmw500

# from package.logHandler import LogHandler
# import logging
#logger = LogHandler("", level = logging.INFO)

# logger.info("tetst")



if __name__ == '__main__':
    try:
        time_start = time.time()
        if "ip_cmw500" in config:
            cmw_addr = "TCPIP0::{0}::inst0::INSTR".format(config["ip_cmw500"])
        else:
            cmw_addr = "GPIB0::{0}::INSTR".format(config["gpib_cmw500"])
            # cmw_addr = device_scan(handle_instr_cmw500, "gpib_cmw500")
        # print( device_scan(handle_instr_66319D, "gpib_addr_66319D"))

        if cmw_addr:
            m = handle_instr_cmw500(cmw_addr)
        else:
            m = None
        if m:
            print(m.get_instr_version())
            m.set_remote_display(state=True)
            # READ:LTE:MEAS<i>:MEValuation:TRACe:ACLR:AVERage?
            while True:
                res = m.instr_query("READ:LTE:MEAS:MEValuation:ACLR:AVERage?").strip().split(",")
                res = tuple(round(float(res[i]),2) for i in [2,3,4,5,6] )
                res_str = "\t".join([str(i) for i in res])
                pyperclip.copy(res_str)
                x = input("press Enter to continue")
                if x != "":
                    break

            m.instr_rm_close()
    finally:
        time_end = time.time()
        print("time elaped {0}:{1}".format(int(time_end-time_start)//60, int(time_end-time_start)%60))
