#coding:utf-8
#导入flask 创建一个模版

from  flask import Flask
from  flask_session import Session
#导入readis
import redis
from  flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)

#设置配置信息
class Config(object):
    Dubug=True
    SECRET_KEY='sadjkahsdhjkashd'
    # 设置数据库的链接地址
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:py123456@localhost:3306/ihome'
    # 动态追踪修改设置，如未设置只会提示警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 查询时会显示原始SQL语句
    SQLALCHEMY_ECHO = False
    # 数据库连接池的大小
    SQLALCHEMY_POOL_SIZE = 10
    # 指定数据库连接池的超时时间
    SQLALCHEMY_POOL_TIMEOUT = 10
    # 控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃。
    SQLALCHEMY_MAX_OVERFLOW=2
    #redis 配置
    redis_host='127.0.0.1'
    redis_port=8888
    #sesson配置
    SESSION_TYPE = 'redis'  # session类型为redis
    SESSION_PERMANENT = False  # 如果设置为True，则关闭浏览器session就失效
    SESSION_REDIS = redis.Redis(host=redis_host, port=redis_port, password='123123')  # 用于连接redis的配置

 # 加载配置
app.config.from_object(Config)
# 数据库
db=SQLAlchemy(app)
#readis 工具进行缓存链接对象
redis_store=redis.StrictRedis(host=Config.redis_host,port=Config.redis_port)
#利用flask自带的工具把seeion缓存到readis中
Session(app)
@app.route('/index')
def index():
    return  "index page"


if __name__=="__main__":
    app.run()