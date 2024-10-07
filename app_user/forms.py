from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from app_user.models import Profile, academic_type
from datetime import date, datetime
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _ 

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("first_name","last_name")



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name","last_name")
        labels = {
            'first_name': 'ชื่อ',
            'last_name': 'นามสกุล'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ExtendedProfileForm(forms.ModelForm):
    ac_id = forms.ModelChoiceField(
        queryset=academic_type.objects.all(),
        empty_label="กรุณาเลือกประเภทตำแหน่งวิชาการ",
        required=True,
        label="ประเภทตำแหน่งวิชาการ"
    )

    class Meta:
        model = Profile
        fields = ( "ac_id", "administrative_position", "salary",
                  "position_number", "affiliation", "old_government", 
                  "special_position", "start_goverment", "sum_time_goverment")
        labels = {
            
            'ac_id': 'ประเภทตำแหน่งวิชาการ',
            'administrative_position': 'ตำแหน่งบริหาร',
            'salary': 'เงินเดือน',
            'position_number': 'เลขที่ประจำตำแหน่ง',
            'affiliation': 'สังกัด',
            'old_government': 'มาช่วยราชการจากที่ใด (ถ้ามี)',
            'special_position': 'หน้าที่พิเศษ',
            'start_goverment': 'เริ่มรับราชการเมื่อวันที่',
        }
        widgets = {
            
            'ac_id': forms.Select(attrs={'class': 'form-control'}),
            'administrative_position': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'position_number': forms.TextInput(attrs={'class': 'form-control'}),
            'affiliation': forms.TextInput(attrs={'class': 'form-control'}),
            'old_government': forms.TextInput(attrs={'class': 'form-control'}),
            'special_position': forms.TextInput(attrs={'class': 'form-control'}),
            'start_goverment': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%d/%m/%Y'  # หรือใช้ '%d-%m-%Y'
            ),
        }

    def clean_start_goverment(self):
        start_goverment = self.cleaned_data.get('start_goverment', None)
        # ตรวจสอบว่ามีค่าและไม่ใช่สตริงก็ส่งค่าคืนกลับมาได้เลย
        if isinstance(start_goverment, date):  # ตรวจสอบ `datetime.date` ไม่ใช่ `datetime`
            return start_goverment
        
        # ถ้าเป็นสตริงให้แปลง
        if start_goverment:
            try:
                # แปลงสตริงเป็นวันที่
                datetime.strptime(start_goverment, '%Y-%m-%d')
            except ValueError:
                raise forms.ValidationError("รูปแบบวันที่ไม่ถูกต้อง. กรุณาใช้รูปแบบ YYYY-MM-DD.")
        return start_goverment
    





    
class CombinedUserProfileForm(forms.Form):
    first_name = forms.CharField(
        label='ชื่อ', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='นามสกุล', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ac_id = forms.CharField(
        label='ประเภทตำแหน่งวิชาการ', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    administrative_position = forms.CharField(
        label='ตำแหน่งบริหาร', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    salary = forms.DecimalField(
        label='เงินเดือน', 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    position_number = forms.CharField(
        label='เลขที่ประจำตำแหน่ง', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    affiliation = forms.CharField(
        label='สังกัด', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    old_government = forms.CharField(
        label='มาช่วยราชการจากที่ใด (ถ้ามี)', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    special_position = forms.CharField(
        label='หน้าที่พิเศษ', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    start_goverment = forms.DateField(
        label='เริ่มรับราชการเมื่อวันที่', 
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    sum_time_goverment = forms.IntegerField(
        label='รวมเวลารับราชการ', 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        if self.current_user and not self.current_user.is_superuser:
            if 'user_permissions' in self.fields:
                self.fields.pop('user_permissions')