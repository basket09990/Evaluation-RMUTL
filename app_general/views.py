from django.shortcuts import render ,get_object_or_404, redirect
from django.http.response import HttpResponse
from rest_framework import generics,status,filters ,mixins
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from .forms import UserSearchForm ,EditUserGroupsForm ,UserGroupEditForm ,SearchForm
from django.contrib.auth.models import User , Group
from django.http import JsonResponse
from django import forms
from app_user.forms import UserProfileForm,ExtendedProfileForm
from app_user.models import Profile,academic_type
from django.contrib import messages 
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator




# Create your views here.



@login_required
def home(request):
    # ตรวจสอบว่ามีข้อมูล academic_type อยู่หรือไม่ ถ้าไม่มีให้เพิ่มเข้าไป
    if not academic_type.objects.exists():
        academic_type.objects.bulk_create([
            academic_type(ac_name="เจ้าหน้าที่"),
            academic_type(ac_name="อาจารย์"),
            academic_type(ac_name="ผู้ช่วยศาสตราจารย์"),
            academic_type(ac_name="รองศาสตราจารย์"),
            academic_type(ac_name="ศาสตราจารย์"),
        ])
    
    # ตรวจสอบว่ามีข้อมูล auth_group อยู่หรือไม่ ถ้าไม่มีให้เพิ่มเข้าไป
    if not Group.objects.exists():
        Group.objects.bulk_create([
            Group(name="Admin"),
            Group(name="Assessor"),
            Group(name="Evaluator"),
            Group(name="Staff"),
        ])

    return render(request, 'app_general/home.html')

@login_required
def about(request):
    return render(request,'app_general/about.html')



@login_required
def search_user(request):
    form = SearchForm(request.GET or None)
    users = User.objects.exclude(is_superuser=True)
    all_groups = Group.objects.exclude(name='Admin')  # ซ่อนกลุ่ม Admin
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
    
    user_data = []
    for user in users:
        user_groups = user.groups.values_list('name', flat=True)
        user_data.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'groups': list(user_groups) if user_groups else ['']
        })
    
    context = {
        'form': form,
        'users': user_data,
        'all_groups': all_groups,
    }
    
    return render(request, 'app_general/search.html', context)


@login_required
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)

    # ตรวจสอบว่าผู้ใช้มี Profile อยู่แล้วหรือไม่ ถ้าไม่มีก็สร้างใหม่โดยไม่บันทึก ac_id
    try:
        profile = Profile.objects.get(user=user_to_edit)
    except Profile.DoesNotExist:
        profile = Profile(user=user_to_edit)  # สร้าง Profile ใหม่แต่ยังไม่บันทึกลงฐานข้อมูล

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user_to_edit)
        profile_form = ExtendedProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # บันทึกข้อมูลของ User

            # ดึงค่า ac_id จากฟอร์มและตรวจสอบ
            selected_academic_type = profile_form.cleaned_data.get('ac_id')

            if selected_academic_type:
                profile.ac_id = selected_academic_type  # บันทึก ac_id ที่ได้รับจากฟอร์ม
                profile.save()

                messages.success(request, 'บันทึกข้อมูลเรียบร้อยแล้ว!')
                return redirect('user_edit', user_id=user_to_edit.id)
            else:
                messages.error(request, "กรุณาเลือกประเภทตำแหน่งวิชาการ.")
                return render(request, 'app_general/user_edit.html', {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'user_to_edit': user_to_edit,
                    'profile': profile,
                })
        else:
            messages.error(request, "กรุณาตรวจสอบความถูกต้องของข้อมูล.")
    else:
        user_form = UserProfileForm(instance=user_to_edit)
        profile_form = ExtendedProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_to_edit': user_to_edit,
        'profile': profile
    }

    return render(request, 'app_general/user_edit.html', context)







GROUP_TRANSLATIONS = {
    'Staff': 'เจ้าหน้าที่',
    'Evaluator': 'ผู้ประเมิน',
    'Assessor': 'ผู้รับประเมิน'
    # เพิ่มการแปลชื่อกลุ่มอื่น ๆ ที่คุณต้องการ
}



@login_required
def ajax_search_user(request):
    query = request.GET.get('query', '')
    users = User.objects.exclude(is_superuser=True).filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )
    results = []
    for user in users:
        groups = [GROUP_TRANSLATIONS.get(group.name, group.name) for group in user.groups.all()]
        results.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'groups': groups if groups else ['ไม่มีกลุ่ม']
        })
    all_groups = [{'id': group.id, 'name': GROUP_TRANSLATIONS.get(group.name, group.name)} for group in Group.objects.exclude(name='Admin')]
    return JsonResponse({'results': results, 'all_groups': all_groups})

@login_required
def ajax_change_user_group(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        
        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            
            user.groups.clear()  # ลบกลุ่มเก่าทั้งหมด
            user.groups.add(group)  # เพิ่มผู้ใช้เข้าไปในกลุ่มใหม่

            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Group.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Group not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})