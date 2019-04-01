# coding: utf-8
from tkinter import *
from tkinter.messagebox import *
from MainPage import *
import re 

 
class LoginPage(object):

    def __init__(self, master):
        self.root = master  # 定义内部变量root
        self.root.geometry('%dx%d' % (300, 200))  # 设置窗口大小
        self.root.resizable(0, 0)
        self.username = StringVar()
        self.password = StringVar()
        self.server = StringVar()
        self.createPage()
 
    def createPage(self):
        self.page = Frame(self.root)  # 创建Frame
        self.page.pack()
        Label(self.page).grid(row=0, stick=W)
        Label(self.page, text='邮箱账户: ').grid(row=1, stick=W, pady=10)
        Entry(self.page, textvariable=self.username).grid(row=1, column=1, stick=E)
        Label(self.page, text='服务器地址: ').grid(row=2, stick=W, pady=10)
        Entry(self.page, textvariable=self.server).grid(row=2, column=1, stick=E)
        Label(self.page, text='授权密码: ').grid(row=3, stick=W, pady=10)
        Entry(self.page, textvariable=self.password, show='*').grid(row=3, column=1, stick=E)
        Button(self.page, text='登陆', command=self.loginCheck).grid(row=4, stick=W, pady=10)
        Button(self.page, text='退出', command=self.page.quit).grid(row=4, column=1, stick=E)
       

    def loginCheck(self):
        username = self.username.get()
        password = self.password.get()
        server = self.server.get()
        #print(self.valid_email())
        if self.valid_email() is True:
        #if True:
            self.page.destroy()
            MainPage(self.root,username,password,server)
        else:
            showinfo(title='错误', message='请输入正确的邮箱格式')

    def valid_email(self):
        if re.match(r'^([\w]+\.*)([\w]+)\@[\w]+\.\w{3}(\.\w{2}|)$', self.username.get()):
            return True
        else :
            return False
