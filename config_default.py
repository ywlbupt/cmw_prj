#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MACRO_DEFINE import *

config = {
    # 1:LTE, 2:WCDMA , 3:GSM , 4:TDSC
    "TEST_RF"   :   (1,),
    'LTE' : {
        # 测试 Band
        # 'band'  :   (1,3,4,5,7,8,12,20,34,38,39,40,41),
        'band'  :   (1,),
        # BW:   5, 10, 20
        'bw'    :   (0,1,0),
        # 高中低信道
        'lmh'   :   (1,1,1),
        # aclr:1, MaxPower Sens main :2, Maxpower Sens div :3
        'test_item'     :   (1,2),
        'data_save'     :   r"./test_data_l.txt",
    },
    'WCDMA' :{
        # 'band'  :   (1,2,5,8),
        'band'  :   (1,),
        'lmh'   :   (1,1,1),
        # aclr:1, MaxPower Sens main :2, Maxpower Sens div :3
        'test_item'     :   (1,2,),
        # WCDMA 有 分集的通路
        'div-support'   :   (1,5,8),
        'data_save'     :   r"./test_data_w.txt",
    },
    'GSM'   :{
        'band'  :   (5,8,3,),
        'lmh'   :   (1,1,1),
        # 1 : Switch Spectrum, 2: Sensm , 3:sensd
        'test_item'     :   (1,2),
        'WITHSIM'   :   True,
        # 1: Call from CMW , 0: Call from phone
        'call_type' :   1,
        # 1: Handover, 0:ON OFF
        'switch_type':  1,
        'div-support'   :   (5,8,3),
        'data_save'     :   r"./test_data_g.txt",
    },
    'TDSC'  :{
        'band'  :   (34,39,),
        'lmh'   :   (1,1,1),
        # aclr:1, MaxPower Sens main :2, Maxpower Sens div :3
        'test_item'     :   (1,2),
        'data_save'     :   r"./test_data_t.txt",
    },
    'dev_ip'    :   "10.237.70.40",
    # 'gpib'      :   20
}

SENSE_PARAM = {
    "LTE" :{
    'pwr_init' : -120,
    'pwr_coarse' : 0.5,
    'pwr_fine' : 0.1,
    'frame_coarse' : 200,
    'frame_fine' : 1000,
    'BER_THRESHOLD' : 5,
    },
    "WCDMA":{
    'pwr_init' : -108,
    'pwr_coarse' : 0.5,
    'pwr_fine' : 0.2,
    'frame_coarse' : 50,
    'frame_fine' : 100,
    'BER_THRESHOLD' : 0.1,
    },
    "GSM":{
    'pwr_init' : -102,
    'pwr_coarse' : 2,
    'pwr_fine' : 0.3,
    'frame_coarse' : 30,
    'frame_fine' : 100,
    'BER_THRESHOLD' : 2.5,
    },
    "TDSC":{
    'pwr_init' : -108,
    'pwr_coarse' : 0.5,
    'pwr_fine' : 0.2,
    'frame_coarse' : 50,
    'frame_fine' : 100,
    'BER_THRESHOLD' : 0.1,
    },
}
