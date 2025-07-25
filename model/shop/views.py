from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from model.shop import models
from api.serializers import ShopSerializer, VisitSerializer
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
import os
from django.conf import settings

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data_list(request):
    search = request.GET.get('search', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    country = request.GET.get('country', '').strip()
    city = request.GET.get('city', '').strip()
    level = request.GET.get('level', '').strip()
    visited = request.GET.get('visited', '').strip()

    qs = models.Shop.objects.all()
    if search:
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(country__icontains=search) |
            Q(city__icontains=search) |
            Q(address__icontains=search) |
            Q(tags__icontains=search)
        )
    if country:
        qs = qs.filter(country=country)
    if city:
        qs = qs.filter(city=city)
    if level:
        qs = qs.filter(level=level)
    if visited != '':
        if visited == '1' or visited.lower() == 'true':
            qs = qs.filter(visited=True)
        elif visited == '0' or visited.lower() == 'false':
            qs = qs.filter(visited=False)

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    qs = qs[start:end]

    data = [ShopSerializer(obj).data for obj in qs]

    columns = ['id', 'name', 'country', 'city', 'lat', 'lon', 'address', 'phone', 'email', 'level', 'tags', 'image',
               'visited']

    # 新增：返回所有国家和城市的去重列表
    all_countries = sorted(list(models.Shop.objects.values_list('country', flat=True).distinct()))
    all_cities = sorted(list(models.Shop.objects.values_list('city', flat=True).distinct()))

    return Response({
        'data': data,
        'columns': columns,
        'total': total,
        'page': page,
        'page_size': page_size,
        'all_countries': all_countries,
        'all_cities': all_cities
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_visit(request):
    user = request.user
    shop_id = request.data.get('shop_id')
    image = request.data.get('image')
    notes = request.data.get('notes', '')
    if not shop_id:
        return Response({'error': '缺少shop_id'}, status=400)
    try:
        shop = models.Shop.objects.get(id=shop_id)
    except models.Shop.DoesNotExist:
        return Response({'error': '商店不存在'}, status=404)
    # 更新商店图片（如有新图片名）
    if image:
        shop.image = f'shop_images/{image}'
    # 标记商店为已拜访
    shop.visited = True
    shop.save()
    # 创建或更新拜访记录
    visit, created = models.Visit.objects.get_or_create(user=user, shop=shop, defaults={'notes': notes})
    if not created:
        visit.notes = notes
        visit.visit_time = timezone.now()
        visit.save()
    return Response({'status': 'success', 'visit': VisitSerializer(visit).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_visit(request):
    visit_id = request.data.get('visit_id')
    if not visit_id:
        return Response({'error': '缺少visit_id'}, status=400)
    try:
        visit = models.Visit.objects.get(id=visit_id)
    except models.Visit.DoesNotExist:
        return Response({'error': '拜访记录不存在'}, status=404)
    shop = visit.shop
    visit.delete()
    # 删除后将商店visited设为0
    shop.visited = False
    shop.save()
    return Response({'status': 'success'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visit_shop_list(request):
    user = request.user
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    qs = models.Visit.objects.filter(user=user).select_related('shop').order_by('id')
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    visits = qs[start:end].values('id', 'visit_time', 'notes', 'shop__name')
    return Response({
        'data': list(visits),
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_visited_shops(request):
    user = request.user
    shop_ids = models.Visit.objects.filter(user=user).values_list('shop_id', flat=True).distinct()
    shops = models.Shop.objects.filter(id__in=shop_ids)
    serializer = ShopSerializer(shops, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_shop(request):
    shop_id = request.data.get('shop_id')
    if not shop_id:
        return Response({'error': '缺少shop_id'}, status=400)
    try:
        shop = models.Shop.objects.get(id=shop_id)
    except models.Shop.DoesNotExist:
        return Response({'error': '商店不存在'}, status=404)
    for field in ['name', 'country', 'city', 'lat', 'lon', 'address', 'phone', 'email', 'level', 'tags']:
        if field in request.data:
            setattr(shop, field, request.data[field])
    # 处理图片上传并覆盖原图片
    if 'image' in request.FILES:
        uploaded_file = request.FILES['image']
        old_image_name = os.path.basename(shop.image.name) if shop.image else None
        if old_image_name:
            old_image_path = os.path.join(settings.MEDIA_ROOT, 'shop_images', old_image_name)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
            uploaded_file.name = old_image_name
        shop.image = uploaded_file
    shop.save()
    return Response({'status': 'success'})
