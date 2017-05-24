#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, visa, threading, time, string
from band_def import TEST_LIST
# from band_def import TEST_LIST_L
# from band_def import TEST_LIST_W
from MACRO_DEFINE import *
from config_default import config
from config_default import SENSE_PARAM
from adb import adb

#import msvcrt

#PM = visa.instrument("TCPIP0::192.168.0.1::inst0::INSTR")
#PM = visa.instrument("GPIB1::20::INSTR")

param_FDCorrection="1920000000, 1.0, 1980000000, 1.0, 2110000000, 1.0, 2170000000, 1.0, 1850000000, 1.0,1910000000, 1.0, 1930000000, 1.0, 1990000000, 1.0, 824000000, 0.6, 849000000, 0.6, 869000000, 0.6, 894000000, 0.6, 925000000, 0.6, 960000000, 0.6, 880000000, 0.6, 915000000, 0.6, 2350000000, 1.2, 2535000000, 1.2, 2700000000, 1.2"

class ConnectionError(Exception):
    pass

class RM_CMW(visa.ResourceManager):
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
        time.sleep(2)
        # preset instr
        self.instr_write("SYSTem:PRESet:ALL;*OPC")
        # self.instr_write("SYSTem:PRESet:ALL")
        print("instr reset.......")
        time.sleep(4)

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
        if self.LWG_check_connection(md="LTE"):
            # self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
            self.LWG_set_dl_pwr(md="LTE", pwr=-80)
            self.LTE_ch_redirection(test_list[0])
            pass
        else:
            self.instr_write ("SOURce:LTE:SIGN:CELL:STATe OFF")
            self.instr_reset_cmw()
            self.set_FDCorrection(param_FDCorrection)
            test_DD = "FDD" if int(test_list[0].BAND[2:])<33 else "TDD"
            self.instr_write ("CONFigure:LTE:SIGN:DMODe {DD}".format(DD=test_DD))
            self.instr_write ("CONFigure:LTE:SIGN:PCC:BAND {band}".format(band=test_list[0].BAND))
            self.instr_write ("CONFigure:LTE:SIGN:RFSettings:CHANnel:UL {0}".format(test_list[0].CH_UL))
        self.instr_write ("ROUTe:LTE:MEAS:SCENario:CSPath 'LTE Sig1'")
        self.instr_write ("SOURce:LTE:SIGN:CELL:STATe ON")
        while self.instr_query("SOURce:LTE:SIGN:CELL:STATe:ALL?").strip() != "ON,ADJ":
            time.sleep(1)
        self.instr_write ("CONFigure:LTE:MEAS:MEValuation:REPetition SINGleshot")
        # 最大功率
        self.LTE_set_ul_pwr(pwr="MAX")

    def LWG_set_dl_pwr(self, md, pwr=None):
        if md=="WCDMA":
            if pwr == None:
                pwr = -56.10
            self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower {pwr}".format(pwr=pwr))
        elif md == "LTE":
            if pwr == None :
                pwr = -80
            self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel {pwr}".format(pwr=pwr))
        elif md == "GSM":
            if pwr == None :
                pwr = -80
            self.instr_write("CONFigure:GSM:SIGN:RFSettings:LEVel:TCH {pwr}".format(pwr=pwr))

    def LWG_ch_travel(self, md, test_list, mea_item):
        total_res = {}
        for item in mea_item:
            total_res[item]=[]
        try:
            for dest_state in test_list:
                getattr(self, md+"_ch_redirection")(dest_state)
                for i in range(3):
                    try:
                        temp = getattr(self, md+"_acquire_meas")(mea_item)
                        break
                    except ConnectionError as e:
                        if not self.LWG_check_connection(md):
                            # TODO
                            self.LWG_set_port_route(md,"main")

                            self.LWG_set_dl_pwr(md)
                            self.LWG_disconnect_off(md, state_on=True)
                            self.LWG_connect(md)
                for item in temp.keys():
                    total_res[item].append(dest_state+temp[item])
                print("")
        finally:
            # getattr(self, md+"_data_output")(total_res,config[md]['data_save'])
            self.LWG_data_output(md, total_res, config[md]['data_save'])
            print(total_res)

    def LWG_set_port_route(self,md,route_path = "main"):
        route_m = "RF1C,RX1,RF1C,TX1"
        route_d = "RF1C,RX1,RF1O,TX1"
        route = {
            "main"  :   route_m,
            "div"   :   route_d,
        }
        # TODO
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

    def LWG_check_connection(self, md = "LTE"):
        if md == "LTE":
            res_ps = self.instr_query("FETCh:LTE:SIGN:PSWitched:STATe?").strip()
            res_rrc = self.instr_query("SENSe:LTE:SIGN:RRCState?").strip()
            if res_ps == "CEST" and res_rrc == "CONN":
                return True
            else:
                return False
        elif md == "WCDMA":
            res_cs = self.instr_query("FETCh:WCDMa:SIGN:CSWitched:STATe?").strip()
            res_ps = self.instr_query("FETCh:WCDMa:SIGN:PSWitched:STATe?").strip()
            ue_info_dinfo = self.instr_query("SENSe:WCDMa:SIGN:UESinfo:DINFo?").strip().split(",")[1:3]
            if res_cs == "CEST" and res_ps == "ATT" and ue_info_dinfo[0]=="OK" and ue_info_dinfo[1]=="OK":
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

    def LWG_connect(self,md):
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
                elif md == "WCDMA":
                    res_ps = self.instr_query("FETCh:WCDMa:SIGN:CSWitched:STATe?",delay=1).strip()
                    print("\r{0:<5} ".format(res_ps),end="")
                    print("Connecting phone, {0}".format(i),end="")
                    if res_ps == "REG":
                        self.instr_write("CALL:WCDMa:SIGN:CSWitched:ACTion CONNect")
                    elif res_ps == "CEST":
                        break
                    time.sleep(2)
                elif md == "GSM":
                    if config['GSM']['WITHSIM']:
                        res_cs = self.instr_query("FETCh:GSM:SIGN:CSWitched:STATe?").strip()
                        print("\r{0:<5} ".format(res_cs),end="")
                        print("Connecting phone, {0}".format(i),end="")
                        if config['GSM']['call_type']:
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
            if not self.LWG_check_connection(md) and j != 2:
                print("phone reboot")
                self.phone_hd.adb_reboot()
                if md == "LTE":
                    save_state = self.LTE_get_state()
                    self.LTE_para_configure((save_state,))
                elif md == "WCDMA":
                    save_state = self.WCDMA_get_state()
                    self.WCDMA_para_configure((save_state,))
                elif md == "GSM":
                    save_state = self.GSM_get_state()
                    self.GSM_para_configure((save_state,))
                    # TODO
                    pass

                time.sleep(PHONE_REBOOT_TIME)
            else:
                break
        if self.LWG_check_connection(md):
            print("Connection Established!")
        else:
            print("Conecting failed")
        return 0

    def LWG_disconnect_off(self, md="LTE", state_on = False):
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
        elif md == "WCDMA":
            for i in range(15):
                res_cs = self.instr_query("FETCh:WCDMa:SIGN:CSWitched:STATe?").strip()
                res_ps = self.instr_query("FETCh:WCDMa:SIGN:PSWitched:STATe?").strip()
                if res_cs == "ON" and res_ps == "ON":
                    break
                else:
                    if res_cs == "REG" and res_ps == "ATT":
                        self.instr_write("CALL:WCDMa:SIGN:CSWitched:ACTion UNRegister")
                    elif res_cs == "CEST" and res_ps == "ATT":
                        self.instr_write("CALL:WCDMa:SIGN:CSWitched:ACTion DISCconnect")
                    time.sleep(1)
            if not state_on:
                self.instr_write("SOURce:WCDMa:SIGN:CELL:STATe OFF")
                while self.instr_query("SOURce:WCDMa:SIGN:CELL:STATe:ALL?").strip() != "OFF,ADJ":
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
        last_state = self.LTE_get_state()
        dest_DD = "FDD" if int(dest_state.BAND[2:])<33 else "TDD"
        last_DD = "FDD" if int(last_state.BAND[2:])<33 else "TDD"

        if dest_DD == last_DD:
            if dest_state.BAND == last_state.BAND:
                # switch_mode = "redirection"
                switch_mode = "Handover"
            else:
                switch_mode = "Handover"
        else:
            switch_mode = "ENHandover"
        print(last_state)
        print("Try {sw} to band {st.BAND}, channel {st.CH_UL}, bw {st.BW}".format(sw=switch_mode,st=dest_state))
        if switch_mode == "redirection":
            # self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
            self.LWG_set_dl_pwr(md="LTE", pwr=-80)
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
            time.sleep(2)

        elif switch_mode == "ENHandover":
            self.instr_write("PREPare:LTE:SIGN:HANDover:DESTination 'LTE Sig1'")
            # self.instr_write("PREPare:LTE:SIGN:HANDover:MMODe HANDover")
            self.instr_write("PREPare:LTE:SIGN:HANDover:ENHanced {md}, {st.BAND}, {st.CH_DL}, {st.BW}, NS01".format(md=dest_DD, st=dest_state))
            self.instr_write("CALL:LTE:SIGN:PSWitched:ACTion HANDover")
            time.sleep(5)

        # check RRC_STATE 
        for i in range(10):
            if self.instr_query("SENSe:LTE:SIGN:RRCState?").strip() == "CONN":
                break
            time.sleep(1)
        if not self.LWG_check_connection(md="LTE"):
            self.LWG_connect(md="LTE")

        present_state = self.LTE_get_state()
        if present_state == dest_state:
            print("{0} sucessful".format(switch_mode))
        else:
            print("{0} faild".format(switch_mode))
        pass

    def LTE_ch_travel(self, test_list, mea_item =("aclr",) ):
        md = "LTE"
        total_res = {}
        for item in mea_item:
            total_res[item]=[]
        try:
            for dest_state in test_list:
                self.LTE_ch_redirection(dest_state)
                # dest_DD = "FDD" if int(dest_state.BAND[2:])<33 else "TDD"
                for i in range(3):
                    try :
                        # temp = self.LTE_acquire_meas(mea_item=mea_item,test_DD = dest_DD)
                        temp = self.LTE_acquire_meas(mea_item=mea_item)
                        break
                    except ConnectionError as e:
                        if not self.LWG_check_connection(md="LTE"):
                            self.instr_write("ROUTe:LTE:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
                            # self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel -80")
                            self.LWG_set_dl_pwr(md="LTE",pwr=-80)
                            self.LWG_disconnect_off(md="LTE", state_on=True)
                            self.LWG_connect(md="LTE")

                for item in temp.keys():
                    total_res[item].append(dest_state+temp[item])
                print("")
        finally:
            self.LTE_data_output(total_res,config[md]['data_save'])
            print(total_res)

    def LTE_acquire_meas(self, mea_item = None):
        md = "LTE"

        output_res = {}
        if not mea_item:
            mea_item = ("aclr",)
        if not self.LWG_check_connection(md):
            print("{md} not connected".format(md=md))
            self.LWG_connect(md)
        if "aclr" in mea_item:
            output_res["aclr"]=self.LTE_meas_aclr()
        if "sensm" in mea_item:
            output_res["sensm"]=self.LTE_meas_sense(route_path="main")
        if "sensd" in mea_item:
            output_res["sensd"]=self.LTE_meas_sense(route_path="div")
        return output_res

    def LTE_meas_aclr(self):
        test_DD = self.instr_query("CONFigure:LTE:SIGN:DMODe?").strip()
        if test_DD == "FDD":
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MSUBframes 0,10,0")
        else:
            self.instr_write("CONFigure:LTE:MEAS:MEValuation:MSUBframes 2,10,0")

        self.LTE_set_ul_pwr(pwr="MAX")
        time.sleep(1)
        self.instr_write("INITiate:LTE:MEAS:MEValuation")
        while self.instr_query("FETCh:LTE:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:LTE:MEAS:MEValuation:ACLR:AVERage?").strip().split(",")
        res = tuple(round(float(res[i]),2) for i in [2,3,4,5,6] )
        print(res)
        return res

    def LTE_meas_sense(self,route_path="main"):
        md = "LTE"
        self.instr_write("CONFigure:LTE:SIGN:EBLer:REPetition SING")
        self.instr_write("CONFigure:LTE:SIGN:EBLer:SCONdition NONE")

        self.LWG_set_dl_pwr(md)
        self.LTE_set_ul_pwr(pwr="MAX")
        if route_path == "div":
            self.LWG_set_port_route(md,"div")
            time.sleep(2)
        
        pwr, ber = self.LWG_sense_alg(md)
        
        self.LWG_set_dl_pwr(md)
        if route_path == "div":
            self.LWG_set_port_route(md,"main")
            time.sleep(2)
        print("sense {rp} : {pwr}, {ber}".format(rp=route_path, pwr=pwr, ber= ber))
        time.sleep(1)
        return (pwr, ber)

    def LTE_meas_sense_cell(self,down_level, frame=1000, output_pwr_format="RS_EPRE"):
        # self.instr_write("CONFigure:LTE:SIGN:DL:RSEPre:LEVel {0}".format(down_level))
        self.LWG_set_dl_pwr(md="LTE", pwr=down_level)
        self.instr_write("CONFigure:LTE:SIGN:EBLer:SFRames {frame}".format(frame=frame))
        self.instr_write("INITiate:LTE:SIGN:EBLer")
        while self.instr_query("FETCh:LTE:SIGN:EBL:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res =self.instr_query("FETCh:LTE:SIGN:EBLer:RELative?").strip().split(",")

        if int(res[0])==0:
            ber = round(100-float(res[1]),2)
            if output_pwr_format=="RS_EPRE":
                return down_level, ber
            elif output_pwr_format=="cell_power":
                cell_pwr = round(float(self.instr_query("SENSe:LTE:SIGN:DL:FCPower?")),2)
                return cell_pwr, ber
        else: 
            raise ConnectionError

    def LTE_set_ul_pwr(self, pwr="MAX"):
        if pwr == "MAX":
            self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET MAXPower")
        elif isinstance(pwr, (int,float)):
            self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:CLTPower {pwr}".format(pwr=pwr))
            self.instr_write("CONFigure:LTE:SIGN:UL:PUSCh:TPC:SET CLOop")
            
    def LTE_get_state(self):
        band = self.instr_query("CONFigure:LTE:SIGN:PCC:BAND?").strip()
        ch_ul = self.instr_query("CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:UL?").strip()
        ch_dl = self.instr_query("CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:DL?").strip()
        bw = self.instr_query("CONFigure:LTE:SIGN:CELL:BANDwidth:DL?").strip()
        # float(dl_level)
        # dl_level = self.instr_query("CONFigure:LTE:SIGN:DL:RSEPre:LEVel?").strip()
        return ue_struct_l(band, int(ch_ul),int(ch_dl), bw)

    def LTE_data_output(self, output_result, fp):
        with open(fp, 'w') as f:
        # output_result, aclr, sense
            if "aclr" in output_result:
                f.write("BAND\tUL_Ch\tBW\tUTRA\tEUTRA\tPWR\tEUTRA\tUTRA\n")
                for line in output_result["aclr"]:
                    f.write(str(str_ue_info_LTE(line[:4])))
                    f.write("\t")
                    f.write("\t".join(map(str,line[4:])))
                    f.write("\n")
            # set_sens = list(set(["sensm","sensd"]) & set([output_result.keys()]))
            set_sens = [item for item in ["sensm","sensd"] if item in output_result]
            if set_sens:
                f.write("BAND\tUL_Ch\tBW\t{0}\n".format("\t".join(set_sens)))
                for i in range(len(output_result[set_sens[0]])):
                    f.write(str(str_ue_info_LTE(output_result[set_sens[0]][i][:4])))
                    for item in set_sens:
                        f.write("\t{0}".format(output_result[item][i][4]))
                    f.write("\n")

    def LWG_sense_alg(self,md="LTE"):
        pwr_init = SENSE_PARAM[md]['pwr_init']
        pwr_coarse = SENSE_PARAM[md]['pwr_coarse']
        pwr_fine = SENSE_PARAM[md]['pwr_fine']
        frame_coarse = SENSE_PARAM[md]['frame_coarse']
        frame_fine = SENSE_PARAM[md]['frame_fine']
        BER_THRESHOLD = SENSE_PARAM[md]['BER_THRESHOLD']
        if md == "LTE":
            meas_func = self.LTE_meas_sense_cell
        elif md == "WCDMA":
            meas_func = self.WCDMA_meas_sense_cell
        elif md == "GSM":
            meas_func = self.GSM_meas_sense_cell

        # init, coarse, pwr_back, fine, pwr_back_fine, end
        EBL_state = "init"
        while EBL_state != "end":
            # try:
            if EBL_state == "init":
                pwr, ber = meas_func(pwr_init,frame=frame_coarse)
                if ber < BER_THRESHOLD:
                    EBL_state = "coarse"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "coarse":
                pwr = pwr - pwr_coarse
                if ber != 0:
                    pwr = pwr+0.4*pwr_coarse
                pwr, ber = meas_func(pwr,frame=frame_coarse)
                if ber < BER_THRESHOLD:
                    EBL_state = "coarse"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "pwr_back":
                pwr = pwr + pwr_coarse
                pwr, ber = meas_func(pwr,frame=frame_coarse)
                if ber < BER_THRESHOLD:
                    EBL_state = "fine"
                else:
                    EBL_state = "pwr_back"
            elif EBL_state == "fine" :
                pwr = pwr - pwr_fine
                pwr, ber = meas_func(pwr,frame=frame_fine)
                if ber < BER_THRESHOLD:
                    EBL_state = "fine"
                else:
                    EBL_state = "pwr_back_fine"
            elif EBL_state == "pwr_back_fine":
                pwr = pwr + pwr_fine
                pwr, ber = meas_func(pwr,frame=frame_fine)
                if ber < BER_THRESHOLD:
                    EBL_state = "end"
                else:
                    EBL_state = "pwr_back_fine"
            print("\r{0}, {1}, {2}".format(round(pwr,2), ber, EBL_state),end="")
            # except TypeError as e:
                # print("BER test error, NoneType receive")
        print("")
        if md == "LTE":
            pwr = float(self.instr_query("SENSe:LTE:SIGN:DL:FCPower?"))
        return (round(pwr,1), round(ber,2))

    def WCDMA_para_configure(self, test_list = None):
        if test_list is None:
            test_list = (("OB1", 9612, 10562),)

        if self.LWG_check_connection(md = "WCDMA"):
            self.WCDMA_ch_redirection(test_list[0])
        else:
            self.instr_reset_cmw()
            self.set_FDCorrection(param_FDCorrection)
            self.instr_write("SOURce:WCDMa:SIGN:CELL:STATe OFF")
            self.instr_write("CONFigure:WCDMa:SIGN:CARRier:BAND {0}".format(test_list[0][0]))
            self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL {0}".format(test_list[0][1]))
            self.instr_write("CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:TMODe MODE2")
        self.instr_write("ROUTe:WCDMa:MEAS:SCENario:CSPath 'WCDMA Sig1'")
        self.instr_write("SOURce:WCDMa:SIGN:CELL:STATe ON")
        while self.instr_query("SOUR:WCDM:SIGN:CELL:STAT:ALL?").strip()!="ON,ADJ":
            time.sleep(1)
        print("Cell initialling done")

        self.instr_write("CONFigure:WCDMa:MEAS:MEValuation:REPetition SINGleshot")
        self.instr_write("CONFigure:WCDMa:MEAS:MEValuation:SCOunt:SPECtrum 10")
        self.instr_write("CONFigure:WCDMa:MEAS:MEValuation:SCOunt:MODulation 10")
        self.WCDMA_set_ul_pwr(pwr="MAX")
        # self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")

    def WCDMA_ch_travel(self, test_list,mea_item=("aclr",)):
        md = "WCDMA"
        total_res = {}
        for item in mea_item:
            total_res[item]=[]
        try:
            for dest_state in test_list:
                self.WCDMA_ch_redirection(dest_state)

                for i in range(3):
                    try:
                        temp = self.WCDMA_acquire_meas(mea_item = mea_item)
                        break
                        # for item in mea_item:
                    except ConnectionError as e:
                        if not self.LWG_check_connection(md):
                            self.instr_write("ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1")
                            # self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower -56.1")
                            self.LWG_set_dl_pwr(md="WCDMA",pwr=-56.1)
                            self.LWG_disconnect_off(md, state_on=True)
                            self.LWG_connect(md)
                for item in temp.keys():
                    total_res[item].append(dest_state+temp[item])
                print("")
        finally:
            self.WCDMA_data_output(total_res,config['WCDMA']['data_save'])
            print(total_res)

    def WCDMA_data_output(self, output_result, fp ):
        with open(fp, 'w') as f:
            if "aclr" in output_result:
                f.write("BAND\tUL_Ch\tACLR_l2\tACLR_l1\tPWR\tACLR_r1\tACLR_r2\n")
                for line in output_result["aclr"]:
                    f.write(str(str_ue_info_WCDMA(line[:3])))
                    f.write("\t")
                    f.write("\t".join(map(str,line[3:])))
                    f.write("\n")
            if "sensm" in output_result:
                f.write("BAND\tUL_Ch\tsensm\n")
                for line in output_result["sensm"]:
                    f.write(str(str_ue_info_WCDMA(line[:3])))
                    f.write("\t")
                    f.write(str(line[3]))
                    f.write("\n")
            if "sensd" in output_result:
                f.write("BAND\tUL_Ch\tsensd\n")
                for line in output_result["sensd"]:
                    f.write(str(str_ue_info_WCDMA(line[:3])))
                    f.write("\t{0}".format(line[3]))
                    f.write("\n")

    def WCDMA_acquire_meas(self, mea_item=None):
        output_res = {}
        if not mea_item:
            mea_item = ("aclr",)
        if not self.LWG_check_connection(md="WCDMA"):
            print("Not connected")
            self.LWG_connect(md="WCDMA")

        if "aclr" in mea_item:
            output_res["aclr"] = self.WCDMA_meas_aclr()
        if "sensm" in mea_item:
            output_res["sensm"] = self.WCDMA_meas_sense(route_path="main")
        if "sensd" in mea_item:
            ue_info_w = self.WCDMA_get_state()
            if int(ue_info_w.w_BAND[2:]) in config['WCDMA']['div-support']:
                output_res["sensd"] = self.WCDMA_meas_sense(route_path="div")
        return output_res
        pass

    def WCDMA_meas_aclr(self):
        # self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
        self.WCDMA_set_ul_pwr(pwr="MAX")
        self.instr_write("INITiate:WCDMa:MEAS:MEValuation")
        while self.instr_query("FETCh:WCDMa:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:WCDMa:MEAS:MEValuation:SPECtrum:AVERage? RELative").split(",")
        res = tuple(round(float(res[i]),2) for i in [2,3,15,4,5] )
        print(res)
        return res

    def WCDMA_meas_sense(self, route_path="main"):
        md = "WCDMA"
        self.instr_write("CONFigure:WCDMa:SIGN:BER:SCONdition None")
        self.instr_write("CONFigure:WCDMa:SIGN:BER:REPetition SINGleshot")

        self.LWG_set_dl_pwr(md)
        self.WCDMA_set_ul_pwr(pwr="MAX")
        if route_path == "div":
            self.LWG_set_port_route(md, "div")
            time.sleep(2)

        pwr,ber = self.LWG_sense_alg(md = "WCDMA")

        self.LWG_set_dl_pwr(md)
        if route_path == "div":
            self.LWG_set_port_route(md, "main")
            time.sleep(2)
        print("sense {rp} : {pwr}, {ber}".format(rp=route_path, pwr=pwr, ber= ber))
        time.sleep(1)
        return (pwr, ber)

    def WCDMA_meas_sense_cell(self, down_level, frame = 100):
        self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower {0}".format(down_level))
        self.instr_write("CONFigure:WCDMa:SIGN:BER:TBLocks {0}".format(frame))
        time.sleep(1)
        self.instr_write("INITiate:WCDMa:SIGN:BER")
        while self.instr_query("FETCh:WCDMa:SIGN:BER:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:WCDMa:SIGN:BER?").split(",")
        if int(res[0]) == 0:
            return (down_level, round(float(res[1]),2))
        else:
            raise ConnectionError

    def WCDMA_ch_redirection(self,dest_state):
        self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:COPower -56.10")
        last_state = self.WCDMA_get_state()
        print("try redrection to {0}".format(dest_state))
        if last_state.w_BAND == dest_state.w_BAND:
            if last_state.w_CH_UL != dest_state.w_CH_UL:
                self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL {ch_ul}".format(ch_ul=dest_state.w_CH_UL))
                time.sleep(6)
        else:
            self.instr_write("CONFigure:WCDMa:SIGN:CARRier:BAND {band}".format(band=dest_state.w_BAND))
            time.sleep(8)
            self.instr_write("CONFigure:WCDMa:SIGN:RFSettings:CARRier:CHANnel:UL {ch_ul}".format(ch_ul=dest_state.w_CH_UL))
            time.sleep(6)
        if self.LWG_check_connection(md="WCDMA"):
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
        return ue_struct_w(band, int(ch_ul), int(ch_dl))

    def WCDMA_set_ul_pwr(self, pwr="MAX"):
        if pwr == "MAX":
            self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL1")
        elif pwr == "MIN":
            self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET ALL0")
        elif isinstance(pwr, (int,float)):
            self.instr_write("CONFigure:WCDMa:SIGN:UL:CARRier:TPC:TPOWer {pwr}".format(pwr=pwr))
            self.instr_write("CONFigure:WCDMa:SIGN:UL:TPC:SET CLOop")
        pass

    def GSM_data_output(self, output_result, fp):
        with open(fp, 'w') as f:
            if "switch_spetrum" in output_result:
                f.write("BAND\tCH\t-400KHz\tPWR\t+400KHz\n")
                for line in output_result["switch_spetrum"]:
                    f.write(str(str_ue_info_GSM(line[:2])))
                    f.write("\t")
                    f.write("\t".join(map(str,line[2:])))
                    f.write("\n")
            if "sensm" in output_result:
                f.write("BAND\tCH\tsensm\n")
                for line in output_result["sensm"]:
                    f.write(str(str_ue_info_GSM(line[:2])))
                    f.write("\t")
                    f.write(str(line[2]))
                    f.write("\n")
            if "sensd" in output_result:
                f.write("BAND\tCH\tsensd\n")
                for line in output_result["sensd"]:
                    f.write(str(str_ue_info_GSM(line[:2])))
                    f.write("\t{0}".format(line[2]))
                    f.write("\n")

    def LWG_data_output(self, md, output_result, fp):
        with open(fp, 'w') as f:
            ue_info = eval("str_ue_info_"+md)
            for i,t in test_item_map[md].items():
                if t[0] in output_result:
                    f.write("{0}\n".format("\t".join(t[1])))
                    for line in output_result[t[0]]:
                        f.write("{0!s}".format(ue_info(line[:ue_info.para_num])))
                        f.write("\t{0}\n".format("\t".join(map(str,line[ue_info.para_num:]))))
        pass
    
    def GSM_set_ul_pwr(self,pwr="MAX"):
        if pwr == "MAX":
            present_state = self.GSM_get_state()    
            pcl = 5 if present_state.g_BAND in ("G085","G09") else 0
            self.instr_write("CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched {pcl}".format(pcl = pcl))
        elif isinstance(pwr, int):
            self.instr_write("CONFigure:GSM:SIGN:RFSettings:PCL:TCH:CSWitched {pcl}".format(pcl = pwr))

    def GSM_para_configure(self, test_list=None):
        def GSM_MEA_configure():
            self.instr_write("CONFigure:GSM:MEAS:MEValuation:REPetition SINGleshot")
            self.instr_write("CONF:GSM:MEAS:MEV:SCO:MOD 10")
            self.instr_write("CONF:GSM:MEAS:MEV:SCO:SSW 10")
            self.instr_write("CONF:GSM:MEAS:MEV:SCO:SMOD 10")

        md = "GSM"
        if self.LWG_check_connection(md):
            self.LWG_set_dl_pwr(md, pwr=-80)
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
        self.GSM_set_ul_pwr(pwr = "MAX")

    def GSM_acquire_meas(self,mea_item=None):
        md = "GSM"
        output_res = {}
        if not mea_item:
            mea_item = ("switch_spetrum",)
        if not self.LWG_check_connection(md):
            print("{md} not connected".format(md=md))
            self.LWG_connect(md)

        if "switch_spetrum" in mea_item:
            output_res["switch_spetrum"]=self.GSM_meas_ssw()
        if "sensm" in mea_item:
            output_res["sensm"]=self.GSM_meas_sense(route_path = "main")
        if "sensd" in mea_item:
            ue_info_g = self.GSM_get_state()
            # TODO
            if ue_info_g.g_BAND in [gsm_band_map[i][0] for i in config['GSM']['div-support']]:
                output_res["sensd"]=self.GSM_meas_sense(route_path="div")
        return output_res

    def GSM_meas_sense(self, route_path = "main"):
        md = "GSM"
        self.instr_write("CONFigure:GSM:SIGN:BER:CSWitched:SCONdition NONE")
        self.instr_write("CONFigure:GSM:SIGN:BER:CSWitched:MMODe BBBurst")

        self.LWG_set_dl_pwr(md)
        self.GSM_set_ul_pwr(pwr="MAX")

        if route_path == "div":
            self.LWG_set_port_route(md,"div")
            time.sleep(2)

        pwr, ber = self.LWG_sense_alg(md)

        print("rscp is {0}".format(self.LWG_get_RSRP(md)))

        self.LWG_set_dl_pwr(md)
        if route_path == "div":
            self.LWG_set_port_route(md,"main")
            time.sleep(2)

        self.instr_write("ABORt:GSM:SIGN:BER:CSWitched")
        while self.instr_query("FETCh:GSM:SIGN:BER:CSWitched:STATe?").strip() != "OFF":
            time.sleep(1)

        print("sense {rp} : {pwr}, {ber}".format(rp=route_path, pwr=pwr, ber= ber))
        time.sleep(1)
        return (pwr, ber)

    def GSM_meas_sense_cell(self, down_level, frame=100):
        md = "GSM"
        self.LWG_set_dl_pwr(md, pwr = down_level)
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

    def GSM_meas_ssw(self):
        self.GSM_set_ul_pwr(pwr="MAX")
        time.sleep(1)
        self.instr_write("INITiate:GSM:MEAS:MEValuation")
        while self.instr_query("FETCh:GSM:MEAS:MEValuation:STATe:ALL?").strip() != "RDY,ADJ,INV":
            time.sleep(1)
        res = self.instr_query("FETCh:GSM:MEAS:MEValuation:SSWitching:FREQuency?").strip().split(",")
        res = tuple(round(float(res[i]),2) for i in [20,21,22] )
        print(res)
        return res
    
    def GSM_get_state(self):
        g_ch = self.instr_query("CONFigure:GSM:SIGN:RFSettings:CHANnel:TCH?").strip()
        g_band = self.instr_query("SENSe:GSM:SIGN:BAND:TCH?").strip()
        return ue_struct_g(g_band, int(g_ch))

    def GSM_ch_travel(self, test_list, mea_item = ("switch_spetrum", )):
        md = "GSM"
        total_res = {}
        for item in mea_item:
            total_res[item]=[]
        try:
            for dest_state in test_list:
                self.GSM_ch_redirection(dest_state)
                temp=self.GSM_acquire_meas(mea_item = mea_item)
                for item in temp.keys():
                    total_res[item].append(dest_state+temp[item])
                print("")
        finally:
            self.GSM_data_output(total_res,config[md]['data_save'])
            print(total_res)

    def GSM_ch_redirection(self, dest_state):
        last_state = self.GSM_get_state()
        print("try redrection to {0}".format(dest_state))
        if last_state.g_BAND == dest_state.g_BAND:
            self.instr_write("CONFigure:GSM:SIGN:RFSettings:CHANnel:TCH {ch}".format(ch=dest_state.g_CH))
            time.sleep(2)
        else:
            if last_state.g_BAND != "G19" and dest_state.g_BAND != "G19" and config['GSM']['switch_type']:
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
                self.LWG_disconnect_off(md="GSM", state_on=False)
                print("phone reboot")
                self.phone_hd.adb_reboot()
                self.GSM_para_configure((dest_state,))

                time.sleep(PHONE_REBOOT_TIME)
                self.LWG_connect(md="GSM")
                pass

        for i in range(10):
            if self.LWG_check_connection():
                break
            time.sleep(1)
        present_state = self.GSM_get_state()
        if present_state == dest_state:
            print("redirection successful")
        else :
            print("redirection failed")

    def test(self, md):
        self.set_FDCorrection(param_FDCorrection)
        getattr(self,md+"_para_configure")(TEST_LIST[md])
        self.LWG_connect(md)
        mea_item = [test_item_map[md][i][0] for i in config[md]['test_item']]
        # getattr(self,md+"_ch_travel")(TEST_LIST[md],mea_item=mea_item)
        self.LWG_ch_travel(md , TEST_LIST[md], mea_item)


if __name__ == '__main__':
    # rm = visa.ResourceManager()
    # instr = rm.open_resource("TCPIP0::10.237.70.10::inst0::INSTR")
    try:
        time_start = time.time()
        phone = adb()
        # phone.adb_reboot()

        rm = RM_CMW()
        if "dev_ip" in config:
            m = handle_instr(rm.open_resource("TCPIP0::{0}::inst0::INSTR".format(config["dev_ip"])), phone)
        elif "gpib" in config:
            m = handle_instr(rm.open_resource("GPIB0::{0}::INSTR".format(config["gpib"])))
        else:
            m = None
        if m:
            print(m.get_instr_version())
            m.set_remote_display(state=True)

            for i, v in enumerate(config.get('TEST_RF', ())):
                md = standard_map[v]
                m.test(md)
                if i+1 < len(config['TEST_RF']) :
                    if config['TEST_RF'][i] != config['TEST_RF'][i+1]:
                        m.LWG_disconnect_off(md,state_on=False)
            m.instr_close()
        rm.close()
    finally:
        time_end = time.time()
        print("time elaped {0}:{1}".format(int(time_end-time_start)//60, int(time_end-time_start)%60))
