#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")

from instr import handle_instr
# from instr import device_scan
import re
import time

class handle_instr_cmw500_common(handle_instr):
    instr_name_p = re.compile (r"Rohde&Schwarz.*CMW.*")

    def __init__(self, instr_socall_addr):
        super().__init__(instr_socall_addr)
        pass

    def instr_reset_cmw(self):
        self.instr_write("*RST;*OPC")
        self.instr_write("*CLS;*OPC?")
        print("instr reset.......")
        time.sleep(4)

    def set_remote_display(self, state=True):
        '''
        state : True or False
        '''
        if state:
            self.instr_write("SYSTem:DISPlay:UPDate ON")
        else:
            self.instr_write("SYSTem:DISPlay:UPDate OFF")

    def set_FDCorrection(self,loss_array):
        OUTPUT_EAT, INPUT_EAT, loss_matrix = loss_array
        self.instr_write("CONFigure:BASE:FDCorrection:CTABle:DELete:ALL")
        if loss_matrix :
            self.instr_write("CONFigure:BASE:FDCorrection:CTABle:CREate 'CMW_loss', {loss_matrix}".format(loss_matrix=loss_matrix))
            self.instr_write ("CONFigure:FDCorrection:ACTivate RF1C, 'CMW_loss', RXTX, RF1")
            self.instr_write ("CONFigure:FDCorrection:ACTivate RF1O, 'CMW_loss', RXTX, RF1")

    def get_cmw_soft_version(self, md=None):
        if md:
            version_name_p = re.compile(r"CMW_{md}_Sig,V(\d+)\.(\d+)\.(\d+)".format(md = md))
        else:
            version_name_p = None
        version_list= self.instr_query("SYSTem:BASE:OPTion:VERSion?",delay = 1).split(";")
        if md:
            for ver in version_list:
                if version_name_p:
                    ver_m = version_name_p.match(ver)
                    if ver_m:
                        return [ int(i) for i in (ver_m.group(1), ver_m.group(2), ver_m.group(3)) ]
        else:
            return version_list

class handle_instr_cmw500_ftm(handle_instr_cmw500_common):
    
    def get_aclr_ftm(self, md):
        def wcdma_get_aclr_ftm():
            self.instr_write("CONFigure:WCDMa:MEAS:MEValuation:REPetition SINGleshot")
            self.instr_write("INITiate:WCDMa:MEAS:MEValuation")
            while self.instr_query("FETCh:WCDMa:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
                time.sleep(1)
            res = self.instr_query("FETCh:WCDMa:MEAS:MEValuation:SPECtrum:AVERage? RELative").strip().split(",")
            res = tuple(round(float(res[i]),2) for i in [2,3,15,4,5] )
            return res
        def lte_get_aclr_ftm():
            self.instr_write ("CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")
            self.instr_write("INITiate:LTE:MEAS:MEValuation")
            while self.instr_query("FETCh:LTE:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
                time.sleep(1)
            res = self.instr_query("FETCh:LTE:MEAS:MEValuation:ACLR:AVERage?").strip().split(",")
            res = tuple(round(float(res[i]),2) for i in [2,3,4,5,6] )
            # self.instr_write("ABORt:LTE:MEAS:MEValuation")
            return res
        if md == "WCDMA":
            return wcdma_get_aclr_ftm()
        elif md == "LTE":
            return lte_get_aclr_ftm()

    def ftm_set_ch(self, _r_param):
        self.instr_write('CONFigure:{0}:MEAS:RFSettings:FREQuency {1}CH'.format(_r_param['md'],_r_param['ch']))
        pass

    # def ftm_setting_of_lte(self, band_num, ch_num, bw_num):
    def cmw_ftm_set(self, _r_param):
        band_num = _r_param["band"]
        ch_num = _r_param["ch"]
        bw_num = _r_param["bw"] # bw : int num 10
        if _r_param["md"] == "LTE":
            test_dd = "FDD" if int(band_num)<33 else "TDD"
            self.instr_write("ROUTe:LTE:MEAS:SCENario:SALone RF1C, RX1")
            self.instr_write("CONFigure:LTE:MEAS:DMODe {dd}".format(dd = test_dd))
            self.instr_write("CONFigure:LTE:MEAS:BAND OB{0}".format(band_num))
            self.instr_write('CONFigure:LTE:MEAS:RFSettings:FREQuency {0}CH'.format(ch_num))
            self.instr_write("CONFigure:LTE:MEAS:PCC:CBANdwidth {0}".format("B"+str(int(bw_num)*10).zfill(3)))
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MSUBframes 0, 10, {0}".format(0 if test_dd=="FDD" else 2))
            self.instr_write("TRIGger:LTE:MEAS:MEValuation:SOURce 'Free Run (Fast Sync)'")
            self.instr_write("CONFigure:LTE:MEAS:RFSettings:ENPMode MANual")
            self.instr_write("CONFigure:LTE:MEAS:RFSettings:ENPower 24")
            self.instr_write("CONFigure:LTE:MEAS:RFSettings:UMARgin 12")
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MOEXception ON")
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")
        elif _r_param["md"] == "WCDMA":
            PMwrite("ROUTe:WCDMa:MEAS:SCENario:SALone RF1C, RX1")
            PMwrite("CONFigure:WCDMa:MEAS:BAND OB{0}".format(band_num))
            PMwrite("CONFigure:WCDMa:MEAS:RFSettings:FREQuency {0} CH".format(ch_num))
            PMwrite("CONFigure:WCDMa:MEAS:MEValuation:MOEXception ON")
            PMwrite("TRIGger:WCDMa:MEAS:MEValuation:SOURce 'Free Run (Fast Sync)'")
            PMwrite("CONFigure:WCDMA:MEAS:RFSettings:ENPower 24")
            PMwrite("CONFigure:WCDMA:MEAS:RFSettings:UMARgin 12") 
            PMwrite("CONFigure:WCDMa:MEAS:MEValuation:SCOunt:MODulation 10")
            PMwrite("CONFigure:WCDMa:MEAS:MEValuation:SCOunt:SPECtrum 10")
            PMwrite("CONFigure:WCDMa:MEAS:MEValuation:REPetition SINGleshot")
            pass
        

def Initial_run(gpib_addr = None):
        cmw_addr = handle_instr_cmw500_ftm.device_scan(gpib_addr)
        hd_cmw = handle_instr_cmw500_ftm(cmw_addr)
        return hd_cmw

if __name__ == "__main__":
    # cmw_addr = "TCPIP0::{0}::inst0::INSTR".format(config["ip_cmw500"])
    time_start = time.time()
    cmw_addr = handle_instr_cmw500_ftm.device_scan(20)
    m = handle_instr_cmw500_ftm(cmw_addr)
    try:
        if m:
            m.set_remote_display(state=True)
            m.ftm_setting_of_lte(band_num=1, ch_num = 18550, bw_num = 10)
            # m.lte_get_aclr_ftm()
            # print(m.get_instr_version())
            m.instr_rm_close()
    finally:
        time_end = time.time()
        print("time elaped {0}:{1}".format(int(time_end-time_start)//60, int(time_end-time_start)%60))
