from . import api
import random
# 图片验证码
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants, db
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from utils.sms_aliyun import send_msg_to_phone
# 引入用户信息
from ihome.models import User


# 图片验证码
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id:图片验证码编号
    :return: 正常图片，异常返回错误代码
    """
    # 获取参数
    # 检验参数
    # 业务逻辑处理
    # 返回值
    name, text, image_data = captcha.generate_captcha()
    # redis_store.set("image_code%s" % image_code_id, text)
    # redis_store.expire("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    # 记录名，有效期，记录值
    try:
        redis_store.setex("image_code%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except  Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="save imge_code id 错误")
    # 返回图片
    resp = make_response(image_data)
    resp.headers["Content-Type"] = 'image/jpg'
    return resp


# GET /api/v1.0/sms_codes
# 短信验证码
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """
    获取手机验证码
    :param mobile:
    :return:
    """
    # 获取参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 从redis获取图片验证码，但是有一个问题可能redis过期
    try:
        real_image_code = redis_store.get("image_code%s" % image_code_id)

    except Exception as e:
        current_app.looger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常reids')
    # 判断redis图片验证码是否过期
    if real_image_code is None:
        # 表示图片验证码不存在或者过期
        return jsonify(errno=RET.NODATA, errmsg='图片验证码失效')

    # 与用户真实写入的信息进行对比
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.NODATA, errmsg='图片验证码写错啦')
    # 判断手机号是否存在是否重复注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        pass
    else:
        if user is None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经存在')
    #  生成一个随机的6位数
    sms_code = "%06d" % str(random.randint(100000, 999999))
    print("短信验证码是:", sms_code)
    # 保存短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXIRES)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码失败')

    # 通过短信发送这个6位数
    result = send_msg_to_phone(mobile, sms_code)
    if result == 0:
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')
