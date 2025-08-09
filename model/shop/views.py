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
from rest_framework import status


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
    tag = request.GET.get('tag', '').strip()

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
    
    # 按标签筛选
    if tag:
        # 通过ShopTag关联筛选
        tag_shops = models.ShopTag.objects.filter(tag_id__name=tag).values_list('shop_id', flat=True)
        # 同时兼容旧的tags字段
        qs = qs.filter(Q(id__in=tag_shops) | Q(tags__icontains=tag))

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    qs = qs[start:end]

    # 处理数据，确保标签正确显示
    data = []
    for obj in qs:
        shop_data = ShopSerializer(obj).data
        
        # 获取商店关联的标签 - 修正字段名称问题
        shop_tags = models.ShopTag.objects.filter(shop_id=obj).select_related('tag_id')
        
        # # 调试输出
        # print(f"data_list: 商店 {obj.name} 找到 {len(shop_tags)} 个ShopTag记录")
        # for st in shop_tags:
        #     print(f"data_list: ShopTag记录: shop_id={st.shop_id.id}, tag_name={st.tag_id.name}")
        
        tag_names = [st.tag_id.name for st in shop_tags]
        
        # 如果没有通过ShopTag找到标签，尝试使用Shop的tags字段（兼容旧数据）
        if not tag_names and obj.tags:
            # 如果shop.tags字段有值，使用它作为备用
            tag_names = [tag.strip() for tag in obj.tags.split(',') if tag.strip()]
        
        # 将标签数据添加到序列化后的商店数据中
        # 确保返回的是逗号分隔的字符串，这样前端可以正确处理
        shop_data['tags'] = ','.join(tag_names) if tag_names else ''
        
        data.append(shop_data)

    columns = ['id', 'name', 'country', 'city', 'lat', 'lon', 'address', 'phone', 'email', 'level', 'tags', 'image',
               'visited', 'website']

    # 新增：返回所有国家和城市的去重列表
    all_countries = sorted(list(models.Shop.objects.values_list('country', flat=True).distinct()))
    all_cities = sorted(list(models.Shop.objects.values_list('city', flat=True).distinct()))
    # print(data)
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
    tags = request.data.get('tags', [])
    
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
    
    # 处理标签关联
    if tags and isinstance(tags, list):
        # 清除现有的标签关联
        models.ShopTag.objects.filter(shop_id=shop).delete()
        
        # 添加新的标签关联
        for tag_id in tags:
            try:
                tag = models.Tag.objects.get(id=tag_id)
                models.ShopTag.objects.create(shop_id=shop, tag_id=tag)
            except models.Tag.DoesNotExist:
                continue
    
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
    qs = models.Visit.objects.filter(user=user).select_related('shop').order_by('-visit_time')  # 按时间倒序
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    # 获取分页后的拜访记录
    visits_page = qs[start:end]
    
    # 构建包含标签的结果列表
    result = []
    for visit in visits_page:
        # 获取商店关联的标签 - 修正字段名称问题
        shop_tags = models.ShopTag.objects.filter(shop_id=visit.shop).select_related('tag_id')
        
        # 调试输出
        # print(f"visit_shop_list: 商店 {visit.shop.name} 找到 {len(shop_tags)} 个ShopTag记录")
        # for st in shop_tags:
        #     print(f"visit_shop_list: ShopTag记录: shop_id={st.shop_id.id}, tag_name={st.tag_id.name}")
        #
        tag_names = [st.tag_id.name for st in shop_tags]
        
        # 如果没有通过ShopTag找到标签，尝试使用Shop的tags字段（兼容旧数据）
        if not tag_names and visit.shop.tags:
            # 如果shop.tags字段有值，使用它作为备用
            tag_names = [tag.strip() for tag in visit.shop.tags.split(',') if tag.strip()]
        
        # print(f"商店 {visit.shop.name} 的标签: {tag_names}")
        # # 打印更多调试信息
        # print(f"标签数量: {len(tag_names)}")
        # print(f"标签字符串: '{','.join(tag_names) if tag_names else ''}'")
        
        visit_data = {
            'id': visit.id,
            'visit_time': visit.visit_time,
            'notes': visit.notes,
            'shop__name': visit.shop.name,
            'tags': ','.join(tag_names) if tag_names else ''  # 确保返回的是逗号分隔的字符串，这样前端可以正确处理
        }

        result.append(visit_data)
    print(result)
    return Response({
        'data': result,
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
    
    # 使用序列化器获取基本数据
    serialized_data = ShopSerializer(shops, many=True).data
    
    # 处理每个商店的标签数据
    for i, shop in enumerate(shops):
        # 获取商店关联的标签 - 修正字段名称问题
        # 在Django ORM中，外键字段名应该是shop_id和tag_id
        shop_tags = models.ShopTag.objects.filter(shop_id=shop).select_related('tag_id')
        
        # # 调试输出
        # print(f"找到 {len(shop_tags)} 个ShopTag记录")
        # for st in shop_tags:
        #     print(f"ShopTag记录: shop_id={st.shop_id.id}, tag_name={st.tag_id.name}")
        
        # 获取标签名称列表
        tag_names = [st.tag_id.name for st in shop_tags]
        
        # 如果没有通过ShopTag找到标签，尝试使用Shop的tags字段（兼容旧数据）
        if not tag_names and shop.tags:
            # 如果shop.tags字段有值，使用它作为备用
            tag_names = [tag.strip() for tag in shop.tags.split(',') if tag.strip()]
        
        # 更新标签字段 - 确保返回的是逗号分隔的字符串，这样前端可以正确处理
        serialized_data[i]['tags'] = ','.join(tag_names) if tag_names else ''
        
        # 调试输出
        # print(f"商店 {shop.name} 的标签: {tag_names}")
        # print(f"标签字符串: '{serialized_data[i]['tags']}'")
    
    return Response(serialized_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_recent_activities(request):
    from django.db.models import Q
    from django.contrib.admin.models import LogEntry, ADDITION
    from django.contrib.contenttypes.models import ContentType
    import os
    from django.conf import settings
    
    user = request.user
    limit = int(request.GET.get('limit', 5))  # 默认获取5条记录
    
    # 获取用户最近的拜访记录
    recent_visits = models.Visit.objects.filter(user=user).select_related('shop').order_by('-visit_time')[:limit]
    
    # 构建活动记录列表
    activities = []
    
    # 处理拜访记录
    for visit in recent_visits:
        activity = {
            'type': 'visit',
            'title': f'拜访了商店 {visit.shop.name}',
            'time': visit.visit_time,
            'shop_id': visit.shop.id
        }
        activities.append(activity)
    
    # 按时间排序
    activities.sort(key=lambda x: x['time'], reverse=True)
    
    # 限制返回数量
    activities = activities[:limit]
    
    # 返回活动记录
    return Response(activities)


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
    
    # 处理标签关联
    if 'tags' in request.data:
        tags_data = request.data.get('tags')
        # 如果是逗号分隔的字符串，拆分为列表
        if isinstance(tags_data, str):
            tag_names = [name.strip() for name in tags_data.split(',') if name.strip()]
            # 调试输出
            # print(f"更新商店 {shop.name} 的标签: {tag_names}")
            # 清除现有的标签关联
            models.ShopTag.objects.filter(shop_id=shop).delete()
            
            # 为每个标签名创建或获取标签，并建立关联
            for tag_name in tag_names:
                tag, _ = models.Tag.objects.get_or_create(name=tag_name)
                shop_tag = models.ShopTag.objects.create(shop_id=shop, tag_id=tag)
                # print(f"创建标签关联: shop_id={shop.id}, tag_id={tag.id}, tag_name={tag.name}")
            # 更新Shop模型的tags字段，保持兼容性
            shop.tags = ','.join(tag_names)
            shop.save(update_fields=['tags'])
    
    # 更新其他字段
    for field in ['name', 'country', 'city', 'lat', 'lon', 'address', 'phone', 'email', 'level']:
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tag_list(request):
    tags = models.Tag.objects.values('id', 'name')  # 返回结构化数据
    # print(tags)
    return Response({'tags': list(tags)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tag_add(request):
    name = request.data.get('name')
    try:
        tag, created = models.Tag.objects.get_or_create(name=name)
        return Response({'status': 'success', 'tag': {'id': tag.id, 'name': tag.name}})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def shop_create(request):
    # print("接收到的数据:", request.data)
    name = request.data.get('name')
    country = request.data.get('country')
    city = request.data.get('city')
    lat = request.data.get('lat')
    lon = request.data.get('lon')
    address = request.data.get('address')
    phone = request.data.get('phone')
    email = request.data.get('email')
    level = request.data.get('level')
    visited = bool(request.data.get('visited'))
    tags = request.data.get('tags')

    try:
        shop = models.Shop.objects.create(
            name=name,
            country=country,
            city=city,
            lat=lat,
            lon=lon,
            address=address,
            phone=phone,
            email=email,
            level=level,
            visited=visited
            )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if tags:
        for tag_id in tags:
            try:
                tag = models.Tag.objects.get(id=tag_id)
                models.ShopTag.objects.create(shop_id=shop, tag_id=tag)
            except models.Tag.DoesNotExist:
                continue

    if visited:
        models.Visit.objects.create(user=request.user, shop=shop)
        return Response({'success': True, 'shop_id': shop.id}, status=status.HTTP_201_CREATED)

    return Response({'success': True, 'shop_id': shop.id}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_shop(request):
    shop_id = request.data.get('shop_id')
    if not shop_id:
        return Response({'error': '缺少shop_id'}, status=400)
    
    try:
        shop = models.Shop.objects.get(id=shop_id)
    except models.Shop.DoesNotExist:
        return Response({'error': '商店不存在'}, status=404)
    
    # 删除图片文件
    if shop.image:
        image_path = shop.image.path
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                # 记录错误但不中断流程
                print(f"删除图片文件失败: {str(e)}")
    
    # 删除与该商店相关的所有拜访记录
    models.Visit.objects.filter(shop=shop).delete()
    
    # 删除与该商店相关的所有标签关联
    models.ShopTag.objects.filter(shop_id=shop).delete()
    
    # 删除商店
    shop.delete()
    
    return Response({'status': 'success'})