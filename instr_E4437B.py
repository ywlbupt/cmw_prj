#!/usr/bin/env python
# -*- coding: utf-8 -*-

from instr import handle_instr
import time
import re


class handle_instr_E4437B(handle_instr):
    instr_name_p = re.compile ("Hewlett-Packard.*E4437B.*")

    def instr_reset(self):
        self.instr_write("*RST")
        self.sig_wait()
        pass

    def sig_rf_onoff(self, state):
        ''' True for RF ON, False for RF OFF 
        *RST Value: OFF 
        '''
        self.instr_write("OUTPut {0}".format('ON' if state else 'OFF'))

    def sig_mod_onoff(self, state):
        ''' True for RF ON, False for RF OFF
        *RST Value: ON  '''
        self.instr_write("OUTPut:MODulation {0}".format('ON' if state else 'OFF'))

    def sig_wait(self):
        '''
        wait to continue for all pending commands completed
        '''
        self.instr_write("*iAI")

    def sig_set_amp(self, unit_dbm):
        self.instr_write("POW:AMPL {0} dBm".format(unit_dbm) )

    def sig_set_freq(self, freq):
        ''' CW output freq : format "2M", "2.5G", '300k' '''
        p= re.compile(r'(?P<freq_num>[0-9]+\.*[0-9]*)(?P<freq_unit>[gmk]?)',re.I)
        mt = p.match(str(freq))
        if mt:
            self.instr_write("FREQ:CW {freq_num} {freq_unit}Hz".format(
                freq_num = mt.group('freq_num'), freq_unit = mt.group('freq_unit')))
        else:
            raise ValueError
    def sig_AmpFreq_set(self, amp_dbm, freq_str):
        ''' param : (amp_dbm, freq_str)
        '''
        self.sig_set_amp(amp_dbm)
        self.sig_set_freq(freq_str)
        self.sig_mod_onoff(False)
        self.sig_rf_onoff(True)
        self.sig_wait()

if __name__ == "__main__":
    tmp_gpib_addr="GPIB0::19::INSTR"
    # print(handle_instr_E4437B.instr_addr_check(tmp_gpib_addr))
    # print(handle_instr_66319D.get_gpib_addr())
    m = handle_instr_E4437B(tmp_gpib_addr)
    if m:
        # m.instr_reset()
        try:
            m.sig_set_freq("2130000k")
            m.sig_set_amp("-55.3")
            m.sig_mod_onoff(True)
            m.sig_rf_onoff(True)
        finally:
            m.instr_rm_close()
    # m.instr_OUTPUT_ONOFF(True)
    # m.instr_OUTPUT_ONOFF(True)

    pass
