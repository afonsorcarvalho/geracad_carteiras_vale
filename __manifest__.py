# -*- coding: utf-8 -*-
{
    'name': "Carteiras da Vale - Treinamento",

    'summary': """
        Geração de carteiras (certificados) de treinamento para alunos matriculados""",

    'description': """
        Módulo para cadastro de treinamentos e geração de carteiras em PDF
        no formato de declaração de participação (Reciclagem de Plataforma Elevatória, etc.).
    """,

    'author': "Netcom Treinamentos e Soluções Tecnológicas",
    'website': "http://www.netcom-ma.com.br",

    'category': 'Academico',
    'version': '14.0.1.1',

    'depends': [
        'base',
        'website',
        'geracad_curso',
    ],

    'external_dependencies': {
        'python': ['qrcode', 'Pillow'],
    },

    'data': [
        'security/geracad_carteiras_vale_security.xml',
        'security/ir.model.access.csv',
        'report/carteira_vale_report.xml',
        'report/carteira_vale_template.xml',
        'report/carteira_entrega_template.xml',
        'views/geracad_carteira_treinamento_views.xml',
        'views/menu_views.xml',
        'views/carteira_verification_templates.xml',
    ],

    'post_init_hook': 'post_init_hook',
}
