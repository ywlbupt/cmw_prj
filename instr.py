#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, visa, threading, time
import string

# instr 为 visa.ResourceManger() Type
# if "dev_ip" in config:
    # m = handle_instr_cmw500("TCPIP0::{0}::inst0::INSTR".format(config["dev_ip"]))
# elif "gpib" in config:
    # m = handle_instr_cmw500("GPIB0::{0}::INSTR"".format(config["gpib"]))

def device_scan(cls, gpib_addr_num = None):
    # gpib_addr_num int type : gpib addr
    # cls : handle_instr
    # from instr import handle_instr
    # 检查 gpib地址，或者扫描gpib
    if gpib_addr_num:
        instr_addr = "GPIB0::{0}::INSTR".format(gpib_addr_num)
    else:
        instr_addr = None
    if cls.instr_addr_check(instr_addr):
        print("{0} check OK".format(cls.__name__))
        print(instr_addr)
        return instr_addr
    else:
        instr_addr= cls.get_gpib_addr()
        if not instr_addr:
            print("Cannot Find {0}".format(cls.__name__))
            return None
        else:
            print("{0} find another addr OK".format(cls.__name__))
            print(instr_addr)
            return instr_addr

class handle_instr():
    instr_name_p = "not a device name is ok"

    def __init__(self, instr_socall_addr):
        # instr_socall_addr : gpib or tcpip format addr
        self.rm = visa.ResourceManager()
        self.instr = self.rm.open_resource(instr_socall_addr)

    def instr_write(self, *args, **kwargs):
        try:
            self.instr.write(*args, **kwargs)
        except:
            print("write error ",args)
            time.sleep(4)
            self.instr.write(*args, **kwargs)

    def instr_query(self, *args, **kwargs):
        try:
            m = self.instr.query(*args,**kwargs)
        # return self.instr.query(cmd)
        except:
            print("query error {0}",args)
            time.sleep(4)
            m = self.instr.query(*args,**kwargs)
        return m

    def get_instr_version(self):
        return self.instr_query("*IDN?",delay = 3).strip()

    @classmethod
    def get_rm_list_resource(cls):
        rm = visa.ResourceManager()
        rs_list = rm.list_resources()
        rm.close()
        return rs_list

    @classmethod
    def get_gpib_addr(cls):
        devices_list = cls.get_rm_list_resource()
        for instr_addr in devices_list:
            try:
                instr = handle_instr(instr_addr)
                instr_info = instr.get_instr_version()
                instr.instr_close()
                m=cls.instr_name_p.match(instr_info)
                if m:
                    return instr_addr
            except:
                pass
        return None

    @classmethod
    def instr_addr_check(cls, instr_addr):
        devices_list = cls.get_rm_list_resource()
        if instr_addr in devices_list:
            instr = handle_instr(instr_addr)
            instr_info = instr.get_instr_version()
            instr.instr_close()
            m=cls.instr_name_p.match(instr_info)
            if m:
                return True
            else:
                return False
        else:
            return False

    '''
    gpib_addr_num int type : gpib addr
    cls : handle_instr
    from instr import handle_instr
    检查 gpib地址，或者扫描gpib
    gpib_addr_num int type : gpib addr
    '''
    @classmethod
    def device_scan(cls, gpib_addr_num = None):
        if gpib_addr_num:
            instr_addr = "GPIB0::{0}::INSTR".format(gpib_addr_num)
        else:
            instr_addr = None
        if cls.instr_addr_check(instr_addr):
            print("{0} check OK".format(cls.__name__))
            print(instr_addr)
            return instr_addr
        else:
            instr_addr= cls.get_gpib_addr()
            if not instr_addr:
                print("Cannot Find {0}".format(cls.__name__))
                return None
            else:
                print("{0} find another addr OK".format(cls.__name__))
                print(instr_addr)
                return instr_addr

    def instr_close(self):
        self.instr.close()

    def instr_rm_close(self):
        self.instr.close()
        # session close
        self.rm.close()

