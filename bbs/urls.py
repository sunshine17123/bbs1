"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from blog import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 登陆、注销、验证码
    url(r'^login/', views.login),
    url(r'^logout/', views.logout),
    url(r'^v-code/', views.v_code),

    # 滑动验证
    url(r'^slide-login/', views.slide_login),
    url(r'^pcgetcaptcha/', views.pcgetcaptcha),


    url(r'^index/', views.index),
    # 注册
    url(r'^register/', views.register),


    url(r'^test/', views.test),

    url(r'^blog/', include('blog.urls')),

    # 点赞
    url(r'^updown/', views.updown),

]
