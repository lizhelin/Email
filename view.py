# coding: utf-8
from tkinter import *
from tkinter.messagebox import *
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from tkinter import scrolledtext
from tkinter import filedialog
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib

 
class receiveFrame(Frame):  # 继承Frame类
    
    def __init__(self, master, username, password, server):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.username = username
        self.password = password
        self.server = server
        self.state = StringVar() #连接状态变量
        self.state.set('等待连接')
        self.mailcount = StringVar() #邮件数量变量
        self.mailmessage = StringVar() #邮件内容变量
        self.mailmessage.set('请选择邮件')
        self.indexmessage = StringVar() #邮件列表变量
        self.createPage()
        self.messagedict = {}
        self.boxdict = {}
        self.content_list = []
        self.index_list = []

    def createPage(self):
        Label(self, text='服务连接状态：').grid(row=0, sticky='W', pady=3)
        Label(self, textvariable=self.state).grid(row=0, column=1, sticky='W', pady=3)
        Label(self, text='邮箱空间状态：').grid(row=1, sticky='W', pady=3)
        Label(self, textvariable=self.mailcount).grid(row=1, column=1, sticky='W', pady=3)
        self.listbox = Listbox(self, listvariable=self.indexmessage, height=15, width=25)
        self.listbox.bind('<Button-1>',self.mailvision)
        self.listbox.grid(row=2, sticky='W', padx=3, pady=3)
        #Label(self, textvariable=self.mailmessage, height=15, width=85, bg='white', justify='left',anchor='nw',wraplength=1000).grid(row=2, column=1, sticky='W', pady=3)
        self.mtext = scrolledtext.ScrolledText(self, width=85, height=20)
        self.mtext.grid(row=2, column=1, sticky='W', pady=3)
        Button(self, text='接收邮件', command=self.clickrecebutton).grid(row=3, sticky='w' + 'e', pady=3)

    def clickrecebutton(self): 
        # 连接到POP3服务器:
        try:
            self.boxdict.clear()
            self.content_list.clear()
            self.index_list.clear()
            
            server = poplib.POP3_SSL(self.server)
            # 可以打开或关闭调试信息:
            # server.set_debuglevel(1)
            # 可选:打印POP3服务器的欢迎文字:
            self.state.set(server.getwelcome().decode('utf-8')[:40])
            # 身份认证:
            server.user(self.username)
            server.pass_(self.password)
            # stat()返回邮件数量和占用空间:
            self.mailcount.set('邮件总数: %s. 占用空间: %s' % server.stat())
            resp, mails, octets = server.list()
            index = len(mails)+1
            for item in range(index-20,index):
                try:
                    resp, lines, octets = server.retr(item)
                    # lines存储了邮件的原始文本的每一行,
                    # 可以获得整个邮件的原始文本:
                    msg_content = b'\r\n'.join(lines).decode('utf-8')
                    # 稍后解析出邮件:
                    msg = Parser().parsestr(msg_content)
                    self.boxdict[item] = self.print_info(msg,0).copy()
                    self.index_list.append(self.boxdict[item]['Subject'])
                except BaseException:
                    messagebox.showwarning(title='系统消息', message='接收邮件信息过长')
            print(self.boxdict)
            self.indexmessage.set(tuple(self.index_list))
            server.quit()
        except Exception as e:
            #print('请核对登录信息/接收邮件信息过长')
            messagebox.showwarning(title='系统消息', message='请核对登录信息')
    
    def mailvision(self,event):
        self.mtext.delete(1.0, END)
        value = self.listbox.get('active')
        for key in self.boxdict :
            if value == self.boxdict[key]['Subject'] :
                '''
                self.mailmessage.set('发件人：'+self.boxdict[key]['From']+'\n'
                                     +'收件人：'+self.boxdict[key]['To']+'\n'
                                     +'主题：'+self.boxdict[key]['Subject']+'\n'
                                     +self.boxdict[key]['content']
                                     )
                '''
                self.mtext.insert(END, '发件人：'+self.boxdict[key]['From']+'\n'
                                     +'收件人：'+self.boxdict[key]['To']+'\n'
                                     +'主题：'+self.boxdict[key]['Subject']+'\n'
                                     +self.boxdict[key]['content'])
    
    def print_info(self,msg, indent):
        if indent == 0:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    if header=='Subject':
                        value = self.decode_str(value)
                    else:
                        hdr, addr = parseaddr(value)
                        name = self.decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                self.messagedict[header] = value
        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                self.print_info(part, indent + 1)
        else:
            content_type = msg.get_content_type()
            if content_type=='text/plain' or content_type=='text/html':
                content = msg.get_payload(decode=True)
                charset = self.guess_charset(msg)
                if charset:
                    self.messagedict['content'] = content.decode(charset)
            else:
                self.content_list.append(content_type)
                self.messagedict['content_type'] = self.content_list
        if indent == 0 :
            return self.messagedict
        
    def decode_str(self,s):
    
    # decode_header()返回一个list  偷懒，只取了第一个元素
    
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value
    
    def guess_charset(self,msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset
 
class sendFrame(Frame):  # 继承Frame类

    def __init__(self, master, username, password, cnf={}, **kw):
        Frame.__init__(self, master, cnf={}, **kw)
        self.root = master  # 定义内部变量root
        self.username = username
        self.password = password
        self.mailall = MIMEMultipart()
        self.var = StringVar()
        self.e_receiver = StringVar()
        self.e_copyreceiver = StringVar()
        self.e_theme = StringVar()
        self.createPage()
 
    def createPage(self):
        
        Label(self, text='收件人').grid(row=0, sticky='W', pady=3)
        Entry(self, textvariable=self.e_receiver, show=None, width=105).grid(row=0, column=1, sticky='W', pady=3)
        
        Label(self, text='抄送人').grid(row=1, sticky='W', pady=3)
        Entry(self, textvariable=self.e_copyreceiver, show=None, width=105).grid(row=1, column=1, sticky='W', pady=3)
        
        Label(self, text='主题').grid(row=2, sticky='W', pady=3)
        Entry(self, textvariable=self.e_theme, show=None, width=105).grid(row=2, column=1, sticky='W', pady=3)
        
        Button(self, text='附件上传', command=self.clickupdatebutton).grid(row=4, sticky='W', pady=3)
        Label(self, textvariable=self.var).grid(row=4, column=1, sticky='W', pady=3)
        
        Label(self, text='邮件正文').grid(row=5, sticky='W', pady=4)
        self.text = scrolledtext.ScrolledText(self, width=103, height=15)
        self.text.grid(row=5, column=1, sticky='W', pady=4)
        Button(self, text='发送邮件', command=self.clicksendbutton).grid(row=6, column=1, sticky='w' + 'e', pady=3)

    def clickupdatebutton(self):
        file_path = filedialog.askopenfilename()
        file_path = file_path.replace('/', '\\\\')
        self.var.set(file_path)
        self.mailAttach = '测试邮件附件内容'
        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/', 1)
        filename = file_path  # 附件文件所在路径
        attfile = MIMEImage(open(file_path, 'rb').read(), _subtype=subtype)
        attfile.add_header('Content-Disposition', 'attachment', filename=os.path.split(file_path)[1])
        self.mailall.attach(attfile)
    
    def clicksendbutton(self):
        receiver = list()
        copyReceive = list()
        # global switch, username, password, receiver, copyReceive, sender, mailall, mailcontent
        username = self.username
        sender = self.username
        password = self.password
        checkmaillist = []
        checkmaillist.append(username)
        checkmaillist.extend(self.e_receiver.get().split(';'))
        checkmaillist.extend(self.e_copyreceiver.get().split(';'))
        
        for item in checkmaillist :
            if not self.is_valid_email(item) is True :
                return messagebox.showwarning(title='系统消息', message='请输入正确的邮箱格式')
        
        receiver.append(self.e_receiver.get())
        copyReceive.append(self.e_copyreceiver.get())
        self.mailall['Subject'] = self.e_theme.get()
        self.mailall['From'] = sender  # 发件人邮箱
        self.mailall['To'] = ';'.join(receiver)  # 收件人邮箱,不同收件人邮箱之间用;分割
        self.mailall['CC'] = ';'.join(copyReceive)  # 抄送邮箱
        # print(type(self.text))
        mailcontent = self.text.get('1.0', 'end')
        self.mailall.attach(MIMEText(mailcontent, 'html', 'utf-8'))
        fullmailtext = self.mailall.as_string()
        try:
            smtp = smtplib.SMTP()
            smtp.connect('smtp.163.com')
            smtp.login(username, password)
            smtp.sendmail(sender, receiver[0].split(';') + copyReceive[0].split(';'), fullmailtext)
            # smtp.sendmail(sender, receiver+copyReceive, fullmailtext)
            smtp.quit()
            messagebox.showinfo(title='系统消息', message='邮件发送成功')
        except smtplib.SMTPException:
            messagebox.showwarning(title='系统消息', message='邮件发送失败，请检查发送地址和授权密码是否正确')
        except TypeError :
            messagebox.showwarning(title='系统消息', message='请确认邮件信息是否全部填写')
    
    def is_valid_email(self, addr):
        if re.match(r'^([\w]+\.*)([\w]+)\@[\w]+\.\w{3}(\.\w{2}|)$', addr) or addr == '':
            return True
        else :
            return False    
