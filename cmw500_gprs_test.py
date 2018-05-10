#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyperclip
import sys, os, visa, threading, time, string
from datetime import datetime
from config_default import config
from test import handle_instr
from test import RM_CMW

param_FDCorrection="699000000, 0.6, 960000000, 0.6, 1710000000, 1.0,2170000000, 1.0, 2300000000, 1.2, 2535000000, 1.2, 2700000000, 1.2"

#复制内容到剪贴板
#pyperclip.copy("hello world")
#res = m.instr_query("READ:LTE:MEAS:MEValuation:ACLR:AVERage?").strip().split(",")
class handle_instr_GPRS(handle_instr):
    
    def GPRS_para_configure(self):
        # *****************************************************************************
        # Enable the "Packet Switched Domain" and disable dual carrier mode.
        # *****************************************************************************
        self.instr_write("CONFigure:GSM:SIGN:CELL:PSDomain ON")
        self.instr_write("CONFigure:GSM:SIGN:CONNection:PSWitched:DLDCarrier:ENABle OFF")
        # Set Packet Switched Test Mode A
        self.instr_write("CONFigure:GSM:SIGN:CONNection:PSWitched:SERVice TMA")
        # Select GPRS as transmission scheme
        self.instr_write("CONFigure:GSM:SIGN:CONNection:PSWitched:TLEVel GPRS")
        # select CS-1 as UL coding Scheme
        self.instr_write("CONFigure:GSM:SIGN:CONNection:PSWitched:CSCHeme:UL C1")
        # Configure the power in all uplink and downlink slots
        self.instr_write("CONF:GSM:SIGN:CONN:PSWitched:SCONfig:GAMMa:UL 13,13,3,3,3,3,13,13")


        pass

    def GPRS_check_connection(self):
        # res_cs = self.instr_query("FETCh:GSM:SIGN:CSWitched:STATe?").strip()
        res_ps = self.instr_query("FETCh:GSM:SIGN:PSWitched:STATe?").strip()
        if res_ps == "TBF":
            return True
        else:
            return False

    def GPRS_Connect(self):
        md = "GPRS"
        print("{md} connect begin".format(md = md))
        for j in range(3):
            for i in range(30):
                res_ps = self.instr_query("FETCh:GSM:SIGN:PSWitched:STATe?").strip()
                print("\r{0:<5} ".format(res_ps),end="")
                print("Connecting phone, {0}".format(i),end="")
                if res_ps == "ATT":
                    self.instr_write("CALL:GSM:SIGN:PSWitched:ACTion CONNect")
                elif res_ps == "TBF":
                    break
                time.sleep(2)
            # if not self.LWGT_check_connection(md) and j != 2:
            if self.GPRS_check_connection():
                break


if __name__ == '__main__':
    try:
        time_start = time.time()
        rm = RM_CMW()
        if "dev_ip" in config:
            m = handle_instr_GPRS(rm.open_resource("TCPIP0::{0}::inst0::INSTR".format(config["dev_ip"])))
        elif "gpib" in config:
            m = handle_instr_GPRS(rm.open_resource("GPIB0::{0}::INSTR".format(config["gpib"])))
        else:
            m = None
        if m:
            print(m.get_instr_version())
            m.set_remote_display(state=True)
            m.set_FDCorrection(param_FDCorrection)
            if not m.GPRS_check_connection():
                m.GPRS_Connect()

            m.instr_write("ROUTe:GSM:MEAS:SCENario:CSPath 'GSM Sig1'")
            m.instr_write("CONFigure:GSM:MEAS:MEValuation:REPetition SINGleshot")
            while True:
                if not m.GPRS_check_connection():
                    m.GPRS_Connect()
                m.instr_write("INITiate:GSM:MEAS:MEValuation")
                while m.instr_query("FETCh:GSM:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
                    time.sleep(1)
                res = m.instr_query("FETCh:GSM:MEAS:MEValuation:PVTime:ALL?").strip().split(",")
                res = tuple(round(float(res[i]),2) for i in [4,5,6,7] )
                print(res)
                if sum([(i>28 and i<23) for i in res]):
                    break
                time.sleep(5)
                # x = input("press Enter to continue")
                # if x != "":
                    # break

            m.instr_close()
        rm.close()
    finally:
        time_end = time.time()
        print("time elaped {0}:{1}".format(int(time_end-time_start)//60, int(time_end-time_start)%60))

#  m.query("FETCh:GSM:MEAS:MEValuation:PVTime:ALL?")
