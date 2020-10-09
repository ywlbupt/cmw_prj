#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
dox
'''

# Dependency:
# pip install pyvisa
# 运行，cmd命令行下运行： python main.py

# B41 宽频段范围选项
# 1,1.7,1.9
LOSS_CONFIG = {
    "LOW" : 0.5,
    "MID" : 0.8,
    "HIGH" : 1.0, }
LOSS_MATRIX = "699000000, {loss_low}, 960000000, {loss_low},1710000000,\
{loss_mid},2170000000, {loss_mid},2300000000, {loss_high}, 2700000000, {loss_high}".format(
    loss_low=LOSS_CONFIG['LOW'], loss_mid=LOSS_CONFIG['MID'],
    loss_high=LOSS_CONFIG['HIGH'])
# 插损设置 , (Ouput, Input, Loss TAble)
param_FDCorrection=(0, 0, LOSS_MATRIX)

config = {
    'ip_cmw500'    :   "192.168.0.2",
    # 'gpib_cmw500'      : 20,
    'gpib_addr_66319D' : 5,

    # 1:LTE, 2:WCDMA , 3:GSM , 4:TDSC, 5:LTE_CA
    "TEST_RF"   :   (1,),
    'LTE' : {
        # use for 辐射耦合Desense测试，CMW500辐射测试不稳定，放弃
        'usr_define' :   False,
        # RB, NS, 测试接收项时，是否根据3gppp配置上行RB
        'partRB_rx_Enable' : True, 
        ## 测试 Band
        # 'band'  :   (1,2,3,4,5,7,8,12,13,17,18,19,20,25,26,28,30,34,38,39,40,41,),
        # 'band'  :   (1,3,7,34,38,39,40,41),
        'band'  :   (5,8,12,20,28,1,2,3,4,7,38,40,41,),
        # 'band'  :   (5,8,),
        # 带宽BW:   5, 10, 20
        'bw'    :   (0,1,0),
        ## 高中低信道
        'lmh'   :   (1,1,1),
        ## 1:aclr, 2:MaxPower Sens main, 3: Sens div, 4: Sens cloop -20，小功率 5：大小功率电流
        'test_item'     :   (1,2,3,4),
        'data_save'     :   r"./lte_data.txt",
    },
    'WCDMA' :{
        'band'  :   (5,8,),
        'lmh'   :   (1,1,1),
        # 1:aclr, 2:MaxPower Sens main, 3: Sens div, 4: Sens cloop -20 小功率灵敏度 5: 大小功率电流
        'test_item'     :   (1,),
        # WCDMA 有 分集的通路
        'div-support'   :   (1,2,5,8),
        'data_save'     :   r"./wcdma_data.txt",
        # Voice, test mode A
    },
    'GSM'   :{
        'band'  :   (5,8),
        'lmh'   :   (1,1,1),
        # 1 : Switch Spectrum, 2: Sensm , 3:sensd , 5: 大小功率电流
        'test_item'     :   (1,2,),
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

PRJ_PORT = {
    # route_m = "RF1C,RX1,RF1C,TX1"
    # route_d = "RF1C,RX1,RF1O,TX1"
    # route_com2_m = "RF2C,RX1,RF2C,TX1"
    # route_com2_d = "RF2C,RX1,RF1O,TX1"

    
    5 :     ('RF2C','1','RF1O','1'),
    8 :     ('RF2C','1','RF1O','1'),
    12 :    ('RF2C','1','RF1O','1'),
    17 :    ('RF2C','1','RF1O','1'),
    20 :    ('RF2C','1','RF1O','1'),
    28 :    ('RF2C','1','RF1O','1'),
    # 1 : ('RF2C','RF1O'),
    # 3 : ('RF2C','RF1O'),
    'default' : ('RF3C','2','RF3O',"2"),
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
    'pwr_init' : -120,
    # 粗调精度
    'pwr_coarse' : 0.5,
    # 细调精度
    'pwr_fine' : 0.2,
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
