# 定义URL路径与视图的映射关系
# 主要功能：
# 将URL路由到对应视图
# 支持URL参数捕获
# 支持URL命名和反向解析

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    
    # 统一密码管理路由
    path('password_reset/', views.unified_password_view, name='password_reset'),
    path('change_password/', views.unified_password_view, {'is_profile': True}, name='change_password'),
    
    # 协议相关路由
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    
    # 用户个人资料路由
    path('profile/', views.profile_view, name='user_profile'),
    
    # 修改手机号路由
    path('change_phone/', views.change_phone_view, name='change_phone'),
    
    # 仪表盘路由
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('provider_dashboard/', views.provider_dashboard, name='provider_dashboard'),
    
    # 验证码发送路由
    path('send_verification_code/', views.send_verification_code, name='send_verification_code'),
    
    # 用户功能路由
    path('user/orders/', views.user_orders, name='user_orders'),
    path('user/quick_booking/', views.quick_booking, name='quick_booking'),
    path('user/favorites/', views.favorites, name='favorites'),
    path('user/address_book/', views.address_book, name='address_book'),
    path('user/recommended_addresses/', views.recommended_addresses, name='recommended_addresses'),
    path('user/refund_request/', views.refund_request, name='refund_request'),
    path('user/rework_request/', views.rework_request, name='rework_request'),
    path('user/complaint/', views.complaint, name='complaint'),
    path('user/service_status/', views.service_status, name='service_status'),
    path('user/pending_reviews/', views.pending_reviews, name='pending_reviews'),
    path('user/review_history/', views.review_history, name='review_history'),
    path('user/featured_reviews/', views.featured_reviews, name='featured_reviews'),
    path('user/security_settings/', views.security_settings, name='security_settings'),
    path('user/provider_verification/', views.provider_verification, name='provider_verification'),

    # 安全设置API路由
    path('api/security/password_status/', views.password_status_api, name='password_status_api'),
    path('api/security/change_password/', views.change_password_api, name='change_password_api'),
    path('api/security/set_password/', views.set_password_api, name='set_password_api'), 
    path('api/security/send_phone_code/', views.send_phone_code_api, name='send_phone_code_api'),
    path('api/security/change_phone/', views.change_phone_api, name='change_phone_api'),
    path('api/security/submit_auth/', views.submit_auth_api, name='submit_auth_api'),
    path('api/security/delete_account/', views.delete_account_api, name='delete_account_api'),
]
