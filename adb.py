#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

def cmd(cmd_str):
    return os.popen(cmd_str)

class adb():
    # p_b = re.compile(r"List of devices attached\s\+(\w\+)\s\+(\w\+)",re.M)
    def __init__(self):
        pass

    def get_device_series(self):
        # r = cmd("adb devices").read().strip().split("\n")
        r = cmd("adb devices").read()
        p = re.compile(r"List of devices attached\s*\n((\w+)\s+(\w+)\s?)+")
        m = p.search(r)
        if m:
            # print(m.group(0))
            res = m.group(0).strip().split("\n")
            # print(len(res))
            if len(res) == 1:
                return None
            # elif len(r)-1 == 1:
            else:
                return r[1].split("\t")[0]
        # else:
            # return None

    def adb_reboot(self):
        serial = self.get_device_series()
        # cmd("adb -s {serial} reboot".format(serial=serial))
        cmd("adb reboot")

    def adb_fly(self):
        pass

if __name__ == "__main__":
    m = adb()
    print(m.get_device_series())
    # m.adb_reboot()
    pass
