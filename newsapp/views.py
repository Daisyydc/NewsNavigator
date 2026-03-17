from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.core.paginator import Paginator # 导入 Django 的分页神器

# 你的 API KEY
API_KEY = "bc8b70ddabc547bf9ff2f1de46618a10"

def home(request):
    country_region = request.GET.get('country', 'us')
    search_query = request.GET.get('q')
    category = request.GET.get('category') # 新增：获取话题分类

    # 1. 构建智能 API 链接
    if search_query:
        url = f'https://newsapi.org/v2/everything?q={search_query}&apiKey={API_KEY}'
    elif country_region in ['cn', 'hk']:
        # 中港地区：继续用保底的 everything 全网搜索
        query_word = "China" if country_region == 'cn' else "Hong Kong"
        if category:
            query_word += f" {category}" # 如果点了分类，就把词叠加上去，比如 "Hong Kong Technology"
        url = f'https://newsapi.org/v2/everything?q={query_word}&apiKey={API_KEY}'
    else:
        # 其他地区：正常使用头条接口，NewsAPI 支持直接传 category
        url = f'https://newsapi.org/v2/top-headlines?country={country_region}&apiKey={API_KEY}'
        if category:
            url += f'&category={category}'

    # 2. 发起网络请求拿数据
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles', [])
        
        # 终极保底：如果还是空的，强制全网搜
        if not articles:
            fallback_word = category if category else "news"
            if country_region in ['cn', 'hk']:
                fallback_word = f"{'China' if country_region == 'cn' else 'Hong Kong'} {fallback_word}"
            url = f'https://newsapi.org/v2/everything?q={fallback_word}&apiKey={API_KEY}'
            articles = requests.get(url).json().get('articles', [])

    except Exception as e:
        print(f"Error: {e}")
        articles = []

    # 3. 核心功能：实现分页 (每页显示 9 篇文章)
    paginator = Paginator(articles, 9) # 告诉分页器，每 9 个分一页
    page_number = request.GET.get('page') # 获取用户点的是第几页
    page_obj = paginator.get_page(page_number) # 获取那一页的 9 篇文章

    # 4. 把数据打包送到前端
    context = {
        'page_obj': page_obj, # 注意：这里从 articles 变成了 page_obj
        'current_country': country_region,
        'current_category': category,
        'current_q': search_query or ''
    }
    return render(request, 'newsapp/home.html', context)