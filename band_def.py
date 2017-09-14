#TDSC!/usr/bin/env python
# -*- coding: utf-8 -*-

from MACRO_DEFINE import *
from config_default import config

# 生成 TEST_LIST
def lte_test_list(cfg, priority = "bw"):
    test_list=[]
    bw_zip = list(zip(lte_bw_map,cfg['LTE']["bw"]))
    if priority == "band":
        for i in cfg['LTE']['band']:
            for cmw_bw, bw_enable in bw_zip:

                if bw_enable and (cmw_bw in lte_band_map[i].bw_lmh_ul):
                    band = lte_band_map[i]
                    for j,v in enumerate(cfg['LTE']["lmh"]):
                        if v:
                            ch_ul = band.bw_lmh_ul[cmw_bw][j]
                            # yield ue_struct_l(band.band,ch_ul,band.lte_ch_ul2dl(ch_ul), cmw_bw)
                            test_list.append(ue_struct_l(band.band,ch_ul,band.lte_ch_ul2dl(ch_ul), cmw_bw))
    elif priority == "bw":
        for cmw_bw, bw_enable in bw_zip:
            for i in cfg['LTE']['band']:

                if bw_enable and (cmw_bw in lte_band_map[i].bw_lmh_ul):
                    band = lte_band_map[i]
                    for j,lmh_enable in enumerate(cfg['LTE']["lmh"]):
                        if lmh_enable:
                            ch_ul = band.bw_lmh_ul[cmw_bw][j]
                            # yield ue_struct_l(band.band,ch_ul,band.lte_ch_ul2dl(ch_ul), cmw_bw)
                            test_list.append(ue_struct_l(band.band,ch_ul,band.lte_ch_ul2dl(ch_ul), cmw_bw))

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

TEST_LIST_L = lte_test_list(config, priority = LTE_TEST_PRIORITY)

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
