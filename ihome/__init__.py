# 导入配置文件
from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
# 导入readis
import redis
# 导入防攻击
from flask_wtf import CSRFProtect
from flask_session import Session


# 数据库
db = SQLAlchemy()

# 创建redis对象
# readis 工具进行缓存链接对象
redis_store = None

# 工厂模式 flask自带的
def create_app(config_name):
    """
    创建flask应用对象
    :param config_name: 配置模式的模式的名字("develop 生产模式"，"product")
    :return:
    """
    # 构造对象
    app = Flask(__name__)

    # 加载配置
    # 根据配置模式的名字来获取配置参数的类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)
    # 使用app初始化db
    db.init_app(app)
    # readis 工具进行缓存链接对象
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.redis_host, port=config_class.redis_port)
    # 利用flask自带的工具把seeion缓存到readis中
    Session(app)
    # 为flask补充防护攻击
    CSRFProtect(app)
    #注册蓝图,添加路有地址
    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")
    return app
