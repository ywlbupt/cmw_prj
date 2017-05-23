#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MACRO_DEFINE import *

config = {
    # LTE:1 ;WCDMA:2
    "TEST_RF"   :   (2,1),
    'LTE' : {
        # 测试 Band
        'band'  :   (1,3,5,7,8,39,40,41),
        # 'band'  :   (5,40,8,41,8,40,5,39,8,41,7,40),
        # BW:   5, 10, 20
        'bw'    :   (0,1,0),
        # 高中低信道
        'lmh'   :   (1,1,1),
        # aclr:1, MaxPower Sens main :2, Maxpower Sens div :3
        'test_item'     :   (1,2,3),
        'data_save'     :   r"./test_data_l.txt",
    },
    'WCDMA' :{
        # 'band'  :   (1,2,5,8),
        'band'  :   (1,2,5,8,),
        'lmh'   :   (1,1,1),
        # aclr:1, MaxPower Sens main :2, Maxpower Sens div :3
        'test_item'     :   (1,2,3),
        # WCDMA 有 分集的通路
        'div-support'   :   (1,5,8),
        'data_save'     :   r"./test_data_w.txt",
    },
    'dev_ip'    :   "10.237.70.10"
    # 'gpib'      :   20
}

SENSE_PARAM = {
    "LTE" :{
    'pwr_init' : -120,
    'pwr_coarse' : 0.5,
    'pwr_fine' : 0.1,
    'frame_coarse' : 200,
    'frame_fine' : 1000,
    'BER_threshold' : 5,
    },
    "WCDMA":{
    'pwr_init' : -108,
    'pwr_coarse' : 0.5,
    'pwr_fine' : 0.2,
    'frame_coarse' : 50,
    'frame_fine' : 100,
    'BER_threshold' : 0.1,
    },
}
