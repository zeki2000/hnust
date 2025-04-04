"""
核心视图定义
创建于: 2024-03-15
作者: zeki2000
功能: 定义家务服务系统的所有视图逻辑
包含:
1. 用户认证相关视图(登录、注册、注销)
2. 服务管理视图(服务列表、详情、下单)
3. 订单管理视图(订单列表、详情、状态变更)
4. 支付处理视图
5. 售后处理视图
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
import re
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib import messages
from django.core.cache import cache
import random

def home(request):
    """系统首页视图"""
    login_form = AuthenticationForm()
    register_form = UserCreationForm()
    return render(request, 'registration/index.html', {
        'login_form': login_form,
        'register_form': register_form
    })

def login_view(request):
    """用户登录视图(支持手机验证码登录)"""
    if request.method == 'POST':
        # 手机验证码登录
        if 'phone' in request.POST:
            phone = request.POST.get('phone')
            code = request.POST.get('verification_code')
            cached_code = cache.get(f'login_code_{phone}')
            
            if not cached_code:
                messages.error(request, '请先获取验证码')
                return redirect('login')
                
            if cached_code != code:
                messages.error(request, '验证码错误')
                return render(request, 'registration/index.html', {
                    'login_form': AuthenticationForm(),
                    'register_form': UserCreationForm(),
                    'phone': phone,
                    'verification_error': True
                })
            
            User = get_user_model()
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                # 自动创建新用户
                user = User.objects.create_user(phone=phone)
                user.set_unusable_password()
                user.save()
                
                # 创建用户信息
                from django.utils import timezone
                nickname = f'用户{phone[-4:]}'
                # 随机选择default_1到default_6的头像
                avatar_num = random.randint(1, 6)
                UserInfo.objects.create(
                    user=user,
                    nickname=nickname,
                    gender='未知',
                    avatar=f'avatars/default_{avatar_num}.png'
                )
                
            login(request, user)
            # 根据用户角色跳转不同界面
            if hasattr(user, 'role'):
                if user.role == 'provider':
                    return redirect('provider_dashboard')  # 服务提供者界面
                return redirect('user_dashboard')  # 普通用户界面
            return redirect('home')  # 默认跳转
        
        # 传统用户名密码登录
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # 根据用户角色跳转不同界面
                if hasattr(user, 'role'):
                    if user.role == 'provider':
                        return redirect('provider_dashboard')
                    return redirect('user_dashboard')
                return redirect('home')
        messages.error(request, '用户名或密码错误')
    return redirect('home')

from django.db import transaction
from .models import UserInfo

def register_view(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    
                    # 创建用户信息记录
                    nickname = f'用户{user.username[:4]}'
                    avatar_num = random.randint(1, 6)
                    UserInfo.objects.create(
                        user=user,
                        nickname=nickname,
                        gender='未知',
                        avatar=f'assets/img/avatars/default_{avatar_num}.png'
                    )
                    
                    login(request, user)
                    messages.success(request, '注册成功!')
                    return redirect('home')
            except Exception as e:
                messages.error(request, f'注册失败: {str(e)}')
            
            login(request, user)
            messages.success(request, '注册成功!')
            return redirect('home')
        messages.error(request, '注册信息无效')
    return redirect('home')

from docx import Document
import os
from django.conf import settings

def terms_view(request):
    """用户协议视图"""
    doc_path = os.path.join(settings.BASE_DIR, 'core/static/docs/terms.docx')
    doc = Document(doc_path)
    content = '\n'.join([para.text for para in doc.paragraphs])
    return render(request, 'registration/terms.html', {'content': content})

def privacy_view(request):
    """隐私政策视图""" 
    doc_path = os.path.join(settings.BASE_DIR, 'core/static/docs/privacy.docx')
    doc = Document(doc_path)
    content = '\n'.join([para.text for para in doc.paragraphs])
    return render(request, 'registration/privacy.html', {'content': content})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def send_verification_code(request):
    """发送手机验证码(开发模式模拟)"""
    if request.method == 'POST':
        # 验证内容类型
        if request.content_type != 'application/json':
            return JsonResponse(
                {'status': 'error', 'message': 'Content-Type必须是application/json'},
                status=400,
                content_type='application/json'
            )
            
        try:
            import json
            data = json.loads(request.body)
            phone = data.get('phone')
            
            if not phone or not re.match(r'^1[3-9]\d{9}$', phone):
                return JsonResponse(
                    {'status': 'error', 'message': '手机号无效'},
                    status=400,
                    content_type='application/json'
                )
            
            # 生成6位随机验证码
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            # 存储验证码到缓存，有效期5分钟
            cache.set(f'login_code_{phone}', code, 300)
            
            return JsonResponse({
                'status': 'success',
                'message': '验证码已发送(开发模式)',
                'code': code,  # 开发模式下返回验证码
                'countdown': 60  # 60秒倒计时
            })
            
        except json.JSONDecodeError:
            return JsonResponse(
                {'status': 'error', 'message': '无效的请求数据'},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=500
            )
    
    return JsonResponse(
        {'status': 'error', 'message': '仅支持POST请求'},
        status=405
    )

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import UserInfo

def user_dashboard(request):
    """普通用户仪表盘视图"""
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_info = UserInfo.objects.get(user=request.user)
        return render(request, 'user/dashboard.html', {
            'user': request.user,
            'user_info': user_info
        })
    except UserInfo.DoesNotExist:
        # 如果UserInfo不存在，创建默认信息
        avatar_num = random.randint(1, 6)
        user_info = UserInfo.objects.create(
            user=request.user,
            nickname=f'用户{request.user.username[:4]}',
            gender='未知',
            avatar=f'assets/img/avatars/default_{avatar_num}.png'
        )
        return render(request, 'user/dashboard.html', {
            'user': request.user,
            'user_info': user_info
        })

def provider_dashboard(request):
    """服务提供者仪表盘视图"""
    if not request.user.is_authenticated:
        return redirect('login')
    if not hasattr(request.user, 'role') or request.user.role != 'provider':
        return redirect('user_dashboard')
    return render(request, 'provider/dashboard.html', {
        'user': request.user
    })

def password_reset_view(request):
    """手机验证码重置密码视图"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('verification_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        cached_code = cache.get(f'reset_code_{phone}')
        
        # 验证验证码
        if not cached_code or cached_code != code:
            messages.error(request, '验证码错误或已过期')
            return redirect('password_reset')
            
        # 验证密码
        if not new_password or len(new_password) < 8:
            messages.error(request, '密码长度不能少于8位')
            return redirect('password_reset')
            
        if new_password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return redirect('password_reset')
            
        # 更新用户密码
        User = get_user_model()
        try:
            user = User.objects.get(phone=phone)
            user.password = make_password(new_password)
            user.save()
            messages.success(request, '密码重置成功，请使用新密码登录')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, '该手机号未注册')
            return redirect('password_reset')
        
    return render(request, 'registration/password_reset.html')
