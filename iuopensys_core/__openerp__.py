{
    'name': 'IUOpenSys Core Module',
    'version': '0.1',
    'author': 'Khoa Phan',
    'category': 'University Management',
    'depends': ['base','percentage_widget','web_tree_dynamic_colored_field'],
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
        'data/department_data.xml',
        
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
        'menu/academic_menu.xml',
        'menu/student_menu.xml',
        'menu/university_menu.xml',
        
        # =========================================
        # WIZARDS
        # =========================================
        
        # =========================================
        # REPORTS
        # =========================================
        
             ],
             
}