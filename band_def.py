#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MACRO_DEFINE import *

class str_ue_info():
    def __init__(self, ue_struct_):
        self.BAND=ue_struct_[0]
        self.CH_UL=ue_struct_[1]
        self.CH_DL=ue_struct_[2]
        self.BW=ue_struct_[3]

    def __str__(self):
        return "B{band:0>2}\t{ch_ul:5}\t{bw:d}MHz".format(band=self.BAND[2:],ch_ul=self.CH_UL,bw=int(int(self.BW[1:])/10))

class lte_band_cmw():
    channel_raster = 10**5
    def __init__(self, band_name, dl_ul_offset, bw_lmh_ul):
        self.band = band_name
        self.dl_ul_offset = dl_ul_offset
        self.bw_lmh_ul=bw_lmh_ul
    
    def lte_channel_ul2dl(self, channel_num):
        return channel_num-self.dl_ul_offset[1]+self.dl_ul_offset[0]
    
    def lte_channel_dl2ul(self, channel_num):
        return channel_num+self.dl_ul_offset[1]-self.dl_ul_offset[0]


def lte_test_set(priority_band,priority_bw, ul_lmh=[1,1,1]):
    test_list=[]
    for band in priority_band :
        for cmw_bw,bw_set in priority_bw :
            if band in bw_set:
                # for i in range(3):
                for i,v in enumerate(ul_lmh):
                    if v:
                        ch_ul = band.bw_lmh_ul[cmw_bw][i]
                        test_list.append(ue_struct(band.band,ch_ul,band.lte_channel_ul2dl(ch_ul), cmw_bw))

                # for ch_ul in band.bw_lmh_ul[cmw_bw]:
                    # test_list.append(ue_struct(band.band,ch_ul,band.lte_channel_ul2dl(ch_ul), cmw_bw))
    return test_list

lte_b1 = lte_band_cmw("OB1",[0   ,18000], {
    LTE_BW_10:(18050,18300,18550),
    LTE_BW_20:(18100,18300,18500),
    LTE_BW_5 :(18025,18300,18575)
})
lte_b3 = lte_band_cmw("OB3",[1200,19200], {
    LTE_BW_10:(19250,19575,19900), 
    LTE_BW_20:(19300,19575,19850),
    LTE_BW_5 :(19225,19575,19925)
})
lte_b5 = lte_band_cmw("OB5",[2400,20400], {LTE_BW_10:(20450,20525,20600)})
lte_b7 = lte_band_cmw("OB7",[2750,20750], {LTE_BW_10:(20800,21100,21400), LTE_BW_20:(20850,21100,21350)})
lte_b8 = lte_band_cmw("OB8",[3450,21450], {LTE_BW_10:(21500,21625,21750)})

lte_b38 = lte_band_cmw("OB38",[37750,37750], {LTE_BW_10:(37800,38000,38200), LTE_BW_20:(37850,38000,38150)})
lte_b39 = lte_band_cmw("OB39",[38250,38250], {LTE_BW_10:(38300,38450,38600), LTE_BW_20:(38350,38450,38550)})
lte_b40 = lte_band_cmw("OB40",[38650,38650], {LTE_BW_10:(38700,39150,39600), LTE_BW_20:(38750,39150,39550)})
lte_b41_n = lte_band_cmw("OB41",[40240,40240], {LTE_BW_10:(40290,40740,41190), LTE_BW_20:(40340,40740,41140)})
lte_b41_w = lte_band_cmw("OB41",[39650,39650], {LTE_BW_10:(39700,40620,41540), LTE_BW_20:(39750,40620,41490)})


# test info param
# lte_5M = (lte_b3,lte_b1)
lte_5M = ()
lte_10M = (lte_b1,lte_b3,lte_b7,lte_b39,lte_b40,lte_b41_n)
# lte_10M = (lte_b7,)
#.format(down_level) lte_10M = (lte_b1,lte_b3,lte_b5,lte_b8,lte_b7)
# lte_20M = (lte_b1,lte_b3,lte_b7)
lte_20M = ()

# priority_band = (lte_b1,lte_b3,lte_b5,lte_b8,lte_b7,lte_b39,lte_b40,lte_b41_n)
priority_band = (lte_b1,lte_b3,lte_b5,lte_b8,lte_b7,lte_b39,lte_b40,lte_b41_n)
# 使用zip返回一个生成器
priority_bw = list(zip((LTE_BW_10,LTE_BW_20,LTE_BW_5),(lte_10M,lte_20M,lte_5M)))


TEST_LIST = lte_test_set(priority_band,priority_bw, ul_lmh=[0,1,0])

if __name__ == "__main__":
    # a=lte_b8
    # print(lte_band_cmw.lte_channel_ul2dl(18050))
    # print(a.lte_channel_dl2ul(50))
    # print(a.channel_raster)
    for i in TEST_LIST:
        print(i)
    pass
