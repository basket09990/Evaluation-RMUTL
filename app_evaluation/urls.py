from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('score', views.score, name='score'),
    path('score0', views.score0, name='score0'),

    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),

    path('groups/<int:group_id>/details/', views.group_detail_list, name='group_detail_list'),
    path('groups/<int:group_id>/details/add/', views.group_detail_add, name='group_detail_add'),
    path('groups/details/<int:pk>/edit/', views.group_detail_edit, name='group_detail_edit'),
    path('groups/details/<int:pk>/delete/', views.group_detail_delete, name='group_detail_delete'),

    # URL patterns สำหรับ wl_field
    path('wl_field/', views.wl_field_list, name='wl_field_list'),
    path('wl_field/add/', views.wl_field_add, name='wl_field_add'),
    path('wl_field/edit/<int:pk>/', views.wl_field_edit, name='wl_field_edit'),
    path('wl_field/delete/<int:pk>/', views.wl_field_delete, name='wl_field_delete'),

    # URL patterns สำหรับ wl_subfield
    path('wl_field/<int:pk>/subfields/', views.wl_subfield_list, name='wl_subfield_list'),
    path('wl_field/<int:field_id>/subfields/add/', views.wl_subfield_add, name='wl_subfield_add'),
    path('wl_subfield/edit/<int:pk>/', views.wl_subfield_edit, name='wl_subfield_edit'),
    path('wl_subfield/delete/<int:pk>/', views.wl_subfield_delete, name='wl_subfield_delete'),

    # URL patterns สำหรับ WorkloadCriteria
    path('wlsubfield/<int:subfield_id>/criteria/', views.workload_criteria_list, name='workload_criteria_list'),
    path('wlsubfield/<int:subfield_id>/criteria/add/', views.workload_criteria_add, name='workload_criteria_add'),
    path('workload_criteria/edit/<int:pk>/', views.workload_criteria_edit, name='workload_criteria_edit'),
    path('workload_criteria/delete/<int:pk>/', views.workload_criteria_delete, name='workload_criteria_delete'),

    path('competency/add/', views.add_main_competency, name='add_main_competency'),
    path('competency/edit/<int:mc_id>/', views.edit_main_competency, name='edit_main_competency'),
    path('competency/delete/<int:mc_id>/', views.delete_main_competency, name='delete_main_competency'),
    path('competency/', views.list_main_competency, name='list_main_competency'),

    path('specific_competency/add/', views.add_specific_competency, name='add_specific_competency'),
    path('specific_competency/edit/<int:sc_id>/', views.edit_specific_competency, name='edit_specific_competency'),
    path('specific_competency/delete/<int:sc_id>/', views.delete_specific_competency, name='delete_specific_competency'),
    path('specific_competency/', views.list_specific_competency, name='list_specific_competency'),

    path('administrative_competency/add/', views.add_administrative_competency, name='add_administrative_competency'),
    path('administrative_competency/edit/<int:adc_id>/', views.edit_administrative_competency, name='edit_administrative_competency'),
    path('administrative_competency/delete/<int:adc_id>/', views.delete_administrative_competency, name='delete_administrative_competency'),
    path('administrative_competency/', views.list_administrative_competency, name='list_administrative_competency'),

    path('search_evaluations/', views.search_evaluation, name='search_evaluations'),
    path('search_evaluations_2/', views.search_evaluations_2, name='search_evaluations_2'),
    path('evaluation/<int:uevr_id>/', views.view_evaluation, name='view_evaluation'),


    path('evaluation/evaluation_page1/<int:evaluation_id>/', views.evaluation_page1, name='evaluation_page1'),
    path('evaluation/evaluation_page2/<int:evaluation_id>/', views.evaluation_page2, name='evaluation_page2'),
    path('evaluation/evaluation_page3/<int:evaluation_id>/', views.evaluation_page3, name='evaluation_page3'),
    path('evaluation/evaluation_page4/<int:evaluation_id>/', views.evaluation_page4, name='evaluation_page4'),
    path('evaluation/evaluation_page5/<int:evaluation_id>/', views.evaluation_page5, name='evaluation_page5'),




    path('evaluation/evaluation_page/<int:criteria_id>/upload1/', views.upload_evidence1, name='upload_evidence1'),
    path('evaluation/evidence/<int:evidence_id>/delete1/', views.delete_evidence1, name='delete_evidence1'),


    path('add_personal_diagram1/<int:evaluation_id>/', views.add_personal_diagram1, name='add_personal_diagram1'),
    path('edit_personal_diagram1/<int:pd_id>/', views.edit_personal_diagram1, name='edit_personal_diagram1'),
    path('evaluation/delete_personal_diagram1/<int:pd_id>/', views.delete_personal_diagram1, name='delete_personal_diagram1'),



    path('evaluation/select_subfields2/<int:f_id>/<int:evaluation_id>/', views.select_subfields2, name='select_subfields2'),
    path('delete_subfield2/<int:sf_id>/', views.delete_selected_subfield2, name='delete_selected_subfield2'),
    path('evaluation/select_workload_criteria2/<int:evaluation_id>/<int:sf_id>/', views.select_workload_criteria2, name='select_workload_criteria2'),
    path('edit_workload_selection2/<int:selection_id>/', views.edit_workload_selection2, name='edit_workload_selection2'),
    path('delete_workload_selection2/<int:selection_id>/', views.delete_workload_selection2, name='delete_workload_selection2'),



    path('select_group/', views.select_group, name='select_group'),
    path('eval_0/', views.create_evaluation, name='eval_0'),


    path('upload_evidence/<int:criteria_id>/', views.upload_evidence, name='upload_evidence'),
    path('evaluation/evidence/<int:evidence_id>/delete/', views.delete_evidence, name='delete_evidence'),


    path('evaluation/evaluation_page/<int:evaluation_id>/', views.evaluation_page, name='evaluation_page'),
    path('evaluation/evaluation_page_2/<int:evaluation_id>/', views.evaluation_page_2, name='evaluation_page_2'),
    path('evaluation/evaluation_page_3/<int:evaluation_id>/', views.evaluation_page_3, name='evaluation_page_3'),
    path('evaluation/evaluation_page_4/<int:evaluation_id>/', views.evaluation_page_4, name='evaluation_page_4'),
    path('evaluation_page_5/<int:evaluation_id>/', views.evaluation_page_5, name='evaluation_page_5'),
    path('evaluation_page_6', views.evaluation_page_6, name='evaluation_page_6'),
    path('update_evr_status/<int:evaluation_id>/', views.update_evr_status, name='update_evr_status'),

    
    path('evaluation/<int:evaluation_id>/edit/', views.edit_evaluation, name='edit_evaluation'),



    path('evaluation/select_subfields/<int:f_id>/<int:evaluation_id>/', views.select_subfields, name='select_subfields'),
    path('delete_subfield/<int:sf_id>/', views.delete_selected_subfield, name='delete_selected_subfield'),
    path('evaluation/select_workload_criteria/<int:evaluation_id>/<int:sf_id>/', views.select_workload_criteria, name='select_workload_criteria'),
   
    path('edit_workload_selection/<int:selection_id>/', views.edit_workload_selection, name='edit_workload_selection'),
    path('delete_workload_selection/<int:selection_id>/', views.delete_workload_selection, name='delete_workload_selection'),
    path('add_personal_diagram/<int:evaluation_id>/', views.add_personal_diagram, name='add_personal_diagram'),
    path('edit_personal_diagram/<int:pd_id>/', views.edit_personal_diagram, name='edit_personal_diagram'),
    path('evaluation/delete_personal_diagram/<int:pd_id>/', views.delete_personal_diagram, name='delete_personal_diagram'),


    path('evaluation/evaluation_page_from_1/<int:evaluation_id>/', views.evaluation_page_from_1, name='evaluation_page_from_1'),
    path('evaluation_page_from_2/<int:evaluation_id>/', views.evaluation_page_from_2, name='evaluation_page_from_2'),
    path('evaluation_page_from_3/<int:evaluation_id>/', views.evaluation_page_from_3, name='evaluation_page_from_3'),
    path('evaluation_page_from_4/<int:evaluation_id>/', views.evaluation_page_from_4, name='evaluation_page_from_4'),
    path('evaluation_page_from_5/<int:evaluation_id>/', views.evaluation_page_from_5, name='evaluation_page_from_5'),

    path('evaluation/<int:evaluation_id>/export_excel/', views.export_evaluation_to_excel, name='export_evaluation_to_excel'),


    path('evaluation/evaluation_page/<int:criteria_id>/upload2/', views.upload_evidence2, name='upload_evidence2'),
    path('evaluation/evidence/<int:evidence_id>/delete2/', views.delete_evidence2, name='delete_evidence2'),



    path('evaluation/select_subfields3/<int:f_id>/<int:evaluation_id>/', views.select_subfields3, name='select_subfields3'),
    path('delete_subfield3/<int:sf_id>/', views.delete_selected_subfield3, name='delete_selected_subfield3'),
    path('evaluation/select_workload_criteria3/<int:evaluation_id>/<int:sf_id>/', views.select_workload_criteria3, name='select_workload_criteria3'),
    path('edit_workload_selection3/<int:selection_id>/', views.edit_workload_selection3, name='edit_workload_selection3'),
    path('delete_workload_selection3/<int:selection_id>/', views.delete_workload_selection3, name='delete_workload_selection3'),


    path('add_personal_diagram2/<int:evaluation_id>/', views.add_personal_diagram2, name='add_personal_diagram2'),
    path('edit_personal_diagram2/<int:pd_id>/', views.edit_personal_diagram2, name='edit_personal_diagram2'),
    path('evaluation/delete_personal_diagram2/<int:pd_id>/', views.delete_personal_diagram2, name='delete_personal_diagram2'),

    path('toggle-approve-status/<int:evaluation_id>/', views.toggle_approve_status, name='toggle_approve_status'),
    path('update_evr_status2/<int:evaluation_id>/', views.update_evr_status2, name='update_evr_status2'),

    path('get-subfields/<int:f_id>/', views.get_subfields, name='get_subfields'),
    path('get-criteria/<int:sf_id>/', views.get_criteria, name='get_criteria'),


    path('eval_2/', views.eval_2, name='eval_2'),
    path('eval_3/', views.eval_3, name='eval_3'),
    path('eval_4/', views.eval_4, name='eval_4'),
    path('eval_5/', views.eval_5, name='eval_5'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)