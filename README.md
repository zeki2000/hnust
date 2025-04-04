# 家务服务预约系统

## 项目概述
基于Django的家务服务预约平台，提供用户注册、服务预约、订单管理等功能。

## 技术栈
- Python 3.12.9
- Django 4.0.8
- MySQL 8.0.41
- Bootstrap 5
- Git 2.48.1

## 数据库设计
包含6大模块：
1. 用户与登录模块
2. 普通用户(C端)模块
3. 家政服务提供者(B端)模块
4. 订单与支付模块
5. 售后服务与评价模块

## 安装指南
1. 克隆仓库
```bash
git clone git@github.com:zeki2000/hnust.git
cd hnust
```

2. 创建虚拟环境
```bash
python -m venv venv
venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据库
- 创建MySQL数据库
- 修改settings.py中的DATABASES配置

5. 运行迁移
```bash
python manage.py migrate
```

6. 启动开发服务器
```bash
python manage.py runserver
```

## 项目结构
```
housekeeping_system/
├── core/            # 核心应用(包含模型、视图、路由等核心业务逻辑)
│   ├── models.py    # 数据模型定义
│   ├── views.py     # 视图函数/类
│   ├── admin.py     # 后台管理配置
│   ├── apps.py      # 应用配置
│   └── migrations/  # 数据库迁移文件
├── housekeeping_system/  # 项目配置
├── media/           # 媒体文件
├── static/          # 静态文件
└── templates/       # 模板文件
```

## 贡献指南
1. Fork项目
2. 创建特性分支
3. 提交Pull Request
