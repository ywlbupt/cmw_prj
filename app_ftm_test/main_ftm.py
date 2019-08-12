#!/usr/bin/env python
# -*- coding: utf-8 -*-

from u_tkinter import OOP
from ftm_test import ftm_test
from instr_cmw500_ftm import Initial_run


def register_ftm_oop(ins_ftm, ins_oop):
    ins_ftm.hook_display_promt(ins_oop._ftm_frame.display_promt)
    ins_ftm.hook_display_res_append(ins_oop._ftm_frame.display_res_append)
    ins_ftm.hook_getparam_func(ins_oop._ftm_frame.get_ui_ftm_param)


    ins_oop._ftm_frame.register_get_pos(ins_ftm._get_pos)
    ins_oop._ftm_frame.register_icq_scan(ins_ftm._icq_scan)
    ins_oop._ftm_frame.register_stop_scan(ins_ftm.callback_stop_scan)
    ins_oop._ftm_frame.register_ftm_set(ins_ftm._ftm_set)

def main():
    hd_cmw = Initial_run(20)
    if hd_cmw:
        m = ftm_test(hd_cmw)
        oop = OOP()
        register_ftm_oop(m, oop)
        oop.run()

        hd_cmw.instr_rm_close()
if __name__ == "__main__":
    main()
