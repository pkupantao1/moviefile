# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')  #改变标准输出的默认编码 ,如果报错请加入此行
# -*- coding: utf-8 -*-

# ubuntu下apt-get mysql-server mysql-client libmysqlclient-dev 三个包
# service mysqld status
# python 安装包：  pip install pymysql mysql-connector

import time,os,sys
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkinter.ttk import Progressbar
import stat
import shutil
import os.path

# import MySQLdb
import pymysql

FontStyle=font=('Times New Roman', 12)
Host='127.0.0.1'
User='root'
Pswd='root'
Port=3306
DB='lotus_db'   #修改成你的dbname

class MySQLAction(object):
    conn=None
    cousor=None

    def __init__(self,host,user,passwd,port,db,charset='utf8'):
        self.Host=host
        self.User=user
        self.Pswd=passwd
        self.Port=port
        self.Charset=charset
        self.DB=db
        pass

    def __del__(self):
        self.conn.close()
        self.cursor.close()
        pass

    def connect(self):
        IsConnectOK=False
        try:
            self.conn=pymysql.connect(host=self.Host,user=self.User,password=self.Pswd,port=self.Port,db=self.DB)
        except pymysql.Error as e:
            errorMsg='Cannot connect to MySql Server\nError(%s):%s'%(e.args[0],e.args[1])
            print(errorMsg)
            return IsConnectOK
            # exit(2)
        self.cursor=self.conn.cursor()
        IsConnectOK=True
        return IsConnectOK

    def get_OneLine(self, sql, params=()):   #获取第一行返回信息
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            # self.close()
        except Exception as e:
            print(e)
        return result

    def get_ALL(self,sql):
        tuple_data = ()
        try:
            self.connect()
            self.cursor.execute(sql)
            tuple_data = self.cursor.fetchall()
            # self.close()
        except Exception as e:
            print(e)
        return tuple_data

    def get_AllLine(self, sql,params=()):
        tuple_data = ()
        try:
            self.connect()
            self.cursor.execute(sql,params)

            tuple_data = self.cursor.fetchall()
            # self.close()
        except Exception as e:
            print(e)
        return tuple_data

    def insert(self, sql, params=()):
        return self.__edit(sql, params)
        pass
    def update(self, sql, params=()):
        return self.__edit(sql, params)
        pass
    def delete(self, sql, params=()):
        return self.__edit(sql, params)
        pass
    def __edit(self, sql, params):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql, params)
            self.conn.commit()
            # self.close()
        except Exception as e:
            print(e)
            self.conn.rollback()    #数据库里做修改后 ( update ,insert , delete)未commit 之前 使用rollback 可以恢复数据到修改之前,相当于失败后什么都没有发生过

        return count

    # def exec(self,sqlcommand):    #执行仅提交，无需反馈
    #     try:
    #         self.curser.execute(sqlcommand)
    #         self.conn.commit()
    #     except:
    #         self.conn.rollback()
    #     pass
    #
    def query(self,sqlcommand): #查询数据
        self.curser.execute(sqlcommand)
        return self.curser.fetchall()
        pass



class MainUI:
    fileNamelist=[]
    filesizelist=[]   #filesize show by byte
    fileCIDlist=[]
    def __init__(self):
        self.IsCreateNewData=False
        self.root = Tk()
        self.root.resizable(width=False, height=False)
        self.root.title("MovieFile")
        width = 720
        height = 640
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth-width)/2, (screenheight-height)/2)
        self.root.geometry(alignstr)
        #self.root.iconbitmap("/root/lotus_ui/myicon.ico")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)    #表示设置窗口内第几列控件的缩放比例，拖动时会有变化
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)
        self.root.columnconfigure(4, weight=1)
        self.root.columnconfigure(5, weight=1)
        self.root.columnconfigure(6, weight=1)
        self.root.columnconfigure(7, weight=1)

        # self.root.rowconfigure(5, weight=1)     #只设置index4的缩放，其他行不随缩放变化

        self.buttonWJX = Button(self.root, text="★  ★   ★   ★", width=10, state='disable')

        self.labelInput = Label(self.root, text="miner", font=FontStyle, height=1)
        self.labelInputDay = Label(self.root, text="days", font=FontStyle, height=1)
        self.labelInputMoney = Label(self.root, text="price", font=FontStyle, height=1)
        self.labelbalance = Label(self.root, text="balance", font=FontStyle, height=1)
        self.inputMiner = Entry(self.root, state='normal', width=10, font=('Times New Roman', 12))   #输入控件
        self.inputDay = Entry(self.root, state='normal', width=10, font=('Times New Roman', 12))
        self.inputMoney = Entry(self.root, state='normal', width=10, font=('Times New Roman', 12))
        self.labelbalanceValue = Label(self.root, text='FIL 35.01', width=10, font=('Times New Roman', 12))

        self.buttonStart = Button(self.root, text="Start", width=10, font=FontStyle, state='normal')
        self.buttonFileSelect = Button(self.root, text="Select", width=10, font=FontStyle, state='normal')
        # self.labelProgress = Button(self.root, text="Process", font=FontStyle, state='disable')

        style = ttk.Style()
        style.configure("Treeview", font=('Times New Roman', 10), rowheight=20)
        style.configure('Treeview.Heading',font=('Times New Roman', 10))
        self.itemList = ttk.Treeview(self.root, columns=['1'], show='headings', height=5)
        self.itemList.column("1", anchor='w')
        self.itemList.heading("1", text='Files List:')

        self.vbar = ttk.Scrollbar(self.root, orient=VERTICAL, command=self.itemList.yview)
        self.itemList.configure(yscrollcommand=self.vbar.set)
        self.vbar.grid(row=5,column=3,sticky=NS+E,pady=6,padx=5)
        self.progressBar = Progressbar(self.root, maximum=100, value=0, mode="indeterminate")

        self.buttonWJX.grid(row=0,column=0,columnspan=4,sticky=W+E+N+S,padx=5,pady=5)



        self.labelInput.grid(row=1, column=0, columnspan=1, sticky=W + E + S, padx=5, pady=0)
        self.labelInputDay.grid(row=1, column=1, columnspan=1, sticky=W + E + S, padx=5, pady=0)
        self.labelInputMoney.grid(row=1, column=2, columnspan=1, sticky=W + E + S, padx=5, pady=0)
        self.labelbalance.grid(row=1, column=3, columnspan=1, sticky=W + E + S, padx=5, pady=0)

        self.inputMiner.grid(row=2, column=0, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)
        self.inputDay.grid(row=2, column=1, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)
        self.inputMoney.grid(row=2, column=2, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)
        self.labelbalanceValue.grid(row=2, column=3, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)

        # self.buttonStart.grid(row=2, column=3, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)

        self.buttonFileSelect.grid(row=3, column=0, columnspan=2, sticky=W + E + N + S, padx=5, pady=5)
        # self.labelProgress.grid(row=3, column=2, columnspan=2, sticky=W + E + N + S, padx=5, pady=5)

        self.progressBar.grid(row=3, column=2, columnspan=2, sticky=W + E + N, padx=5, pady=5)
        self.itemList.grid(row=5, column=0, columnspan=4, rowspan=1, sticky=W + E + N + S, padx=5, pady=5)





        mysqlPanel = ttk.LabelFrame(text='MySQL Query')
        self.buttonStore = Button(mysqlPanel, text="Store", width=5, font=FontStyle,state='normal' if self.IsCreateNewData else 'disable')
        self.inputQuery = Entry(mysqlPanel, state='normal', width=20, font=('Times New Roman', 12))
        self.buttonSearch = Button(mysqlPanel, text="Search", width=5, font=FontStyle, state='normal')
        # self.buttonDownload = Button(mysqlPanel, text="Download", width=10, font=FontStyle, state='disable')
        # self.buttonStatic = Button(mysqlPanel, text="Static", width=10, font=FontStyle, state='disable')

        self.buttonStore.grid(row=7, column=0, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)
        self.inputQuery.grid(row=7,column=1,columnspan=2,stick='NSEW',padx=1,pady=1)
        self.buttonSearch.grid(row=7, column=3, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)
        # self.buttonDownload.grid(row=7, column=2, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)
        # self.buttonStatic.grid(row=7, column=3, columnspan=1, sticky=W + E + N + S, padx=5, pady=5)

        mysqlPanel.grid(row=6,column=0, columnspan=4,sticky=W + E + N + S, padx=4, pady=4)
        self.tree=ttk.Treeview(mysqlPanel,columns=['1'], show='headings', height=50)#表格
        self.tree["columns"]=("FileName","FileSize","FileCIDValue")
        self.tree.column("FileName",width=400)   #表示列,不显示
        self.tree.column("FileSize",width=100)
        self.tree.column("FileCIDValue",width=200)
        self.tree.heading('FileName',text='FileName')
        self.tree.heading('FileSize',text='FileSize')
        self.tree.heading('FileCIDValue',text='FileCIDValue')

        self.tree.grid(row=8,column=0, columnspan=4,sticky='NSEW', padx=4, pady=4)


#button click event
        self.buttonFileSelect.configure(command=self.onFileSelect)
        self.buttonStore.configure(command=self.onStoreDB)
        self.buttonSearch.configure(command=self.onQueryDB)

        self.inputMiner.insert(0,"f090869")
        self.inputDay.insert(0,180)
        self.inputMoney.insert(0,0.00000001)

        self.onFileSelect()    #add here to get Input focus
        self.root.mainloop() if self.onDbConnect()==True else exit(2)



    def file_location(self):
        fileslist = filedialog.askopenfilenames(parent=self.root, title='Choose files')
        fileslist = self.root.tk.splitlist(fileslist)
        print(fileslist)
        return fileslist

    def runCmd_getFileCIDValue(self,filePath):
        CIDValue=''
        os.system('lotus client import {}'.format(filePath))
#add your debug code here!!
        return CIDValue

    def runCmd_deal(self,CIDValue,MinerValue,PriceValue,Duration):
        os.system('lotus client deal <{cid}> <{miner}> <{price}> <{dur}>'.format(cid=CIDValue,miner=MinerValue,price=PriceValue,dur=Duration))
#add your debug code here!!
        return True

    def onFileSelect(self):
        self.fileNamelist.clear()
        self.filesizelist.clear()
        self.fileCIDlist.clear()
        if len(self.inputMiner.get().strip())==0 or len(self.inputDay.get().strip())==0 or len(self.inputMoney.get().strip())==0:
            messagebox.showerror(title='Input Notice',message='Please Input Parameters Firstly~~')#返回'True','False'
            return


        self.itemList.delete(*self.itemList.get_children())
        for file in self.file_location():
            self.itemList.insert("", 'end', values=(file))
            self.fileNamelist.append(os.path.basename(file))
            self.filesizelist.append(os.stat(file)[stat.ST_SIZE])
            self.fileCIDlist.append('CID{}'.format(os.stat(file)[stat.ST_SIZE]))


        print(self.fileNamelist)
        print(self.filesizelist)


        for i in range(100):
            # 每次更新加1
            self.progressBar['value'] = i + 1
            # 更新画面
            self.progressBar.update()
            time.sleep(0.01)
        self.IsCreateNewData=True
        self.buttonStore['state']='normal' if self.IsCreateNewData else 'disable'
        self.inputMiner.delete(0,len(self.inputMiner.get())+1)
        self.inputDay.delete(0,len(self.inputDay.get())+1)
        self.inputMoney.delete(0,len(self.inputMoney.get())+1)


    def onStoreDB(self):
#create a table
        sqlcommand='INSERT INTO filetbl(id,filename,filesize,filecid) VALUES(%s,%s,%s,%s)'
        for idx in range(len(self.filesizelist)):
            print(self.fileNamelist[idx],self.filesizelist[idx],self.fileCIDlist[idx])
            sz=self.pMySql.insert(sqlcommand,('',self.fileNamelist[idx],self.filesizelist[idx],self.fileCIDlist[idx]))
            if sz!=1:  #success return 1 , fail return 0
                messagebox.showerror(title='Insert DB',message='Insert Info To DataBase Failed~~')#返回'True','False'
                return
        self.buttonStore['state']='disable'
        pass

    def onQueryDB(self):
        [self.tree.delete(item) for item in self.tree.get_children()]   #clean TreeView Contents
        if len(self.inputQuery.get())==0:
            sqlcommand="SELECT * FROM filetbl"
        else:
            # sqlcommand="SELECT * FROM filetbl WHERE {}=%s".format('filecid')
            # result=self.pMySql.get_AllLine(sqlcommand,('CID142356'))
            #模糊查询
            sqlcommand="SELECT * FROM filetbl WHERE {fn} LIKE '%{qs}%' OR {fs} LIKE '%{qs}%' OR {fc} LIKE '%{qs}%'".format(fn='filename',fs='filesize',fc='filecid',qs=self.inputQuery.get())
        result=self.pMySql.get_ALL(sqlcommand)
        print(result)
        for i in range(len(result)):
            self.tree.insert('', i, text=i ,values=(result[i][1], result[i][2],result[i][3]))
        pass

    def onDbConnect(self):
        self.pMySql=MySQLAction(Host,User,Pswd,Port,DB)
        if not self.pMySql.connect():
            print('Connect MySQL Failed~~~')
            messagebox.showwarning(title='MySQL Connection Info',message='Connect MySQL Failed~~~Please Check It~~')#返回'True','False'
            return False
        else:
            print('Connect MySQL Successfully~~~')
            messagebox.showinfo(title='MySQL Connection Info',message='Connect MySQL Successfully~~')#返回'True','False'
            sqlcommand='CREATE TABLE IF NOT EXISTS filetbl(id INT(11) NOT NULL AUTO_INCREMENT,filename VARCHAR(255) NOT NULL,filesize bigint(20) NOT NULL,fileCIDValue VARCHAR(255) NOT NULL,PRIMARY KEY (id))'
            self.pMySql.insert(sqlcommand)
            print("CREATE TABLE OK")
            return True


if __name__ == '__main__':
    ui = MainUI()

