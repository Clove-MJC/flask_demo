# 导入readis
import redis
# 设置配置信息
class Config(object):

    SECRET_KEY = 'sadjkahsdhjkashd'
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
    SQLALCHEMY_MAX_OVERFLOW = 2
    # redis 配置
    redis_host = '127.0.0.1'
    redis_port = 6379
    # sesson配置
    SESSION_TYPE = 'redis'  # session类型为redis
    SESSION_PERMANENT = False  # 如果设置为True，则关闭浏览器session就失效
    SESSION_REDIS = redis.Redis(host=redis_host, port=redis_port)  # 用于连接redis的配置



#开发模式信息
class DevelopentConfig(Config):
    Dubug = True


#生产环境
class ProductionConfig(Config):
    pass


#判断映射关系

config_map={
    "develop":DevelopentConfig,
    "prouduct":ProductionConfig
}