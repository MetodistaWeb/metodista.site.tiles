# -*- coding: utf-8 -*-

from metodista.site.tiles.config import PROJECTNAME

import logging

logger = logging.getLogger(PROJECTNAME)


def setup(context):
    """ Descricao bse da atualizacao
    """
    logger.info('Faz nada - padrao de passo de atualizacao')
