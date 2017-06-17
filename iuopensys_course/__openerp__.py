{
    'name': 'IUOpenSys Course Module',
    'version': '0.1',
    'author': 'Khoa Phan',
    'category': 'University Management',
    'depends': ['base', 'iuopensys_core','calendar',],
    'data': [
        # =========================================
        # DATA
        # =========================================
        'data/course_tuition_data.xml',
        'data/study_period_data.xml',
        'data/partner_university_data.xml',
        'data/student_course_data.xml',
             
        # =========================================
        # SECURITY
        # =========================================
        'security/ir.model.access.csv',
        'security/iuopensys_security.xml',
        
        # =========================================
        # WIZARDS
        # =========================================
        'wizards/student_course_addition_wizard_view.xml',
        'wizards/student_balance_update_wizard_view.xml',
        
        # =========================================
        # VIEWS
        # =========================================
        'views/semester_view.xml',
        'views/course_view.xml',
        'views/offer_course_view.xml',
        'views/student_inherit_view.xml',
        'views/student_course_view.xml',
        'views/study_period_view.xml',
        'views/course_registration_view.xml',
        'views/student_registration_view.xml',
        'views/course_tuition_view.xml',
        'views/calendar_event_inherit_view.xml',
        'views/iu_document_view.xml',
        'views/partner_university_view.xml',
        'views/student_academic_program_view.xml',
        'views/student_document_view.xml',
        'views/iu_curriculum_view.xml',
        'views/major_inherit_view.xml',
        'views/financial_aid_view.xml',
#         'views/student_behavior_point_view.xml',
        'views/student_semester_view.xml',
        'views/student_financial_aid_view.xml',
        
        # =========================================
        # MENU
        # =========================================
        'menu/course_manage_menu.xml',
        
        # =========================================
        # REPORTS and CUSTOM ASSETS
        # =========================================
        'report/report_menu.xml',
        'report/report_exam_student_list.xml',
        'views/web_custom_assets.xml',
        ],
}