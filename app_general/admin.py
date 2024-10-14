from django.contrib import admin

from app_user.models import Profile

from django.utils.translation import gettext_lazy as _
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

class CustomAdminSite(AdminSite):
    site_header = _("ระบบประเมินบุคลากรสายวิชาการ คณะวิศวกรรมศาสตร์ สาขาวิศวกรรมไฟฟ้า")
    site_title = _("การจัดการไซต์")
    index_title = _("")
    
custom_admin_site = CustomAdminSite(name='management_admin')



