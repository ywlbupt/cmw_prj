#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, visa, time 
import re
import operator
from datetime import datetime
from package.logHandler import LogHandler
import heapq

from band_def import TEST_LIST
from lte_band_def import LTE_Calc
from instr import handle_instr
from instr import device_scan
from MACRO_DEFINE import *
from instr_66319D import handle_instr_66319D

from config_default import param_FDCorrection
from config_default import config as CONFIG
from config_default import SENSE_PARAM
from config_default import PRJ_PORT
from adb import adb

# import logging
# log = LogHandler("test_log", level = logging.DEBUG)
# log.info("test log")

#import msvcrt

#PM = visa.instrument("TCPIP0::192.168.0.1::inst0::INSTR")
#PM = visa.instrument("GPIB1::20::INSTR")

MD_MAP = {"WCDMA":"WT","TDSC":"WT","LTE":"LTE","GSM":"GSM"}

def printt(*args, **kwargs):
    if True:
        print(*args, **kwargs)
    else:
        log.info(*args)

class ConnectionError(Exception):
    pass

class handle_instr_cmw500(handle_instr):
    instr_name_p = re.compile (r"Rohde&Schwarz.*CMW.*")

    def __init__(self, instr_socall_addr, phone_hd=None):
        super().__init__(instr_socall_addr)
        self.phone_hd=phone_hd
        self.device_A66319D = None
        self.soft_version = {}
    
    def instr_reset_cmw(self):
        self.instr_write("*RST;*OPC")
        self.instr_write("*CLS;*OPC?")
        print("instr reset.......")
        time.sleep(4)

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
                        # return(int(i) for i in ver_m.group[1:4])
        else:
            return version_list

    def cmw_soft_version_compare(self, version_vector, require_vector):
        # operator.ge python3中大于或者等于
        if operator.ge(version_vector, require_vector):
            return True
        else:
            return False

    def set_remote_display(self, state=True):
        if state:
            self.instr_write("SYSTem:DISPlay:UPDate ON")
        else:
            self.instr_write("SYSTem:DISPlay:UPDate OFF")

    def set_FDCorrection(self,loss_array, md = None):
        OUTPUT_EAT, INPUT_EAT, loss_matrix = loss_array
        if md:
            self.instr_write("CONFigure:{0}:SIGN:RFSettings:EATTenuation:OUTPut {1}".format(md, OUTPUT_EAT))
            self.instr_write("CONFigure:{0}:SIGN:RFSettings:EATTenuation:INPut {1}".format(md, INPUT_EAT))

        self.instr_write("CONFigure:BASE:FDCorrection:CTABle:DELete:ALL")
        if loss_matrix :
            self.instr_write("CONFigure:BASE:FDCorrection:CTABle:CREate 'CMW_loss', {loss_matrix}".format(loss_matrix=loss_matrix))
            self.instr_write ("CONFigure:FDCorrection:ACTivate RF1C, 'CMW_loss', RXTX, RF1")
            self.instr_write ("CONFigure:FDCorrection:ACTivate RF1O, 'CMW_loss', RXTX, RF1")
            self.instr_write ("CONFigure:FDCorrection:ACTivate RF2C, 'CMW_loss', RXTX, RF1")
            try:
                self.instr_write ("CONFigure:FDCorrection:ACTivate RF3C, 'CMW_loss', RXTX, RF2")
                self.instr_write ("CONFigure:FDCorrection:ACTivate RF3O, 'CMW_loss', RXTX, RF2")
            except:
                pass

    def __LTE_get_fdd_or_tdd(self, dd_int):
        if isinstance (dd_int, str):
            dd_int = int(dd_int)
        if dd_int < 33 or dd_int == 66:
            return "FDD"
        else:
            return "TDD"

    def LTE_para_configure(self, md, test_list):
        if self.LWGT_check_connection(md):
            self.LWGT_set_dl_pwr(md)
            self.set_FDCorrection(param_FDCorrection)
            self.LTE_ch_redirection(test_list[0])
            pass
        else:
            self.instr_write ("SOURce:LTE:SIGN:CELL:STATe OFF")
            self.instr_reset_cmw()
            self.set_FDCorrection(param_FDCorrection)
            # test_DD = "FDD" if int(test_list[0].BAND[2:])<33 or  else "TDD"
            test_DD = self.__LTE_get_fdd_or_tdd(int(test_list[0].BAND[2:])<33)
            self.instr_write ("CONFigure:LTE:SIGN:DMODe {DD}".format(DD=test_DD))
            self.instr_write ("CONFigure:LTE:SIGN:PCC:BAND {band}".format(band=test_list[0].BAND))
            self.instr_write ("CONFigure:LTE:SIGN:RFSettings:CHANnel:UL {0}".format(test_list[0].CH_UL))
            self.instr_write ("CONFigure:LTE:SIGN:CELL:BANDwidth:DL {0}".format(test_list[0].BW))

        self.LWGT_set_port_route(md,test_list[0].BAND[2:],route_path = "main")

        self.instr_write ("ROUTe:LTE:MEAS:SCENario:CSPath 'LTE Sig1'")


        self.instr_write ("SOURce:LTE:SIGN:CELL:STATe ON")

        while self.instr_query("SOURce:LTE:SIGN:CELL:STATe:ALL?").strip() != "ON,ADJ":
            time.sleep(1)
        self.instr_write ("CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")
        # 最大功率
        self.LWGT_set_ul_pwr(md, pwr="MAX")

    def LTE_set_ul_RB(self, rb_num, rb_pos):
        self.instr_write ("CONFigure:LTE:SIGN:CONNection:PCC:RMC:UL N{rb_num},QPSK,KEEP".format(rb_num = rb_num))
        self.instr_write ("CONFigure:LTE:SIGN:CONNection:PCC:RMC:RBPosition:UL P{rb_pos}".format(rb_pos = rb_pos))
        # CONFigure:LTE:SIGN:CONNection:PCC:RMC:UL N12,QPSK,KEEP
        # CONFigure:LTE:SIGN:CONNection:PCC:RMC:RBPosition:UL P0
        pass


    def LWGT_set_dl_pwr(self, md, pwr=None):
        if md=="WCDMA":
            if pwr == None:
                pwr = -56.10
            self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower {0}".format(pwr))
        elif md == "TDSC":
            if pwr == None:
                pwr = -60
            self.instr_write("CONFigure:TDSCdma:SIGN:DL:LEVel:PCCPch {0}".format(pwr))
        elif md == "LTE":
            if pwr == None :
                pwr = -80
            self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel {pwr}".format(pwr=pwr))
        elif md == "GSM":
            if pwr == None :
                pwr = -80
            self.instr_write("CONFigure:GSM:SIGN:RFSettings:LEVel:TCH {pwr}".format(pwr=pwr))

    def LWGT_meas_curr(self, md, m_66319D):
        res = []
        # 取10次平均
        mea_len = 10
        # test_status = ["MAX", "MIN"]
        test_pwr_status = {
            "LTE" : [22, "MIN"],
            "WCDMA" : [23, "MIN"],
            "GSM" : ["MAX", "MIN"],
            "TDSC" : [23, "MIN"],
        }
        pwr_pos = {
            "LTE" : 2,
            "WCDMA" : 2,
            "TDSC" : 2,
        }
        def data_filter(res_array):
            # 舍弃比最小值大10的数值
            # require py lib : heapq
            delta_mA = 10
            min5_res_array = heapq.nsmallest(5, res_array)
            if (max(min5_res_array) - min(min5_res_array))< delta_mA/1000:
                return round( sum(min5_res_array)/5,4 )
            else:
                return False

        def stable_cur_get(mea_len_f):
            while(True):
                res_list = []
                for i in range(mea_len_f):
                    time.sleep(0.5)
                    temp = m_66319D.instr_get_DC_current()
                    print("{0}, ".format(temp),end="",flush =True)
                    res_list.append(temp)
                print("")
                res_avg = data_filter(res_list)
                if res_avg:
                    return round(res_avg,4)
                else:
                    print("currents unstable")
        
        if md == "LTE":
            ul_rb_info_save = self.instr_query("CONFigure:LTE:SIGN:CONNection:PCC:RMC:UL?").strip()
            ul_rb_pos_info_save = self.instr_query("CONFigure:LTE:SIGN:CONNection:PCC:RMC:RBPosition:UL?").strip()
            self.LTE_set_ul_RB(12,0)
            pass


        for j,st in enumerate(test_pwr_status[md]):
            # self.LWGT_set_ul_pwr(md, pwr=st)
            pwr_target = int(st) if st!="MIN" and st!="MAX" else None

            if md != "GSM":
                res_aclr = getattr(self, MD_MAP[md]+"_meas_aclr")(md, pwr=st)
            else:
                res_aclr = self.GSM_meas_ssw(pwr=st)
            time.sleep(5)

            # GSM MAX状态暂时不考虑
            if j==0 and md!="GSM":
                Cstate = "init"
                aclr_l, aclr_h = None ,None
                pwr_present = pwr_target
                cur_temp = stable_cur_get(mea_len)
                while(True):
                    if Cstate == "init":
                        if res_aclr[pwr_pos[md]] > pwr_target:
                            pwr_present = pwr_present - 1
                            aclr_h,cur_h = res_aclr, cur_temp
                            Cstate = "high_seek_lower"
                        elif res_aclr[pwr_pos[md]] < pwr_target: 
                            pwr_present = pwr_present + 1
                            aclr_l, cur_l = res_aclr,cur_temp
                            Cstate = "low_seek_higher"
                        elif res_aclr[pwr_pos[md]] == pwr_target:
                            cur_unit = cur_temp
                            aclr_unit = res_aclr
                            break
                    elif Cstate == "high_seek_lower":
                        if res_aclr[pwr_pos[md]] > pwr_target:
                            pwr_present = pwr_present - 1
                            aclr_h,cur_h = res_aclr, cur_temp
                            Cstate = "high_seek_lower"
                        elif res_aclr[pwr_pos[md]] < pwr_target: 
                            pwr_present = pwr_present + 1
                            aclr_l, cur_l = res_aclr,cur_temp
                            Cstate = "unit"
                        elif res_aclr[pwr_pos[md]] == pwr_target:
                            cur_unit = cur_temp
                            aclr_unit = res_aclr
                            break
                    elif Cstate == "low_seek_higher":
                        if res_aclr[pwr_pos[md]] > pwr_target:
                            pwr_present = pwr_present - 1
                            aclr_h,cur_h = res_aclr, cur_temp
                            Cstate = "unit"
                        elif res_aclr[pwr_pos[md]] < pwr_target: 
                            pwr_present = pwr_present + 1
                            aclr_l, cur_l = res_aclr,cur_temp
                            Cstate = "low_seek_higher"
                        elif res_aclr[pwr_pos[md]] == pwr_target:
                            cur_unit = cur_temp
                            aclr_unit = res_aclr
                            break

                    print(Cstate, pwr_present)
                    if Cstate == "unit":
                        pwr_l,pwr_h = aclr_l[pwr_pos[md]], aclr_h[pwr_pos[md]]
                        per_pwr_l = (pwr_target-pwr_l)/(pwr_h-pwr_l)
                        aclr_unit = (round(lx+(hx-lx)*per_pwr_l,2) for lx,hx in zip(aclr_l, aclr_h))
                        print("unit_aclr: {0}".format(list(aclr_unit)))
                        cur_unit = round(cur_l+(cur_h-cur_l)*per_pwr_l,4)
                        break

                    res_aclr = getattr(self, MD_MAP[md]+"_meas_aclr")(md, pwr=pwr_present)
                    cur_temp = stable_cur_get(mea_len)

                pass
            # j==1 状态直接测小功率
            else:
                cur_unit = stable_cur_get(mea_len)

            res.append(cur_unit)
            # res.append(stable_cur_get(mea_len))
            print("Pwr {0} Average: {1}".format(st,res[j]))
            print("")

        if md =="LTE":
            self.instr_write("CONFigure:LTE:SIGN:CONNection:PCC:RMC:UL {0}".format(ul_rb_info_save))
            self.instr_write("CONFigure:LTE:SIGN:CONNection:PCC:RMC:RBPosition:UL {0}".format(ul_rb_pos_info_save))

        return (res[0], res[1], round(res[0]-res[1],4))

    def LWGT_set_ul_pwr(self, md, pwr):
        def WT_set_ul_pwr(md, pwr="MAX"):
            confirm_res = { "MAX":  "MAXP", "MIN":  "MINP", }
            if pwr == "MAX":
                # PM.write ("CONFigure:TDSCdma:MEAS:TPC:SETup ALL1")
                self.instr_write("CONFigure:{md}:SIGN:UL:TPC:SET ALL1".format(md=md))
            elif pwr == "MIN":
                self.instr_write("CONFigure:{md}:SIGN:UL:TPC:SET ALL0".format(md=md))
            elif isinstance(pwr, (int,float)):
                self.instr_write("CONFigure:{md}:SIGN:UL:TPC:SET CLOop".format(md=md))
                self.instr_write("CONFigure:{md}:SIGN:UL:TPC:TPOWer:REFerence TOTal".format(md=md))
                self.instr_write("CONFigure:{md}:SIGN:UL:TPC:TPOWer {pwr}".format(md=md,pwr=pwr))

            else:
                return
            self.instr_write("CONFigure:{md}:SIGN:UL:TPC:PRECondition".format(md=md))
            self.instr_write("CONFigure:{md}:SIGN:UL:TPC:PEXecute".format(md=md))
            time.sleep(1)
            for i in range(10):
                res_tpc = self.instr_query("CONFigure:{md}:SIGN:UL:TPC:STATe?".format(md=md)).strip()
                if res_tpc == "IDLE" or res_tpc == confirm_res.get(pwr,"TPL"):
                    # TPLock
                    # raise ConnectionError
                    break
                time.sleep(0.5)
        
        def GSM_set_ul_pwr(md, pwr="MAX"):
            # GSM set pcl
            if pwr == "MAX":
                present_state = self.LWGT_get_state(md)
                pcl = 5 if present_state.g_BAND in ("G085","G09") else 0
                self.instr_write("CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched {pcl}".format(pcl = pcl))
            elif pwr == "MIN":
                present_state = self.LWGT_get_state(md)
                pcl = 19 if present_state.g_BAND in ("G085","G09") else 15
                self.instr_write("CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched {pcl}".format(pcl = pcl))
            elif isinstance(pwr, int):
                self.instr_write("CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched {pcl}".format(pcl = pwr))
            else:
                return 

        def LTE_set_ul_pwr(md, pwr="MAX"):
            if pwr == "MAX":
                self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET CLOop")
                self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
            elif pwr == "MIN":
                self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET CLOop")
                self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MINPower")
            elif isinstance(pwr, (int,float)):
                self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET CLOop")
                self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:CLTPower {pwr}".format(pwr=pwr))
            else:
                return 

        func = eval(MD_MAP[md]+"_set_ul_pwr")
        return func(md, pwr)

    def LWGT_ch_travel(self, md, test_list, mea_item):
        total_res = {}
        for item in mea_item:
            total_res[item]=[]
        try:
            for dest_state in test_list:
                try:
                    if md in ['WCDMA', "TDSC"]:
                        self.WT_ch_redirection(md, dest_state)
                    else:
                        getattr(self, md+"_ch_redirection")(dest_state)
                except ConnectionError as e:
                    self.LWGT_disconnect_off(md, state_on=False)
                    getattr(self,MD_MAP[md]+"_para_configure")(md, TEST_LIST[md])
                    self.LWGT_connect(md)

                for i in range(3):
                    try:
                        temp = getattr(self, MD_MAP[md]+"_acquire_meas")(md, mea_item)
                        break
                    except ConnectionError as e:
                        if not self.LWGT_check_connection(md):
                            self.LWGT_set_port_route(md, dest_state.BAND[2:], "main")
                            self.LWGT_set_dl_pwr(md)
                            self.LWGT_disconnect_off(md, state_on=True)
                            self.LWGT_connect(md)
                        else:
                            print("still connected, try again")
                for item in temp.keys():
                    total_res[item].append(dest_state+temp[item])
                print("")
        finally:
            self.LWGT_data_output(md, total_res, 
                os.path.splitext(CONFIG[md]['data_save'])[0]+datetime.today().strftime("_%Y_%m_%d_%H_%M")
                +os.path.splitext(CONFIG[md]['data_save'])[1])
            print(total_res)

    def LWGT_set_port_route(self,md, band_num,route_path = "main"):
        if int(band_num) in PRJ_PORT:
            _port = PRJ_PORT[int(band_num)]
        else:
            _port = PRJ_PORT['default']
        _str_port_main = _port[0]+","+"RX"+_port[1]+","+_port[0]+","+"TX"+_port[1]
        _str_port_div = _port[0]+","+"RX"+_port[1]+","+_port[2]+","+"TX"+_port[3]

        route = {
            "main"  :   _str_port_main,
            "div"   :   _str_port_div,
        }
        print(route[route_path])
        self.instr_write("ROUTe:{md}:SIGN:SCENario:SCELl {route}".format(
            md=md, route=route[route_path]))

    def LWG_get_RSRP(self, md="LTE"):
        # cmd_md = "WCDMa" if md=="WCDMA" else md
        if md != "GSM":
            self.instr_write("CONFigure:{md}:SIGN:UEReport:ENABle ON".format(md=md))
            # time.sleep(1)
        if md == "LTE":
            res = self.instr_query("SENSe:LTE:SIGN:UEReport:RSRP:RANGe?")
            while "NAV" in res:
                time.sleep(1)
                res = self.instr_query("SENSe:LTE:SIGN:UEReport:RSRP:RANGe?")
            RSRP = list(map(float, res.strip().split(",")[:2]))
        elif md == "WCDMA":
            res = self.instr_query("SENSe:WCDMa:SIGN:UEReport:CCELl?")
            while "NAV" in res:
                time.sleep(1)
                res = self.instr_query("SENSe:WCDMa:SIGN:UEReport:CCELl?")
            RSRP = list(map(float, res.strip().split(",")[:2]))
        elif md == "GSM":
            res = self.instr_query("SENSe:GSM:SIGN:RREPort:RXLevel:RANGe?")
            while "NAV" in res:
                time.sleep(1)
                res = self.instr_query("SENSe:GSM:SIGN:RREPort:RXLevel:RANGe?")
            RSRP = list(map(float, res.strip().split(",")[:2]))
        return RSRP

    def LWGT_get_state(self, md):
        def GSM_get_state():
            g_ch = self.instr_query("CONFigure:GSM:SIGN:RFSettings:CHANnel:TCH?").strip()
            g_band = self.instr_query("SENSe:GSM:SIGN:BAND:TCH?").strip()
            return ue_struct_g(g_band, int(g_ch))

        def LTE_get_state():
            band = self.instr_query("CONFigure:LTE:SIGN:PCC:BAND?").strip()
            ch_ul = self.instr_query("CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:UL?").strip()
            ch_dl = self.instr_query("CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:DL?").strip()
            bw = self.instr_query("CONFigure:LTE:SIGN:CELL:BANDwidth:DL?").strip()
            return ue_struct_l(band, int(ch_ul),int(ch_dl), bw)
        
        def WCDMA_get_state():
            band = self.instr_query("CONFigure:WCDMa:SIGN:CARRier:BAND?").strip()
            ch_ul = self.instr_query("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL?").strip()
            ch_dl = self.instr_query("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:DL?").strip()
            return ue_struct_w(band, int(ch_ul), int(ch_dl))

        def TDSC_get_state():
            t_band = self.instr_query("CONFigure:TDSCdma:SIGN:RFSettings:BAND?").strip()
            t_ch = self.instr_query("CONFigure:TDSCdma:SIGN:RFSettings:CHANnel?").strip()
            return ue_struct_t(t_band, int(t_ch))

        md_get_state = eval(md+"_get_state")
        return md_get_state()
    
    def LWGT_check_connection(self, md = "LTE"):
        if md == "LTE":
            res_ps = self.instr_query("FETCh:LTE:SIGN:PSWitched:STATe?").strip()
            res_rrc = self.instr_query("SENSe:LTE:SIGN:RRCState?").strip()
            if res_ps == "CEST" and res_rrc == "CONN":
                return True
            else:
                return False
        elif md in ["WCDMA","TDSC"]:
            res_cs = self.instr_query("FETCh:{0}:SIGN:CSWitched:STATe?".format(md)).strip()
            res_ps = self.instr_query("FETCh:{0}:SIGN:PSWitched:STATe?".format(md)).strip()
            if res_cs == "CEST" and res_ps == "ATT" :
                if md == "WCDMA":
                    ue_info_dinfo = self.instr_query("SENSe:{0}:SIGN:UESinfo:DINFo?".format(md)).strip().split(",")[1:3]
                    if ue_info_dinfo[0]=="OK" and ue_info_dinfo[1]=="OK":
                        pass
                    else: 
                        return False
                return True
            else:
                return False
        elif md == "GSM":
            res_cs = self.instr_query("FETCh:GSM:SIGN:CSWitched:STATe?").strip()
            if res_cs == "CEST":
                return True
            else:
                return False
        else :
            return True

    def LWGT_connect(self,md):
        print("{md} connect begin".format(md = md))
        for j in range(3):
            for i in range(30):
                if md == "LTE":
                    self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion CONNect")
                    time.sleep(2)
                    res_ps = self.instr_query( "FETCh:LTE:SIGN:PSWitched:STATe?").strip()
                    res_rrc = self.instr_query("SENSe:LTE:SIGN:RRCState?").strip()
                    print("\r{0:<5} ".format(res_ps),end="")
                    print("Connecting phone, {0}".format(i),end="")
                    if res_ps == "CEST" and res_rrc == "CONN":
                        break
                elif md in ["WCDMA","TDSC"]:
                    res_ps = self.instr_query("FETCh:{0}:SIGN:CSWitched:STATe?".format(md),delay=1).strip()
                    print("\r{0:<5} ".format(res_ps),end="")
                    print("Connecting phone, {0}".format(i),end="")
                    if res_ps == "REG":
                        self.instr_write("CALL:{0}:SIGN:CSWitched:ACTion CONNect".format(md))
                    elif res_ps == "CEST":
                        break
                    time.sleep(2)
                elif md == "GSM":
                    if CONFIG['GSM']['WITHSIM']:
                        res_cs = self.instr_query("FETCh:GSM:SIGN:CSWitched:STATe?").strip()
                        print("\r{0:<5} ".format(res_cs),end="")
                        print("Connecting phone, {0}".format(i),end="")
                        if CONFIG['GSM']['call_type']:
                            if res_cs == "SYNC":
                                self.instr_write("CALL:GSM:SIGN:CSWitched:ACTion CONNect")
                            elif res_cs == "ALER":
                                print("  Please answer the call",end="")
                        else:
                            if res_cs == "SYNC":
                                print("  Please call from phone",end="")

                        if res_cs == "CEST":
                            break
                        time.sleep(2)
                else:
                    break
            print("")
            if not self.LWGT_check_connection(md) and j != 2:
                print("phone reboot")
                if self.phone_hd:
                    self.phone_hd.adb_reboot()
                save_state = self.LWGT_get_state(md)
                if md == "LTE":
                    self.LTE_para_configure(md, (save_state,))
                elif md == ["WCDMA","TDSC"]:
                    self.WT_para_configure(md, (save_state,))
                elif md == "GSM":
                    self.GSM_para_configure(md, (save_state,))
                    # TODO
                    pass
                time.sleep(PHONE_REBOOT_TIME)
            else:
                break
        if self.LWGT_check_connection(md):
            print("Connection Established!")
        else:
            print("Conecting failed")
        return 0

    def LWGT_disconnect_off(self, md="LTE", state_on = False):
        if md == "LTE":
            for i in range(15):
                if self.instr_query("SENSe:LTE:SIGN:RRCState?").strip() == "IDLE":
                    break
                else:
                    res = self.instr_query("FETCh:LTE:SIGN:PSWitched:STATe?").strip()
                    if res == "CEST":
                        self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion DISConnect")
                    elif res == "ATT":
                        self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion DETach")
                    time.sleep(1)
            if not state_on:
                self.instr_write("SOURce:LTE:SIGN:CELL:STATe OFF")
                while self.instr_query("SOURce:LTE:SIGN:CELL:STATe:ALL?").strip() != "OFF,ADJ":
                    time.sleep(1)
        elif md in ["WCDMA","TDSC"]:
            for i in range(15):
                res_cs = self.instr_query("FETCh:{md}:SIGN:CSWitched:STATe?".format(md=md)).strip()
                res_ps = self.instr_query("FETCh:{md}:SIGN:PSWitched:STATe?".format(md=md)).strip()
                if res_cs == "ON" and res_ps == "ON":
                    break
                else:
                    if res_cs == "REG" and res_ps == "ATT":
                        self.instr_write("CALL:{md}:SIGN:CSWitched:ACTion UNRegister".format(md=md))
                    elif res_cs == "CEST" and res_ps == "ATT":
                        self.instr_write("CALL:{md}:SIGN:CSWitched:ACTion DISCconnect".format(md=md))
                time.sleep(1)
            if not state_on:
                self.instr_write("SOURce:{md}:SIGN:CELL:STATe OFF".format(md=md))
                while self.instr_query("SOURce:{md}:SIGN:CELL:STATe:ALL?".format(md=md)).strip() != "OFF,ADJ":
                    time.sleep(1)
        elif md == "GSM":
            for i in range(15):
                res_cs = self.instr_query("FETCh:GSM:SIGN:CSWitched:STATe?").strip()
                if res_cs == "CEST":
                    self.instr_write("CALL:GSM:SIGN:CSWitched:ACTion DISC")
                if res_cs not in ["CEST","ALER", "CONN", "REL"]:
                    break
            if not state_on:
                self.instr_write("SOURce:GSM:SIGN:CELL:STATe OFF")
                while self.instr_query("SOURce:GSM:SIGN:CELL:STATe:ALL?").strip() != "OFF,ADJ":
                    time.sleep(1)

    def LTE_ch_redirection(self, dest_state):
        ''' dest_state ue_struct_l'''
        md = "LTE"
        last_state = self.LWGT_get_state(md)
        # dest_DD = "FDD" if int(dest_state.BAND[2:])<33 else "TDD"
        dest_DD = self.__LTE_get_fdd_or_tdd(dest_state.BAND[2:])
        # last_DD = "FDD" if int(last_state.BAND[2:])<33 else "TDD"
        last_DD = self.__LTE_get_fdd_or_tdd(last_state.BAND[2:])

        print(last_state)

        if dest_DD == last_DD:
            if dest_state.BAND == last_state.BAND:
                # switch_mode = "redirection"
                switch_mode = "Handover"
            else:
                switch_mode = "Handover"
            # switch_mode = "redirection"
        else:
            if self.cmw_soft_version_compare(self.soft_version[md], [3, 5, 10]):
                switch_mode = "ENHandover"
                # switch_mode = "ON_And_OFF"
            else :
                print("This devices isn't support ENHanced Handover")
                print("Try reset and Reconnect")
                # switch_mode = "ON_And_OFF"
                switch_mode = "ON_And_OFF"

        print("Try {sw} to band {st.BAND}, channel ul {st.CH_UL},channel dl {st.CH_DL}, bw {st.BW}".format(sw=switch_mode,st=dest_state))

        self.LWGT_set_port_route(md,dest_state.BAND[2:],route_path = "main")

        if switch_mode == "redirection":
            self.LWGT_set_dl_pwr(md="LTE", pwr=-80)
            band_str = "CONFigure:LTE:SIGN:PCC:BAND {0}".format(dest_state.BAND)
            ch_str = "CONFigure:LTE:SIGN:RFSettings:CHANnel:UL {0}".format(dest_state.CH_UL)
            bw_str = "CONFigure:LTE:SIGN:CELL:BANDwidth:DL {0}".format(dest_state.BW)
            str_list = [band_str,]
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
            # self.instr_write("PREPare:LTE:SIGN:HANDover:ENHanced {md}, {st.BAND}, {st.CH_DL}, {st.BW}, NS01".format(md=dest_DD, st=dest_state))
            self.instr_write("PREPare:LTE:SIGN:HANDover {st.BAND},{st.CH_DL},{st.BW},NS01".format(st=dest_state))
            self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion HANDover")
            time.sleep(2)
        elif switch_mode == "ENHandover":
            self.instr_write("PREPare:LTE:SIGN:HANDover:DESTination 'LTE Sig1'")
            # self.instr_write("PREPare:LTE:SIGN:HANDover:MMODe REDirection")
            print ("PREPare:LTE:SIGN:HANDover:ENHanced {md},{st.BAND},{st.CH_DL},{st.BW},NS01".format(md=dest_DD, st=dest_state))
            self.instr_write("PREPare:LTE:SIGN:HANDover:ENHanced {md},{st.BAND},{st.CH_DL},{st.BW},NS01".format(md=dest_DD, st=dest_state))
            time.sleep(2)
            self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion HANDover")
            time.sleep(5)
        elif switch_mode == "ON_And_OFF":
            self.LWGT_disconnect_off(md, state_on=False)
            self.LTE_para_configure(md, (dest_state,))
            self.LWGT_connect(md)

        # check RRC_STATE 
        for i in range(10):
            if self.instr_query("SENSe:LTE:SIGN:RRCState?").strip() == "CONN":
                break
            time.sleep(1)
        if not self.LWGT_check_connection(md="LTE"):
            # self.LTE_para_configure(md, (dest_state,))
            self.LWGT_connect(md="LTE")

        present_state = self.LWGT_get_state(md)
        if present_state == dest_state:
            print("{0} sucessful".format(switch_mode))
        else:
            print("{0} faild".format(switch_mode))
        pass

    def LTE_acquire_meas(self, md, mea_item = None):
        output_res = {}
        if not mea_item:
            mea_item = ("aclr",)
        elif not isinstance(mea_item, list):
            mea_item = (mea_item,)
        if not self.LWGT_check_connection(md):
            print("{md} not connected".format(md=md))
            self.LWGT_connect(md)
        if "aclr" in mea_item:
            output_res["aclr"]=self.LTE_meas_aclr(md)
        if "tx_curr" in mea_item:
            m_66319D = handle_instr_66319D("GPIB::{0}::INSTR".format(CONFIG['gpib_addr_66319D']))
            output_res["tx_curr"]=self.LWGT_meas_curr(md ,m_66319D)
            m_66319D.instr_close()
        if "sensm_max" in mea_item:
            output_res["sensm_max"]=self.LTE_meas_sense(route_path="main",ul_pwr="MAX", part_rb_enable = CONFIG['LTE']['partRB_rx_Enable'])
        if "sensm_cloop" in mea_item:
            output_res["sensm_cloop"]=self.LTE_meas_sense(route_path="main",ul_pwr=-20)
        if "sensd" in mea_item:
            # output_res["sensd"]=self.LTE_meas_sense(route_path="div", ul_pwr = "MAX")
            output_res["sensd"]=self.LTE_meas_sense(route_path="div", ul_pwr = -20)
        return output_res

    def LTE_meas_aclr(self, md="LTE", pwr = "MAX"):
        md = "LTE"
        test_DD = self.instr_query("CONFigure:LTE:SIGN:DMODe?").strip()
        if test_DD == "FDD":
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MSUBframes 0,10,0")
        else:
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MSUBframes 2,10,0")

        self.LWGT_set_ul_pwr(md, pwr)
        time.sleep(1)
        self.instr_write("INITiate:LTE:MEAS:MEValuation")
        while self.instr_query("FETCh:LTE:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:LTE:MEAS:MEValuation:ACLR:AVERage?").strip().split(",")
        res = tuple(round(float(res[i]),2) for i in [2,3,4,5,6] )
        print(res)
        self.instr_write("ABORt:LTE:MEAS:MEValuation")
        time.sleep(1)
        return res

    def LTE_meas_sense(self,route_path="main", ul_pwr="MAX", part_rb_enable = False):
        '''
        route_path : "main" or "div"
        '''
        md = "LTE"
        self.instr_write("CONFigure:LTE:SIGN:EBLer:REPetition SING")
        self.instr_write("CONFigure:LTE:SIGN:EBLer:SCONdition NONE")

        self.LWGT_set_dl_pwr(md)
        self.LWGT_set_ul_pwr(md,ul_pwr)
        state = self.LWGT_get_state(md)
        if part_rb_enable:
            cmw_bw = state.BW
            band_num = int((state.BAND)[2:])
            rb_num, rb_pos = LTE_Calc.get_band_ul_rb(band_num, cmw_bw )
            if rb_num:
                self.LTE_set_ul_RB(rb_num, rb_pos)

        if route_path == "div":
            self.LWGT_set_port_route(md,state.BAND[2:],"div")
            time.sleep(2)

        pwr, ber = self.LWGT_sense_alg(md, alg_type = "coarse") # fine or coarse
        
        self.LWGT_set_dl_pwr(md)
        if route_path == "div":
            self.LWGT_set_port_route(md,state.BAND[2:],"main")
            time.sleep(2)

        if part_rb_enable:
            rb_num = LTE_Calc.get_bw_to_rb(state.BW)
            rb_pos = 0
            # 恢复Full RB 状态
            self.LTE_set_ul_RB(rb_num, rb_pos)

        print("sense {rp} : {pwr}, {ber}".format(rp=route_path, pwr=pwr, ber= ber))
        time.sleep(1)
        return (pwr, ber)

    def LTE_meas_sense_cell(self, md, down_level, frame=1000, output_pwr_format="RS_EPRE"):
        self.LWGT_set_dl_pwr(md, pwr=down_level)
        # self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel {0}".format(down_level))
        self.instr_write("CONFigure:LTE:SIGN:EBLer:SFRames {frame}".format(frame=frame))

        self.instr_write("INITiate:LTE:SIGN:EBLer")

        while self.instr_query("FETCh:LTE:SIGN:EBL:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res =self.instr_query("FETCh:LTE:SIGN:EBLer:RELative?").strip().split(",")

        self.instr_write("ABORt:LTE:SIGN:EBLer")

        if int(res[0])==0:
            ber = round(100-float(res[1]),2)
            if output_pwr_format=="RS_EPRE":
                return down_level, ber
            elif output_pwr_format=="cell_power":
                cell_pwr = round(float(self.instr_query("SENSe:LTE:SIGN:DL:FCPower?")),2)
                return cell_pwr, ber
        else: 
            raise ConnectionError

    def LWGT_sense_alg(self,md, alg_type = "fine"):
        pwr_init = SENSE_PARAM[md]['pwr_init']
        pwr_coarse = SENSE_PARAM[md]['pwr_coarse']
        pwr_fine = SENSE_PARAM[md]['pwr_fine']
        frame_coarse = SENSE_PARAM[md]['frame_coarse']
        frame_fine = SENSE_PARAM[md]['frame_fine']
        BER_THRESHOLD = SENSE_PARAM[md]['BER_THRESHOLD']

        meas_func = getattr (self, MD_MAP[md]+"_meas_sense_cell")

        #state machine: init, coarse, pwr_back, fine, pwr_back_fine, end
        EBL_state = "init"
        while EBL_state != "end":
            if EBL_state == "init":
                pwr, ber = meas_func(md, pwr_init,frame=frame_coarse)
                if ber < BER_THRESHOLD:
                    EBL_state = "coarse"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "coarse":
                pwr = pwr - pwr_coarse
                if ber != 0:
                    pwr = pwr+0.4*pwr_coarse
                pwr, ber = meas_func(md, pwr,frame=frame_coarse)
                if ber < BER_THRESHOLD:
                    EBL_state = "coarse"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "pwr_back":
                pwr = pwr + pwr_coarse
                pwr, ber = meas_func(md, pwr,frame=frame_coarse)
                if ber < BER_THRESHOLD:
                    EBL_state = "fine_1"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "fine_1" :
                pwr = pwr - pwr_fine
                pwr, ber = meas_func(md, pwr,frame=frame_fine)
                if ber < BER_THRESHOLD:
                    EBL_state = "fine_1"
                else:
                    EBL_state = "pwr_back_fine_1"
            elif EBL_state == "pwr_back_fine_1":
                pwr = pwr + pwr_fine
                pwr, ber = meas_func(md, pwr,frame=frame_fine)
                if ber < BER_THRESHOLD:
                    if alg_type == "coarse":
                        EBL_state = "end"
                    else:
                        EBL_state = "fine_2"
                else:
                    EBL_state = "pwr_back_fine_1"
            elif EBL_state == "fine_2":
                pwr = pwr - pwr_fine
                pwr, ber = meas_func(md, pwr,frame=frame_fine)
                if ber < BER_THRESHOLD:
                    EBL_state = "fine_1"
                else:
                    EBL_state = "pwr_back_fine_2"
            elif EBL_state == "pwr_back_fine_2":
                pwr = pwr + pwr_fine
                pwr, ber = meas_func(md, pwr,frame=frame_fine)
                if ber < BER_THRESHOLD:
                    EBL_state = "end"
                else:
                    EBL_state = "pwr_back_fine_1"
            print("\r{0}, {1}, {2}".format(round(pwr,2), ber, EBL_state),end="")
            # except TypeError as e:
                # print("BER test error, NoneType receive")
        print("")
        if md == "LTE":
            pwr = float(self.instr_query("SENSe:LTE:SIGN:DL:FCPower?"))
            if CONFIG[md]['usr_define']:
                pwr = self.LWG_get_RSRP(md)[1]
                print("RSRP:"+str(self.LWG_get_RSRP(md)))
        return (round(pwr,1), round(ber,2))

    def LWGT_data_output(self, md, output_result, fp):
        if not os.path.exists(CONFIG["Report_file"]):
            os.mkdir(CONFIG["Report_file"])
        with open(os.path.join(CONFIG["Report_file"], fp),'w') as f:
            ue_info = eval("str_ue_info_"+md)
            for i,t in test_item_map[md].items():
                if t[0] in output_result:
                    f.write("{0}\n".format("\t".join(t[1])))
                    for line in output_result[t[0]]:
                        f.write("{0!s}".format(ue_info(line[:ue_info.para_num])))
                        f.write("\t{0}\n".format("\t".join(map(str,line[ue_info.para_num:]))))
        pass
    
    def GSM_para_configure(self, md, test_list=None):
        def GSM_MEA_configure():
            self.instr_write("CONFigure:GSM:MEAS:MEValuation:REPetition SINGleshot")
            self.instr_write("CONF:GSM:MEAS:MEV:SCO:MOD 10")
            self.instr_write("CONF:GSM:MEAS:MEV:SCO:SSW 10")
            self.instr_write("CONF:GSM:MEAS:MEV:SCO:SMOD 10")

        if self.LWGT_check_connection(md):
            self.LWGT_set_dl_pwr(md, pwr=-80)
            self.set_FDCorrection(param_FDCorrection)
            self.GSM_ch_redirection(test_list[0])
        else:
            self.instr_reset_cmw()
            self.set_FDCorrection(param_FDCorrection)
            self.instr_write("CONFigure:GSM:SIGN:BAND:BCCH {band}".format(band=test_list[0].g_BAND))
            self.instr_write("CONFigure:GSM:SIGN:RFSettings:CHANnel:TCH {ch}".format(ch=test_list[0].g_CH))
        self.instr_write("ROUTe:GSM:MEAS:SCENario:CSPath 'GSM Sig1'")
        self.instr_write("SOURce:GSM:SIGN:CELL:STATe ON")
        while self.instr_query("SOURce:GSM:SIGN:CELL:STATe:ALL?").strip() != "ON,ADJ":
            time.sleep(1)
        GSM_MEA_configure()
        self.LWGT_set_ul_pwr(md, pwr = "MAX")

    def GSM_acquire_meas(self, md, mea_item=None):
        output_res = {}
        if not mea_item:
            mea_item = ("switch_spetrum",)
        if not self.LWGT_check_connection(md):
            print("{md} not connected".format(md=md))
            self.LWGT_connect(md)

        if "switch_spetrum" in mea_item:
            output_res["switch_spetrum"]=self.GSM_meas_ssw()
        if "tx_curr" in mea_item:
            m_66319D = handle_instr_66319D("GPIB::{0}::INSTR".format(CONFIG['gpib_addr_66319D']))
            output_res["tx_curr"]=self.LWGT_meas_curr(md, m_66319D)
            m_66319D.instr_close()
        if "sensm" in mea_item:
            output_res["sensm"]=self.GSM_meas_sense(route_path = "main")
        if "sensd" in mea_item:
            ue_info_g = self.LWGT_get_state(md)
            # TODO
            if ue_info_g.g_BAND in [gsm_band_map[i][0] for i in CONFIG['GSM']['div-support']]:
                output_res["sensd"]=self.GSM_meas_sense(route_path="div")
        return output_res

    def GSM_meas_sense(self, route_path = "main"):
        md = "GSM"
        self.instr_write("CONFigure:GSM:SIGN:BER:CSWitched:SCONdition NONE")
        self.instr_write("CONFigure:GSM:SIGN:BER:CSWitched:MMODe BBBurst")

        self.LWGT_set_dl_pwr(md)
        self.LWGT_set_ul_pwr(md, pwr="MAX")

        if route_path == "div":
            self.LWGT_set_port_route(md,"div")
            time.sleep(2)

        pwr, ber = self.LWGT_sense_alg(md)

        print("rscp is {0}".format(self.LWG_get_RSRP(md)))

        self.LWGT_set_dl_pwr(md)
        if route_path == "div":
            self.LWGT_set_port_route(md,"main")
            time.sleep(2)

        self.instr_write("ABORt:GSM:SIGN:BER:CSWitched")
        while self.instr_query("FETCh:GSM:SIGN:BER:CSWitched:STATe?").strip() != "OFF":
            time.sleep(1)

        print("sense {rp} : {pwr}, {ber}".format(rp=route_path, pwr=pwr, ber= ber))
        time.sleep(1)
        return (pwr, ber)

    def GSM_meas_sense_cell(self, md, down_level, frame=100):
        self.LWGT_set_dl_pwr(md, pwr = down_level)
        self.instr_write("CONFigure:GSM:SIGN:BER:CSWitched:SCOunt {frame}".format(frame = frame))
        self.instr_write("INITiate:GSM:SIGN:BER:CSWitched")
        while self.instr_query("FETCh:GSM:SIGN:BER:CSWitched:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:GSM:SIGN:BER:CSWitched?").strip().split(",")
        if int(res[0])==0:
            ber = round(float(res[2]),2)
            return down_level, ber
        else: 
            raise ConnectionError

    def GSM_meas_ssw(self, pwr = "MAX"):
        md = "GSM"
        self.LWGT_set_ul_pwr(md, pwr)
        time.sleep(1)
        self.instr_write("INITiate:GSM:MEAS:MEValuation")
        while self.instr_query("FETCh:GSM:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:GSM:MEAS:MEValuation:SSWitching:FREQuency?").strip().split(",")
        res = tuple(round(float(res[i]),2) for i in [20,21,22] )
        print(res)
        return res

    def GSM_ch_redirection(self, dest_state):
        md = "GSM"
        last_state = self.LWGT_get_state(md)
        print("try redrection to {0}".format(dest_state))
        if last_state.g_BAND == dest_state.g_BAND:
            self.instr_write("CONFigure:GSM:SIGN:RFSettings:CHANnel:TCH {ch}".format(ch=dest_state.g_CH))
            time.sleep(2)
        else:
            if last_state.g_BAND != "G19" and dest_state.g_BAND != "G19" and CONFIG['GSM']['switch_type']:
                self.instr_write("PREPare:GSM:SIGN:HANDover:DESTination 'GSM Sig1'")
                self.instr_write("PREPare:GSM:SIGN:HANDover:TARGet {band}".format(band = dest_state.g_BAND))
                self.instr_write("PREPare:GSM:SIGN:HANDover:CHANnel:TCH {ch}".format(ch = dest_state.g_CH))
                self.instr_write("PREPare:GSM:SIGN:HANDover:LEVel:TCH -80".format(ch = dest_state.g_CH))
                self.instr_write("PREPare:GSM:SIGN:HANDover:PCL 5")
                self.instr_write("CALL:GSM:SIGN:HANDover:STARt")
                if self.instr_query("CONFigure:GSM:SIGN:BAND:BCCH?") != dest_state.g_BAND:
                    handover_state = "DUAL"
                else:
                    handover_state = "OFF"
                for i in range(10):
                    if self.instr_query("FETCh:GSM:SIGN:HANDover:STATe?").strip() == handover_state:
                        break
                    time.sleep(1)
            else:
                self.LWGT_disconnect_off(md, state_on=False)
                print("phone reboot")
                self.phone_hd.adb_reboot()
                self.GSM_para_configure(md, (dest_state,))

                time.sleep(PHONE_REBOOT_TIME)
                self.LWGT_connect(md)
                pass

        for i in range(10):
            if self.LWGT_check_connection():
                break
            time.sleep(1)
        present_state = self.LWGT_get_state(md)
        if present_state == dest_state:
            print("redirection successful")
        else :
            print("redirection failed")
            raise ConnectionError

    def WT_ch_redirection(self, md, dest_state):
        self.LWGT_set_dl_pwr(md)
        last_state = self.LWGT_get_state(md)
        print("try redrection to {0}".format(dest_state))
        if last_state.BAND != dest_state.BAND:
            if md == "WCDMA":
                self.instr_write("CONFigure:{md}:SIGN:BAND {band}".format(md=md, band=dest_state.BAND))
            else :
                self.instr_write("CONFigure:{md}:SIGN:RFSettings:BAND {band}".format(md=md, band=dest_state.BAND))
            time.sleep(8)
        if last_state.CH_UL != dest_state.CH_UL:
            # self.instr_write("CONFigure:{md}:SIGN:RFSettings:CHANnel:UL {ch_ul}".format(md=md, ch_ul=dest_state.CH_UL))
            self.instr_write("CONFigure:{md}:SIGN:RFSettings:CHANnel{ch_ul}".format(md=md, ch_ul=(":UL " if md == "WCDMA" else " ")+str(dest_state.CH_UL)))
            time.sleep(6)
        if self.LWGT_check_connection(md):
            if self.LWGT_get_state(md) == dest_state:
                print("redirection successful")
            else:
                print("redirection failed but connected")
                print(self.LWGT_get_state(md))
        else:
            print("------------redirection error---------------------------")

    def WT_para_configure(self, md, test_list):
        str_sig1 = {"WCDMA" : "WCDMA Sig1", "TDSC": "TD-SCDMA Sig1"}
        if self.LWGT_check_connection(md):
            # self.TDSC_ch_redirection(test_list[0])
            self.LWGT_set_dl_pwr(md)
            self.set_FDCorrection(param_FDCorrection)
            self.WT_ch_redirection(md, test_list[0])
        else:
            self.instr_write("SOURce:{0}:SIGN:CELL:STATe OFF".format(md))
            while self.instr_query("SOUR:{0}:SIGN:CELL:STAT:ALL?".format(md)).strip()!="OFF,ADJ":
                time.sleep(1)
            self.instr_reset_cmw()
            self.set_FDCorrection(param_FDCorrection)
            if md == "WCDMA":
                self.instr_write("CONFigure:{0}:SIGN:BAND {1}".format(md, test_list[0].BAND))
            else:
                self.instr_write("CONFigure:{0}:SIGN:RFSettings:BAND {1}".format(md, test_list[0].BAND))
            self.instr_write("CONFigure:{0}:SIGN:RFSettings:CHANnel {1}".format(md, test_list[0].CH_UL))
            print("ssadf",test_list[0])
            # TODO
            self.instr_write("CONFigure:{0}:SIGN:CONNection:TMODe:RMC:TMODe MODE2".format(md))
        self.instr_write("ROUTe:{0}:MEAS:SCENario:CSPath '{1}'".format(md, str_sig1[md]))
        self.instr_write("SOURce:{0}:SIGN:CELL:STATe ON".format(md))
        while self.instr_query("SOUR:{0}:SIGN:CELL:STAT:ALL?".format(md)).strip()!="ON,ADJ":
            time.sleep(1)
        print("Cell initialling done")
        self.instr_write("CONFigure:{0}:MEAS:MEValuation:REPetition SINGleshot".format(md))
        self.instr_write("CONF:{0}:MEAS:MEV:SCO:MOD 10".format(md))
        self.instr_write("CONF:{0}:MEAS:MEV:SCO:SPEC 10".format(md))
        self.LWGT_set_ul_pwr(md,pwr="MAX")

    def WT_acquire_meas(self,md, mea_item=None):
        output_res = {}
        if not mea_item:
            mea_item = ("aclr",)
        if not self.LWGT_check_connection(md):
            print("Not connected")
            self.LWGT_connect(md)
        if "aclr" in mea_item:
            output_res["aclr"] = self.WT_meas_aclr(md)
        if "tx_curr" in mea_item:
            m_66319D = handle_instr_66319D("GPIB::{0}::INSTR".format(CONFIG['gpib_addr_66319D']))
            output_res["tx_curr"]=self.LWGT_meas_curr(md, m_66319D)
            m_66319D.instr_close()
        if "sensm_max" in mea_item:
            output_res["sensm_max"] = self.WT_meas_sense(md, route_path="main",pwr="MAX")
        if "sensm_cloop" in mea_item:
            output_res["sensm_cloop"] = self.WT_meas_sense(md, route_path="main", pwr=-20)
        if "sensd" in mea_item:
            ue_info = self.LWGT_get_state(md)
            # TODO
            if ue_info.BAND in [wt_band_map[i][0] for i in CONFIG[md].get("div-support", ())]:
                output_res["sensd"] = self.WT_meas_sense(md,route_path="div")
        return output_res

    def WT_meas_aclr(self, md, pwr = "MAX"):
        # self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
        self.LWGT_set_ul_pwr(md, pwr)
        self.instr_write("INITiate:{0}:MEAS:MEValuation".format(md))
        while self.instr_query("FETCh:{0}:MEAS:MEValuation:STATe:ALL?".format(md)).strip() != "RDY,ADJ,INV":
            time.sleep(1)
        if md == "WCDMA":
            res = self.instr_query("FETCh:{0}:MEAS:MEValuation:SPECtrum:AVERage? RELative".format(md)).split(",")
            res = tuple(round(float(res[i]),2) for i in [2,3,15,4,5] )
        else :
            res = self.instr_query("FETCh:{0}:MEAS:MEValuation:SPECtrum:AVERage?".format(md)).split(",")
            for i in [2,3,4,5]:
                res[i] = float(res[i]) - float(res[1])
            res = tuple(round(float(res[i]),2) for i in [2,3,13,4,5] )
        print(res)
        return res

    def WT_meas_sense(self, md, route_path="main",pwr = "MAX"):
        self.instr_write("CONFigure:{0}:SIGN:BER:SCONdition None".format(md))
        self.instr_write("CONFigure:{0}:SIGN:BER:REPetition SINGleshot".format(md))

        self.LWGT_set_dl_pwr(md)
        self.LWGT_set_ul_pwr(md, pwr)
        if route_path == "div":
            self.LWGT_set_port_route(md, "div")
            time.sleep(2)

        pwr,ber = self.LWGT_sense_alg(md)

        self.LWGT_set_dl_pwr(md)
        if route_path == "div":
            self.LWGT_set_port_route(md, "main")
            time.sleep(2)
        print("sense {rp} : {pwr}, {ber}".format(rp=route_path, pwr=pwr, ber= ber))
        time.sleep(1)
        return (pwr, ber)

    def WT_meas_sense_cell(self, md, down_level, frame = 100):
        # self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower {0}".format(down_level))
        self.LWGT_set_dl_pwr(md, pwr=down_level)
        self.instr_write("CONFigure:{0}:SIGN:BER:TBLocks {1}".format(md, frame))
        time.sleep(1)
        self.instr_write("INITiate:{0}:SIGN:BER".format(md))
        while self.instr_query("FETCh:{0}:SIGN:BER:STATe:ALL?".format(md)).strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:{0}:SIGN:BER?".format(md)).split(",")
        # print(res)
        # if int(res[0]) == 0 and "INV" not in res:
        if int(res[0]) == 0 :
            return (down_level, round(float(res[1]),2))
        else:
            raise ConnectionError

    def test_main(self, md):
        self.set_FDCorrection(param_FDCorrection)
        self.soft_version [md] = self.get_cmw_soft_version(md)
        getattr(self,MD_MAP[md]+"_para_configure")(md, TEST_LIST[md])
        self.LWGT_connect(md)
        # TODO 可加入电源设备管理
        mea_item = [test_item_map[md][i][0] for i in CONFIG[md]['test_item']]
        self.LWGT_ch_travel(md , TEST_LIST[md], mea_item)

    def main_lte_setup(self,test_list):
        '''
        test_list : list of ue_struct_l(BAND='OB4', CH_UL=20000, CH_DL=2000, BW='B100')
        mea_item : list of "aclr", "sensm_cloop", "sensm_max", "sensd", "tx_curr"
        ''' 
        md = "LTE"
        self.set_FDCorrection(param_FDCorrection, md = md)
        self.LTE_para_configure(md, test_list)
        self.LWGT_connect(md)

        # for band_ch in test_list:
            # self.LTE_ch_redirection(band_ch)
