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
import time
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib import messages
from django.core.cache import cache
import random
from django.db import transaction
from .models import UserInfo
from docx import Document
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

#-----------------------------通用模块 登录注册注销退出-----------------------------#

## 首页视图
## 功能: 显示系统首页, 包含登录表单
def home(request):
    """系统首页视图"""
    login_form = AuthenticationForm()
    return render(request, 'registration/index.html', {
        'login_form': login_form,
    })

## 用户登录视图
## 功能: 处理用户登录请求, 支持 手机+验证码 或 手机+密码 登录（注册）
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
                # 生成随机有趣用户名
                adjectives = ['快乐的', '忧郁的', '活泼的', '安静的', '聪明的', '勇敢的']
                nouns = ['熊猫', '程序员', '旅行家', '美食家', '艺术家', '运动员'] 
                verbs = ['爱吃', '喜欢', '沉迷', '擅长', '收集', '研究']
                objects = ['螺蛳粉', '咖啡', '吉他', '代码', '摄影', '瑜伽']
                
                nickname = (
                    f"{random.choice(adjectives)}"
                    f"{random.choice(nouns)}"
                    f"{random.choice(verbs)}"
                    f"{random.choice(objects)}"
                )
                # 随机选择default_1到default_6的头像
                avatar_num = random.randint(1, 6)
                UserInfo.objects.create(
                    user=user,
                    nickname=nickname,
                    gender='未知',
                    avatar=f'image/avatars/default_{avatar_num}.png'
                )
                
            login(request, user)
            # 根据用户角色跳转不同界面
            if hasattr(user, 'role'):
                if user.role == 'B':
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

## 用户协议视图
## 功能: 显示用户协议内容
def terms_view(request):
    """用户协议视图"""
    doc_path = os.path.join(settings.BASE_DIR, 'core/static/docs/terms.docx')
    doc = Document(doc_path)
    content = '\n'.join([para.text for para in doc.paragraphs])
    return render(request, 'registration/terms.html', {'content': content})

## 隐私政策视图
## 功能: 显示隐私政策内容
def privacy_view(request):
    """隐私政策视图""" 
    doc_path = os.path.join(settings.BASE_DIR, 'core/static/docs/privacy.docx')
    doc = Document(doc_path)
    content = '\n'.join([para.text for para in doc.paragraphs])
    return render(request, 'registration/privacy.html', {'content': content})

## 手机验证码发送视图
## 功能: 发送手机验证码(开发模式模拟)
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


#-----------------------------用户模块 个人资料修改-----------------------------#
## 用户仪表盘视图
## 功能: 显示用户仪表盘, 包含用户信息和服务列表
def user_dashboard(request):
    """普通用户仪表盘视图"""
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_info = UserInfo.objects.get(user=request.user)
        # 确保user_info有role属性，如果没有则从user获取
        if not hasattr(user_info, 'role'):
            user_info.role = getattr(request.user, 'role', 'user')
        return render(request, 'user/common/dashboard.html', {
            'user': request.user,
            'user_info': user_info,
            'user_info_with_role': {
                'role': getattr(request.user, 'role', 'user'),
                **user_info.__dict__
            }
        })
    except UserInfo.DoesNotExist:
        # 如果UserInfo不存在，创建默认信息
        avatar_num = random.randint(1, 6)
        user_info = UserInfo.objects.create(
            user=request.user,
            nickname=f'用户{request.user.username[:4]}',
            gender='未知',
            avatar=f'image/avatars/default_{avatar_num}.png'
        )
        # 确保传递角色信息
        return render(request, 'user/common/dashboard.html', {
            'user': request.user,
            'user_info': user_info,
            'user_info_with_role': {
                'role': getattr(request.user, 'role', 'user'),
                **user_info.__dict__
            }
        })

def provider_dashboard(request):
    """服务提供者仪表盘视图"""
    if not request.user.is_authenticated:
        return redirect('login')
    if not hasattr(request.user, 'role') or request.user.role != 'provider':
        return redirect('user_dashboard')
    return render(request, 'provider\common\dashboard.html', {
        'user': request.user
    })

def unified_password_view(request, is_profile=False):
    """
    统一密码管理视图
    参数:
        is_profile: 是否来自个人资料页(True=修改密码, False=忘记密码)
    功能:
        1. 忘记密码: 通过手机验证码验证后重置
        2. 修改密码: 
           - 已设置密码: 验证原密码或手机验证码
           - 未设置密码: 直接设置新密码
    """
    User = get_user_model()
    
    if request.method == 'POST':
        # 获取表单数据
        phone = request.POST.get('phone')
        code = request.POST.get('verification_code', '')
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # 验证密码一致性
        if not new_password or len(new_password) < 8:
            messages.error(request, '密码长度不能少于8位')
            return redirect('password_reset')
            
        if new_password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return redirect('password_reset')
        
        # 处理不同场景
        if is_profile and request.user.is_authenticated:
            # 个人资料页修改密码
            user = request.user
            
            # 检查用户是否有密码
            if user.has_usable_password():
                # 验证原密码或验证码
                if not (user.check_password(current_password) or 
                       (code and cache.get(f'reset_code_{user.phone}') == code)):
                    messages.error(request, '原密码错误或验证码无效')
                    return redirect('user_profile')
            # 未设置密码则直接更新
        else:
            # 忘记密码流程
            cached_code = cache.get(f'reset_code_{phone}')
            if not cached_code or cached_code != code:
                messages.error(request, '验证码错误或已过期')
                return redirect('password_reset')
                
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                messages.error(request, '该手机号未注册')
                return redirect('password_reset')
        
        # 更新密码
        user.set_password(new_password)
        user.save()
        
        msg = '密码修改成功' if is_profile else '密码重置成功，请使用新密码登录'
        messages.success(request, msg)
        return redirect('user_profile' if is_profile else 'login')
    
    # GET请求处理
    context = {
        'is_profile': is_profile,
        'has_password': request.user.has_usable_password() if request.user.is_authenticated else False
    }
    template = 'user/change_password.html' if is_profile else 'registration/password_reset.html'
    return render(request, template, context)

def profile_view(request):
    """用户个人资料视图"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        user_info = UserInfo.objects.get(user=request.user)
    except UserInfo.DoesNotExist:
        # 如果UserInfo不存在，创建默认信息
        avatar_num = random.randint(1, 6)
        user_info = UserInfo.objects.create(
            user=request.user,
            nickname=f'用户{request.user.username[:4]}',
            gender='未知',
            avatar=f'image/avatars/default_{avatar_num}.png'
        )
    
    if request.method == 'POST':
        # 处理表单提交
        try:
            # 更新昵称
            if 'nickname' in request.POST:
                nickname = request.POST['nickname'].strip()
                if 2 <= len(nickname) <= 10:
                    user_info.nickname = nickname
            
            # 更新性别
            if 'gender' in request.POST:
                gender = request.POST['gender']
                if gender in ['M', 'F', 'O']:
                    user_info.gender = gender
            
            # 更新出生日期
            if 'birth_date' in request.POST:
                user_info.birth_date = request.POST['birth_date'] or None
            
            # 处理头像上传
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                # 验证文件类型和大小
                if avatar_file.content_type in ['image/jpeg', 'image/png'] and avatar_file.size <= 2*1024*1024:
                    # 保存到avatars目录
                    import os
                    from django.conf import settings
                    filename = f'avatar_{request.user.id}_{int(time.time())}.{avatar_file.name.split(".")[-1]}'
                    save_path = os.path.join(settings.MEDIA_ROOT, 'avatars', filename)
                    
                    with open(save_path, 'wb+') as destination:
                        for chunk in avatar_file.chunks():
                            destination.write(chunk)
                    
                    user_info.avatar = os.path.join('avatars', filename)
            
            user_info.save()
            messages.success(request, '个人信息更新成功')
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
        
        return redirect('user_profile')
    
    return render(request, 'user/account/profile.html', {
        'user': request.user,
        'user_info': user_info
    })

def change_phone_view(request):
    """修改手机号视图"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        new_phone = request.POST.get('new_phone')
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', new_phone):
            messages.error(request, '手机号格式不正确')
            return redirect('user_profile')
            
        # 更新手机号
        request.user.phone = new_phone
        request.user.save()
        messages.success(request, '手机号修改成功')
        return redirect('user_profile')
    
    return redirect('user_profile')

# 订单管理视图
def user_orders(request):
    """用户订单管理视图"""
    status = request.GET.get('status', 'active')
    return render(request, 'user/orders/orders.html', {
        'status': status,
        'orders': []  # 实际项目中这里应该查询数据库
    })

def quick_booking(request):
    """快速预约视图"""
    return render(request, 'user/quick_booking.html')

def favorites(request):
    """服务收藏夹视图"""
    return render(request, 'user/reviews/favorites.html')

def address_book(request):
    """地址簿视图"""
    return render(request, 'user/address/address_book.html')

def recommended_addresses(request):
    """推荐地址视图"""
    return render(request, 'user/recommended_addresses.html')

def refund_request(request):
    """退款申请视图"""
    return render(request, 'user/refund_request.html')

def rework_request(request):
    """返工申请视图"""
    return render(request, 'user/rework_request.html')

def complaint(request):
    """投诉建议视图"""
    return render(request, 'user/complaint.html')

def service_status(request):
    """服务进度查询视图"""
    return render(request, 'user/service_status.html')

def pending_reviews(request):
    """待评价订单视图"""
    return render(request, 'user/pending_reviews.html')

def review_history(request):
    """评价历史视图"""
    return render(request, 'user/review_history.html')

def featured_reviews(request):
    """精选评价视图"""
    return render(request, 'user/featured_reviews.html')

def security_settings(request):
    """安全设置视图"""
    return render(request, 'user/security_settings.html')

def provider_verification(request):
    """服务者认证视图"""
    return render(request, 'user/provider_verification.html')
