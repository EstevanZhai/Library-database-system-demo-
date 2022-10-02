# -*- coding = utf-8 -*-
# @Time : 2020/12/28 20:58
# @Author : zhai_xiangyang
# @File : test1.py
# @Software : PyCharm

import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import random
import datetime

app = Flask(__name__)


def isAuthenticated(type, id, pw):  # 登录时检查账号密码是否正确
    conn = sqlite3.connect('database.db')  # 与数据库建立连接
    cur = conn.cursor()  # 获取游标
    sql = "select count(Uid) from User where type = '" + type + "' and Uid = '" + id + "' and Upw = '" + pw + "'"
    data = cur.execute(sql)
    for i in data:
        data = i[0]
        break
    cur.close()
    conn.close()
    if data == 1:
        return True
    else:
        return False


def createUser():
    pass


def search(keytext):  # 本函数用于在数据库中搜索数据
    conn = sqlite3.connect('database.db')  # 与数据库建立连接
    cur = conn.cursor()  # 获取游标
    datalist = []  # 初始化两个列表，供后面使用
    datalist_2 = []
    sql_1 = "select Brank,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave,Bid from Booklist where Bname like '%" + keytext + "%'"  # 对关键字进行搜索
    data = cur.execute(sql_1)  # 执行搜索语句
    for item in data:
        datalist.append(item)
    keyword = list(keytext)  # 将用户输入的关键字进行拆分，逐个检索
    for i in keyword:
        sql_2 = "select Brank,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave,Bid from Booklist where Bname like '%" + i + "%'"  # 对拆分后的关键字进行检索
        data = cur.execute(sql_2)  # 执行检索语句
        for item in data:
            if item not in datalist:  # 防止出现重复元素
                datalist.append(item)
    index = 1
    for i in range(len(datalist)):
        datalist[i] += (index,)
        index += 1
    for j in range(0, 5):  # 我还在网页上制作了一个“猜你想看”部分，本处的作用就是为“猜你想看”提供随机的书籍数据
        rand = random.randrange(0, 250, 1)  # 此处用于随机匹配数据，向用户推荐书籍
        sql_3 = "select Brank,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave,Bid from Booklist where Bid like '" + "{:06d}".format(
            rand) + "'"
        data = cur.execute(sql_3)
        for item in data:
            if item not in datalist:  # 防止出现重复元素
                datalist_2.append(item)
    cur.close()
    conn.close()  # 数据检索完成，关闭数据库
    if len(datalist) == 0:
        datalist = []  # 如果搜索不到西配的书籍，就在网页上显示“暂无”
    datalist_3 = [datalist, datalist_2]  # datalist_3包含了检索到的数据和“猜你想看”的随机书籍数据
    print("search result:", datalist_3)  # 借助此处的print()，我们可以在Python程序上监测数据库为关键字匹配到的内容
    return datalist_3


def setBorrow(state):  # 设置借阅状态state(真或假，分别对应 已被借阅 与 尚有馆藏)
    pass


@app.route("/login", methods=['POST', 'GET'])
def login():  # 用户登录页
    if request.method == 'POST':
        print(request.form.to_dict())
        id = request.form.to_dict()['用户账号']
        pw = request.form.to_dict()['用户密码']
        if isAuthenticated('reader', id, pw):
            return redirect("/?user=" + id)
        elif isAuthenticated('admin', id, pw):
            return redirect("/admin?user=" + id)
        else:
            return render_template("./login.html",
                                   id=id,
                                   showState=True)
    else:
        return render_template("./login.html",
                               showState=False)


@app.route("/search")
def research():  # 搜索框页面
    if request.args.get("user") != "":
        return render_template("./search.html",
                               user=request.args.get("user", "用户"))
    else:
        return redirect("/login")


@app.route("/results", methods=['POST', 'GET'])
def results():  # 搜索结果页
    if request.method == 'POST':
        keytext = request.form.get('关键字')  # 获取用户输入的关键字
        print("Keyword:", keytext)  # 打印用户提交的关键字
        return redirect("/results?kw=" + keytext + "&user=" + request.args.get("user", "用户"))
    elif request.method == 'GET':
        keytext = request.args.get('kw', '')
        datalist = search(keytext)
        if bool(datalist[0]):
            return render_template("results.html",
                                   haveResult=True,
                                   keytext=keytext,
                                   datalist=datalist[0],
                                   recommend_data=datalist[1],
                                   user=request.args.get("user", "用户"))
        else:
            return render_template("results.html",
                                   haveResult=False,
                                   keytext=keytext,
                                   recommend_data=datalist[1],
                                   user=request.args.get("user", "用户"))


@app.route("/detail", methods=['POST', 'GET'])
def detail():  # 在用户:reader登陆的情况下进行书籍的借阅和评论
    if request.method == 'POST':

        if request.form.get('mark'):
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            # 插入reader的打分和评价   request.args是存有mark和comment的字典
            comment = request.form.to_dict()
            for key in comment.keys():  # 对于comment中的每个key
                comment[key] = "'" + comment[key] + "'"
                print(comment[key])
            sql = '''replace into Mark(Bid,Uid,mark,comment) values ('%s','%s',%s,%s)''' % (
                request.args.get("id"), request.args.get("user"), comment['mark'], comment['comment'])
            cur.execute(sql)
            conn.commit()
            # 显示评分和评价
            valuelist = []  # 存了评分和评论的列表
            for value in request.args.items():
                valuelist.append(value)
            print("detail Page | id:", request.args.get('id', ''))
            cur.close()
            conn.close()
            return redirect("/detail?id=" + request.args.get("id", "000001") + "&user="+request.args.get("user","reader")+"'")
        else:  # 点击借阅
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            sql = '''replace into Borrow(Bid,Uid,startDate,borrowState)  values('%s','%s',datetime('now', 'start of day'),'已借出')''' % (request.args.get("id"), request.args.get("user","reader"))
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('jieguo.html',
                                   link=request.headers.get("Referer", "/"))

    elif request.method == 'GET':
        print("detail Page", request.args.get('id', ''))
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        a="select Bhave from Booklist where Booklist.Bid = " + "'" + request.args.get(
            'id', '') + "'"
        b=cur.execute(a)
        for item in b:
            c=item[0]
        if c=="有":
            sql="select Booklist.*,Situation.* from Booklist,Situation where Booklist.Bid=Situation.Bid and Booklist.Bid = " + "'" + request.args.get(
            'id', '') + "'"
        else :
            sql="select * from Booklist where Booklist.Bid = " + "'" + request.args.get(
            'id', '') + "'"

        data = cur.execute(sql)  # 与html中的data对应
        datalist = []
        for item in data:
            datalist=item
        print(datalist)
        sql_1 = "select Uid,mark,comment from Booklist,Mark where Booklist.Bid=Mark.Bid and Booklist.Bid = " + "'" + request.args.get(
            'id', '') + "'"
        data_1 = cur.execute(sql_1)
        datalist_1 = []
        for item in data_1:  # datalist_1是元素为元组的数组
            datalist_1.append(item)
        print(datalist_1)
        cur.close()
        conn.close()
        return render_template("detail.html",
                               # bookName=datalist[1],
                               data=datalist,
                               datalist_1=datalist_1,
                               user=request.args.get("user"))


@app.route('/')
def index():
    if request.args.get("user", "") != "":
        return render_template("index.html",
                               login=True,
                               user=request.args.get("user"))
    else:
        return render_template("index.html")


@app.route('/guide')
def guide():
    if request.args.get('floor', ''):
        floor = request.args.get('floor', '')
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        sql = "select Booklist.* from Booklist,Situation where Booklist.Bid=Situation.Bid and floor = " + floor
        data = cur.execute(sql)
        datalist = []
        for item in data:
            datalist.append(item)
        print(datalist)
        return render_template("guide.html",
                               floor=floor,
                               datalist=datalist,
                               user=request.args.get("user", ""),
                               login=(request.args.get("user", "") != ""))
    else:
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        sql = "select * from Booklist order by Bmark limit 10"
        data = cur.execute(sql)
        datalist = []
        for item in data:
            datalist.append(item)
        print(datalist)
        return render_template("guide.html",
                               datalist=datalist,
                               user=request.args.get("user", ""),
                               login=(request.args.get("user", "") != ""))


@app.route('/support')
def support():
    return render_template("support.html",
                           user=request.args.get("user"))


@app.route('/addbook', methods=['POST', 'GET'])
def addbook():
    if request.method == 'POST':
        book = request.form.to_dict()
        for key in book.keys():
            if book[key] == '':
                book[key] = 'null'
            else:
                book[key] = "'" + book[key] + "'"
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        lastdata = cur.execute('select Bid from Booklist order by Bid desc limit 1')
        for item in lastdata:
            lastBid = item
        Bid = int(lastBid[0]) + 1
        book['Bid'] = "'{:06d}'".format(Bid)
        print(book)
        sql = '''insert into Booklist(Bid,Bname,Beditor,Bprice,Boverview,Blink,Bhave) values (%s,%s,%s,%s,%s,%s,%s)''' % (
            book['Bid'], book['bookname'], book['writer'], book['price'], book['overview'], book['link'], book['have'])
        cur.execute(sql)
        conn.commit()
        print("end")
        return render_template('addbook.html')
    elif request.method == 'GET':
        return render_template('addbook.html')


@app.route('/addzhanghu', methods=['POST', 'GET'])
def addzhanghu():
    if request.method == 'POST':
        if request.form.get('Uid'):
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            # 插入reader的打分和评价   request.args是存有mark和comment的字典
            sql = '''insert into User(Uid,Upw,type) values ('%s','%s','%s')''' % (
            request.form.get("Uid"), request.form.get('Upw'), request.form.get('type'))
            cur.execute(sql)
            conn.commit()
            sql = "select * from User "
            data = cur.execute(sql)
            u = []
            for item in data:
                u.append(item)
            cur.close()
            conn.close()
            return render_template('addzhanghu.html', u=u[1:],user=request.args.get("user","admin"))

    elif request.method == 'GET':
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        sql = "select * from User where type like'reader'"
        data = cur.execute(sql)
        u = []
        for item in data:
            u.append(item)
        cur.close()
        conn.close()
        return render_template('addzhanghu.html', u=u[1:],user=request.args.get("user","admin"))


@app.route('/dezhanghu', methods=['POST', 'GET'])
def dezhanghu():
    if request.method == 'POST':
        if request.form.get('Uid'):
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            # 插入reader的打分和评价   request.args是存有mark和comment的字典
            sql = '''delete from User where Uid='%s' ''' % (request.form.get("Uid"))
            cur.execute(sql)
            conn.commit()
            sql = "select * from User where type like'reader'"
            data = cur.execute(sql)
            u = []
            for item in data:
                u.append(item)
            cur.close()
            conn.close()
            return render_template('dezhanghu.html', u=u[1:],user=request.args.get("user","admin"))
    elif request.method == 'GET':
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        sql = "select * from User where type like'reader'"
        data = cur.execute(sql)
        u = []
        for item in data:
            u.append(item)
        cur.close()
        conn.close()
        return render_template('dezhanghu.html', u=u[1:],user=request.args.get("user","admin"))


@app.route("/manageresults", methods=['POST', 'GET'])
def manageresults():  # 索结果页
    if request.method == 'POST':
        if request.form.get('关键字') != None:
            keytext = request.form.get('关键字', "")  # 获取用户输入的关键字
            print("Keyword:", keytext)  # 打印用户提交的关键字
            print(request.args.to_dict())
            return redirect("/manageresults?kw=" + keytext + "&user=" + request.args.get("user", "admin"))
        elif request.form.get('Uid',"")!="":
            print("123")
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            sql = '''replace into Borrow(Bid,Uid,startDate,endDate,borrowState) values ('%s','%s','%s','%s','%s')''' % (
                request.form.get('Bid'),request.form.get('Uid'), request.form.get('Btime'), request.form.get('Etime'),
                request.form.get('br'))
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/manageresults?kw=" + request.args.get("kw","") + "&user=" + request.args.get("user", "admin"))
        else:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            print(request.form.to_dict())
            sql = "delete from Booklist where Bid='"+request.form.get("Bid")+"'"
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return redirect("manageresults?kw="+request.args.get("kw")+"&user="+request.args.get("user"))
    elif request.method == 'GET':
        keytext = request.args.get('kw', '')
        datalist = search(keytext)
        if bool(datalist[0]):
            return render_template("manageresults.html",
                                   haveResult=True,
                                   keytext=keytext,
                                   datalist=datalist[0],
                                   recommend_data=datalist[1],
                                   user=request.args.get("user"))
        else:
            return render_template("manageresults.html",
                                   haveResult=False,
                                   keytext=keytext,
                                   recommend_data=datalist[1],
                                   user=request.args.get("user"))
    else:
        return render_template("manageresults.html")


@app.route('/movebook', methods=['POST', 'GET'])
def movebook():
    if request.method == 'POST':
        change = request.form.to_dict()
        for key in change.keys():
            change[key] = "'" + change[key] + "'"
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        sql = "UPDATE Situation SET floor=%s,area=%s,shelf=%s "%(change['floor'], change['area'], change['shelf'])+"WHERE Bid = '" +request.args.get("id")+"'"
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        return render_template('jieguo.html',
                               link=request.headers.get("Referer","/"))
    elif request.method == 'GET':
        return render_template("movebook.html")


@app.route('/admin', methods=['POST', 'GET'])
def admin():  # 本函数用于在数据库中搜索数据
    if request.method == 'GET' and request.args.get("keytext") != None:
        keytext = request.args.get("keytext")
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        Sump = cur.execute('select count(Bid) from Borrow ')
        sql_4 = "select count(borrowState) from Borrow where borrowState = '已借出'"
        data = cur.execute(sql_4)
        print(data)
        for item in data:
            Bing = item
            print(item)
        Bing = Bing[0]
        sql_5 = "select count() from Borrow where endDate<datetime('now','start of day')"
        Nr = cur.execute(sql_5)
        datalist = []  # 初始化两个列表，供后面使用
        sql_1 = "select Brank,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave from Booklist where Bname like '%" + keytext + "%'"  # 对关键字进行搜索
        data = cur.execute(sql_1)  # 执行搜索语句
        for item in data:
            datalist.append(item)
        keyword = list(keytext)  # 将用户输入的关键字进行拆分，逐个检索
        for i in keyword:
            sql_2 = "select Brank,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave from Booklist where Bname like '%" + i + "%'"  # 对拆分后的关键字进行检索
            data = cur.execute(sql_2)  # 执行检索语句
            for item in data:
                if item not in datalist:  # 防止出现重复元素
                    datalist.append(item)
        return render_template("admin.html", Nr=Nr, Bing=Bing, Sump=Sump)
    elif request.method == 'GET':
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        data = cur.execute('select count(Bid) from Borrow ')
        for item in data:
            Sump = item
            print(item)
        Sump = Sump[0]
        sql_4 = "select count(borrowState) from Borrow where borrowState = '已借出'"
        data = cur.execute(sql_4)
        for item in data:
            Bing = item
            print(item)
        Bing = Bing[0]
        sql_5 = "select count() from Borrow where endDate<date('now','start of day')"
        data = cur.execute(sql_5)
        for item in data:
            Nr = item
            print(item)
        Nr = Nr[0]
        return render_template("admin.html", Nr=Nr, Bing=Bing, Sump=Sump, user=request.args.get("user"))
    elif request.method == 'POST':
        keytext = request.args.get("keytext")
        conn = sqlite3.connect('database.db')  # 与数据库建立连接
        cur = conn.cursor()  # 获取游标
        Sump = cur.execute('select count(Bid) from Borrow ')
        sql_4 = "select count(borrowState) from Borrow where borrowState = '已借出'"
        Bing = cur.execute(sql_4)
        sql_5 = "select count() from Borrow where endDate<date('now','start of day')"
        Nr = cur.execute(sql_5)
        datalist = []  # 初始化两个列表，供后面使用
        sql_1 = "select Brank,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave from Booklist where Bname like '%" + keytext + "%'"  # 对关键字进行搜索
        data = cur.execute(sql_1)  # 执行搜索语句
        for item in data:
            datalist.append(item)
        keyword = list(keytext)  # 将用户输入的关键字进行拆分，逐个检索
        for i in keyword:
            sql_2 = "select Brank,Bname,Beditor,BmarkNum,Bmark,Bprice,Boverview,Blink,Bhave from Booklist where Bname like '%" + i + "%'"  # 对拆分后的关键字进行检索
            data = cur.execute(sql_2)  # 执行检索语句
            for item in data:
                if item not in datalist:  # 防止出现重复元素
                    datalist.append(item)
        return render_template("admin.html", Nr=Nr, Bing=Bing, Sump=Sump)


@app.route('/jieyue')
def jieyue():
    conn = sqlite3.connect('database.db')  # 与数据库建立连接
    cur = conn.cursor()  # 获取游标
    sql = "select * from Borrow where borrowState like '已借出'"
    data = cur.execute(sql)
    u = []
    for item in data:
        u.append(item)
    cur.close()
    conn.close()
    return render_template("jieyue.html", u=u[1:])


@app.route('/jieguo')
def jieguo():
    return render_template('jieguo.html',
                           link=request.headers.get("Referer", "/"))


if __name__ == '__main__':
    app.run()
