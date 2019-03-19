from flask import Flask, url_for, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

#配置数据库
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()


    # 全局的两个变量移动到这个函数内
    name = 'AWSL'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)


    db.session.commit()
    click.echo('Done.')

#上下文处理函数
@app.context_processor
def inject_user():   #函数名可以随意修改
    user = User.query.first()
    return dict(user=user)   #需要返回字典，等同于return{'user': user}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':     #判断是否是POST请求
        title = request.form.get('title')   #传入表单对应输入字段的NAME值
        year = request.form.get('year')
        #验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('输入错误')
            return redirect(url_for('index'))
        #保存表单数据到数据库
        movie = Movie(title=title, year=year)  #创建记录
        db.session.add(movie)
        db.session.commit()
        flash('提交成功')
        return redirect(url_for('index'))

    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user,  movies=movies)


app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':   #处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title)  > 60:
            flash('输入错误')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title  #更新标题
        movie.year = year    #更新年份
        db.session.commit()  #提交数据库会话
        flash('提交成功')
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)   #传入被编辑的电影记录


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('index'))

@app.errorhandler(404)  #传入要处理的错误代码
def page_not_found(e):  #接受异常对象作为参数
    return render_template('404.html'), 404 #返回模板和状态码



if __name__ == '__main__':
    app .run(debug=True, host='0.0.0.0')
