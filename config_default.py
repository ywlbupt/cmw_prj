#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependency:
# pip install pyvisa
# 运行，cmd命令行下运行： python main.py

# B41 宽频段范围选项

# 插损设置 , (Ouput, Input, Loss TAble)
param_FDCorrection=(0, 0,
                    "699000000, 0.5, 960000000, 0.5, 1710000000, 0.8,2170000000, 0.8, 2300000000, 0.9, 2535000000, 0.9, 2700000000, 0.9")
# param_FDCorrection="699000000, 30, 2700000000, 30"

config = {
    'ip_cmw500'    :   "192.168.0.10",
    # 'gpib_cmw500'      :   20 ,
    'gpib_addr_66319D' : 5,

    # 1:LTE, 2:WCDMA , 3:GSM , 4:TDSC, 5:LTE_CA
    "TEST_RF"   :   (1,),
    'LTE' : {
        # use for 辐射耦合Desense测试，CMW500辐射测试不稳定，放弃
        'usr_define' :   False,
        # RB, NS, 测试接收项时，是否根据3gppp配置上行RB
        'partRB_rx_Enable' : False, 
        ## 测试 Band
        # 'band'  :   (1,2,3,4,5,7,8,12,13,17,18,19,20,25,26,28,30,34,38,39,40,41,),
        'band'  :   (1,3,7,20,1,3,7,20),
        # 'band'  :   (41,41,38,38),
        ## 带宽BW:   5, 10, 20
        'bw'    :   (0,1,0),
        ## 高中低信道
        'lmh'   :   (1,1,1),
        ## 1:aclr, 2:MaxPower Sens main, 3: Sens div, 4: Sens cloop -20，小功率 5：大小功率电流
        'test_item'     :   (1,3),
        'data_save'     :   r"./lte_data.txt",
    },
    'WCDMA' :{
        'band'  :   (1,2,5,8,3,4,6,9,19,),
        'lmh'   :   (1,1,1),
        # 1:aclr, 2:MaxPower Sens main, 3: Sens div, 4: Sens cloop -20 小功率灵敏度 5: 大小功率电流
        'test_item'     :   (1,5),
        # WCDMA 有 分集的通路
        'div-support'   :   (1,2,5,8),
        'data_save'     :   r"./wcdma_data.txt",
        # Voice, test mode A
    },
    'GSM'   :{
        'band'  :   (2,5,8,3),
        'lmh'   :   (1,1,1),
        # 1 : Switch Spectrum, 2: Sensm , 3:sensd , 5: 大小功率电流
        'test_item'     :   (1,5),
        'WITHSIM'   :   True,
        # 1: Call from CMW , 0: Call from phone
        'call_type' :   1,
        # 1: Handover, 0:ON OFF
        'switch_type':  1,
        'div-support'   :   (5,8,3,2),
        'data_save'     :   r"./gsm_data.txt",
    },
    'TDSC'  :{
        'band'  :   (34,39),
        'lmh'   :   (1,1,1),
        # aclr:1, MaxPower Sens main :2, Maxpower Sens div :3 5:大小功率电流
        'test_item'     :   (1,5),
        'data_save'     :   r"./td_data.txt",
    },
    'LTE_CA':{
        'band' : ("1A+18A", "1A+19A", "B1A+20A", "B41C", "B40C"),
        # Throughput:1, 
        'test_item'     :   (1,),
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
    # 起始功率
    'pwr_init' : -123,
    # 粗调精度
    'pwr_coarse' : 0.5,
    # 细调精度
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
