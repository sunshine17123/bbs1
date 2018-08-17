from django import template
from blog import models
from django.db.models import Avg, Count

register = template.Library()


@register.inclusion_tag(filename='left_menu.html')
def left_menu(username):
    # 当前点击要看的博主对象
    user_obj = models.UserInfo.objects.filter(username=username).first()

    # 博主的主站的对象
    blog = user_obj.blog

    # 主站中的所有分类
    category_list = models.Category.objects.filter(blog=blog)

    # 主站中的所有标签
    tag_list = models.Tag.objects.filter(blog=blog)

    # 主站中的所有时间归档
    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={'create_y_m': "DATE_FORMAT(create_time,'%%Y-%%m')"}
    ).values('create_y_m').annotate(c=Count('id')).values('c', 'create_y_m')
    return {
        'user_obj': user_obj,
        'blog': blog,
        'category_list': category_list,
        'tag_list': tag_list,
        'archive_list': archive_list,
    }
