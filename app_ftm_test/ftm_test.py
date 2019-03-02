#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from threading import Thread
import time
from datetime import datetime
import os
import pyautogui

from _pyuserinput import keyboard_press_to_get_position
from _pyuserinput import keyboard_hook
# with keyboard_hook(key, callback) as k:
from u_param import _str2list
from u_param import split_digit_alpha
from u_param import R_PARAM
from u_param import CATCH_ORDER
from u_param import LOSS
from instr_cmw500_ftm import Initial_run

class ftm_test():
    '''
    usage :  icq scan 过程中， enter 控制暂停恢复，esc键控制退出整个过程
    '''

    def __init__(self, hd_cmw):
        self.t = Thread()
        self._pause_flag = threading.Event()
        self._pause_flag.set()
        self._is_runing = threading.Event()

        self.coordinate_xy = {}
        self.result = []
        self.hd_cmw = hd_cmw

        # tobe hook
        self.getparam_func = None
        self.display_promt = None
        self.display_res_append = None
        pass

    def hook_display_promt(self, callback):
        self.display_promt = callback

    def hook_display_res_append(self, callback):
        self.display_res_append = callback
    
    def hook_getparam_func(self, callback):
        self.getparam_func = callback

    def single_click(self, x, y):
        pyautogui.moveTo(x, y,duration=0.2)
        pyautogui.click()
        time.sleep(0.5)

    def double_click_and_type(self, x, y, type_data):
        pyautogui.moveTo(x, y, duration =0.2)
        pyautogui.doubleClick(x, y)
        time.sleep(0.5)
        pyautogui.typewrite(str(type_data))
        time.sleep(0.5)

    def typewrite(self, str_value):
        pyautogui.typewrite(str_value, duration = 0.2)

    def click_and_typewrite(self, x, y, type_data = None):
        if type_data:
            self.double_click_and_type(x, y, type_data)
        else:
            self.single_click(x, y)
            time.sleep(1)

    def callback_pause_toggle(self, event=None):
        # keyboard_hook toggle self._pause_flag
        if self._pause_flag.is_set():
            self._pause_flag.clear()
        else:
            self._pause_flag.set()

    def callback_stop_scan(self):
        self._pause_flag.clear()
        self._is_runing.set()

    def retrieve_ftm_param(self):
        if not self.getparam_func :
            _r_param = R_PARAM
        else:
            _r_param = self.getparam_func()

        for item in ['r_ch', "r_icq", "r_rgi"]:
            _r_param[item] = _str2list(_r_param[item])
        _r_param['bw'] = split_digit_alpha()[0]
        print("_r_param :{0}".format(_r_param))
        return _r_param

    def _get_pos(self):
        if not self.t.is_alive():
            self.display_promt("Begin catch pos")
            self.t = Thread(target = self._param_pos_get, daemon = True)
            self.t.start()
    
    def _param_pos_get(self, timeout = None):
        for key_param in CATCH_ORDER:
            self.display_promt( "press enter at {pos}".format(pos=key_param))
            self.coordinate_xy[key_param] = keyboard_press_to_get_position("enter")
            self.display_promt( "{pos} locate at: {l[0]}, {l[1]}".format(pos = key_param, l = self.coordinate_xy[key_param]))
        self.display_res_append("Get Pos Done")

    def _icq_scan(self, retrieve_way = None):
        if not self.t.is_alive():
            self.display_res_append("Begin icq scan")
            _r_param = self.retrieve_ftm_param()
            self.t = Thread(target = self._icq_scan_proc, args=(_r_param), daemon = True)
            self.t.start()

    def _icq_scan_proc(self, r_param):
        if len(self.coordinate_xy)==len(CATCH_ORDER):
            _res = []
            try:
                self.hd_cmw.set_FDCorrection(LOSS)
                self.hd_cmw.set_remote_display(state=True)
                time.sleep(2)
                with keyboard_hook("enter", self.callback_pause_toggle),\
                keyboard_hook("esc", self.callback_stop_scan):
                    # 利用func return特性终止多重循环
                    self._is_runing.set()
                    def _icq_scan_func():
                        for ch in r_param["r_ch"]:
                                self.click_and_typewrite(*self.coordinate_xy["b_tear_down"])
                                self.click_and_typewrite(*self.coordinate_xy["d_ch"], ch)
                                self.hd_cmw.ftm_set_ch(ch)
                                for icq in r_param["r_icq"]:
                                    self.click_and_typewrite(*self.coordinate_xy["d_icq"],icq )
                                    for rgi in r_param["r_rgi"]:
                                        self.click_and_typewrite(*self.coordinate_xy["d_rgi"],rgi )
                                        self.click_and_typewrite(*self.coordinate_xy["b_radio_set"] )
                                        self.click_and_typewrite(*self.coordinate_xy["b_tx_set"] )
                                        temp = self.hd_cmw.get_aclr_ftm("LTE")
                                        self.display_res_append (ch, icq, rgi, *temp)
                                        _res.append(ch, icq, rgi, *temp)
                                        if not self._pause_flag.is_set():
                                            self._pause_flag.wait()
                                        if not self._is_runing.is_set():
                                            return
                        self.display_res_append("icq scan done")

                    _icq_scan_func()

            finally:
                # print(_res)
                self._data_output(_res, "ftm_scan"+ datetime.today().strftime("_%Y_%m_%d_%H_%M")+".txt")
        else:
            self.display_promt("please anchor position first")

    def _data_ouput(self, _res, fn):
        ''' 当前路径下新建Report文件夹保存测试数据 '''
        if not os.path.exists("Report"):
            os.mkdir("Report")
        with open(os.path.join("Report", fn),'w') as f:
            f.write("ch\ticq\trgi\tresult\n")
            for data in _res:
                f.write("{0}\n".format("\t".join(str(i) for i in data)))

    def _ftm_set(self):
        _r_param = self.retrieve_ftm_param()
        self.hd_cmw.cmw_ftm_set(_r_param)

def main():
    '''
    before using this moduale 
    hook virable param of 'display_promt, display_res_append, and getparam_func'
    '''
    hd_cmw = Initial_run(20)
    if hd_cmw:
        m = ftm_test(hd_cmw)
        m.hook_display_promt = print
        m.hook_display_res_append = print
    pass

if __name__ == "__main__":
    pass
