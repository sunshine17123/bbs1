from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from blog.forms import LoginForm, RegisterForm
from django.contrib import auth
from django.http import JsonResponse

from geetest import GeetestLib  # 用pycharm装
from blog import models

from blog.utils.mypage import Pagination  # 分页
from django.db.models import Avg, Count  # 导入ORM分组查询的聚合函数
from django.db.models import Q,F

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 普通验证码登陆
def login(request):
    login_obj = LoginForm()
    if request.method == 'POST':
        res = {'code': 0}
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        v_code = request.POST.get('v_code')
        if v_code.upper() != request.session.get('v_code', ''):
            res['code'] = 1
            res['err_msg'] = '验证码错误'
        else:
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名和密码正确
                auth.login(request, user)
            else:
                # 用户名和密码错误
                res['code'] = 1
                res['err_msg'] = '用户名或者密码错误'
        print(res)
        return JsonResponse(res)
    return render(request, 'login.html', {'login_obj': login_obj})


def logout(request):
    auth.logout(request)
    return redirect('/login/')


# 随机生成图片
def v_code(request):
    '''随机生成图片'''

    from PIL import ImageDraw, Image, ImageFont
    import random

    # 生成随机的颜色
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成图片对象
    image_obj = Image.new(
        'RGB',  # 生成图片的模式
        (250, 35),  # 图片大小
        random_color(),
    )

    # 生成一个准备写字的画笔
    draw_obj = ImageDraw.Draw(image_obj)  # 在那个图片对象写（传入对应的图片对象）
    font_obj = ImageFont.truetype('static/fonts/kumo.ttf', size=28)

    # 生成随机的验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))
        l = chr(random.randint(65, 90))
        u = chr(random.randint(97, 122))
        r = random.choice([n, l, u])
        tmp.append(r)
        draw_obj.text(
            (i * 45 + 25, 0),  # 坐标
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj  # 字体
        )

    v_code = ''.join(tmp)  # 得到最终的验证码
    request.session['v_code'] = v_code.upper()

    # 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, "png")
    # 从内存读取图片数据
    data = f.getvalue()
    return HttpResponse(data, content_type="image/png")


# 滑动验证码第一步的API，初始化一些参数用来校验滑动验证码
def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 滑动验证码登陆
def slide_login(request):
    login_obj = LoginForm()
    if request.method == "POST":
        res = {'code': 0}
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        username = request.POST.get('username')
        pwd = request.POST.get('password')

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        if result:
            user = auth.authenticate(username=username, password=pwd)
            login_obj = LoginForm(request.POST)
            login_obj.is_valid()
            if user:
                # 用户名和密码正确
                auth.login(request, user)
            else:
                # 用户名和密码错误
                res['code'] = 1
                res['err_msg'] = '用户名或者密码错误'
        else:
            # 滑动验证码验证失败
            res = {'code': 2}
            res = {'err_msg': '验证码不正确'}
        # result = {"status": "success"} if result else {"status": "fail"}
        return JsonResponse(res)
    return render(request, 'login.html', {'login_obj': login_obj})


def register(request):
    register_obj = RegisterForm()
    if request.method == 'POST':
        return HttpResponse('ok')
    return render(request, 'register.html', {'register_obj': register_obj})


def index(request):
    '''首页'''
    data_list = models.Article.objects.all()
    pager = Pagination(request.GET.get("page"), len(data_list), request.path_info)
    data_list = data_list[pager.start:pager.end]
    page_html = pager.page_html()
    return render(request, 'index.html', {"data_list": data_list,
                                          "page_html": page_html,
                                          })


def single_user_home(request, username, *args):
    # copy index 页面的业务逻辑

    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return HttpResponse('<h1>404....</h1>')

    blog = user_obj.blog
    category_list = models.Category.objects.filter(blog=blog)
    tag_list = models.Tag.objects.filter(blog=blog)
    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={
            'y_m': "DATE_FORMAT(create_time,'%%Y-%%m')"
        }
    ).values('y_m').annotate(c=Count('id')).values('y_m', 'c')
    print('-archive_list-->', archive_list)
    print('-category_list-->', category_list)
    print('-tag_list-->', tag_list)

    article_list = models.Article.objects.filter(user=user_obj)  # 查询到所有的文章且没有args时返回

    if args:  # 不为空时，用查到的文章queryset对象,在惊醒筛选
        print('args', args)
        if args[0] == 'category':
            print(args[1])
            article_list = article_list.filter(category__title=args[1])
        elif args[0] == 'tag':
            article_list = article_list.filter(tags__title=args[1])
        else:
            # 'select':"DATE_FORMAT(create_time,'%%Y-%%m')" 或者'select':r'DATE_FORMAT(create_time,%Y-%m)'
            try:
                year, month = args[1].split('-')
                print('====article_list', article_list)
                # article_list = article_list.filter(create_time__year=year, create_time__month=month)
                # article_list = article_list.filter(create_time__year='2018')
                print('1', article_list.first().create_time)
                print('====article_list', article_list)

            except Exception as e:
                pass
    print('sdjfsalkdjflksajd', article_list)

    print(len(article_list))
    pager = Pagination(request.GET.get("page"), len(article_list), request.path_info)
    article_list = article_list[pager.start:pager.end]
    page_html = pager.page_html()
    print(page_html)

    return render(request, 'home.html', {
        # copy index 页面的业务逻辑
        "page_html": page_html,
        'article_list': article_list,

        'username': username,

        # 'user_obj':user_obj,
        # 'blog': blog,
        # 'category_list': category_list,
        # 'tag_list': tag_list,
        # 'archive_list':archive_list,
    })

    # # 查到当前用户关联
    # article_obj = models.Article.objects.filter(title=request.GET.get('title', '')).first()
    # print(article_obj.tags.all())
    # tags_obj = models.Tag.objects.all()
    # print('tags--->', tags_obj.count())
    # category_obj = models.Category.objects.all()
    # print('category_obj--->', category_obj.count())
    # return render(request, 'sun.html', {'article_obj': article_obj,
    #                                     'tags_obj': tags_obj,
    #                                     'category_obj': category_obj,
    #                                     })


def article(request, username, id):
    '''

    :param request:
    :param username: 博主的名字
    :param id: 文章的id
    :return: 文章消息内容
    '''
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog = user_obj.blog
    article_obj = models.Article.objects.filter(id=id).first()
    return render(request, 'article.html', {
        'blog': blog,
        'article_obj': article_obj,
        'username': username,
    })


# 点赞
def updown(request):
    res = {'code':0}
    # 取到ajax传的值
    user_id = request.POST.get('user_id')
    article_id = request.POST.get('article_id')
    is_up = request.POST.get('is_up')
    print(user_id)
    print(article_id)
    print(is_up)
    # 判断自己不能给自己点赞
    is_up = True if is_up.upper() == 'TRUE' else False
    article_obj = models.Article.objects.filter(user__id=user_id,id=article_id)

    if article_obj:
        res['code'] = 1
        res['msg'] = '不能点赞自己' if is_up else '不能反对自己内容'
    # 判断是否已经点过赞或踩过
    is_exist = models.ArticleUpDown.objects.filter(article_id=article_id,user_id=user_id).first()
    if is_exist:
        # 数据库存在相同的文章记录和点赞记录，就证明点过赞
        res['code'] = 1
        res['msg'] = '您已经推荐过了' if is_exist.is_up else '您已经反对过了'
    else:
        # 成功点赞
        # 往数据库中加数据
        models.ArticleUpDown.objects.create(article_id=article_id, user_id=user_id)
        if is_up:
            # 更新Article表中的点赞数
            models.Article.objects.filter(id=article_id).update(up_count=F('up_count')+1)
        else:
            # 更新Article表中的踩灭数
            models.Article.objects.filter(id=article_id).update(down_count=F('down_count')+1)
        res['msg'] = '点赞成功' if is_up else '踩灭成功'

    return JsonResponse(res)


def test(request):
    return render(request, 'base.html')
