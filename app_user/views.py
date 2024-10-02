from django.shortcuts import render, get_object_or_404 ,redirect
from app_user.forms import RegisterForm, UserProfileForm ,ExtendedProfileForm
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from app_user.models import Profile
from django.contrib import messages 
from django.core.paginator import Paginator



def register(request: HttpRequest):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
    else:
        form = RegisterForm()
    
    context = {"form": form}
    return render(request, "app_user/register.html", context)


@login_required
def profile(request: HttpRequest):
    user = request.user
    is_new_profile = False

    # ตรวจสอบว่าผู้ใช้มี Profile อยู่แล้วหรือไม่ ถ้าไม่มีก็สร้างใหม่โดยไม่บันทึก ac_id
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile(user=user)  # สร้าง Profile ใหม่แต่ยังไม่บันทึกลงฐานข้อมูล
        is_new_profile = True

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        extended_form = ExtendedProfileForm(request.POST, instance=profile)

        if form.is_valid() and extended_form.is_valid():
            form.save()
            profile = extended_form.save(commit=False)
            if is_new_profile:
                profile.user = user

            # ดึงค่า ac_id จากฟอร์มและตรวจสอบ
            ac_id = extended_form.cleaned_data.get('ac_id')

            if ac_id:
                profile.ac_id = ac_id  # บันทึก ac_id ที่ได้รับจากฟอร์ม
            else:
                messages.error(request, "กรุณาเลือกประเภทตำแหน่งวิชาการ.")
                return render(request, "app_user/profile.html", {
                    "form": form,
                    "extended_form": extended_form,
                    "profile": profile,
                })

            profile.save()
            messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
            return HttpResponseRedirect(reverse("profile"))
    else:
        form = UserProfileForm(instance=user)
        extended_form = ExtendedProfileForm(instance=profile)

    context = {
        "form": form,
        "extended_form": extended_form,
        "profile": profile,  # ส่งข้อมูล profile ไปยัง template
    }

    return render(request, "app_user/profile.html", context)

