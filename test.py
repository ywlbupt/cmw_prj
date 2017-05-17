#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, visa, threading, time, string
from band_def import TEST_LIST
from band_def import TEST_LIST_W
from band_def import str_ue_info
from MACRO_DEFINE import *
from adb import adb

#import msvcrt

#PM = visa.instrument("TCPIP0::192.168.0.1::inst0::INSTR")
#PM = visa.instrument("GPIB1::20::INSTR")

param_FDCorrection="1920000000, 1.0, 1980000000, 1.0, 2110000000, 1.0, 2170000000, 1.0, 1850000000, 1.0,1910000000, 1.0, 1930000000, 1.0, 1990000000, 1.0, 824000000, 0.6, 849000000, 0.6, 869000000, 0.6, 894000000, 0.6, 925000000, 0.6, 960000000, 0.6, 880000000, 0.6, 915000000, 0.6, 2350000000, 1.2, 2535000000, 1.2, 2700000000, 1.2"

f = r"./test_data.txt"

class RM_cmw(visa.ResourceManager):
    pass

class handle_instr():
    def __init__(self, instr, phone_hd=None):
        self.instr=instr
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

    def instr_reset_cmw(self):
        self.instr_write("*RST;*OPC")
        self.instr_write("*CLS;*OPC?")
        # preset instr
        self.instr_write("SYSTem:PRESet:ALL;*OPC")
        # self.instr_write("SYSTem:PRESet:ALL")
        time.sleep(5)

    def instr_close(self):
        self.instr.close()

    def get_instr_version(self):
        return self.instr_query("*IDN?",delay = 5).strip()

    def set_remote_display(self, state=True):
        if state:
            self.instr_write("SYSTem:DISPlay:UPDate ON")
        else:
            self.instr_write("SYSTem:DISPlay:UPDate OFF")

    def set_FDCorrection(self,loss_matrix):
        lossName = self.instr_query ("CONFigure:BASE:FDCorrection:CTABle:CATalog?")
        # if lossName.find ("CMW_loss") != -1:
            # self.instr_write ("CONFigure:BASE:FDCorrection:CTABle:DELete 'CMW_loss'")
        self.instr_write("CONFigure:BASE:FDCorrection:CTABle:CREate 'CMW_loss', {loss_matrix}".format(loss_matrix=loss_matrix))
        self.instr_write ("CONFigure:FDCorrection:ACTivate RF1C, 'CMW_loss', RXTX, RF1")
        self.instr_write ("CONFigure:FDCorrection:ACTivate RF1O, 'CMW_loss', RXTX, RF1")

    def LTE_para_configure(self,test_list):
        if self.LW_check_connection(md="LTE"):
            self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
            self.LTE_ch_redirection(test_list[0])
            pass
        else:
            self.instr_reset_cmw()
            self.instr_write ("SOURce:LTE:SIGN:CELL:STATe OFF")
            test_DD = "FDD" if int(test_list[0].BAND[2:])<33 else "TDD"
            self.instr_write ("CONFigure:LTE:SIGN:DMODe {DD}".format(DD=test_DD))
            self.instr_write ("CONFigure:LTE:SIGN:PCC:BAND {band}".format(band=test_list[0].BAND))
            self.instr_write ("CONFigure:LTE:SIGN:RFSettings:CHANnel:UL {0}".format(test_list[0].CH_UL))
        # elif state =="Connected":
        # 最大功率
        self.instr_write ("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
        self.instr_write ("SOURce:LTE:SIGN:CELL:STATe ON")

        while self.instr_query("SOURce:LTE:SIGN:CELL:STATe:ALL?").strip() != "ON,ADJ":
            print("LTE state ONing")
            time.sleep(1)
        return 

    def LW_check_connection(self, md = "LTE"):
        if md == "LTE":
            str_query = "FETCh:LTE:SIGN:PSWitched:STATe?"
        elif md == "WCDMA":
            str_query = "FETCh:WCDMa:SIGN:CSWitched:STATe?"
        str_state_conn = "CEST"

        if self.instr_query(str_query,delay=2).strip() == str_state_conn:
            return True
        else:
            return False

    def LW_connect(self,md="LTE", phone_reset=False, instr_reset=False):
        if instr_reset:
            self.instr_reset_cmw()
            self.set_FDCorrection(param_FDCorrection)
        if self.phone_hd and phone_reset:
            self.phone_hd.reboot()
        if md == "LTE":
            str_call = "CALL:LTE:SIGN:PSWitched:ACTion CONNect"
            str_query = "FETCh:LTE:SIGN:PSWitched:STATe?"
            str_state_conn = "CEST"
        elif md == "WCDMA":
            str_call = "CALL:WCDMa:SIGN:CSWitched:ACTion CONNect"
            str_query = "FETCh:WCDMa:SIGN:CSWitched:STATe?"
            str_state_conn = "CEST"
        print("{md} connect begin".format(md = md))
        for j in range(2):
            for i in range(50):
                if md == "LTE":
                    self.instr_write(str_call)
                    res_state = self.instr_query(str_query,delay=1).strip()
                elif md == "WCDMA":
                    res_state = self.instr_query(str_query,delay=1).strip()
                    if res_state == "REG":
                        self.instr_write(str_call)

                if res_state != str_state_conn:
                    print("\r{0:<5} ".format(res_state),end="")
                    print("Connecting phone, {0}".format(i),end="")
                else:
                    break
            print("")
            if res_state != "CEST" and j == 0:
                print("phone reboot")
                self.phone_hd.adb_reboot()
                time.sleep(50)
                # while self.phone_hd.get_device_series() is not None:
                    # print("\rWaiting phone reboot", end="")
                    # time.sleep(2)
            else:
                break
        if res_state == str_state_conn:
            print("Connection Established!")
        else:
            print("Conecting failed")
        return 0

    def LTE_ch_redirection(self, dest_state):
        last_state = self.LTE_get_state()
        dest_DD = "FDD" if int(dest_state.BAND[2:])<33 else "TDD"
        last_DD = "FDD" if int(last_state.BAND[2:])<33 else "TDD"

        if dest_DD == last_DD:
            if dest_state.BAND == last_state.BAND:
                switch_mode = "redirection"
            else:
                switch_mode = "Handover"
        else:
            switch_mode = "ENHandover"
        print(last_state)
        print("Try {sw} to band {st.BAND}, channel {st.CH_UL}, bw {st.BW}".format(sw=switch_mode,st=dest_state))
        if switch_mode == "redirection":
            self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
            # band_str = "CONFigure:LTE:SIGN:PCC:BAND {0}".format(dest_state.BAND)
            ch_str = "CONFigure:LTE:SIGN:RFSettings:CHANnel:UL {0}".format(dest_state.CH_UL)
            bw_str = "CONFigure:LTE:SIGN:CELL:BANDwidth:DL {0}".format(dest_state.BW)
            str_list = []
            if dest_state.BW <= last_state.BW:
                str_list+=[bw_str, ch_str]
            else:
                str_list+=[ch_str, bw_str]
            for cmd in str_list:
                self.instr_write(cmd)
                time.sleep(2)
        elif switch_mode == "Handover":
            self.instr_write("PREPare:LTE:SIGN:HANDover:DESTination 'LTE Sig1'")
            self.instr_write("PREPare:LTE:SIGN:HANDover:MMODe HANDover")
            self.instr_write("PREPare:LTE:SIGN:HANDover:ENHanced {md}, {st.BAND}, {st.CH_DL}, {st.BW}, NS01".format(md=dest_DD, st=dest_state))
            # self.instr_write("PREPare:LTE:SIGN:HANDover: {st.BAND}, {st.CH_DL}, {st.BW}, NS01".format(st=dest_state))
            self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion HANDover")
            time.sleep(3)
        elif switch_mode == "ENHandover":
            # check RRC_STATE 
            self.instr_write("PREPare:LTE:SIGN:HANDover:DESTination 'LTE Sig1'")
            # self.instr_write("PREPare:LTE:SIGN:HANDover:MMODe HANDover")
            self.instr_write("PREPare:LTE:SIGN:HANDover:ENHanced {md}, {st.BAND}, {st.CH_DL}, {st.BW}, NS01".format(md=dest_DD, st=dest_state))
            self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion HANDover")
            time.sleep(5)
        present_state = self.LTE_get_state()
        if present_state == dest_state:
            print("{0} sucessful".format(switch_mode))
        else:
            print("{0} faild".format(switch_mode))
        pass

    def LTE_ch_travel(self, test_list, mea_item =("aclr",) ):
        self.instr_write ("ROUTe:LTE:MEAS:SCENario:CSPath 'LTE Sig1'")
        self.instr_write ("CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")
        # mea_item=("aclr",)
        total_res = {}
        for item in mea_item:
            total_res[item]=[]
        try:
            for dest_state in test_list:
                self.LTE_ch_redirection(dest_state)
                dest_DD = "FDD" if int(dest_state.BAND[2:])<33 else "TDD"
                temp = self.LTE_acquire_Meas(mea_item=mea_item,test_DD = dest_DD)
                for item in mea_item:
                    total_res[item].append(dest_state+temp[item])
                print("")
        finally:
            self.LTE_data_output(total_res,f)
            print(total_res)
        pass

    def LTE_acquire_Meas(self, mea_item = None, test_DD="FDD"):
        if test_DD == "FDD":
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MSUBframes 0,10,0")
        else:
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MSUBframes 2,10,0")
        time.sleep(2)
        output_res = {}
        if not mea_item:
            mea_item = ("aclr",)
        if self.LW_check_connection(md="LTE"):
            self.instr_write("INITiate:LTE:MEAS:MEValuation")
            while self.instr_query("FETCh:LTE:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
                # print (self.instr_query("FETCh:LTE:MEAS:MEValuation:STATe:ALL?"))
                time.sleep(1)
            # ACLR acquire
            if "aclr" in mea_item:
                output_res["aclr"]=self.LTE_meas_aclr()
            if "sensm" in mea_item:
                output_res["sensm"]=self.LTE_meas_sense(route_path="main")
            if "sensd" in mea_item:
                output_res["sensd"]=self.LTE_meas_sense(route_path="div")
        else:
            print("Not connected")
        return output_res

    def LTE_meas_aclr(self):
        self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
        self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
        time.sleep(1)
        res = self.LTE_data_dealing(self.instr_query ("READ:LTE:MEAS:MEValuation:ACLR:AVERage?"), data_type="aclr")
        print(res)
        return res

    def LTE_sens_param(self,down_level, frame=1000, output_pwr_format="RS_EPRE"):
        self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel {0}".format(down_level))
        self.instr_write("CONFigure:LTE:SIGN:EBLer:SFRames {frame}".format(frame=frame))
        self.instr_write("INITiate:LTE:SIGN:EBLer")
        while self.instr_query("FETCh:LTE:SIGN:EBL:STATe:ALL?").strip() != "RDY,ADJ,INV":
            # print (self.instr_query("FETCh:LTE:SIGN:EBL:STATe:ALL?"))
            time.sleep(1)
        res = self.LTE_data_dealing(self.instr_query("FETCh:LTE:SIGN:EBLer:RELative?"),data_type="bler")
        if output_pwr_format=="RS_EPRE":
            return down_level, res["Throughput"]
        elif output_pwr_format=="cell_power":
            cell_pwr = round(float(self.instr_query("SENSe:LTE:SIGN:DL:FCPower?")),2)
            return cell_pwr, res["Throughput"]
        else: 
            return None

    def LTE_get_RSRP(self):
        self.instr_write("CONFigure:LTE:SIGN:UEReport:ENABle ON")
        time.sleep(1)
        RSRP = self.instr_query("SENSe:LTE:SIGN:UEReport:RSRP:RANGe?").strip().split(",")
        # RSRP = list(map(int,RSRP))
        # self.instr_write("CONFigure:LTE:SIGN:UEReport:ENABle OFF")
        return RSRP

    def LTE_get_state(self):
        band = self.instr_query("CONFigure:LTE:SIGN:PCC:BAND?").strip()
        ch_ul = self.instr_query("CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:UL?").strip()
        ch_dl = self.instr_query("CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:DL?").strip()
        bw = self.instr_query("CONFigure:LTE:SIGN:CELL:BANDwidth:DL?").strip()
        # float(dl_level)
        # dl_level = self.instr_query("CONFigure:LTE:SIGN:DL:RSEPre:LEVel?").strip()
        # ue_struct = namedtuple("ue_struct",['BAND','CH_UL','CH_DL','BW'])
        return ue_struct(band, int(ch_ul),int(ch_dl), bw)

    def LTE_meas_sense(self,route_path="main", pwr_init =-120, pwr_coarse = 0.5, pwr_fine=0.1, frame_coarse=200, frame_fine = 1000):
        self.instr_write("CONFigure:LTE:SIGN:EBLer:REPetition SING")
        self.instr_write("CONFigure:LTE:SIGN:EBLer:SCONdition NONE")

        self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
        self.instr_write ("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
        # route_path="div"
        if route_path == "div":
            self.instr_write("ROUTe:LTE:SIGN:SCENario:SCELl RF1C,RX1,RF1O,TX1")
            time.sleep(3)
        
        # init, coarse, pwr_back, fine, pwr_back_fine, end
        EBL_state = "init"
        while EBL_state != "end":
            if EBL_state == "init":
                pwr, throughput = self.LTE_sens_param(pwr_init,frame=frame_coarse)
                if throughput >= 95:
                    EBL_state = "coarse"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "coarse":
                pwr = pwr - pwr_coarse
                if throughput != 100:
                    pwr = pwr+0.4*pwr_coarse
                pwr, throughput = self.LTE_sens_param(pwr,frame=frame_coarse)
                if throughput >=95:
                    EBL_state = "coarse"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "pwr_back":
                pwr = pwr + pwr_coarse
                pwr, throughput = self.LTE_sens_param(pwr,frame=frame_coarse)
                if throughput >= 95:
                    EBL_state = "fine"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "fine" :
                pwr = pwr - pwr_fine
                pwr, throughput = self.LTE_sens_param(pwr,frame=frame_fine)
                if throughput >= 95:
                    EBL_state = "fine"
                else:
                    EBL_state = "pwr_back_fine"
            elif EBL_state == "pwr_back_fine":
                pwr = pwr + pwr_fine
                pwr, throughput = self.LTE_sens_param(pwr,frame=frame_fine)
                if throughput >= 95:
                    EBL_state = "end"
                else:
                    EBL_state = "pwr_back_fine"
            # print("\r",round(pwr,2), throughput, EBL_state,end="")
            print("\r{0}, {1}, {2}".format(round(pwr,2), throughput, EBL_state),end="")
        print("\nsense {md}: {pwr:.1f}, {throughput}".format(md=route_path, pwr=pwr, throughput=throughput))
        cell_pwr = float(self.instr_query("SENSe:LTE:SIGN:DL:FCPower?"))
        self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
        if route_path == "div":
            self.instr_write("ROUTe:LTE:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
            time.sleep(2)
        time.sleep(1)
        # return (round(pwr,2), round(throughput,2))
        return (round(cell_pwr,2), round(throughput,2))

    def LTE_data_dealing(self, res, data_type):
        res = res.split (',')
        if not int(res[0]):
            if data_type =="aclr":
                # return "UTRA1neg {0:.2f}, EUTRAneg {1:.2f}, PWR {2:.2f}, EUTRApos {3:.2f}, UTRA1pos {4:.2f}".format(
                    # float(res[3]), float(res[4]), float(res[5]), float(res[6]), float(res[7]))
                res_aclr = {}
                res_aclr["UTRA1neg"] = float(res[2])
                res_aclr["EUTRAneg"] = float(res[3])
                res_aclr["PWR"] = float(res[4])
                res_aclr["EUTRApos"] = float(res[5])
                res_aclr["UTRA1pos"] = float(res[6])
                # return res_aclr
                return (round(float(res[2]),2),round(float(res[3]),2),round(float(res[4]),2),round(float(res[5]),2),round(float(res[6]),2))
            elif data_type == "bler":
                res_bler = {}
                res_bler["ACK"] = round(float(res[1]),2)
                res_bler["BLER"] = round(float(res[3]),2)
                res_bler["Throughput"] = round(float(res[4]),2)
                # return "ACK {0:.2f}, NACK {1:.2f}, BLER {2:.2f}, Throughput {3:.2f}, DTX {4:.2f}".format(
                    # float(res[1]), float(res[2]), float(res[3]), float(res[4]), float(res[5]))
                return res_bler
            else :
                return None
        else :
            # 错误处理函数，参考P490
            return None
    
    def LTE_data_output(self, output_result, fp):
        # output_result, aclr, sense
        with open(fp, 'w') as f:
            if "aclr" in output_result:
                f.write("BAND\tUL_Ch\tBW\tEUTRA\tUTRA\tPWR\tUTRA\tEUTRA\n")
                for line in output_result["aclr"]:
                    f.write(str(str_ue_info(line[:4])))
                    f.write("\t")
                    f.write("\t".join(map(str,line[4:])))
                    f.write("\n")
            # set_sens = list(set(["sensm","sensd"]) & set([output_result.keys()]))
            set_sens = [item for item in ["sensm","sensd"] if item in output_result]
            if set_sens:
                f.write("BAND\tUL_Ch\tBW\t{0}\n".format("\t".join(set_sens)))
                for i in range(len(output_result[set_sens[0]])):
                    f.write(str(str_ue_info(output_result[set_sens[0]][i][:4])))
                    for item in set_sens:
                        f.write("\t{0}".format(output_result[item][i][4]))
                    f.write("\n")

    def LW_sense_algorithm(self,md="LTE"):
        if md == "LTE":
            pwr_init = -120
            pwr_coarse = 0.5
            pwr_fine = 0.1
            frame_coarse = 200
            frame_fine = 1000
            BER_threshold = 5

        
        # init, coarse, pwr_back, fine, pwr_back_fine, end

    def WCDMA_para_configure(self, test_list = None):
        if test_list is None:
            test_list = (("OB1", 9612, 10562),)

        if self.LW_check_connection(md = "WCDMA"):
            self.WCDMA_ch_redirection(test_list[0])
        else:
            self.instr_reset_cmw()
            self.set_FDCorrection(param_FDCorrection)
            self.instr_write("SOURce:WCDMa:SIGN:CELL:STATe OFF")
            self.instr_write("CONFigure:WCDMa:SIGN:CARRier:BAND {0}".format(test_list[0][0]))
            self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL {0}".format(test_list[0][1]))
            self.instr_write("CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:TMODe MODE2")
            self.instr_write("SOURce:WCDMa:SIGN:CELL:STATe ON")
            self.instr_write("ROUTe:WCDMa:MEAS:SCENario:CSPath 'WCDMA Sig1'")
            while self.instr_query("SOUR:WCDM:SIGN:CELL:STAT:ALL?").strip()!="ON,ADJ":
                time.sleep(1)
            print("Cell initialling done")
        self.instr_write("CONFigure:WCDMa:MEAS:MEValuation:REPetition SINGleshot")
        self.instr_write("CONFigure:WCDMa:MEAS:MEValuation:SCOunt:SPECtrum 10")
        self.instr_write("CONFigure:WCDMa:MEAS:MEValuation:SCOunt:MODulation 10")
        self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")

    def WCDMA_ch_travel(self, test_list,mea_item=("aclr",)):
        # self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower -56.10")
        # 平均次数
        if "sensm" in mea_item:
            self.instr_write("CONFigure:WCDMa:SIGN:BER:SCONdition None")
            self.instr_write("CONFigure:WCDMa:SIGN:BER:REPetition SINGleshot")
            self.instr_write("CONFigure:WCDMa:SIGN:BER:TBLocks 100")
        for item in test_list:
            self.WCDMA_ch_redirection(item)
            self.WCDMA_acquire_Meas(mea_item = mea_item)

    def WCDMA_acquire_Meas(self, mea_item=("aclr",)):
        if self.LW_check_connection(md="WCDMA"):
            self.instr_write("INITiate:WCDMa:MEAS:MEValuation")
            while self.instr_query("FETCh:WCDMa:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
                time.sleep(1)
            if "aclr" in mea_item:
                self.WCDMA_meas_aclr()
            if "sensm" in mea_item:
                self.WCDMA_meas_sense()
            print("")
        else:
            print("Not connected")
        pass

    def WCDMA_meas_aclr(self):
        self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower -56.10")
        self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
        time.sleep(1)
        res = self.instr_query("READ:WCDMa:MEAS:MEValuation:SPECtrum:AVERage?",delay = 4)
        # res = self.instr_query("FETCh:WCDMa:MEAS:MEValuation:SPECtrum:AVERage?")
        res = [ round(float(res.split(",")[i]),2) for i in [2,3,15,4,5] ]
        # return (round(res[2],2),round(res[3],2),round(res[15],2),round(res[4],2),round(res[5],2))
        print(res)
        return res

    def WCDMA_meas_sense(self):
        print(self.WCDMA_meas_sense_cell(-90))
        self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower -56.1")
        pass

    def WCDMA_meas_sense_cell(self, down_level):
        self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower {0}".format(down_level))
        time.sleep(1)
        # self.instr_write("INITiate:WCDMa:SIGN:BER")
        res = self.instr_query("READ:WCDMa:SIGN:BER?",delay = 4)
        return down_level, round(float(res.split(",")[1]),2)

    def WCDMA_ch_redirection(self,dest_state):
        self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower -56.10")
        last_state = self.WCDMA_get_state()
        print("try redrection to {0}".format(dest_state))
        if last_state[0] == dest_state[0]:
            if last_state[1] != dest_state[1]:
                self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL {ch_ul}".format(ch_ul=dest_state[1]))
                time.sleep(4)
        else:
            self.instr_write("CONFigure:WCDMa:SIGN:CARRier:BAND {band}".format(band=dest_state[0]))
            time.sleep(8)
            self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL {ch_ul}".format(ch_ul=dest_state[1]))
            time.sleep(4)
        if self.LW_check_connection(md="WCDMA"):
            if self.WCDMA_get_state() == dest_state:
                print("redirection successful")
            else:
                print("redirection failed but connected")
        else:
            print("------------redirection error---------------------------")

    def WCDMA_get_state(self):
        band = self.instr_query("CONFigure:WCDMa:SIGN:CARRier:BAND?").strip()
        ch_ul = self.instr_query("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL?").strip()
        ch_dl = self.instr_query("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:DL?").strip()
        return (band, int(ch_ul), int(ch_dl))

        # "SOURce:WCDMa:SIGN:CELL:STATe ON"
        # ON 的过程比较久
        # PM.write ("CONFigure:WCDMa:SIGN:CARRier:BAND OB1")
        # PM.write ("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL 9612")
        # "ROUTe:WCDMa:MEAS:SCENario:CSPath 'WCDMA Sig1'"
        # CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:TMODe MODE2
        #     PM.write ("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
        # CONFigure:WCDMa:SIGN:RFSettings:COPower -56.10


        # CONFigure:WCDMa:SIGN<i>:CARRier<c>:BAND
        # CONFigure:WCDMa:SIGN<i>:RFSettings:CARRier<c>:CHANnel:DL
        # CONFigure:WCDMa:SIGN<i>:RFSettings:CARRier<c>:CHANnel:UL
        # 查看WCDMA的软件版本
        # SYST:OPT:VERS? 'CMW_WCDMA_Sig'

    def test_wcdma(self):
        # self.instr_reset_cmw()
        # base 配置 loss
        self.set_FDCorrection(param_FDCorrection)
        # for i in range(10):
        # print("----------------- {0} time -----------".format(i))
        self.WCDMA_para_configure(TEST_LIST_W)
        self.LW_connect(md="WCDMA")
        self.WCDMA_ch_travel(TEST_LIST_W, mea_item = ("sensm","aclr"))
        pass
    
    def test_lte(self):
        # self.instr_reset_cmw()
        # base 配置 loss
        self.set_FDCorrection(param_FDCorrection)
        self.LTE_para_configure(TEST_LIST)
        self.LW_connect(md="LTE")
        self.LTE_ch_travel(TEST_LIST,mea_item=("aclr","sensm","sensd"))
        # self.LTE_ch_travel(TEST_LIST,mea_item=("aclr","sensm"))
        pass

if __name__ == '__main__':
    # instr.close()
    # rm = visa.ResourceManager()
    # instr = rm.open_resource("TCPIP0::10.237.70.51::inst0::INSTR")
    # print( "res:", rm.list_resources())
    # print(instr.query("*IDN?"))
    # print(instr.query("*IDN?"))
    # Reset_cmw(instr)
    phone = adb()
    # phone.adb_reboot()

    rm = RM_cmw()
    m = handle_instr(rm.open_resource("TCPIP0::10.237.70.10::inst0::INSTR"), phone)
    # m = handle_instr(rm.open_resource("GPIB0::20::INSTR"))

    print(m.get_instr_version())
    m.set_remote_display(state=True)
    m.test_lte()
    # m.test_wcdma()

    m.instr_close()
    rm.close()

    # CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:UL?
    # CONFigure:LTE:SIGN:PCC:BAND?
    # CONFigure:LTE:SIGN:CELL:BANDwidth:DL?
