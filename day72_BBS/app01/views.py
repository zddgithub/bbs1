from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required


# Create your views here.

def register(request):
    form_obj = MyRegForm()
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        form_obj = MyRegForm(request.POST)
        if form_obj.is_valid():
            # print(form_obj.cleaned_data)
            # 得到四个键值对
            # {'username': 'jack', 'password': '123', 'confirm_password': '123', 'email': '123@qq.com'}
            # 将校验通过的数据字典赋值个一个变量
            clean_data = form_obj.cleaned_data
            # 将字典中的confirm_password键值对删除
            clean_data.pop('confirm_password')

            # 获取用户头像
            file_obj = request.FILES.get('avatar')
            # 针对用户头像一定要判断是否传值，不能直接添加到字典中去
            if file_obj:
                clean_data['avatar'] = file_obj
            # 直接操作数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            # 注册成功之后要跳转到一个登录界面，所以给这个前后端交互的字典加上一个url
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)  # 将这个字典返回给回调函数

    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        # 针对ajax的前后端交互，通常会定义一个字典
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 校验验证码是否正确
        if request.session.get('code').upper() == code.upper():  # 都转成大写来比较(忽略大小写)
            # 校验用户名和密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                # 校验成功的话，给字典增加一个url，之后再跳转到home首页
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


# 图片相关的模块
from PIL import Image, ImageDraw, ImageFont
# Image:生成图片
# ImageDraw：在图片上写字
# ImageFont：控制字体样式
from io import BytesIO, StringIO
# 内存管理器模块
# BytesIO：临时帮你存储数据，返回时数据是二进制
# StringIO：临时帮你存储数据，返回时数据是字符串

import random


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    # 推导步骤1：直接获取后端现成的图片二进制数据发送给前端，图片局限于本地
    # with open(r'/Users/dingding/PycharmProjects/day72_BBS/static/img/default.jpg','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤2：利用pillow模块动态产生图片,io操作频繁,效率低
    # img_obj = Image.new('RGB',(430,35),'red')
    # img_obj = Image.new('RGB',(430,35),get_random())
    # 先将图片对象保存起来
    # with open('x.png','wb') as f:
    #     img_obj.save(f,'png')
    # 再将图片对象读取出来
    # with open('x.png','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤3：
    # img_obj = Image.new('RGB', (430, 35), get_random())
    # 生成一个io内存管理器对象,可以看成是文件句柄
    # io_obj = BytesIO()
    # img_obj.save(io_obj,'png')   # 要指定图片的格式
    # 从内存管理器中读取二进制的图片数据返回给前端
    # return HttpResponse(io_obj.getvalue())

    # 最终步骤4：写图片验证码
    img_obj = Image.new('RGB', (430, 35), get_random())
    # 产生一个画笔对象
    img_draw = ImageDraw.Draw(img_obj)
    # 字体样式(.ttf格式的文件)
    img_font = ImageFont.truetype('static/font/杨任东竹石体-Semibold.ttf', 30)  # 要加上字体大小

    # 接下来产生随机验证码(包含5位数的数字、大写小写字母)
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))  # chr会将数字通过ASCII表转成数字对应的字母
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))  # 转成字符串
        # 从上面3个随机选择一个
        tmp = random.choice([random_upper, random_lower, random_int])

        # 将产生的随机字符串一个个写入到图片上(一个个写可以控制每个字之间的间隙，生成之后再写就没法控制间隙了)
        img_draw.text((i * 60 + 50, 0), tmp, get_random(), img_font)
        code += tmp
    print(code)
    # 随机验证码在登录的视图函数中需要用到，要进行校验，所以需要存起来，并且其他视图函数也要能拿到，可以存到session中。
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    # 查询本网站所有的文章数据展示到前端页面，这里可以自行加上分页器
    article_queryset = models.Article.objects.all()
    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    # 直接判断是不是ajax请求，只处理ajax请求
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')
            is_right = request.user.check_password(old_password)  # 自动转成加密密码并校验
            if is_right:
                if new_password == confirm_new_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '密码修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码输入不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
        return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    # 注销后重定向到home页面
    return redirect('/home/')

from django.db.models import Count
from django.db.models.functions import TruncMonth
def site(request,username,**kwargs):
    # 如果该参数kwargs有值，也就意味着要对article_list做额外的筛选操作(分类、标签或日期)

    # 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 如果站点不存在则返回404页面
    if not user_obj:
        return render(request,'errors.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有文章
    article_list = models.Article.objects.filter(blog = blog)
    if kwargs:
        # print(kwargs)
        # {'condition': 'tag', 'param': 'jQuery.js'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 然后判断用户到底想按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id = param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id =param)
        else:
            year,month = param.split('-') # 解压赋值
            article_list = article_list.filter(create_time__year = year, create_time__month = month)

    # 1、查询当前用户所有的分类及分类下的文章数
    category_list = models.Category.objects.filter(blog = blog).annotate(count_num = Count('article__pk')).values_list('name','count_num','pk')
    # print(category_list)
    # <QuerySet [('ding的文章分类1', 2), ('ding的文章分类2', 1)]>

    # 2、查询当前用户所有的标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog = blog).annotate(count_num = Count('article__pk')).values_list('name','count_num','pk')
    # print(tag_list)
    # <QuerySet [('ding的标签3', 0), ('ding的标签2', 1), ('ding的标签1', 2)]>

    # 3、按照年月统计所有的文章
    date_list = models.Article.objects.filter(blog = blog).annotate(month = TruncMonth('create_time')).values('month').annotate(count_num = Count('pk')).values_list('month','count_num','pk')
    # print(date_list)
    # < QuerySet[(datetime.date(2020, 8, 1), 2), (datetime.date(2020, 1, 1), 1)] >
    return render(request,'site.html',locals())

