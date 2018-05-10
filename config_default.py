#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 插损设置
param_FDCorrection="699000000, 0.6, 960000000, 0.6, 1710000000, 1.0,2170000000, 1.0, 2300000000, 1.2, 2535000000, 1.2, 2700000000, 1.2"
# param_FDCorrection="699000000, 30, 2700000000, 30"


config = {
    'dev_ip'    :   "192.168.0.2",
    # 'gpib'      :   20 ,

    # 1:LTE, 2:WCDMA , 3:GSM , 4:TDSC
    "TEST_RF"   :   (1,),
    'LTE' : {
        # use for 辐射耦合Desense测试，CMW500辐射测试不稳定，放弃
        'usr_define' :   False,
        # 测试 Band
        'band'  :   (1,2,3,4,5,7,8,12,13,17,18,19,20,25,26,28,30,34,38,39,40,41,),
        # 'band'  :   (34,38,39,40,41,28,30,),
        # BW:   5, 10, 20
        'bw'    :   (1,0,0),
        # 高中低信道
        'lmh'   :   (1,1,1),
        # 1:aclr, 2:MaxPower Sens main, 3: Sens div, 4: Sens cloop -20， 小功率
        'test_item'     :   (1,),
        'data_save'     :   r"./lte_data.txt",
    },
    'WCDMA' :{
        'band'  :   (1,2,5,8,3,4,6,9,19,),
        'lmh'   :   (1,1,1),
        # 1:aclr, 2:MaxPower Sens main, 3: Sens div, 4: Sens cloop -20
        'test_item'     :   (1,),
        # WCDMA 有 分集的通路
        'div-support'   :   (1,2,5,8),
        'data_save'     :   r"./wcdma_data.txt",
    },
    'GSM'   :{
        'band'  :   (5,8,3,5,8,3),
        'lmh'   :   (1,1,1),
        # 1 : Switch Spectrum, 2: Sensm , 3:sensd
        'test_item'     :   (1,),
        'WITHSIM'   :   True,
        # 1: Call from CMW , 0: Call from phone
        'call_type' :   1,
        # 1: Handover, 0:ON OFF
        'switch_type':  1,
        'div-support'   :   (5,8,3,2),
        'data_save'     :   r"./gsm_data.txt",
    },
    'TDSC'  :{
        'band'  :   (34,39,34,39),
        'lmh'   :   (1,1,1),
        # aclr:1, MaxPower Sens main :2, Maxpower Sens div :3
        'test_item'     :   (1,),
        'data_save'     :   r"./td_data.txt",
    },
    'Report_file'   : "Report",
}

lte_define_ch = ( 
    # (1,(18150, 18550, 50)),
    # (3,(19250, 19900, 50)),
    # (4,(20000, 20350, 50)),
    (5,(20450, 20600, 50)),
    # (7,(20800, 21400, 50)),
    (8,(21500, 21750, 50)),
    (20,(24200, 24400, 50)),
    # (34,(36250, 36300, 50)),
    # (38,(37800, 38200, 50)),
    # (39,(38300, 38600, 50)),
    # (40,(38700, 39600, 50)),
    # (41,(40090, 41190, 50)),
 )

SENSE_PARAM = {
    "LTE" :{
    'pwr_init' : -124,
    'pwr_coarse' : 0.5,
    'pwr_fine' : 0.1,
    'frame_coarse' : 100,
    'frame_fine' : 200,
    'BER_THRESHOLD' : 5,
    },
    "WCDMA":{
    'pwr_init' : -109,
    'pwr_coarse' : 0.5,
    'pwr_fine' : 0.2,
    'frame_coarse' : 50,
    'frame_fine' : 300,
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
