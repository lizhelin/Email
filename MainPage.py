# coding: utf-8
from tkinter import *
from view import *  # 菜单栏对应的各个子页面

 
class MainPage(object):

    def __init__(self, master, username, password, server):
        self.root = master  # 定义内部变量root
        self.root.geometry('%dx%d' % (800, 400))  # 设置窗口大小
        self.username = username
        self.password = password
        self.server = server
        self.createPage()
 
    def createPage(self):
        self.receivePage = receiveFrame(self.root,self.username,self.password,self.server)  # 创建不同Frame
        self.sendPage = sendFrame(self.root, self.username, self.password)
        self.receivePage.pack(fill = 'both')  # 默认显示数据录入界面
        menubar = Menu(self.root)
        menubar.add_command(label='收件箱', command=self.receiveData)
        menubar.add_command(label='发邮件', command=self.sendData)
        self.root['menu'] = menubar  # 设置菜单栏
 
    def receiveData(self):
        self.receivePage.pack(fill = 'both')
        self.sendPage.pack_forget()
 
    def sendData(self):
        self.receivePage.pack_forget()
        self.sendPage.pack(fill = 'both')

 
