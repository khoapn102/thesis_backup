{
    'name': 'IUOpenSys Course Module',
    'version': '0.1',
    'author': 'Khoa Phan',
    'category': 'University Management',
    'depends': ['base', 'iuopensys_core','calendar'],
    'data': [
        # =========================================
        # DATA
        # =========================================
        'data/course_tuition_data.xml',
        'data/study_period_data.xml',
        'data/partner_university_data.xml',
             
        # =========================================
        # SECURITY
        # =========================================
        
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
        'views/student_behavior_point_view.xml',
        
        # =========================================
        # MENU
        # =========================================
        'menu/course_manage_menu.xml',
        
        # =========================================
        # WIZARDS
        # =========================================
        
        # =========================================
        # REPORTS and CUSTOM ASSETS
        # =========================================
        
        'views/web_custom_assets.xml',
        ],
}