import pandas as pd
import numpy as np
from uiautomation import WindowControl, MenuControl
import win32gui
import win32con
import pyautogui
import random


# 获取窗口句柄并打开窗口
def getHwnd():
    hwnd = win32gui.FindWindow('WeChatMainWndForPC', '微信')
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWMINIMIZED)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    win32gui.SetForegroundWindow(hwnd)
    return hwnd


# 复位（自动回复之后自动点击消息列表第二个聊天窗口）
def fuwei(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    leftpoint = left + 155
    toppoint = top + 150
    pyautogui.moveTo(leftpoint, toppoint)
    pyautogui.click()
    return '已复位'


getHwnd()
wx = WindowControl(Name="微信")
wx.SwitchToThisWindow()
hw = wx.ListControl(Name="会话")

# 持续循环监听未读消息
while 1:
    try:
        we = hw.TextControl(searchDepth=4)
        # 如果存在未读消息
        if we.Name:
            random()
            we.Click(simulateMove=False)
            # 获取当前最后一条消息
            last_msg = wx.ListControl(Name='消息').GetChildren()[-1].Name
            if last_msg == '你好':
                wx.SendKeys('你好，才是真的好{ENTER}')
                fuwei(getHwnd())
            elif last_msg == '123':
                wx.SendKeys('456{ENTER}')
                fuwei(getHwnd())
            elif last_msg == '测试':
                wx.SendKeys('测试成功{ENTER}')
                fuwei(getHwnd())
            else:
                wx.SendKeys('无法匹配{ENTER}')
                fuwei(getHwnd())
    except Exception as exc:
        print(exc)