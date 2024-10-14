# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import Profile
from .forms import ExtendedProfileForm, CustomUserChangeForm
from app_general.admin import custom_admin_site
from django.contrib.auth.admin import GroupAdmin
from app_user.models import user_evaluation_agreement,academic_type


# Profile Inline
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'โปรไฟล์'
    form = ExtendedProfileForm
    fields = ['position', 'ac_id', 'administrative_position', 'salary', 'position_number',
              'affiliation', 'old_government', 'special_position', 'start_goverment', 'sum_time_goverment']


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    inlines = [ProfileInline]

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = self.form
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CustomUserAdmin, self).get_fieldsets(request, obj)
        if not request.user.is_superuser:
            if 'permissions' in fieldsets:
                fieldsets.remove('permissions')
            return [(None, {'fields': ('username', 'first_name', 'last_name', 'email', 'groups')})]
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_superuser=False)

    def save_model(self, request, obj, form, change):
        super(CustomUserAdmin, self).save_model(request, obj, form, change)

        # ตรวจสอบว่า Profile มีอยู่แล้วหรือไม่
        profile, created = Profile.objects.get_or_create(user=obj)
        
        # ปรับปรุงข้อมูลใน Profile
        profile.position = form.cleaned_data.get('position', profile.position)
        profile.ac_id = form.cleaned_data.get('academic_type', profile.ac_id)
        profile.administrative_position = form.cleaned_data.get('administrative_position', profile.administrative_position)
        profile.salary = form.cleaned_data.get('salary', profile.salary)
        profile.position_number = form.cleaned_data.get('position_number', profile.position_number)
        profile.affiliation = form.cleaned_data.get('affiliation', profile.affiliation)
        profile.old_government = form.cleaned_data.get('old_government', profile.old_government)
        profile.special_position = form.cleaned_data.get('special_position', profile.special_position)
        profile.start_goverment = form.cleaned_data.get('start_goverment', profile.start_goverment)
        profile.sum_time_goverment = form.cleaned_data.get('sum_time_goverment', profile.sum_time_goverment)

        profile.save()

    def has_add_permission(self, request):
        return False


# Unregister โมเดล User จาก admin site หากมีการลงทะเบียนแล้ว
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# ลงทะเบียนโมเดล User กับ custom_admin_site
admin.site.register(user_evaluation_agreement)
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Group, GroupAdmin)

