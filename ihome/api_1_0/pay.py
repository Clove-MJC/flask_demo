# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from ihome.models import Order
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
from alipay import AliPay
from ihome import constants, db
import os


@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_required
def order_pay(order_id):
    """发起支付宝支付"""
    user_id = g.user_id

    # 判断订单状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单数据有误")

    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2016102600767752",
        app_notify_url=None,  # 默认回调url
        app_private_key_string="""-----BEGIN RSA PRIVATE KEY-----
        MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDDuSCQb0S02RaZFYPs1TytTkYNamgD3Uqf0udxTKigR0GRabb4ovI3Nwjs/i8b4PqC5wFq7LzADmwRoaquve418uaAzFfrNva/a6hzEWtSw31R+fYpTStEvHfnJxtU7EhfpkoU1+C68tMfW4QEIQG/IjlZmdNggkpAC6I4Aeqbk2jooQZnIL3UsJ2sZ2UeBg/XgJJU4qVeTXMyS5mvdfPECWDjfCY7J/FLNnSPfZH4NE1+IllIdiAEQ1U3Hlyau6tVWUik9HMFJJldLD44iA08fvliShAOnzpHIitthMdFFCtnCcvhbCbpe5eN/9n4DocvRu660n3YfU/5Jp3Ci4CBAgMBAAECggEBAIREWnZhS3wv7O6dNJ9bZ3rzF7I/Q3XBGYoynAfcN2TBYtUjLOyQKcIYpiaKjEl527GU7UdWHyRnWq77ov4eCppYwV8vOQcTCONJnPfOQMoYpFs+4hT9Oo1kFF+Y9QaJ+0rwdMXrMcsFCJn7XZbwu15wgXNE2i0xP35SnljdKq/hWwTMZI5y9uL0pVVlKxxT+7clUg170dS3qRvZv60wvhFBHkySog5xsD2a+4ayLLr8q9dR9bjJGVlGn45CfoAgDt8v80a6HxFANb9C6BkuI9dgdUwPIdn2zCiIuwf1Mc7u7Ylavcsu2bkGToUzTp9sfRfwfQ2fjOd2FuICOSYcrbECgYEA4vjeKTTleIY9TMmzXp4TSFganGbt5v1KNKbCHyJzWVLI7pMd66aHHtY0hEAkADscn0s0SZYbkHFQ3JPzzNkZdkfnwjQGlwp3NKlofv4/+EZ27p2V7phXAgUWwtL3sjj9gOoMQlB9th45bJacuMwb/9KgsfYYZEu9TlFxT+jeC/UCgYEA3MEooORi51rzMh99qNcPu22FFgLG8H2GDTa4DXp+ZBLdkp8Q7SX6oBejcWbBdd8MiAs1nUdeZ2Y7R6Ikkxr2sN595d5bnvp6rAcAcuBUFlbsZygHRKDZgrSLpqf4saBzbJYWIxnGOO9H1cfGzf15SqBvtm+C8p08OKi5lJ8Ptt0CgYAbXByLoxC2QphJFVdF5JA2fEhY6h9rZMT5K9Dip+h3r/8Ao0NMELrhALk75+9vB7EfkpUu+aVA+CfjLwKIgvMKywgo5NSWiHBuLK2oAUX8y6GyidR0+nAikjJ4Ma4iEbSdQZlQtRsyRNpvOIiTzibh46XzTdMK5AZh1nduRofdsQKBgBCp1/pFIx4ZpG/tJpwfF8XrH3eo4AF5SCwpLD2AOJgvQGB391wfWMrK3gCKZCIUoyqFxhdIMt0VP3ZJy/76sxJoyRIX9cyLVcU0hhkly9Mf3ppu0BWjGqgeHsiGt2QZG31f2u3tXSQhE8gUW3JjJsu2Tphz1Guh6NDSE6gfVZ1VAoGAHgB20ihtMr1JKah2AQFyQQQimLpF0nAt8ATTm/qz66NYla5kTJlJ8BgCMlg3vidhZrivTjPDjpEuGf7XorH2MpIqng0ml91BOBR4St3P2GNLF809WWJzjZF3L0F2xFWzRRE7/a4YTHiUirq1EJgaTMo/AQB1p/CgIEpOoHsNRhY=
        -----END RSA PRIVATE KEY-----""",  # 私钥
        alipay_public_key_string="""-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiP+d4l/WHrnKvF38gwRxnmLNdDTuUskj2qQvLcY2z4hqo4ltfYPJh+OpHNztq5ygdclu2b80EnFykfJUEW+VYbPGrTQKkFE7CNadoXkRz8bxm8EavTWyO/PzhhseGe84L2UL4S3fuOYos7E1Ht++DLIzb+cTSqO/ckLzvD4wawoRN7wMiA8rbP6rhfGY+oqSALxvsghM5iXzsbaqJRfQ3MztG7LRoebiktu0wySRotiX1izyawz6WByTfxGnOJn4Y18bQ+O69vF/17j0U8sfw0HhzZySV3M+wza0/5Ugc9QVtNCXPKN8esfu+lPsgdEX/yZNYCksaMdaVKGlNW3quQIDAQAB
        -----END PUBLIC KEY-----""",
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount / 100.0),  # 总金额
        subject=u"爱家租房 %s" % order.id,  # 订单标题
        return_url="http://127.0.0.1:7777/payComplete.html",  # 返回的连接地址
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 构建让用户跳转的支付连接地址
    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url": pay_url})


@api.route("/order/payment", methods=["PUT"])
def save_order_payment_result():
    """保存订单支付结果"""
    alipay_dict = request.form.to_dict()

    # 对支付宝的数据进行分离  提取出支付宝的签名参数sign 和剩下的其他数据
    alipay_sign = alipay_dict.pop("sign")

    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2016102600767752",
        app_notify_url=None,  # 默认回调url
        app_private_key_string="""-----BEGIN RSA PRIVATE KEY-----
        MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDDuSCQb0S02RaZFYPs1TytTkYNamgD3Uqf0udxTKigR0GRabb4ovI3Nwjs/i8b4PqC5wFq7LzADmwRoaquve418uaAzFfrNva/a6hzEWtSw31R+fYpTStEvHfnJxtU7EhfpkoU1+C68tMfW4QEIQG/IjlZmdNggkpAC6I4Aeqbk2jooQZnIL3UsJ2sZ2UeBg/XgJJU4qVeTXMyS5mvdfPECWDjfCY7J/FLNnSPfZH4NE1+IllIdiAEQ1U3Hlyau6tVWUik9HMFJJldLD44iA08fvliShAOnzpHIitthMdFFCtnCcvhbCbpe5eN/9n4DocvRu660n3YfU/5Jp3Ci4CBAgMBAAECggEBAIREWnZhS3wv7O6dNJ9bZ3rzF7I/Q3XBGYoynAfcN2TBYtUjLOyQKcIYpiaKjEl527GU7UdWHyRnWq77ov4eCppYwV8vOQcTCONJnPfOQMoYpFs+4hT9Oo1kFF+Y9QaJ+0rwdMXrMcsFCJn7XZbwu15wgXNE2i0xP35SnljdKq/hWwTMZI5y9uL0pVVlKxxT+7clUg170dS3qRvZv60wvhFBHkySog5xsD2a+4ayLLr8q9dR9bjJGVlGn45CfoAgDt8v80a6HxFANb9C6BkuI9dgdUwPIdn2zCiIuwf1Mc7u7Ylavcsu2bkGToUzTp9sfRfwfQ2fjOd2FuICOSYcrbECgYEA4vjeKTTleIY9TMmzXp4TSFganGbt5v1KNKbCHyJzWVLI7pMd66aHHtY0hEAkADscn0s0SZYbkHFQ3JPzzNkZdkfnwjQGlwp3NKlofv4/+EZ27p2V7phXAgUWwtL3sjj9gOoMQlB9th45bJacuMwb/9KgsfYYZEu9TlFxT+jeC/UCgYEA3MEooORi51rzMh99qNcPu22FFgLG8H2GDTa4DXp+ZBLdkp8Q7SX6oBejcWbBdd8MiAs1nUdeZ2Y7R6Ikkxr2sN595d5bnvp6rAcAcuBUFlbsZygHRKDZgrSLpqf4saBzbJYWIxnGOO9H1cfGzf15SqBvtm+C8p08OKi5lJ8Ptt0CgYAbXByLoxC2QphJFVdF5JA2fEhY6h9rZMT5K9Dip+h3r/8Ao0NMELrhALk75+9vB7EfkpUu+aVA+CfjLwKIgvMKywgo5NSWiHBuLK2oAUX8y6GyidR0+nAikjJ4Ma4iEbSdQZlQtRsyRNpvOIiTzibh46XzTdMK5AZh1nduRofdsQKBgBCp1/pFIx4ZpG/tJpwfF8XrH3eo4AF5SCwpLD2AOJgvQGB391wfWMrK3gCKZCIUoyqFxhdIMt0VP3ZJy/76sxJoyRIX9cyLVcU0hhkly9Mf3ppu0BWjGqgeHsiGt2QZG31f2u3tXSQhE8gUW3JjJsu2Tphz1Guh6NDSE6gfVZ1VAoGAHgB20ihtMr1JKah2AQFyQQQimLpF0nAt8ATTm/qz66NYla5kTJlJ8BgCMlg3vidhZrivTjPDjpEuGf7XorH2MpIqng0ml91BOBR4St3P2GNLF809WWJzjZF3L0F2xFWzRRE7/a4YTHiUirq1EJgaTMo/AQB1p/CgIEpOoHsNRhY=
        -----END RSA PRIVATE KEY-----""",  # 私钥
        alipay_public_key_string="""-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiP+d4l/WHrnKvF38gwRxnmLNdDTuUskj2qQvLcY2z4hqo4ltfYPJh+OpHNztq5ygdclu2b80EnFykfJUEW+VYbPGrTQKkFE7CNadoXkRz8bxm8EavTWyO/PzhhseGe84L2UL4S3fuOYos7E1Ht++DLIzb+cTSqO/ckLzvD4wawoRN7wMiA8rbP6rhfGY+oqSALxvsghM5iXzsbaqJRfQ3MztG7LRoebiktu0wySRotiX1izyawz6WByTfxGnOJn4Y18bQ+O69vF/17j0U8sfw0HhzZySV3M+wza0/5Ugc9QVtNCXPKN8esfu+lPsgdEX/yZNYCksaMdaVKGlNW3quQIDAQAB
        -----END PUBLIC KEY-----""",
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # 借助工具验证参数的合法性
    # 如果确定参数是支付宝的，返回True，否则返回false
    result = alipay_client.verify(alipay_dict, alipay_sign)

    if result:
        # 修改数据库的订单状态信息
        order_id = alipay_dict.get("out_trade_no")
        trade_no = alipay_dict.get("trade_no")  # 支付宝的交易号
        try:
            Order.query.filter_by(id=order_id).update({"status": "WAIT_COMMENT", "trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK")
