#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.storage import Storage
from agiscore.db import unidad_organica
from agiscore import tools

def obtener_manejo():
    db = current.db
    definir_tabla()
    db.departamento.id.readable = False
    return tools.manejo_simple( db.departamento )

def obtener_por_uo(unidad_organica_id):
    """Dado una unidad organica retorna los departamentos"""
    db = current.db
    q  = (db.departamento.id > 0)
    q &= (db.departamento.unidad_organica_id == unidad_organica_id)
    return db(q).select(db.departamento.ALL,
                        orderby=db.departamento.nombre)

def seleccionar(context):
    # TODO: move this to modules.gui.departamento and
    # TODO: reimplement it
    assert isinstance(context, Storage)
    request = current.request
    response = current.response
    T = current.T
    db = current.db
    context.asunto = T('Seleccione Departamento')
    query = ((db.departamento.id > 0) &
        (db.departamento.unidad_organica_id == context.unidad_organica.id))
    context.manejo = tools.selector(query,
        [db.departamento.nombre, db.departamento.unidad_organica_id],
        'departamento_id')
    response.title = context.unidad_organica.nombre
    response.subtitle = T('Departamentos')
    return context

def definir_tabla():
    db = current.db
    T = current.T
    unidad_organica.definir_tabla()
    if not hasattr( db,'departamento' ):
        db.define_table( 'departamento',
            Field( 'nombre','string',length=20 ),
            Field( 'unidad_organica_id','reference unidad_organica' ),
            format="%(nombre)s",
            )
        db.departamento.nombre.label=T( 'Nombre' )
        db.departamento.nombre.requires = [IS_NOT_EMPTY(error_message=current.T('Información requerida'))]
        db.departamento.nombre.requires.append(IS_UPPER())
        db.departamento.unidad_organica_id.label=T( 'Unidad organica' )
        db.departamento.unidad_organica_id.requires = IS_IN_DB( db,'unidad_organica.id',"%(nombre)s",zero=None )
        db.commit()