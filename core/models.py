"""
核心数据模型定义
创建于: 2024-03-15
作者: zeki2000
功能: 定义家务服务系统的所有数据模型
包含:
1. 用户相关模型(User, UserInfo, AddressBook, UserCertification)
2. 服务提供者模型(ServiceProviderInfo, Certification)
3. 服务项目模型(Service, ProviderService) 
4. 订单与支付模型(Order, Payment)
5. 售后与评价模型(AfterSales, Review)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinLengthValidator, MaxLengthValidator

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('C', '普通用户'),
        ('B', '服务提供者'), 
        ('ADMIN', '管理员')
    ]
    STATUS_CHOICES = [
        ('正常', '正常'),
        ('冻结', '冻结'),
        ('注销', '注销')
    ]

    # 覆盖默认字段
    username = None
    first_name = None
    last_name = None

    # 自定义字段
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[MinLengthValidator(11), MaxLengthValidator(11)],
        verbose_name='手机号'
    )
    role = models.CharField(
        max_length=5,
        choices=ROLE_CHOICES,
        default='C',
        verbose_name='角色'
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default='正常',
        verbose_name='状态'
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

    def __str__(self):
        return f'{self.phone}({self.get_role_display()})'


class UserInfo(models.Model):
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
        ('未知', '未知')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='info',
        verbose_name='用户'
    )
    nickname = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(2), MaxLengthValidator(10)],
        verbose_name='昵称'
    )
    gender = models.CharField(
        max_length=2,
        choices=GENDER_CHOICES,
        default='未知',
        verbose_name='性别'
    )
    birthday = models.DateField(
        null=True,
        blank=True,
        verbose_name='生日'
    )
    avatar = models.URLField(
        max_length=255,
        default='assets/img/avatars/default_1.png',
        verbose_name='头像URL'
    )

    def save(self, *args, **kwargs):
        if not self.avatar:
            import os
            import random
            avatar_dir = os.path.join('static', 'assets', 'img', 'avatars')
            default_avatars = [f for f in os.listdir(avatar_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if default_avatars:
                self.avatar = os.path.join('assets', 'img', 'avatars', random.choice(default_avatars))
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'user_info'
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息管理'

    def __str__(self):
        return self.nickname


class AddressBook(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='用户'
    )
    address = models.CharField(
        max_length=255,
        verbose_name='详细地址'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='默认地址'
    )

    class Meta:
        db_table = 'address_book'
        verbose_name = '地址簿'
        verbose_name_plural = '地址簿管理'

    def __str__(self):
        return f'{self.user.phone}-{self.address}'


class UserCertification(models.Model):
    STATUS_CHOICES = [
        ('待审核', '待审核'),
        ('通过', '通过'),
        ('驳回', '驳回')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='certification',
        verbose_name='用户'
    )
    real_name = models.CharField(
        max_length=50,
        verbose_name='真实姓名'
    )
    id_card = models.CharField(
        max_length=18,
        verbose_name='身份证号'
    )
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default='待审核',
        verbose_name='认证状态'
    )

    class Meta:
        db_table = 'user_certification'
        verbose_name = '用户实名认证'
        verbose_name_plural = '用户实名认证管理'

    def __str__(self):
        return f'{self.user.phone}-{self.real_name}'


class ServiceProviderInfo(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='provider_info',
        verbose_name='服务提供者'
    )
    service_area = models.CharField(
        max_length=100,
        verbose_name='服务范围'
    )
    introduction = models.CharField(
        max_length=100,
        verbose_name='个人简介'
    )

    class Meta:
        db_table = 'service_provider_info'
        verbose_name = '服务者信息'
        verbose_name_plural = '服务者信息管理'

    def __str__(self):
        return f'{self.user.phone}-服务者'


class Certification(models.Model):
    STATUS_CHOICES = [
        ('待审核', '待审核'),
        ('通过', '通过'),
        ('驳回', '驳回')
    ]

    provider = models.ForeignKey(
        ServiceProviderInfo,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name='服务提供者'
    )
    certificate_url = models.URLField(
        max_length=255,
        verbose_name='证书URL'
    )
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default='待审核',
        verbose_name='审核状态'
    )

    class Meta:
        db_table = 'certification'
        verbose_name = '资质证书'
        verbose_name_plural = '资质证书管理'

    def __str__(self):
        return f'{self.provider.user.phone}-证书'


class Service(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('保洁', '保洁'),
        ('维修', '维修')
    ]

    provider = models.ForeignKey(
        ServiceProviderInfo,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='服务提供者'
    )
    service_name = models.CharField(
        max_length=50,
        verbose_name='服务名称'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='服务价格'
    )
    service_type = models.CharField(
        max_length=2,
        choices=SERVICE_TYPE_CHOICES,
        verbose_name='服务类型'
    )

    class Meta:
        db_table = 'service'
        verbose_name = '服务项目'
        verbose_name_plural = '服务项目管理'

    def __str__(self):
        return f'{self.service_name}-{self.price}元'


class ProviderService(models.Model):
    provider = models.ForeignKey(
        ServiceProviderInfo,
        on_delete=models.CASCADE,
        verbose_name='服务提供者'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='服务项目'
    )

    class Meta:
        db_table = 'provider_service'
        verbose_name = '服务者-服务关联'
        verbose_name_plural = '服务者-服务关联管理'
        unique_together = ('provider', 'service')

    def __str__(self):
        return f'{self.provider.user.phone}-{self.service.service_name}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('待支付', '待支付'),
        ('已支付', '已支付'),
        ('已取消', '已取消'),
        ('已完成', '已完成')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='用户'
    )
    provider = models.ForeignKey(
        ServiceProviderInfo,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='服务提供者'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='服务项目'
    )
    address = models.ForeignKey(
        AddressBook,
        on_delete=models.CASCADE,
        verbose_name='服务地址'
    )
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default='待支付',
        verbose_name='订单状态'
    )
    start_time = models.DateTimeField(
        verbose_name='开始时间'
    )
    end_time = models.DateTimeField(
        verbose_name='结束时间'
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'order'
        verbose_name = '订单'
        verbose_name_plural = '订单管理'

    def __str__(self):
        return f'{self.user.phone}-{self.service.service_name}'


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('微信', '微信'),
        ('支付宝', '支付宝')
    ]
    STATUS_CHOICES = [
        ('成功', '成功'),
        ('失败', '失败')
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='订单'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='支付金额'
    )
    payment_method = models.CharField(
        max_length=3,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='支付方式'
    )
    channel_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='渠道手续费'
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        verbose_name='支付状态'
    )

    class Meta:
        db_table = 'payment'
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录管理'

    def __str__(self):
        return f'{self.order.id}-{self.amount}元'


class AfterSales(models.Model):
    TYPE_CHOICES = [
        ('退款', '退款'),
        ('返工', '返工'),
        ('投诉', '投诉')
    ]
    STATUS_CHOICES = [
        ('待处理', '待处理'),
        ('已解决', '已解决'),
        ('驳回', '驳回')
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='after_sales',
        verbose_name='订单'
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        verbose_name='售后类型'
    )
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default='待处理',
        verbose_name='处理状态'
    )

    class Meta:
        db_table = 'after_sales'
        verbose_name = '售后工单'
        verbose_name_plural = '售后工单管理'

    def __str__(self):
        return f'{self.order.id}-{self.get_type_display()}'


class Review(models.Model):
    STATUS_CHOICES = [
        ('待审核', '待审核'),
        ('通过', '通过'),
        ('驳回', '驳回')
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='订单'
    )
    content = models.TextField(
        verbose_name='评价内容'
    )
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default='待审核',
        verbose_name='审核状态'
    )

    class Meta:
        db_table = 'review'
        verbose_name = '评价'
        verbose_name_plural = '评价管理'

    def __str__(self):
        return f'{self.order.id}-评价'
