# coding=utf-8
from flask import *
from flask import request
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import config
import math
import os
from datetime import timedelta
from ast import literal_eval


app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.urandom(24)  # 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。

# 对flask进行一个初始化
# 创建一个simple表
class Simple(db.Model):
    __tablename__ = 'simple'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(100), nullable=False)
    pwd = db.Column(db.CHAR(50), nullable=False)
    saw_movie = db.Column(db.CHAR(1000))
class Movie_info(db.Model):
    __tablename__ = 'Movie_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    M_name = db.Column(db.String(100), nullable=False)
    similars = db.Column(db.VARCHAR(1000), nullable=False)
    update_time = db.Column(db.CHAR(20), nullable=False)
db.create_all()

#文本相似度
def jaccard_similarity(s1, s2):
    def add_space(s):
        return ' '.join(s)
    # 将字中间加入空格
    s1, s2 = add_space(s1), add_space(s2)
    # 转化为TF矩阵
    cv = CountVectorizer(tokenizer=lambda s: s.split())
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    # 求交集
    numerator = np.sum(np.min(vectors, axis=0))
    # 求并集
    denominator = np.sum(np.max(vectors, axis=0))
    # 计算杰卡德系数
    return 1.0 * numerator / denominator

#余弦相似度
def MergeWord(T1, T2):
        MergeWord = []
        duplicateWord = 0
        for ch in range(len(T1)):
            MergeWord.append(T1[ch][0])
        for ch in range(len(T2)):
            if T2[ch][0] in MergeWord:
                duplicateWord = duplicateWord + 1
            else:
                MergeWord.append(T2[ch][0])
        return MergeWord
# 计算向量
def CalVector(T1, MergeWord):
    TF1 = [0] * len(MergeWord)
    for ch in range(len(T1)):
        TermFrequence = T1[ch][1]
        word = T1[ch][0]
        i = 0
        while i < len(MergeWord):
            if word == MergeWord[i]:
                TF1[i] = TermFrequence
                break
            else:
                i = i + 1
    # print(TF1)
    return TF1
# 求余弦similar
def CalConDis(v1, v2, lengthVector):
    # 计算出两个向量的乘积
    B = 0
    i = 0
    while i < lengthVector:
        B = v1[i] * v2[i] + B
        i = i + 1
    # print('乘积 = ' + str(B))
    # 计算两个向量的模的乘积
    A = 0
    A1 = 0
    A2 = 0
    i = 0
    while i < lengthVector:
        A1 = A1 + v1[i] * v1[i]
        i = i + 1
    i = 0
    while i < lengthVector:
        A2 = A2 + v2[i] * v2[i]
        i = i + 1
    # print('A2 = ' + str(A2))
    A = math.sqrt(A1) * math.sqrt(A2)
    # print('两篇文章的相似度 = ' + format(float(B) / A,".3f"))
    d = format(float(B) / A, ".3f")
    return d

def consi(t1,t2):
    M = MergeWord(t1,t2)
    V1= CalVector(t1,M)
    V2 = CalVector(t2,M)
    return CalConDis(V1,V2,len(V1))

@app.route("/")
def Home():
    return render_template('index.html')

@app.route("/login/")  # 请求方式为get
def login():
    return render_template('login.html')

@app.route("/login1", methods=['POST'])  # 请求方式为post
def loginin():
    if request.method == "POST":
        login_name = request.form['uname'];
        login_psw = request.form['upwd'];
        if login_name == Simple.user and login_psw == Simple.pwd:
            return render_template('login.html', data="输入有误")
        else:

            result = Simple.query.filter(Simple.user == login_name and Simple.pwd == login_psw).first()
            print(result)
            if result is not None:
                session['uname'] = result.user;
                session['similar_m'] = ['1'];
                session['name'] = [];
                session["other"] = 0
                session["s"] = 0
                session["e"] = 14
                return render_template('index1.html')
            else:
                return render_template('login.html', data="输入有误")

    return render_template('login.html', username='username', moban='shurucuowu')

@app.route("/register")  # 请求方式为get
def register():
    return render_template('register.html')

@app.route('/rsuccess/', methods=['POST', 'GET'])
def regist_function():
    if request.method == "POST":
        user = request.form.get('uname')
        password = request.form.get('upwd')
        simple1 = Simple(user=user, pwd=password)
        result = Simple.query.filter(Simple.user == user).first()
        if result is not None:
            return render_template('register.html', data="该用户已注册")
        db.session.add(simple1)
        db.session.commit()

        return render_template('login.html', data="注册成功，欢迎登陆！")

@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/rank")
def rank():
    data = pd.read_csv("all.csv", header=0, encoding='utf_8_sig')
    x = [i.split("/") for i in data["电影类型"].values.tolist()]
    jinnian = data[data["上映时间"] == 2019]
    jinnian = jinnian.values.tolist()
    xiju = [i for i, val in enumerate(x) if "喜剧" in val]
    xiju = data.iloc[xiju].values.tolist()

    donghua = data[data["电影类型"] == "动画"]
    donghua = donghua.reset_index().sort_values('hot', ascending=0)[:14].sort_values('评分', ascending=0).values.tolist()

    kehuan = [i for i, val in enumerate(x) if "科幻" in val]
    kehuan = data.iloc[kehuan][:14].sort_values('评分', ascending=0).values.tolist()

    xuanyi = [i for i, val in enumerate(x) if "悬疑" in val]
    xuanyi = data.iloc[xuanyi][:14].sort_values('评分', ascending=0).values.tolist()

    lenmen = data[(data["评分"] > 9) & (data["评分人数"] > 9999) & (data["评分人数"] < 59999)]
    lenmen = lenmen.sort_values('评分', ascending=0).values.tolist()

    data = data.values.tolist()
    print(donghua[0:2])

    return render_template('about.html', data=data[0:14], xiju=xiju[0:14], kehuan=kehuan, xuanyi=xuanyi,
                           donghua=donghua[0:14], jinnian=jinnian[0:14], lenmen=lenmen[0:14])

@app.route("/similar", methods=["GET", "POST"])
def similar():
    import _thread
    from threading import Thread
    data = pd.read_csv("all_similar.csv", header=0, encoding='utf_8_sig')

    if request.method == "POST":

        movie_name = request.form.get("similar_name")
        if(len(data[data["片名"] == movie_name])==0 ):
            info = "没有相关电影信息，看看其他好看的电影吧。"
            return render_template('gallery.html', data_info= info, similar_name=movie_name)

        # if 'uname' in session:
        #     result = Simple.query.filter(Simple.user == session['uname']).first()
        #     names = result.saw_movie
        #     x = names + '/' + str(movie_name)
        #     count = Simple.query.filter_by(user=session['uname']).update({'saw_movie': x})  # 返回受影响行数
        #     db.session.commit()

        rs = Movie_info.query.filter(Movie_info.M_name == movie_name).first()
        if rs is not None:
            list2 = rs.similars
            list2 = literal_eval(list2)
            list2 = [i[1] for i in list2]
            list3 = [data[data["片名"] == i.replace("?","·")].sort_values('评分', ascending=0).values.tolist()[0] for i in list2[0:14]]
            thr = Thread(target=update, args=[movie_name,rs])
            thr.start()
            return render_template('gallery.html', data=list3, similar_name=movie_name)
        else:
            list_m = []
            x = data[data["片名"] == movie_name]
            one = literal_eval(data.iloc[x.index].similar_words.values[0])
            for i in range(len(data)):
                all1 = literal_eval(data.iloc[i]['similar_words'])
                for r in one:
                    if r in all1:
                        list_m.append(i)
                        break;
            sourcefile = literal_eval(data[data["片名"] == movie_name]["word_fre"].values[0])
            similar = dict()
            for i in list_m:
                similar[consi(sourcefile, literal_eval(data.iloc[i]['word_fre']))] = data.iloc[i]['片名']
            list2 = sorted(similar.items(), reverse=True)
            import time
            time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            M_info = Movie_info(M_name=movie_name, similars=str(list2[:100]),update_time = time1)
            db.session.add(M_info)
            db.session.commit()
            list3 = [data[data["片名"] == i[1]].sort_values('评分', ascending=0).values.tolist()[0] for i in list2[0:14]]
            return render_template('gallery.html', data=list3, similar_name=movie_name)
    else:
        movie_name = "名侦探柯南：贝克街的亡灵"
        rs = Movie_info.query.filter(Movie_info.M_name == movie_name).first()
        if rs is not None:
            list2 = rs.similars
            list2 = literal_eval(list2)
            list2 = [i[1] for i in list2]
            list3 = [data[data["片名"] == i.replace("?","·")].sort_values('评分', ascending=0).values.tolist()[0] for i in list2[0:14]]
        return render_template('gallery.html',data = list3, similar_name=movie_name)

@app.route("/guess")
def guess():
    if "uname" in session:
        import pandas as pd
        data = pd.read_csv("all.csv", header=0, encoding='utf_8_sig')
        jinnian = data[data["上映时间"] == 2019]
        jinnian = jinnian.values.tolist()
        return render_template('blog.html', data=jinnian[0:14])
    else:
        return render_template('login.html')


@app.route('/dataQuery/', methods=['GET'])
def dataQuery():
    result = Simple.query.filter(Simple.user == session['uname']).first()
    names = result.saw_movie.split("/")[1:-1]
    if (len(names) == 0):
        import pandas as pd
        data = pd.read_csv("all.csv", header=0, encoding='utf_8_sig')
        jinnian = data[data["上映时间"] == 2019]
        session['s'] = session['e'];
        session['e'] = session['e'] + 14;
        print(session['s'])
        jinnian = jinnian.values.tolist()[session['s']:session['e']]
        return render_template('1.html', data=jinnian)
    else:
        import pandas as pd
        data = pd.read_csv("all.csv", header=0, encoding='utf_8_sig')
        import random
        if (session["other"] < len(names)):
            i = names[random.randint(0, len(names) - 1)]
            rs = Movie_info.query.filter(Movie_info.M_name == i).first()
            if rs is not None:
                list2 = rs.similars
                list2 = literal_eval(list2)
                list2 = [i[1] for i in list2]
                list3 = [data[data["片名"] == i.replace("?", "·")].values.tolist()[0] for i
                         in list2[0:57]]
                y = [0, 14, 28, 42][random.randint(0, 3)]
                list5 = list3[y:y + 14]
                if(len(list5)<14):
                    list5 = list3[0:14]
            return render_template('1.html', data=list5)
        else:
            import pandas as pd
            data = pd.read_csv("all.csv", header=0, encoding='utf_8_sig')
            jinnian = data[data["上映时间"] == 2019]
            jinnian = jinnian.values.tolist()[session['s']:session['e']]
            session['s'] = session['e'];
            session['e'] = session['e'] + 14;
            return render_template('1.html', data=jinnian)


@app.route('/choice1')
def choice1():
    data = pd.read_csv("all1.csv", header=0, encoding='utf_8_sig')
    xiju = data
    y2020 = xiju[xiju["上映时间"] == 2020].sort_values('评分', ascending=0).values.tolist()
    y2019 = xiju[xiju["上映时间"] == 2019].sort_values('评分', ascending=0).values.tolist()
    y2018 = xiju[xiju["上映时间"] == 2018].sort_values('评分', ascending=0).values.tolist()
    y2017 = xiju[xiju["上映时间"] == 2017].sort_values('评分', ascending=0).values.tolist()
    y2016 = xiju[xiju["上映时间"] == 2016].sort_values('评分', ascending=0).values.tolist()
    y15_00 = xiju[(xiju["上映时间"] < 2015) & (xiju["上映时间"] > 2000)].sort_values('评分', ascending=0).values.tolist()
    y2000 = xiju[xiju["上映时间"] < 2000].sort_values('评分', ascending=0).values.tolist()
    return render_template('choice1.html', y2020=y2020[:50], y2019=y2019[:50], y2018=y2018[:50], y2017=y2017[:50],
                           y2016=y2016[:50], y15_00=y15_00[:50], y2000=y2000[:50])


@app.route('/choices/<string:type>')
def choices(type):
    data = pd.read_csv("all1.csv", header=0, encoding='utf_8_sig')
    x = [i.split("/") for i in data["电影类型"].values.tolist()]
    xiju = [i for i, val in enumerate(x) if type in val]
    xiju = data.iloc[xiju]
    y2020 = xiju[xiju["上映时间"] == 2020].sort_values('评分', ascending=0).values.tolist()
    y2019 = xiju[xiju["上映时间"] == 2019].sort_values('评分', ascending=0).values.tolist()
    y2018 = xiju[xiju["上映时间"] == 2018].sort_values('评分', ascending=0).values.tolist()
    y2017 = xiju[xiju["上映时间"] == 2017].sort_values('评分', ascending=0).values.tolist()
    y2016 = xiju[xiju["上映时间"] == 2016].sort_values('评分', ascending=0).values.tolist()
    y15_00 = xiju[(xiju["上映时间"] < 2015) & (xiju["上映时间"] > 2000)].sort_values('评分', ascending=0).values.tolist()
    y2000 = xiju[xiju["上映时间"] < 2000].sort_values('评分', ascending=0).values.tolist()
    return render_template('choice.html', type=type, y2020=y2020, y2019=y2019[:100], y2018=y2018[:100],
                           y2017=y2017[:100], y2016=y2016[:100], y15_00=y15_00[:100], y2000=y2000[:100])

#更新后台数据
def update(movie_name,rs):
    list_m1 = []
    data = pd.read_csv("all_similar.csv", header=0, encoding='utf_8_sig')
    x = data[data["片名"] == movie_name]
    one = literal_eval(data.iloc[x.index].similar_words.values[0])
    for i in range(len(data)):
        all1 = literal_eval(data.iloc[i]['similar_words'])
        for r in one:
            if r in all1:
                list_m1.append(i)
                break;
    sourcefile = literal_eval(data[data["片名"] == movie_name]["word_fre"].values[0])
    similar = dict()
    for i in list_m1:
        similar[consi(sourcefile, literal_eval(data.iloc[i]['word_fre']))] = data.iloc[i]['片名']
    list2 = sorted(similar.items(), reverse=True)
    if rs is not None:
        import time
        time1 = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        x2 = str(list2)
        count = Movie_info.query.filter_by(M_name=movie_name).update({'similars': x2,'update_time':time1})  # 返回受影响行数
        db.session.commit()



if __name__ == "__main__":
    app.debug = True
    app.run()
