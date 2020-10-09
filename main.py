#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
# from package.logHandler import LogHandler

from MACRO_DEFINE import *

from instr_66319D import handle_instr_66319D
from instr_cmw500 import handle_instr_cmw500

from config_default import config
from config_default import SENSE_PARAM
from adb import adb


if __name__ == '__main__':
    # instr = rm.open_resource("TCPIP0::10.237.70.10::inst0::INSTR")
    try:
        time_start = time.time()
        phone = adb()

        if "ip_cmw500" in config:
            cmw_addr = "TCPIP0::{0}::inst0::INSTR".format(config["ip_cmw500"])
        elif "gpib_cmw500" in config:
            cmw_addr = "GPIB0::{0}::INSTR".format(config["gpib_cmw500"])
        else:
            cmw_addr = handle_instr_cmw500.device_scan(handle_instr_cmw500 )
        if cmw_addr:
            m = handle_instr_cmw500(cmw_addr , phone)
        else:
            m = None
        if m:
            print(m.get_instr_version())

            m.set_remote_display(state=True)

            for i, v in enumerate(config.get('TEST_RF', ())):
                md = standard_map[v]
                m.test_main(md)
                if i+1 < len(config['TEST_RF']) :
                    if config['TEST_RF'][i] != config['TEST_RF'][i+1]:
                        m.LWGT_disconnect_off(md,state_on=False)
            m.instr_rm_close()
    finally:
        time_end = time.time()
        print("time elaped {0}:{1}".format(int(time_end-time_start)//60, int(time_end-time_start)%60))
