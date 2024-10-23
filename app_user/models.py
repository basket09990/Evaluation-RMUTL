from django.db import models
from django.contrib.auth.models import  User
from datetime import date, datetime
from django.utils import timezone


class group(models.Model):
    g_id = models.AutoField(primary_key=True)
    g_name = models.TextField(default="", blank=True, null=True)
    g_field_name = models.TextField(default="", blank=True, null=True)
    g_max_workload = models.IntegerField(default="", blank=True, null=True)

    def __str__(self):
        return self.g_name

class evr_round(models.Model):
    evr_id = models.AutoField(primary_key=True)
    evr_year = models.IntegerField(default=datetime.now().year)
    evr_round = models.IntegerField(default="", blank=True, null=True)
    evr_status = models.BooleanField(default=False)
    end_date = models.DateField(default=timezone.now) 

class user_evaluation_agreement(models.Model):
    uevra_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField(default=datetime.now().year)
    g_id = models.ForeignKey(group, on_delete=models.CASCADE)
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.year} - {self.g_id.g_name}"

class wl_field(models.Model):
    f_id = models.AutoField(primary_key=True)
    f_name = models.TextField(default="", blank=True, null=True,verbose_name="ชื่อน้ำหนักงาน")

    def __str__(self):
        return self.f_name

class wl_subfield(models.Model):
    sf_id = models.AutoField(primary_key=True)
    sf_name = models.TextField(default="", blank=True, null=True)
    f_id = models.ForeignKey(wl_field, on_delete=models.CASCADE,related_name='subfields')

    def __str__(self):
        return self.sf_name
    
class group_detail(models.Model):
    gd_id = models.AutoField(primary_key=True)
    f_id = models.ForeignKey(wl_field, on_delete=models.CASCADE)
    gd_workload = models.IntegerField(default="", blank=True, null=True)
    g_id = models.ForeignKey(group, on_delete=models.CASCADE)

class academic_type(models.Model):
    # ตัวเลือกประเภทตำแหน่งวิชาการ
    ACADEMIC_CHOICES = [
        ("เจ้าหน้าที่", "เจ้าหน้าที่"),
        ("อาจารย์", "อาจารย์"),
        ("รองศาสตราจารย์", "รองศาสตราจารย์"),
        ("ผู้ช่วยศาสตราจารย์", "ผู้ช่วยศาสตราจารย์"),
        ("ศาสตราจารย์", "ศาสตราจารย์"),
    ]

    ac_id = models.AutoField(primary_key=True)
    ac_name = models.TextField(
        verbose_name="ประเภทตำแหน่งวิชาการ",
        choices=ACADEMIC_CHOICES
    )

    def __str__(self):
        return self.ac_name

class Profile(models.Model):
    position = models.TextField(default="", blank=True, null=True, verbose_name="ตำแหน่ง")
    administrative_position = models.TextField(default="", verbose_name="ตำแหน่งบริหาร")
    salary = models.TextField(default="", verbose_name="เงินเดือน")
    position_number = models.TextField(default="", verbose_name="เลขที่ประจำตำแหน่ง")
    affiliation = models.TextField(default="", verbose_name="สังกัด")
    old_government = models.TextField(default="", verbose_name="มาช่วยราชการจากที่ใด (ถ้ามี)")
    special_position = models.TextField(default="", verbose_name="หน้าที่พิเศษ")
    start_goverment = models.TextField(default="", verbose_name="เริ่มรับราชการเมื่อวันที่")
    sum_time_goverment = models.IntegerField(null=True, blank=True)
    years_of_service = models.IntegerField(null=True, blank=True)
    months_of_service = models.IntegerField(null=True, blank=True)
    days_of_service = models.IntegerField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="ผู้ใช้")
    ac_id = models.ForeignKey('app_user.academic_type', on_delete=models.CASCADE, verbose_name="ประเภทตำแหน่งวิชาการ")

    def save(self, *args, **kwargs):
        if self.start_goverment:
            try:
                # ตรวจสอบว่าค่า start_goverment เป็นสตริงหรือ datetime
                if isinstance(self.start_goverment, str):
                    start_date = datetime.strptime(self.start_goverment, '%Y-%m-%d').date()
                elif isinstance(self.start_goverment, date):
                    start_date = self.start_goverment
                else:
                    raise ValueError("Invalid date format")

                today = datetime.today().date()
                days_passed = (today - start_date).days
                self.sum_time_goverment = days_passed

                # คำนวณจำนวนปี เดือน และวัน
                years = days_passed // 365
                months = (days_passed % 365) // 30
                days = (days_passed % 365) % 30

                self.years_of_service = years
                self.months_of_service = months
                self.days_of_service = days
            except (ValueError, TypeError):
                # จัดการกับกรณีวันที่ไม่ถูกต้องหรือค่าเป็น None
                self.sum_time_goverment = 0
                self.years_of_service = 0
                self.months_of_service = 0
                self.days_of_service = 0
        else:
            self.sum_time_goverment = 0
            self.years_of_service = 0
            self.months_of_service = 0
            self.days_of_service = 0

        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.username}"

class WorkloadCriteria(models.Model):
    c_id = models.AutoField(primary_key=True)
    c_name = models.TextField(default="", blank=True, null=True)
    c_num = models.FloatField(default="0", blank=True, null=True)
    c_unit = models.TextField(default="", blank=True, null=True)
    c_maxnum = models.FloatField(default="0", blank=True, null=True)
    c_workload = models.FloatField(default="0", blank=True, null=True)
    f_id = models.ForeignKey(wl_field, on_delete=models.CASCADE, blank=True, null=True)
    sf_id = models.ForeignKey(wl_subfield, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.c_name}"

    # ฟังก์ชันเพื่อดึงตัวเลือก c_name ที่สัมพันธ์กับ c_maxnum
    @classmethod
    def get_maxnum_choices(cls):
        return [(criteria.c_id, f"{criteria.c_name} (Max: {criteria.c_maxnum})") for criteria in cls.objects.all()]

    # ฟังก์ชันเพื่อดึงตัวเลือก c_name ที่สัมพันธ์กับ c_workload
    @classmethod
    def get_workload_choices(cls):
        return [(criteria.c_id, f"{criteria.c_name} (Workload: {criteria.c_workload})") for criteria in cls.objects.all()]

class WorkLeave(models.Model):
    # กำหนดประเภทการลา
    SICK_LEAVE = 'SL'
    PERSONAL_LEAVE = 'PL'
    LATE = 'LT'
    MATERNITY_LEAVE = 'ML'
    ORDINATION_LEAVE = 'OL'
    LONG_SICK_LEAVE = 'LSL'
    ADSENT_WORK = 'AW'
    
    LEAVE_TYPES = [
        (SICK_LEAVE, 'ลาป่วย'),
        (PERSONAL_LEAVE, 'ลากิจ'),
        (LATE, 'มาสาย'),
        (MATERNITY_LEAVE, 'ลาคลอดบุตร'),
        (ORDINATION_LEAVE, 'ลาอุปสมบท'),
        (LONG_SICK_LEAVE, 'ลาป่วยจำเป็นต้องรักษาตัวเป็นเวลานานคราวเดียวหรือหลายคราวรวมกัน'),
        (ADSENT_WORK, 'ขาดราชการ'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    round = models.ForeignKey('evr_round', on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPES)
    times = models.IntegerField(default=0, blank=True, null=True, verbose_name="จำนวนครั้ง")
    days = models.IntegerField(default=0, blank=True, null=True, verbose_name="จำนวนวัน")

    def __str__(self):
        return f'{self.user.username} - {self.get_leave_type_display()} (รอบ {self.round.evr_round})'

class user_work_info(models.Model):
    uwf_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    round = models.ForeignKey('evr_round', on_delete=models.CASCADE)
    punishment = models.TextField(default="", blank=True, null=True, verbose_name="การกระทำผิดวินัย/การถูกลงโทษ")

    def __str__(self):
        return f'{self.user.username} - รอบที่ {self.round.evr_round}'

    @property
    def work_leaves(self):
        """ ดึงข้อมูลการลาในแต่ละประเภทของผู้ใช้ """
        return WorkLeave.objects.filter(user=self.user, round=self.round)

class user_evaluation(models.Model):
    uevr_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)
    ac_id = models.ForeignKey(academic_type, on_delete=models.SET_NULL, null=True, blank=True)
    administrative_position = models.TextField(null=True, blank=True)
    c_gtt = models.FloatField(default="0", blank=True, null=True)
    c_wl = models.FloatField(default="0", blank=True, null=True)
    c_sumwl = models.FloatField(default="0", blank=True, null=True)
    approve_status = models.BooleanField(default=False)
    evaluater_id = models.IntegerField(default="0", blank=True, null=True)
    evaluater_editgtt = models.FloatField(default="0", blank=True, null=True)
    mc_score = models.FloatField(default="0", blank=True, null=True, verbose_name="ผลสัมฤทธิ์ของงาน")
    sc_score = models.FloatField(default="0", blank=True, null=True, verbose_name="ผลสัมฤทธิ์ของงาน")
    adc_score = models.FloatField(default="0", blank=True, null=True, verbose_name="ผลสัมฤทธิ์ของงาน")
    cp_num = models.FloatField(default="0", blank=True, null=True, verbose_name="จำนวนสมรรถนะ")
    cp_score = models.FloatField(default="0", blank=True, null=True, verbose_name="คะแนน")
    cp_sum = models.FloatField(default="0", blank=True, null=True, verbose_name="ผลรวมคะแนน")
    cp_main_sum = models.FloatField(default="0", blank=True, null=True, verbose_name="คะแนนที่ได้")
    achievement_work = models.FloatField(default="0", blank=True, null=True, verbose_name="ผลสัมฤทธิ์ของงาน")
    performing_work = models.FloatField(default="0", blank=True, null=True, verbose_name="พฤติกรรมการปฏิบัติราชการ (สมรรถนะ)")
    other_work = models.FloatField(default="0", blank=True, null=True, verbose_name="องค์ประกอบอื่น ๆ (ถ้ามี) ")
    sum_work = models.FloatField(default="0", blank=True, null=True, verbose_name="รวม")
    improved = models.TextField(default="", blank=True, null=True, verbose_name="จุดเด่น และ/หรือ สิ่งที่ควรปรับปรุงแก้ไข")
    suggestions = models.TextField(default="", blank=True, null=True, verbose_name="ข้อเสนอแนะเกี่ยวกับวิธีส่งเสริมและพัฒนา")
    remark_achievement = models.TextField(default="", blank=True, null=True, verbose_name="ข้อเสนอแนะเกี่ยวกับวิธีส่งเสริมและพัฒนา")
    remark_mc = models.TextField(default="", blank=True, null=True, )
    remark_other = models.TextField(default="", blank=True, null=True, )
    remark_total = models.TextField(default="", blank=True, null=True, )
    created_at = models.DateTimeField(auto_now_add=True) 
    
    full_name = models.CharField(max_length=255, blank=True, null=True)
    # ฟิลด์สำหรับเก็บวัน เดือน ปี
    start_day = models.IntegerField(blank=True, null=True)
    start_month = models.IntegerField(blank=True, null=True)
    start_year = models.IntegerField(blank=True, null=True)

class main_competency(models.Model):
    mc_id = models.AutoField(primary_key=True)
    mc_name = models.TextField(default="", blank=True, null=True)
    mc_type = models.TextField(default="", blank=True, null=True)
    mc_num = models.IntegerField(default="0", blank=True, null=True)

class user_competency_main(models.Model):
    ucm_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    mc_id = models.ForeignKey(main_competency, on_delete=models.CASCADE)
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)
    umc_name = models.TextField(default="", blank=True, null=True)
    umc_type = models.TextField(default="", blank=True, null=True)
    actual_score = models.IntegerField(default=0, blank=True, null=True)

class specific_competency(models.Model):
    sc_id = models.AutoField(primary_key=True)
    sc_name = models.TextField(default="", blank=True, null=True)
    sc_type = models.TextField(default="", blank=True, null=True)
    sc_num = models.IntegerField(default="0", blank=True, null=True)

class user_competency_councilde(models.Model):
    ucc_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    sc_id = models.ForeignKey(specific_competency, on_delete=models.CASCADE)
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)
    ucc_name = models.TextField(default="", blank=True, null=True)
    ucc_type = models.TextField(default="", blank=True, null=True)
    actual_score = models.IntegerField(default=0, blank=True, null=True)

class administrative_competency(models.Model):
    adc_id = models.AutoField(primary_key=True)
    adc_name = models.TextField(default="", blank=True, null=True)
    adc_type = models.TextField(default="", blank=True, null=True)
    adc_num = models.IntegerField(default="0", blank=True, null=True)

class user_competency_ceo(models.Model):
    uceo_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    adc_id = models.ForeignKey(administrative_competency, on_delete=models.CASCADE)
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)
    uceo_name = models.TextField(default="", blank=True, null=True)
    uceo_type = models.TextField(default="", blank=True, null=True)
    actual_score = models.IntegerField(default=0, blank=True, null=True)
    uceo_num = models.IntegerField(default=0, blank=True, null=True)

class PersonalDiagram(models.Model):
    pd_id = models.AutoField(primary_key=True)
    uevr_id = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    skill_evol = models.TextField(default="", blank=True, null=True)
    dev = models.TextField(default="", blank=True, null=True)
    dev_time = models.TextField(default="", blank=True, null=True)

class user_evaluation_score(models.Model):
    ues_id = models.AutoField(primary_key=True)
    uevr_id = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    f_id = models.ForeignKey(wl_field, on_delete=models.CASCADE, blank=True, null=True)
    sf_id = models.ForeignKey(wl_subfield, on_delete=models.CASCADE, blank=True, null=True)
    g_id = models.ForeignKey(group, on_delete=models.CASCADE, blank=True, null=True)
    gd_id = models.ForeignKey(group_detail, on_delete=models.CASCADE, blank=True, null=True)
    c_id = models.ForeignKey(WorkloadCriteria, on_delete=models.CASCADE, blank=True, null=True)
    ues_name = models.TextField(default="", blank=True, null=True)
    ues_name_detail = models.TextField(default="", blank=True, null=True)
    ues_num = models.FloatField(default="", blank=True, null=True)
    ues_unit = models.FloatField(default="", blank=True, null=True)
    ues_score = models.FloatField(default="", blank=True, null=True)
    ues_maxnum = models.FloatField(default="", blank=True, null=True)
    ues_workload = models.FloatField(default="", blank=True, null=True)

class UserMainCompetencyScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ผู้ใช้ที่ทำการประเมิน
    mc_id = models.ForeignKey(main_competency, on_delete=models.CASCADE)  # สมรรถนะหลักที่ถูกประเมิน
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)  # รอบการประเมิน
    expected_score = models.FloatField(default=0)  # ระดับสมรรถนะที่คาดหวัง
    actual_score = models.FloatField(default=0)  # ระดับสมรรถนะที่แสดงออก

    class Meta:
        unique_together = ('user', 'mc_id', 'evr_id')  # เพื่อไม่ให้มีการบันทึกซ้ำในรอบการประเมินเดียวกัน

    def __str__(self):
        return f"{self.user.username} - {self.mc_id.mc_name} - {self.actual_score}"
    
class UserSpecificCompetencyScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sc_id = models.ForeignKey(specific_competency, on_delete=models.CASCADE)
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)
    expected_score = models.FloatField(default=0)
    actual_score = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'sc_id', 'evr_id')

    def __str__(self):
        return f"{self.user.username} - {self.sc_id.sc_name} - {self.actual_score}"
    
class UserAdministrativeCompetencyScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    adc_id = models.ForeignKey(administrative_competency, on_delete=models.CASCADE)
    evr_id = models.ForeignKey(evr_round, on_delete=models.CASCADE)
    expected_score = models.FloatField(default=0)
    actual_score = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'adc_id', 'evr_id')

    def __str__(self):
        return f"{self.user.username} - {self.adc_id.adc_name} - {self.actual_score}"

class SelectedSubfields(models.Model):
    user_evaluation = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    sf_id = models.ForeignKey(wl_subfield, on_delete=models.CASCADE)
    selected_value = models.TextField(blank=True, null=True)  # ข้อมูลเพิ่มเติม

    def __str__(self):
        return f"Evaluation: {self.user_evaluation}, Subfield: {self.sf_id.sf_name}"
    
class SelectedWorkload(models.Model):
    user_evaluation = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    c_id = models.ForeignKey(WorkloadCriteria, on_delete=models.CASCADE)
    sf_id = models.ForeignKey(wl_subfield, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_evaluation} - {self.c_id.c_name} - {self.sf_id.sf_name}"
    
class UserSelectedSubField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    f_id = models.ForeignKey(wl_field, on_delete=models.CASCADE)
    sf_id = models.ForeignKey(wl_subfield, on_delete=models.CASCADE)
    date_selected = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.sf_id.sf_name}"
    
class UserWorkloadSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    sf_id = models.ForeignKey(wl_subfield, on_delete=models.CASCADE)
    selected_id = models.ForeignKey(WorkloadCriteria, on_delete=models.PROTECT)
    selected_name = models.TextField(default="", blank=True, null=True)
    selected_num = models.FloatField(default="1", blank=True, null=True)

    # ใช้ FloatField แทน choices เพื่อดึงข้อมูลโดยตรงจาก selected_id
    selected_maxnum = models.FloatField(default="0", blank=True, null=True)
    selected_unit = models.TextField(default="", blank=True, null=True)
    selected_workload = models.FloatField(default="0", blank=True, null=True)
    calculated_workload = models.FloatField(default="0")
    selected_workload_edit = models.FloatField(default="0", blank=True, null=True)
    selected_workload_edit_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.selected_name} "

    def save(self, *args, **kwargs):
        if self.selected_id:
            # ตั้งค่า selected_maxnum, selected_unit, และ selected_workload จาก selected_id
            self.selected_maxnum = self.selected_id.c_maxnum
            self.selected_unit = self.selected_id.c_unit
            self.selected_workload = self.selected_id.c_workload

            # คำนวณค่า calculated_workload
            if self.selected_maxnum == 0:
                self.calculated_workload = self.selected_num  * self.selected_workload
            else:
                if self.selected_num <= self.selected_maxnum:
                    self.calculated_workload = self.selected_num  * self.selected_workload
                else:
                    self.calculated_workload = self.selected_maxnum  * self.selected_workload

        # เรียกใช้ฟังก์ชันบันทึกของแม่แบบ
        super().save(*args, **kwargs)

class user_evident(models.Model):
    uevd_id = models.AutoField(primary_key=True)
    uevr_id = models.ForeignKey(user_evaluation, on_delete=models.CASCADE)
    uwls_id = models.ForeignKey(UserWorkloadSelection, on_delete=models.CASCADE)
    filename = models.TextField(default="", blank=True, null=True)
    picture = models.ImageField(default="", blank=True, null=True, upload_to='uploads/')
    file = models.FileField(default="", blank=True, null=True, upload_to='uploads/')