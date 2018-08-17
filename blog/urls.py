from django.conf.urls import url
from blog import views

urlpatterns = [
    #跳转到想要看的博主的首页
    url(r'^(\w+)/$',views.single_user_home),

    url(r'^(\w+)/(category|tag|archive)/(.*)/$',views.single_user_home),
    url(r'^(\w+)/p/(\d+)/$',views.article),

]
