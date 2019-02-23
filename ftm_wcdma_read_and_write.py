#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyperclip
#复制内容到剪贴板
#pyperclip.copy("hello world")

import sys, os, visa, threading, time, string
from datetime import datetime
from config_default import config
from instr_cmw500 import handle_instr_cmw500

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

        if cmw_addr:
            m = handle_instr_cmw500(cmw_addr)
        else:
            m = None
        if m:
            print(m.get_instr_version())
            m.set_remote_display(state=True)

            while True:
                # res = m.instr_query("FETCh:WCDMa:MEAS:MEValuation:SPECtrum:AVERage? RELative",delay =2).strip().split(",")
                m.instr_write("INITiate:WCDMa:MEAS:MEValuation")
                while m.instr_query("FETCh:WCDMa:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
                    time.sleep(1)
                res = m.instr_query("FETCh:WCDMa:MEAS:MEValuation:SPECtrum:AVERage? RELative").strip().split(",")

                res = tuple(round(float(res[i]),2) for i in [2,3,15,4,5] )
                res_str = "\t".join([str(i) for i in res])
                pyperclip.copy(res_str)
                x = input("press Enter to continue")
                if x != "":
                    break

            m.instr_rm_close()
    finally:
        time_end = time.time()
        print("time elaped {0}:{1}".format(int(time_end-time_start)//60, int(time_end-time_start)%60))
