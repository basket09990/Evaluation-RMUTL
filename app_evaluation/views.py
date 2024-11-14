from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from app_user.models import academic_type,wl_field,group_detail,Profile,group,user_evaluation_agreement,wl_subfield,user_competency_main,user_work_info,evr_round,main_competency,user_competency_main,specific_competency,user_competency_councilde,administrative_competency,user_competency_ceo,user_evaluation,user_evident
from django.http import HttpRequest, JsonResponse , HttpResponseRedirect
from django.contrib import messages 
from datetime import datetime,date
from django.urls import reverse_lazy,reverse
from app_user.models import WorkLeave,PersonalDiagram,UserWorkloadSelection,UserSelectedSubField,SelectedWorkload,SelectedSubfields,WorkloadCriteria,main_competency,Profile ,user_evaluation_score,UserMainCompetencyScore,UserAdministrativeCompetencyScore,UserSpecificCompetencyScore
from .forms import UserWorkloadSelectionForm,UserWorkInfoForm, GroupForm, GroupDetailForm, WlFieldForm ,WorkloadCriteriaForm,WlSubfieldForm ,MainCompetencyForm,SpecificCompetencyForm,AdministrativeCompetencyForm,GroupSelectionForm,UserEvaluationForm ,UserEvidentForm
from .forms import UserWorkloadSelectionForm2,UserWorkloadSelectionForm1,UserEvaluationScoreForm , SubFieldForm , SelectSubfieldForm , WorkloadCriteriaSelectionForm, SubFieldSelectionForm,PersonalDiagramForm,WorkLeaveForm
from django.utils import timezone
from app_user.forms import UserProfileForm,ExtendedProfileForm
from django.forms import modelformset_factory
import uuid
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.db.models import Max
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.template.loader import render_to_string
from django.template.loader import get_template
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph,Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from reportlab.lib.enums import TA_LEFT




# สัญญาณที่จะถูกเรียกเมื่อ UserSelectedSubField ถูกลบ
@receiver(post_delete, sender=UserSelectedSubField)
def delete_related_workload_selection(sender, instance, **kwargs):
    # ลบ UserWorkloadSelection ทั้งหมดที่มี sf_id ตรงกับที่ถูกลบ
    UserWorkloadSelection.objects.filter(
        user=instance.user,
        evaluation=instance.evaluation,
        sf_id=instance.sf_id
    ).delete()

@csrf_exempt  # ใช้เพื่อข้ามการตรวจสอบ CSRF ในกรณีที่ใช้ AJAX แบบไม่ส่งฟอร์ม
def auto_save_workload(request):
    if request.method == 'POST':
        try:
            # โหลดข้อมูลจาก body ของ request
            data = json.loads(request.body)
            selection_id = data.get('selection_id')
            selected_workload_edit_value = float(data.get('selected_workload_edit'))

            # ค้นหา UserWorkloadSelection จาก selection_id
            selection = UserWorkloadSelection.objects.get(id=selection_id)
            selection.selected_workload_edit = selected_workload_edit_value
            selection.selected_workload_edit_status = True
            selection.save()

            # ส่งสถานะความสำเร็จกลับไปยัง AJAX
            return JsonResponse({'status': 'success', 'message': 'บันทึกข้อมูลสำเร็จ!'})

        except UserWorkloadSelection.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'ไม่พบข้อมูลที่ต้องการบันทึก'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



# Views สำหรับจัดการ Group
def group_list(request):
    groups = group.objects.all()
    return render(request, 'app_evaluation/group_list.html', {'groups': groups})

def group_add(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'app_evaluation/group_form.html', {'form': form, 'action': 'เพิ่มกลุ่ม'})

def group_edit(request, pk):
    group_instance = get_object_or_404(group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group_instance)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = GroupForm(instance=group_instance)
    return render(request, 'app_evaluation/group_form.html', {'form': form, 'action': 'แก้ไขกลุ่ม'})

def group_delete(request, pk):
    group_instance = get_object_or_404(group, pk=pk)
    if request.method == 'POST':
        group_instance.delete()
        return redirect('group_list')
    return render(request, 'app_evaluation/group_confirm_delete.html', {'group': group_instance})

# Views สำหรับจัดการ GroupDetail
def group_detail_list(request, group_id):
    group_instance = get_object_or_404(group, pk=group_id)
    details = group_detail.objects.filter(g_id=group_instance)
    return render(request, 'app_evaluation/group_detail_list.html', {'group': group_instance, 'details': details})

def group_detail_add(request, group_id):
    group_instance = get_object_or_404(group, pk=group_id)

    if request.method == 'POST':
        form = GroupDetailForm(request.POST)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.g_id = group_instance
            detail.save()
            return redirect('group_detail_list', group_id=group_instance.g_id)
    else:
        form = GroupDetailForm()
    
    return render(request, 'app_evaluation/group_detail_form.html', {
        'form': form, 
        'action': 'เพิ่มรายละเอียดกลุ่ม', 
        'group': group_instance
    })

def group_detail_edit(request, pk):
    detail = get_object_or_404(group_detail, pk=pk)
    if request.method == 'POST':
        form = GroupDetailForm(request.POST, instance=detail)
        if form.is_valid():
            form.save()
            return redirect('group_detail_list', group_id=detail.g_id.g_id)
    else:
        form = GroupDetailForm(instance=detail)
    return render(request, 'app_evaluation/group_detail_form.html', {'form': form, 'action': 'แก้ไขรายละเอียดกลุ่ม', 'group': detail.g_id})

def group_detail_delete(request, pk):
    detail = get_object_or_404(group_detail, pk=pk)
    if request.method == 'POST':
        group_id = detail.g_id.g_id
        detail.delete()
        return redirect('group_detail_list', group_id=group_id)
    return render(request, 'app_evaluation/group_detail_confirm_delete.html', {'detail': detail})

# Views สำหรับ wl_field
def wl_field_list(request):
    fields = wl_field.objects.all()
    return render(request, 'app_evaluation/wl_field_list.html', {'fields': fields})

def wl_field_add(request):
    if request.method == 'POST':
        form = WlFieldForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wl_field_list')
    else:
        form = WlFieldForm()
    return render(request, 'app_evaluation/wl_field_form.html', {'form': form, 'action': 'เพิ่มกลุ่มภาระงาน'})

def wl_field_edit(request, pk):
    field = get_object_or_404(wl_field, pk=pk)
    if request.method == 'POST':
        form = WlFieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            return redirect('wl_field_list')
    else:
        form = WlFieldForm(instance=field)
    return render(request, 'app_evaluation/wl_field_form.html', {'form': form, 'action': 'แก้ไขกลุ่มภาระงาน'})

def wl_field_delete(request, pk):
    field = get_object_or_404(wl_field, pk=pk)
    if request.method == 'POST':
        field.delete()
        return redirect('wl_field_list')
    return render(request, 'app_evaluation/wl_field_confirm_delete.html', {'field': field})

# Views สำหรับ wl_subfield
def wl_subfield_list(request, pk):  # ใช้ 'pk' แทน 'field_id'
    field = get_object_or_404(wl_field, pk=pk)
    subfields = field.subfields.all()  # ใช้ related_name 'subfields' ที่กำหนดใน ForeignKey ของ wl_subfield
    return render(request, 'app_evaluation/wl_subfield_list.html', {
        'field': field,
        'subfields': subfields,
    })

def wl_subfield_add(request, field_id):
    field = get_object_or_404(wl_field, pk=field_id)
    if request.method == 'POST':
        form = WlSubfieldForm(request.POST)
        if form.is_valid():
            subfield = form.save(commit=False)
            subfield.f_id = field  # เชื่อม f_id กับ wl_field ที่ได้จาก field_id
            subfield.save()
            return redirect('wl_subfield_list', pk=field_id)  # ต้องส่ง pk ให้ครบ
    else:
        form = WlSubfieldForm()

    return render(request, 'app_evaluation/wl_subfield_form.html', {
        'form': form,
        'action': 'เพิ่มกลุ่มย่อย',
        'field': field,
        'is_edit': False
    })

def wl_subfield_edit(request, pk):
    subfield = get_object_or_404(wl_subfield, pk=pk)
    field = subfield.f_id  # เชื่อมกับ wl_field

    if request.method == 'POST':
        form = WlSubfieldForm(request.POST, instance=subfield)
        if form.is_valid():
            form.save()
            # ใช้ field.f_id.pk เพื่อส่งค่าที่ถูกต้อง
            return redirect('wl_subfield_list', pk=field.f_id)
    else:
        form = WlSubfieldForm(instance=subfield)

    return render(request, 'app_evaluation/wl_subfield_form.html', {
        'form': form,
        'action': 'แก้ไขกลุ่มย่อยภาระงาน',
        'field': field,
        'is_edit': True
    })

def wl_subfield_delete(request, pk):
    subfield = get_object_or_404(wl_subfield, pk=pk)
    field_id = subfield.f_id.pk  # ดึงค่า pk ของ wl_field ที่เกี่ยวข้อง

    if request.method == 'POST':
        subfield.delete()
        return redirect('wl_subfield_list', pk=field_id)  # ส่ง field_id กลับไป

    return render(request, 'app_evaluation/wl_subfield_confirm_delete.html', {
        'subfield': subfield
    })

# Views สำหรับ WorkloadCriteria
def workload_criteria_list(request, subfield_id):
    # ดึงข้อมูล wl_subfield ที่เกี่ยวข้อง
    subfield = get_object_or_404(wl_subfield, pk=subfield_id)

    # Query เพื่อดึง WorkloadCriteria ที่เชื่อมโยงกับ wl_subfield นี้
    criteria = WorkloadCriteria.objects.filter(sf_id=subfield)

    return render(request, 'app_evaluation/workload_criteria_list.html', {
        'subfield': subfield,
        'criteria': criteria,
    })

def workload_criteria_add(request, subfield_id):
    subfield = get_object_or_404(wl_subfield, pk=subfield_id)

    if request.method == 'POST':
        form = WorkloadCriteriaForm(request.POST)
        if form.is_valid():
            criteria = form.save(commit=False)
            criteria.sf_id = subfield  # เชื่อมกับ wl_subfield

            # ตรวจสอบว่ามีค่า f_id หรือไม่ ถ้าไม่มีกำหนดค่าให้ f_id
            if not criteria.f_id_id:  # ถ้ายังไม่มีการตั้งค่า f_id
                # สามารถตั้งค่า f_id ได้ เช่น:
                default_field = wl_field.objects.first()  # ดึงค่า wl_field แรกจากฐานข้อมูล
                if default_field:
                    criteria.f_id = default_field
                else:
                    # กรณีที่ไม่มี wl_field ในฐานข้อมูลเลย
                    messages.error(request, "ไม่พบข้อมูลฟิลด์ที่ถูกต้องในระบบ กรุณาตรวจสอบ")
                    return render(request, 'app_evaluation/workload_criteria_form.html', {
                        'form': form,
                        'subfield': subfield,
                        'action': 'เพิ่มเกณฑ์ภาระงาน',
                        'is_edit': False,
                        'subfield_id': subfield_id,  # ส่ง subfield_id ไปยัง template
                    })

            criteria.save()
            return redirect('workload_criteria_list', subfield_id=subfield.pk)  # ใช้ subfield.pk ที่ถูกต้อง
    else:
        form = WorkloadCriteriaForm()

    return render(request, 'app_evaluation/workload_criteria_form.html', {
        'form': form,
        'subfield': subfield,
        'action': 'เพิ่มเกณฑ์ภาระงาน',
        'is_edit': False,
        'subfield_id': subfield_id,  # ส่ง subfield_id ไปยัง template
    })

def workload_criteria_edit(request, pk):
    criteria = get_object_or_404(WorkloadCriteria, pk=pk)
    subfield_id = criteria.sf_id.sf_id  # ตรวจสอบให้แน่ใจว่าได้ subfield_id ที่ถูกต้อง

    if request.method == 'POST':
        form = WorkloadCriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            form.save()
            return redirect('workload_criteria_list', subfield_id=subfield_id)  # ส่ง subfield_id กลับไปใน redirect
    else:
        form = WorkloadCriteriaForm(instance=criteria)

    return render(request, 'app_evaluation/workload_criteria_form.html', {
        'form': form,
        'action': 'แก้ไขเกณฑ์ภาระงาน',
        'subfield_id': subfield_id,  # ส่ง subfield_id ไปยังเทมเพลต
        'is_edit': True,  # บอกว่าเป็นการแก้ไข
    })

def workload_criteria_delete(request, pk):
    criteria = get_object_or_404(WorkloadCriteria, pk=pk)

    if request.method == 'POST':
        subfield_id = criteria.sf_id.sf_id  # เก็บ subfield_id จาก criteria
        criteria.delete()
        # ส่ง subfield_id ใน redirect ให้ถูกต้อง
        return redirect('workload_criteria_list', subfield_id=subfield_id)

    return render(request, 'app_evaluation/workload_criteria_confirm_delete.html', {
        'criteria': criteria
    })

# แสดงรายการ main_competency
def list_main_competency(request):
    competencies = main_competency.objects.all()
    return render(request, 'app_evaluation/list_main_competency.html', {'competencies': competencies})

def add_main_competency(request):
    if request.method == 'POST':
        form = MainCompetencyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มข้อมูลสำเร็จ!")
            return redirect('list_main_competency')
    else:
        form = MainCompetencyForm()
    
    return render(request, 'app_evaluation/add_main_competency.html', {'form': form})

# แก้ไขข้อมูล
def edit_main_competency(request, mc_id):
    competency = get_object_or_404(main_competency, mc_id=mc_id)
    if request.method == 'POST':
        form = MainCompetencyForm(request.POST, instance=competency)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขข้อมูลสำเร็จ!")
            return redirect('list_main_competency')
    else:
        form = MainCompetencyForm(instance=competency)

    return render(request, 'app_evaluation/edit_main_competency.html', {'form': form, 'competency': competency})

# ลบข้อมูล
def delete_main_competency(request, mc_id):
    competency = get_object_or_404(main_competency, mc_id=mc_id)
    if request.method == 'POST':
        competency.delete()
        messages.success(request, "ลบข้อมูลสำเร็จ!")
        return redirect('list_main_competency')

    return render(request, 'app_evaluation/delete_main_competency.html', {'competency': competency})

# แสดงรายการ specific_competency
def list_specific_competency(request):
    competencies = specific_competency.objects.all()
    return render(request, 'app_evaluation/list_specific_competency.html', {'competencies': competencies})

# เพิ่มข้อมูล
def add_specific_competency(request):
    if request.method == 'POST':
        form = SpecificCompetencyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มข้อมูลสำเร็จ!")
            return redirect('list_specific_competency')
    else:
        form = SpecificCompetencyForm()
    
    return render(request, 'app_evaluation/add_specific_competency.html', {'form': form})

# แก้ไขข้อมูล
def edit_specific_competency(request, sc_id):
    competency = get_object_or_404(specific_competency, sc_id=sc_id)
    if request.method == 'POST':
        form = SpecificCompetencyForm(request.POST, instance=competency)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขข้อมูลสำเร็จ!")
            return redirect('list_specific_competency')
    else:
        form = SpecificCompetencyForm(instance=competency)

    return render(request, 'app_evaluation/edit_specific_competency.html', {'form': form, 'competency': competency})

# ลบข้อมูล
def delete_specific_competency(request, sc_id):
    competency = get_object_or_404(specific_competency, sc_id=sc_id)
    if request.method == 'POST':
        competency.delete()
        messages.success(request, "ลบข้อมูลสำเร็จ!")
        return redirect('list_specific_competency')

    return render(request, 'app_evaluation/delete_specific_competency.html', {'competency': competency})

# แสดงรายการ administrative_competency
def list_administrative_competency(request):
    competencies = administrative_competency.objects.all()
    return render(request, 'app_evaluation/list_administrative_competency.html', {'competencies': competencies})

# เพิ่มข้อมูล
def add_administrative_competency(request):
    if request.method == 'POST':
        form = AdministrativeCompetencyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มข้อมูลสำเร็จ!")
            return redirect('list_administrative_competency')
    else:
        form = AdministrativeCompetencyForm()
    
    return render(request, 'app_evaluation/add_administrative_competency.html', {'form': form})

# แก้ไขข้อมูล
def edit_administrative_competency(request, adc_id):
    competency = get_object_or_404(administrative_competency, adc_id=adc_id)
    if request.method == 'POST':
        form = AdministrativeCompetencyForm(request.POST, instance=competency)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขข้อมูลสำเร็จ!")
            return redirect('list_administrative_competency')
    else:
        form = AdministrativeCompetencyForm(instance=competency)

    return render(request, 'app_evaluation/edit_administrative_competency.html', {'form': form, 'competency': competency})

# ลบข้อมูล
def delete_administrative_competency(request, adc_id):
    competency = get_object_or_404(administrative_competency, adc_id=adc_id)
    if request.method == 'POST':
        competency.delete()
        messages.success(request, "ลบข้อมูลสำเร็จ!")
        return redirect('list_administrative_competency')

    return render(request, 'app_evaluation/delete_administrative_competency.html', {'competency': competency})

@login_required
def score(request):
    return render(request,'app_evaluation/score.html')

@login_required
def score0(request):
    return render(request,'app_evaluation/score0.html')

# ฟังก์ชันเพื่อดึงข้อมูลรอบการประเมิน
def get_evr_round():
    current_date = timezone.now().date()
    current_month = current_date.month
    current_year = current_date.year

    if 10 <= current_month <= 12:
        # รอบแรก (ปลายปี)
        round_number = 1
        evr_year = current_year
        start_date = date(current_year, 10, 1)  # 1 ตุลาคมของปีปัจจุบัน
        end_date = date(current_year + 1, 3, 31)  # 31 มีนาคมของปีถัดไป
    elif 1 <= current_month <= 3:
        # รอบแรก (ต้นปีถัดไป)
        round_number = 1
        evr_year = current_year - 1
        start_date = date(current_year - 1, 10, 1)  # 1 ตุลาคมของปีที่ผ่านมา
        end_date = date(current_year, 3, 31)  # 31 มีนาคมของปีปัจจุบัน
    else:
        # รอบสอง (กลางปี)
        round_number = 2
        evr_year = current_year - 1
        start_date = date(current_year, 4, 1)  # 1 เมษายน
        end_date = date(current_year, 9, 30)  # 30 กันยายน

    # อัปเดตหรือสร้างรอบการประเมิน
    evr_round_obj, created = evr_round.objects.get_or_create(
        evr_year=evr_year,
        evr_round=round_number,
        defaults={'start_date': start_date, 'end_date': end_date}
    )

    # อัปเดต end_date หากมีการเปลี่ยนแปลง (ถ้าเป็นการอัปเดตค่าเดิม)
    if not created:
        evr_round_obj.end_date = end_date
        evr_round_obj.save()

    return evr_round_obj

@login_required
def search_evaluation(request):
    # ดึงเฉพาะ evaluation ที่เชื่อมกับผู้ใช้ที่ล็อกอินอยู่ และเรียงลำดับจากใหม่ไปเก่า
    evaluations = user_evaluation.objects.filter(user=request.user).order_by('-uevr_id')
    
    query = request.GET.get('query', '')
    year = request.GET.get('year', '')
    round = request.GET.get('round', '')

    # กรองตามคำค้นหาชื่อผู้ใช้ ถ้ามีการป้อนข้อมูล
    if query:
        evaluations = evaluations.filter(user__username__icontains=query)
    
    # กรองตามปี ถ้ามีการป้อนข้อมูล
    if year:
        evaluations = evaluations.filter(evr_id__evr_year=year)
    
    # กรองตามรอบ ถ้ามีการป้อนข้อมูล
    if round:
        evaluations = evaluations.filter(evr_id__evr_round=round)

    # ตรวจสอบวันที่ปัจจุบันกับ end_date ของ evr_round และอัพเดตสถานะ
    current_date = timezone.now().date()
    for evaluation in evaluations:
        evr_round_obj = evaluation.evr_id
        
        # ถ้า end_date เกิน current_date ให้เปลี่ยนสถานะเป็น True
        if evr_round_obj.end_date and current_date > evr_round_obj.end_date:
            if not evr_round_obj.evr_status:  # ตรวจสอบสถานะก่อนว่าเป็น False อยู่หรือไม่
                evr_round_obj.evr_status = True  # หมดเวลา: เปลี่ยนสถานะเป็น True
                evr_round_obj.save()
               
    # ดึงปีและรอบทั้งหมดเพื่อนำไปใช้ในตัวเลือก
    years = evaluations.values_list('evr_id__evr_year', flat=True).distinct()
    rounds = evaluations.values_list('evr_id__evr_round', flat=True).distinct()

    context = {
        'evaluations': evaluations,
        'query': query,
        'years': years,
        'rounds': rounds,
    }
    
    return render(request, 'app_evaluation/search_evaluations.html', context)

@login_required
def evaluation_page1(request, evaluation_id):
     # ดึงข้อมูล user_evaluation โดยไม่สนใจ request.user
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    evr_round_obj = evaluation.evr_id  # Get the current evaluation round from user_evaluation

    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user, evr_id=evr_round_obj).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    # ดึงข้อมูลการปฏิบัติงานของผู้ใช้
    user_work_info_obj, created = user_work_info.objects.get_or_create(
        user=evaluation.user,
        round=evr_round_obj,
        defaults={'punishment': ''}
    )
    work_form_current = UserWorkInfoForm(instance=user_work_info_obj)

    # สร้างฟอร์มโปรไฟล์และการปฏิบัติงาน
    profile_form = UserProfileForm(instance=evaluation.user)
    extended_form = ExtendedProfileForm(instance=profile)

    # ฟังก์ชันสำหรับดึงข้อมูลการลา
    def get_or_create_leave(user, round_obj, leave_type):
        leave, _ = WorkLeave.objects.get_or_create(
            user=user,
            round=round_obj,
            leave_type=leave_type,
            defaults={'times': 0, 'days': 0}
        )
        return leave

    # ตรวจสอบรอบที่ 1 (หากมีข้อมูล)
    round_1 = evr_round.objects.filter(
        evr_round=1, evr_year=(evr_round_obj.evr_year - 1 if evr_round_obj.evr_round == 2 else evr_round_obj.evr_year)
    ).first()

    # ดึงข้อมูลการลาของรอบที่ 1 และรอบปัจจุบัน
    sick_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'SL') if round_1 else None
    sick_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'SL'), prefix='sick_leave')
    
    personal_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'PL') if round_1 else None
    personal_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'PL'), prefix='personal_leave')

    late_round_1 = get_or_create_leave(evaluation.user, round_1, 'LT') if round_1 else None
    late_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'LT'), prefix='late')

    maternity_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'ML') if round_1 else None
    maternity_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'ML'), prefix='maternity_leave')

    ordination_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'OL') if round_1 else None
    ordination_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'OL'), prefix='ordination_leave')

    longsick_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'LSL') if round_1 else None
    longsick_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'LSL'), prefix='longsick_leave')

    adsent_work_round_1 = get_or_create_leave(evaluation.user, round_1, 'AW') if round_1 else None
    adsent_work_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'AW'), prefix='adsent_work')

    # ฟอร์มสำหรับรอบที่ 1 และรอบปัจจุบัน
    round_1_forms = {
        'sick_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=sick_leave_round_1, prefix='sick_leave_round_1') if round_1 else None,
        'personal_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=personal_leave_round_1, prefix='personal_leave_round_1') if round_1 else None,
        'late_round_1_form': WorkLeaveForm(request.POST or None, instance=late_round_1, prefix='late_round_1') if round_1 else None,
        'maternity_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=maternity_leave_round_1, prefix='maternity_leave_round_1') if round_1 else None,
        'ordination_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=ordination_leave_round_1, prefix='ordination_leave_round_1') if round_1 else None,
        'longsick_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=longsick_leave_round_1, prefix='longsick_leave_round_1') if round_1 else None,
        'adsent_work_round_1_form': WorkLeaveForm(request.POST or None, instance=adsent_work_round_1, prefix='adsent_work_round_1') if round_1 else None
    }

    # จัดการการบันทึกข้อมูลฟอร์ม
    if request.method == 'POST':
        # ตรวจสอบข้อมูลทุกฟอร์ม
        profile_form = UserProfileForm(request.POST, instance=evaluation.user)
        extended_form = ExtendedProfileForm(request.POST, instance=profile)
        work_form_current = UserWorkInfoForm(request.POST, instance=user_work_info_obj)

        # ฟอร์มทั้งหมดที่จะตรวจสอบความถูกต้อง
        current_round_forms = [sick_leave_form, personal_leave_form, late_form, maternity_leave_form, ordination_leave_form, longsick_leave_form, adsent_work_form]
        all_forms = [profile_form, extended_form, work_form_current] + current_round_forms + list(round_1_forms.values())

        if all(form.is_valid() for form in all_forms if form is not None):
            # บันทึกข้อมูลทุกฟอร์ม
            profile_form.save()
            extended_form.save()
            work_form_current.save()
            
            for form in current_round_forms:
                form.save()

            for form in round_1_forms.values():
                if form:
                    form.save()

            messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
            return redirect('evaluation_page_from_1', evaluation_id=evaluation_id)
        else:
            messages.error(request, "มีข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลอีกครั้ง")

    # เตรียมข้อมูลเพื่อส่งไปแสดงผล
    context = {
        'profile_form': profile_form,
        'extended_form': extended_form,
        'work_form_current': work_form_current,
        'evr_round': evr_round_obj,
        'profile': profile,
        'selected_group': selected_group,
        'sick_leave_form': sick_leave_form,
        'personal_leave_form': personal_leave_form,
        'late_form': late_form,
        'maternity_leave_form': maternity_leave_form,
        'ordination_leave_form': ordination_leave_form,
        'longsick_leave_form': longsick_leave_form,
        'adsent_work_form': adsent_work_form,
        # ฟอร์มรอบที่ 1 ถ้ามี
        **round_1_forms,
        'evaluation_id': evaluation_id,
        'user_evaluation_agreement_year_thai': user_evaluation_agreement_obj.year + 543 if user_evaluation_agreement_obj else None,
        'user_evaluation_agreement': user_evaluation_agreement_obj,
        'user_evaluation': evaluation,
    }

    return render(request, 'app_evaluation/evaluation_page1.html', context)

@login_required
def evaluation_page2(request, evaluation_id):
    # ดึงข้อมูล user_evaluation โดยไม่สนใจ request.user
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    evr_round_obj = evaluation.evr_id

    # ดึงข้อมูล profile
    profile = evaluation.user.profile

    # ดึง selected_group ที่สัมพันธ์กับ user ผ่าน user_evaluation_agreement
    try:
        user_evaluation_agreement_obj = user_evaluation_agreement.objects.get(user=evaluation.user, evr_id=evr_round_obj)
        selected_group = user_evaluation_agreement_obj.g_id
    except user_evaluation_agreement.DoesNotExist:
        selected_group = None

    # ดึงข้อมูล f_id ที่เชื่อมโยงกับ group_detail ของ selected_group
    if selected_group:
        fields = wl_field.objects.filter(group_detail__g_id=selected_group).distinct()
    else:
        fields = wl_field.objects.none()

    # ดึงข้อมูล subfields ที่ผู้ใช้เลือก
    selected_subfields = UserSelectedSubField.objects.filter(evaluation=evaluation)

    # ดึงข้อมูล subfields ที่เกี่ยวข้องกับ fields ที่ได้เลือก
    subfields = wl_subfield.objects.filter(f_id__in=fields)

    # ดึงข้อมูล workload_selections ที่เชื่อมโยงกับ subfields
    workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation, sf_id__in=subfields)


    if request.method == 'POST':
        if 'save_form' in request.POST:
            selection_id = request.POST.get('save_form')
            
            
            # ดึง selection ที่ตรงกับ selection_id
            selection = UserWorkloadSelection.objects.get(id=selection_id)
            selection.selected_workload_edit = selection.calculated_workload
            selection.save()

            messages.success(request, 'บันทึกข้อมูลสำเร็จ')
            return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

        elif 'edit_form' in request.POST:
            selection_id = request.POST.get('edit_form')
            selected_workload_edit_value = request.POST.get(f'selected_workload_edit_{selection_id}')
            # ดำเนินการสำหรับการแก้ไข
            
            selection = UserWorkloadSelection.objects.get(id=selection_id)
            selection.selected_workload_edit_status = True
            selection.selected_workload_edit = selected_workload_edit_value
            selection.save()

            messages.info(request, 'แก้ไขข้อมูลสำเร็จ')
            return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

    else:
        forms = [UserWorkloadSelectionForm2(instance=selection) for selection in workload_selections]
        
        # สร้าง dictionary ที่จับคู่ selection กับ form
        forms_dict = {selection.id: form for selection, form in zip(workload_selections, forms)}

    # คำนวณค่า min_workload จากข้อมูล group
    min_workload = group.objects.filter(g_id=selected_group.g_id).values_list('g_max_workload', flat=True).first()
    if not min_workload:
        min_workload = 35  # ตั้งค่า default ถ้าไม่มีข้อมูล

    # คำนวณผลรวมของ calculated_workload
    total_workload = sum(selection.calculated_workload for selection in workload_selections) if workload_selections else 0

    # ดึง c_wl ที่สูงที่สุดจาก user_evaluation
    max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0

    # คำนวณส่วนต่างคะแนนภาระงาน
    workload_difference = max_workload - total_workload
    workload_difference_score = workload_difference * (28 / 115)
    achievement_work = 70 - workload_difference_score

    # บันทึกค่าที่คำนวณใน evaluation
    evaluation.c_wl = total_workload
    evaluation.achievement_work = round(achievement_work, 1)
    evaluation.save()


    # ส่ง context ไปยังเทมเพลต
    context = {
        'user_evaluation': evaluation,
        'fields': fields,
        'selected_subfields': selected_subfields,
        'workload_selections': workload_selections,
        'subfields': subfields,
        'total_workload': total_workload,
        'achievement_work': evaluation.achievement_work,
        'evaluation_id': evaluation_id,
        'min_workload': min_workload,
        'user_evaluation_agreement_year_thai': user_evaluation_agreement_obj.year + 543 if user_evaluation_agreement_obj else None,
        'forms': forms,  # ส่งฟอร์มไปยังเทมเพลต
        'forms_dict': forms_dict,

    }

    return render(request, 'app_evaluation/evaluation_page2.html', context)

@login_required
def select_subfields2(request, f_id, evaluation_id):
    field = get_object_or_404(wl_field, pk=f_id)
    subfields = wl_subfield.objects.filter(f_id=field)

    # ดึงข้อมูลการประเมินที่สอดคล้องกับ evaluation_id
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    if request.method == 'POST':
        selected_sf_id = request.POST.get('sf_id')  # ใช้ get() เพื่อดึงค่า sf_id จากฟอร์ม
        if selected_sf_id:
            selected_sf = wl_subfield.objects.get(sf_id=selected_sf_id)
            # เพิ่มข้อมูล evaluation เข้าไปในการสร้าง UserSelectedSubField
            UserSelectedSubField.objects.create(
                user=request.user,
                evaluation=evaluation,  # เชื่อม evaluation
                f_id=field,
                sf_id=selected_sf
            )
            return redirect('evaluation_page2', evaluation_id=evaluation_id)

    context = {
        'field': field,
        'subfields': subfields,
        'evaluation_id': evaluation_id,
    }
    return render(request, 'app_evaluation/select_subfields2.html', context)

@login_required
def delete_selected_subfield2(request, sf_id):
    # ตรวจสอบว่ามีการส่ง evaluation_id มาหรือไม่
    evaluation_id = request.POST.get('evaluation_id') or request.GET.get('evaluation_id')
    if not evaluation_id:
        messages.error(request, "ไม่พบ evaluation_id")
        return redirect('select_group')

    try:
        # ลบข้อมูลทั้งหมดใน UserSelectedSubField ที่มี sf_id
        selected_subfields = UserSelectedSubField.objects.filter(sf_id=sf_id)

        if not selected_subfields.exists():
            messages.error(request, 'ไม่พบ Subfield ที่คุณพยายามจะลบ.')
            return redirect('evaluation_page2', evaluation_id=evaluation_id)

        if request.method == 'POST':
            # ลบข้อมูลที่ค้นหาได้ทั้งหมด
            selected_subfields.delete()
            messages.success(request, 'ลบ Subfield เรียบร้อยแล้ว!')
            return redirect('evaluation_page2', evaluation_id=evaluation_id)

    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
        return redirect('evaluation_page2', evaluation_id=evaluation_id)

    return redirect('evaluation_page2', evaluation_id=evaluation_id)

@login_required
def select_workload_criteria2(request, evaluation_id, sf_id):
    # ดึงข้อมูล evaluation และ subfield ที่เกี่ยวข้อง
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    subfield = get_object_or_404(wl_subfield, pk=sf_id)
    
    # สร้างฟอร์มและส่งค่า subfield ไปยังฟอร์มเพื่อกรองข้อมูลใน selected_id
    criteria_form = UserWorkloadSelectionForm(initial={'sf_id': subfield}, subfield=subfield)

    # ตรวจสอบการส่งฟอร์ม
    if request.method == 'POST':
        criteria_form = UserWorkloadSelectionForm(request.POST, subfield=subfield)
        if criteria_form.is_valid():
            new_criteria = criteria_form.save(commit=False)
            new_criteria.sf_id = subfield
            new_criteria.evaluation = evaluation
            new_criteria.user = request.user

            try:
                # แปลงค่าทั้งหมดเป็น float ก่อนทำการคำนวณ
                selected_num = float(new_criteria.selected_num )
                selected_maxnum = float(new_criteria.selected_maxnum )
                selected_workload = float(new_criteria.selected_workload )

                # คำนวณค่า calculated_workload
                if selected_maxnum == 0:
                    calculated_workload = selected_num * selected_workload
                else:
                    if selected_num <= selected_maxnum:
                        calculated_workload = selected_num * selected_workload
                    else:
                        calculated_workload = selected_maxnum* selected_workload

                # แสดงข้อมูลการคำนวณใน log
                print(f"selected_num: {selected_num}, selected_maxnum: {selected_maxnum}, selected_workload: {selected_workload}")
                print(f"calculated_workload: {calculated_workload}")

                # บันทึกค่า calculated_workload ลงใน new_criteria
                new_criteria.calculated_workload = calculated_workload
                new_criteria.save()

                messages.success(request, f'เพิ่มภาระงานใหม่เรียบร้อยแล้ว! คำนวณภาระงาน: {calculated_workload:.2f}')
                return redirect('evaluation_page2', evaluation_id=evaluation_id)

            except ValueError as e:
                # ถ้ามีข้อผิดพลาดในการแปลงค่า แสดงใน log
                print(f"ValueError: {e}")
                messages.error(request, 'ไม่สามารถคำนวณค่าได้ โปรดตรวจสอบข้อมูลที่กรอก.')

    # ส่งข้อมูลไปยังเทมเพลต
    context = {
        'evaluation': evaluation,
        'subfield': subfield,
        'criteria_form': criteria_form,
    }
    return render(request, 'app_evaluation/select_workload_criteria2.html', context)

@login_required
def edit_workload_selection2(request, selection_id):
    selection = get_object_or_404(UserWorkloadSelection, pk=selection_id)

    if request.method == 'POST':
        form = UserWorkloadSelectionForm1(request.POST, instance=selection)

        if form.is_valid():
            # ถ้าฟอร์มถูกต้อง ให้บันทึกการเปลี่ยนแปลง
            if selection.selected_maxnum == 0:
                selection.calculated_workload = selection.selected_num * selection.selected_workload
            else:
                if selection.selected_num <= selection.selected_maxnum:
                    selection.calculated_workload = selection.selected_num * selection.selected_workload
                else:
                    selection.calculated_workload = selection.selected_maxnum  * selection.selected_workload
            form.save()
            messages.success(request, 'แก้ไขภาระงานเรียบร้อยแล้ว!')
            return redirect('evaluation_page2', evaluation_id=selection.evaluation.uevr_id)
        else:
            messages.error(request, 'กรุณาเลือกข้อมูลภาระงานให้ครบถ้วน.')
    else:
        form = UserWorkloadSelectionForm1(instance=selection)

    return render(request, 'app_evaluation/edit_workload_selection2.html', {
        'form': form,
        'selection': selection,
    })

@login_required
def delete_workload_selection2(request, selection_id):
    selection = get_object_or_404(UserWorkloadSelection, pk=selection_id)

    if request.method == 'POST':
        # ลบเฉพาะการเชื่อมโยงกับ UserWorkloadSelection
        selection.delete()  
        messages.success(request, 'ลบภาระงานเรียบร้อยแล้ว!')
        return redirect('evaluation_page2', evaluation_id=selection.evaluation.uevr_id)

    return render(request, 'app_evaluation/confirm_delete2.html', {
        'selection': selection,
    })

@login_required
def upload_evidence1(request, criteria_id):
    # ดึงข้อมูล WorkloadCriteria โดยใช้ criteria_id
    criteria = get_object_or_404(UserWorkloadSelection, pk=criteria_id)
    evaluation = criteria.evaluation  # ดึงค่า evaluation จาก UserWorkloadSelection

    if request.method == 'POST':
        form = UserEvidentForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        pictures = request.FILES.getlist('picture')

        if form.is_valid():
            # บันทึกไฟล์ PDF และ DOCX
            for file in files:
                new_filename = f"{uuid.uuid4()}_{file.name}"
                evidence = user_evident(
                    uwls_id=criteria,  # ตั้งค่า uwls_id ด้วย instance ของ UserWorkloadSelection
                    uevr_id=evaluation,  # ตั้งค่า uevr_id ด้วย instance ของ UserEvaluation
                    file=file,
                    filename=new_filename
                )
                evidence.save()

            # ลดขนาดรูปภาพก่อนบันทึก
            for picture in pictures:
                new_filename = f"{uuid.uuid4()}_{picture.name}"
                image = Image.open(picture)

                # ลดขนาดรูปภาพ
                max_size = (1366, 800)  # ขนาดที่ต้องการ
                image.thumbnail(max_size)

                # บันทึกรูปภาพที่ลดขนาด
                img_io = ContentFile(b'')
                image_format = image.format or 'JPEG'
                image.save(img_io, format=image_format)

                # บันทึกไฟล์ลงใน storage
                file_name = default_storage.save(f"uploads/{new_filename}", img_io)
                evidence = user_evident(
                    uwls_id=criteria,  # ตั้งค่า uwls_id ด้วย instance ของ UserWorkloadSelection
                    uevr_id=evaluation,  # ตั้งค่า uevr_id ด้วย instance ของ UserEvaluation
                    picture=file_name,
                    filename=new_filename
                )
                evidence.save()

            messages.success(request, "อัปโหลดไฟล์เรียบร้อยแล้ว!")
            return redirect('upload_evidence1', criteria_id=criteria_id)

    else:
        form = UserEvidentForm()

    # แสดงรายการไฟล์ที่อัปโหลด
    evidences = user_evident.objects.filter(uwls_id=criteria)

    return render(request, 'app_evaluation/upload_evidence1.html', {
        'form': form,
        'evaluation': evaluation,
        'evidences': evidences  # ส่งรายการไฟล์/รูปภาพไปยัง template
    })

@login_required
def delete_evidence1(request, evidence_id):
    evidence = get_object_or_404(user_evident, uevd_id=evidence_id)

    # ลบไฟล์หรือรูปภาพที่เกี่ยวข้องจากระบบ
    if evidence.file:
        if os.path.isfile(evidence.file.path):
            os.remove(evidence.file.path)  # ลบไฟล์จาก storage
    if evidence.picture:
        if os.path.isfile(evidence.picture.path):
            os.remove(evidence.picture.path)  # ลบรูปภาพจาก storage

    # ลบรายการ evidence จากฐานข้อมูล
    evidence.delete()
    messages.success(request, "ลบไฟล์/รูปภาพเรียบร้อยแล้ว!")
    
    # ใช้ `redirect` ให้ไปยัง `upload_evidence` โดยใช้ `criteria_id`
    return redirect('upload_evidence1', criteria_id=evidence.uwls_id.id)  # เปลี่ยน `evaluation_id` เป็น `criteria_id`

def calculate_competency_score(actual_score, expected_score):
    # ตรวจสอบว่า actual_score และ expected_score ไม่ใช่ None
    if actual_score is None or expected_score is None:
        return 0

    # คำนวณความแตกต่างระหว่าง actual_score (คะแนนที่กรอก) และ expected_score (ระดับที่คาดหวัง)
    difference = expected_score - actual_score

    if difference <= 0:  # สมรรถนะที่แสดงออก >= คาดหวัง
        return 3  # คูณด้วย 3 คะแนน
    elif difference == 1:  # ต่ำกว่าคาดหวัง 1 ระดับ
        return 2  # คูณด้วย 2 คะแนน
    elif difference == 2:  # ต่ำกว่าคาดหวัง 2 ระดับ
        return 1  # คูณด้วย 1 คะแนน
    else:  # ต่ำกว่าคาดหวัง 3 ระดับหรือมากกว่า
        return 0  # คูณด้วย 0 คะแนน

@login_required
def evaluation_page3(request, evaluation_id):
# ดึงข้อมูล user_evaluation
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    

    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    main_competencies = main_competency.objects.filter(mc_type=evaluation.ac_id.ac_name)
    specific_competencies = specific_competency.objects.filter(sc_type=evaluation.ac_id.ac_name)
    administrative_competencies = None  # ตั้งค่าเริ่มต้นเป็น None
    
    # เช็คว่าถ้ามีตำแหน่งบริหารและไม่ใช่ "-"
    if evaluation.administrative_position and evaluation.administrative_position != "-":
        administrative_competencies = administrative_competency.objects.filter()

    # ตรวจสอบการส่งข้อมูล POST
    if request.method == 'POST':
        # วนลูปผ่าน main_competencies
        for competency in main_competencies:
            actual_score = request.POST.get(f'main_actual_score_{competency.mc_id}')
            if actual_score and actual_score.isdigit():
                actual_score = int(actual_score)
                user_competency_main.objects.update_or_create(
                    evaluation=evaluation,
                    mc_id=competency,
                  
                    defaults={'user': evaluation.user, 'umc_name': competency.mc_name, 'umc_type': competency.mc_type, 'actual_score': actual_score}
                )

        # วนลูปผ่าน specific_competencies
        for competency in specific_competencies:
            actual_score = request.POST.get(f'specific_actual_score_{competency.sc_id}')
            if actual_score and actual_score.isdigit():
                actual_score = int(actual_score)
                user_competency_councilde.objects.update_or_create(
                    evaluation=evaluation,
                    sc_id=competency,
                   
                    defaults={'user': evaluation.user, 'ucc_name': competency.sc_name, 'ucc_type': competency.sc_type, 'actual_score': actual_score}
                )

        # วนลูปผ่าน administrative_competencies
        if administrative_competencies is not None:
            for competency in administrative_competencies:
                actual_score = request.POST.get(f'admin_actual_score_{competency.adc_id}')
                uceo_num = request.POST.get(f'admin_uceo_num_{competency.adc_id}') 
                if actual_score and actual_score.isdigit():
                    actual_score = int(actual_score)
                    uceo_num = int(uceo_num) if uceo_num.isdigit() else 0
                    user_competency_ceo.objects.update_or_create(
                        evaluation=evaluation,
                        adc_id=competency,
                        
                        defaults={'user': evaluation.user, 'uceo_name': competency.adc_name, 'uceo_type': competency.adc_type, 'actual_score': actual_score,'uceo_num': uceo_num}
                    )

        messages.success(request, "บันทึกคะแนนเรียบร้อยแล้ว!")
        return redirect('evaluation_page_from_3', evaluation_id=evaluation_id)

    # ดึงข้อมูลคะแนนที่เคยกรอก
    main_scores = user_competency_main.objects.filter(evaluation=evaluation)
    specific_scores = user_competency_councilde.objects.filter(evaluation=evaluation)
    administrative_scores = user_competency_ceo.objects.filter(evaluation=evaluation)

    # เก็บจำนวนสมรรถนะที่ได้คะแนนตามเงื่อนไขต่าง ๆ
    score_count = {3: 0, 
                   2: 0, 
                   1: 0, 
                   0: 0}

    # คำนวณคะแนนสำหรับ main competencies
    main_competency_total = 0
    for score in main_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.mc_id.mc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        main_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ specific competencies
    specific_competency_total = 0
    for score in specific_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.sc_id.sc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        specific_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ administrative competencies (ถ้ามี)
    administrative_competency_total = 0
    if administrative_competencies is not None:
        for score in administrative_scores:
            calculated_score = calculate_competency_score(score.actual_score, score.uceo_num)
            score_count[calculated_score] += 1
            administrative_competency_total += calculated_score

    # ผลรวมคะแนนทั้งหมด
    total_score = main_competency_total + specific_competency_total + administrative_competency_total

    # คำนวณคะแนนในแต่ละกรณี (คูณ 3, 2, 1 และ 0)
    score_3_total = score_count[3] * 3
    score_2_total = score_count[2] * 2
    score_1_total = score_count[1] * 1
    score_0_total = score_count[0] * 0

    # คำนวณค่ารวมของคะแนนที่คาดหวังสำหรับแต่ละตาราง
    main_max_num = sum([c.mc_num for c in main_competencies])
    specific_max_num = sum([c.sc_num for c in specific_competencies])
    administrative_max_num = sum([score.uceo_num for score in administrative_scores]) if administrative_competencies is not None else 0

    # คำนวณคะแนนจากสูตร
    total_max_num = main_max_num + specific_max_num + administrative_max_num

    if total_max_num > 0:
        calculated_score = (total_score / total_max_num) * 30
    print(f"Total Score: {total_score}")
    print(f"Total Max Num: {total_max_num}")
    # บันทึก calculated_score ใน mc_score ของ user_evaluation
    evaluation.mc_score = calculated_score  # บันทึกคะแนนที่คำนวณได้
    evaluation.save()  # บันทึกการเปลี่ยนแปลงลงในฐานข้อมูล


    # ส่งข้อมูลไปยังเทมเพลต
    context = {
        'profile': profile,
        'main_competencies': main_competencies,
        'specific_competencies': specific_competencies,
        'administrative_competencies': administrative_competencies,
        'main_scores': main_scores,
        'specific_scores': specific_scores,
        'administrative_scores': administrative_scores,
        'main_competency_total': main_competency_total,
        'specific_competency_total': specific_competency_total,
        'administrative_competency_total': administrative_competency_total,
        'total_score': total_score,
        'total_max_num': total_max_num,
        'main_max_num': main_max_num,
        'specific_max_num': specific_max_num,
        'administrative_max_num': administrative_max_num,
        'calculated_score': calculated_score,
        'evaluation_id': evaluation_id,
        'user_evaluation_obj': evaluation,
        'ac_name': evaluation.ac_id.ac_name,
        'count_3': score_count[3],
        'count_2': score_count[2],
        'count_1': score_count[1],
        'count_0': score_count[0],
        'score_3_total': score_count[3] * 3,
        'score_2_total': score_count[2] * 2,
        'score_1_total': score_count[1] * 1,
        'score_0_total': score_count[0] * 0,
        'user_evaluation_obj': evaluation,
    }

    return render(request, 'app_evaluation/evaluation_page3.html', context)

@login_required
def evaluation_page4(request, evaluation_id):
# ดึงข้อมูล user_evaluation
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)


    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    # ตรวจสอบการร้องขอจากผู้ใช้
    if request.method == 'POST':
        # ดึงข้อมูลจากฟอร์มที่ถูกส่งมา
        remark_achievement = request.POST.get('remark_achievement')
        remark_mc = request.POST.get('remark_mc')
        remark_other = request.POST.get('remark_other')
        remark_total = request.POST.get('remark_total')

        # บันทึกข้อมูลหมายเหตุ
        evaluation.remark_achievement = remark_achievement
        evaluation.remark_mc = remark_mc
        evaluation.remark_other = remark_other
        evaluation.remark_total = remark_total

        evaluation.save()  # บันทึกการเปลี่ยนแปลง

        messages.success(request, 'บันทึกหมายเหตุเรียบร้อยแล้ว!')
        return redirect('evaluation_page_from_4', evaluation_id=evaluation_id)
    
    # คำนวณคะแนนต่าง ๆ
    achievement_work = evaluation.achievement_work or 0
    mc_score = evaluation.mc_score or 0
    total_score = achievement_work + mc_score

    # กำหนดระดับผลการประเมิน
    if total_score >= 90:
        level = 'ดีเด่น'
    elif total_score >= 80:
        level = 'ดีมาก'
    elif total_score >= 70:
        level = 'ดี'
    elif total_score >= 60:
        level = 'พอใช้'
    else:
        level = 'ต้องปรับปรุง'

    # ส่งข้อมูลไปยังเทมเพลต
    context = {
        'user_evaluation': evaluation,
        'achievement_work': achievement_work,  # Achievement work value
        'mc_score': mc_score,
        'total_score': total_score,
        'level': level,
        'remark_achievement': evaluation.remark_achievement,
        'remark_mc': evaluation.remark_mc,
        'remark_other': evaluation.remark_other,
        'remark_total': evaluation.remark_total,
        'evaluation_id': evaluation_id,
    }

    return render(request, 'app_evaluation/evaluation_page4.html', context)

@login_required
def evaluation_page5(request, evaluation_id):
    # ดึงข้อมูล user_evaluation โดยไม่สนใจ request.user
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    
    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    # สร้างฟอร์ม PersonalDiagramFormset และ UserEvaluationForm
    PersonalDiagramFormset = modelformset_factory(PersonalDiagram, fields=('skill_evol', 'dev', 'dev_time'), extra=0)
    form = UserEvaluationForm(instance=evaluation)
    formset = PersonalDiagramFormset(queryset=PersonalDiagram.objects.filter(uevr_id=evaluation))

    # จัดการการบันทึกข้อมูลฟอร์ม
    if request.method == 'POST':
        if 'save_form' in request.POST:
            # ตรวจสอบฟอร์ม UserEvaluationForm
            form = UserEvaluationForm(request.POST, instance=evaluation)
            if form.is_valid():
                form.save()
                messages.success(request, "บันทึกข้อมูลการประเมินสำเร็จ!")
            else:
                messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลที่กรอก")
        
        elif 'save_formset' in request.POST:
            # ตรวจสอบฟอร์ม PersonalDiagramFormset
            formset = PersonalDiagramFormset(request.POST)
            if formset.is_valid():
                formset.save()
                messages.success(request, "บันทึกข้อมูลฟอร์มสำเร็จ!")
            else:
                messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลที่กรอก")

    # เตรียม context เพื่อส่งไปยัง template
    context = {
        'form': form,
        'formset': formset,
        'evaluation_id': evaluation_id,
        'profile': profile,
        'selected_group': selected_group,
        'evaluation':evaluation,
    }

    return render(request, 'app_evaluation/evaluation_page5.html', context)

@login_required
def add_personal_diagram1(request, evaluation_id):
    # ดึง user_evaluation ตาม evaluation_id
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    if request.method == 'POST':
        form = PersonalDiagramForm(request.POST)
        if form.is_valid():
            personal_diagram = form.save(commit=False)
            personal_diagram.uevr_id = evaluation  # เชื่อมโยงกับ user_evaluation
            personal_diagram.save()
            messages.success(request, 'เพิ่มข้อมูลแผนพัฒนาสำเร็จ!')
            # กลับไปยังหน้า evaluation_page_5
            return redirect('evaluation_page5', evaluation_id=evaluation_id)
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการบันทึก กรุณาตรวจสอบข้อมูล.')
    else:
        form = PersonalDiagramForm()

    context = {
        'form': form,
        'evaluation_id': evaluation_id,
    }
    return render(request, 'app_evaluation/add_personal_diagram1.html', context)

@login_required
def edit_personal_diagram1(request, pd_id):
    # ดึงข้อมูล PersonalDiagram ที่ต้องการแก้ไข
    personal_diagram = get_object_or_404(PersonalDiagram, pk=pd_id)

    if request.method == 'POST':
        form = PersonalDiagramForm(request.POST, instance=personal_diagram)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลแผนพัฒนาสำเร็จ!')
            # กลับไปยังหน้า evaluation_page_5
            return redirect('evaluation_page5', evaluation_id=personal_diagram.uevr_id.uevr_id)
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการแก้ไข กรุณาตรวจสอบข้อมูล.')
    else:
        form = PersonalDiagramForm(instance=personal_diagram)

    context = {
        'form': form,
        'evaluation_id': personal_diagram.uevr_id.uevr_id,
    }
    return render(request, 'app_evaluation/edit_personal_diagram1.html', context)

@login_required
def delete_personal_diagram1(request, pd_id):
    # ดึงข้อมูล PersonalDiagram ที่ต้องการลบ
    personal_diagram = get_object_or_404(PersonalDiagram, pk=pd_id)

    if request.method == 'POST':
        evaluation_id = personal_diagram.uevr_id.uevr_id
        
        try:
            # ตรวจสอบว่าค่า pd_id ถูกต้อง
            print(f"Trying to delete PersonalDiagram with ID: {pd_id}, Linked Evaluation ID: {evaluation_id}")
            personal_diagram.delete()
            messages.success(request, 'ลบข้อมูลแผนพัฒนาสำเร็จ!')
        except Exception as e:
            # แสดงข้อความข้อผิดพลาดที่เกิดขึ้น
            print(f"Error occurred while deleting PersonalDiagram ID {pd_id}: {e}")
            messages.error(request, f'เกิดข้อผิดพลาดในการลบข้อมูล: {e}')
        return redirect('evaluation_page5', evaluation_id=evaluation_id)
    
    return redirect('evaluation_page5', evaluation_id=personal_diagram.uevr_id.uevr_id)

@login_required
def evaluation_page6(request, evaluation_id):
    # Fetch the evaluation object
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    context = {
        'evaluation_id': evaluation_id,
        'evaluation':evaluation,
    }

    return render(request,'app_evaluation/evaluation_page6.html', context)

@login_required
def search_evaluations_2(request):
    query = request.GET.get('q')  # รับค่าค้นหาจาก URL เช่น ?q=คำค้นหา
    year = request.GET.get('year')  # รับค่าปีจาก URL
    round = request.GET.get('round')  # รับค่ารอบจาก URL
    
    evaluations = user_evaluation.objects.all()

    # ตรวจสอบว่ามีการค้นหาหรือไม่
    if query:
        evaluations = evaluations.filter(
            user__first_name__icontains=query
        ) | evaluations.filter(
            user__last_name__icontains=query
        )
    
    # ตรวจสอบว่ามีการกรองตามปีหรือไม่
    if year:
        evaluations = evaluations.filter(evr_id__evr_year=year)
    
    # ตรวจสอบว่ามีการกรองตามรอบหรือไม่
    if round:
        evaluations = evaluations.filter(evr_id__evr_round=round)

    # ตรวจสอบวันที่ปัจจุบันกับ end_date ของ evr_round และอัพเดตสถานะ
    current_date = timezone.now().date()
    
    for evaluation in evaluations:
        evr_round_obj = evaluation.evr_id
        
        # ถ้า end_date เกิน current_date ให้เปลี่ยนสถานะเป็น True
        if evr_round_obj.end_date and current_date > evr_round_obj.end_date:
            if not evr_round_obj.evr_status:  # ตรวจสอบสถานะก่อนว่าเป็น False อยู่หรือไม่
                evr_round_obj.evr_status = True  # หมดเวลา: เปลี่ยนสถานะเป็น True
                evr_round_obj.save()
    
    # เรียงข้อมูลให้ใหม่สุดอยู่ด้านบน โดยใช้ฟิลด์ created_at ในการจัดเรียง
    evaluations = evaluations.order_by('-created_at')  # เปลี่ยน 'created_at' เป็นฟิลด์เวลาที่เหมาะสม

    # ดึงข้อมูลปีและรอบทั้งหมดเพื่อนำไปแสดงในฟอร์มค้นหา
    years = user_evaluation.objects.values_list('evr_id__evr_year', flat=True).distinct()
    rounds = user_evaluation.objects.values_list('evr_id__evr_round', flat=True).distinct()

    context = {
        'evaluations': evaluations,
        'query': query,
        'years': years,
        'rounds': rounds,
    }

    return render(request, 'app_evaluation/search_evaluations_2.html', context)

@login_required
def search_evaluations_3(request):
    query = request.GET.get('q')  # รับค่าค้นหาจาก URL เช่น ?q=คำค้นหา
    year = request.GET.get('year')  # รับค่าปีจาก URL
    round = request.GET.get('round')  # รับค่ารอบจาก URL
    
    evaluations = user_evaluation.objects.exclude(full_name__isnull=True).exclude(full_name__exact='')

    # ตรวจสอบว่ามีการค้นหาหรือไม่
    if query:
        evaluations = evaluations.filter(
            user__first_name__icontains=query
        ) | evaluations.filter(
            user__last_name__icontains=query
        )
    
    # ตรวจสอบว่ามีการกรองตามปีหรือไม่
    if year:
        evaluations = evaluations.filter(evr_id__evr_year=year)
    
    # ตรวจสอบว่ามีการกรองตามรอบหรือไม่
    if round:
        evaluations = evaluations.filter(evr_id__evr_round=round)

    # ตรวจสอบวันที่ปัจจุบันกับ end_date ของ evr_round และอัพเดตสถานะ
    current_date = timezone.now().date()
    
    for evaluation in evaluations:
        evr_round_obj = evaluation.evr_id
        
        # ถ้า end_date เกิน current_date ให้เปลี่ยนสถานะเป็น True
        if evr_round_obj.end_date and current_date > evr_round_obj.end_date:
            if not evr_round_obj.evr_status:  # ตรวจสอบสถานะก่อนว่าเป็น False อยู่หรือไม่
                evr_round_obj.evr_status = True  # หมดเวลา: เปลี่ยนสถานะเป็น True
                evr_round_obj.save()
    
    # เรียงข้อมูลให้ใหม่สุดอยู่ด้านบน โดยใช้ฟิลด์ created_at ในการจัดเรียง
    evaluations = evaluations.order_by('-created_at')  # เปลี่ยน 'created_at' เป็นฟิลด์เวลาที่เหมาะสม

    # ดึงข้อมูลปีและรอบทั้งหมดเพื่อนำไปแสดงในฟอร์มค้นหา
    years = user_evaluation.objects.values_list('evr_id__evr_year', flat=True).distinct()
    rounds = user_evaluation.objects.values_list('evr_id__evr_round', flat=True).distinct()

    context = {
        'evaluations': evaluations,
        'query': query,
        'years': years,
        'rounds': rounds,
    }

    return render(request, 'app_evaluation/search_evaluations_3.html', context)

@login_required
def evaluation_page_from_1(request, evaluation_id):
    # ดึงข้อมูล user_evaluation โดยไม่สนใจ request.user
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    evr_round_obj = evaluation.evr_id  # Get the current evaluation round from user_evaluation

    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user, evr_id=evr_round_obj).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    # ดึงข้อมูลการปฏิบัติงานของผู้ใช้
    user_work_info_obj, created = user_work_info.objects.get_or_create(
        user=evaluation.user,
        round=evr_round_obj,
        defaults={'punishment': ''}
    )
    work_form_current = UserWorkInfoForm(instance=user_work_info_obj)

    # สร้างฟอร์มโปรไฟล์และการปฏิบัติงาน
    profile_form = UserProfileForm(instance=evaluation.user)
    extended_form = ExtendedProfileForm(instance=profile)

    # ฟังก์ชันสำหรับดึงข้อมูลการลา
    def get_or_create_leave(user, round_obj, leave_type):
        leave, _ = WorkLeave.objects.get_or_create(
            user=user,
            round=round_obj,
            leave_type=leave_type,
            defaults={'times': 0, 'days': 0}
        )
        return leave

    # ตรวจสอบรอบที่ 1 (หากมีข้อมูล)
    round_1 = evr_round.objects.filter(
        evr_round=1, evr_year=(evr_round_obj.evr_year - 1 if evr_round_obj.evr_round == 2 else evr_round_obj.evr_year)
    ).first()

    # ดึงข้อมูลการลาของรอบที่ 1 และรอบปัจจุบัน
    sick_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'SL') if round_1 else None
    sick_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'SL'), prefix='sick_leave')
    
    personal_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'PL') if round_1 else None
    personal_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'PL'), prefix='personal_leave')

    late_round_1 = get_or_create_leave(evaluation.user, round_1, 'LT') if round_1 else None
    late_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'LT'), prefix='late')

    maternity_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'ML') if round_1 else None
    maternity_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'ML'), prefix='maternity_leave')

    ordination_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'OL') if round_1 else None
    ordination_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'OL'), prefix='ordination_leave')

    longsick_leave_round_1 = get_or_create_leave(evaluation.user, round_1, 'LSL') if round_1 else None
    longsick_leave_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'LSL'), prefix='longsick_leave')

    adsent_work_round_1 = get_or_create_leave(evaluation.user, round_1, 'AW') if round_1 else None
    adsent_work_form = WorkLeaveForm(request.POST or None, instance=get_or_create_leave(evaluation.user, evr_round_obj, 'AW'), prefix='adsent_work')

    # ฟอร์มสำหรับรอบที่ 1 และรอบปัจจุบัน
    round_1_forms = {
        'sick_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=sick_leave_round_1, prefix='sick_leave_round_1') if round_1 else None,
        'personal_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=personal_leave_round_1, prefix='personal_leave_round_1') if round_1 else None,
        'late_round_1_form': WorkLeaveForm(request.POST or None, instance=late_round_1, prefix='late_round_1') if round_1 else None,
        'maternity_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=maternity_leave_round_1, prefix='maternity_leave_round_1') if round_1 else None,
        'ordination_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=ordination_leave_round_1, prefix='ordination_leave_round_1') if round_1 else None,
        'longsick_leave_round_1_form': WorkLeaveForm(request.POST or None, instance=longsick_leave_round_1, prefix='longsick_leave_round_1') if round_1 else None,
        'adsent_work_round_1_form': WorkLeaveForm(request.POST or None, instance=adsent_work_round_1, prefix='adsent_work_round_1') if round_1 else None
    }

    # จัดการการบันทึกข้อมูลฟอร์ม
    if request.method == 'POST':
        # ตรวจสอบข้อมูลทุกฟอร์ม
        profile_form = UserProfileForm(request.POST, instance=evaluation.user)
        extended_form = ExtendedProfileForm(request.POST, instance=profile)
        work_form_current = UserWorkInfoForm(request.POST, instance=user_work_info_obj)

        # ฟอร์มทั้งหมดที่จะตรวจสอบความถูกต้อง
        current_round_forms = [sick_leave_form, personal_leave_form, late_form, maternity_leave_form, ordination_leave_form, longsick_leave_form, adsent_work_form]
        all_forms = [profile_form, extended_form, work_form_current] + current_round_forms + list(round_1_forms.values())

        if all(form.is_valid() for form in all_forms if form is not None):
            # บันทึกข้อมูลทุกฟอร์ม
            profile_form.save()
            extended_form.save()
            work_form_current.save()
            
            for form in current_round_forms:
                form.save()

            for form in round_1_forms.values():
                if form:
                    form.save()

            messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
            return redirect('evaluation_page_from_1', evaluation_id=evaluation_id)
        else:
            messages.error(request, "มีข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลอีกครั้ง")

    # เตรียมข้อมูลเพื่อส่งไปแสดงผล
    context = {
        'profile_form': profile_form,
        'extended_form': extended_form,
        'work_form_current': work_form_current,
        'evr_round': evr_round_obj,
        'profile': profile,
        'selected_group': selected_group,
        'sick_leave_form': sick_leave_form,
        'personal_leave_form': personal_leave_form,
        'late_form': late_form,
        'maternity_leave_form': maternity_leave_form,
        'ordination_leave_form': ordination_leave_form,
        'longsick_leave_form': longsick_leave_form,
        'adsent_work_form': adsent_work_form,
        # ฟอร์มรอบที่ 1 ถ้ามี
        **round_1_forms,
        'evaluation_id': evaluation_id,
        'user_evaluation_agreement_year_thai': user_evaluation_agreement_obj.year + 543 if user_evaluation_agreement_obj else None,
        'user_evaluation_agreement': user_evaluation_agreement_obj,
        'user_evaluation': evaluation,
    }

    return render(request, 'app_evaluation/evaluation_page_from_1.html', context)

@login_required
def evaluation_page_from_2(request, evaluation_id):
    # ดึงข้อมูล user_evaluation โดยไม่สนใจ request.user
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    evr_round_obj = evaluation.evr_id

    # ดึงข้อมูล profile
    profile = evaluation.user.profile

    # ดึง selected_group ที่สัมพันธ์กับ user ผ่าน user_evaluation_agreement
    try:
        user_evaluation_agreement_obj = user_evaluation_agreement.objects.get(user=evaluation.user, evr_id=evr_round_obj)
        selected_group = user_evaluation_agreement_obj.g_id
    except user_evaluation_agreement.DoesNotExist:
        selected_group = None

    # ดึงข้อมูล f_id ที่เชื่อมโยงกับ group_detail ของ selected_group
    if selected_group:
        fields = wl_field.objects.filter(group_detail__g_id=selected_group).distinct()
    else:
        fields = wl_field.objects.none()

    # ดึงข้อมูล subfields ที่ผู้ใช้เลือก
    selected_subfields = UserSelectedSubField.objects.filter(evaluation=evaluation)

    # ดึงข้อมูล subfields ที่เกี่ยวข้องกับ fields ที่ได้เลือก
    subfields = wl_subfield.objects.filter(f_id__in=fields)

    # ดึงข้อมูล workload_selections ที่เชื่อมโยงกับ subfields
    workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation, sf_id__in=subfields)

    # บันทึก selected_workload_edit อัตโนมัติถ้าเป็น 0
    for selection in workload_selections:
        if selection.selected_workload_edit == 0:
            selection.selected_workload_edit = selection.calculated_workload
            selection.save()  # บันทึกการเปลี่ยนแปลงของ selected_workload_edit
            # คำนวณผลรวมของ calculated_workload
            total_workload = sum(selection.calculated_workload for selection in workload_selections)

            # ดึง c_wl ที่สูงที่สุดจาก user_evaluation
            max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0

            # คำนวณผลรวมของ calculated_workload
            total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)

            # ดึง c_wl ที่สูงที่สุดจาก user_evaluation
            max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_gtt'))['max_workload'] or 0

            evaluation.c_wl = total_workload
            evaluation.c_gtt = total_workload_edit
            # คำนวณส่วนต่างคะแนนภาระงาน
            workload_difference = max_workload - evaluation.c_wl
            workload_difference_score = workload_difference * (28 / 115)
            achievement_work = 70 - workload_difference_score

            workload_difference_edit = max_workload_edit - total_workload_edit
            workload_difference_score_edit = workload_difference_edit * (28 / 115)
            c_sumwl = 70 - workload_difference_score_edit


            # บันทึกค่าที่คำนวณใน evaluation
            
            evaluation.achievement_work = round(achievement_work, 1)
            
            evaluation.c_sumwl = round(c_sumwl, 1)
            evaluation.save()

    if request.method == 'POST':
        if 'save_form' in request.POST:
            selection_id = request.POST.get('save_form')
            
            # ดึง selection ที่ตรงกับ selection_id
            selection = UserWorkloadSelection.objects.get(id=selection_id)
            
            # ตั้งค่า selected_workload_edit เป็น calculated_workload ถ้าเป็น 0
            if selection.selected_workload_edit == 0:
                selection.selected_workload_edit = selection.calculated_workload
            selection.save()

            messages.success(request, 'บันทึกข้อมูลสำเร็จ')
            return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

        elif 'edit_form' in request.POST:
            selection_id = request.POST.get('edit_form')
            selected_workload_edit_value = request.POST.get(f'selected_workload_edit_{selection_id}')

            # ดำเนินการสำหรับการแก้ไข
            selection = UserWorkloadSelection.objects.get(id=selection_id)
            selection.selected_workload_edit_status = True
            selection.selected_workload_edit = float(selected_workload_edit_value)
            selection.save()

            messages.info(request, 'แก้ไขข้อมูลสำเร็จ')
            return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

    else:
        forms = [UserWorkloadSelectionForm2(instance=selection) for selection in workload_selections]
        
        # สร้าง dictionary ที่จับคู่ selection กับ form
        forms_dict = {selection.id: form for selection, form in zip(workload_selections, forms)}


    # คำนวณค่า min_workload จากข้อมูล group
    min_workload = group.objects.filter(g_id=selected_group.g_id).values_list('g_max_workload', flat=True).first()
    if not min_workload:
        min_workload = 35  # ตั้งค่า default ถ้าไม่มีข้อมูล

    # คำนวณผลรวมของ calculated_workload
    total_workload = sum(selection.calculated_workload for selection in workload_selections)

    # ดึง c_wl ที่สูงที่สุดจาก user_evaluation
    max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0

    # คำนวณผลรวมของ calculated_workload
    total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)

    # ดึง c_wl ที่สูงที่สุดจาก user_evaluation
    max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_gtt'))['max_workload'] or 0

    evaluation.c_wl = total_workload
    evaluation.c_gtt = total_workload_edit
    # คำนวณส่วนต่างคะแนนภาระงาน
    workload_difference = max_workload - evaluation.c_wl
    workload_difference_score = workload_difference * (28 / 115)
    achievement_work = 70 - workload_difference_score

    workload_difference_edit = max_workload_edit - total_workload_edit
    workload_difference_score_edit = workload_difference_edit * (28 / 115)
    c_sumwl = 70 - workload_difference_score_edit


    # บันทึกค่าที่คำนวณใน evaluation
    
    evaluation.achievement_work = round(achievement_work, 1)
    
    evaluation.c_sumwl = round(c_sumwl, 1)
    evaluation.save()

    # ส่ง context ไปยังเทมเพลต
    context = {
        'user_evaluation': evaluation,
        'fields': fields,
        'selected_subfields': selected_subfields,
        'workload_selections': workload_selections,
        'subfields': subfields,
        'total_workload': total_workload,
        'achievement_work': evaluation.achievement_work,
        'evaluation_id': evaluation_id,
        'min_workload': min_workload,
        'user_evaluation_agreement_year_thai': user_evaluation_agreement_obj.year + 543 if user_evaluation_agreement_obj else None,
        'forms': forms,  # ส่งฟอร์มไปยังเทมเพลต
        'forms_dict': forms_dict,
    }

    return render(request, 'app_evaluation/evaluation_page_from_2.html', context)

@login_required
def select_subfields3(request, f_id, evaluation_id):
    field = get_object_or_404(wl_field, pk=f_id)
    subfields = wl_subfield.objects.filter(f_id=field)

    # ดึงข้อมูลการประเมินที่สอดคล้องกับ evaluation_id
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    if request.method == 'POST':
        selected_sf_id = request.POST.get('sf_id')  # ใช้ get() เพื่อดึงค่า sf_id จากฟอร์ม
        if selected_sf_id:
            selected_sf = wl_subfield.objects.get(sf_id=selected_sf_id)
            # เพิ่มข้อมูล evaluation เข้าไปในการสร้าง UserSelectedSubField
            UserSelectedSubField.objects.create(
                user=request.user,
                evaluation=evaluation,  # เชื่อม evaluation
                f_id=field,
                sf_id=selected_sf
            )
            return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

    context = {
        'field': field,
        'subfields': subfields,
        'evaluation_id': evaluation_id,
    }
    return render(request, 'app_evaluation/select_subfields3.html', context)

@login_required
def delete_selected_subfield3(request, sf_id):
    # ตรวจสอบว่ามีการส่ง evaluation_id มาหรือไม่
    evaluation_id = request.POST.get('evaluation_id') or request.GET.get('evaluation_id')
    if not evaluation_id:
        messages.error(request, "ไม่พบ evaluation_id")
        return redirect('select_group')

    try:
        # ลบข้อมูลทั้งหมดใน UserSelectedSubField ที่มี sf_id
        selected_subfields = UserSelectedSubField.objects.filter(sf_id=sf_id)

        if not selected_subfields.exists():
            messages.error(request, 'ไม่พบ Subfield ที่คุณพยายามจะลบ.')
            return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

        if request.method == 'POST':
            # ลบข้อมูลที่ค้นหาได้ทั้งหมด
            selected_subfields.delete()
            messages.success(request, 'ลบ Subfield เรียบร้อยแล้ว!')
            return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
        return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

    return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

@login_required
def select_workload_criteria3(request, evaluation_id, sf_id):
    # ดึงข้อมูล evaluation และ subfield ที่เกี่ยวข้อง
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    subfield = get_object_or_404(wl_subfield, pk=sf_id)
    
    # สร้างฟอร์มและส่งค่า subfield ไปยังฟอร์มเพื่อกรองข้อมูลใน selected_id
    criteria_form = UserWorkloadSelectionForm(initial={'sf_id': subfield}, subfield=subfield)

    # ตรวจสอบการส่งฟอร์ม
    if request.method == 'POST':
        criteria_form = UserWorkloadSelectionForm(request.POST, subfield=subfield)
        
        if criteria_form.is_valid():
            new_criteria = criteria_form.save(commit=False)
            new_criteria.sf_id = subfield
            new_criteria.evaluation = evaluation
            new_criteria.user = request.user

            try:
                # แปลงค่าทั้งหมดเป็น float ก่อนทำการคำนวณ
                selected_num = float(new_criteria.selected_num)
                selected_maxnum = float(new_criteria.selected_maxnum)
                selected_workload = float(new_criteria.selected_workload)

                # คำนวณค่า calculated_workload
                if selected_maxnum == 0:
                    calculated_workload = selected_num * selected_workload
                else:
                    calculated_workload = min(selected_num, selected_maxnum) * selected_workload

                # บันทึกค่า calculated_workload ลงใน new_criteria
                new_criteria.calculated_workload = calculated_workload
                new_criteria.save()

                # คำนวณค่าใหม่หลังการเพิ่มภาระงาน
                workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)

                total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)
                total_workload = sum(selection.calculated_workload for selection in workload_selections)

                max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(Max('c_wl'))['c_wl__max'] or 0
                max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(Max('c_gtt'))['c_gtt__max'] or 0

                # อัปเดตค่าใน evaluation
                evaluation.c_wl = total_workload
                evaluation.c_gtt = total_workload_edit

                workload_difference = max_workload - evaluation.c_wl
                workload_difference_score = workload_difference * (28 / 115)
                achievement_work = 70 - workload_difference_score
                evaluation.achievement_work = round(achievement_work, 1)

                workload_difference_edit = max_workload_edit - evaluation.c_gtt
                workload_difference_score_edit = workload_difference_edit * (28 / 115)
                c_sumwl = 70 - workload_difference_score_edit
                evaluation.c_sumwl = round(c_sumwl, 1)

                evaluation.save()

                messages.success(request, f'เพิ่มภาระงานใหม่เรียบร้อยแล้ว! คำนวณภาระงาน: {calculated_workload:.2f}')
                return redirect('evaluation_page_from_2', evaluation_id=evaluation_id)

            except ValueError as e:
                print(f"ValueError: {e}")
                messages.error(request, 'ไม่สามารถคำนวณค่าได้ โปรดตรวจสอบข้อมูลที่กรอก.')

    # ส่งข้อมูลไปยังเทมเพลต
    context = {
        'evaluation': evaluation,
        'subfield': subfield,
        'criteria_form': criteria_form,
    }
    return render(request, 'app_evaluation/select_workload_criteria3.html', context)

@login_required
def edit_workload_selection3(request, selection_id):
    selection = get_object_or_404(UserWorkloadSelection, pk=selection_id)

    if request.method == 'POST':
        form = UserWorkloadSelectionForm1(request.POST, instance=selection)
        evaluation_id = selection.evaluation.uevr_id
        if form.is_valid():
            # ถ้าฟอร์มถูกต้อง ให้บันทึกการเปลี่ยนแปลง
            if selection.selected_maxnum == 0:
                selection.calculated_workload = selection.selected_num * selection.selected_workload
            else:
                if selection.selected_num <= selection.selected_maxnum:
                    selection.calculated_workload = selection.selected_num  * selection.selected_workload
                else:
                    selection.calculated_workload = selection.selected_maxnum * selection.selected_workload
            form.save()
            evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
            workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)
            max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_gtt'))['max_workload'] or 0
            max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0
            
            # คำนวณค่าที่เกี่ยวข้องใหม่หลังจากการลบ
            total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)
            total_workload = sum(selection.calculated_workload for selection in workload_selections)
            
            evaluation.c_wl = total_workload
            evaluation.c_gtt = total_workload_edit
            # คำนวณค่า c_sumwl ใหม่
            workload_difference = max_workload - evaluation.c_wl
            workload_difference_score = workload_difference * (28 / 115)
            achievement_work = 70 - workload_difference_score
            evaluation.achievement_work = round(achievement_work, 1)

            workload_difference_edit = max_workload_edit - total_workload_edit
            workload_difference_score_edit = workload_difference_edit * (28 / 115)
            c_sumwl = 70 - workload_difference_score_edit
            evaluation.c_sumwl = round(c_sumwl, 1)

            evaluation.save()
            messages.success(request, 'แก้ไขภาระงานเรียบร้อยแล้ว!')
            return redirect('evaluation_page_from_2', evaluation_id=selection.evaluation.uevr_id)
        else:
            messages.error(request, 'กรุณาเลือกข้อมูลภาระงานให้ครบถ้วน.')
    else:
        form = UserWorkloadSelectionForm1(instance=selection)

    return render(request, 'app_evaluation/edit_workload_selection3.html', {
        'form': form,
        'selection': selection,
    })

@login_required
def delete_workload_selection3(request, selection_id):
    selection = get_object_or_404(UserWorkloadSelection, pk=selection_id)

    if request.method == 'POST':
        evaluation_id = selection.evaluation.uevr_id
        # ลบเฉพาะการเชื่อมโยงกับ UserWorkloadSelection
        selection.delete()  

        # ดึงข้อมูล evaluation ใหม่หลังจากลบ

        evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
        workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)
        max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_gtt'))['max_workload'] or 0
        max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0
        
        # คำนวณค่าที่เกี่ยวข้องใหม่หลังจากการลบ
        total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)
        total_workload = sum(selection.calculated_workload for selection in workload_selections)
        
        evaluation.c_wl = total_workload
        evaluation.c_gtt = total_workload_edit
        # คำนวณค่า c_sumwl ใหม่
        workload_difference = max_workload - evaluation.c_wl
        workload_difference_score = workload_difference * (28 / 115)
        achievement_work = 70 - workload_difference_score
        evaluation.achievement_work = round(achievement_work, 1)

        workload_difference_edit = max_workload_edit - total_workload_edit
        workload_difference_score_edit = workload_difference_edit * (28 / 115)
        c_sumwl = 70 - workload_difference_score_edit
        evaluation.c_sumwl = round(c_sumwl, 1)

        evaluation.save()
        messages.success(request, 'ลบภาระงานเรียบร้อยแล้ว!')
        return redirect('evaluation_page_from_2', evaluation_id=selection.evaluation.uevr_id)

    return render(request, 'app_evaluation/confirm_delete3.html', {
        'selection': selection,
    })

@login_required
def upload_evidence2(request, criteria_id):
    criteria = get_object_or_404(UserWorkloadSelection, pk=criteria_id)
    evaluation = criteria.evaluation  # ดึงค่า evaluation จาก UserWorkloadSelection

    if request.method == 'POST':
        form = UserEvidentForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        pictures = request.FILES.getlist('picture')
        filenames = request.POST.getlist('filename')  # รับรายชื่อไฟล์ที่ผู้ใช้กรอกเข้ามา

        if form.is_valid():
            # บันทึกไฟล์ PDF และ DOCX
            for index, file in enumerate(files):
                custom_filename = filenames[index] if index < len(filenames) and filenames[index] else file.name
                new_filename = f"{uuid.uuid4()}_{custom_filename}"

                evidence = user_evident(
                    uwls_id=criteria,
                    uevr_id=evaluation,
                    file=file,
                    filename=new_filename
                )
                evidence.save()

            # ลดขนาดรูปภาพก่อนบันทึก
            for index, picture in enumerate(pictures):
                custom_filename = filenames[index] if index < len(filenames) and filenames[index] else picture.name
                new_filename = f"{uuid.uuid4()}_{custom_filename}"

                image = Image.open(picture)
                max_size = (1366, 800)
                image.thumbnail(max_size)
                img_io = ContentFile(b'')
                image_format = image.format or 'JPEG'
                image.save(img_io, format=image_format)

                file_name = default_storage.save(f"uploads/{new_filename}", img_io)
                evidence = user_evident(
                    uwls_id=criteria,
                    uevr_id=evaluation,
                    picture=file_name,
                    filename=new_filename
                )
                evidence.save()

            messages.success(request, "อัปโหลดไฟล์เรียบร้อยแล้ว!")
            return redirect('upload_evidence2', criteria_id=criteria_id)

    else:
        form = UserEvidentForm()

    evidences = user_evident.objects.filter(uwls_id=criteria)

    return render(request, 'app_evaluation/upload_evidence2.html', {
        'form': form,
        'evaluation': evaluation,
        'evidences': evidences,  # ส่งรายการไฟล์/รูปภาพไปยัง template
        'criteria_id': criteria_id,
    })

@login_required
def delete_evidence2(request, evidence_id):
    evidence = get_object_or_404(user_evident, uevd_id=evidence_id)

    # ลบไฟล์หรือรูปภาพที่เกี่ยวข้องจากระบบ
    if evidence.file:
        if os.path.isfile(evidence.file.path):
            os.remove(evidence.file.path)  # ลบไฟล์จาก storage
    if evidence.picture:
        if os.path.isfile(evidence.picture.path):
            os.remove(evidence.picture.path)  # ลบรูปภาพจาก storage

    # ลบรายการ evidence จากฐานข้อมูล
    evidence.delete()
    messages.success(request, "ลบไฟล์/รูปภาพเรียบร้อยแล้ว!")
    
    # ใช้ `redirect` ให้ไปยัง `upload_evidence` โดยใช้ `criteria_id`
    return redirect('upload_evidence2', criteria_id=evidence.uwls_id.id)  # เปลี่ยน `evaluation_id` เป็น `criteria_id`

@login_required
def evaluation_page_from_3(request, evaluation_id):
    # ดึงข้อมูล user_evaluation
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    

    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    main_competencies = main_competency.objects.filter(mc_type=evaluation.ac_id.ac_name)
    specific_competencies = specific_competency.objects.filter(sc_type=evaluation.ac_id.ac_name)
    administrative_competencies = None  # ตั้งค่าเริ่มต้นเป็น None
    
    # เช็คว่าถ้ามีตำแหน่งบริหารและไม่ใช่ "-"
    if evaluation.administrative_position and evaluation.administrative_position != "-":
        administrative_competencies = administrative_competency.objects.filter()

    # ตรวจสอบการส่งข้อมูล POST
    if request.method == 'POST':
        # วนลูปผ่าน main_competencies
        for competency in main_competencies:
            actual_score = request.POST.get(f'main_actual_score_{competency.mc_id}')
            if actual_score and actual_score.isdigit():
                actual_score = int(actual_score)
                user_competency_main.objects.update_or_create(
                    evaluation=evaluation,
                    mc_id=competency,
                  
                    defaults={'user': evaluation.user, 'umc_name': competency.mc_name, 'umc_type': competency.mc_type, 'actual_score': actual_score}
                )

        # วนลูปผ่าน specific_competencies
        for competency in specific_competencies:
            actual_score = request.POST.get(f'specific_actual_score_{competency.sc_id}')
            if actual_score and actual_score.isdigit():
                actual_score = int(actual_score)
                user_competency_councilde.objects.update_or_create(
                    evaluation=evaluation,
                    sc_id=competency,
                   
                    defaults={'user': evaluation.user, 'ucc_name': competency.sc_name, 'ucc_type': competency.sc_type, 'actual_score': actual_score}
                )

        # วนลูปผ่าน administrative_competencies
        if administrative_competencies is not None:
            for competency in administrative_competencies:
                actual_score = request.POST.get(f'admin_actual_score_{competency.adc_id}')
                uceo_num = request.POST.get(f'admin_uceo_num_{competency.adc_id}') 
                if actual_score and actual_score.isdigit():
                    actual_score = int(actual_score)
                    uceo_num = int(uceo_num) if uceo_num.isdigit() else 0
                    user_competency_ceo.objects.update_or_create(
                        evaluation=evaluation,
                        adc_id=competency,
                        
                        defaults={'user': evaluation.user, 'uceo_name': competency.adc_name, 'uceo_type': competency.adc_type, 'actual_score': actual_score,'uceo_num': uceo_num}
                    )

        messages.success(request, "บันทึกคะแนนเรียบร้อยแล้ว!")
        return redirect('evaluation_page_from_3', evaluation_id=evaluation_id)

    # ดึงข้อมูลคะแนนที่เคยกรอก
    main_scores = user_competency_main.objects.filter(evaluation=evaluation)
    specific_scores = user_competency_councilde.objects.filter(evaluation=evaluation)
    administrative_scores = user_competency_ceo.objects.filter(evaluation=evaluation)

    # เก็บจำนวนสมรรถนะที่ได้คะแนนตามเงื่อนไขต่าง ๆ
    score_count = {3: 0, 
                   2: 0, 
                   1: 0, 
                   0: 0}

    # คำนวณคะแนนสำหรับ main competencies
    main_competency_total = 0
    for score in main_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.mc_id.mc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        main_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ specific competencies
    specific_competency_total = 0
    for score in specific_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.sc_id.sc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        specific_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ administrative competencies (ถ้ามี)
    administrative_competency_total = 0
    if administrative_competencies is not None:
        for score in administrative_scores:
            calculated_score = calculate_competency_score(score.actual_score, score.uceo_num)
            score_count[calculated_score] += 1
            administrative_competency_total += calculated_score

    # ผลรวมคะแนนทั้งหมด
    total_score = main_competency_total + specific_competency_total + administrative_competency_total

    # คำนวณคะแนนในแต่ละกรณี (คูณ 3, 2, 1 และ 0)
    score_3_total = score_count[3] * 3
    score_2_total = score_count[2] * 2
    score_1_total = score_count[1] * 1
    score_0_total = score_count[0] * 0

    # คำนวณค่ารวมของคะแนนที่คาดหวังสำหรับแต่ละตาราง
    main_max_num = sum([c.mc_num for c in main_competencies])
    specific_max_num = sum([c.sc_num for c in specific_competencies])
    administrative_max_num = sum([score.uceo_num for score in administrative_scores]) if administrative_competencies is not None else 0

    # คำนวณคะแนนจากสูตร
    total_max_num = main_max_num + specific_max_num + administrative_max_num

    if total_max_num > 0:
        calculated_score = (total_score / total_max_num) * 30
    print(f"Total Score: {total_score}")
    print(f"Total Max Num: {total_max_num}")
    # บันทึก calculated_score ใน mc_score ของ user_evaluation
    evaluation.mc_score = calculated_score  # บันทึกคะแนนที่คำนวณได้
    evaluation.save()  # บันทึกการเปลี่ยนแปลงลงในฐานข้อมูล


    # ส่งข้อมูลไปยังเทมเพลต
    context = {
        'profile': profile,
        'main_competencies': main_competencies,
        'specific_competencies': specific_competencies,
        'administrative_competencies': administrative_competencies,
        'main_scores': main_scores,
        'specific_scores': specific_scores,
        'administrative_scores': administrative_scores,
        'main_competency_total': main_competency_total,
        'specific_competency_total': specific_competency_total,
        'administrative_competency_total': administrative_competency_total,
        'total_score': total_score,
        'total_max_num': total_max_num,
        'main_max_num': main_max_num,
        'specific_max_num': specific_max_num,
        'administrative_max_num': administrative_max_num,
        'calculated_score': calculated_score,
        'evaluation_id': evaluation_id,
        'user_evaluation_obj': evaluation,
        'ac_name': evaluation.ac_id.ac_name,
        'count_3': score_count[3],
        'count_2': score_count[2],
        'count_1': score_count[1],
        'count_0': score_count[0],
        'score_3_total': score_count[3] * 3,
        'score_2_total': score_count[2] * 2,
        'score_1_total': score_count[1] * 1,
        'score_0_total': score_count[0] * 0,
        'user_evaluation_obj': evaluation,
    }

    return render(request, 'app_evaluation/evaluation_page_from_3.html', context)


@login_required
def evaluation_page_from_4(request, evaluation_id):
    # ดึงข้อมูล user_evaluation
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)


    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    # ตรวจสอบการร้องขอจากผู้ใช้
    if request.method == 'POST':
        # ดึงข้อมูลจากฟอร์มที่ถูกส่งมา
        remark_achievement = request.POST.get('remark_achievement')
        remark_mc = request.POST.get('remark_mc')
        remark_other = request.POST.get('remark_other')
        remark_total = request.POST.get('remark_total')

        # บันทึกข้อมูลหมายเหตุ
        evaluation.remark_achievement = remark_achievement
        evaluation.remark_mc = remark_mc
        evaluation.remark_other = remark_other
        evaluation.remark_total = remark_total

        evaluation.save()  # บันทึกการเปลี่ยนแปลง

        messages.success(request, 'บันทึกหมายเหตุเรียบร้อยแล้ว!')
        return redirect('evaluation_page_from_4', evaluation_id=evaluation_id)
    
    # คำนวณคะแนนต่าง ๆ
    achievement_work = evaluation.achievement_work or 0
    mc_score = evaluation.mc_score or 0
    c_sumwl = evaluation.c_sumwl or 0
    total_score = achievement_work + mc_score
    cp_main_sum = c_sumwl + mc_score

    # กำหนดระดับผลการประเมิน
    if total_score >= 90:
        level = 'ดีเด่น'
    elif total_score >= 80:
        level = 'ดีมาก'
    elif total_score >= 70:
        level = 'ดี'
    elif total_score >= 60:
        level = 'พอใช้'
    else:
        level = 'ต้องปรับปรุง'

    # กำหนดระดับผลการประเมิน
    if cp_main_sum >= 90:
        level1 = 'ดีเด่น'
    elif cp_main_sum >= 80:
        level1 = 'ดีมาก'
    elif cp_main_sum >= 70:
        level1 = 'ดี'
    elif cp_main_sum >= 60:
        level1 = 'พอใช้'
    else:
        level1 = 'ต้องปรับปรุง'

    # ส่งข้อมูลไปยังเทมเพลต
    context = {
        'user_evaluation': evaluation,
        'achievement_work': achievement_work,  # Achievement work value
        'mc_score': mc_score,
        'total_score': total_score,
        'level': level,
        'level1': level1,
        'remark_achievement': evaluation.remark_achievement,
        'remark_mc': evaluation.remark_mc,
        'remark_other': evaluation.remark_other,
        'remark_total': evaluation.remark_total,
        'evaluation_id': evaluation_id,
        'cp_main_sum':cp_main_sum,
        'c_sumwl':c_sumwl,
    }

    return render(request, 'app_evaluation/evaluation_page_from_4.html', context)

@login_required
def evaluation_page_from_5(request, evaluation_id):
    # ดึงข้อมูล user_evaluation โดยไม่สนใจ request.user
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    
    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=evaluation.user).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None

    # สร้างฟอร์ม PersonalDiagramFormset และ UserEvaluationForm
    PersonalDiagramFormset = modelformset_factory(PersonalDiagram, fields=('skill_evol', 'dev', 'dev_time'), extra=0)
    form = UserEvaluationForm(instance=evaluation)
    formset = PersonalDiagramFormset(queryset=PersonalDiagram.objects.filter(uevr_id=evaluation))

    # จัดการการบันทึกข้อมูลฟอร์ม
    if request.method == 'POST':
        form = UserEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกข้อมูลการประเมินสำเร็จ!")
        else:
            print(form.errors)  # แสดงข้อผิดพลาดของฟอร์มใน console/log เพื่อช่วยดีบัก
            messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลที่กรอก")
    
    # เตรียม context เพื่อส่งไปยัง template
    context = {
        'form': form,
        'formset': formset,
        'evaluation_id': evaluation_id,
        'profile': profile,
        'selected_group': selected_group,
        'evaluation': evaluation,
    }

    return render(request, 'app_evaluation/evaluation_page_from_5.html', context)

@login_required
def save_full_name_and_current_date2(request, evaluation_id):
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    if request.method == 'POST':
        # ดึงข้อมูลชื่อ-นามสกุลจาก evaluation
        full_name = f"{evaluation.user.first_name} {evaluation.user.last_name}"
        
        # ใช้ timezone.now() เพื่อดึงวันที่ปัจจุบันที่รองรับ timezone
        current_date = timezone.now()

        # แปลงปีเป็น พ.ศ.
        thai_year = current_date.year + 543

        # บันทึกค่าลงในฟิลด์ที่แยกเป็น วัน เดือน ปี
        evaluation.start_day = current_date.day
        evaluation.start_month = current_date.month
        evaluation.start_year = thai_year  # บันทึกปีเป็น พ.ศ.

        # บันทึกชื่อเต็มลงในฟิลด์ full_name
        evaluation.full_name = full_name
        
        # บันทึกวันที่ลงใน evaluation (ถ้าอยากบันทึกใน created_at ต้องเปลี่ยนฟิลด์นี้เป็น null=True, blank=True)
        evaluation.created_at = current_date
        evaluation.save()

        # แปลงวันที่เป็นรูปแบบไทย (เช่น วัน/เดือน/ปี)
        thai_date_str = f"{current_date.day}/{current_date.month}/{thai_year}"

        # ส่งข้อความสำเร็จพร้อมแสดงวันที่ในรูปแบบไทย
        messages.success(request, f"บันทึกชื่อ-นามสกุล: {full_name} และวันที่ {thai_date_str} เรียบร้อยแล้ว")
        
        return redirect('evaluation_page_from_5', evaluation_id=evaluation_id)

@login_required
def add_personal_diagram2(request, evaluation_id):
    # ดึง user_evaluation ตาม evaluation_id
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    if request.method == 'POST':
        form = PersonalDiagramForm(request.POST)
        if form.is_valid():
            personal_diagram = form.save(commit=False)
            personal_diagram.uevr_id = evaluation  # เชื่อมโยงกับ user_evaluation
            personal_diagram.save()
            messages.success(request, 'เพิ่มข้อมูลแผนพัฒนาสำเร็จ!')
            # กลับไปยังหน้า evaluation_page_5
            return redirect('evaluation_page_from_5', evaluation_id=evaluation_id)
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการบันทึก กรุณาตรวจสอบข้อมูล.')
    else:
        form = PersonalDiagramForm()

    context = {
        'form': form,
        'evaluation_id': evaluation_id,
    }
    return render(request, 'app_evaluation/add_personal_diagram2.html', context)

@login_required
def edit_personal_diagram2(request, pd_id):
    # ดึงข้อมูล PersonalDiagram ที่ต้องการแก้ไข
    personal_diagram = get_object_or_404(PersonalDiagram, pk=pd_id)

    if request.method == 'POST':
        form = PersonalDiagramForm(request.POST, instance=personal_diagram)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลแผนพัฒนาสำเร็จ!')
            # กลับไปยังหน้า evaluation_page_5
            return redirect('evaluation_page_from_5', evaluation_id=personal_diagram.uevr_id.uevr_id)
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการแก้ไข กรุณาตรวจสอบข้อมูล.')
    else:
        form = PersonalDiagramForm(instance=personal_diagram)

    context = {
        'form': form,
        'evaluation_id': personal_diagram.uevr_id.uevr_id,
    }
    return render(request, 'app_evaluation/edit_personal_diagram2.html', context)

@login_required
def delete_personal_diagram2(request, pd_id):
    # ดึงข้อมูล PersonalDiagram ที่ต้องการลบ
    personal_diagram = get_object_or_404(PersonalDiagram, pk=pd_id)

    # ตรวจสอบคำขอเป็น POST ก่อนทำการลบ
    if request.method == 'POST':
        # เก็บ evaluation_id ก่อนลบ เพื่อ redirect กลับไปที่หน้า evaluation_page_5
        evaluation_id = personal_diagram.uevr_id.uevr_id
        personal_diagram.delete()
        messages.success(request, 'ลบข้อมูลแผนพัฒนาสำเร็จ!')
        return redirect('evaluation_page_from_5', evaluation_id=evaluation_id)

    # ในกรณีที่ไม่ใช่ POST ให้กลับไปที่ evaluation_page_5
    return redirect('evaluation_page_from_5', evaluation_id=personal_diagram.uevr_id.uevr_id)

@login_required
def evaluation_page_from_6(request, evaluation_id):
    # Fetch the evaluation object
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    context = {
        'evaluation_id': evaluation_id,
        'evaluation':evaluation,
    }

    return render(request,'app_evaluation/evaluation_page_from_6.html', context)

@login_required
def view_evaluation(request, uevr_id):
    evaluation = get_object_or_404(user_evaluation, uevr_id=uevr_id)
    
    # ดึงข้อมูลที่ต้องการแสดงในหน้า "ดู" การประเมิน
    context = {
        'evaluation': evaluation,
    }

    return render(request, 'app_evaluation/evaluation_page.html', context)

@login_required
def edit_evaluation(request, evaluation_id):



    # ดึง user_evaluation ที่เลือกจาก evaluation_id
    try:
        user_evaluation_obj = user_evaluation.objects.get(uevr_id=evaluation_id)
    except user_evaluation.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลการประเมินที่เลือก")
        return redirect('search_evaluations')  # กลับไปหน้าค้นหา

    # ดึงข้อมูล user_work_info ที่เชื่อมโยงกับการประเมินนี้
    try:
        user_work = user_work_info.objects.get(user=user_evaluation_obj.user, round=user_evaluation_obj.evr_id)
    except user_work_info.DoesNotExist:
        user_work = None



    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user_evaluation_obj.user)
        extended_form = ExtendedProfileForm(request.POST, instance=user_evaluation_obj.user.profile)
        work_form = UserWorkInfoForm(request.POST, instance=user_work)

        # ตรวจสอบฟอร์มทั้งหมด
        if profile_form.is_valid() and extended_form.is_valid() and work_form.is_valid():
            # บันทึกข้อมูลผู้ใช้
            profile_form.save()
            extended_profile = extended_form.save(commit=False)
            extended_profile.user = user_evaluation_obj.user
            extended_profile.save()

            # บันทึกข้อมูลการทำงาน
            work_instance = work_form.save(commit=False)
            work_instance.user = user_evaluation_obj.user
            work_instance.round = user_evaluation_obj.evr_id
            work_instance.save()

            messages.success(request, "แก้ไขข้อมูลเรียบร้อยแล้ว!")
            return redirect('search_evaluations')  # กลับไปหน้าค้นหา
        else:
            messages.error(request, "มีข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลอีกครั้ง")

    else:
        # แสดงฟอร์มในกรณีที่เป็นการ GET
        profile_form = UserProfileForm(instance=user_evaluation_obj.user)
        extended_form = ExtendedProfileForm(instance=user_evaluation_obj.user.profile)
        work_form = UserWorkInfoForm(instance=user_work)

    # ตรวจสอบว่ามี uevr_id หรือไม่ เพื่อสร้าง URL สำหรับอัปโหลดไฟล์
    if user_evaluation_obj.uevr_id:
        upload_url = reverse('upload_evidence', args=[user_evaluation_obj.uevr_id])
    else:
        upload_url = None

    context = {
        'profile_form': profile_form,
        'extended_form': extended_form,
        'work_form': work_form,
        'user_evaluation': user_evaluation_obj,
        'upload_url': upload_url,  # ส่ง URL สำหรับอัปโหลดไฟล์ไปยัง template
        'evaluation_id': evaluation_id,  # ส่ง evaluation_id ผ่านไปยัง template
    }

    return render(request, 'app_evaluation/evaluation_page.html', context)

@login_required
def select_group(request):
    # ดึงข้อมูลกลุ่มที่มีอยู่ทั้งหมด
    groups = group.objects.all()
    evr_round_obj = get_evr_round()  # ดึงข้อมูลรอบการประเมินปัจจุบัน


    # ตรวจสอบว่าผู้ใช้มีการเลือกกลุ่มและมีข้อมูลการประเมินสำหรับรอบปัจจุบันแล้วหรือไม่
    selected_agreement = user_evaluation_agreement.objects.filter(
        user=request.user,
        year=timezone.now().year,
        evr_id=evr_round_obj
    ).first()

    # เพิ่มการดึงข้อมูลรอบที่ 1 (ปีที่แล้ว) ถ้าเป็นรอบที่ 2 ในปัจจุบัน
    round_1_agreement = None
    if evr_round_obj.evr_round == 2:
        round_1_agreement = user_evaluation_agreement.objects.filter(
            user=request.user,
            year=timezone.now().year - 1,
            evr_id__evr_round=1
        ).first()

    # ถ้ามีการเลือกกลุ่มแล้ว ให้ใช้ข้อมูลกลุ่มที่ถูกเลือก
    if selected_agreement:
        selected_group_name = selected_agreement.g_id.g_name
        selected_round = selected_agreement.evr_id.evr_round

        # ตรวจสอบว่ามีการสร้างการประเมินในรอบนี้แล้วหรือไม่
        evaluation = user_evaluation.objects.filter(
            user=request.user,
            evr_id=evr_round_obj
        ).first()

        if evaluation:
            # ถ้ามีข้อมูลการประเมินแล้ว ให้ไปที่หน้า evaluation_page ทันที
            return redirect('evaluation_page', evaluation_id=evaluation.uevr_id)

    # ถ้าเป็นรอบที่ 2 และมีข้อมูลกลุ่มจากรอบที่ 1 ให้ใช้กลุ่มของรอบที่ 1
    if evr_round_obj.evr_round == 2 and round_1_agreement:
        selected_group_name = round_1_agreement.g_id.g_name
        selected_round = evr_round_obj.evr_round

        # สร้างการประเมินใหม่สำหรับรอบที่ 2 โดยใช้กลุ่มจากรอบที่ 1
        evaluation = user_evaluation.objects.create(
            user=request.user,
            evr_id=evr_round_obj,
            c_gtt=None,
            c_wl=None,
            c_sumwl=None,
            approve_status=False,
            evaluater_id=None,
            evaluater_editgtt=None,
            mc_score=None,
            sc_score=None,
            adc_score=None,
            cp_num=None,
            cp_score=None,
            cp_sum=None,
            cp_main_sum=None,
            achievement_work=None,
            performing_work=None,
            other_work=None,
            sum_work=None,
            improved=None,
            suggestions=None,
        )

        # บันทึกข้อมูลการเลือกกลุ่มสำหรับรอบที่ 2
        user_evaluation_agreement.objects.update_or_create(
            user=request.user,
            year=timezone.now().year,
            evr_id=evr_round_obj,
            defaults={'g_id': round_1_agreement.g_id}
        )

        # รีไดเร็กไปที่หน้าแบบประเมินหลังจากสร้าง
        return redirect('evaluation_page', evaluation_id=evaluation.uevr_id)

    # ถ้าไม่มีการประเมิน ให้ผู้ใช้เลือกกลุ่มใหม่
    selected_group_name = None
    selected_round = evr_round_obj.evr_round

    if request.method == 'POST':
        form = GroupSelectionForm(request.POST)
        if form.is_valid():
            # เก็บค่ากลุ่มที่ผู้ใช้เลือก
            selected_group_name = form.cleaned_data['g_name']
            selected_group = get_object_or_404(group, g_name=selected_group_name)

            # สร้างหรืออัปเดตข้อมูลการเลือกกลุ่มของผู้ใช้สำหรับรอบนี้
            user_evaluation_agreement.objects.update_or_create(
                user=request.user,
                year=timezone.now().year,
                evr_id=evr_round_obj,
                defaults={'g_id': selected_group}
            )

            # สร้างแบบประเมินใหม่หลังจากเลือกกลุ่มแล้ว
            evaluation = user_evaluation.objects.create(
                user=request.user,
                evr_id=evr_round_obj,
                c_gtt=None,
                c_wl=None,
                c_sumwl=None,
                approve_status=False,
                evaluater_id=None,
                evaluater_editgtt=None,
                mc_score=None,
                sc_score=None,
                adc_score=None,
                cp_num=None,
                cp_score=None,
                cp_sum=None,
                cp_main_sum=None,
                achievement_work=None,
                performing_work=None,
                other_work=None,
                sum_work=None,
                improved=None,
                suggestions=None,
            )

            # รีไดเร็กไปที่หน้าแบบประเมินหลังจากสร้าง
            return redirect('evaluation_page', evaluation_id=evaluation.uevr_id)
    else:
        form = GroupSelectionForm()

    return render(request, 'app_evaluation/select_group.html', {
        'form': form,
        'groups': groups,
        'selected_group_name': selected_group_name,
        'selected_round': selected_round
    })

@login_required
def create_evaluation(request):
    evr_round_obj = get_evr_round()  # ใช้ฟังก์ชันเพื่อดึงรอบการประเมินที่ถูกต้อง
    if request.method == 'POST':
        form = UserEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.user = request.user
            evaluation.evr_id = evr_round_obj  # เชื่อมกับรอบการประเมิน
            evaluation.save()
            return redirect('evaluation_success')
    else:
        form = UserEvaluationForm()

    return render(request, 'app_evaluation/create_evaluation.html', {'form': form, 'evr_round': evr_round_obj})

# ฟังก์ชันหน้าแบบประเมิน
@login_required
def evaluation_page(request, evaluation_id):
    user = request.user

    # ตรวจสอบว่า Profile ของผู้ใช้มีอยู่แล้วหรือไม่ ถ้าไม่ให้ redirect ไปหน้าโปรไฟล์
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        messages.error(request, "กรุณากรอกข้อมูลโปรไฟล์ก่อนทำการประเมิน")
        return redirect('profile')

    evr_round_obj = get_evr_round()  # ดึงข้อมูลรอบการประเมินปัจจุบัน

    # ดึงข้อมูล user_evaluation โดยไม่สนใจ request.user
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    # ดึงข้อมูล profile ที่เชื่อมกับ user_evaluation
    profile = evaluation.user.profile

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=user, evr_id=evr_round_obj).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None


    # ตรวจสอบว่า user_evaluation มีข้อมูลในรอบนี้หรือไม่
    user_evaluation_obj, created = user_evaluation.objects.get_or_create(
        user=user,
        evr_id=evr_round_obj,
        defaults={
            'c_gtt': None,
            'c_wl': None,
            'c_sumwl': None,
            'approve_status': False,
            'evaluater_id': None,
            'evaluater_editgtt': None,
            'mc_score': None,
            'sc_score': None,
            'adc_score': None,
            'cp_num': None,
            'cp_score': None,
            'cp_sum': None,
            'cp_main_sum': None,
            'achievement_work': None,
            'performing_work': None,
            'other_work': None,
            'sum_work': None,
            'improved': None,
            'suggestions': None,
            'ac_id': profile.ac_id,
            'administrative_position': profile.administrative_position,
        }
    )

    # ตรวจสอบว่าต้องอัปเดตฟิลด์ ac_id และ administrative_position หรือไม่
    if not created:  # ถ้าไม่ได้สร้างใหม่ อาจจะต้องทำการอัปเดตข้อมูล
        if user_evaluation_obj.ac_id != profile.ac_id or user_evaluation_obj.administrative_position != profile.administrative_position:
            user_evaluation_obj.ac_id = profile.ac_id
            user_evaluation_obj.administrative_position = profile.administrative_position
            user_evaluation_obj.save()

    # ดึงข้อมูลการทำงานของรอบปัจจุบัน
    user_work_current = user_work_info.objects.filter(user=user, round=evr_round_obj).first()
    # ดึงข้อมูลการทำงานในรอบที่ 1
    round_1 = evr_round.objects.filter(evr_round=1, evr_year=(timezone.now().year - 1 if evr_round_obj.evr_round == 2 else timezone.now().year)).first()

    user_work_round_1 = user_work_info.objects.filter(user=user, round=round_1).first() if round_1 else None
    
    # ดึงข้อมูลการลาในรอบปัจจุบันและรอบที่ 1
    def get_or_create_leave(user, round_obj, leave_type):
        leave, created = WorkLeave.objects.get_or_create(
            user=user,
            round=round_obj,
            leave_type=leave_type,
            defaults={'times': 0, 'days': 0}
        )
        return leave

    # สร้างหรือดึงข้อมูลการลาในแต่ละประเภทสำหรับรอบที่ 1 และรอบปัจจุบัน
    sick_leave_round_1 = get_or_create_leave(user, round_1, 'SL') if round_1 else None
    sick_leave_current = get_or_create_leave(user, evr_round_obj, 'SL')

    personal_leave_round_1 = get_or_create_leave(user, round_1, 'PL') if round_1 else None
    personal_leave_current = get_or_create_leave(user, evr_round_obj, 'PL')

    late_round_1 = get_or_create_leave(user, round_1, 'LT') if round_1 else None
    late_current = get_or_create_leave(user, evr_round_obj, 'LT')

    maternity_leave_round_1 = get_or_create_leave(user, round_1, 'ML') if round_1 else None
    maternity_leave_current = get_or_create_leave(user, evr_round_obj, 'ML')

    ordination_leave_round_1 = get_or_create_leave(user, round_1, 'OL') if round_1 else None
    ordination_leave_current = get_or_create_leave(user, evr_round_obj, 'OL')

    longsick_leave_round_1 = get_or_create_leave(user, round_1, 'LSL') if round_1 else None
    longsick_leave_current = get_or_create_leave(user, evr_round_obj, 'LSL')

    adsent_work_round_1 = get_or_create_leave(user, round_1, 'AW') if round_1 else None
    adsent_work_current = get_or_create_leave(user, evr_round_obj, 'AW')

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user)
        extended_form = ExtendedProfileForm(request.POST, instance=profile)
        work_form_current = UserWorkInfoForm(request.POST, instance=user_work_current)

        # ฟอร์มข้อมูลการลา สำหรับรอบที่ 1 (ถ้ามี)
        if round_1:
            sick_leave_round_1_form = WorkLeaveForm(request.POST, instance=sick_leave_round_1, prefix='sick_leave_round_1')
            personal_leave_round_1_form = WorkLeaveForm(request.POST, instance=personal_leave_round_1, prefix='personal_leave_round_1')
            late_round_1_form = WorkLeaveForm(request.POST, instance=late_round_1, prefix='late_round_1')
            maternity_leave_round_1_form = WorkLeaveForm(request.POST, instance=maternity_leave_round_1, prefix='maternity_leave_round_1')
            ordination_leave_round_1_form = WorkLeaveForm(request.POST, instance=ordination_leave_round_1, prefix='ordination_leave_round_1')
            longsick_leave_round_1_form = WorkLeaveForm(request.POST, instance=longsick_leave_round_1, prefix='longsick_leave_round_1')
            adsent_work_round_1_form = WorkLeaveForm(request.POST, instance=adsent_work_round_1, prefix='adsent_work_round_1')

        # ฟอร์มข้อมูลการลา สำหรับรอบที่ 2 (ปัจจุบัน)
        sick_leave_form = WorkLeaveForm(request.POST, instance=sick_leave_current, prefix='sick_leave')
        personal_leave_form = WorkLeaveForm(request.POST, instance=personal_leave_current, prefix='personal_leave')
        late_form = WorkLeaveForm(request.POST, instance=late_current, prefix='late')
        maternity_leave_form = WorkLeaveForm(request.POST, instance=maternity_leave_current, prefix='maternity_leave')
        ordination_leave_form = WorkLeaveForm(request.POST, instance=ordination_leave_current, prefix='ordination_leave')
        longsick_leave_form = WorkLeaveForm(request.POST, instance=longsick_leave_current, prefix='longsick_leave')
        adsent_work_form = WorkLeaveForm(request.POST, instance=adsent_work_current, prefix='adsent_work')

        # ตรวจสอบฟอร์มและบันทึกเฉพาะฟอร์มที่ถูกต้อง
        if profile_form.is_valid():
            profile_form.save()
            extended_profile = extended_form.save(commit=False)
            extended_profile.user = user
            extended_profile.save()

            if work_form_current.is_valid():
                work_instance = work_form_current.save(commit=False)
                work_instance.user = user
                work_instance.round = evr_round_obj
                work_instance.save()

            # ตรวจสอบและบันทึกข้อมูลการลาในรอบที่ 1 (ถ้ามี)
            if round_1:
                form_list_round_1 = [
                    (sick_leave_round_1_form, 'SL'),
                    (personal_leave_round_1_form, 'PL'),
                    (late_round_1_form, 'LT'),
                    (maternity_leave_round_1_form, 'ML'),
                    (ordination_leave_round_1_form, 'OL'),
                    (longsick_leave_round_1_form, 'LSL'),
                    (adsent_work_round_1_form, 'AW')
                ]

                # บันทึกฟอร์มข้อมูลการลาในรอบที่ 1
                for form, leave_type in form_list_round_1:
                    if form.is_valid():
                        # กำหนดค่า leave_type
                        form.instance.leave_type = leave_type
                        form.save()
                    else:
                        print(f"{form.prefix} Form Errors: ", form.errors)

            # ตรวจสอบและบันทึกข้อมูลการลาในรอบที่ 2 (ปัจจุบัน)
            form_list_round_2 = [
                (sick_leave_form, 'SL'),
                (personal_leave_form, 'PL'),
                (late_form, 'LT'),
                (maternity_leave_form, 'ML'),
                (ordination_leave_form, 'OL'),
                (longsick_leave_form, 'LSL'),
                (adsent_work_form, 'AW')
            ]

            # บันทึกฟอร์มข้อมูลการลาในรอบที่ 2 (ปัจจุบัน)
            for form, leave_type in form_list_round_2:
                if form.is_valid():
                    # กำหนดค่า leave_type
                    form.instance.leave_type = leave_type
                    form.save()
                else:
                    print(f"{form.prefix} Form Errors: ", form.errors)

            messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
            return redirect('evaluation_page', evaluation_id=evaluation_id)
        else:
            print("Profile Form Errors: ", profile_form.errors)
            print("Extended Form Errors:", extended_form.errors)
            print("Work Form Errors:", work_form_current.errors)
            if round_1:
                for form, _ in form_list_round_1:
                    print(f"{form.prefix} Form Errors: ", form.errors)
            for form, _ in form_list_round_2:
                print(f"{form.prefix} Form Errors: ", form.errors)
            messages.error(request, "มีข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลอีกครั้ง")
    else:
        # ถ้าเป็นการ GET ให้แสดงฟอร์มปัจจุบัน
        profile_form = UserProfileForm(instance=user)
        extended_form = ExtendedProfileForm(instance=profile)
        work_form_current = UserWorkInfoForm(instance=user_work_current)

        # สร้างฟอร์มสำหรับ round 1 เฉพาะเมื่อ round_1 มีข้อมูล
        if round_1:
            sick_leave_round_1_form = WorkLeaveForm(instance=sick_leave_round_1, prefix='sick_leave_round_1')
            personal_leave_round_1_form = WorkLeaveForm(instance=personal_leave_round_1, prefix='personal_leave_round_1')
            late_round_1_form = WorkLeaveForm(instance=late_round_1, prefix='late_round_1')
            maternity_leave_round_1_form = WorkLeaveForm(instance=maternity_leave_round_1, prefix='maternity_leave_round_1')
            ordination_leave_round_1_form = WorkLeaveForm(instance=ordination_leave_round_1, prefix='ordination_leave_round_1')
            longsick_leave_round_1_form = WorkLeaveForm(instance=longsick_leave_round_1, prefix='longsick_leave_round_1')
            adsent_work_round_1_form = WorkLeaveForm(instance=adsent_work_round_1, prefix='adsent_work_round_1')

        sick_leave_form = WorkLeaveForm(instance=sick_leave_current, prefix='sick_leave')
        personal_leave_form = WorkLeaveForm(instance=personal_leave_current, prefix='personal_leave')
        late_form = WorkLeaveForm(instance=late_current, prefix='late')
        maternity_leave_form = WorkLeaveForm(instance=maternity_leave_current, prefix='maternity_leave')
        ordination_leave_form = WorkLeaveForm(instance=ordination_leave_current, prefix='ordination_leave')
        longsick_leave_form = WorkLeaveForm(instance=longsick_leave_current, prefix='longsick_leave')
        adsent_work_form = WorkLeaveForm(instance=adsent_work_current, prefix='adsent_work')

    # ตรวจสอบว่า uevr_id มีค่าหรือไม่เพื่อสร้าง URL สำหรับอัปโหลดไฟล์
    upload_url = reverse('upload_evidence', args=[user_evaluation_obj.uevr_id]) if user_evaluation_obj.uevr_id else None

    context = {
        'profile_form': profile_form,
        'extended_form': extended_form,
        'work_form_current': work_form_current,
        'user_work_round_1': user_work_round_1,
        'evr_round': evr_round_obj,
        'profile': profile,
        'user_evaluation_agreement': user_evaluation_agreement_obj,
        'user_evaluation_agreement_year_thai': user_evaluation_agreement_obj.year + 543,
        'selected_group': selected_group,
        'user_evaluation': user_evaluation_obj,
        'upload_url': upload_url,
        'evaluation_id': evaluation_id,
        'evaluation': evaluation,
        # ข้อมูลการลา round 1
        **({'sick_leave_round_1_form': sick_leave_round_1_form,
            'personal_leave_round_1_form': personal_leave_round_1_form,
            'late_round_1_form': late_round_1_form,
            'maternity_leave_round_1_form': maternity_leave_round_1_form,
            'ordination_leave_round_1_form': ordination_leave_round_1_form,
            'longsick_leave_round_1_form': longsick_leave_round_1_form,
            'adsent_work_round_1_form': adsent_work_round_1_form} if round_1 else {}),
        # ข้อมูลการลา round 2 (ปัจจุบัน)
        'sick_leave_form': sick_leave_form,
        'personal_leave_form': personal_leave_form,
        'late_form': late_form,
        'maternity_leave_form': maternity_leave_form,
        'ordination_leave_form': ordination_leave_form,
        'longsick_leave_form': longsick_leave_form,
        'adsent_work_form': adsent_work_form,
    }

    return render(request, 'app_evaluation/evaluation_page.html', context)


@login_required
def evaluation_page_2(request, evaluation_id):
    user = request.user
    evr_round_obj = get_evr_round()

    # ดึงข้อมูล user_evaluation ที่สัมพันธ์กับ evaluation_id
    try:
        user_evaluation_obj = user_evaluation.objects.get(pk=evaluation_id, user=user)
    except user_evaluation.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลการประเมิน")
        return redirect('select_group')

    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    # ดึง selected_group ที่สัมพันธ์กับ user ผ่าน user_evaluation_agreement
    try:
        selected_group = user_evaluation_agreement.objects.get(user=user, evr_id=user_evaluation_obj.evr_id).g_id
    except user_evaluation_agreement.DoesNotExist:
        selected_group = None

    # ดึงข้อมูล f_id ที่เชื่อมโยงกับ group_detail ของ selected_group
    if selected_group:
        fields = wl_field.objects.filter(group_detail__g_id=selected_group).distinct()
    else:
        fields = wl_field.objects.none()

    # ดึงข้อมูล subfield ที่เกี่ยวข้องกับ field
    subfields = wl_subfield.objects.filter(f_id__in=fields)

    # ดึง workload criteria ที่เชื่อมโยงกับ subfield
    workload_criteria = WorkloadCriteria.objects.filter(sf_id__in=subfields)

    # ดึง workload ที่เชื่อมโยงกับ evaluation
    
    for subfield in subfields:
        workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)
        for selection in workload_selections:
            print(f"Selection sf_id: {selection.sf_id}, Subfield sf_id: {subfield.sf_id}")

    
    # คำนวณค่า min_workload จากข้อมูล group
    min_workload = group.objects.filter(g_id=selected_group.g_id).values_list('g_max_workload', flat=True).first()
    if not min_workload:
        min_workload = 35  # ตั้งค่า default ถ้าไม่มีข้อมูล

    # คำนวณผลรวมของ calculated_workload
    total_workload = sum(selection.calculated_workload for selection in workload_selections)

    # ดึง c_wl ที่สูงที่สุดจาก user_evaluation
    max_workload = user_evaluation.objects.filter( evr_id=user_evaluation_obj.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0

    # คำนวณส่วนต่างคะแนนภาระงาน
    evaluation.c_wl = total_workload
    
    workload_difference = max_workload - total_workload
    workload_difference_score = workload_difference * (28 / 115)
    achievement_work = 70 - workload_difference_score

    
    evaluation.achievement_work = round(achievement_work, 2)
    evaluation.save()


    context = {
        'user_evaluation': user_evaluation_obj,
          # ส่ง formsets ไปยัง template
        'fields': fields,
        
        'evaluation': evaluation,
        'workload_selections': workload_selections,
        'subfields': subfields,  # ตรวจสอบให้แน่ใจว่าส่งค่า sf_id
        'total_workload': total_workload,  # ส่งผลรวมไปยังเทมเพลตเพื่อแสดง
        'achievement_work': evaluation.achievement_work,
        'evaluation_id': evaluation_id,
        'min_workload': min_workload,
    }

    return render(request, 'app_evaluation/evaluation_page_2.html', context)

@login_required
def select_subfields(request, f_id, evaluation_id):
    field = get_object_or_404(wl_field, pk=f_id)
    subfields = wl_subfield.objects.filter(f_id=field)

    # ดึงข้อมูลการประเมินที่สอดคล้องกับ evaluation_id
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    if request.method == 'POST':
        selected_sf_id = request.POST.get('sf_id')  # ใช้ get() เพื่อดึงค่า sf_id จากฟอร์ม
        if selected_sf_id:
            selected_sf = wl_subfield.objects.get(sf_id=selected_sf_id)
            # เพิ่มข้อมูล evaluation เข้าไปในการสร้าง UserSelectedSubField
            UserSelectedSubField.objects.create(
                user=request.user,
                evaluation=evaluation,  # เชื่อม evaluation
                f_id=field,
                sf_id=selected_sf
            )
            return redirect('evaluation_page_2', evaluation_id=evaluation_id)

    context = {
        'field': field,
        'subfields': subfields,
        'evaluation_id': evaluation_id,
    }
    return render(request, 'app_evaluation/select_subfields.html', context)

@login_required
def delete_selected_subfield(request, sf_id):
    # ตรวจสอบว่ามีการส่ง evaluation_id มาหรือไม่
    evaluation_id = request.POST.get('evaluation_id') or request.GET.get('evaluation_id')
    print(f"evaluation_id from POST: {request.POST.get('evaluation_id')}")
    print(f"evaluation_id from GET: {request.GET.get('evaluation_id')}")

    if not evaluation_id:
        messages.error(request, "ไม่พบ evaluation_id")
        return redirect('select_group')

    try:
        # ลบข้อมูลทั้งหมดใน UserSelectedSubField ที่มี sf_id
        selected_subfields = UserSelectedSubField.objects.filter(sf_id=sf_id)

        if not selected_subfields.exists():
            messages.error(request, 'ไม่พบ Subfield ที่คุณพยายามจะลบ.')
            return redirect('evaluation_page_2', evaluation_id=evaluation_id)

        if request.method == 'POST':
            # ลบข้อมูลที่ค้นหาได้ทั้งหมด
            selected_subfields.delete()
            messages.success(request, 'ลบ Subfield เรียบร้อยแล้ว!')
            return redirect('evaluation_page_2', evaluation_id=evaluation_id)

    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
        return redirect('evaluation_page_2', evaluation_id=evaluation_id)

    return redirect('evaluation_page_2', evaluation_id=evaluation_id)

@login_required
def select_workload_criteria(request, evaluation_id, sf_id):
    # ดึงข้อมูล evaluation และ subfield ที่เกี่ยวข้อง
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    subfield = get_object_or_404(wl_subfield, pk=sf_id)
    
    # สร้างฟอร์มและส่งค่า subfield ไปยังฟอร์มเพื่อกรองข้อมูลใน selected_id
    criteria_form = UserWorkloadSelectionForm(initial={'sf_id': subfield}, subfield=subfield)

    # ตรวจสอบการส่งฟอร์ม
    if request.method == 'POST':
        criteria_form = UserWorkloadSelectionForm(request.POST, subfield=subfield)
        
        if criteria_form.is_valid():
            new_criteria = criteria_form.save(commit=False)
            new_criteria.sf_id = subfield
            new_criteria.evaluation = evaluation
            new_criteria.user = request.user

            try:
                # แปลงค่าทั้งหมดเป็น float ก่อนทำการคำนวณ
                selected_num = float(new_criteria.selected_num)
                selected_maxnum = float(new_criteria.selected_maxnum)
                selected_workload = float(new_criteria.selected_workload)

                # คำนวณค่า calculated_workload
                if selected_maxnum == 0:
                    calculated_workload = selected_num * selected_workload
                else:
                    calculated_workload = min(selected_num, selected_maxnum) * selected_workload

                # บันทึกค่า calculated_workload ลงใน new_criteria
                new_criteria.calculated_workload = calculated_workload
                new_criteria.save()

                # คำนวณค่าใหม่หลังการเพิ่มภาระงาน
                workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)

                total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)
                total_workload = sum(selection.calculated_workload for selection in workload_selections)

                max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(Max('c_wl'))['c_wl__max'] or 0
                max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(Max('c_gtt'))['c_gtt__max'] or 0

                # อัปเดตค่าใน evaluation
                evaluation.c_wl = total_workload
                evaluation.c_gtt = total_workload_edit

                workload_difference = max_workload - evaluation.c_wl
                workload_difference_score = workload_difference * (28 / 115)
                achievement_work = 70 - workload_difference_score
                evaluation.achievement_work = round(achievement_work, 1)

                workload_difference_edit = max_workload_edit - evaluation.c_gtt
                workload_difference_score_edit = workload_difference_edit * (28 / 115)
                c_sumwl = 70 - workload_difference_score_edit
                evaluation.c_sumwl = round(c_sumwl, 1)

                evaluation.save()

                messages.success(request, f'เพิ่มภาระงานใหม่เรียบร้อยแล้ว! คำนวณภาระงาน: {calculated_workload:.2f}')
                return redirect('evaluation_page_2', evaluation_id=evaluation_id)

            except ValueError as e:
                # ถ้ามีข้อผิดพลาดในการแปลงค่า แสดงใน log
                print(f"ValueError: {e}")
                messages.error(request, 'ไม่สามารถคำนวณค่าได้ โปรดตรวจสอบข้อมูลที่กรอก.')

    print(criteria_form.errors)

    # ส่งข้อมูลไปยังเทมเพลต
    context = {
        'evaluation': evaluation,
        'subfield': subfield,
        'criteria_form': criteria_form,
    }
    return render(request, 'app_evaluation/select_workload_criteria.html', context)

@login_required
def edit_workload_selection(request, selection_id):
    selection = get_object_or_404(UserWorkloadSelection, pk=selection_id)

    if request.method == 'POST':
        form = UserWorkloadSelectionForm1(request.POST, instance=selection)
        evaluation_id = selection.evaluation.uevr_id
        if form.is_valid():
            # ถ้าฟอร์มถูกต้อง ให้บันทึกการเปลี่ยนแปลง
            if selection.selected_maxnum == 0:
                selection.calculated_workload = selection.selected_num * selection.selected_workload
            else:
                if selection.selected_num <= selection.selected_maxnum:
                    selection.calculated_workload = selection.selected_num  * selection.selected_workload
                else:
                    selection.calculated_workload = selection.selected_maxnum * selection.selected_workload
            form.save()
            evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
            workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)
            max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_gtt'))['max_workload'] or 0
            max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0
            
            # คำนวณค่าที่เกี่ยวข้องใหม่หลังจากการลบ
            total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)
            total_workload = sum(selection.calculated_workload for selection in workload_selections)
            
            evaluation.c_wl = total_workload
            evaluation.c_gtt = total_workload_edit
            # คำนวณค่า c_sumwl ใหม่
            workload_difference = max_workload - evaluation.c_wl
            workload_difference_score = workload_difference * (28 / 115)
            achievement_work = 70 - workload_difference_score
            evaluation.achievement_work = round(achievement_work, 1)

            workload_difference_edit = max_workload_edit - total_workload_edit
            workload_difference_score_edit = workload_difference_edit * (28 / 115)
            c_sumwl = 70 - workload_difference_score_edit
            evaluation.c_sumwl = round(c_sumwl, 1)

            evaluation.save()
            messages.success(request, 'แก้ไขภาระงานเรียบร้อยแล้ว!')
            return redirect('evaluation_page_2', evaluation_id=selection.evaluation.uevr_id)
        else:
            messages.error(request, 'กรุณาเลือกข้อมูลภาระงานให้ครบถ้วน.')
    else:
        form = UserWorkloadSelectionForm1(instance=selection)

    return render(request, 'app_evaluation/edit_workload_selection.html', {
        'form': form,
        'selection': selection,
    })

@login_required
def delete_workload_selection(request, selection_id):
    selection = get_object_or_404(UserWorkloadSelection, pk=selection_id)

    if request.method == 'POST':
        evaluation_id = selection.evaluation.uevr_id
        # ลบเฉพาะการเชื่อมโยงกับ UserWorkloadSelection
        selection.delete()  
        # คำนวณผลรวมของ calculated_workload
        evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
        workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)
        max_workload_edit = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_gtt'))['max_workload'] or 0
        max_workload = user_evaluation.objects.filter(evr_id=evaluation.evr_id).aggregate(max_workload=Max('c_wl'))['max_workload'] or 0
        
        # คำนวณค่าที่เกี่ยวข้องใหม่หลังจากการลบ
        total_workload_edit = sum(selection.selected_workload_edit for selection in workload_selections)
        total_workload = sum(selection.calculated_workload for selection in workload_selections)
        
        evaluation.c_wl = total_workload
        evaluation.c_gtt = total_workload_edit
        # คำนวณค่า c_sumwl ใหม่
        workload_difference = max_workload - evaluation.c_wl
        workload_difference_score = workload_difference * (28 / 115)
        achievement_work = 70 - workload_difference_score
        evaluation.achievement_work = round(achievement_work, 1)

        workload_difference_edit = max_workload_edit - total_workload_edit
        workload_difference_score_edit = workload_difference_edit * (28 / 115)
        c_sumwl = 70 - workload_difference_score_edit
        evaluation.c_sumwl = round(c_sumwl, 1)

        evaluation.save()
        messages.success(request, 'ลบภาระงานเรียบร้อยแล้ว!')
        return redirect('evaluation_page_2', evaluation_id=selection.evaluation.uevr_id)

    return render(request, 'app_evaluation/confirm_delete.html', {
        'selection': selection,
    })

@login_required
def show_all_evidence(request, selection_id):
    # ดึงข้อมูล WorkloadSelection โดยใช้ selection_id
    selection = get_object_or_404(UserWorkloadSelection, pk=selection_id)

    # ดึงข้อมูลหลักฐานทั้งหมดที่เชื่อมโยงกับ selection
    evidences = user_evident.objects.filter(uwls_id=selection)

    return render(request, 'app_evaluation/show_all_evidence.html', {
        'selection': selection,
        'evidences': evidences,
    })

def get_subfields(request, f_id):
    subfields = wl_subfield.objects.filter(f_id=f_id)
    subfield_list = [{'id': sf.id, 'name': sf.sf_name} for sf in subfields]
    return JsonResponse(subfield_list, safe=False)


def get_criteria(request, sf_id):
    criteria = WorkloadCriteria.objects.filter(sf_id=sf_id)
    criteria_list = [{'id': c.id, 'name': c.c_name} for c in criteria]
    return JsonResponse(criteria_list, safe=False)


@login_required
def evaluation_page_3(request, evaluation_id):
    user = request.user
    
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        messages.error(request, "กรุณากรอกข้อมูลโปรไฟล์ก่อนทำการประเมิน")
        return redirect('profile')

    evr_round_obj = get_evr_round()

    # ดึงข้อมูล user_evaluation ที่สัมพันธ์กับ evaluation_id
    try:
        user_evaluation_obj = user_evaluation.objects.get(uevr_id=evaluation_id)
    except user_evaluation.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลการประเมินที่เลือก")
        return redirect('evaluation_page', evaluation_id=evaluation_id)

    # ดึงข้อมูล competencies
    main_competencies = main_competency.objects.filter(mc_type=user_evaluation_obj.ac_id.ac_name)
    specific_competencies = specific_competency.objects.filter(sc_type=user_evaluation_obj.ac_id.ac_name)
    administrative_competencies = None  # ตั้งค่าเริ่มต้นเป็น None
    
    # เช็คว่าถ้ามีตำแหน่งบริหารและไม่ใช่ "-"
    if user_evaluation_obj.administrative_position and user_evaluation_obj.administrative_position != "-":
        administrative_competencies = administrative_competency.objects.filter()

    # ตรวจสอบการส่งข้อมูล POST
    if request.method == 'POST':
        # วนลูปผ่าน main_competencies
        for competency in main_competencies:
            actual_score = request.POST.get(f'main_actual_score_{competency.mc_id}')
            if actual_score and actual_score.isdigit():
                actual_score = int(actual_score)
                user_competency_main.objects.update_or_create(
                    evaluation=user_evaluation_obj,
                    mc_id=competency,
                    evr_id=evr_round_obj,
                    defaults={'user': user, 'umc_name': competency.mc_name, 'umc_type': competency.mc_type, 'actual_score': actual_score}
                )

        # วนลูปผ่าน specific_competencies
        for competency in specific_competencies:
            actual_score = request.POST.get(f'specific_actual_score_{competency.sc_id}')
            if actual_score and actual_score.isdigit():
                actual_score = int(actual_score)
                user_competency_councilde.objects.update_or_create(
                    evaluation=user_evaluation_obj,
                    sc_id=competency,
                    evr_id=evr_round_obj,
                    defaults={'user': user, 'ucc_name': competency.sc_name, 'ucc_type': competency.sc_type, 'actual_score': actual_score}
                )

        # วนลูปผ่าน administrative_competencies ถ้าไม่เป็น None
        if administrative_competencies is not None:
            for competency in administrative_competencies:
                actual_score = request.POST.get(f'admin_actual_score_{competency.adc_id}')
                uceo_num = request.POST.get(f'admin_uceo_num_{competency.adc_id}') 
                if actual_score and actual_score.isdigit():
                    actual_score = int(actual_score)
                    uceo_num = int(uceo_num) if uceo_num.isdigit() else 0
                    user_competency_ceo.objects.update_or_create(
                        evaluation=user_evaluation_obj,
                        adc_id=competency,
                        evr_id=evr_round_obj,
                        defaults={'user': user, 'uceo_name': competency.adc_name, 'uceo_type': competency.adc_type, 'actual_score': actual_score,'uceo_num': uceo_num }
                    )

        messages.success(request, "บันทึกคะแนนเรียบร้อยแล้ว!")
        return redirect('evaluation_page_3', evaluation_id=evaluation_id)

    # ดึงข้อมูลคะแนนที่เคยกรอก
    main_scores = user_competency_main.objects.filter(evaluation=user_evaluation_obj)
    specific_scores = user_competency_councilde.objects.filter(evaluation=user_evaluation_obj)
    administrative_scores = user_competency_ceo.objects.filter(evaluation=user_evaluation_obj)

    # เก็บจำนวนสมรรถนะที่ได้คะแนนตามเงื่อนไขต่าง ๆ
    score_count = {3: 0, 2: 0, 1: 0, 0: 0}

    # คำนวณคะแนนสำหรับ main competencies
    main_competency_total = 0
    for score in main_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.mc_id.mc_num)
        score_count[calculated_score] += 1
        main_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ specific competencies
    specific_competency_total = 0
    for score in specific_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.sc_id.sc_num)
        score_count[calculated_score] += 1
        specific_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ administrative competencies ถ้าไม่เป็น None
    administrative_competency_total = 0
    if administrative_competencies is not None:
        for score in administrative_scores:
            calculated_score = calculate_competency_score(score.actual_score, score.uceo_num)
            score_count[calculated_score] += 1
            administrative_competency_total += calculated_score

    # ผลรวมคะแนนทั้งหมด
    total_score = main_competency_total + specific_competency_total + administrative_competency_total

    # คำนวณคะแนนในแต่ละกรณี (คูณ 3, 2, 1 และ 0)
    score_3_total = score_count[3] * 3
    score_2_total = score_count[2] * 2
    score_1_total = score_count[1] * 1
    score_0_total = score_count[0] * 0

    # คำนวณค่ารวมของคะแนนที่คาดหวังสำหรับแต่ละตาราง
    main_max_num = sum([c.mc_num for c in main_competencies])
    specific_max_num = sum([c.sc_num for c in specific_competencies])
    administrative_max_num = sum([score.uceo_num for score in administrative_scores]) if administrative_competencies is not None else 0

    # คำนวณคะแนนจากสูตร
    total_max_num = main_max_num + specific_max_num + administrative_max_num

    calculated_score = 0
    if total_max_num > 0:
        calculated_score = (total_score / total_max_num) * 30


    print(f"Total Score: {total_score}")
    print(f"Total Max Num: {total_max_num}")

    # บันทึก calculated_score ใน mc_score ของ user_evaluation
    user_evaluation_obj.mc_score = calculated_score
    user_evaluation_obj.save()
    
    context = {
        'profile': profile,
        'main_competencies': main_competencies,
        'specific_competencies': specific_competencies,
        'administrative_competencies': administrative_competencies,
        'main_scores': main_scores,
        'specific_scores': specific_scores,
        'administrative_scores': administrative_scores,
        'main_competency_total': main_competency_total,
        'specific_competency_total': specific_competency_total,
        'administrative_competency_total': administrative_competency_total,
        'total_score': total_score,
        'total_max_num': total_max_num,
        'count_3': score_count[3],
        'count_2': score_count[2],
        'count_1': score_count[1],
        'count_0': score_count[0],
        'score_3_total': score_3_total,
        'score_2_total': score_2_total,
        'score_1_total': score_1_total,
        'score_0_total': score_0_total,
        'main_max_num': main_max_num,
        'specific_max_num': specific_max_num,
        'administrative_max_num': administrative_max_num,
        'calculated_score': calculated_score,
        'evaluation_id': evaluation_id,
    }

    return render(request, 'app_evaluation/evaluation_page_3.html', context)

@login_required
def upload_evidence(request, criteria_id):
    criteria = get_object_or_404(UserWorkloadSelection, pk=criteria_id)
    evaluation = criteria.evaluation  # ดึงค่า evaluation จาก UserWorkloadSelection

    if request.method == 'POST':
        form = UserEvidentForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        pictures = request.FILES.getlist('picture')
        filenames = request.POST.getlist('filename')  # รับรายชื่อไฟล์ที่ผู้ใช้กรอกเข้ามา

        if form.is_valid():
            # บันทึกไฟล์ PDF และ DOCX
            for index, file in enumerate(files):
                custom_filename = filenames[index] if index < len(filenames) and filenames[index] else file.name
                new_filename = f"{uuid.uuid4()}_{custom_filename}"

                evidence = user_evident(
                    uwls_id=criteria,
                    uevr_id=evaluation,
                    file=file,
                    filename=new_filename
                )
                evidence.save()

            # ลดขนาดรูปภาพก่อนบันทึก
            for index, picture in enumerate(pictures):
                custom_filename = filenames[index] if index < len(filenames) and filenames[index] else picture.name
                new_filename = f"{uuid.uuid4()}_{custom_filename}"

                image = Image.open(picture)
                max_size = (1366, 800)
                image.thumbnail(max_size)
                img_io = ContentFile(b'')
                image_format = image.format or 'JPEG'
                image.save(img_io, format=image_format)

                file_name = default_storage.save(f"uploads/{new_filename}", img_io)
                evidence = user_evident(
                    uwls_id=criteria,
                    uevr_id=evaluation,
                    picture=file_name,
                    filename=new_filename
                )
                evidence.save()

            messages.success(request, "อัปโหลดไฟล์เรียบร้อยแล้ว!")
            return redirect('upload_evidence', criteria_id=criteria_id)

    else:
        form = UserEvidentForm()

    evidences = user_evident.objects.filter(uwls_id=criteria)

    return render(request, 'app_evaluation/upload_evidence.html', {
        'form': form,
        'evidences': evidences,
        'criteria': criteria
    })

@login_required
def delete_evidence(request, evidence_id):
    evidence = get_object_or_404(user_evident, uevd_id=evidence_id)

    # ลบไฟล์หรือรูปภาพที่เกี่ยวข้องจากระบบ
    if evidence.file:
        if os.path.isfile(evidence.file.path):
            os.remove(evidence.file.path)  # ลบไฟล์จาก storage
    if evidence.picture:
        if os.path.isfile(evidence.picture.path):
            os.remove(evidence.picture.path)  # ลบรูปภาพจาก storage

    # ลบรายการ evidence จากฐานข้อมูล
    evidence.delete()
    messages.success(request, "ลบไฟล์/รูปภาพเรียบร้อยแล้ว!")
    
    # ใช้ `redirect` ให้ไปยัง `upload_evidence` โดยใช้ `criteria_id`
    return redirect('upload_evidence', criteria_id=evidence.uwls_id.id)  # เปลี่ยน `evaluation_id` เป็น `criteria_id`

@login_required
def evaluation_page_4(request, evaluation_id):
    # Get the current user
    user = request.user

    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    # Fetch evaluation object based on ID
    try:
        user_evaluation_obj = user_evaluation.objects.get(pk=evaluation_id, user=user)
    except user_evaluation.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลการประเมิน")
        return redirect('select_group')
    
    # ตรวจสอบการร้องขอจากผู้ใช้
    if request.method == 'POST':
        # ดึงข้อมูลจากฟอร์มที่ถูกส่งมา
        remark_achievement = request.POST.get('remark_achievement')
        remark_mc = request.POST.get('remark_mc')
        remark_other = request.POST.get('remark_other')
        remark_total = request.POST.get('remark_total')

        # บันทึกข้อมูลหมายเหตุ (อาจเพิ่มฟิลด์ใน model `user_evaluation` สำหรับบันทึกหมายเหตุ)
        evaluation.remark_achievement = remark_achievement
        evaluation.remark_mc = remark_mc
        evaluation.remark_other = remark_other
        evaluation.remark_total = remark_total

        evaluation.save()  # บันทึกการเปลี่ยนแปลง

        messages.success(request, 'บันทึกหมายเหตุเรียบร้อยแล้ว!')
        return redirect('evaluation_page_4', evaluation_id=evaluation_id)
    

    # Any specific business logic for `evaluation_page_4`
    # Example: Calculate totals, aggregate scores, etc.
    achievement_work = user_evaluation_obj.achievement_work or 0
    mc_score = user_evaluation_obj.mc_score or 0
    total_score = achievement_work + mc_score

    print(f"Achievement Work: {achievement_work}, MC Score: {mc_score}, Total Score: {total_score}")


    if total_score >= 90:
        level = 'ดีเด่น'
    elif total_score >= 80:
        level = 'ดีมาก'
    elif total_score >= 70:
        level = 'ดี'
    elif total_score >= 60:
        level = 'พอใช้'
    else:
        level = 'ต้องปรับปรุง'

    print(f"Total Score: {total_score}, Level: {level}")

    # Context to pass to template
    context = {
        'user_evaluation': user_evaluation_obj,
        'achievement_work': user_evaluation_obj.achievement_work,  # Achievement work value
        'mc_score': user_evaluation_obj.mc_score,
        'total_score': total_score,
        'level': level,
        'remark_achievement': evaluation.remark_achievement,
        'remark_mc': evaluation.remark_mc,
        'remark_other': evaluation.remark_other,
        'remark_total': evaluation.remark_total,
        'evaluation_id': evaluation_id,
        # Add more variables as needed
    }

    return render(request, 'app_evaluation/evaluation_page_4.html', context)

@login_required
def evaluation_page_5(request, evaluation_id):
    # Fetch the evaluation object
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id, user=request.user)

    # Initialize form and formset
    PersonalDiagramFormset = modelformset_factory(PersonalDiagram, fields=('skill_evol', 'dev', 'dev_time'), extra=0)
    
    form = UserEvaluationForm(instance=evaluation)
    formset = PersonalDiagramFormset(queryset=PersonalDiagram.objects.filter(uevr_id=evaluation))

    if request.method == 'POST':
        if 'save_form' in request.POST:
            # If 'save_form' button is clicked
            form = UserEvaluationForm(request.POST, instance=evaluation)
            if form.is_valid():
                form.save()
                messages.success(request, "บันทึกข้อมูลการประเมินสำเร็จ!")
            else:
                messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลที่กรอก")
        
        elif 'save_formset' in request.POST:
            # If 'save_formset' button is clicked
            formset = PersonalDiagramFormset(request.POST)
            if formset.is_valid():
                formset.save()
                messages.success(request, "บันทึกข้อมูลฟอร์มสำเร็จ!")
            else:
                messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาตรวจสอบข้อมูลที่กรอก")

    context = {
        'form': form,
        'formset': formset,
        'evaluation_id': evaluation_id,
        'evaluation':evaluation,
    }
    return render(request, 'app_evaluation/evaluation_page_5.html', context)

@login_required
def save_full_name_and_current_date(request, evaluation_id):
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id, user=request.user)
    if request.method == 'POST':
        # ดึงข้อมูลชื่อ-นามสกุลจาก evaluation
        full_name = f"{evaluation.user.first_name} {evaluation.user.last_name}"
        
        # ใช้ timezone.now() เพื่อดึงวันที่ปัจจุบันที่รองรับ timezone
        current_date = timezone.now()

        # แปลงปีเป็น พ.ศ.
        thai_year = current_date.year + 543

        # บันทึกค่าลงในฟิลด์ที่แยกเป็น วัน เดือน ปี
        evaluation.start_day = current_date.day
        evaluation.start_month = current_date.month
        evaluation.start_year = thai_year  # บันทึกปีเป็น พ.ศ.

        # บันทึกชื่อเต็มลงในฟิลด์ full_name
        evaluation.full_name = full_name
        
        # บันทึกวันที่ลงใน evaluation (ถ้าอยากบันทึกใน created_at ต้องเปลี่ยนฟิลด์นี้เป็น null=True, blank=True)
        evaluation.created_at = current_date
        evaluation.save()

        # แปลงวันที่เป็นรูปแบบไทย (เช่น วัน/เดือน/ปี)
        thai_date_str = f"{current_date.day}/{current_date.month}/{thai_year}"

        # ส่งข้อความสำเร็จพร้อมแสดงวันที่ในรูปแบบไทย
        messages.success(request, f"บันทึกชื่อ-นามสกุล: {full_name} และวันที่ {thai_date_str} เรียบร้อยแล้ว")
        
        return redirect('evaluation_page_5', evaluation_id=evaluation_id)

@login_required
def add_personal_diagram(request, evaluation_id):
    # ดึง user_evaluation ตาม evaluation_id
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)

    if request.method == 'POST':
        form = PersonalDiagramForm(request.POST)
        if form.is_valid():
            personal_diagram = form.save(commit=False)
            personal_diagram.uevr_id = evaluation  # เชื่อมโยงกับ user_evaluation
            personal_diagram.save()
            messages.success(request, 'เพิ่มข้อมูลแผนพัฒนาสำเร็จ!')
            # กลับไปยังหน้า evaluation_page_5
            return redirect('evaluation_page_5', evaluation_id=evaluation_id)
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการบันทึก กรุณาตรวจสอบข้อมูล.')
    else:
        form = PersonalDiagramForm()

    context = {
        'form': form,
        'evaluation_id': evaluation_id,
    }
    return render(request, 'app_evaluation/add_personal_diagram.html', context)


@login_required
def edit_personal_diagram(request, pd_id):
    # ดึงข้อมูล PersonalDiagram ที่ต้องการแก้ไข
    personal_diagram = get_object_or_404(PersonalDiagram, pk=pd_id)

    if request.method == 'POST':
        form = PersonalDiagramForm(request.POST, instance=personal_diagram)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลแผนพัฒนาสำเร็จ!')
            # กลับไปยังหน้า evaluation_page_5
            return redirect('evaluation_page_5', evaluation_id=personal_diagram.uevr_id.uevr_id)
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการแก้ไข กรุณาตรวจสอบข้อมูล.')
    else:
        form = PersonalDiagramForm(instance=personal_diagram)

    context = {
        'form': form,
        'evaluation_id': personal_diagram.uevr_id.uevr_id,
    }
    return render(request, 'app_evaluation/edit_personal_diagram.html', context)

@login_required
def delete_personal_diagram(request, pd_id):
    # ดึงข้อมูล PersonalDiagram ที่ต้องการลบ
    personal_diagram = get_object_or_404(PersonalDiagram, pk=pd_id)

    # ตรวจสอบคำขอเป็น POST ก่อนทำการลบ
    if request.method == 'POST':
        # เก็บ evaluation_id ก่อนลบ เพื่อ redirect กลับไปที่หน้า evaluation_page_5
        evaluation_id = personal_diagram.uevr_id.uevr_id
        personal_diagram.delete()
        messages.success(request, 'ลบข้อมูลแผนพัฒนาสำเร็จ!')
        return redirect('evaluation_page_5', evaluation_id=evaluation_id)

    # ในกรณีที่ไม่ใช่ POST ให้กลับไปที่ evaluation_page_5
    return redirect('evaluation_page_5', evaluation_id=personal_diagram.uevr_id.uevr_id)

@login_required
def evaluation_page_6(request, evaluation_id):
    # Fetch the evaluation object
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id, user=request.user)

    context = {
        'evaluation_id': evaluation_id,
        'evaluation':evaluation,
    }

    return render(request,'app_evaluation/evaluation_page_6.html', context)

@login_required
def update_evr_status(request, evaluation_id):
    # Fetch the user_evaluation object
    user_evaluation_obj = get_object_or_404(user_evaluation, pk=evaluation_id)

    # Fetch the related evr_round object
    evr_round_obj = user_evaluation_obj.evr_id

    # Check request method and update evr_status
    if request.method == 'POST':
        evr_round_obj.evr_status = True  # or the desired status
        evr_round_obj.save()
        messages.success(request, 'สถานะการประเมินถูกอัพเดตเรียบร้อยแล้ว')
    
    # Redirect back to the evaluation page
    return redirect('search_evaluations')

@login_required
def update_evr_status2(request, evaluation_id):
    # Fetch the user_evaluation object
    user_evaluation_obj = get_object_or_404(user_evaluation, pk=evaluation_id)

    # Fetch the related evr_round object
    evr_round_obj = user_evaluation_obj.evr_id

    # Check request method and update evr_status
    if request.method == 'POST':
        evr_round_obj.evr_status = True  # or the desired status
        evr_round_obj.save()
        messages.success(request, 'สถานะการประเมินถูกอัพเดตเรียบร้อยแล้ว')
    
    # Redirect back to the evaluation page
    return redirect('search_evaluations_2')

@login_required
def toggle_approve_status(request, evaluation_id):
    # ดึงข้อมูล user_evaluation จาก evaluation_id
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    
    # เปลี่ยนสถานะ approve_status
    evaluation.approve_status = not evaluation.approve_status
    evaluation.save()
    
    # ส่งข้อความแสดงผลสำเร็จ
    messages.success(request, f"เปลี่ยนสถานะการอนุมัติสำเร็จเป็น {'อนุมัติ' if evaluation.approve_status else 'ไม่อนุมัติ'}")
    
    # กลับไปยังหน้าที่ต้องการ (เช่น หน้ารายการการประเมิน)
    return redirect('search_evaluations_2')  # แก้ไข URL name ให้ตรงกับ project ของคุณ



@login_required
def eval_2(request):
    return render(request,'app_evaluation/evaluation2.html')

@login_required
def eval_3(request):
    return render(request,'app_evaluation/evaluation3.html')

@login_required
def eval_4(request):
    return render(request,'app_evaluation/evaluation4.html')

@login_required
def eval_5(request):
    return render(request,'app_evaluation/evaluation5.html')


from django.views.decorators.http import require_GET
@require_GET
def get_c_unit(request):
    selected_id = request.GET.get('selected_id')
    data = {}
    if selected_id:
        try:
            workload_criteria = WorkloadCriteria.objects.get(pk=selected_id)
            data['c_unit'] = workload_criteria.c_unit or '-'
        except WorkloadCriteria.DoesNotExist:
            data['error'] = "Workload criteria not found."
    else:
        data['error'] = "No selected_id provided."
    return JsonResponse(data)




@login_required
def print_evaluation_pdf(request, evaluation_id):
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    user = evaluation.user
    profile = evaluation.user.profile


    # ฟังก์ชันสำหรับการดึงข้อมูลการลาในแต่ละรอบ
    def get_or_create_leave(user, round_obj, leave_type):
        leave, created = WorkLeave.objects.get_or_create(
            user=user,
            round=round_obj,
            leave_type=leave_type,
            defaults={'times': 0, 'days': 0}
        )
        return leave
    

    # ดึงข้อมูลการลา
    evr_round_obj = get_evr_round()  # ดึงข้อมูลรอบการประเมินปัจจุบัน
    round_1 = evr_round.objects.filter(evr_round=1, evr_year=(timezone.now().year - 1 if evr_round_obj.evr_round == 2 else timezone.now().year)).first()
    
    sick_leave_round_1 = get_or_create_leave(user, round_1, 'SL') if round_1 else None
    sick_leave_current = get_or_create_leave(user, evr_round_obj, 'SL')
    
    personal_leave_round_1 = get_or_create_leave(user, round_1, 'PL') if round_1 else None
    personal_leave_current = get_or_create_leave(user, evr_round_obj, 'PL')
    
    late_round_1 = get_or_create_leave(user, round_1, 'LT') if round_1 else None
    late_current = get_or_create_leave(user, evr_round_obj, 'LT')

    maternity_leave_round_1 = get_or_create_leave(user, round_1, 'ML') if round_1 else None
    maternity_leave_current = get_or_create_leave(user, evr_round_obj, 'ML')

    ordination_leave_round_1 = get_or_create_leave(user, round_1, 'OL') if round_1 else None
    ordination_leave_current = get_or_create_leave(user, evr_round_obj, 'OL')

    longsick_leave_round_1 = get_or_create_leave(user, round_1, 'LSL') if round_1 else None
    longsick_leave_current = get_or_create_leave(user, evr_round_obj, 'LSL')

    adsent_work_round_1 = get_or_create_leave(user, round_1, 'AW') if round_1 else None
    adsent_work_current = get_or_create_leave(user, evr_round_obj, 'AW')

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=user, evr_id=evr_round_obj).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None
    year_thai=user_evaluation_agreement_obj.year+543
    user_work_current = user_work_info.objects.filter(user=user, round=evr_round_obj).first()
    user_work_round_1 = user_work_info.objects.filter(user=user, round=round_1).first() if round_1 else None

        # ตรวจสอบว่า profile.start_goverment มีข้อมูลหรือไม่
    if profile.start_goverment:
        try:
            # สมมติว่า format ของวันที่ใน profile.start_goverment เป็น 'YYYY-MM-DD'
            start_goverment_date = datetime.strptime(profile.start_goverment, '%Y-%m-%d')
            start_goverment_thai = start_goverment_date.year + 543
            start_goverment_str = start_goverment_date.strftime('%d/%m/') + str(start_goverment_thai)
        except ValueError:
            # กรณีที่รูปแบบวันที่ไม่ถูกต้อง
            start_goverment_str = 'รูปแบบวันที่ไม่ถูกต้อง'
    else:
        start_goverment_str = 'ไม่มีข้อมูล'


    # ดึงข้อมูล competencies
    main_competencies = main_competency.objects.filter(mc_type=evaluation.ac_id.ac_name)
    specific_competencies = specific_competency.objects.filter(sc_type=evaluation.ac_id.ac_name)
    administrative_competencies = None
    
    if evaluation.administrative_position and evaluation.administrative_position != "-":
        administrative_competencies = administrative_competency.objects.all()

    # ดึงข้อมูลคะแนนที่เคยกรอก
    main_scores = user_competency_main.objects.filter(evaluation=evaluation)
    specific_scores = user_competency_councilde.objects.filter(evaluation=evaluation)
    administrative_scores = user_competency_ceo.objects.filter(evaluation=evaluation)

    # เก็บจำนวนสมรรถนะที่ได้คะแนนตามเงื่อนไขต่าง ๆ
    score_count = {3: 0, 
                   2: 0, 
                   1: 0, 
                   0: 0}

    # คำนวณคะแนนสำหรับ main competencies
    main_competency_total = 0
    for score in main_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.mc_id.mc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        main_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ specific competencies
    specific_competency_total = 0
    for score in specific_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.sc_id.sc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        specific_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ administrative competencies (ถ้ามี)
    administrative_competency_total = 0
    if administrative_competencies is not None:
        for score in administrative_scores:
            calculated_score = calculate_competency_score(score.actual_score, score.uceo_num)
            score_count[calculated_score] += 1
            administrative_competency_total += calculated_score

    # คำนวณคะแนนในแต่ละกรณี (คูณ 3, 2, 1 และ 0)
    score_3_total = score_count[3] * 3
    score_2_total = score_count[2] * 2
    score_1_total = score_count[1] * 1
    score_0_total = score_count[0] * 0

    total_score = total_score if 'total_score' is locals() else 0.0
    total_max_num = total_max_num if 'total_max_num' is locals() else 0.0

    total_score = float(total_score) if total_score is not None else 0.0
    total_max_num = float(total_max_num) if total_max_num is not None else 0.0

    total_score = score_3_total + score_2_total + score_1_total + score_0_total

    # คำนวณค่ารวมของคะแนนที่คาดหวังสำหรับแต่ละตาราง
    main_max_num = sum([c.mc_num for c in main_competencies])
    specific_max_num = sum([c.sc_num for c in specific_competencies])
    administrative_max_num = sum([score.uceo_num for score in administrative_scores]) if administrative_competencies is not None else 0

    # คำนวณคะแนนจากสูตร
    total_max_num = main_max_num + specific_max_num + administrative_max_num

    calculated_score = calculated_score if 'calculated_score' in locals() else 0.0

    calculated_score = float(calculated_score) if calculated_score is not None else 0.0
    if total_max_num > 0.0:
        calculated_score = (total_score / total_max_num) * 30


    # สร้าง response สำหรับการดาวน์โหลดไฟล์ PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="แบบประเมินผลการปฏิบัติงาน.pdf"'

    # เริ่มสร้าง PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4



    # ลงทะเบียนฟอนต์ภาษาไทย
    pdfmetrics.registerFont(TTFont('Sarabun', 'static/fonts/THSarabunNew.ttf'))
    pdfmetrics.registerFont(TTFont('SarabunBold', 'static/fonts/THSarabunNew Bold.ttf'))

    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20
    
    # ใช้ฟอนต์ภาษาไทย
    p.setFont("SarabunBold", 18)

    # กำหนดหัวเรื่องและรายละเอียด
    p.drawCentredString(width / 2, height - 50, "ข้อตกลงและแบบประเมินผลการปฏิบัติงานของบุคลากรสายวิชาการ")
    p.drawCentredString(width / 2, height - 70, "มหาวิทยาลัยเทคโนโลยีราชมงคลล้านนา ประจำปีงบประมาณ "f"{year_thai}")
    p.drawCentredString(width / 2, height - 90, "หน่วยงาน คณะวิศวกรรมศาสตร์ มหาวิทยาลัยเทคโนโลยีราชมงคลล้านนา")

    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 150, f"กลุ่มที่เลือก: {selected_group.g_field_name}")

    if evr_round_obj.evr_round == 1:
        p.drawString(50, height - 175, "ช่วงเวลา: ครั้งที่ 1 (1 ตุลาคม - 31 มีนาคม)")
    elif evr_round_obj.evr_round == 2:
        p.drawString(50, height - 175, "ช่วงเวลา: ครั้งที่ 2 (1 เมษายน - 30 กันยายน)")

    # เพิ่มข้อมูลผู้ใช้งาน
    p.setFont("SarabunBold", 16)
    # กำหนดค่าเริ่มต้นสำหรับคอลัมน์ซ้ายและขวา
    col1_x = 50  # ตำแหน่ง X ของคอลัมน์ซ้าย
    col2_x = 300  # ตำแหน่ง X ของคอลัมน์ขวา
    y_position = height - 210  # เริ่มต้นที่ความสูงนี้
    # คอลัมน์ซ้าย
    p.drawString(col1_x, y_position, "ชื่อ-นามสกุล:")
    p.drawString(col1_x, y_position - 20, f"ตำแหน่งวิชาการ:")
    p.drawString(col1_x, y_position - 45, f"ตำแหน่งบริหาร:")
    p.drawString(col1_x, y_position - 70, f"เลขที่ประจำตำแหน่ง:")
    p.drawString(col1_x, y_position - 95, f"เงินเดือน:")
    p.drawString(col1_x, y_position - 120, f"หน้าที่พิเศษ:")
    p.drawString(col1_x, y_position - 145, f"สังกัด:")
    p.drawString(col1_x, y_position - 170, f"มาช่วยราชการจากที่ใด (ถ้ามี):")
    p.drawString(col1_x, y_position - 195, f"เริ่มรับราชการเมื่อวันที่:")
    p.drawString(col1_x, y_position - 220, f"รวมเวลารับราชการ:")
    p.setFont("Sarabun", 16)
    p.drawString(col1_x + 70, y_position, f"{evaluation.user.first_name}""   "f"{evaluation.user.last_name}")
    p.drawString(col1_x + 90, y_position - 20, f"{evaluation.ac_id.ac_name}")
    p.drawString(col1_x + 80, y_position - 45, f"{evaluation.administrative_position}")
    p.drawString(col1_x + 100, y_position - 70, f"{profile.position_number}")
    p.drawString(col1_x + 50, y_position - 95, f"{profile.salary}")
    p.drawString(col1_x + 70, y_position - 120, f"{profile.special_position}")
    p.drawString(col1_x + 40, y_position - 145, f"{profile.affiliation}")
    p.drawString(col1_x + 140, y_position - 170, f"{profile.old_government}")
    p.drawString(col1_x + 110, y_position - 195, f"{start_goverment_str}")
    p.drawString(col1_x + 100, y_position - 220, f"{profile.years_of_service} ปี { profile.months_of_service } เดือน { profile.days_of_service } วัน")

    # สร้าง Style สำหรับภาษาไทย
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.fontName = 'Sarabun'  # ใช้ฟอนต์ที่ลงทะเบียนไว้
    styleN.fontSize = 12  # กำหนดขนาดฟอนต์

    styleB = ParagraphStyle(name='Bold', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)
    p.setFont("SarabunBold", 16)
    p.drawString(col1_x, y_position - 250, "บันทึกการปฏิบัติงาน: ")
    # ตรวจสอบว่ามีข้อมูลของ round_1 หรือไม่ก่อนสร้างตารางใน PDF
    if round_1:
        data = [
            [Paragraph("ประเภทการลา", styleCenter), Paragraph("รอบที่ 1 (ครั้ง)", styleB), Paragraph("รอบที่ 1 (วัน)", styleB), Paragraph("รอบที่ 2 (ครั้ง)", styleB), Paragraph("รอบที่ 2 (วัน)", styleB)],
            ["ลาป่วย", sick_leave_current.times, sick_leave_current.days, "0", "0"],
            ["ลากิจ", personal_leave_current.times, personal_leave_current.days, "0", "0"],
            ["มาสาย",  late_current.times, late_current.days, "0", "0"],
            ["ลาคลอดบุตร", maternity_leave_current.times, maternity_leave_current.days, "0", "0"],
            ["ลาอุปสมบท", ordination_leave_current.times, ordination_leave_current.days, "0", "0"],
            [Paragraph("ลาป่วยจำเป็นต้องรักษาตัวเป็นเวลานานคราวเดียวหรือหลายคราวรวมกัน", styleN), longsick_leave_current.times, longsick_leave_current.days, "0", "0"],
            ["ขาดราชการ", adsent_work_current.times, adsent_work_current.days, "0", "0"],
        ]
    else:
        data = [
            [Paragraph("ประเภทการลา", styleCenter), Paragraph("รอบที่ 1 (ครั้ง)", styleB), Paragraph("รอบที่ 1 (วัน)", styleB), Paragraph("รอบที่ 2 (ครั้ง)", styleB), Paragraph("รอบที่ 2 (วัน)", styleB)],
            ["ลาป่วย", sick_leave_round_1.times, sick_leave_round_1.days, sick_leave_current.times, sick_leave_current.days],
            ["ลากิจ",  personal_leave_round_1.times, personal_leave_round_1.days, personal_leave_current.times, personal_leave_current.days],
            ["มาสาย", late_round_1.times, late_round_1.days, late_current.times, late_current.days],
            ["ลาคลอดบุตร", maternity_leave_round_1.times, maternity_leave_round_1.days, maternity_leave_current.times, maternity_leave_current.days],
            ["ลาอุปสมบท", ordination_leave_round_1.times, ordination_leave_round_1.days, ordination_leave_current.times, ordination_leave_current.days],
            [Paragraph("ลาป่วยจำเป็นต้องรักษาตัวเป็นเวลานานคราวเดียวหรือหลายคราวรวมกัน", styleN), longsick_leave_round_1.times, longsick_leave_round_1.days, longsick_leave_current.times, longsick_leave_current.days],
            ["ขาดราชการ", adsent_work_round_1.times, adsent_work_round_1.days, adsent_work_current.times, adsent_work_current.days],
        ]

    # สร้างตารางใน PDF โดยใช้ข้อมูลที่กำหนดตามเงื่อนไข
    table = Table(data, colWidths=[6 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm],rowHeights=[1*cm, 1*cm,1*cm, 1*cm,1*cm,1*cm, None, 1*cm])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # จัดกึ่งกลางคอลัมน์อื่น ๆ
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # จัดชิดซ้ายสำหรับคอลัมน์แรก
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # จัดกึ่งกลางแนวตั้งข้อความทั้งหมด
        ('FONT', (0, 0), (-1, -1), 'Sarabun'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, 0), 16),  # ขนาดฟอนต์ของหัวตาราง
        ('FONTSIZE', (0, 1), (-1, -1), 16),  # ขนาดฟอนต์ของข้อมูลในตาราง
    ]))

    # เพิ่มตารางใน PDF
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 700)  # ตำแหน่งของตารางในหน้า PDF
    styleBA = ParagraphStyle( name="Normal",
    fontName="Sarabun",
    fontSize=16,
    leading=18,  # ระยะห่างระหว่างบรรทัด
    alignment=TA_LEFT)
    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 725, "การกระทำผิดวินัย/การถูกลงโทษ: ")
    p.setFont("Sarabun", 16)
    # ข้อความ
    text = f"{user_work_current.punishment}"

    # สร้าง Paragraph และกำหนดขนาดพื้นที่แสดง
    paragraph = Paragraph(text, styleBA)
    width, height_needed = paragraph.wrap(510, 200)  # กำหนดความกว้างที่ 400 (ปรับตามต้องการ)

    # แสดงข้อความ
    paragraph.drawOn(p, 50, height - 730 - height_needed)
    p.showPage()

    if selected_group:
        fields = wl_field.objects.filter(group_detail__g_id=selected_group).distinct()
    else:
        fields = wl_field.objects.none()

    # ดึงข้อมูลที่จำเป็น
    subfields = wl_subfield.objects.filter(f_id__in=fields)
    workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)
    
    min_workload = selected_group.g_max_workload if selected_group else 35
    total_workload = sum(selection.calculated_workload for selection in workload_selections)
    achievement_work = evaluation.achievement_work or 0
    

    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่ถ้าพื้นที่ไม่พอ
            current_y = height - 100  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20

    # สร้าง Style สำหรับภาษาไทย
    styles = getSampleStyleSheet()
    styleN = ParagraphStyle(name='Normal', fontName='Sarabun', fontSize=16)
    styleB = ParagraphStyle(name='Bold', fontName='SarabunBold', fontSize=16)

    # ตรวจสอบการขึ้นหน้าใหม่ก่อนแสดงหัวข้อ
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)

    # แสดงหัวข้อ
    start_y -= line_height  # ลดตำแหน่ง Y หลังจากวาดข้อความ
    # สร้างตาราง
    data = [[Paragraph("ภาระงาน/กิจกรรม/โครงการ/งาน", styleCenter),Paragraph( "จำนวน", styleCenter),Paragraph( "ภาระงาน", styleCenter),Paragraph( "รวมภาระงาน", styleCenter), Paragraph("หมายเหตุ", styleCenter)]]

    field_counter = 0
    for field in fields:
        field_counter += 1
        total_for_field = 0
        data.append([Paragraph(f"{field_counter}. {field.f_name}", styleB), "", "", "", ""])

        subfield_counter = 0
        for subfield in subfields.filter(f_id=field):
            subfield_counter += 1
            data.append([Paragraph(f"{field_counter}.{subfield_counter}. {subfield.sf_name}", styleN), "", "", "", ""])

            selection_counter = 0
            for selection in workload_selections.filter(sf_id=subfield):
                selection_counter += 1
                data.append([
                    Paragraph(f"{field_counter}.{subfield_counter}.{selection_counter}. {selection.selected_name}", styleN),
                    str(selection.selected_num),
                    f"{selection.selected_workload:.1f}",  # แสดงทศนิยม 1 ตำแหน่ง
                    f"{selection.calculated_workload:.1f}",  # แสดงทศนิยม 1 ตำแหน่ง
                    selection.notes or ""
                ])
                total_for_field += selection.calculated_workload
            
    # เพิ่มแถวที่เป็นตัวหนา
    data.append([Paragraph("รวมคะแนนสำหรับภาระงานทั้งหมด", styleB), "", "", f"{total_workload:.1f}", ""])
    data.append([Paragraph("คะแนนผลสัมฤทธิ์ของงาน", styleB), "", "", f"{achievement_work:.1f}", ""])

    # ฟังก์ชันแบ่งข้อมูลเป็นชุด ๆ
    def chunk_data(data, chunk_size):
        """แบ่งข้อมูลออกเป็นชุด ๆ ตาม chunk_size"""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    # ฟังก์ชันสร้างตาราง
    def draw_table(p, data, start_x, start_y, max_rows_per_page):
        table_data = data[:max_rows_per_page]  # ดึงเฉพาะข้อมูลที่พอดีกับหน้า
        table = Table(table_data, colWidths=[9.75 * cm, 1.5 * cm, 2 * cm, 2.5 * cm, 2.5 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # จัดชิดซ้ายสำหรับคอลัมน์แรก
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # วาดตารางและลดตำแหน่ง Y
        w, h = table.wrap(width, height)  # คำนวณขนาดตาราง
        table.drawOn(p, start_x, start_y - h)  # วาดตารางที่ตำแหน่ง start_y ลดด้วย h
        return start_y - h  # คืนค่าตำแหน่งใหม่หลังจากวาดตาราง

    # คำนวณจำนวนแถวที่พอดีกับแต่ละหน้า
    max_rows_per_page = 23  # สมมติว่าเราจะแสดง 30 แถวต่อหน้า

    # วาดตารางในแต่ละหน้า
    for chunk in chunk_data(data, max_rows_per_page):
        start_y = height - 50  # กำหนดจุดเริ่มต้นของหน้าใหม่
        p.setFont("SarabunBold", 16)
        p.drawString(start_x, start_y, "ส่วนที่ 1 องค์ประกอบที่ 1 ผลสัมฤทธิ์ของงาน")
        start_y = height - 70
        start_y = draw_table(p, data + chunk, start_x, start_y, max_rows_per_page)  # วาดและอัพเดท start_y
        p.showPage()  # ขึ้นหน้าใหม่เมื่อวาดเสร็จ


    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง
    
    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=12, alignment=TA_CENTER)

    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 50, "ส่วนที่ 2 องค์ประกอบที่ 2 พฤติกรรมการปฏิบัติงาน (สมรรถนะ)")
    start_y -= line_height
    
    # สร้างตารางสมรรถนะหลัก
    data_main = [[Paragraph("สมรรถนะหลัก", styleCenter), Paragraph("ระดับสมรรถนะที่คาดหวัง", styleCenter), Paragraph("ระดับสมรรถนะที่แสดงออก", styleCenter)]]
    for score in main_scores:
        data_main.append([score.mc_id.mc_name, str(score.mc_id.mc_num), str(score.actual_score)])

    # สร้างตารางสมรรถนะเฉพาะ
    data_specific = [[Paragraph("สมรรถนะเฉพาะ", styleCenter), Paragraph("ระดับสมรรถนะที่คาดหวัง", styleCenter), Paragraph("ระดับสมรรถนะที่แสดงออก", styleCenter)]]
    for score in specific_scores:
        data_specific.append([score.sc_id.sc_name, str(score.sc_id.sc_num), str(score.actual_score)])

    # สร้างตารางสมรรถนะทางการบริหาร (ถ้ามี)
    if administrative_competencies:
        data_administrative = [[Paragraph("สมรรถนะทางการบริหาร", styleCenter), Paragraph("ระดับสมรรถนะที่คาดหวัง", styleCenter), Paragraph("ระดับสมรรถนะที่แสดงออก", styleCenter)]]
        for score in administrative_scores:
            data_administrative.append([score.adc_id.adc_name, str(score.uceo_num), str(score.actual_score)])
    else:
        data_administrative = []

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[9 * cm, 4 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # จัดชิดซ้ายสำหรับคอลัมน์แรก
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตาราง
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    # วางตารางสมรรถนะหลัก
    p.setFont("SarabunBold", 16)
    p.drawString(start_x, start_y, "สมรรถนะหลัก (ที่สภามหาวิทยาลัยกำหนด)")
    start_y -= line_height
    start_y = draw_table(p, data_main, start_x, start_y)

    # เพิ่มช่องว่าง
    start_y -= 2 * line_height

    # วางตารางสมรรถนะเฉพาะ
    p.setFont("SarabunBold", 16)
    p.drawString(start_x, start_y, "สมรรถนะเฉพาะ (ที่สภามหาวิทยาลัยกำหนด)")
    start_y -= line_height
    start_y = draw_table(p, data_specific, start_x, start_y)

    # วางตารางสมรรถนะทางการบริหารถ้ามี
    if data_administrative:
        start_y -= 2 * line_height
        p.setFont("SarabunBold", 16)
        p.drawString(start_x, start_y, "สมรรถนะทางการบริหาร (ถ้ามี)")
        start_y -= line_height
        start_y = draw_table(p, data_administrative, start_x, start_y)

    # เพิ่มช่องว่าง
    start_y -= 2 * line_height
    # สร้างตารางการประเมินคะแนน
    data = [
        [Paragraph("จำนวนสมรรถนะ", styleCenter), Paragraph("คูณ (X)", styleCenter), Paragraph("คะแนน", styleCenter)],
        [str(score_count[3]), "3", str(score_3_total)],
        [str(score_count[2]), "2", str(score_2_total)],
        [str(score_count[1]), "1", str(score_1_total)],
        [str(score_count[0]), "0", str(score_0_total)],
        ["", Paragraph("ผลรวมคะแนน", styleCenter), str(total_score)],
    ]

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[9 * cm, 4 * cm, 4 * cm])  # กำหนดขนาดคอลัมน์
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตารางและตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        p.setFont("SarabunBold", 16)
        p.drawString(start_x, start_y,"การประเมิน")
        start_y -= line_height
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    styleCenterA = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16)

    # วางตารางการประเมินคะแนน
    start_y = draw_table(p, data, start_x, start_y)

        # เพิ่มช่องว่าง
    start_y -= 2 * line_height
    p.drawString(start_x, start_y, f"ผลรวมคะแนน {total_score:.1f} / ผลรวมระดับสมรรถนะที่คาดหวัง {total_max_num:.1f} * 30 คะแนนที่ได้: {calculated_score:.1f}")
    start_y -= line_height
    # สร้างตารางการประเมินคะแนน
    data = [
        [Paragraph("หลักเกณฑ์การประเมิน", styleCenter)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก สูงกว่าหรือเท่ากับ ระดับสมรรถนะที่คาดหวัง x ๓ คะแนน", styleCenterA)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก ต่ำกว่า ระดับสมรรถนะที่คาดหวัง ๑ ระดับ x ๒ คะแนน", styleCenterA)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก ต่ำกว่า ระดับสมรรถนะที่คาดหวัง ๒ ระดับ x ๑ คะแนน", styleCenterA)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก ต่ำกว่า ระดับสมรรถนะที่คาดหวัง ๓ ระดับ x ๐ คะแนน", styleCenterA)],
    ]

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[17 * cm])  # กำหนดขนาดคอลัมน์
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'SarabunBold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตารางและตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    # วางตารางการประเมินคะแนน
    start_y = draw_table(p, data, start_x, start_y)

    p.showPage()

     # คำนวณคะแนนต่าง ๆ
    achievement_work = evaluation.achievement_work or 0
    mc_score = evaluation.mc_score or 0
    total_score = achievement_work + mc_score

    # กำหนดระดับผลการประเมิน
    if total_score >= 90:
        level = 'ดีเด่น'
    elif total_score >= 80:
        level = 'ดีมาก'
    elif total_score >= 70:
        level = 'ดี'
    elif total_score >= 60:
        level = 'พอใช้'
    else:
        level = 'ต้องปรับปรุง'


    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง
    
    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)
    styleBB = ParagraphStyle(name='Bold', fontName='SarabunBold', fontSize=16)

    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 50, "ส่วนที่ 3 สรุปการประเมินผลการปฏิบัติราชการ")

    data = [
        [Paragraph("องค์ประกอบการประเมิน", styleCenter),Paragraph("คะแนนเต็ม", styleCenter),Paragraph("คะแนนที่ได้", styleCenter),Paragraph("หมายเหตุ", styleCenter)],
        ["องค์ประกอบที่ 1: ผลสัมฤทธิ์ของงาน", "70", f"{achievement_work:.1f}", f"{evaluation.remark_achievement}"],
        ["องค์ประกอบที่ 2: พฤติกรรมการปฏิบัติราชการ (สมรรถนะ)", "30", f"{mc_score:.1f}", f"{evaluation.remark_mc}"],
        ["องค์ประกอบอื่น ๆ (ถ้ามี)", "", "", f"{evaluation.remark_other}"],
        [Paragraph("รวม", styleBB), "100", f"{total_score:.1f}", f"{evaluation.remark_total}"],
    ]

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[9 * cm,2.5 * cm,2.5 * cm,4 * cm])  # กำหนดขนาดคอลัมน์
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตารางและตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    # วางตารางการประเมินคะแนน
    start_y = draw_table(p, data, start_x, start_y)

    # แสดงระดับผลการประเมินในแบบ radio button (เลือกแล้ว)
    p.drawString(50, height - 250, "ระดับผลการประเมิน:")
    
    levels = [
        ("ดีเด่น (90 - 100)", total_score >= 90),
        ("ดีมาก (80 - 89.99)", 80 <= total_score < 90),
        ("ดี (70 - 79.99)", 70 <= total_score < 80),
        ("พอใช้ (60 - 69.99)", 60 <= total_score < 70),
        ("ต้องปรับปรุง (ต่ำกว่า 60)", total_score < 60),
    ]

    # วาด radio button (ข้อความแสดงผลการประเมิน)
    start_y = height - 280
    for level_text, is_selected in levels:
        p.circle(55, start_y, 5, fill=1 if is_selected else 0)  # วาดวงกลม
        p.drawString(70, start_y - 5, level_text)  # วาดข้อความข้าง ๆ
        start_y -= 20

    p.showPage()

    formset_data = PersonalDiagram.objects.filter(uevr_id=evaluation)

    # ฟังก์ชันตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20

    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=12, alignment=TA_CENTER)

    p.setFont("SarabunBold", 16)
    styleLeft = ParagraphStyle(name='Left', fontName='Sarabun', fontSize=16, alignment=0)
    styleCenter = ParagraphStyle(name='Center', fontName='Sarabun', fontSize=16, alignment=1)


    # แสดงหัวข้อ "ส่วนที่ 4 : แผนพัฒนาการปฏิบัติราชการรายบุคคล"
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    p.drawString(start_x, start_y, "ส่วนที่ 4 : แผนพัฒนาการปฏิบัติราชการรายบุคคล")
    start_y -= line_height

    # สร้างตารางที่มีฟิลด์ข้อมูลจาก formset_data
    data = [[Paragraph("ความรู้/ทักษะ/สมรรถนะ", styleCenter), Paragraph("วิธีการพัฒนา", styleCenter), Paragraph("ช่วงเวลาที่ต้องการพัฒนา", styleCenter)]]

    for item in formset_data:
        data.append([
        Paragraph(str(item.skill_evol), styleLeft),
        Paragraph(str(item.dev), styleLeft),
        Paragraph(str(item.dev_time), styleLeft)
    ])

    table = Table(data, colWidths=[6 * cm, 6 * cm, 5 * cm])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Sarabun'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
        ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
        ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
    ]))

    # คำนวณความสูงของตารางและตรวจสอบว่ามีพื้นที่เพียงพอหรือไม่
    table_width, table_height = table.wrap(width, height)
    start_y = check_and_create_new_page(p, start_y, table_height, bottom_margin)
    table.drawOn(p, start_x, start_y - table_height)
    start_y -= table_height + line_height

    start_y -= 2* line_height

    # ความเห็นเพิ่มเติมของผู้ประเมิน
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    p.drawString(start_x, start_y, "ความเห็นเพิ่มเติมของผู้ประเมิน")
    start_y -= line_height

    # ส่วนแสดงความคิดเห็น
    p.drawString(start_x, start_y, "1) จุดเด่น และ/หรือ สิ่งที่ควรปรับปรุงแก้ไข")
    start_y -= line_height
    p.rect(start_x, start_y - 60, 483, 60)  # สร้างกล่องสำหรับแสดงความคิดเห็น
    p.setFont("Sarabun", 16)
    p.drawString(start_x + 5, start_y -20 , f"{evaluation.improved if evaluation.improved else ''}")
    start_y -= 80  # ลดระยะหลังจากกล่องแสดงความคิดเห็น
    p.setFont("SarabunBold", 16)
    p.drawString(start_x, start_y, "2) ข้อเสนอแนะเกี่ยวกับวิธีส่งเสริมและพัฒนา")
    start_y -= line_height
    p.rect(start_x, start_y - 60, 483, 60)  # สร้างกล่องสำหรับแสดงความคิดเห็น
    p.setFont("Sarabun", 16)
    p.drawString(start_x + 5, start_y -20 , f"{evaluation.suggestions if evaluation.suggestions else ''}")
    start_y -= 80  # ลดระยะหลังจากกล่องแสดงความคิดเห็น

    start_y -=  line_height
    p.setFont("SarabunBold", 16)
    p.line(start_x , start_y+20, start_x + 500, start_y+20)
    # ลายมือชื่อ
    start_y = check_and_create_new_page(p, start_y, 60, bottom_margin)
    p.drawString(start_x + 50, start_y, "ผู้ประเมินและผู้รับการประเมินได้ตกลงร่วมกันและเห็นพ้องกันแล้ว (ระบุข้อมูลให้ครบ)")
    start_y -= line_height
    p.drawString(start_x + 100, start_y, "จึงลงลายมือชื่อไว้เป็นหลักฐาน (ลงนามเมื่อจัดทำข้อตกลง)")
    start_y -= 2* line_height

    p.drawString(start_x+2, start_y, "ลายมือชื่อ.................................................(ผู้ประเมิน)")
    p.drawString(start_x + 240, start_y, f"ลายมือชื่อ.................................................(ผู้รับการประเมิน)")
    #if evaluation.full_name is None:
    #    p.drawString(start_x + 240, start_y, f"ลายมือชื่อ.................................................(ผู้รับการประเมิน)")
    #else:
    #    p.drawString(start_x + 288, start_y+2, f"{evaluation.full_name}")
    #    p.drawString(start_x + 240, start_y, f"ลายมือชื่อ.................................................(ผู้รับการประเมิน)")
    start_y -= line_height
    
    p.drawString(start_x + 25, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    p.drawString(start_x + 265, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    #if evaluation.full_name is None:
    #    p.drawString(start_x + 265, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    #else:
    #    p.drawString(start_x + 290, start_y-8, f"{evaluation.start_day}")
    #   p.drawString(start_x + 352, start_y-8, f"{evaluation.start_month}")
    #    p.drawString(start_x + 413, start_y-8, f"{evaluation.start_year}")
    #   p.drawString(start_x + 265, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    p.line(start_x , start_y-20, start_x + 500, start_y-20)
    p.line(start_x , start_y+50, start_x + 500, start_y+50)
    p.line(start_x, start_y-20, start_x, start_y+100)
    p.line(start_x+500, start_y-20, start_x+500, start_y+100)
    p.line(start_x+236, start_y-20, start_x+236, start_y+50)

    p.showPage()


    # ฟังก์ชันตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20

    p.setFont("SarabunBold", 16)

    start_y = check_and_create_new_page(p, start_y, 60, bottom_margin)

    p.drawString(start_x, start_y, "ส่วนที่ 5 การรับทราบผลการประเมิน")
    start_y -=2 * line_height
    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้รับการประเมิน :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y-10, "☐ ได้รับทราบผลการประเมิน")
    p.drawString(start_x + 20 , start_y-25, "และแผนพัฒนาการปฏิบัติราชการรายบุคคลแล้ว")

    p.drawString(start_x + 300, start_y, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-20, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-40, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-55)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-55)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-55)
    p.line(start_x , start_y-55, start_x + 480, start_y-55)
    start_y -= 2* line_height
    start_y -= 2* line_height
    start_y -=  line_height

    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้ประเมิน :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y, "☐ ได้แจ้งผลการประเมินและผู้รับการประเมินได้ลงนามรับทราบ")
    p.drawString(start_x + 5 , start_y-25, "☐ ได้แจ้งผลการประเมินเมื่อวันที่.................................................")
    p.drawString(start_x + 20 , start_y-45, "แต่ผู้รับการประเมินไม่ลงนามรับทราบผลการประเมิน")
    p.drawString(start_x + 20 , start_y-65, "โดยมี.......................................................................เป็นพยาน")

    p.drawString(start_x + 300, start_y-10, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-30, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-50, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-80)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-80)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-80)
    p.line(start_x , start_y-80, start_x + 480, start_y-80)
    start_y -= 2* line_height
    start_y -= 2* line_height
    start_y -= 2* line_height

    p.setFont("SarabunBold", 16)

    start_y = check_and_create_new_page(p, start_y, 60, bottom_margin)

    p.drawString(start_x, start_y, "ส่วนที่ 6 ความเห็นของผู้บังคับบัญชาเหนือขึ้นไป")
    start_y -= 2* line_height

    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้บังคับบัญชาเหนือขึ้นไป :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y, "☐ เห็นด้วยกับผลการประเมิน")
    p.drawString(start_x + 5 , start_y-25, "☐ มีความเห็นแตกต่าง ดังนี้")
    p.drawString(start_x + 20 , start_y-45, ".........................................................................................................")
    p.drawString(start_x + 20 , start_y-65, ".........................................................................................................")

    p.drawString(start_x + 300, start_y-10, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-30, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-50, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-80)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-80)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-80)
    p.line(start_x , start_y-80, start_x + 480, start_y-80)
    start_y -= 2* line_height
    start_y -= 2* line_height
    start_y -= 2* line_height

    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้บังคับบัญชาเหนือขึ้นไปอีกชั้นหนึ่ง (ถ้ามี) :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y, "☐ เห็นด้วยกับผลการประเมิน")
    p.drawString(start_x + 5 , start_y-25, "☐ มีความเห็นแตกต่าง ดังนี้")
    p.drawString(start_x + 20 , start_y-45, ".........................................................................................................")
    p.drawString(start_x + 20 , start_y-65, ".........................................................................................................")

    p.drawString(start_x + 300, start_y-10, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-30, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-50, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-80)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-80)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-80)
    p.line(start_x , start_y-80, start_x + 480, start_y-80)
    start_y -= 2* line_height

    p.save()

    return response





@login_required
def print_evaluation_pdf_eva(request, evaluation_id):
    evaluation = get_object_or_404(user_evaluation, pk=evaluation_id)
    user = evaluation.user
    profile = evaluation.user.profile


    # ฟังก์ชันสำหรับการดึงข้อมูลการลาในแต่ละรอบ
    def get_or_create_leave(user, round_obj, leave_type):
        leave, created = WorkLeave.objects.get_or_create(
            user=user,
            round=round_obj,
            leave_type=leave_type,
            defaults={'times': 0, 'days': 0}
        )
        return leave
    

    # ดึงข้อมูลการลา
    evr_round_obj = get_evr_round()  # ดึงข้อมูลรอบการประเมินปัจจุบัน
    round_1 = evr_round.objects.filter(evr_round=1, evr_year=(timezone.now().year - 1 if evr_round_obj.evr_round == 2 else timezone.now().year)).first()
    
    sick_leave_round_1 = get_or_create_leave(user, round_1, 'SL') if round_1 else None
    sick_leave_current = get_or_create_leave(user, evr_round_obj, 'SL')
    
    personal_leave_round_1 = get_or_create_leave(user, round_1, 'PL') if round_1 else None
    personal_leave_current = get_or_create_leave(user, evr_round_obj, 'PL')
    
    late_round_1 = get_or_create_leave(user, round_1, 'LT') if round_1 else None
    late_current = get_or_create_leave(user, evr_round_obj, 'LT')

    maternity_leave_round_1 = get_or_create_leave(user, round_1, 'ML') if round_1 else None
    maternity_leave_current = get_or_create_leave(user, evr_round_obj, 'ML')

    ordination_leave_round_1 = get_or_create_leave(user, round_1, 'OL') if round_1 else None
    ordination_leave_current = get_or_create_leave(user, evr_round_obj, 'OL')

    longsick_leave_round_1 = get_or_create_leave(user, round_1, 'LSL') if round_1 else None
    longsick_leave_current = get_or_create_leave(user, evr_round_obj, 'LSL')

    adsent_work_round_1 = get_or_create_leave(user, round_1, 'AW') if round_1 else None
    adsent_work_current = get_or_create_leave(user, evr_round_obj, 'AW')

    # ดึงข้อมูลการประเมินผลของผู้ใช้
    user_evaluation_agreement_obj = user_evaluation_agreement.objects.filter(user=user, evr_id=evr_round_obj).first()
    selected_group = user_evaluation_agreement_obj.g_id if user_evaluation_agreement_obj else None
    year_thai=user_evaluation_agreement_obj.year+543
    user_work_current = user_work_info.objects.filter(user=user, round=evr_round_obj).first()
    user_work_round_1 = user_work_info.objects.filter(user=user, round=round_1).first() if round_1 else None

        # ตรวจสอบว่า profile.start_goverment มีข้อมูลหรือไม่
    if profile.start_goverment:
        try:
            # สมมติว่า format ของวันที่ใน profile.start_goverment เป็น 'YYYY-MM-DD'
            start_goverment_date = datetime.strptime(profile.start_goverment, '%Y-%m-%d')
            start_goverment_thai = start_goverment_date.year + 543
            start_goverment_str = start_goverment_date.strftime('%d/%m/') + str(start_goverment_thai)
        except ValueError:
            # กรณีที่รูปแบบวันที่ไม่ถูกต้อง
            start_goverment_str = 'รูปแบบวันที่ไม่ถูกต้อง'
    else:
        start_goverment_str = 'ไม่มีข้อมูล'


    # ดึงข้อมูล competencies
    main_competencies = main_competency.objects.filter(mc_type=evaluation.ac_id.ac_name)
    specific_competencies = specific_competency.objects.filter(sc_type=evaluation.ac_id.ac_name)
    administrative_competencies = None
    
    if evaluation.administrative_position and evaluation.administrative_position != "-":
        administrative_competencies = administrative_competency.objects.all()

    # ดึงข้อมูลคะแนนที่เคยกรอก
    main_scores = user_competency_main.objects.filter(evaluation=evaluation)
    specific_scores = user_competency_councilde.objects.filter(evaluation=evaluation)
    administrative_scores = user_competency_ceo.objects.filter(evaluation=evaluation)

    # เก็บจำนวนสมรรถนะที่ได้คะแนนตามเงื่อนไขต่าง ๆ
    score_count = {3: 0, 
                   2: 0, 
                   1: 0, 
                   0: 0}

    # คำนวณคะแนนสำหรับ main competencies
    main_competency_total = 0
    for score in main_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.mc_id.mc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        main_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ specific competencies
    specific_competency_total = 0
    for score in specific_scores:
        calculated_score = calculate_competency_score(score.actual_score, score.sc_id.sc_num)  # ส่ง expected_score ด้วย
        score_count[calculated_score] += 1
        specific_competency_total += calculated_score

    # คำนวณคะแนนสำหรับ administrative competencies (ถ้ามี)
    administrative_competency_total = 0
    if administrative_competencies is not None:
        for score in administrative_scores:
            calculated_score = calculate_competency_score(score.actual_score, score.uceo_num)
            score_count[calculated_score] += 1
            administrative_competency_total += calculated_score

    # คำนวณคะแนนในแต่ละกรณี (คูณ 3, 2, 1 และ 0)
    score_3_total = score_count[3] * 3
    score_2_total = score_count[2] * 2
    score_1_total = score_count[1] * 1
    score_0_total = score_count[0] * 0

    total_score = total_score if 'total_score' is locals() else 0.0
    total_max_num = total_max_num if 'total_max_num' is locals() else 0.0

    total_score = float(total_score) if total_score is not None else 0.0
    total_max_num = float(total_max_num) if total_max_num is not None else 0.0

    total_score = score_3_total + score_2_total + score_1_total + score_0_total

    # คำนวณค่ารวมของคะแนนที่คาดหวังสำหรับแต่ละตาราง
    main_max_num = sum([c.mc_num for c in main_competencies])
    specific_max_num = sum([c.sc_num for c in specific_competencies])
    administrative_max_num = sum([score.uceo_num for score in administrative_scores]) if administrative_competencies is not None else 0

    # คำนวณคะแนนจากสูตร
    total_max_num = main_max_num + specific_max_num + administrative_max_num

    calculated_score = calculated_score if 'calculated_score' in locals() else 0.0

    calculated_score = float(calculated_score) if calculated_score is not None else 0.0
    if total_max_num > 0.0:
        calculated_score = (total_score / total_max_num) * 30


    # สร้าง response สำหรับการดาวน์โหลดไฟล์ PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="แบบประเมินผลการปฏิบัติงาน.pdf"'

    # เริ่มสร้าง PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4



    # ลงทะเบียนฟอนต์ภาษาไทย
    pdfmetrics.registerFont(TTFont('Sarabun', 'static/fonts/THSarabunNew.ttf'))
    pdfmetrics.registerFont(TTFont('SarabunBold', 'static/fonts/THSarabunNew Bold.ttf'))

    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20
    
    # ใช้ฟอนต์ภาษาไทย
    p.setFont("SarabunBold", 18)

    # กำหนดหัวเรื่องและรายละเอียด
    p.drawCentredString(width / 2, height - 50, "ข้อตกลงและแบบประเมินผลการปฏิบัติงานของบุคลากรสายวิชาการ")
    p.drawCentredString(width / 2, height - 70, "มหาวิทยาลัยเทคโนโลยีราชมงคลล้านนา ประจำปีงบประมาณ "f"{year_thai}")
    p.drawCentredString(width / 2, height - 90, "หน่วยงาน คณะวิศวกรรมศาสตร์ มหาวิทยาลัยเทคโนโลยีราชมงคลล้านนา")

    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 150, f"กลุ่มที่เลือก: {selected_group.g_field_name}")

    if evr_round_obj.evr_round == 1:
        p.drawString(50, height - 175, "ช่วงเวลา: ครั้งที่ 1 (1 ตุลาคม - 31 มีนาคม)")
    elif evr_round_obj.evr_round == 2:
        p.drawString(50, height - 175, "ช่วงเวลา: ครั้งที่ 2 (1 เมษายน - 30 กันยายน)")

    # เพิ่มข้อมูลผู้ใช้งาน
    p.setFont("SarabunBold", 16)
    # กำหนดค่าเริ่มต้นสำหรับคอลัมน์ซ้ายและขวา
    col1_x = 50  # ตำแหน่ง X ของคอลัมน์ซ้าย
    col2_x = 300  # ตำแหน่ง X ของคอลัมน์ขวา
    y_position = height - 210  # เริ่มต้นที่ความสูงนี้
    # คอลัมน์ซ้าย
    p.drawString(col1_x, y_position, "ชื่อ-นามสกุล:")
    p.drawString(col1_x, y_position - 20, f"ตำแหน่งวิชาการ:")
    p.drawString(col1_x, y_position - 45, f"ตำแหน่งบริหาร:")
    p.drawString(col1_x, y_position - 70, f"เลขที่ประจำตำแหน่ง:")
    p.drawString(col1_x, y_position - 95, f"เงินเดือน:")
    p.drawString(col1_x, y_position - 120, f"หน้าที่พิเศษ:")
    p.drawString(col1_x, y_position - 145, f"สังกัด:")
    p.drawString(col1_x, y_position - 170, f"มาช่วยราชการจากที่ใด (ถ้ามี):")
    p.drawString(col1_x, y_position - 195, f"เริ่มรับราชการเมื่อวันที่:")
    p.drawString(col1_x, y_position - 220, f"รวมเวลารับราชการ:")
    p.setFont("Sarabun", 16)
    p.drawString(col1_x + 70, y_position, f"{evaluation.user.first_name}""   "f"{evaluation.user.last_name}")
    p.drawString(col1_x + 90, y_position - 20, f"{evaluation.ac_id.ac_name}")
    p.drawString(col1_x + 80, y_position - 45, f"{evaluation.administrative_position}")
    p.drawString(col1_x + 100, y_position - 70, f"{profile.position_number}")
    p.drawString(col1_x + 50, y_position - 95, f"{profile.salary}")
    p.drawString(col1_x + 70, y_position - 120, f"{profile.special_position}")
    p.drawString(col1_x + 40, y_position - 145, f"{profile.affiliation}")
    p.drawString(col1_x + 140, y_position - 170, f"{profile.old_government}")
    p.drawString(col1_x + 110, y_position - 195, f"{start_goverment_str}")
    p.drawString(col1_x + 100, y_position - 220, f"{profile.years_of_service} ปี { profile.months_of_service } เดือน { profile.days_of_service } วัน")

    # สร้าง Style สำหรับภาษาไทย
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.fontName = 'Sarabun'  # ใช้ฟอนต์ที่ลงทะเบียนไว้
    styleN.fontSize = 12  # กำหนดขนาดฟอนต์

    styleB = ParagraphStyle(name='Bold', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)
    p.setFont("SarabunBold", 16)
    p.drawString(col1_x, y_position - 250, "บันทึกการปฏิบัติงาน: ")
    # ตรวจสอบว่ามีข้อมูลของ round_1 หรือไม่ก่อนสร้างตารางใน PDF
    if round_1:
        data = [
            [Paragraph("ประเภทการลา", styleCenter), Paragraph("รอบที่ 1 (ครั้ง)", styleB), Paragraph("รอบที่ 1 (วัน)", styleB), Paragraph("รอบที่ 2 (ครั้ง)", styleB), Paragraph("รอบที่ 2 (วัน)", styleB)],
            ["ลาป่วย", sick_leave_current.times, sick_leave_current.days, "0", "0"],
            ["ลากิจ", personal_leave_current.times, personal_leave_current.days, "0", "0"],
            ["มาสาย",  late_current.times, late_current.days, "0", "0"],
            ["ลาคลอดบุตร", maternity_leave_current.times, maternity_leave_current.days, "0", "0"],
            ["ลาอุปสมบท", ordination_leave_current.times, ordination_leave_current.days, "0", "0"],
            [Paragraph("ลาป่วยจำเป็นต้องรักษาตัวเป็นเวลานานคราวเดียวหรือหลายคราวรวมกัน", styleN), longsick_leave_current.times, longsick_leave_current.days, "0", "0"],
            ["ขาดราชการ", adsent_work_current.times, adsent_work_current.days, "0", "0"],
        ]
    else:
        data = [
            [Paragraph("ประเภทการลา", styleCenter), Paragraph("รอบที่ 1 (ครั้ง)", styleB), Paragraph("รอบที่ 1 (วัน)", styleB), Paragraph("รอบที่ 2 (ครั้ง)", styleB), Paragraph("รอบที่ 2 (วัน)", styleB)],
            ["ลาป่วย", sick_leave_round_1.times, sick_leave_round_1.days, sick_leave_current.times, sick_leave_current.days],
            ["ลากิจ",  personal_leave_round_1.times, personal_leave_round_1.days, personal_leave_current.times, personal_leave_current.days],
            ["มาสาย", late_round_1.times, late_round_1.days, late_current.times, late_current.days],
            ["ลาคลอดบุตร", maternity_leave_round_1.times, maternity_leave_round_1.days, maternity_leave_current.times, maternity_leave_current.days],
            ["ลาอุปสมบท", ordination_leave_round_1.times, ordination_leave_round_1.days, ordination_leave_current.times, ordination_leave_current.days],
            [Paragraph("ลาป่วยจำเป็นต้องรักษาตัวเป็นเวลานานคราวเดียวหรือหลายคราวรวมกัน", styleN), longsick_leave_round_1.times, longsick_leave_round_1.days, longsick_leave_current.times, longsick_leave_current.days],
            ["ขาดราชการ", adsent_work_round_1.times, adsent_work_round_1.days, adsent_work_current.times, adsent_work_current.days],
        ]

    # สร้างตารางใน PDF โดยใช้ข้อมูลที่กำหนดตามเงื่อนไข
    table = Table(data, colWidths=[6 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm],rowHeights=[1*cm, 1*cm,1*cm, 1*cm,1*cm,1*cm, None, 1*cm])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # จัดกึ่งกลางคอลัมน์อื่น ๆ
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # จัดชิดซ้ายสำหรับคอลัมน์แรก
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # จัดกึ่งกลางแนวตั้งข้อความทั้งหมด
        ('FONT', (0, 0), (-1, -1), 'Sarabun'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, 0), 16),  # ขนาดฟอนต์ของหัวตาราง
        ('FONTSIZE', (0, 1), (-1, -1), 16),  # ขนาดฟอนต์ของข้อมูลในตาราง
    ]))

    # เพิ่มตารางใน PDF
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 700)  # ตำแหน่งของตารางในหน้า PDF
    styleBA = ParagraphStyle( name="Normal",
    fontName="Sarabun",
    fontSize=16,
    leading=18,  # ระยะห่างระหว่างบรรทัด
    alignment=TA_LEFT)
    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 725, "การกระทำผิดวินัย/การถูกลงโทษ: ")
    p.setFont("Sarabun", 16)
    # ข้อความ
    text = f"{user_work_current.punishment}"

    # สร้าง Paragraph และกำหนดขนาดพื้นที่แสดง
    paragraph = Paragraph(text, styleBA)
    width, height_needed = paragraph.wrap(510, 200)  # กำหนดความกว้างที่ 400 (ปรับตามต้องการ)

    # แสดงข้อความ
    paragraph.drawOn(p, 50, height - 730 - height_needed)
    p.showPage()

    if selected_group:
        fields = wl_field.objects.filter(group_detail__g_id=selected_group).distinct()
    else:
        fields = wl_field.objects.none()

    # ดึงข้อมูลที่จำเป็น
    subfields = wl_subfield.objects.filter(f_id__in=fields)
    workload_selections = UserWorkloadSelection.objects.filter(evaluation=evaluation)
    
    min_workload = selected_group.g_max_workload if selected_group else 35
    total_workload = sum(selection.calculated_workload for selection in workload_selections)
    achievement_work = evaluation.achievement_work or 0

    c_gtt = sum(selection.selected_workload_edit for selection in workload_selections)
    c_sumwl = evaluation.c_sumwl or 0
    
    

    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่ถ้าพื้นที่ไม่พอ
            current_y = height - 100  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20





    # สร้าง Style สำหรับภาษาไทย
    styles = getSampleStyleSheet()
    styleN = ParagraphStyle(name='Normal', fontName='Sarabun', fontSize=16)
    styleB = ParagraphStyle(name='Bold', fontName='SarabunBold', fontSize=16)

    # ตรวจสอบการขึ้นหน้าใหม่ก่อนแสดงหัวข้อ
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)

    # แสดงหัวข้อ
    start_y -= line_height  # ลดตำแหน่ง Y หลังจากวาดข้อความ
    # สร้างตาราง
    data = [[Paragraph("ภาระงาน/กิจกรรม/โครงการ/งาน", styleCenter),Paragraph( "จำนวน", styleCenter),Paragraph( "ภาระงาน", styleCenter),Paragraph( "รวมภาระงาน(เดิม)", styleCenter), Paragraph("หมายเหตุ", styleCenter)]]

    field_counter = 0
    for field in fields:
        field_counter += 1
        total_for_field = 0
        data.append([Paragraph(f"{field_counter}. {field.f_name}", styleB), "", "", "", ""])

        subfield_counter = 0
        for subfield in subfields.filter(f_id=field):
            subfield_counter += 1
            data.append([Paragraph(f"{field_counter}.{subfield_counter}. {subfield.sf_name}", styleN), "", "", "", ""])

            selection_counter = 0
            for selection in workload_selections.filter(sf_id=subfield):
                selection_counter += 1
                data.append([
                    Paragraph(f"{field_counter}.{subfield_counter}.{selection_counter}. {selection.selected_name}", styleN),
                    str(selection.selected_num),
                    f"{selection.selected_workload:.1f}",  # แสดงทศนิยม 1 ตำแหน่ง
                    f"{selection.selected_workload_edit:.1f} ({selection.calculated_workload:.1f})",  # แสดงทศนิยม 1 ตำแหน่ง
                    selection.notes or ""
                ])
                total_for_field += selection.calculated_workload
            
    # เพิ่มแถวที่เป็นตัวหนา
    data.append([Paragraph("รวมคะแนนสำหรับภาระงานทั้งหมด", styleB), "", "", f"{c_gtt:.1f} ({total_workload:.1f})", ""])
    data.append([Paragraph("คะแนนผลสัมฤทธิ์ของงาน", styleB), "", "", f"{c_sumwl:.1f} ({achievement_work:.1f})", ""])

    # ฟังก์ชันแบ่งข้อมูลเป็นชุด ๆ
    def chunk_data(data, chunk_size):
        """แบ่งข้อมูลออกเป็นชุด ๆ ตาม chunk_size"""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    # ฟังก์ชันสร้างตาราง
    def draw_table(p, data, start_x, start_y, max_rows_per_page):
        table_data = data[:max_rows_per_page]  # ดึงเฉพาะข้อมูลที่พอดีกับหน้า
        table = Table(table_data, colWidths=[9.75 * cm, 1.5 * cm, 2 * cm, 2.5 * cm, 2.5 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # จัดชิดซ้ายสำหรับคอลัมน์แรก
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # วาดตารางและลดตำแหน่ง Y
        w, h = table.wrap(width, height)  # คำนวณขนาดตาราง
        table.drawOn(p, start_x, start_y - h)  # วาดตารางที่ตำแหน่ง start_y ลดด้วย h
        return start_y - h  # คืนค่าตำแหน่งใหม่หลังจากวาดตาราง

    # คำนวณจำนวนแถวที่พอดีกับแต่ละหน้า
    max_rows_per_page = 22  # สมมติว่าเราจะแสดง 30 แถวต่อหน้า

    # วาดตารางในแต่ละหน้า
    for chunk in chunk_data(data, max_rows_per_page):
        start_y = height - 50  # กำหนดจุดเริ่มต้นของหน้าใหม่
        p.setFont("SarabunBold", 16)
        p.drawString(start_x, start_y, "ส่วนที่ 1 องค์ประกอบที่ 1 ผลสัมฤทธิ์ของงาน")
        # กำหนดหัวตาราง
        table_header = [[Paragraph("ภาระงาน/กิจกรรม/โครงการ/งาน", styleCenter),
                         Paragraph("จำนวน", styleCenter),
                         Paragraph("ภาระงาน", styleCenter),
                         Paragraph("รวมภาระงาน(เดิม)", styleCenter),
                         Paragraph("หมายเหตุ", styleCenter)]]
        start_y = height - 70
        start_y = draw_table(p, data + chunk, start_x, start_y, max_rows_per_page)  # วาดและอัพเดท start_y
        p.showPage()  # ขึ้นหน้าใหม่เมื่อวาดเสร็จ


    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง
    
    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=12, alignment=TA_CENTER)

    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 50, "ส่วนที่ 2 องค์ประกอบที่ 2 พฤติกรรมการปฏิบัติงาน (สมรรถนะ)")
    start_y -= line_height
    
    # สร้างตารางสมรรถนะหลัก
    data_main = [[Paragraph("สมรรถนะหลัก", styleCenter), Paragraph("ระดับสมรรถนะที่คาดหวัง", styleCenter), Paragraph("ระดับสมรรถนะที่แสดงออก", styleCenter)]]
    for score in main_scores:
        data_main.append([score.mc_id.mc_name, str(score.mc_id.mc_num), str(score.actual_score)])

    # สร้างตารางสมรรถนะเฉพาะ
    data_specific = [[Paragraph("สมรรถนะเฉพาะ", styleCenter), Paragraph("ระดับสมรรถนะที่คาดหวัง", styleCenter), Paragraph("ระดับสมรรถนะที่แสดงออก", styleCenter)]]
    for score in specific_scores:
        data_specific.append([score.sc_id.sc_name, str(score.sc_id.sc_num), str(score.actual_score)])

    # สร้างตารางสมรรถนะทางการบริหาร (ถ้ามี)
    if administrative_competencies:
        data_administrative = [[Paragraph("สมรรถนะทางการบริหาร", styleCenter), Paragraph("ระดับสมรรถนะที่คาดหวัง", styleCenter), Paragraph("ระดับสมรรถนะที่แสดงออก", styleCenter)]]
        for score in administrative_scores:
            data_administrative.append([score.adc_id.adc_name, str(score.uceo_num), str(score.actual_score)])
    else:
        data_administrative = []

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[9 * cm, 4 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # จัดชิดซ้ายสำหรับคอลัมน์แรก
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตาราง
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    # วางตารางสมรรถนะหลัก
    p.setFont("SarabunBold", 16)
    p.drawString(start_x, start_y, "สมรรถนะหลัก (ที่สภามหาวิทยาลัยกำหนด)")
    start_y -= line_height
    start_y = draw_table(p, data_main, start_x, start_y)

    # เพิ่มช่องว่าง
    start_y -= 2 * line_height

    # วางตารางสมรรถนะเฉพาะ
    p.setFont("SarabunBold", 16)
    p.drawString(start_x, start_y, "สมรรถนะเฉพาะ (ที่สภามหาวิทยาลัยกำหนด)")
    start_y -= line_height
    start_y = draw_table(p, data_specific, start_x, start_y)

    # วางตารางสมรรถนะทางการบริหารถ้ามี
    if data_administrative:
        start_y -= 2 * line_height
        p.setFont("SarabunBold", 16)
        p.drawString(start_x, start_y, "สมรรถนะทางการบริหาร (ถ้ามี)")
        start_y -= line_height
        start_y = draw_table(p, data_administrative, start_x, start_y)

    # เพิ่มช่องว่าง
    start_y -= 2 * line_height
    
    # สร้างตารางการประเมินคะแนน
    data = [
        [Paragraph("จำนวนสมรรถนะ", styleCenter), Paragraph("คูณ (X)", styleCenter), Paragraph("คะแนน", styleCenter)],
        [str(score_count[3]), "3", str(score_3_total)],
        [str(score_count[2]), "2", str(score_2_total)],
        [str(score_count[1]), "1", str(score_1_total)],
        [str(score_count[0]), "0", str(score_0_total)],
        ["", Paragraph("ผลรวมคะแนน", styleCenter), str(total_score)],
    ]

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[9 * cm, 4 * cm, 4 * cm])  # กำหนดขนาดคอลัมน์
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตารางและตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        p.setFont("SarabunBold", 16)
        p.drawString(start_x, start_y,"การประเมิน")
        start_y -= line_height
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    styleCenterA = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16)
    
    # วางตารางการประเมินคะแนน
    start_y = draw_table(p, data, start_x, start_y)

        # เพิ่มช่องว่าง
    start_y -= 2 * line_height
    p.setFont("SarabunBold", 16)
    p.drawString(start_x, start_y, f"ผลรวมคะแนน {total_score:.1f} / ผลรวมระดับสมรรถนะที่คาดหวัง {total_max_num:.1f} * 30 คะแนนที่ได้: {calculated_score:.1f}")
    start_y -= line_height
    # สร้างตารางการประเมินคะแนน
    data = [
        [Paragraph("หลักเกณฑ์การประเมิน", styleCenter)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก สูงกว่าหรือเท่ากับ ระดับสมรรถนะที่คาดหวัง x ๓ คะแนน", styleCenterA)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก ต่ำกว่า ระดับสมรรถนะที่คาดหวัง ๑ ระดับ x ๒ คะแนน", styleCenterA)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก ต่ำกว่า ระดับสมรรถนะที่คาดหวัง ๒ ระดับ x ๑ คะแนน", styleCenterA)],
        [Paragraph("จำนวนสมรรถนะหลัก/สมรรถนะเฉพาะ/สมรรถนะทางการบริหาร ที่มีระดับสมรรถนะที่แสดงออก ต่ำกว่า ระดับสมรรถนะที่คาดหวัง ๓ ระดับ x ๐ คะแนน", styleCenterA)],
    ]

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[17 * cm])  # กำหนดขนาดคอลัมน์
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'SarabunBold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตารางและตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    # วางตารางการประเมินคะแนน
    start_y = draw_table(p, data, start_x, start_y)

    p.showPage()

     # คำนวณคะแนนต่าง ๆ
    achievement_work = evaluation.achievement_work or 0
    mc_score = evaluation.mc_score or 0
    c_score = evaluation.c_sumwl or 0
    total_score = c_score + mc_score

    # กำหนดระดับผลการประเมิน
    if total_score >= 90:
        level = 'ดีเด่น'
    elif total_score >= 80:
        level = 'ดีมาก'
    elif total_score >= 70:
        level = 'ดี'
    elif total_score >= 60:
        level = 'พอใช้'
    else:
        level = 'ต้องปรับปรุง'


    # ตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง
    
    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=16, alignment=TA_CENTER)
    styleBB = ParagraphStyle(name='Bold', fontName='SarabunBold', fontSize=16)

    p.setFont("SarabunBold", 16)
    p.drawString(50, height - 50, "ส่วนที่ 3 สรุปการประเมินผลการปฏิบัติราชการ")

    data = [
        [Paragraph("องค์ประกอบการประเมิน", styleCenter),Paragraph("คะแนนเต็ม", styleCenter),Paragraph("คะแนนที่ได้", styleCenter),Paragraph("หมายเหตุ", styleCenter)],
        ["องค์ประกอบที่ 1: ผลสัมฤทธิ์ของงาน", "70", f"{c_score:.1f}", f"{evaluation.remark_achievement}"],
        ["องค์ประกอบที่ 2: พฤติกรรมการปฏิบัติราชการ (สมรรถนะ)", "30", f"{mc_score:.1f}", f"{evaluation.remark_mc}"],
        ["องค์ประกอบอื่น ๆ (ถ้ามี)", "", "", f"{evaluation.remark_other}"],
        [Paragraph("รวม", styleBB), "100", f"{total_score:.1f}", f"{evaluation.remark_total}"],
    ]

    # ฟังก์ชันสำหรับสร้างตารางใน PDF
    def draw_table(p, data, start_x, start_y):
        table = Table(data, colWidths=[9 * cm,2.5 * cm,2.5 * cm,4 * cm])  # กำหนดขนาดคอลัมน์
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Sarabun'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
            ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
            ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
        ]))

        # คำนวณขนาดตารางและตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่
        w, h = table.wrap(width, height)
        start_y = check_and_create_new_page(p, start_y, h, bottom_margin)

        # วางตาราง
        table.drawOn(p, start_x, start_y - h)
        return start_y - h  # คืนค่าตำแหน่ง Y ใหม่หลังจากวางตาราง

    # วางตารางการประเมินคะแนน
    start_y = draw_table(p, data, start_x, start_y)

    # แสดงระดับผลการประเมินในแบบ radio button (เลือกแล้ว)
    p.drawString(50, height - 250, "ระดับผลการประเมิน:")
    
    levels = [
        ("ดีเด่น (90 - 100)", total_score >= 90),
        ("ดีมาก (80 - 89.99)", 80 <= total_score < 90),
        ("ดี (70 - 79.99)", 70 <= total_score < 80),
        ("พอใช้ (60 - 69.99)", 60 <= total_score < 70),
        ("ต้องปรับปรุง (ต่ำกว่า 60)", total_score < 60),
    ]

    # วาด radio button (ข้อความแสดงผลการประเมิน)
    start_y = height - 280
    for level_text, is_selected in levels:
        p.circle(55, start_y, 5, fill=1 if is_selected else 0)  # วาดวงกลม
        p.drawString(70, start_y - 5, level_text)  # วาดข้อความข้าง ๆ
        start_y -= 20

    p.showPage()

    formset_data = PersonalDiagram.objects.filter(uevr_id=evaluation)

    # ฟังก์ชันตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20

    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    styleCenter = ParagraphStyle(name='Center', fontName='SarabunBold', fontSize=12, alignment=TA_CENTER)

    p.setFont("SarabunBold", 16)
    styleLeft = ParagraphStyle(name='Left', fontName='Sarabun', fontSize=16, alignment=0)
    styleCenter = ParagraphStyle(name='Center', fontName='Sarabun', fontSize=16, alignment=1)


    # แสดงหัวข้อ "ส่วนที่ 4 : แผนพัฒนาการปฏิบัติราชการรายบุคคล"
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    p.drawString(start_x, start_y, "ส่วนที่ 4 : แผนพัฒนาการปฏิบัติราชการรายบุคคล")
    start_y -= line_height

    # สร้างตารางที่มีฟิลด์ข้อมูลจาก formset_data
    data = [[Paragraph("ความรู้/ทักษะ/สมรรถนะ", styleCenter), Paragraph("วิธีการพัฒนา", styleCenter), Paragraph("ช่วงเวลาที่ต้องการพัฒนา", styleCenter)]]

    for item in formset_data:
        data.append([
        Paragraph(str(item.skill_evol), styleLeft),
        Paragraph(str(item.dev), styleLeft),
        Paragraph(str(item.dev_time), styleLeft)
    ])

    table = Table(data, colWidths=[6 * cm, 6 * cm, 5 * cm])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Sarabun'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Padding for left side
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding for right side
        ('TOPPADDING', (0, 0), (-1, -1), 5),    # Padding for top side
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # Padding for bottom side
        ('ROWHEIGHT', (0, 1), (-1, -1), 25),    # Row height for all rows in the body
    ]))

    # คำนวณความสูงของตารางและตรวจสอบว่ามีพื้นที่เพียงพอหรือไม่
    table_width, table_height = table.wrap(width, height)
    start_y = check_and_create_new_page(p, start_y, table_height, bottom_margin)
    table.drawOn(p, start_x, start_y - table_height)
    start_y -= table_height + line_height

    start_y -= 2* line_height

    # ความเห็นเพิ่มเติมของผู้ประเมิน
    start_y = check_and_create_new_page(p, start_y, line_height, bottom_margin)
    p.drawString(start_x, start_y, "ความเห็นเพิ่มเติมของผู้ประเมิน")
    start_y -= line_height

    # ส่วนแสดงความคิดเห็น
    p.drawString(start_x, start_y, "1) จุดเด่น และ/หรือ สิ่งที่ควรปรับปรุงแก้ไข")
    start_y -= line_height
    p.rect(start_x, start_y - 60, 483, 60)  # สร้างกล่องสำหรับแสดงความคิดเห็น
    p.setFont("Sarabun", 16)
    p.drawString(start_x + 5, start_y -20 , f"{evaluation.improved if evaluation.improved else ''}")
    start_y -= 80  # ลดระยะหลังจากกล่องแสดงความคิดเห็น
    p.setFont("SarabunBold", 16)
    p.drawString(start_x, start_y, "2) ข้อเสนอแนะเกี่ยวกับวิธีส่งเสริมและพัฒนา")
    start_y -= line_height
    p.rect(start_x, start_y - 60, 483, 60)  # สร้างกล่องสำหรับแสดงความคิดเห็น
    p.setFont("Sarabun", 16)
    p.drawString(start_x + 5, start_y -20 , f"{evaluation.suggestions if evaluation.suggestions else ''}")
    start_y -= 80  # ลดระยะหลังจากกล่องแสดงความคิดเห็น

    start_y -=  line_height
    p.setFont("SarabunBold", 16)
    p.line(start_x , start_y+20, start_x + 500, start_y+20)
    # ลายมือชื่อ
    start_y = check_and_create_new_page(p, start_y, 60, bottom_margin)
    p.drawString(start_x + 50, start_y, "ผู้ประเมินและผู้รับการประเมินได้ตกลงร่วมกันและเห็นพ้องกันแล้ว (ระบุข้อมูลให้ครบ)")
    start_y -= line_height
    p.drawString(start_x + 100, start_y, "จึงลงลายมือชื่อไว้เป็นหลักฐาน (ลงนามเมื่อจัดทำข้อตกลง)")
    start_y -= 2* line_height

    p.drawString(start_x+2, start_y, "ลายมือชื่อ.................................................(ผู้ประเมิน)")
    p.drawString(start_x + 240, start_y, f"ลายมือชื่อ.................................................(ผู้รับการประเมิน)")
    #if evaluation.full_name is None:
    #    p.drawString(start_x + 240, start_y, f"ลายมือชื่อ.................................................(ผู้รับการประเมิน)")
    #else:
    #    p.drawString(start_x + 288, start_y+2, f"{evaluation.full_name}")
    #    p.drawString(start_x + 240, start_y, f"ลายมือชื่อ.................................................(ผู้รับการประเมิน)")
    start_y -= line_height
    
    p.drawString(start_x + 25, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    p.drawString(start_x + 265, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    #if evaluation.full_name is None:
    #    p.drawString(start_x + 265, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    #else:
    #    p.drawString(start_x + 290, start_y-8, f"{evaluation.start_day}")
    #   p.drawString(start_x + 352, start_y-8, f"{evaluation.start_month}")
    #    p.drawString(start_x + 413, start_y-8, f"{evaluation.start_year}")
    #   p.drawString(start_x + 265, start_y-10, "วันที่..........เดือน...................พ.ศ. ............")
    p.line(start_x , start_y-20, start_x + 500, start_y-20)
    p.line(start_x , start_y+50, start_x + 500, start_y+50)
    p.line(start_x, start_y-20, start_x, start_y+100)
    p.line(start_x+500, start_y-20, start_x+500, start_y+100)
    p.line(start_x+236, start_y-20, start_x+236, start_y+50)

    p.showPage()


    # ฟังก์ชันตรวจสอบว่าต้องขึ้นหน้าใหม่หรือไม่ (เช็คระยะท้ายกระดาษ)
    def check_and_create_new_page(p, current_y, required_height, bottom_margin):
        if current_y - required_height < bottom_margin:
            p.showPage()  # ขึ้นหน้าใหม่
            current_y = height - 70  # รีเซ็ตตำแหน่ง current_y สำหรับหน้าใหม่
        return current_y  # คืนค่า current_y ที่ถูกต้อง

    bottom_margin = 50  # ระยะห่างจากท้ายกระดาษ
    start_x = 50
    start_y = height - 70
    line_height = 20

    p.setFont("SarabunBold", 16)

    start_y = check_and_create_new_page(p, start_y, 60, bottom_margin)

    p.drawString(start_x, start_y, "ส่วนที่ 5 การรับทราบผลการประเมิน")
    start_y -=2 * line_height
    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้รับการประเมิน :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y-10, "☐ ได้รับทราบผลการประเมิน")
    p.drawString(start_x + 20 , start_y-25, "และแผนพัฒนาการปฏิบัติราชการรายบุคคลแล้ว")

    p.drawString(start_x + 300, start_y, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-20, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-40, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-55)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-55)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-55)
    p.line(start_x , start_y-55, start_x + 480, start_y-55)
    start_y -= 2* line_height
    start_y -= 2* line_height
    start_y -=  line_height

    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้ประเมิน :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y, "☐ ได้แจ้งผลการประเมินและผู้รับการประเมินได้ลงนามรับทราบ")
    p.drawString(start_x + 5 , start_y-25, "☐ ได้แจ้งผลการประเมินเมื่อวันที่.................................................")
    p.drawString(start_x + 20 , start_y-45, "แต่ผู้รับการประเมินไม่ลงนามรับทราบผลการประเมิน")
    p.drawString(start_x + 20 , start_y-65, "โดยมี.......................................................................เป็นพยาน")

    p.drawString(start_x + 300, start_y-10, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-30, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-50, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-80)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-80)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-80)
    p.line(start_x , start_y-80, start_x + 480, start_y-80)
    start_y -= 2* line_height
    start_y -= 2* line_height
    start_y -= 2* line_height

    p.setFont("SarabunBold", 16)

    start_y = check_and_create_new_page(p, start_y, 60, bottom_margin)

    p.drawString(start_x, start_y, "ส่วนที่ 6 ความเห็นของผู้บังคับบัญชาเหนือขึ้นไป")
    start_y -= 2* line_height

    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้บังคับบัญชาเหนือขึ้นไป :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y, "☐ เห็นด้วยกับผลการประเมิน")
    p.drawString(start_x + 5 , start_y-25, "☐ มีความเห็นแตกต่าง ดังนี้")
    p.drawString(start_x + 20 , start_y-45, ".........................................................................................................")
    p.drawString(start_x + 20 , start_y-65, ".........................................................................................................")

    p.drawString(start_x + 300, start_y-10, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-30, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-50, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-80)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-80)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-80)
    p.line(start_x , start_y-80, start_x + 480, start_y-80)
    start_y -= 2* line_height
    start_y -= 2* line_height
    start_y -= 2* line_height

    p.setFont("SarabunBold", 14)
    p.line(start_x , start_y+15, start_x + 480, start_y+15)
    p.drawString(start_x +5 , start_y, "ผู้บังคับบัญชาเหนือขึ้นไปอีกชั้นหนึ่ง (ถ้ามี) :")
    p.line(start_x , start_y-10, start_x + 480, start_y-10)
    start_y -=2* line_height
    p.setFont("Sarabun", 14)

    p.drawString(start_x + 5, start_y, "☐ เห็นด้วยกับผลการประเมิน")
    p.drawString(start_x + 5 , start_y-25, "☐ มีความเห็นแตกต่าง ดังนี้")
    p.drawString(start_x + 20 , start_y-45, ".........................................................................................................")
    p.drawString(start_x + 20 , start_y-65, ".........................................................................................................")

    p.drawString(start_x + 300, start_y-10, "ลงชื่อ..........................................................")
    p.drawString(start_x + 300, start_y-30, "ตำแหน่ง.....................................................")
    p.drawString(start_x + 300, start_y-50, "วันที่...........................................................")
    p.line(start_x , start_y+55, start_x, start_y-80)
    p.line(start_x+280 , start_y+55, start_x + 280, start_y-80)
    p.line(start_x+480 , start_y+55, start_x + 480, start_y-80)
    p.line(start_x , start_y-80, start_x + 480, start_y-80)
    start_y -= 2* line_height

    p.save()

    return response



