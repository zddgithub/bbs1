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


def site(request, username, **kwargs):
    # 如果该参数kwargs有值，也就意味着要对article_list做额外的筛选操作(分类、标签或日期)

    # 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 如果站点不存在则返回404页面
    if not user_obj:
        return render(request, 'errors.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有文章
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs:
        # print(kwargs)
        # {'condition': 'tag', 'param': 'jQuery.js'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 然后判断用户到底想按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')  # 解压赋值
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    # 先获取文章对象(条件是用户名为当前用户名，文章id为主键值)
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    # 获取用户对象
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog  # 这是为了将个人站点的标题传到页面上
    if not article_obj:
        return render(request, 'errors.html')
    # 获取当前文章所有评论内容
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


import json
from django.db.models import F


def up_or_down(request):
    '''
    1、校验用户是否登录
    2、判断当前文章是否是当前用户写的，当前用户不能给自己的文章点赞点踩
    3、当前用户是否已经给当前文章点过了，不能重复点
    4、操作数据库
    '''
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 1、校验用户是否登录
        if request.user.is_authenticated():
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')  # 这里获取到的是一个字符串，不是布尔值
            is_up = json.loads(is_up)  # Json格式转成Python格式

            # 2、判断当前文章是否是当前用户写的，根据文章id查询文章作者，根据文章对象查文章作者，然后跟request.user校验
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 3、判断当前用户是否已经给当前文章点过了
                is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    # 4、如果没有点赞点踩，则操作数据库
                    # 这里要同步数据给Article表的三个字段，判断用户是点赞还是点踩，从而决定给哪个字段加1
                    if is_up:
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        # 点赞成功后反馈给前端
                        back_dic['msg'] = '点赞成功'
                    else:
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        # 点赞成功后反馈给前端
                        back_dic['msg'] = '点踩成功'
                    # 操作点赞点踩表
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    # 当前用户已经点过赞或点过踩了
                    back_dic['code'] = 1001
                    back_dic['msg'] = '您已经点过赞或点过踩了'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '不能给自己点赞或点踩'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '<a href="/login/">请先登录</a>'
        return JsonResponse(back_dic)


from django.db import transaction


def comment(request):
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                # 直接操作评论表，存储数据(以及文章表中的comment_num)
                # 事务
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                  parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登录'
            return JsonResponse(back_dic)


from utils.mypage import Pagination


# 登录用户才能进行后台管理
@login_required
def backend(request):
    # 获取当前用户的所有文章
    article_list = models.Article.objects.filter(blog=request.user.blog)
    current_page = request.GET.get("page", 1)
    all_count = article_list.count()
    # 1、传值生成对象
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=10)
    # 2、对总数据进行切片操作
    page_queryset = article_list[page_obj.start:page_obj.end]
    # 3、将page_queryset传递到前端页面
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup
@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')

        # bs4模块的使用
        soup = BeautifulSoup(content, 'html.parser')
        # 获取所有的标签
        tags = soup.find_all()
        for tag in tags:
            print(tag.name)  # 获取页面所有的标签
            # 将script标签找出来并直接删除
            if tag.name == 'script':
                tag.decompose()

        # 获取文章简介,截取150个文本
        # desc = content[0:150]  # 直接截取到的是HTML代码
        desc = soup.text[0:150]  # 通过soup.text截取
        article_obj = models.Article.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog
        )
        # 文章和标签的关系表是我们自己创建的，没法使用add\set\remove\clear方法
        # 需要自己去操作关系表，文章和标签是一对多的关系，所以添加一篇文章有时需要几条数据，所以这里用批量插入的方式
        article_obj_list = []
        for i in tag_id_list:
            article_obj1 = models.Article2Tag(article=article_obj, tag_id=i)
            article_obj_list.append(article_obj1)
        models.Article2Tag.objects.bulk_create(article_obj_list)
        # 跳转到后台管理文章展示页
        return redirect('/backend/')

    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request, 'backend/add_article.html', locals())

import os
from day72_BBS import settings
def upload_image(request):
    '''
    返回数据时有如下格式限制：
    //成功时
    {
        "error" : 0,
        "url" : "http://www.example.com/path/to/file.ext"
    }
    //失败时
    {
        "error" : 1,
        "message" : "错误信息"
    }
    '''
    back_dic = {'error': 0, }  # 先提前定义返回给编辑器的数据格式
    if request.method == 'POST':
        # 获取用户上传的图片对象
        file_obj = request.FILES.get('imgFile')
        # 手动拼接存储文件的路径
        file_dir = os.path.join(settings.BASE_DIR,'media','article_img')
        # print(file_dir)
        # /Users/dingding/PycharmProjects/day72_BBS/media/article_img

        # 判断文件夹是否存在
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        # 拼接图片的完整路径
        file_path = os.path.join(file_dir,file_obj.name)
        # print(file_path)
        # /Users/dingding/PycharmProjects/day72_BBS/media/article_img/WechatIMG249.jpeg
        with open(file_path,'wb') as f:
            for line in file_obj:
                f.write(line) # 将图片对象保存到图片文件中
        # 将url放到字典中
        back_dic['url'] = '/media/article_img/{}'.format(file_obj.name)
    return JsonResponse(back_dic)

@login_required
def set_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)   # 这种方式不会给图片自动加avatar/前缀，所以上传失败
        # 用如下方式：
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()

        # 改完头像，跳转到首页
        return redirect('/home/')
    blog = request.user.blog
    username = request.user.username
    return render(request,'set_avatar.html',locals())
