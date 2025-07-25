from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os, zipfile, rarfile, tempfile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import pandas as pd
import os
from model.shop.models import Shop
from model.shop.models import Visit

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'shop_images')
os.makedirs(UPLOAD_DIR, exist_ok=True)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': '用户名、密码和邮箱均为必填项'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': '用户名已存在'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'error': '该邮箱已被注册'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    user.save()
    return Response({'status': '注册成功'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'status': 'success', 'token': token.key})
    else:
        return Response({'status': 'failed'}, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({'status': '登出成功'})
    except:
        return Response({'error': '登出失败'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_data(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'error': '未上传文件'}, status=400)

    filename = file.name.lower()
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return Response({'error': '仅支持CSV或Excel文件'}, status=400)

        column_mapping = {
            'name': 'name',
            'country': 'country',
            'city': 'city',
            'lat': 'lat',
            'lon': 'lon',
            'address': 'address',
            'phone': 'phone',
            'email': 'email',
            'image_path': 'image',
        }

        shops_to_create = []
        for _, row in df.iterrows():
            shop_data = {}

            for csv_col, model_field in column_mapping.items():
                if pd.notna(row.get(csv_col)):
                    shop_data[model_field] = row[csv_col]

            shop_data.setdefault('level', 'D')
            shop_data.setdefault('tags', '')
            shop_data.setdefault('visited', False)

            shops_to_create.append(Shop(**shop_data))

        Shop.objects.bulk_create(shops_to_create)
        return Response({'status': '导入成功', 'rows': len(shops_to_create)})

    except Exception as e:
        return Response({'error': f'导入失败: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_images(request):
    files = request.FILES.getlist('images')
    saved_files = []

    for f in files:
        fname = f.name
        ext = fname.lower().split('.')[-1]

        if ext in ['zip', 'rar']:
            # 保存临时压缩包
            tmp_path = os.path.join(tempfile.gettempdir(), fname)
            with open(tmp_path, 'wb') as tmpf:
                for chunk in f.chunks():
                    tmpf.write(chunk)

            # 处理 zip 压缩包
            if ext == 'zip':
                with zipfile.ZipFile(tmp_path, 'r') as zf:
                    for name in zf.namelist():
                        if name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                            data = zf.read(name)
                            save_name = os.path.join('shop_images', os.path.basename(name))
                            full_path = os.path.join(settings.MEDIA_ROOT, save_name)

                            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                            with open(full_path, 'wb') as imgf:
                                imgf.write(data)

                            saved_files.append(save_name)

            # 处理 rar 压缩包
            elif ext == 'rar':
                with rarfile.RarFile(tmp_path, 'r') as rf:
                    for name in rf.namelist():
                        if name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                            data = rf.read(name)
                            save_name = os.path.join('shop_images', os.path.basename(name))
                            full_path = os.path.join(settings.MEDIA_ROOT, save_name)

                            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                            with open(full_path, 'wb') as imgf:
                                imgf.write(data)
                            saved_files.append(save_name)

            os.remove(tmp_path)

        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            save_name = os.path.join('shop_images', fname)
            full_path = os.path.join(settings.MEDIA_ROOT, save_name)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as imgf:
                for chunk in f.chunks():
                    imgf.write(chunk)
            # print("Saved:", full_path)
            saved_files.append(save_name)

    return Response({'status': 'success', 'files': saved_files})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_user(request):
    total_users = User.objects.all().count()
    return Response({'total_users': total_users})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_visit(request):
    total_visits = Visit.objects.all().count()
    return Response({'total_visits': total_visits})
