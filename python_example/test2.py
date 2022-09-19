#!/usr/bin/env python
# coding: utf-8

# hash密碼
from sre_constants import SUCCESS
import bcrypt

# 解析 URL
from urllib import parse

# mysql connector
from flask_mysqldb import MySQL, MySQLdb

# flask
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__, template_folder='templates')

app.config['MYSQL_HOST'] = 'localhost'          # 登入ip
app.config['MYSQL_USER'] = 'hj'                 # 登入帳號
app.config['MYSQL_PASSWORD'] = 'test1234'       # 登入密碼
app.config['MYSQL_DB'] = 'testdb'               # 登入資料庫名稱
# app.config['MYSQL_PORT'] = '3306'             # Port號（預設就是3306)
mysql = MySQL(app)


# conn = MySQLdb.connect(host="127.0.0.1",
#                        user="hj",
#                        passwd="test1234",
#                        db="testdb")

# 主頁
@app.route('/')
def home():
    return render_template("home.html")

# 退選頁面
@app.route('/unselect', methods=['GET', 'POST'])
def unselect():
    if request.method == 'GET':
        return render_template("unselect.html")
    else:
        courseid = request.form['cid']
        print(courseid)
        print(session['name'])
        sel = mysql.connection.cursor()
        sel.execute("SELECT coursename FROM course where courseID LIKE %s;", [courseid])
        res = sel.fetchall()

        # 檢查是否低於選課學分下限(2)
        zzz = "SELECT courseID FROM " + session['name'] + ";"
        sel6 = mysql.connection.cursor()
        sel6.execute(zzz)
        course_list = sel6.fetchall()
        print(course_list)
        tot_credits = 0
        for i in range(len(course_list)):
            yyy = "SELECT credits FROM course WHERE courseID LIKE " + str(course_list[i][0]) + ";"
            print(yyy)
            sel7 = mysql.connection.cursor()
            sel7.execute(yyy)
            aa = sel7.fetchall()
            print(aa)
            tot_credits+=aa[0][0]
        print("pre:tot_credits")
        print(tot_credits)
        xxx = "SELECT credits FROM course WHERE courseID LIKE " + courseid + ";"
        print(xxx)
        sel8 = mysql.connection.cursor()
        sel8.execute(xxx)
        bb = sel8.fetchall()
        print(bb)
        tot_credits-=bb[0][0]
        # 設定選課學分上限
        if tot_credits < 2:
            return "已修習學分不得低於最低學分"

        sel2 = mysql.connection.cursor()
        sel2.execute("SELECT required_or_elective FROM course WHERE courseID LIKE %s;", [courseid])
        res2 = sel2.fetchall()
        print(res2)
        if len(res) != 0:
            if res2[0][0] == "Required":
                print("y")
                query = "DELETE FROM " + session['name'] + " WHERE courseID LIKE " + courseid
                print(query)
                sel1 = mysql.connection.cursor()
                sel1.execute(query)
                mysql.connection.commit()
                sel1.close()
                end = """<p><a href="/unselect">退選必修</a></p>"""
                return end
            query = "DELETE FROM " + session['name'] + " WHERE courseID LIKE " + courseid
            print(query)
            sel1 = mysql.connection.cursor()
            sel1.execute(query)
            mysql.connection.commit()
            sel1.close()
        else:
            return "沒有這個課程"
        return render_template("unselect.html")

# 選課頁面
@app.route('/select', methods=['GET', 'POST'])
def select():
    if request.method == 'GET':
        return render_template("select.html")
    else:
        courseid = request.form['cid']
        print(courseid)
        print(session['name'])
        sel = mysql.connection.cursor()
        sel.execute("SELECT coursename FROM course where courseID LIKE %s;", [courseid])
        res = sel.fetchall()

        # 檢查是否超過選課學分上限(8)
        zzz = "SELECT courseID FROM " + session['name'] + ";"
        sel6 = mysql.connection.cursor()
        sel6.execute(zzz)
        course_list = sel6.fetchall()
        print(course_list)
        tot_credits = 0
        for i in range(len(course_list)):
            yyy = "SELECT credits FROM course WHERE courseID LIKE " + str(course_list[i][0]) + ";"
            print(yyy)
            sel7 = mysql.connection.cursor()
            sel7.execute(yyy)
            aa = sel7.fetchall()
            print(aa)
            tot_credits+=aa[0][0]
        print("pre:tot_credits")
        print(tot_credits)
        xxx = "SELECT credits FROM course WHERE courseID LIKE " + courseid + ";"
        print(xxx)
        sel8 = mysql.connection.cursor()
        sel8.execute(xxx)
        bb = sel8.fetchall()
        print(bb)
        tot_credits+=bb[0][0]
        # 設定選課學分上限
        if tot_credits > 8:
            return "已超過選課學分上限"

        # 看這堂課的的教室的容量
        aaa = """SELECT capacity FROM classroom WHERE classroomID=(
                 SELECT classroomID FROM course WHERE courseID=""" + courseid + ");"
        sel3 = mysql.connection.cursor()
        sel3.execute(aaa)
        capacity_room = sel3.fetchall()
        print(capacity_room)

        # 算這堂課的修課人數
        bbb = """SELECT name FROM users;"""
        sel4 = mysql.connection.cursor()
        sel4.execute(bbb)
        name_list = sel4.fetchall()
        print(name_list)
        count = 0
        for i in range(len(name_list)):
            ans = []
            print(name_list[i][0])
            ccc = "SELECT courseID FROM " + name_list[i][0] + ";"
            print(ccc)
            sel5 = mysql.connection.cursor()
            sel5.execute(ccc)
            arr = sel5.fetchall()
            print(arr)
            for j in range(len(arr)):
                ans.append(arr[j][0])
            if int(courseid) in ans:
                count+=1
            print(ans)
        print(count)
        if(count == int(capacity_room[0][0])):
            print("The course is full.")
            return "這堂課已經額滿"

        if len(res) != 0:
            query = "INSERT INTO " + session['name'] + " (courseID) VALUES ("+ courseid + ")"
            print(query)
            sel1 = mysql.connection.cursor()
            sel1.execute(query)
            mysql.connection.commit()
            sel1.close()
        else:
            return "沒有這個課程"
        return render_template("select.html")
    
    #sel1.execute("INSERT INTO %s (id, courseID) VALUES (%s, %s);", [session['name'], i, courseid])

    # courseid = request.form.get('cid')
    # if request.method == 'POST':
    #     courseid = request.form['cid']
    #     print(courseid)
    # sel1 = mysql.connection.cursor()
    # sel1.execute("SELECT coursename FROM course where courseID LIKE %s;", [courseid])
    # results = sel1.fetchall()
    # sel1.close()
    # print(results[0][0])

    #return results[0][0]
    #if len(results) != None:
        ## return "沒有這堂課"
        #return render_template("home.html")
    #else:
        ## return results

    #return render_template("home.html")

# 查看已選課程
@app.route('/check', methods=["GET", "POST"])
def check():
    print("check:" + session['name'])
    query1 = "SELECT courseID FROM " + session['name']
    sel2 = mysql.connection.cursor()
    sel2.execute(query1)
    course_list = sel2.fetchall()

    # 算出已選學分
    zzz = "SELECT courseID FROM " + session['name'] + ";"
    sel6 = mysql.connection.cursor()
    sel6.execute(zzz)
    course_list = sel6.fetchall()
    print(course_list)
    tot_credits = 0
    for i in range(len(course_list)):
        yyy = "SELECT credits FROM course WHERE courseID LIKE " + str(course_list[i][0]) + ";"
        print(yyy)
        sel7 = mysql.connection.cursor()
        sel7.execute(yyy)
        aa = sel7.fetchall()
        print(aa)
        tot_credits+=aa[0][0]
    print("pre:tot_credits")
    print(tot_credits)

    course_name = []
    for i in range(len(course_list)):
        query2 = "SELECT coursename FROM course WHERE courseID LIKE " + str(course_list[i][0]) + ";"
        #print(query2)
        ww = mysql.connection.cursor()
        ww.execute(query2)
        namelist = ww.fetchall()
        course_name.append(namelist[0][0])
        
    print(course_name)
    #results = sel2.fetchall()
    #sel2.close()
    #print(len(results))
    #print(results[0][0])
    #return render_template("check.html")
    results = """
    <p><a href="/">Back to Interface</a><br><br>已選學分 &nbsp:&nbsp {}<br></p>
    """.format(str(tot_credits))
    i = 0
    for (description, ) in course_list:
        results += "<p>CourseID &nbsp:&nbsp {} &nbsp&nbsp&nbsp&nbsp Course name &nbsp:&nbsp {}</p>".format(description, course_name[i])
        i+=1
    return results

# 註冊頁面
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                    (name, email, hash_password))
        # 不同使用者建不同資料表
        newuser = "CREATE TABLE " + name + "(courseID int NOT NULL UNIQUE);"
        cur.execute(newuser)
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('home'))


# 登入頁面
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        print("email:",email)
        password = request.form['password'].encode('utf-8')
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s", [email])
        user = curl.fetchone()
        curl.close()
        if user == None:
            return "沒有這個帳號"
        if len(user) != 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("home.html")
            else:
                return "您的密碼錯誤"
    else:
        return render_template("login.html")


# 登出
@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")


if __name__ == '__main__':
    app.secret_key = "This is a secret_key"
    # print(app.ur1_map)
    app.run(debug=True, host='127.0.0.1', port=5005)





