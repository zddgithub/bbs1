from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth
register = template.Library()

# 自定义inclusion.tag
@register.inclusion_tag('left_menu.html')
def left_menu(username):
    # 构造侧边栏需要的数据
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog

    # 1、查询当前用户所有的分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')
    # print(category_list)
    # <QuerySet [('ding的文章分类1', 2), ('ding的文章分类2', 1)]>

    # 2、查询当前用户所有的标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name',
                                                                                                         'count_num',
                                                                                                         'pk')
    # print(tag_list)
    # <QuerySet [('ding的标签3', 0), ('ding的标签2', 1), ('ding的标签1', 2)]>

    # 3、按照年月统计所有的文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_num=Count('pk')).values_list('month', 'count_num', 'pk')
    # print(date_list)
    # < QuerySet[(datetime.date(2020, 8, 1), 2), (datetime.date(2020, 1, 1), 1)] >
    return locals()


