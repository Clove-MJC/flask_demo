from . import api
# 图片验证码
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id:图片验证码编号
    :return:
    """
    # 获取参数
    # 检验参数
    # 业务逻辑处理
    # 返回值
    name, text, image_data = captcha.generate_captcha()
    # redis_store.set("image_code%s" % image_code_id, text)
    # redis_store.expire("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    #记录名，有效期，记录值
    try:
        redis_store.setex("image_code%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except  Exception as e:
                pass