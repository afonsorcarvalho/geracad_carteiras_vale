# -*- coding: utf-8 -*-

import uuid
import base64
from io import BytesIO
from odoo import models, fields, api

try:
    import qrcode
except ImportError:
    qrcode = None


class GeracadCarteiraAluno(models.Model):
    _name = 'geracad.carteira.aluno'
    _description = 'Aluno Matriculado no Treinamento (Carteira de Vale)'

    training_id = fields.Many2one(
        'geracad.carteira.treinamento',
        string='Treinamento',
        required=True,
        ondelete='cascade',
    )
    aluno_id = fields.Many2one(
        'res.partner',
        string='Aluno',
        required=True,
        domain=[('e_aluno', '=', True)],
        help='Selecione um aluno cadastrado no sistema',
    )
    student_name = fields.Char(
        string='Nome do Aluno (na Carteira)',
        compute='_compute_student_name',
        store=True,
        readonly=False,
        help='Nome que aparecerá na carteira (ex: Sr. Alex Tadeu de Souza Alexandrino). Pode ser editado.',
    )
    verification_code = fields.Char(
        string='Código de Verificação',
        required=True,
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: self._generate_verification_code(),
        help='Código único para verificação pública da autenticidade da carteira.',
    )

    @api.model
    def _generate_verification_code(self):
        """Gera um código único de verificação usando UUID."""
        return str(uuid.uuid4()).replace('-', '')[:32].upper()

    @api.depends('aluno_id', 'aluno_id.name', 'aluno_id.sexo')
    def _compute_student_name(self):
        for rec in self:
            if rec.aluno_id:
                name = (rec.aluno_id.name or '').strip()
                if name and not name.upper().startswith('SR') and not name.upper().startswith('SRA'):
                    sexo = rec.aluno_id.sexo
                    if sexo == 'M':
                        name = 'Sr. ' + name
                    elif sexo == 'F':
                        name = 'Sra. ' + name
                    else:
                        name = 'Sr./Sra. ' + name
                rec.student_name = name.upper() if name else ''
            else:
                rec.student_name = ''

    def get_verification_url(self):
        """Retorna a URL pública para verificação da carteira."""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
        return f"{base_url}/carteira/verificar/{self.verification_code}"

    def get_qr_code_image(self):
        """Gera e retorna o QR code como imagem base64 para uso no relatório."""
        self.ensure_one()
        if not qrcode:
            return ''
        try:
            url = self.get_verification_url()
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=4,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f'data:image/png;base64,{img_str}'
        except Exception:
            return ''

    def write(self, vals):
        """Garante que o nome na carteira seja sempre salvo em maiúsculas."""
        if 'student_name' in vals and vals['student_name']:
            vals['student_name'] = vals['student_name'].strip().upper()
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Garante que o nome na carteira seja sempre salvo em maiúsculas e gera código de verificação."""
        for vals in vals_list:
            if vals.get('student_name'):
                vals['student_name'] = vals['student_name'].strip().upper()
            if not vals.get('verification_code'):
                vals['verification_code'] = self._generate_verification_code()
        return super().create(vals_list)
