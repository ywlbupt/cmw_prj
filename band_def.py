#TDSC!/usr/bin/env python
# -*- coding: utf-8 -*-

from MACRO_DEFINE import *
from config_default import config
from config_default import lte_define_ch
from lte_band_def import LTE_Calc

def new_lte_test_list(cfg, priority = 'bw'):
    test_list=[]
    if cfg['LTE']['usr_define']:
        priority = "usr_define"
    bw_zip = list(zip(lte_bw_map,cfg['LTE']["bw"]))
    if priority == "band":
        for i in cfg['LTE']['band']:
            for cmw_bw, bw_enable in bw_zip:
                if bw_enable and LTE_Calc.get_band_support(i, cmw_bw):
                    band_lmh = LTE_Calc.get_bw_ul_lmh_ch(i,cmw_bw)
                    for j,v in enumerate(cfg['LTE']["lmh"]):
                        if v:
                            ch_ul = band_lmh[j]
                            # test_list.append(ue_struct_l(band.band,ch_ul,band.lte_ch_ul2dl(ch_ul), cmw_bw))
                            test_list.append(ue_struct_l(LTE_Calc.get_cmwband_name(i),ch_ul,LTE_Calc.get_lte_ch_ul2dl(i, ch_ul), cmw_bw))
    elif priority == "usr_define":
        cmw_bw = LTE_BW_10
        for band_num, ch_tuple in lte_define_ch:
            for ch_ul in LTE_Calc.get_arithmetic_ch(band_num, *ch_tuple):
                test_list.append(ue_struct_l(LTE_Calc.get_cmwband_name(band_num),ch_ul,LTE_Calc.get_lte_ch_ul2dl(band_num, ch_ul), cmw_bw))
    elif priority == "bw":
        for cmw_bw, bw_enable in bw_zip:
            for i in cfg['LTE']['band']:
                if bw_enable and LTE_Calc.get_band_support(i, cmw_bw):
                    band_lmh = LTE_Calc.get_bw_ul_lmh_ch(i,cmw_bw)
                    for j,v in enumerate(cfg['LTE']["lmh"]):
                        if v:
                            ch_ul = band_lmh[j]
                            # test_list.append(ue_struct_l(band.band,ch_ul,band.lte_ch_ul2dl(ch_ul), cmw_bw))
                            test_list.append(ue_struct_l(LTE_Calc.get_cmwband_name(i),ch_ul,LTE_Calc.get_lte_ch_ul2dl(i, ch_ul), cmw_bw))
    return test_list

def wcdma_test_list(cfg):
    test_list=[]
    for i in cfg['WCDMA']['band']:
        band = wt_band_map[i]
        for j,lmh_enable in enumerate(cfg['WCDMA']['lmh']):
            if lmh_enable:
                test_list.append(ue_struct_w(band[0],band[1][j],band[2][j]))
    return test_list

def tdsc_test_list(cfg):
    test_list=[]
    for i in cfg['TDSC']['band']:
        band = wt_band_map[i]
        for j,lmh_enable in enumerate(cfg['TDSC']['lmh']):
            if lmh_enable:
                test_list.append(ue_struct_t(band[0],band[1][j]))
    return test_list


def gsm_test_list(cfg):
    test_list = []
    for i in cfg['GSM']['band']:
        band = gsm_band_map[i]
        for j,lmh_enable in enumerate(cfg['GSM']['lmh']):
            if lmh_enable:
                test_list.append(ue_struct_g(band[0],band[1][j]))
    return test_list

TEST_LIST_G = gsm_test_list(config)

TEST_LIST_W = wcdma_test_list(config)

TEST_LIST_T = tdsc_test_list(config)

TEST_LIST_L = new_lte_test_list(config, priority = LTE_TEST_PRIORITY)

TEST_LIST = {
    "LTE" : TEST_LIST_L,
    "WCDMA" :   TEST_LIST_W,
    "GSM"   :   TEST_LIST_G,
    "TDSC"  :   TEST_LIST_T,
}

if __name__ == "__main__":
    for i in TEST_LIST["LTE"]:
        print(i)
    # for i in TEST_LIST_W:
        # print(i)
    # md = "WCDMA"
    # print([wt_band_map[i][0] for i in config[md].get("div-support", ())])
