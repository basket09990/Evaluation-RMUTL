from django.urls import path
from . import views
from django.contrib import admin
from app_user.admin import custom_admin_site
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about , name='about'),
    path('search', views.search_user , name='search'),
    path('admin/', custom_admin_site.urls, name='management_admin'),
    path('user_edit/<int:user_id>/', views.edit_user, name='user_edit'),
    path('ajax_search_user/', views.ajax_search_user, name='ajax_search_user'),
    #path('ajax_search_evaluation/', views.ajax_search_evaluation, name='ajax_search_evaluation'),
    path('ajax_change_user_group/', views.ajax_change_user_group, name='ajax_change_user_group'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)