#!/usr/bin/env python
# -*- coding: utf-8 -*-

#pip install PyAutoGUI==0.9.38
import pyautogui
import time
import keyboard

############ Setting ############
# one second pause after every pyautogui function
# pyautogui.PAUSE = 1
############ Function ############
# pyautogui.moveTo(x,y,duration_time) : absolute 
# pyautogui.moveRel(ix,iy,duration_time) : relative
# pyautogui.clik(x, y, button = "left") : keyword "left" "right" and "middle"
# pyautogui.rightClick(x,y), pyautogui.leftClick(x, y), pyautogui.middleClick(x, y)
# pyautogui.dragTo(x,y, duration_time) pyautogui.drageRel
# pyautogui.typewrite("hello world")
# pyautogui.keyDown('shift'); pyautogui.press('4'); pyautogui.keyUp('shift')
# pytautogui.hotkey("ctrl", "c")

def pygui_get_screen_size():
    return pyautogui.size()
    # return (1920, 1080)

def pygui_get_cursor_pos():
    return pyautogui.position()

def on_press_key_callback(event):
    print("name: ",event.name)
    print("code: ",event.scan_code)

def keyboard_hook_key():
    # https://github.com/boppreh/keyboard
    keyboard.on_press(on_press_key_callback)
    keyboard.wait()

def keyboard_press_to_get_position(key, suppress = True):
    # block until press enter
    keyboard.wait(key, suppress)
    return pygui_get_cursor_pos()

def e_draw_rectangle():
    # 打开画图工具
    time.sleep(5)
    pyautogui.click()    # click to put drawing program in focus
    distance = 200
    while distance > 0:
        pyautogui.dragRel(distance, 0, duration=0.2)   # move right
        distance = distance - 5
        pyautogui.dragRel(0, distance, duration=0.2)   # move down
        pyautogui.dragRel(-distance, 0, duration=0.2)  # move left
        distance = distance - 5
        pyautogui.dragRel(0, -distance, duration=0.2)  # move up

class keyboard_hook():
    def __init__(self, key, callback, suppress = True ):
        self.hook_handler = keyboard.on_press_key(key, callback, suppress)
        # example of callback
        # self.hook_handler = keyboard.on_press_key(key, self._callback, suppress=True)

    def _callback(self, event):
        print(event)
        # !callback 函数不能含有return，否则 supresse 不生效
        # return True

    def __enter__(self):
        print("zhixing enter")
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        keyboard.unhook_key(self.hook_handler)

if __name__ == "__main__":
    # print(keyboard_press_to_get_position('a'))
    # with keyboard_hook("a", callback) as k:
        # keyboard.wait("b", suppress=True)
        pass
