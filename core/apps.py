"""
Django应用配置
创建于: 2024-03-15
作者: zeki2000
功能: 配置家务服务系统核心应用
包含:
1. 应用名称配置
2. 自动字段类型配置
3. 应用初始化逻辑
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
