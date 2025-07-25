from django.contrib import admin
from django.urls import path, include
from server.user import user_views
from server import views
from django.conf import settings
from django.conf.urls.static import static
from model.shop import views as shop_views

urlpatterns = [
    path('api/login', views.login),
    path('api/register', views.register),
    path('api/all-user', views.all_user),
    path('api/all-visit', views.all_visit),
    path('api/logout', views.logout),
    path('api/import-excel', views.import_data),
    path('api/import-images', views.import_images),
    path('api/user-data', user_views.user_data),
    path('api/visit-list', user_views.visit_list),
    path('api/data-list', shop_views.data_list),
    path('api/add-visit', shop_views.add_visit),
    path('api/visit-shop-list', shop_views.visit_shop_list),
    path('api/delete-visit', shop_views.delete_visit),
    path('api/user-visited-shops', shop_views.user_visited_shops),
    path('api/update-shop', shop_views.update_shop),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
