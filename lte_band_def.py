#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from MACRO_DEFINE import LTE_BW_1P4
from MACRO_DEFINE import LTE_BW_3
from MACRO_DEFINE import LTE_BW_5
from MACRO_DEFINE import LTE_BW_10
from MACRO_DEFINE import LTE_BW_15
from MACRO_DEFINE import LTE_BW_20

LTE_BW_MAP = namedtuple("LTE_BW_MAP", [LTE_BW_1P4, LTE_BW_3, LTE_BW_5, 
                                       LTE_BW_10, LTE_BW_15, LTE_BW_20])

# 1p4, 3, 5, 10, 15, 20
LTE_BW_SUPPORT = {
    1:  LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    2:  LTE_BW_MAP(1, 1, 1, 1, 1, 1),
    3:  LTE_BW_MAP(1, 1, 1, 1, 1, 1),
    4:  LTE_BW_MAP(1, 1, 1, 1, 1, 1),
    5:  LTE_BW_MAP(1, 1, 1, 1, 0, 0),
    6:  LTE_BW_MAP(0, 0, 1, 1, 0, 0),
    7:  LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    8:  LTE_BW_MAP(1, 1, 1, 1, 0, 0),
    9:  LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    10: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    11: LTE_BW_MAP(0, 0, 1, 1, 0, 0),
    12: LTE_BW_MAP(1, 1, 1, 1, 0, 0),
    13: LTE_BW_MAP(0, 0, 1, 1, 0, 0),
    14: LTE_BW_MAP(0, 0, 1, 1, 0, 0),
    17: LTE_BW_MAP(0, 0, 1, 1, 0, 0),
    18: LTE_BW_MAP(0, 0, 1, 1, 1, 0),
    19: LTE_BW_MAP(0, 0, 1, 1, 1, 0),
    20: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    21: LTE_BW_MAP(0, 0, 1, 1, 1, 0),
    22: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    23: LTE_BW_MAP(1, 1, 1, 1, 1, 1),
    24: LTE_BW_MAP(0, 0, 1, 1, 0, 0),
    25: LTE_BW_MAP(1, 1, 1, 1, 1, 1),
    26: LTE_BW_MAP(1, 1, 1, 1, 1, 0),
    27: LTE_BW_MAP(1, 1, 1, 1, 0, 0),
    28: LTE_BW_MAP(0, 1, 1, 1, 1, 1),
    30: LTE_BW_MAP(0, 0, 1, 1, 0, 0),
    33: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    34: LTE_BW_MAP(0, 0, 1, 1, 1, 0),
    35: LTE_BW_MAP(1, 1, 1, 1, 1, 1),
    36: LTE_BW_MAP(1, 1, 1, 1, 1, 1),
    37: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    38: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    39: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    40: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    41: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    42: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    43: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    44: LTE_BW_MAP(0, 1, 1, 1, 1, 1),
    45: LTE_BW_MAP(0, 0, 1, 1, 1, 1),
    66: LTE_BW_MAP(1, 1, 1, 1, 1, 1),
}

# 2DL_CA_Contiguous without ULCA
# 100+25, 100+50, 75+75, 100+75, 100+100
# ul_configuration of full RB
LTE_2DLCA_Intra_Congtiguous = {
    "1C" : (0, 0, 1, 0, 1),
    "3C" : (1, 1, 0, 1, 1),
    "7C" : (0, 0, 1, 0, 1),
    "38C" : (0, 0, 1, 0, 1),
    "39C" : (1, 1, 0, 1, 0),
    "40C" : (0, 1, 1, 1, 1),
    "41C" : (0, 1, 1, 1, 1),
    "42C" : (1, 1, 0, 1, 1),
    "66C" : (1, 1, 1, 1, 1),
}

LTE_UDL_MAP = namedtuple("LTE_UDL_MAP",['freq_ul_l', 'freq_ul_h', 'freq_dl_l',
                        'freq_dl_h', 'ch_ul_l', 'ch_ul_h', 'ch_dl_l', 'ch_dl_h'])
# UL_freq, UL_ch, DL_freq, DL_ch
LTE_UDL={
    1:  LTE_UDL_MAP(1920,   1980,   2110,   2170,   18000, 18599, 0,     599),
    2:  LTE_UDL_MAP(1850,   1910,   1930,   1990,   18600, 19199, 600,   1199),
    3:  LTE_UDL_MAP(1710,   1785,   1805,   1880,   19200, 19949, 1200,  1949),
    4:  LTE_UDL_MAP(1710,   1755,   2110,   2155,   19950, 20399, 1950,  2399),
    5:  LTE_UDL_MAP(824,    849,    869,    894,    20400, 20649, 2400,  2649),
    6:  LTE_UDL_MAP(830,    840,    875,    885,    20650, 20749, 2650,  2749),
    7:  LTE_UDL_MAP(2500,   2570,   2620,   2690,   20750, 21449, 2750,  3449),
    8:  LTE_UDL_MAP(880,    915,    925,    960,    21450, 21799, 3450,  3799),
    9:  LTE_UDL_MAP(1749.9, 1784.9, 1844.9, 1879.9, 21800, 22149, 3800,  4149),
    10: LTE_UDL_MAP(1710,   1770,   2110,   2170,   22150, 22749, 4150,  4749),
    11: LTE_UDL_MAP(1427.9, 1447.9, 1475.9, 1495.9, 22750, 22949, 4750,  4949),
    12: LTE_UDL_MAP(699,    716,    729,    746,    23010, 23179, 5010,  5179),
    13: LTE_UDL_MAP(777,    787,    746,    756,    23180, 23279, 5180,  5279),
    14: LTE_UDL_MAP(788,    798,    758,    768,    23280, 23379, 5280,  5379),
    17: LTE_UDL_MAP(704,    716,    734,    746,    23730, 23849, 5730,  5849),
    18: LTE_UDL_MAP(815,    830,    860,    875,    23850, 23999, 5850,  5999),
    19: LTE_UDL_MAP(830,    845,    875,    890,    24000, 24149, 6000,  6149),
    20: LTE_UDL_MAP(832,    862,    791,    821,    24150, 24449, 6150,  6449),
    21: LTE_UDL_MAP(1447.9, 1462.9, 1495.9, 1510.9, 24450, 24599, 6450,  6599),
    22: LTE_UDL_MAP(3410,   3490,   3510,   3590,   24600, 25399, 6600,  7399),
    23: LTE_UDL_MAP(2000,   2020,   2180,   2200,   25500, 25699, 7500,  7699),
    24: LTE_UDL_MAP(1626.5, 1660.5, 1525,   1559,   25700, 26039, 7700,  8039),
    25: LTE_UDL_MAP(1850,   1915,   1930,   1995,   26040, 26689, 8040,  8689),
    26: LTE_UDL_MAP(814,    849,    859,    894,    26690, 27039, 8690,  9039),
    27: LTE_UDL_MAP(807,    824,    852,    869,    27040, 27209, 9040,  9209),
    28: LTE_UDL_MAP(703,    748,    758,    803,    27210, 27659, 9210,  9659),
    29: LTE_UDL_MAP(None,   None,   717,    728,    None,  None,  9660,  9769),
    30: LTE_UDL_MAP(2305,   2315,   2350,   2360,   27660, 27759, 9770,  9869),
    31: LTE_UDL_MAP(452.5,  457.5,  462.5,  467.5,  27760, 27809, 9870,  9919),
    32: LTE_UDL_MAP(None,   None,   1452,   1496,   None,  None,  9920,  10359),
    33: LTE_UDL_MAP(1990,   1920,   1990,   1920,   36000, 36199, 36000, 36199),
    34: LTE_UDL_MAP(2010,   2025,   2010,   2025,   36200, 36349, 36200, 36349),
    35: LTE_UDL_MAP(1850,   1910,   1850,   1910,   36350, 36949, 36350, 36949),
    36: LTE_UDL_MAP(1930,   1990,   1930,   1990,   36950, 37549, 36950, 37549),
    37: LTE_UDL_MAP(1910,   1930,   1910,   1930,   37550, 37749, 37550, 37749),
    38: LTE_UDL_MAP(2570,   2620,   2570,   2620,   37750, 38249, 37750, 38249),
    39: LTE_UDL_MAP(1880,   1920,   1880,   1920,   38250, 38649, 38250, 38649),
    40: LTE_UDL_MAP(2300,   2400,   2300,   2400,   38650, 39649, 38650, 39649),
    # 41: LTE_UDL_MAP(2496,   2690,   2496,   2690,   39650, 41589, 39650, 41589),
    41: LTE_UDL_MAP(2535,   2655,   2496,   2690,   40040, 41239, 40040, 41239),
    42: LTE_UDL_MAP(3400,   3600,   3400,   3600,   41590, 43589, 41590, 43589),
    43: LTE_UDL_MAP(3600,   3800,   3600,   3800,   43590, 45589, 43590, 45589),
    44: LTE_UDL_MAP(703,    803,    703,    803,    45590, 46589, 45590, 46589),
    45: LTE_UDL_MAP(1446,   1467,   1447,   1467,   46590, 46789, 46590, 46789),
    46: LTE_UDL_MAP(5150,   5925,   5150,   5925,   46790, 54539, 46790, 54539),
    66: LTE_UDL_MAP(1710,   1780,   2110,   2200,   131972, 132671, 66436, 67335),
}

LTE_UL_RB_CONFIG = {
    1: LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    2: LTE_BW_MAP("6@0","15@0","25@0","50@0","50@25","50@50"),
    3: LTE_BW_MAP("6@0","15@0","25@0","50@0","50@25","50@50"),
    4: LTE_BW_MAP("6@0","15@0","25@0","50@0","75@0","100@0"),
    5: LTE_BW_MAP("6@0","15@0","25@0","25@25","-","-"),
    6: LTE_BW_MAP("-","-","25@0","25@25","-","-"),
    7: LTE_BW_MAP("-","-","25@0","50@0","75@0","75@25"),
    8: LTE_BW_MAP("6@0","15@0","25@0","25@25","-","-"),
    9: LTE_BW_MAP("-","-","25@0","50@0","50@25","50@50"),
    10:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    11:LTE_BW_MAP("-","-","25@0","25@25","-","-"),
    12:LTE_BW_MAP("6@0","15@0","20@5","20@30","-","-"),
    13:LTE_BW_MAP("-","-","20@0","20@0","-","-"),
    14:LTE_BW_MAP("-","-","15@0","15@0","-","-"),
    17:LTE_BW_MAP("-","-","20@5","20@30","-","-"),
    18:LTE_BW_MAP("-","-","25@0","25@25","25@50","-"),
    19:LTE_BW_MAP("-","-","25@0","25@25","25@50","-"),
    20:LTE_BW_MAP("-","-","25@0","20@0","20@11","20@16"),
    21:LTE_BW_MAP("-","-","25@0","25@25","25@50","-"),
    22:LTE_BW_MAP("-","-","25@0","50@0","50@25","50@50"),
    23:LTE_BW_MAP("6@0","15@0","25@0","50@0","75@0","100@0"),
    24:LTE_BW_MAP("-","-","25@0","50@0","-","-"),
    25:LTE_BW_MAP("6@0","15@0","25@0","50@0","50@25","50@50"),
    26:LTE_BW_MAP("6@0","15@0","25@0","25@25","25@50","-"),
    27:LTE_BW_MAP("6@0","15@0","25@0","25@25","-","-"),
    28:LTE_BW_MAP("-","15@0","25@0","25@25","25@50","25@75"),
    30:LTE_BW_MAP("-","-","25@0","25@25","-","-"),
    31:LTE_BW_MAP("6@0","5@9","5@10","-","-","-"),
    33:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    34:LTE_BW_MAP("-","-","25@0","50@0","75@0","-"),
    35:LTE_BW_MAP("6@0","15@0","25@0","50@0","75@0","100@0"),
    36:LTE_BW_MAP("6@0","15@0","25@0","50@0","75@0","100@0"),
    37:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    38:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    39:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    40:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    41:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    42:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    43:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
    44:LTE_BW_MAP("-","15@0","25@0","50@0","75@0","100@0"),
    45:LTE_BW_MAP("-","-","25@0","50@0","75@0","100@0"),
}

class LTE_Calc():
    bw_ch_gap_map={
        LTE_BW_1P4 : 7,
        LTE_BW_3   :15,
        LTE_BW_5   :25,
        LTE_BW_10  :50,
        LTE_BW_15  :75,
        LTE_BW_20  :100,
    }
    def __init__(self):
        pass

    @classmethod
    def get_freq_ch(cls,band_num):
        return LTE_UDL[band_num]

    #bw : format LTE_BW_xx or like "B100"
    # 判断 BAND 是否支持 BW
    @classmethod
    def get_band_support(cls, band_num, bw):
        return getattr(LTE_BW_SUPPORT[band_num],bw)

    #bw : format LTE_BW_xx or like "B100"
    @classmethod
    def get_band_ul_rb(cls, band_num, cmw_bw):
        ulrb_str = getattr(LTE_UL_RB_CONFIG[band_num], cmw_bw)
        if ulrb_str != "-":
            ulrb_num, ulrb_pos = ulrb_str.split("@")
            return (ulrb_num, ulrb_pos)
        else:
            return (None,None)

    @classmethod
    def get_cmwband_name(cls, band_num):
        return "OB"+str(band_num)

    # bw 这里可以是 字符串"1p4"，也可以是数字 1.4
    @classmethod
    def get_bw_dl_lmh_ch(cls,band_num, bw):
        if getattr(LTE_BW_SUPPORT[band_num],bw):
            band_info = LTE_UDL[band_num]
            sep = cls.bw_ch_gap_map[bw]
            return(band_info.ch_dl_l+sep,round((band_info.ch_dl_l+band_info.ch_dl_h+1)/2), band_info.ch_dl_h-sep+1)
        else:
            return None

    # bw 这里可以是 字符串"1p4"，也可以是数字 1.4
    @classmethod
    def get_bw_ul_lmh_ch(cls,band_num, bw):
        if getattr(LTE_BW_SUPPORT[band_num],bw):
            band_info = LTE_UDL[band_num]
            sep = cls.bw_ch_gap_map[bw]
            return(band_info.ch_ul_l+sep,round((band_info.ch_ul_l+band_info.ch_ul_h+1)/2), band_info.ch_ul_h-sep+1)
        else:
            return None

    @classmethod
    def get_lte_ch_ul2dl(cls, band_num, ch_ul):
        return ch_ul-LTE_UDL[band_num].ch_ul_l+LTE_UDL[band_num].ch_dl_l

    # bw : format : LTE_BW_3
    @classmethod
    def get_bw_to_rb(cls, cmw_bw):
        rb_map = {
            LTE_BW_1P4 : 6,
            LTE_BW_3   : 15,
            LTE_BW_5   : 25,
            LTE_BW_10  : 50,
            LTE_BW_15  : 75,
            LTE_BW_20  : 100,
        }
        return rb_map[cmw_bw]

    # 获取等差数列信道，供辐射测试
    @classmethod
    def get_arithmetic_ch(cls, band_num, ul_start, ul_end, step):
        if ul_start >= LTE_UDL[band_num].ch_ul_l and ul_end<= LTE_UDL[band_num].ch_ul_h:
            return range(ul_start, ul_end+step, step)
        else:
            return None

class LTE_Calc_ca(LTE_Calc):
    def __init__():
        pass

if __name__ == "__main__":
    print(LTE_Calc.get_bw_ul_lmh_ch(38, LTE_BW_10))
    print(LTE_Calc.get_bw_dl_lmh_ch(38, LTE_BW_10))
    print(LTE_Calc.get_bw_ul_lmh_ch(41, LTE_BW_20))
    print(LTE_Calc.get_bw_dl_lmh_ch(41, LTE_BW_20))
    print(LTE_Calc.get_bw_ul_lmh_ch(5,  LTE_BW_10))
    print(LTE_Calc.get_bw_dl_lmh_ch(5,  LTE_BW_10))
    print(LTE_Calc.get_bw_ul_lmh_ch(4,  LTE_BW_10))
    print(LTE_Calc.get_bw_dl_lmh_ch(4,  LTE_BW_10))
    print(LTE_Calc.get_bw_ul_lmh_ch(1,  LTE_BW_10))
    print(LTE_Calc.get_bw_dl_lmh_ch(1,  LTE_BW_10))
    print(LTE_Calc.get_bw_dl_lmh_ch(3,  LTE_BW_5))
    print(LTE_Calc.get_bw_dl_lmh_ch(3,  LTE_BW_10))
    print(LTE_Calc.get_bw_dl_lmh_ch(3,  LTE_BW_15))
    print(LTE_Calc.get_bw_dl_lmh_ch(3,  LTE_BW_20))
    print(list(LTE_Calc.get_arithmetic_ch(41,40290,41190,50)))
    print(LTE_Calc.get_band_support(5, LTE_BW_20))
    print(LTE_Calc.get_band_ul_rb(20, LTE_BW_10))
    print(LTE_Calc.get_band_ul_rb(5, LTE_BW_20))
    pass
