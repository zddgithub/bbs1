from django.db import models

# Create your models here.
# 创建表：先写普通字段，再写外键字段

from django.contrib.auth.models import AbstractUser

class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='手机号',null=True,blank=True)
    # null=True 表示数据库中该字段可以为空
    # blank=True 表示admin后台管理该字段可以为空

    # 头像
    # 给avatar字段传文件对象，该文件会自动存储到avatar文件夹下，设置一个默认头像
    avatar = models.FileField(upload_to='avatar/',default='avatar/default.jpg',verbose_name='用户头像')
    create_time = models.DateField(auto_now_add = True)
    # 一对一关系
    blog = models.OneToOneField(to='Blog',null=True)

    class Meta:
        # verbose_name = '用户表' # admin后台管理默认显示的表名后面会加s
        verbose_name_plural  = '用户表'  # 修改admin后台管理默认显示的表名
    def __str__(self):
        return self.username

class Blog(models.Model):
    site_name = models.CharField(max_length=32,verbose_name='站点名称')
    site_title = models.CharField(max_length=32,verbose_name='站点标题')
    # site_theme站点样式中存储css/js的文件路径
    site_theme = models.CharField(max_length=64,verbose_name='站点样式')
    def __str__(self):
        return self.site_name

class Category(models.Model):
    name = models.CharField(max_length=32,verbose_name='文章分类')
    # 外键字段
    blog = models.ForeignKey(to='Blog',null=True)
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=32,verbose_name='文章标签')
    blog = models.ForeignKey(to='Blog',null=True)
    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=64,verbose_name='文章标题')
    desc = models.CharField(max_length=255,verbose_name='文章简介')
    # 文章内容一般用TextField
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True)

    # 数据库字段优化设计
    up_num = models.BigIntegerField(default=0,verbose_name='点赞数')
    down_num = models.BigIntegerField(default=0,verbose_name='点踩数')
    comment_num = models.BigIntegerField(default=0,verbose_name='评论数')

    # 外键字段
    blog = models.ForeignKey(to='Blog', null=True)
    category = models.ForeignKey(to='Category', null=True)
    tags = models.ManyToManyField(to='Tag',
                                  through='Article2Tag',
                                  through_fields=('article','tag'))
    def __str__(self):
        return self.title

class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')

class UpAndDown(models.Model):
    user = models.ForeignKey(to = 'UserInfo')
    article = models.ForeignKey(to = 'Article')
    is_up = models.BooleanField(verbose_name='是否点赞')

class Comment(models.Model):
    user = models.ForeignKey(to = 'UserInfo')
    article = models.ForeignKey(to = 'Article')
    content = models.CharField(max_length=255,verbose_name='评论内容')
    comment_time = models.DateTimeField(verbose_name='评论时间',auto_now_add=True)
    # 自关联
    parent = models.ForeignKey(to='self',null=True)













