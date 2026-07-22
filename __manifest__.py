{
    'name': "Payroll and Remittance",
    'summary': "Employee Compensation & Deductions",
    'description': """
        Module for managing employee compensation and deductions
        - Compensation: Basic Salary, PERA, etc.
        - Deductions: GSIS, HDMF, Other Deductions
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '1.0',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_deduction.xml',
        'views/employee_compensation.xml',
        'views/employee_take_home_pay.xml',
        'views/hr_employee.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}