from django.contrib.auth.models import User
from app_user.models import Profile

# ตรวจสอบและลบ Profile ที่ซ้ำกัน
for user in User.objects.all():
    profiles = Profile.objects.filter(user=user)
    if profiles.count() > 1:
        # ลบ Profile ที่ซ้ำออกให้เหลือเพียงหนึ่ง
        profiles.exclude(pk=profiles.first().pk).delete()