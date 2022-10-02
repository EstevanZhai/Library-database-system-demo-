# -*- coding = utf-8 -*-
# @Time : 2020/12/29 1:21
# @Author : zhai_xiangyang
# @File : part_1.py
# @Software : PyCharm
import random

import requests
from bs4 import BeautifulSoup
import re
import xlwt
import xlrd
from xlutils.copy import copy
import os
import sqlite3


def getdata(basic_url):
    headers = {
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 78.0.3904.108Safari / 537.36'
    }  # 为了顺利爬取网页内容，需要进行UA伪装
    find_name = re.compile(r'<a href=".*" onclick=".*" title="(.*)">')  # 用于匹配书名
    find_link = re.compile(r'<a href="(.*)" onclick=".*" title=".*">')  # 用于匹配书本详情的链接
    find_inf = re.compile(r'<p class="pl">(.*)</p>')  # 用于匹配作者、出版社、定价等信息
    find_price = re.compile(r'(\d+[.?]\d?)')  # 用于匹配价格
    find_editor = re.compile(r'(.*?)/\d\d\d\d[-|年|/]\d*')  # 用于匹配作者和出版社信息
    find_markNum = re.compile('(.*)人评价')  # 用于匹配评价人数
    find_mark = re.compile(r'<span class="rating_nums">(.*)</span>')  # 用于匹配图书的评分
    find_overview = re.compile('<span class="inq">(.*)</span>')  # 用于匹配图书的概述
    alldata = []  # 对列表进行初始化，alldata将会用于存储上榜的所有图书的基本信息
    for i in range(0, 10):
        url = basic_url + str(i * 25)
        response = requests.get(url=url, headers=headers).text
        soup = BeautifulSoup(response, 'html.parser')  # 对网页进行解析
        for item in soup.find_all('tr', class_="item"):
            content = str(item)  # 此处需要类型转换
            name = re.findall(find_name, content)[0]  # 获取图书名称
            link = re.findall(find_link, content)[0]  # 获取书本的详情链接
            inf = re.findall(find_inf, content)[0].replace(" ", "")  # 获取图书的作者、出版社、定价等信息
            price = re.findall(find_price, inf)  # 获取图书价格
            editor = re.findall(find_editor, inf)  # 获取图书的作者和出版社信息
            markNum = re.findall(find_markNum, content)[0].replace(" ", "")  # 获取图书的评价人数
            mark = re.findall(find_mark, content)[0]  # 获取图书的评分
            overview = re.findall(find_overview, content)  # 获取图书的概述
            if random.random() < 0.75:
                have = "有"
            else:
                have = "无"
            data = []  # 初始化data列表，下方开始添加图书的基本信息
            data.append(name)
            if len(editor) != 0:  # 考虑到可能存在没有作者和出版社信息的情况，因此需要用条件语句
                data.append(editor[0])
            else:
                data.append('暂无作者和出版社信息')
            print(name)
            data.append(markNum)
            data.append(mark)
            if len(price) != 0:  # 考虑到有的书的价格信息缺失，匹配不到价格数据，因此需要添加条件语句
                data.append(price[0])
            else:
                data.append('null')
            if len(overview) != 0:  # 同样的道理，概述信息也可能会缺失，因此需要添加条件语句
                data.append(overview[0])
            else:
                data.append("暂无简介")
            data.append(link)
            data.append(have)
            alldata.append(data)
    return alldata


def save_as_sheet(alldata):  # 将爬取到的数据保存为Excel表格文件
    # 第一次运行本程序时，未创建Excel文件，应先创建一个工作簿
    if not os.path.exists('.\booktoplist.xlsx'):
        workbook = xlwt.Workbook(encoding='utf-8')  # 创建工作簿
        sheet = workbook.add_sheet('booklist', cell_overwrite_ok=True)  # 创建工作表
        workbook.save('booktoplist.xlsx')
    # 第二次或者更多次运行本程序时，对已有工作簿进行操作
    workbook = xlrd.open_workbook("booktoplist.xlsx")  # 打开已有的工作簿
    newform = copy(workbook)
    newsheet = newform.get_sheet(0)
    newsheet.col(0).width = 6000  # 规定单元格的宽度，以方便阅读
    newsheet.col(1).width = 10000
    newsheet.col(2).width = 3500
    newsheet.col(3).width = 2000
    newsheet.col(4).width = 3000
    newsheet.col(5).width = 11000
    newsheet.col(6).width = 11000
    newsheet.col(7).width = 3000
    style = [xlwt.XFStyle(), xlwt.XFStyle(), xlwt.XFStyle(), xlwt.XFStyle(), xlwt.XFStyle(), xlwt.XFStyle(),
             xlwt.XFStyle(), xlwt.XFStyle(), xlwt.XFStyle()]
    for col in range(0, 9):  # 规定字体高度，防止字体过小影响阅览效果
        style[col].font.height = 260
    style[0].font.name = '仿宋'  # 规定字体，此处将第一行的字体规定为宋体
    style[0].font.colour_index = 0x0c  # 规定字体颜色
    style[2].num_format_str = '#,##0'  # 规定数据格式
    style[2].font.colour_index = 0x30
    style[3].num_format_str = '0.0'
    style[3].font.colour_index = 0x35
    style[4].num_format_str = '0.00'
    style[4].font.colour_index = 0x1c
    style[8].font.height = 280
    style[8].font.colour_index = 0x12
    style[8].font.name = '微软雅黑'
    patterns = xlwt.Pattern()
    patterns.pattern = 1
    patterns.pattern_fore_colour = 7  # 规定单元格的前景颜色，此处为首行着色，使首行更醒目
    style[8].pattern = patterns
    column = ["图书名称", "作者及出版社", "评价人数", "评分", "定价/元", "图书概述", "详情链接", "有无馆藏"]
    for col in range(0, 8):  # 先填上每列的信息类别
        newsheet.write(0, col, column[col], style[8])
    newsheet.set_panes_frozen('1')  # 冻结窗格：冻结第一行，便于使用者查看数据类别
    newsheet.set_horz_split_pos(1)
    for row in range(len(alldata)):  # 一共250行信息
        data = alldata[row]
        for col in range(0, 8):  # 一共8列信息
            if col == 2 or col == 3 or col == 4:
                newsheet.write(row + 1, col, float(data[col]), style[col])
            else:
                newsheet.write(row + 1, col, data[col], style[col])
    newform.save('booktoplist.xlsx')


def initializeBook(alldata):  # 将爬取到的数据保存至数据库
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    try:
        cur.execute('drop table Booklist')
    except:
        pass
    sql1 = '''
        create table Booklist
        (
        Bid char(20) primary key,
        Bname text,
        Beditor text,
        BmarkNum numeric,
        Bmark numeric,
        Bprice numeric,
        Boverview text,
        Blink text,
        Bhave char(2),
        Brank integer
        )
        '''
    cur.execute(sql1)
    index=0
    for data in alldata:
        index+=1
        data.insert(0, "{:06d}".format(index))
        data.append(index)
        for i in range(len(data)):
            if i in (3,4,5):
                continue
            data[i] = '"' + str(data[i]) + '"'
        sql2 = '''
                insert or ignore into Booklist (
                Bid,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave,Brank)
                values(%s)''' % ",".join(data)
        cur.execute(sql2)
        conn.commit()

    cur.close()
    conn.close()

def initializeSituation():
    # Situation Table
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    try:
        cur.execute('drop table Situation')
    except:
        pass
    cur.execute('''
        create table Situation
        (
        Bid char(20) primary key,
        floor integer not null ,
        area char(2) not null ,
        shelf char(2) not null ,
        foreign key(Bid) references Booklist(Bid))''')
    conn.commit()

    Bidlist = []
    temp = cur.execute('''select Bid from Booklist where Bhave = '有' ''')
    for Bid in temp:
        Bidlist.append(Bid[0])
    for Bid in Bidlist:
        floor = random.randint(1, 5)
        area = chr(random.randint(65, 67))
        shelf = str(random.randint(1, 5))
        sql1 = '''
                insert or ignore into Situation (
                Bid,floor,area,shelf)
                values('%s',%d,'%s','%s')''' % (Bid,floor,area,shelf)
        cur.execute(sql1)
        conn.commit()
    cur.close()
    conn.close()

def initializeUser():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    try:
        cur.execute('drop table User')
    except:
        pass
    sql1 = '''
                    create table User
                    (Uid text primary key,
                     Upw text not null,
                     type text not null 
                    )'''
    cur.execute(sql1)
    conn.commit()
    sql2 = '''
            insert or ignore into User(Uid,Upw,type)
            values('reader','reader','reader')'''
    sql3 = '''
            insert or ignore into User(Uid,Upw,type)
            values('admin','admin','admin')'''
    cur.execute(sql2)
    cur.execute(sql3)
    for i in range(100):
        tempID = ''
        tempPW = ''
        if random.random()<0.75:
            type = 'reader'
        else:
            type = 'admin'
        for j in range(6):
            tempID+=chr(random.randint(97,122))
            tempPW+=chr(random.randint(97,122))
        sql4 = '''
            insert or ignore into User(Uid,Upw,type)
            values('%s','%s','%s')'''%(tempID,tempPW,type)
        cur.execute(sql4)
    conn.commit()
    cur.close()
    conn.close()

def initializeBorrow():
    # Borrow Table
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    try:
        cur.execute('drop table Borrow')
    except:
        pass
    cur.execute('''
            create table Borrow
            (
            Bid char(20),
            Uid text,
            startDate date,
            endDate date,
            borrowState text,
            primary key (Bid,Uid),
            foreign key(Bid) references Situation(Bid),
            foreign key (Uid) references User(Uid))''')
    conn.commit()

    Bidlist = []
    tempBid = cur.execute('''select Bid from Situation''')
    for Bid in tempBid:
        Bidlist.append(Bid[0])

    Uidlist = []
    tempUid = cur.execute('''select Uid from User''')
    for Uid in tempUid:
        Uidlist.append(Uid[0])

    for i in range(min(len(Bidlist),len(Uidlist))):
        data = []
        data.append("'" + Bidlist[random.randint(0,len(Bidlist)-1)] + "'")
        data.append("'" + Uidlist[random.randint(0,len(Uidlist)-1)] + "'")
        startDate = "'2021-" + str(random.randint(1, 6)) + "-"+str(random.randint(1,28))+"'"
        if random.random() < 0.75:
            endDate = "'2022-" + str(random.randint(1, 11))+ "-" + str(random.randint(1, 28)) + "'"
            borrowState = "'已借出'"
        else:
            endDate = "'2021-" + str(random.randint(7, 11))+ "-" + str(random.randint(1, 28)) + "'"
            borrowState = "'已归还'"
        data.append(startDate)
        data.append(endDate)
        data.append(borrowState)
        sql1 = '''
                    insert or ignore into Borrow (
                    Bid,Uid,startDate,endDate,borrowState)
                    values(%s)''' % ",".join(data)
        cur.execute(sql1)
        conn.commit()
    cur.close()
    conn.close()

def initializeMark():
    # Borrow Table
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    try:
        cur.execute('drop table Mark')
    except:
        pass
    cur.execute('''
                create table Mark
                (
                Bid char(20),
                Uid text,
                mark numeric,
                comment text,
                primary key (Bid,Uid),
                foreign key(Bid) references Booklist(Bid),
                foreign key (Uid) references User(Uid))''')
    conn.commit()

    Bidlist = []
    tempBid = cur.execute('''select Bid from Booklist''')
    for Bid in tempBid:
        Bidlist.append(Bid[0])

    Uidlist = []
    tempUid = cur.execute('''select Uid from User''')
    for Uid in tempUid:
        Uidlist.append(Uid[0])

    for i in range(700):
        book = "'" + Bidlist[random.randint(0, len(Bidlist) - 1)] + "'"
        for j in range(3):
            data = []
            data.append(book)
            data.append("'" + Uidlist[random.randint(0, len(Uidlist) - 1)] + "'")
            mark = "'"+str(random.randint(50,100)/10.0)+"'"
            data.append(mark)
            data.append(["'很好'",
                         "'超棒！！！'",
                         "'好久没读过这么棒的书了~'",
                         "'感觉这本书很值'",
                         "'感觉一般般'",
                         "'这本书让我感受到了阅读的乐趣'",
                         "'这，就是生活！'",
                         "'还不错还不错！'",
                         "'读完了，感悟颇多！'",
                         "'Nice!'",
                         "'虽然有的地方没看懂，但我大受震撼！'",
                         "'读到结尾的时候，感觉灵魂受到了冲击。'",
                         "'时代的烙印，渗透其中，更增加了文章的现实好处，在特定环境下的思维，呈现着反反复复的，不停地锤炼着人格，信仰。感受时代的进步，感受人的成长。'",
                         "'里面的人物，都鲜明着自己的性格，浓缩了很多很多，客观的看待，领略作者先生的意境，在自己的生活中借鉴发扬。'",
                         "'真情的贯穿，是本书的魅力不竭的源泉，重温自会有更进一层的体会。粗读之后，不吐不快。'"][random.randint(0,12)])
            sql1 = '''
                            insert or ignore into Mark (
                            Bid,Uid,mark,comment)
                            values(%s)''' % ",".join(data)
            cur.execute(sql1)
            conn.commit()
    cur.close()
    conn.close()

def main():
    basic_url = 'https://book.douban.com/top250?start='  # 基本的url，在它后面加一些数字可以拼成完整的url
    try:
        alldata = getdata(basic_url)
        initializeBook(alldata)
        initializeSituation()
        initializeUser()
        initializeBorrow()
        initializeMark()
        print('over!')
        # save_as_sheet(alldata)
    except:
        print("网络出错！信息爬取失败，请检查网络情况后重新运行本程序。")

if __name__ == "__main__":
    main()