# -*- coding:utf-8 -*-

'''
1.设置服务器
2.默认网址访问提交登录界面WTF表单
3.为服务器配置数据库连接
4.服务器获取用户登录信息并查询数据库
5.成功登录服务器发送操作界面表单
'''
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import PrimaryKeyConstraint
from flask_sqlalchemy import SQLAlchemy
from main.form_class_item import *
import base64
import time
import re
from main import Data_spider
from main import email_plug

app = Flask(__name__)

app.secret_key = 'dengyifei'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/app_base?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['MAIL_SERVER'] = 'smtp.qq.com'
# app.config['MAIL_PORT'] = 465

db = SQLAlchemy(app)


# 定义图片流函数，将图片以流的形式从服务端传递给用户端浏览器
def get_img_stream(img_path):
    img_stream = ''
    with open(img_path, 'rb') as img_file:
        img_stream = img_file.read()
        img_stream = base64.b64encode(img_stream)
    img_stream = str(img_stream, encoding='utf8')
    return img_stream


# 定义系统用户对象类
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer)
    name = db.Column(db.String(16))
    password = db.Column(db.String(32))
    email = db.Column(db.String(32), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_delete = db.Column(db.Boolean,default=False)
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        {},
    )

    def __repr__(self):
        return 'User:<id:%s name:%s email:%s role_id:%s>' % (self.id, self.name, self.email, self.role_id)


# 定义系统用户类型类
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(16), unique=True)

    users = db.relationship('User', backref='role')

    def __repr__(self):
        return 'Role:<id:%s role:%s>' % (self.id, self.role_name)


# 定义图片记录元组类
class Picinfo_Record(db.Model):
    __tablename__ = 'pic_info'
    __table_args__ = {
        "mysql_charset": "utf8",
    }

    city = db.Column(db.String(16))
    keyword = db.Column(db.String(60))
    path = db.Column(db.String(255), unique=True)
    # 声明联合主键
    __table_args__ = (
        PrimaryKeyConstraint('city', 'keyword'),
        {},
    )

    def __repr__(self):
        return 'Picinfo_Record:<city:%s keyword:%s path:%s>' % (self.city, self.keyword, self.path)


# 系统初始登录路由
@app.route('/', methods=['GET', 'POST'])
def login_surface():
    login_surface_form = loginform()
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')

        if login_surface_form.validate_on_submit():

            # 数据库用户名和密码匹配
            user = User.query.filter(User.name == user, User.password == password,User.is_delete == False).first()

            if user:
                # url_for()方法传入路由对应的函数就会返回路由对应的地址，
                # redirect()传入路由地址作为参数并且返回就会重定向置该路由执行该路由操作
                return redirect(url_for('analyse_surface'))

            else:
                flash('The username or password false!')

        else:
            flash('Input Error!')

    return render_template('login_surface.html', login_surface_form=login_surface_form)


# 用户登录成功后路由选择重定向/analyse地址
@app.route('/analyse', methods=['GET', 'POST'])
def analyse_surface():
    analyse_surface_form = analyseform()

    if request.method == 'POST':
        # 1.获取需要爬取数据对应的城市和关键字信息
        city = request.form.get('city')
        keyword = request.form.get('keyword')
        bind = str(city) + ' ' + str(keyword)  # city是一个数字代号

        # 2.传递城市和关键字作为参数进行爬取数据操作
        # 查询数据库看是否存在城市和关键字记录  返回对象
        # print('#########')  计算查询需要的时间
        # start = time.clock()
        pic_path = Picinfo_Record.query.filter(
            Picinfo_Record.city == city, Picinfo_Record.keyword == keyword).first()
        # end = time.clock()
        # print(end - start)  # 计时

        # 如果图片不存在，爬取数据生成图片，如果存在，直接上传图片
        if pic_path is None:  # 如果查不到则返回none
            # 爬虫模块
            Data = Data_spider.getData(city, keyword)

            if len(Data) == 0:
                flash('no information!')
                return redirect(url_for('analyse_surface'))
            Data_spider.saveData("require_data.csv", Data)
            pic_path = Data_spider.analyse_data("require_data.csv", bind)

            # 将爬取的图片记录存入数据库
            temp = Picinfo_Record(city=city,
                                  keyword=keyword, path=('static/wordclouds_res/' + bind + '.png'))  # 必须要加上变量引用提示符
            session = db.session
            session.add(temp)
            session.commit()
            session.close()

        # 用自定义函数get_img_stream()将图片转为字节流形式传给HTML网页
        else:
            pic_path = pic_path.path

        img_stream = get_img_stream(img_path=pic_path)

        return render_template('wordcloud_surface.html', img_stream=img_stream)

    return render_template('analyse_surface.html', analyse_surface_form=analyse_surface_form)


# 注册新账户路由
@app.route('/register', methods=['GET', 'POST'])
def register_surface():
    register_surface_form = registerform()

    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password1')
        email = request.form.get('email')

        if register_surface_form.validate_on_submit():
            # 对数据库操作加上异常处理更加安全，发现异常可以用rollback函数进行回滚
            try:
                if User.query.filter(User.name == user, User.password == password,User.is_delete == False).first():
                    flash('User exist!')
                    return redirect(url_for('register_surface'))

                if User.query.filter(User.email == email).first():
                    flash('email exist!')
                    return redirect(url_for('register_surface'))

                new_user = User(name=user, password=password, email=email, role_id=2, is_delete=False)
                db.session.add(new_user)
                db.session.commit()
                flash('success!')
                return redirect(url_for('login_surface'))

            except Exception as e:
                print(e)
                flash('注册失败！')
                db.session.rollback()

        else:
            flash('Input Error!')

    return render_template('register_surface.html', register_surface_form=register_surface_form)


# 注销用户
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw_surface():
    withdraw_surface_form = withdrawform()

    if request.method == 'POST':
        name = request.form.get('user')
        password = request.form.get('password')
        if withdraw_surface_form.validate_on_submit():
            try:
                # 根据用户名和密码来获取用户对象，没有返回空
                user = User.query.filter(User.name == name, User.password == password, User.is_delete == False).first()
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    flash('success!')
                else:
                    flash('User not exit!')
            except Exception as e:
                print(e)
                flash('注销失败！')
                db.session.rollback()
        else:
            flash('Input Error!')
    return render_template('withdraw_surface.html', withdraw_surface_form=withdraw_surface_form)


@app.route('/forget', methods=['GET', 'POST'])
def forget_surface():
    forget_surface_form = forgetpin(verifycode='请输入验证码')

    if request.method == 'POST':
        if forget_surface_form.validate_on_submit():
            if forget_surface_form.sendcode.data:  # 选中的是发送验证码
                name = request.form.get('user')
                mail = request.form.get('email')
                if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', mail):
                    user = User.query.filter(User.name == name, User.email == mail).first()
                    if user:
                        forget_surface.verify_code = email_plug.send_verify_email(mail_addr=mail)
                        forget_surface.start = time.time()  # 计时 todo 全局变量的使用
                        flash('发送成功,请输入验证码')
                        forget_surface_form.verifycode.data = ""
                    else:
                        flash('请输入正确的注册邮箱')
                        time.time()
                else:
                    flash("邮箱格式错误!")
                    time.time()  # 初始化时间
            else:  # 选中的是提交
                name = request.form.get('user')
                code = request.form.get('verifycode')
                end = time.time()
                timing = end - forget_surface.start
                if forget_surface.verify_code.__eq__(''):
                    # 提示没有输入验证码
                    flash('没有输入验证码')
                elif forget_surface.verify_code.__eq__(code) and timing < 905:  # 15min
                    return redirect(url_for('reset_surface', user=name))
                elif forget_surface.verify_code.__eq__(code) and timing >= 905:
                    flash('验证码失效')
                else:
                    flash("验证码错误")  # 验证码输入错误

    return render_template('forget_surface.html', forget_surface_form=forget_surface_form)


@app.route('/reset/<user>', methods=['GET', 'POST'])
def reset_surface(user):
    reset_surface_form = resetpin(user=user)  # 在路由中传递参数，在route里面使用<>来声明函数的形参
    if request.method == 'POST':
        name = request.form.get('user')
        password = request.form.get('password1')
        if reset_surface_form.validate_on_submit():
            try:
                user = User.query.filter(User.name == name).first()
                if user.password.__eq__(password):
                    flash('和原密码相同，请输入新密码')
                else:
                    User.query.filter_by(name=name).update({'password': password})
                    db.session.commit()
                    flash('success!')
                    return redirect(url_for('login_surface'))  # 重定位到登录

            except Exception as e:
                print(e)
                flash('更新失败！')
                db.session.rollback()
        else:
            flash('Input Error!')

    return render_template('reset_surface.html', reset_surface_form=reset_surface_form)


if __name__ == '__main__':
    # 注释如果再次运行，数据库已经保存内容
    db.drop_all()
    db.create_all()

    # role_1 = Role(role_name='管理员')
    role_1 = Role(role_name='admin')
    role_2 = Role(role_name='user')
    # role_2 = Role(role_name='用户')

    db.session.add_all([role_1, role_2])
    db.session.commit()

    user_1 = User(name='hzj', password='20000', email='1@qq.com', role_id=role_1.id, is_delete=False)
    user_2 = User(name='dyf', password='12345', email='2@qq.com', role_id=role_2.id, is_delete=False)
    user_3 = User(name='qjy', password='54321', email='3@qq.com', role_id=role_2.id, is_delete=False)
    user_4 = User(name='cyk', password='67890', email='4@qq.com', role_id=role_2.id, is_delete=False)
    user_5 = User(name='ksd', password='09876', email='5@qq.com', role_id=role_2.id, is_delete=False)
    user_6 = User(name='xxg', password='qwert', email='6@qq.com', role_id=role_2.id, is_delete=False)
    user_7 = User(name='nly', password='yuiop', email='7@qq.com', role_id=role_2.id, is_delete=False)
    user_8 = User(name='lsy', password='asdfg', email='8@qq.com', role_id=role_2.id, is_delete=False)
    user_9 = User(name='xjm', password='zxcvb', email='9@qq.com', role_id=role_2.id, is_delete=False)
    db.session.add_all([user_1, user_2, user_3, user_4, user_5, user_6, user_7, user_8, user_9])
    db.session.commit()

    # 用管理员密码作为主键的值,初始化第一条记录
    picinfo = Picinfo_Record(city='#', keyword='20000', path='')
    db.session.add_all([picinfo])
    db.session.commit()

    # app.run(host='127.0.0.1',port=8080)
    app.run(host='0.0.0.0',port=8080)

# 如果是外网访问的话，你还需要设置 host='0.0.0.0'，或者通过 apache 或者 nginx 转发。