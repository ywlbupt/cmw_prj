#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import tkinter as tk                 # 导入 Tkinter 库
from tkinter import ttk

from tkinter import scrolledtext        # 导入滚动文本框的模块
from threading import Thread
import time

class ftm_frame(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.md_strVar = tk.StringVar()
        self.band_strVar = tk.StringVar()          
        self.ch_strVar = tk.StringVar()          
        self.bw_strVar = tk.StringVar()
        self.icq_strVar = tk.StringVar()          
        self.rgi_strVar = tk.StringVar()          

        self.promt_text = tk.StringVar()
        self.res_text = tk.StringVar()
        self.res_scr = None

        # optional "LTE" or "WCDMA"
        self.md_strVar.set("LTE")
        self.band_strVar.set("1")
        self.ch_strVar.set("18050,18300")
        self.bw_strVar.set("10MHz")
        self.icq_strVar.set(" 1-10 ,34570, 35580 , 5-8")
        self.rgi_strVar.set("50-54")

        self.createWidgets()
        pass

    def param_frame(self, parent):
        row_num =0
        mds = ["LTE", "WCDMA"]
        md_label = tk.Label(parent, width = 10,text = "md").grid(column=1,row =row_num, sticky = tk.W)
        md_cbox = ttk.Combobox(parent, value = mds,width = 30, state = "readonly", textvariable = self.md_strVar )
        md_cbox.grid(column = 2, row = row_num ,sticky = tk.W)
        md_cbox.current(0) # default index
        md_cbox.bind('<<ComboboxSelected>>', self.md_cbox_select)
        row_num = row_num+1
        band_label = tk.Label(parent,width = 10, text="Test Band").grid(column=1,row =row_num, sticky = tk.W)
        band_entry = ttk.Entry(parent, width = 30, textvariable = self.band_strVar).grid(column = 2, row = row_num, sticky = tk.W)
        row_num = row_num+1
        ch_label = tk.Label(parent, width = 10,text = "ch List").grid(column=1,row =row_num, sticky = tk.W)
        ch_entry = ttk.Entry(parent, width = 30, textvariable = self.ch_strVar).grid(column = 2, row = row_num, sticky = tk.W)
        row_num = row_num+1
        bws = ["5MHz", '10MHz', "20MHz"]
        bw_label = tk.Label(parent, width = 10, text = "bw").grid(column=1,row =row_num, sticky = tk.W)
        bw_cbox = ttk.Combobox(parent, value = bws, width = 30, state = "readonly", textvariable = self.bw_strVar)
        bw_cbox.current(1)# default index
        # bw_cbox['state']="disable"
        bw_cbox.grid(column = 2, row=row_num, sticky = tk.W)
        row_num = row_num + 1
        icq_label = tk.Label(parent, width = 10,text = "icq List").grid(column=1,row =row_num, sticky = tk.W)
        icq_entry = ttk.Entry(parent, width = 30, textvariable = self.icq_strVar).grid(column = 2, row = row_num, sticky = tk.W)
        row_num = row_num + 1
        rgi_label = tk.Label(parent, width = 10,text = "rgi List").grid(column=1,row =row_num, sticky = tk.W)
        rgi_entry = ttk.Entry(parent, width = 30, textvariable = self.rgi_strVar).grid(column = 2, row = row_num, sticky = tk.W)

    def work_frame(self, parent):
        self.button_get_pos = ttk.Button(parent, text="Get_pos")
        self.button_get_pos.grid(column = 1,row =0 )
        self.button_icq_scan = ttk.Button(parent, text="icq_scan")
        self.button_icq_scan.grid(column = 1, row = 1)
        self.button_stop = ttk.Button(parent,text = "stop_scan")
        self.button_stop.grid(column = 1, row = 2)
        self.button_text_clear = ttk.Button(parent,text = "clear_text",command = self.res_scr_clear )
        self.button_text_clear.grid(column = 3, row = 3)

    def display_frame(self, parent):
        promt_label = tk.Label(parent, height =2, textvariable = self.promt_text)
        promt_label.pack(expand = "yes", anchor = "nw")

        scrolW = 50
        scrolH = 30
        self.res_scr = scrolledtext.ScrolledText(parent,width = scrolW, height = scrolH, wrap=tk.WORD)
        # self.res_scr = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
        self.res_scr.pack(expand = "yes", fill="both")
        self.res_scr["state"] = "disabled"

        self.button_ftm_set = ttk.Button(parent, text="ftm_set" )
        self.button_ftm_set.pack()

    def createWidgets(self):
        _param_frame = tk.Frame(self)
        _param_frame.pack()
        self.param_frame(_param_frame)

        _work_frame = tk.Frame(self)
        _work_frame.pack(fill = "x", expand = "no")
        self.work_frame(_work_frame)

        _display_frame = tk.Frame(self)
        _display_frame.pack(side = "bottom", fill = "both", expand="yes")
        self.display_frame(_display_frame)
        pass

    def md_cbox_select(self, event):
        self.display_promt(self.md_strVar.get())
        self.display_res_append(self.md_strVar.get())
        self.display_res_append(str(self.get_ftm_param()))
        pass

    def get_ui_ftm_param(self):
        ''' md, band, ch, bw '''
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

        param_dict = {
            "md"    : self.md_strVar.get(),
            "band"  : self.band_strVar.get(),
            "bw"    : self.bw_strVar.get(), # value for 10MHz, 5MHz, 20MHz
            # "r_ch"  : self.ch_strVar.get(),
            "r_ch"  : self.ch_strVar.get(),
            "r_icq" : self.icq_strVar.get(),
            "r_rgi" : self.rgi_strVar.get(),
        }
        return param_dict

    def register_get_pos(self, callback):
        self.button_get_pos.configure(command = callback)
    
    def register_icq_scan(self, callback):
        self.button_icq_scan.configure(command = callback)

    def register_stop_scan(self, callback):
        self.button_stop.configure(command = callback)

    def register_ftm_set(self, callback):
        self.button_ftm_set.configure(command = callback)

    def display_promt(self, text):
        self.promt_text.set(text)
    
    def display_res_append(self, text):
        self.res_scr["state"] = "normal"
        self.res_scr.insert(tk.END, text + "\n")
        self.res_scr["state"] = "disabled"

    def res_scr_clear(self):
        self.res_scr["state"] = "normal"
        self.res_scr.delete(1.0, tk.END)
        self.res_scr["state"] = "disabled"
        pass

class OOP():
    def __init__(self):
        self.win = tk.Tk()                       # 创建窗口对象的背景色
        self.win.title("Hello world Frame")
        # 窗口置顶
        self.win.wm_attributes('-topmost',1)
        # 窗口大小
        self.win.geometry ("400x800")
        self.win.resizable(width=False, height=True)    # 设置窗口宽度不可变，高度可变

        self._ftm_frame = None
        self.createWidgets()
    
    def createWidgets(self):
        tabControl = ttk.Notebook(self.win)     # Create Tab Control
        # add tab
        tab_ftm = ttk.Frame(tabControl)
        tabControl.add(tab_ftm, text = "FTM")
        
        tab_LTE = ttk.Frame(tabControl)
        tabControl.add(tab_LTE, text = "LTE")

        # ftm_tab add frame
        self._ftm_frame = ftm_frame(tab_ftm)
        self._ftm_frame.pack(side = "top", expand = "no", fill = "x", anchor = "nw")

        # layout : pack grid place
        tabControl.pack(expand="yes", fill = "both") # pack to make visible
    
    # 示例bind func
    def bind_notice_board(self, u_widgets):
        u_widgets.bind("<Button-1>", self.bind_callback) # 鼠标左键
        # u_widgets.focus_set()
        # u_widgets.bind("<Key>", self.bind_callback) # 键盘按键 键盘输入事件只发送给获得focus的widget，可以使用focus_set()函数
        # u_widgets.bind("<Motion>", self.bind_callback) # 鼠标移动，只有在widget 区域时才被触发
        pass

    # 示例bind func
    def bind_callback(self, event):
        ''' event.x, event.x_root'''
        self.display("click at {e.x_root}, {e.y_root}".format(e=event))

    def run(self):
        self.win.mainloop()

    def _msgBox(self):
        answer = mBox.askyesnocancel("python message info Box", "a python message box GUI created using tkinter :\n nice job" )
        print(answer)


# ===================
# Start GUI
# ===================

if __name__ == "__main__":
    oop = OOP()
    oop.run()
