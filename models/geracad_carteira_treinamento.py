# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class GeracadCarteiraTreinamento(models.Model):
    _name = 'geracad.carteira.treinamento'
    _description = 'Treinamento para Carteira de Vale'

    name = fields.Char(
        string='Treinamento',
        required=True,
        help='Ex: Reciclagem de Plataforma Elevatória',
    )
    description = fields.Text(
        string='Descrição do Treinamento',
        help='Ex: Empregado que executa atividade de: Operador Plataforma Elevatória | PEMT | Grupo 3B - Tipo Lança Articulada Diesel ou Elétrica',
    )
    training_date = fields.Date(
        string='Data do Treinamento',
        required=True,
    )
    validity_date = fields.Date(
        string='Validade',
        compute='_compute_validity_date',
        store=True,
        readonly=False,
        help='Preenchido automaticamente: 2 anos após a data do treinamento.',
    )
    workload_hours = fields.Float(
        string='Carga Horária (horas)',
        default=8.0,
        help='Carga horária do treinamento (igual para todos os matriculados). Ex: 8 ou 4 horas.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.company,
        required=True,
    )
    coordinator_name = fields.Char(
        string='Coordenador Pedagógico',
        required=True,
    )
    instructor_name = fields.Char(
        string='Instrutor',
        required=True,
    )
    instructor_signature = fields.Binary(
        string='Assinatura do Instrutor',
        attachment=True,
    )
    coordinator_signature = fields.Binary(
        string='Assinatura do Coordenador',
        attachment=True,
    )
    student_ids = fields.One2many(
        'geracad.carteira.aluno',
        'training_id',
        string='Alunos Matriculados',
    )
    student_count = fields.Integer(
        string='Quantidade de Alunos',
        compute='_compute_student_count',
        store=True,
    )

    @api.depends('training_date')
    def _compute_validity_date(self):
        for rec in self:
            if rec.training_date:
                rec.validity_date = rec.training_date + relativedelta(years=2)
            else:
                rec.validity_date = False

    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)

    def action_print_carteiras(self):
        """Abre o relatório de carteiras em PDF para os alunos matriculados."""
        self.ensure_one()
        if not self.student_ids:
            return
        return self.env.ref('geracad_carteiras_vale.action_report_carteira_vale').report_action(self)

    def get_signature_data_uri(self, field_name='instructor_signature'):
        """Retorna o campo Binary como data URI para uso em relatório (img src)."""
        self.ensure_one()
        value = getattr(self, field_name, None)
        if not value:
            return ''
        if isinstance(value, bytes):
            import base64
            return 'data:image/png;base64,' + base64.b64encode(value).decode('utf-8')
        return 'data:image/png;base64,' + (value if isinstance(value, str) else '')

    def get_company_logo_data_uri(self):
        """Retorna o logo da empresa do usuário (res.company do env) como data URI para uso no relatório."""
        self.ensure_one()
        company = self.env.company
        if not company or not company.logo:
            return ''
        value = company.logo
        if isinstance(value, bytes):
            import base64
            return 'data:image/png;base64,' + base64.b64encode(value).decode('utf-8')
        return 'data:image/png;base64,' + (value if isinstance(value, str) else '')

    def get_student_chunks(self, chunk_size=3):
        """Retorna os alunos agrupados em listas de até chunk_size (ex.: 3 por página)."""
        self.ensure_one()
        students = self.student_ids
        return [students[i:i + chunk_size] for i in range(0, len(students), chunk_size)]
