{
    'name': 'IUOpenSys Course Module',
    'version': '0.1',
    'author': 'Khoa Phan',
    'category': 'University Management',
    'depends': ['base', 'iuopensys_core','calendar'],
    'data': [
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
        
        # =========================================
        # MENU
        # =========================================
        'menu/course_manage_menu.xml',
        
        # =========================================
        # WIZARDS
        # =========================================
        
        # =========================================
        # REPORTS
        # =========================================
        
             ],
             
}