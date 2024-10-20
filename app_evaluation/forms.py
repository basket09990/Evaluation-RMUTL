from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from app_user.models import  WorkLeave,PersonalDiagram,UserWorkloadSelection,user_evaluation_score,user_work_info, administrative_competency,user_evident,group, user_evaluation_agreement, wl_field, wl_subfield, group_detail, WorkloadCriteria ,user_competency_main , main_competency , academic_type,specific_competency,user_evaluation
from django.core.exceptions import ValidationError



class UserEvaluationAgreementForm(forms.ModelForm):
    class Meta:
        model = user_evaluation_agreement
        fields = ['user', 'year']

class GroupForm(forms.ModelForm):
    class Meta:
        model = group
        fields = ['g_name', 'g_field_name', 'g_max_workload']
        labels = {
            'g_name': 'กลุ่มที่',
            'g_field_name': 'ชื่อกลุ่ม',
            'g_max_workload': 'ภาระงานขั้นต่ำ',

        }

class GroupDetailForm(forms.ModelForm):
    f_id = forms.ModelChoiceField(
        queryset=wl_field.objects.all(),
        label='ชื่อภาระงาน',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="กรุณาเลือกชื่อน้ำหนักงาน"
    )

    class Meta:
        model = group_detail
        fields = ['f_id', 'gd_workload']
        labels = {
            'gd_workload': 'น้ำหนักภาระงาน',

        }

class WlFieldForm(forms.ModelForm):
    class Meta:
        model = wl_field
        fields = ['f_name']
        labels = {
            'f_name': 'ชื่อภาระงาน',

        }

class WlSubfieldForm(forms.ModelForm):
    class Meta:
        model = wl_subfield
        fields = ['sf_name']
        labels = {
            'sf_name': 'ชื่อกลุ่มย่อยภาระงาน',

        }

class WorkloadCriteriaForm(forms.ModelForm):
    class Meta:
        model = WorkloadCriteria
        fields = ['c_name', 'c_num', 'c_maxnum', 'c_unit', 'c_workload']
        labels = {
            'c_name': 'สมรรถนะหลัก (ที่สภามหาวิทยาลัยกำหนด)',
            'c_num': 'จำนวน',
            'c_maxnum': 'จำนวนสูงสุด',
            'c_unit': 'หน่วย',
            'c_workload': 'ภาระงาน',
        }

class MainCompetencyForm(forms.ModelForm):
    # mc_type ดึงข้อมูลจาก ac_name ของ academic_type
    mc_type = forms.ModelChoiceField(
        queryset=academic_type.objects.all(),
        to_field_name='ac_name',  # ดึงชื่อของ ac_name
        empty_label="เลือกประเภทตำแหน่งวิชาการ",
        required=True,
        label="ประเภทตำแหน่งวิชาการ"
    )
    
    class Meta:
        model = main_competency
        fields = ['mc_name', 'mc_type', 'mc_num']
        labels = {
            'mc_name': 'สมรรถนะหลัก (ที่สภามหาวิทยาลัยกำหนด)',
            'mc_type': 'ประเภทตำแหน่งวิชาการ',
            'mc_num': 'ระดับสมรรถนะที่คาดหวัง',
        }

class SpecificCompetencyForm(forms.ModelForm):
    # ดึงข้อมูล ac_name ของ academic_type มาใช้ใน sc_type
    sc_type = forms.ModelChoiceField(
        queryset=academic_type.objects.all(),
        to_field_name='ac_name',  # ใช้ชื่อของ ac_name
        empty_label="เลือกประเภทตำแหน่งวิชาการ",
        required=True,
        label="ประเภทตำแหน่งวิชาการ"
    )

    class Meta:
        model = specific_competency
        fields = ['sc_name', 'sc_type', 'sc_num']
        labels = {
            'sc_name': 'สมรรถนะเฉพาะตามลักษณะงานที่ปฏิบัติ (ที่สภามหาวิทยาลัยกำหนด)',
            'sc_type': 'ประเภทตำแหน่งวิชาการ',
            'sc_num': 'ระดับสมรรถนะที่คาดหวัง',
        }

class AdministrativeCompetencyForm(forms.ModelForm):
    # ดึงข้อมูล ac_name ของ academic_type มาใช้ใน adc_type


    class Meta:
        model = administrative_competency
        fields = ['adc_name']
        labels = {
            'adc_name': 'สมรรถนะทางการบริหาร (ที่สภามหาวิทยาลัยกำหนด) ',
            
            
        }

class GroupSelectionForm(forms.ModelForm):
    g_name = forms.ModelChoiceField(
        queryset=group.objects.all(),
        empty_label="เลือกกลุ่มประเมิน",
        label="กลุ่มประเมิน",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = user_evaluation_agreement
        fields = ['g_name']
        
class UserEvaluationForm(forms.ModelForm):
    full_name = forms.CharField(label="ชื่อ-นามสกุล", max_length=255, required=False)
    day = forms.IntegerField(label="วัน", min_value=1, max_value=31, required=False)
    month = forms.IntegerField(label="เดือน", min_value=1, max_value=12, required=False)
    year = forms.IntegerField(label="ปี", min_value=1900, max_value=2100, required=False)

    class Meta:
        model = user_evaluation
        fields = [
            'c_gtt', 'c_wl', 'c_sumwl', 'mc_score', 'sc_score', 'adc_score',
            'achievement_work', 'performing_work', 'other_work', 'improved', 'suggestions'
        ]
        widgets = {
            'c_gtt': forms.NumberInput(attrs={'class': 'form-control'}),
            'c_wl': forms.NumberInput(attrs={'class': 'form-control'}),
            'c_sumwl': forms.NumberInput(attrs={'class': 'form-control'}),
            'mc_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'sc_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'adc_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'achievement_work': forms.NumberInput(attrs={'class': 'form-control'}),
            'performing_work': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_work': forms.NumberInput(attrs={'class': 'form-control'}),
            'improved': forms.Textarea(attrs={'class': 'form-control'}),
            'suggestions': forms.Textarea(attrs={'class': 'form-control'}),
        }
        widgets = {
            'improved': forms.Textarea(attrs={'placeholder': 'ระบุจุดเด่น หรือสิ่งที่ควรปรับปรุงแก้ไข'}),
            'suggestions': forms.Textarea(attrs={'placeholder': 'ระบุข้อเสนอแนะเกี่ยวกับการส่งเสริมและพัฒนา'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # บันทึกข้อมูล "ชื่อ-นามสกุล" และวันที่ใน instance
        full_name = self.cleaned_data.get('full_name', None)
        day = self.cleaned_data.get('day', None)
        month = self.cleaned_data.get('month', None)
        year = self.cleaned_data.get('year', None)

        if full_name:
            instance.full_name = full_name
        if day and month and year:
            instance.start_day = day
            instance.start_month = month
            instance.start_year = year

        if commit:
            instance.save()
        return instance

class UserEvidentForm(forms.ModelForm):
    class Meta:
        model = user_evident
        fields = ['picture', 'file']
        widgets = {
            'picture': forms.ClearableFileInput(),
            'file': forms.ClearableFileInput(),
        }

class UserWorkInfoForm(forms.ModelForm):
    class Meta:
        model = user_work_info
        fields = [
            'punishment',
        ]
        labels = {
            'punishment': 'การกระทำผิดวินัย/การถูกลงโทษ',
        }
        widgets = {
            'punishment': forms.TextInput(attrs={'style': 'width: 500px; height: 40px;'}),
        }


ALLOWED_FILE_EXTENSIONS = ['pdf', 'docx', 'xlsx']
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']

def validate_file_extension(value):
    ext = value.name.split('.')[-1].lower()
    if ext not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError('อัปโหลดได้เฉพาะไฟล์ .pdf หรือ .docx เท่านั้น')

def validate_image_extension(value):
    ext = value.name.split('.')[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError('อัปโหลดได้เฉพาะไฟล์รูปภาพ .jpg, .jpeg หรือ .png เท่านั้น')

class UserEvidentForm(forms.ModelForm):

    class Meta:
        model = user_evident
        fields = ['file', 'picture']

    def clean_file(self):
        files = self.files.getlist('file')
        for file in files:
            validate_file_extension(file)
        return files

    def clean_picture(self):
        pictures = self.files.getlist('picture')
        for picture in pictures:
            validate_image_extension(picture)
        return pictures

class UserEvaluationScoreForm(forms.ModelForm):

    class Meta:
        model = user_evaluation_score
        fields = [
            'f_id', 'sf_id', 'g_id', 'gd_id', 'c_id', 'ues_name', 'ues_name_detail',
            'ues_num', 'ues_unit', 'ues_score', 'ues_maxnum', 'ues_workload'
        ]

        # การปรับแต่งฟิลด์ เช่น การเพิ่ม widget หรือ placeholder
        widgets = {
            'f_id': forms.Select(attrs={'class': 'short-input'}),
            'sf_id': forms.Select(attrs={'class': 'short-input'}),
            'g_id': forms.Select(attrs={'class': 'short-input'}),
            'gd_id': forms.Select(attrs={'class': 'short-input'}),
            'c_id': forms.Select(attrs={'class': 'short-input'}),
            'ues_name': forms.TextInput(attrs={'class': 'short-input', 'placeholder': 'ชื่อการประเมิน'}),
            'ues_name_detail': forms.Textarea(attrs={'class': 'short-input', 'placeholder': 'รายละเอียดการประเมิน', 'rows': 3}),
            'ues_num': forms.NumberInput(attrs={'class': 'short-input', 'min': 0,'value': 0,  'placeholder': 'จำนวนหน่วย'}),
            'ues_unit': forms.NumberInput(attrs={'class': 'short-input', 'min': 0, 'placeholder': 'หน่วย'}),
            'ues_score': forms.NumberInput(attrs={'class': 'short-input', 'min': 0, 'placeholder': 'คะแนนรวม'}),
            'ues_maxnum': forms.NumberInput(attrs={'class': 'short-input', 'min': 0,'value': 0, 'placeholder': 'ค่าสูงสุด'}),
            'ues_workload': forms.NumberInput(attrs={'class': 'short-input', 'min': 0, 'placeholder': 'ค่าน้ำหนักงาน'}),
        }

        labels = {
            'f_id': 'ชื่อน้ำหนักงาน',
            'sf_id': 'รายละเอียดน้ำหนักงาน',
            'g_id': 'กลุ่ม',
            'gd_id': 'รายละเอียดกลุ่ม',
            'c_id': 'ชื่อการประเมิน',
            'ues_name': 'ชื่อการประเมิน',
            'ues_name_detail': 'รายละเอียดการประเมิน',
            'ues_num': 'จำนวนหน่วย',
            'ues_unit': 'หน่วย',
            'ues_score': 'คะแนนรวม',
            'ues_maxnum': 'ค่าสูงสุด',
            'ues_workload': 'ค่าน้ำหนักงาน',
        }

    def clean(self):
        cleaned_data = super().clean()
        ues_unit = cleaned_data.get('ues_unit')
        ues_workload = cleaned_data.get('ues_workload')

        if ues_unit is not None and ues_workload is not None:
            cleaned_data['ues_score'] = ues_unit * ues_workload  # คำนวณ ues_score
        else:
            cleaned_data['ues_score'] = 0  # ตั้งค่าเริ่มต้นเป็น 0 หากค่าใดว่าง

        return cleaned_data
    
    def clean_ues_num(self):
        ues_num = self.cleaned_data.get('ues_num')
        if ues_num in [None, '']:
            return 0  # ถ้าฟิลด์ว่าง ให้ตั้งค่าเป็น 0
        return ues_num
    
    def clean_ues_maxnum(self):
        ues_maxnum = self.cleaned_data.get('ues_maxnum')
        if ues_maxnum in [None, '']:
            return 0  # ถ้าฟิลด์ว่าง ให้ตั้งค่าเป็น 0
        return ues_maxnum

class SubFieldForm(forms.ModelForm):
    class Meta:
        model = wl_subfield
        fields = ['sf_name']  # ฟิลด์ที่ต้องการให้กรอก
        labels = {
            'sf_name': 'ชื่อสมรรถนะเฉพาะ',
        }

class SelectSubfieldForm(forms.Form):
    selected_subfields = forms.ModelMultipleChoiceField(
        queryset=wl_subfield.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # แสดงเป็นกล่อง checkbox
        required=True
    )

class WorkloadCriteriaSelectionForm(forms.Form):
    selected_criteria = forms.ModelMultipleChoiceField(
        queryset=WorkloadCriteria.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="เลือกเกณฑ์การทำงาน"
    )

class SubFieldSelectionForm(forms.ModelForm):
    class Meta:
        model = wl_subfield
        fields = ['sf_id']  # เลือก subfield จาก f_id

class WorkloadCriteriaSelectionForm(forms.ModelForm):
    class Meta:
        model = UserWorkloadSelection
        fields = ['selected_unit', 'notes']  # เพิ่ม field สำหรับหมายเหตุ

    def __init__(self, *args, **kwargs):
        super(WorkloadCriteriaSelectionForm, self).__init__(*args, **kwargs)
        self.fields['selected_unit'].label = 'จำนวน Unit'
        self.fields['notes'].label = 'หมายเหตุ'

class UserWorkloadSelectionForm(forms.ModelForm):
    selected_id = forms.ModelChoiceField(
        queryset=WorkloadCriteria.objects.none(),  # เริ่มต้นด้วย queryset ว่าง
        label="เลือกเกณฑ์ภาระงาน",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    selected_unit = forms.FloatField(
        label="จำนวน",
        required=False,  # กำหนดเป็น False เพื่อไม่ให้ฟอร์มบังคับฟิลด์นี้เสมอ
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserWorkloadSelection
        fields = ['selected_id', 'selected_name', 'selected_num', 'selected_unit', 'notes']
        labels = {
            'selected_unit': 'จำนวน',
            'notes': 'หมายเหตุ',
        }

    def __init__(self, *args, **kwargs):
        subfield = kwargs.pop('subfield', None)  # ดึง subfield จาก kwargs
        super().__init__(*args, **kwargs)
        
        # ถ้ามี subfield ให้กำหนดค่า queryset ของ selected_id ใหม่
        if subfield:
            self.fields['selected_id'].queryset = WorkloadCriteria.objects.filter(sf_id=subfield)
        
        # ถ้า instance มีค่า selected_id ให้ใช้ค่า c_unit เป็นค่าเริ่มต้นของ selected_unit
        if self.instance and getattr(self.instance, 'selected_id', None):
            self.fields['selected_unit'].initial = self.instance.selected_id.c_unit

class UserWorkloadSelectionForm1(forms.ModelForm):

    class Meta:
        model = UserWorkloadSelection
        fields = [ 'selected_name', 'selected_num', 'notes']
        labels = {
            'selected_unit': 'จำนวน',
            'notes': 'หมายเหตุ',
        }

class UserWorkloadSelectionForm2(forms.ModelForm):
    class Meta:
        model = UserWorkloadSelection
        fields = ['selected_workload_edit']
        labels = {
            'selected_workload_edit': 'ภาระงานที่แก้ไข',
        }

class PersonalDiagramForm(forms.ModelForm):
    class Meta:
        model = PersonalDiagram
        fields = ['skill_evol', 'dev', 'dev_time']
        widgets = {
            'skill_evol': forms.TextInput(attrs={'placeholder': 'ความรู้/ทักษะ/สมรรถนะที่ต้องได้รับการพัฒนา '}),
            'dev': forms.TextInput(attrs={'placeholder': 'วิธีการพัฒนา'}),
            'dev_time': forms.TextInput(attrs={'placeholder': 'ช่วงเวลาที่ต้องการพัฒนา'}),
        }

class UserSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'ค้นหาด้วยชื่อผู้ใช้...',
        'class': 'form-control'
    }))

class WorkLeaveForm(forms.ModelForm):
    class Meta:
        model = WorkLeave
        fields = ['times', 'days']  # เอา 'leave_type' ออกจากฟอร์ม
        widgets = {
            'times': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'จำนวนครั้ง'}),
            'days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'จำนวนวัน'}),
        }


        