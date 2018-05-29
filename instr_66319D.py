#!/usr/bin/env python
# -*- coding: utf-8 -*-

from instr import handle_instr
import re


class handle_instr_66319D(handle_instr):
    instr_name_p = re.compile ("Agilent.*66319D.*")

    def instr_reset(self):
        pass

    def instr_OUTPUT_ONOFF(self, ONOFF = False):
        cmdstr="ON" if ONOFF else "OFF"
        self.instr_write("OUTP {0}".format(cmdstr))

    def instr_OUTPUT_VOL_SET(self, voltage, ch_num=1):
        # 默认output通道1 输出
        self.instr_write("VOLT{0} {1}".format("" if ch_num==1 else ch_num, voltage))

    def instr_get_DC_current(self):
        dc_curr = round(float(self.instr_query("MEAS:CURR:DC?").strip()),3)
        return dc_curr

    def instr_reset_to_idle(self):
        self.instr_write("ABORt")

    def instr_get_dc_volt(self):
        dc_volt = round(float(self.instr_query("MEAS:VOLT:DC?").strip()),3)
        return dc_volt


if __name__ == "__main__":
    # tmp_gpib_addr="GPIB0::5::INSTR"
    # m = handle_instr_66319D(tmp_gpib_addr)
    # m.instr_OUTPUT_ONOFF(True)
    # print(m.instr_get_DC_current())
    # print(m.instr_get_dc_volt())
    # print(m.get_instr_version())
    # m.instr_rm_close()
    # print(handle_instr_66319D.get_gpib_addr())
    print(handle_instr_66319D.instr_addr_check("GPIB0::5::INSTR"))
    pass
