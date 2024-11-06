from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm

class UserSearchForm(forms.Form):
    query = forms.CharField(label='ค้นหาผู้ใช้', max_length=100)



class UserGroupEditForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='กลุ่ม'
    )

    class Meta:
        model = User
        fields = ['groups']

class EditUserGroupsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # ตัวอย่างการใช้ request ในฟอร์ม
        if self.request and self.request.user.is_superuser:
            self.fields['groups'].queryset = Group.objects.all()
        else:
            self.fields['groups'].queryset = Group.objects.filter(name='User')
    
    class Meta:
        model = User
        fields = ['groups']
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }

class SearchForm(forms.Form):
    query = forms.CharField(label='ค้นหา', max_length=100, required=False)

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(label='Select a PDF file')