#coding:utf-8
#导入flask 创建一个模版
#
from  flask import Flask
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
    #redis 配置
    redis_host='127.0.0.1'
    redis_port=8888
 # 加载配置
app.config.from_object(Config)
# 数据库
db=SQLAlchemy(app)
#readis 工具进行缓存链接对象
redis_store=redis.StrictRedis(host=Config.redis_host,port=Config.redis_port)

@app.route('/index')
def index():
    return  "index page"


if __name__=="__main__":
    app.run()