#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

# =======
# param setting
# =======

CATCH_ORDER = ['d_ch','d_icq', 'd_rgi','b_tear_down', "b_radio_set", "b_tx_set"]

UNITE_SPEC = {
    "LTE": {
        "pwr_range" : (21, 23),
        "pwr_unite" : [22,23],
        "spec": [(0, 32.2), (1, 29.2), (3, 29.2), (4, 32.2)],
    },
    "WCDMA":{
        "pwr_range" : (23, 24.5),
        "pwr_unite" : [24, 24.5],
        "spec": [(0, 42.2), (1, 32.2), (3, 32.2), (4, 42.2)],
    },
}

def _str2list(v_str):
    res=[]
    v_list = v_str.split(",")
    for v in v_list:
        if v.strip().isdigit():
            res.append(int(v))
        else:
            rs = v.strip().split("-")
            if len(rs) ==2 and rs[0].isdigit() and rs[1].isdigit():
                res=res+list(range(int(rs[0]), int(rs[1])+1))
    return res

def split_digit_alpha(v_str):
    import re
    return re.findall(r'[0-9]+|[a-zA-Z]+', v_str)

def unite_res(res_list, index, unite_target):
    l_row, h_row = None, None
    for row in res_list:
        if isinstance(row[index], (int, float)):
            if row[index] < unite_target:
                l_row = row
            elif row[index] > unite_target: 
                h_row = row
                break
            else:
                unite_row = row
                return unite_row
    if l_row and h_row:
        delta_l = (unite_target - l_row[index])/(h_row[index]-l_row[index])
        unite_row = [(round(lx+(hx-lx)*delta_l,2)) for lx,hx in zip(l_row, h_row)]
        return unite_row
    else:
        return None



# 不考虑不同band的情况
_r_ch = "18900"
_r_icq = "32440-32455"
_r_rgi = "50-55"

R_PARAM = {
    # "LTE" or "WCDMA"
    "md"    : "LTE",
    "band"  : "2",
    "bw"    : "10MHz",
    "r_ch": _r_ch,
    "r_icq" : _r_icq,
    "r_rgi" : _r_rgi,
}

# =======
# 插损配置
# =======
loss_config = {
    "LOW" : 0.5,
    "MID" : 0.8,
    "HIGH" : 0.9, }
loss_matrix =  "699000000, {loss_low}, 960000000, {loss_low},1710000000,{loss_mid},2170000000, {loss_mid},2300000000, {loss_high}, 2700000000, {loss_high}".format(
                        loss_low = loss_config['LOW'], loss_mid = loss_config['MID'], loss_high = loss_config['HIGH'])
# 插损设置 , (Ouput, Input, Loss TAble)
LOSS=(0, 0, loss_matrix)
