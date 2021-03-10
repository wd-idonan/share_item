import datetime
import json

import random
import shortuuid
from django.conf import settings
from django.core.cache import caches, cache
from django.db.models import Sum
from django.forms import model_to_dict
from djcelery.views import JsonResponse
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import requests
from .models import *
from .serializers import *
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from .baoxian_util import submit_one

cache_user = caches["user"]


# 显示主页的图片
class AdvertiseListAPIView(ListAPIView):
    queryset = Advertise.objects.filter(
        is_used=True
    )
    serializer_class = AdvertiseSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        print(serializer.data)

        return Response({
            "code": 1,
            "msg": "OK",
            "data": serializer.data,
            "hint": "领钱",
            "scan": "支付"
        })


class AdvAPI(View):
    def get(self, req):
        advs = Advertise.objects.filter(
            is_used=True
        )
        data = [model_to_dict(i) for i in advs]
        print(data)
        return JsonResponse({
            "code": 1,
            "msg": "OK",
            "data": data,
            "hint": "领钱",
            "scan": "支付"
        })


# 显示活动列表
class ActiveListAPIView(ListAPIView):
    queryset = Active.objects.filter(
        is_active=True
    )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 快速活动
        fast = queryset.filter(
            is_fast=True
        )
        # 非快速活动
        unfast = queryset.filter(
            is_fast=False
        )
        fast_data = []
        for i in fast:
            tmp = model_to_dict(i)
            tmp["btn_name"] = "领取"
            if i.need_num == 0:
                tmp["percent"] = "30"
            else:
                tmp["percent"] = round((i.complete_num / i.need_num), 2) * 100
                if tmp["percent"] < 40:
                    tmp["percent"] = random.randrange(30, 40)
            fast_data.append(tmp)
        unfast_data = []
        for i in unfast:
            tmp = model_to_dict(i)
            tmp["btn_name"] = "领取"
            if i.need_num == 0:
                tmp["percent"] = "30"
            else:
                tmp["percent"] = round((i.complete_num / i.need_num), 2) * 100
                if tmp["percent"] < 40:
                    tmp["percent"] = random.randrange(30, 40)
            unfast_data.append(tmp)

        return Response({
            "code": 1,
            "msg": "ok",
            "data": {
                "fast": fast_data,
                "unfast": unfast_data,
                "phone": "红包作用：结账抵扣或者提现",
                "title": {
                    "first": "快快领",
                    "last": "慢慢攒"
                }
            }

        })


# 获取单条活动信息
class ActiveRetrieveAPIView(RetrieveAPIView):
    serializer_class = ActiveSerializer

    def retrieve(self, request, *args, **kwargs):
        aid = request.query_params.get("id")
        instance = Active.objects.get(pk=aid)
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "msg": "OK",
            "data": serializer.data
        })


# 微信用户登录，调取第三方接口
class ShangmiUserViewSet(ViewSet):

    @action(methods=["post"], detail=False)
    def login(self, req):
        code = req.data.get("code")
        mini_type = req.data.get("mini_type")
        token = req.data.get("token")
        nick_name = req.data.get("nick_name")
        print("redis前面")
        user_id = cache_user.get(token)
        if user_id:
            print("缓存的数据")
            return Response({
                "code": 200,
                "msg": "OK",
                "data": {
                    "token": token,
                    "uid": user_id
                }
            })
        url = settings.SMALL_WEIXIN_OPENID_URL
        params = {
            "js_code": code,
            "appid": "wxa69b51dadaf1c8d2",
            "secret": "ac236516a216f44a1c7a698a7679b1d2"
        }
        response = requests.get(url, params=params)
        data = json.loads(response.content.decode())
        print(data)
        if "errorcode" in data:
            return Response({
                "code": 2,
                "msg": "登陆失败",
                "data": data
            })
        else:
            print("生成的数据")
            openid = data.get("openid")
            user = ShangmiUser.objects.get_or_create(openid=openid)[0]
            print(user)
            token = shortuuid.uuid()
            cache_user.set(token, user.id, settings.USER_TOKEN_LIFE)
            user.source = mini_type
            user.nick_name = nick_name
            user.save()
            return Response({
                "code": 200,
                "msg": "OK",
                "data": {
                    "token": token,
                    "uid": user.id
                }
            })


# 获取验证码，调取第三方接口(保险)
class VerifyCodeViewSet(ViewSet):

    @action(methods=["post"], detail=False)
    def send(self, req):
        phone = req.data.get("phone")
        type = req.data.get("type")
        # 随机生成4位验证码
        code = str(random.randrange(1000, 10000))
        template_param = "{\"code\":\"%s\"}" % code

        client = AcsClient(settings.ACCESS_KEY_ID, settings.ACCESS_SECRET_KEY, settings.REGION_ID)

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(settings.DOMAIN)
        request.set_method('POST')
        request.set_protocol_type('http')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('PhoneNumbers', phone)
        request.add_query_param('SignName', settings.SIGN_NAME)
        request.add_query_param('TemplateCode', settings.TEMPLATE_NAME)
        request.add_query_param('TemplateParam', template_param)

        response = client.do_action_with_exception(request)
        res = json.loads(response.decode())
        if res.get("Message") == "OK" and res.get("Code") == "OK":
            live_time = 60 * 5  # 5分钟
            # cache.set("baoxian" + phone, code, live_time)
            cache.set(type + phone, code, live_time)
            data = {
                "code": 200,
                "msg": "发送成功"
            }
        else:
            data = {
                "code": 2,
                "msg": res.get("Message")
            }
        return Response(data)


# 领取保险奖励  先校验验证码
class NewBaoXianViewSet(ViewSet):

    @action(methods=["post"], detail=False)
    def test_code(self, req):
        # 获取前端传来的验证码和电话
        code = req.data.get("code")
        phone = req.data.get("phone")
        type = req.data.get("type")
        cache_code = cache.get(type + phone)
        if code == cache_code:
            return Response({
                "code": 200,
                "msg": "OK",

            })
        else:
            return Response({
                "code": 2,
                "msg": "验证码错误"
            })

    @action(methods=["post"], detail=False)
    def get_money(self, req):
        token = req.data.get("token")
        aid = req.data.get("aid")
        name = req.data.get("name")
        phone = req.data.get("phone")
        user_id = cache_user.get(token)
        user = ShangmiUser.objects.get(pk=user_id)
        active = Active.objects.get(pk=aid)
        if UserActiveLog.objects.filter(
                user=user,
                active=active,
                status=1
        ).exists():
            return Response({
                "code": 2,
                "msg": "你已经参与过了，可分享他人"
            })
        birth = ""
        sex = ""
        code = ""
        idcard = ""
        res = submit_one(name, phone, birth, sex, idcard, code)
        if res.get("error_code") == 80 or res.get("error_code") == 0:
            try:
                balance = Balance.objects.get(
                    user=user
                )
            except:
                balance = Balance.objects.create(
                    user=user
                )
            # 修改日志状态
            UserActiveLog.objects.create(
                user=user,
                active=active,
                integral=active.give_money,
                type="join",
                status=1
            )
            # 修改活动数量
            active.complete_num += 1
            active.save()
            # 添加用户积分
            balance.money += active.give_money
            balance.save()
            # 保存用户信息
            user.name = name
            user.phone = phone
            user.save()
            return Response({
                "code": 200,
                "msg": "领取成功 积分已经存至余额"
            })
        else:
            return Response({
                "code": 2,
                "msg": res.get("error_msg")
            })


# 校验验证码（装修）
class RenovationViewSet(ViewSet):

    @action(methods=["post"], detail=False)
    def test_code(self, req):
        phone = req.data.get("phone")
        type = req.data.get("type")
        code = req.data.get("code")
        cache_code = cache.get(type + phone)
        if code == cache_code:
            return Response({
                "code": 200,
                "msg": "OK"
            })
        else:
            return Response({
                "code": 2,
                "msg": "验证码错误"
            })

    @action(methods=["post"], detail=False)
    def get_money(self, req):
        token = req.data.get("token")
        aid = req.data.get("aid")
        lat = req.data.get("lat")
        lng = req.data.get("lng")
        phone = req.data.get("phone")
        user = ShangmiUser.objects.get(pk=cache_user.get(token))
        active = Active.objects.get(pk=aid)
        if UserActiveLog.objects.filter(
                user=user,
                active=active,
                status=1
        ).exists():
            return Response({
                "code": 2,
                "msg": "你已领取过奖励,可分享他人"
            })
        else:
            log = UserActiveLog.objects.create(
                user=user,
                active=active,
                status=1,
                integral=active.give_money,
                type="join"
            )
            active.complete_num += 1
            active.save()
            try:
                balance = Balance.objects.get(user=user)
            except:
                balance = Balance.objects.create(user=user)
            balance.money += active.give_money
            balance.save()
            user.lat = lat
            user.lng = lng
            user.phone = phone
            user.save()
            return Response({
                "code":200,
                "msg":"OK"
            })


# 个人主页
class HomeIndexListAPIView(ListAPIView):

    def list(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        user = ShangmiUser.objects.get(pk=cache_user.get(token))
        actives = UserActiveLog.objects.filter(user=user)
        # 审核通过的数量
        finish_count = actives.filter(status=1).count()
        # 审核未通过的数量
        doing_count = actives.filter(status=0).count()
        now = datetime.datetime.now()
        zero_now = now.replace(hour=0,minute=0,second=0)
        print(now,"now",zero_now,"zero_now")
        today_money = actives.filter(
            create_time__gte=zero_now,
            create_time__lte=now,
            status=1
        ).aggregate(Sum("integral")).get("integral__sum")
        if not today_money:
            today_money = 0.00
        else:
            today_money = "%.2f"%(today_money/100)
        try:
            money = Balance.objects.get(user=user).money
        except:
            money=0
        data = {
            "code":200,
            "msg":"OK",
            "data":{
                "finish_count":finish_count,
                "doing_count":doing_count,
                "money":money,
                "today":today_money,
                "is_show_tixian":True,
                "wechat":"010-59440917",
                "option":{
                    "t1":"今日收益",
                    "t2": "提现",
                    "t3": "收入明细",
                    "t4": "任务明细",
                    "t5": "付款记录",
                    "t6": "提现记录",
                    "t7": 0
                }
            }
        }
        return Response(data)

# 提现
class CashOutRetrieveAPIView(RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        data = {
            "code":200,
            "msg":"OK",
            "data":{
                "target":"提现到",
                "weixin":"微信零钱",
                "hint":"提现金额需大于等于1元",
                "num_hint":"提现金额",
                "now":"本次可提现",
                "all":"全部提现",
                "input_hint":"输入金额超过零钱余额",
                "btn":"提现"
            }
        }
        return Response(data)