"""
Django后台管理配置
创建于: 2024-03-15
作者: zeki2000
功能: 配置家务服务系统的后台管理界面
包含:
1. 用户模型管理配置
2. 服务管理配置
3. 订单管理配置
4. 支付记录管理
5. 自定义管理界面优化
"""

# 配置Django admin后台界面
# 主要功能：
# 注册需要在后台管理的模型
# 自定义后台显示字段
# 配置搜索/过滤选项
# 添加自定义操作
# 示例配置：
# 注册User模型
# 自定义Order模型的显示方式

from django.contrib import admin

# Register your models here.
