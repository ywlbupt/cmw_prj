#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple

LTE_BW_1P4 = "B014"
LTE_BW_3 = "B030"
LTE_BW_5="B050"
LTE_BW_10="B100"
LTE_BW_15="B150"
LTE_BW_20="B200"

ue_struct_l = namedtuple("ue_struct_l",['BAND','CH_UL','CH_DL','BW'])
ue_struct_w = namedtuple("ue_struct_w",['BAND','CH_UL','CH_DL'])
ue_struct_g = namedtuple("ue_struct_g",['g_BAND','g_CH'])
ue_struct_t = namedtuple("ue_struct_t",['BAND','CH_UL'])

# "bw" or "band" or "usr_define"，LTE测试以BW优先，例如先测完10MHz再转5MHz
LTE_TEST_PRIORITY = "band"
# LTE_TEST_PRIORITY = "bw"
# 手机预估的重启时间
PHONE_REBOOT_TIME = 60

class str_ue_info_LTE():
    para_num = 4
    def __init__(self, ue_struct_):
        self.BAND=ue_struct_[0]
        self.CH_UL=ue_struct_[1]
        self.CH_DL=ue_struct_[2]
        self.BW=ue_struct_[3]

    def __str__(self):
        return "B{band:0>2}\t{ch_ul:5}\t{bw:d}MHz".format(band=self.BAND[2:],ch_ul=self.CH_UL,bw=int(int(self.BW[1:])/10))

class str_ue_info_WCDMA():
    para_num = 3
    def __init__(self, ue_struct_):
        self.BAND=ue_struct_[0]
        self.CH_UL=ue_struct_[1]
        self.CH_DL=ue_struct_[2]

    def __str__(self):
        return "WB{band:0>2}\t{ch_ul:5}".format(band=self.BAND[2:],ch_ul=self.CH_UL)

class str_ue_info_GSM():
    para_num = 2
    def __init__(self, ue_struct_):
        self.BAND=ue_struct_[0]
        self.CH=ue_struct_[1]

    def __str__(self):
        band_map = { "G085":"GSM850", "G09":"GSM900","G18":"DCS","G19":"PCS",}
        return "{band:7}\t{ch:5}".format(band=band_map[self.BAND],ch=self.CH)

class str_ue_info_TDSC():
    para_num = 2
    def __init__(self, ue_struct_):
        self.BAND=ue_struct_[0]
        self.CH=ue_struct_[1]

    def __str__(self):
        band_map = { "B1":"TDS-A", "B2":"TDS-F"}
        return "{band:7}\t{ch:5}".format(band=band_map[self.BAND],ch=self.CH)

# "md"表示主+分都有，"m"表示只有主集
w_b1 = ("OB1", [9612, 9750, 9888],[10562,10700,10838])
w_b2 = ("OB2", [9262, 9400, 9538],[9662, 9800, 9938])
w_b3 = ("OB3", [937, 1113, 1288],[1162, 1338, 1513])
w_b4 = ("OB4", [1312, 1413, 1513],[1537, 1638, 1738])
w_b5 = ("OB5", [4132, 4183, 4233],[4357,4408,4458])
w_b6 = ("OB6", [4162, 4175, 4188],[4387,4400,4413])
w_b8 = ("OB8", [2712, 2788, 2863],[2937,3013,3088])
w_b9 = ("OB9", [8762, 8837, 8912],[9237,9312,9387])
w_b19 = ("OB19", [312, 338, 363],[712,738,763])

g_085 = ("G085", [128,192,251])
g_09  = ("G09",  [975,62,124])
g_18  = ("G18",  [512,698,885])
g_19  = ("G19",  [512,661,810])

t_f = ("B1", [9404, 9500, 9596]) # B39 1900
t_a = ("B2", [10054, 10087, 10121]) # B34 2100

lte_bw_map = (LTE_BW_5,LTE_BW_10,LTE_BW_20)

standard_map = {
    1   :   "LTE",
    2   :   "WCDMA",
    3   :   "GSM",
    4   :   "TDSC",
}

wt_band_map = {
    1   :   w_b1,
    2   :   w_b2,
    3   :   w_b3,
    4   :   w_b4,
    5   :   w_b5,
    6   :   w_b6,
    8   :   w_b8,
    9   :   w_b9,
    19   :   w_b19,
    34  :   t_a,
    39  :   t_f,
}
gsm_band_map = {
    5   :   g_085,
    8   :   g_09,
    3   :   g_18,
    2   :   g_19,
}

test_item_map = {
    "LTE"   :{
        1   :   ( "aclr", ["BAND","UL_Ch","BW","UTRA","EUTRA","PWR","EUTRA","UTRA"]),
        2   :   ( "sensm_max",["BAND","UL_Ch","BW","sensm_max"] ),
        3   :   ( "sensd",["BAND","UL_Ch","BW","sensd"] ),
        4   :   ( "sensm_cloop",["BAND","UL_Ch","BW","sensm_cloop"] ),
    },
    "WCDMA" :{
        1   :   ( "aclr", ["BAND","UL_Ch","ACLR_l2","ACLR_l1","PWR","ACLR_r1","ACLR_r2"]),
        2   :   ( "sensm_max",["BAND","UL_Ch","sensm_max"] ),
        3   :   ( "sensd",["BAND","UL_Ch","sensd"] ),
        4   :   ( "sensm_cloop",["BAND","UL_Ch","sensm_cloop"] ),
    },
    "TDSC" :{
        1   :   ( "aclr", ["BAND","UL_Ch","ACLR_l2","ACLR_l1","PWR","ACLR_r1","ACLR_r2"]),
        2   :   ( "sensm",["BAND","UL_Ch","sensm"] ),
        3   :   ( "sensd",["BAND","UL_Ch","sensd"] ),
    },
    "GSM"   :{
        1   :   ( "switch_spetrum", ["BAND","CH","-400KHz","PWR","+400KHz"] ),
        2   :   ( "sensm",          ["BAND","CH","sensm"] ),
        3   :   ( "sensd",          ["BAND","CH","sensd"] ),
    },
}

