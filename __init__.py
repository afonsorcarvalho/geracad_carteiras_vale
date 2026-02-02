# -*- coding: utf-8 -*-

from . import models
from . import controllers


def post_init_hook(cr, registry):
    """Migra training_date para date_start em instalações que tinham o campo antigo."""
    try:
        with cr.savepoint():
            cr.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'geracad_carteira_treinamento' AND column_name = 'training_date'
            """)
            if cr.fetchone():
                cr.execute("""
                    UPDATE geracad_carteira_treinamento
                    SET date_start = training_date
                    WHERE date_start IS NULL AND training_date IS NOT NULL
                """)
    except Exception:
        pass
