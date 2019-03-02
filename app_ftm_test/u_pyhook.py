#!/usr/bin/env python
# -*- coding: utf-8 -*-

# dependency : pywin32 , pyHook
import PyHook3 as pyHook
import pythoncom
import time

'''
MouseAll = property(fset=SubscribeMouseAll) 
MouseAllButtons = property(fset=SubscribeMouseAllButtons) 
MouseAllButtonsUp = property(fset=SubscribeMouseAllButtonsUp) 
MouseAllButtonsDown = property(fset=SubscribeMouseAllButtonsDown) 
MouseAllButtonsDbl = property(fset=SubscribeMouseAllButtonsDbl) 

MouseWheel = property(fset=SubscribeMouseWheel) 
MouseMove = property(fset=SubscribeMouseMove) 
MouseLeftUp = property(fset=SubscribeMouseLeftUp) 
MouseLeftDown = property(fset=SubscribeMouseLeftDown) 
MouseLeftDbl = property(fset=SubscribeMouseLeftDbl) 
MouseRightUp = property(fset=SubscribeMouseRightUp) 
MouseRightDown = property(fset=SubscribeMouseRightDown) 
MouseRightDbl = property(fset=SubscribeMouseRightDbl) 
MouseMiddleUp = property(fset=SubscribeMouseMiddleUp) 
MouseMiddleDown = property(fset=SubscribeMouseMiddleDown) 
MouseMiddleDbl = property(fset=SubscribeMouseMiddleDbl) 

KeyUp = property(fset=SubscribeKeyUp) 
KeyDown = property(fset=SubscribeKeyDown) 
KeyChar = property(fset=SubscribeKeyChar) 
KeyAll = property(fset=SubscribeKeyAll) 
'''
click_count = 0
def OnMouseLeftDown(event):
    # print("MessageName: ", event.MessageName)
    # print("Message: ", event.Message)
    # called when mouse events are received
    # print( 'MessageName:',event.MessageName)
    # print( 'Message:',event.Message)
    # print( 'Time:',event.Time)
    # print( 'Window:',event.Window)
    # print( 'WindowName:',event.WindowName)
    print( 'Position:',event.Position)
    print( 'Wheel:',event.Wheel)
    print( 'Injected:',event.Injected)
    print( '---')
    # return True to pass the event to other handlers
    # 这儿如果返回 False ，则鼠标事件将被全部拦截
    global click_count
    click_count = click_count +1
    if click_count == 10:
       global hm
       global flag
       # 取消钩子
       # hm.UnhookMouse()
       flag = False
    return True

hm = pyHook.HookManager()
flag = True

def main():
    global hm
    # create a hook manager
    # hm = pyHook.HookManager()
    # watch for mouse left down
    hm.MouseLeftDown = OnMouseLeftDown
    # set the mouse hook
    hm.HookMouse()
    # set the keyboard hook
    hm.HookKeyboard()
    # pythoncom.PumpMessages()
    while (flag):
        time.sleep(0.01)
        pythoncom.PumpWaitingMessages()
    else:
        hm.UnhookMouse()
        # del hm
        print("quit while")
    # pythoncom.PumpMessages()


if __name__ == "__main__":
    main()
