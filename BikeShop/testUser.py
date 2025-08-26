import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BikeShop.settings')  # 修改为你项目的settings路径
django.setup()

from django.contrib.auth.models import User

# 创建新用户
user = User.objects.create_user(username='shuiys', password='123456')
user.save()

# print(f"Created user: {user.username}")
