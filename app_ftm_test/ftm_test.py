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
from u_param import unite_res
from u_param import UNITE_SPEC
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
            self.display_res_append("pause scan")
        else:
            self._pause_flag.set()
            self.display_res_append("resume scan")

    def callback_stop_scan(self, event=None):
        self._pause_flag.set()
        self._is_runing.clear()
        self.display_res_append("stop scan")

    def retrieve_ftm_param(self):
        if not self.getparam_func :
            _r_param = R_PARAM
        else:
            _r_param = self.getparam_func()

        for item in ['r_ch', "r_icq", "r_rgi"]:
            _r_param[item] = _str2list(_r_param[item])
        _r_param['bw'] = split_digit_alpha(_r_param['bw'])[0]
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
            self.t = Thread(target = self._icq_scan_proc, args=(_r_param,), daemon = True)
            self.t.start()

    def _icq_scan_proc(self, r_param):
        def _icq_scan_func():
            for ch in r_param["r_ch"]:
                self.click_and_typewrite(*self.coordinate_xy["b_tear_down"])
                self.click_and_typewrite(*self.coordinate_xy["d_ch"], ch)
                self.hd_cmw.ftm_set_ch(r_param['md'], ch)
                for icq in r_param["r_icq"]:
                    self.click_and_typewrite(*self.coordinate_xy["d_icq"],icq )
                    for rgi in r_param["r_rgi"]:
                        self.click_and_typewrite(*self.coordinate_xy["d_rgi"],rgi )
                        self.click_and_typewrite(*self.coordinate_xy["b_radio_set"] )
                        self.click_and_typewrite(*self.coordinate_xy["b_tx_set"] )
                        temp = self.hd_cmw.get_aclr_ftm(r_param['md'])
                        self.display_res_append (str([ch, icq, rgi, *temp]))
                        _res_detail.append([ch, icq, rgi, *temp])
                        if not self._pause_flag.is_set():
                            self._pause_flag.wait()
                        if not self._is_runing.is_set():
                            return

        def _data_judge(_aclr_data):
            ''' 判断alcr 数据有效与超spec
            return : True 有效，False INV或者超spec
            '''
            _md = r_param["md"]
            for i,j in UNITE_SPEC[_md]["spec"]:
                if abs(_aclr_data[i]) < abs(j):
                    return False
            return True

        def _pwr_pos(_pwr,):
            ''' spec = UNITE_SPEC['pwr_range'] '''
            _md = r_param["md"]
            if _pwr < UNITE_SPEC[_md]['pwr_range'][0]:
                return "L"
            elif _pwr > UNITE_SPEC[_md]['pwr_range'][1]: 
                return "H"
            else:
                return "M"

        def state_machine(_aclr_data, _rgi_present, _state_present, _rgi_anchor):
            ''' state machine '''
            _pwr = _aclr_data[2]
            _md = r_param["md"]
            if _pwr == "INV":
                state_next = "end" 
                rgi_next = _rgi_present
            elif _pwr < UNITE_SPEC[_md]['pwr_range'][0] and not _data_judge(_aclr_data):
                state_next = "end" 
                rgi_next = _rgi_present
            elif _state_present == "init":
                if _pwr_pos(_pwr) == "L":
                    state_next = "low_seek_higher"
                    rgi_next = _rgi_present + 1
                elif _pwr_pos(_pwr) == "H":
                    state_next = "high_seek_lower"
                    rgi_next = _rgi_present - 1
                elif _pwr_pos(_pwr) == "M":
                    state_next = "middle_seek_higher"
                    rgi_next = _rgi_present + 1
            elif _state_present == "low_seek_higher":
                if _pwr_pos(_pwr) != "H":
                    state_next = "low_seek_higher"
                    rgi_next = _rgi_present + 1
                elif _pwr_pos(_pwr) == "H":
                    state_next, rgi_next = "end" , _rgi_present
            elif _state_present == "high_seek_lower":
                if _pwr_pos(_pwr) != "L":
                    state_next = "high_seek_lower"
                    rgi_next = _rgi_present - 1
                elif _pwr_pos(_pwr) == "L":
                    state_next, rgi_next = "end", _rgi_present
            elif _state_present == "middle_seek_higher":
                if _pwr_pos(_pwr) != "H":
                    state_next = "middle_seek_higher"
                    rgi_next = _rgi_present + 1
                elif _pwr_pos(_pwr) == "H":
                    state_next = "middle_seek_lower"
                    rgi_next = _rgi_anchor-1
            elif _state_present == "middle_seek_lower":
                if _pwr_pos(_pwr) != "L":
                    state_next = "middle_seek_lower"
                    rgi_next = _rgi_present - 1
                elif _pwr_pos(_pwr) == "L":
                    state_next, rgi_next = "end", _rgi_present
            return state_next, rgi_next

        def _icq_scan_unite_func():
            nonlocal _res_unite
            nonlocal _res_detail
            # nonlocal r_param
            for ch in r_param["r_ch"]:
                self.click_and_typewrite(*self.coordinate_xy["b_tear_down"])
                self.click_and_typewrite(*self.coordinate_xy["d_ch"], ch)
                self.click_and_typewrite(*self.coordinate_xy["b_radio_set"] )
                self.hd_cmw.ftm_set_ch(r_param['md'], ch)
                for icq in r_param["r_icq"]:
                    self.click_and_typewrite(*self.coordinate_xy["d_icq"],icq )

                    rgi,rgi_anchor = 50,50
                    _res_pericq = []
                    _md = r_param["md"]
                    state = "init"
                    while( rgi <= 57 and rgi >= 45 and state != "end"):
                        self.click_and_typewrite(*self.coordinate_xy["d_rgi"],rgi )
                        self.click_and_typewrite(*self.coordinate_xy["b_tx_set"] )
                        aclr_data = self.hd_cmw.get_aclr_ftm(r_param['md'])

                        _res_pericq.append([ch, icq, rgi, *aclr_data])
                        self.display_res_append (str([ch, icq, rgi, *aclr_data]))
                        _res_detail.append([ch, icq, rgi, *aclr_data])
                        
                        state_next,  rgi_next= state_machine(aclr_data, rgi, state, rgi_anchor)
                        rgi, state = rgi_next, state_next

                        if not self._pause_flag.is_set():
                            self._pause_flag.wait()
                        if not self._is_runing.is_set():
                            return

                    # 通过rgi 排序
                    _res_pericq.sort(key = lambda r: r[2])
                    # pwr index is 5
                    for target_pwr in UNITE_SPEC[_md]["pwr_unite"]:
                        u_row = unite_res(_res_pericq, 5, target_pwr)
                        if u_row:
                            _res_unite.append([ch, icq, *(u_row[2:])])
                            self.display_res_append (str([ch, icq, *(u_row[2:])]))


        if len(self.coordinate_xy)==len(CATCH_ORDER):
            _res_detail = []
            _res_unite = []
            try:
                self.hd_cmw.set_FDCorrection(LOSS)
                self.hd_cmw.set_remote_display(state=True)
                time.sleep(2)
                with keyboard_hook("enter", self.callback_pause_toggle),\
                keyboard_hook("esc", self.callback_stop_scan):
                    # 利用func return特性终止多重循环
                    self._is_runing.set()
                    # _icq_scan_func()
                    _icq_scan_unite_func()

                    self.display_res_append("icq scan done")

            finally:
                self._data_output(_res_detail, "ftm_scan"+ datetime.today().strftime("_%Y_%m_%d_%H_%M")+".txt")
                self._data_output(_res_unite, "ftm_scan_unite"+ datetime.today().strftime("_%Y_%m_%d_%H_%M")+".txt")
        else:
            self.display_promt("please anchor position first")

    def _data_output(self, _res, fn):
        ''' 当前路径下新建Report文件夹保存测试数据 '''
        if not os.path.exists("Report"):
            os.mkdir("Report")
        with open(os.path.join("Report", fn),'w') as f:
            f.write("ch\ticq\trgi\tresult\n")
            for data in _res:
                f.write("{0}\n".format("\t".join(str(i) for i in data)))

    def _ftm_set(self):
        _r_param = self.retrieve_ftm_param()
        self.hd_cmw.set_FDCorrection(LOSS)
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
