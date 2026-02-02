# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class CarteiraVerificationController(http.Controller):

    @http.route('/carteira/verificar/<string:code>', type='http', auth='public', website=True)
    def verify_carteira(self, code, **kwargs):
        """Página pública para verificação da autenticidade da carteira."""
        carteira = request.env['geracad.carteira.aluno'].sudo().search([
            ('verification_code', '=', code)
        ], limit=1)

        if not carteira:
            return request.render('geracad_carteiras_vale.carteira_verification_invalid', {
                'code': code,
            })

        training = carteira.training_id
        company = training.company_id

        return request.render('geracad_carteiras_vale.carteira_verification_valid', {
            'carteira': carteira,
            'training': training,
            'company': company,
            'code': code,
        })
