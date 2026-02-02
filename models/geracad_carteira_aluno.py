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
    _description = 'Aluno da Carteira da Vale (matriculado no treinamento)'

    training_id = fields.Many2one(
        'geracad.carteira.treinamento',
        string='Treinamento',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Nome',
        required=True,
        help='Nome do aluno que aparecerá na carteira.',
    )
    matricula = fields.Char(
        string='Matrícula',
        help='Número de matrícula do aluno.',
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
        """Garante que o nome seja salvo em maiúsculas."""
        if 'name' in vals and vals.get('name'):
            vals['name'] = vals['name'].strip().upper()
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Garante que o nome seja salvo em maiúsculas e gera código de verificação."""
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].strip().upper()
            if not vals.get('verification_code'):
                vals['verification_code'] = self._generate_verification_code()
        return super().create(vals_list)
