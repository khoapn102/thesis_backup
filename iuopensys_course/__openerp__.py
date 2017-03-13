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