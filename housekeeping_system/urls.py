# 定义URL路径与视图函数的映射关系
# 主要功能：
# 将特定URL路由到对应的视图处理函数
# 支持URL参数捕获和传递
# 可以包含其他应用的URL配置(include)
# 支持URL命名和反向解析
# 是Django处理HTTP请求的入口点
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views as core_views


urlpatterns = [
    # Django后台管理界面--管理数据库内容
    path('admin/', admin.site.urls),
    
    # 核心应用的路由配置(包含在core/urls.py中)
    path('', include('core.urls')),
    
    # 用户登录注册页面
    path('accounts/login/', core_views.login_view, name='login'),
    
    # 用户登出功能
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 发送验证码接口
    path('accounts/send_verification_code/', core_views.send_verification_code, name='send_verification_code'),
    
    # 普通用户仪表盘
    path('user/dashboard/', core_views.user_dashboard, name='user_dashboard'),
    
    # 服务提供商仪表盘
    path('provider/dashboard/', core_views.provider_dashboard, name='provider_dashboard'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
