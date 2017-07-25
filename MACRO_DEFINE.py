#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple

ue_struct_l = namedtuple("ue_struct_l",['BAND','CH_UL','CH_DL','BW'])
ue_struct_w = namedtuple("ue_struct_w",['BAND','CH_UL','CH_DL'])
ue_struct_g = namedtuple("ue_struct_g",['g_BAND','g_CH'])
ue_struct_t = namedtuple("ue_struct_t",['BAND','CH_UL'])

LTE_BW_5="B050"
LTE_BW_10="B100"
LTE_BW_20="B200"

# "bw" or "band"
LTE_TEST_PRIORITY = "bw"
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

class lte_band_cmw():
    def __init__(self, band_name, dl_ul_offset, bw_lmh_ul):
        self.band = band_name
        self.dl_ul_offset = dl_ul_offset
        self.bw_lmh_ul=bw_lmh_ul
    
    def lte_ch_ul2dl(self, channel_num):
        return channel_num-self.dl_ul_offset[1]+self.dl_ul_offset[0]
    
    def lte_ch_dl2ul(self, channel_num):
        return channel_num+self.dl_ul_offset[1]-self.dl_ul_offset[0]

lte_b1 = lte_band_cmw(
    "OB1",[0   ,18000], {
        LTE_BW_10:(18050,18300,18550),
        LTE_BW_20:(18100,18300,18500),
        LTE_BW_5 :(18025,18300,18575)
    }
)
lte_b3 = lte_band_cmw(
    "OB3",[1200,19200], {
        LTE_BW_10:(19250,19575,19900), 
        LTE_BW_20:(19300,19575,19850),
        LTE_BW_5 :(19225,19575,19925)
    }
)
lte_b4 = lte_band_cmw(
    "OB4",[1950,19950], {
        LTE_BW_10:(20000,20175,20350), 
        LTE_BW_20:(20050,20175,20300), 
        LTE_BW_5 :(19975,20175,20375), 
    }
)
lte_b5 = lte_band_cmw(
    "OB5",[2400,20400], {
        LTE_BW_10:(20450,20525,20600)
    }
)
lte_b7 = lte_band_cmw(
    "OB7",[2750,20750], {
        LTE_BW_10:(20800,21100,21400), 
        LTE_BW_20:(20850,21100,21350)
    }
)
lte_b8 = lte_band_cmw(
    "OB8",[3450,21450], {
        LTE_BW_10:(21500,21625,21750)
    }
)
lte_b12 = lte_band_cmw(
    "OB12",[5010,23010], {
        LTE_BW_10:(23060, 23095, 23130)
    }
)
lte_b20 = lte_band_cmw(
    "OB20",[6150,24150], {
        LTE_BW_10:(24200, 24300, 24400)
    }
)
lte_b34 = lte_band_cmw(
    "OB34",[2010,2010], {
        LTE_BW_10:(36250, 36275, 36300)
    }
)
lte_b38 = lte_band_cmw(
    "OB38",[37750,37750], {
        LTE_BW_10:(37800,38000,38200), 
        LTE_BW_20:(37850,38000,38150)
    }
)
lte_b39 = lte_band_cmw(
    "OB39",[38250,38250], {
        LTE_BW_10:(38300,38450,38600), 
        LTE_BW_20:(38350,38450,38550)
    }
)
lte_b40 = lte_band_cmw(
    "OB40",[38650,38650], {
        LTE_BW_10:(38700,39150,39600), 
        LTE_BW_20:(38750,39150,39550)
    }
)
lte_b41_n = lte_band_cmw(
    "OB41",[40240,40240], {
        LTE_BW_10:(40290,40740,41190), 
        LTE_BW_20:(40340,40740,41140)
    }
)
lte_b41_w = lte_band_cmw(
    "OB41",[39650,39650], {
        LTE_BW_10:(39700,40620,41540), 
        LTE_BW_20:(39750,40620,41490)
    }
)

# "md"表示主+分都有，"m"表示只有主集
w_b1 = ("OB1", [9612, 9750, 9888],[10562,10700,10838])
w_b2 = ("OB2", [9262, 9400, 9538],[9662, 9800, 9938])
w_b5 = ("OB5", [4132, 4183, 4233],[4357,4408,4458])
w_b8 = ("OB8", [2712, 2788, 2863],[2937,3013,3088])

g_085 = ("G085", [128,192,251])
g_09  = ("G09",  [975,62,124])
g_18  = ("G18",  [512,698,885])
g_19  = ("G19",  [512,661,810])

t_f = ("B1", [9404, 9500, 9596]) # B39 1900
t_a = ("B2", [10054, 10087, 10121]) # B34 2100

standard_map = {
    1   :   "LTE",
    2   :   "WCDMA",
    3   :   "GSM",
    4   :   "TDSC",
}

lte_bw_map = (LTE_BW_5,LTE_BW_10,LTE_BW_20)
lte_band_map = {
    1   :   lte_b1,
    3   :   lte_b3,
    4   :   lte_b4,
    5   :   lte_b5,
    7   :   lte_b7,
    8   :   lte_b8,
    12  :   lte_b12,
    20  :   lte_b20,
    34  :   lte_b34,
    38  :   lte_b38,
    39  :   lte_b39,
    40  :   lte_b40,
    41  :   lte_b41_n,
}
wt_band_map = {
    1   :   w_b1,
    2   :   w_b2,
    5   :   w_b5,
    8   :   w_b8,
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
        2   :   ( "sensm",["BAND","UL_Ch","BW","sensm"] ),
        3   :   ( "sensd",["BAND","UL_Ch","BW","sensd"] ),
    },
    "WCDMA" :{
        1   :   ( "aclr", ["BAND","UL_Ch","ACLR_l2","ACLR_l1","PWR","ACLR_r1","ACLR_r2"]),
        2   :   ( "sensm",["BAND","UL_Ch","sensm"] ),
        3   :   ( "sensd",["BAND","UL_Ch","sensd"] ),
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
