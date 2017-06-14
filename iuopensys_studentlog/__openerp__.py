{
    'name': 'IUOpenSys Student Log Module',
    'version': '0.1',
    'author': 'Khoa Phan',
    'category': 'University Management',
    'depends': ['base','iuopensys_course'],
    'data': [
        # =========================================
        # DATA
        # =========================================
        
        # =========================================
        # SECURITY
        # =========================================
        'security/ir.model.access.csv',
        
        # =========================================
        # WIZARDS
        # =========================================
        'wizards/add_graduation_date_wizard_view.xml',
        
        # =========================================
        # VIEWS
        # =========================================
        'views/student_log_view.xml',
        'views/student_inherit_view.xml',
        'views/year_batch_inherit_view.xml',
        
        # =========================================
        # MENU
        # =========================================
        'menu/student_log_menu.xml',
        
        
        # =========================================
        # REPORTS and CUSTOM ASSETS
        # =========================================
        'report/report_menu.xml',
        'report/report_student_transcript.xml',
        'report/report_graduating_student.xml',
        'report/report_student_progress.xml',
        
        ],
}