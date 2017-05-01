{
    'name': 'IUOpenSys Core Module',
    'version': '0.1',
    'author': 'Khoa Phan',
    'category': 'University Management',
    'depends': ['base','percentage_widget',],
    'data': [
        # =========================================
        # SECURITY
        # =========================================
        'security/iuopensys_security.xml',
        'security/ir.model.access.csv',
        
        # =========================================
        # SEQUENCE CODE
        # ========================================= 
        'data/student_code_sequence.xml',
        
        # =========================================
        # VIEWS
        # =========================================        
        'views/student_view.xml',
        'views/department_view.xml',
        'views/major_view.xml',
        'views/lecturer_view.xml',
        'views/year_batch_view.xml',
        'views/academic_year_view.xml',
        
        # =========================================
        # MENU
        # =========================================
        'menu/student_menu.xml',
        'menu/university_menu.xml',
        'menu/academic_menu.xml',
        
        # =========================================
        # WIZARDS
        # =========================================
        
        # =========================================
        # REPORTS
        # =========================================
        
             ],
             
}