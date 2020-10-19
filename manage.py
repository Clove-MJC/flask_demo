# coding:utf-8
from ihome import create_app, db
from flask_script import Manager
# 数据库迁移
from flask_migrate import Migrate, MigrateCommand

# 创建flask的应用对象
app = create_app("develop")
# 添加数据库迁移等工具
manager = Manager(app)
# 生成migrate对象 用来数据库迁移
Migrate(app, db)
# 添加db命令
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    # app.run()
    manager.run()
