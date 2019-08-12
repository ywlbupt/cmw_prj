#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
测试不同单音干扰对LTE 不同子载波频率 灵敏度的影响
'''

import time
from datetime import datetime
import os

from adb import cmd
from MACRO_DEFINE import *

from instr_cmw500 import handle_instr_cmw500 as hd_cmw
from instr_cmw500 import ConnectionError
from instr_E4437B import handle_instr_E4437B as hd_sig

# from config_default import config
from config_default import SENSE_PARAM
from MACRO_DEFINE import ue_struct_l
''' ue_struct_l = namedtuple("ue_struct_l",['BAND','CH_UL','CH_DL','BW']) '''
from band_def import lte_test_list_build

cfg_lte = {
    "LTE" :{
        ## 测试 Band
        'band'  :   (3,),
        # 'band'  :   (38,40,38,40),
        ## 带宽BW:   5, 10, 20
        'bw'    :   (1,0,0),
        ## 高中低信道
        'lmh'   :   (0,1,0),
    },
}

# unit : kHz
def freq_expand_center(freq_center=1842500000, freq_sep=15000, bw=1400000):
    pre_list = list(range(freq_center, freq_center-int(bw/2), -1*freq_sep ))
    pre_list.reverse()
    forward_list = range(freq_center+freq_sep, freq_center+int(bw/2), freq_sep)
    return pre_list+list(forward_list)

freq_range = freq_expand_center()
# freq_range= range(2138545000 ,2139430000 , 15000)
amp_range = [-103,]

def loop_sig(_sig, _cmw, sigrfamp, sigfreq, mea_item = "sensm_cloop"):
    '''
    mea_item is single string
    '''
    _sig.sig_AmpFreq_set(sigrfamp, sigfreq)
    res = _cmw.LTE_acquire_meas(md="LTE", mea_item=mea_item)
    return (mea_item, sigrfamp, sigfreq, *res[mea_item])

def sig_data_output( _res_l, fn ):
        if not os.path.exists("Report"):
            os.mkdir("Report")
        with open(os.path.join("Report", fn),'w') as f:
            f.write("ch\titem\tsig_amp\tsig_freq\treslut\n")
            for data in _res_l:
                f.write("{0}\n".format("\t".join(str(i) for i in data)))

def main():
    try:
        time_start = time.time()

        sig_addr="GPIB0::19::INSTR"
        sigen = hd_sig(sig_addr)

        cmw_addr= "GPIB0::20::INSTR"
        cmw = hd_cmw(cmw_addr)
        if sigen and cmw:
            res_list = []
            try :
                lte_test_list  = lte_test_list_build(cfg_lte)
                cmw.main_lte_setup(lte_test_list)

                for band_ch in lte_test_list:
                    cmw.LTE_ch_redirection(band_ch)
                    for s_amp in amp_range:
                        for s_freq in freq_range:
                            # begin loop
                            try:
                                res = loop_sig(sigen, cmw, s_amp, s_freq, "sensm_cloop")
                                print (res)
                                res_list.append((band_ch.BAND+str(band_ch.CH_UL)+band_ch.BW, *res))
                            except ConnectionError:
                                for i in range(5):
                                    try:
                                        cmd("taskkill /f /im adb.exe")
                                        print("kill adb process")
                                        time.sleep(5)
                                        cmd("adb reboot")
                                        time.sleep(30)
                                        cmw.main_lte_setup([band_ch,])
                                        res = loop_sig(sigen, cmw, s_amp, s_freq, "sensm_cloop")
                                        print (res)
                                        res_list.append((band_ch.BAND+str(band_ch.CH_UL)+band_ch.BW, *res))
                                        break
                                    except:
                                        pass
            finally:
                # datetime.today().strftime("_%Y_%m_%d_%H_%M")
                sig_data_output(res_list, "sense"+ datetime.today().strftime("_%Y_%m_%d_%H_%M")+".txt")
                sigen.instr_close()
                cmw.instr_rm_close()
    finally:
        time_end = time.time()
        print("time elaped {0}:{1}".format(int(time_end-time_start)//60, int(time_end-time_start)%60))

if __name__ == '__main__':
    # instr = rm.open_resource("TCPIP0::10.237.70.10::inst0::INSTR")
    main()
