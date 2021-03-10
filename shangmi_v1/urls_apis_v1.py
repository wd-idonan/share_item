from django.conf.urls import url
from .apis_v1 import *

urlpatterns = [
    url(r'^advs/',AdvertiseListAPIView.as_view()),
    # url(r'^advs/',AdvAPI.as_view()),
    url(r'^actives/',ActiveListAPIView.as_view()),
    url(r'^active/',ActiveRetrieveAPIView.as_view()),
    url(r'^verify_code/',VerifyCodeViewSet.as_view({"post":"send"})),
    url(r'^test_code_bx/',NewBaoXianViewSet.as_view({"post":"test_code"})),
    url(r'^get_money_bx/',NewBaoXianViewSet.as_view({"post":"get_money"})),
    url(r'^home/',HomeIndexListAPIView.as_view()),
    url(r'^money_index/',CashOutRetrieveAPIView.as_view()),
    url(r'^login/',ShangmiUserViewSet.as_view({"post":"login"})),

]