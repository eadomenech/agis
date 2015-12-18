# -*- coding: utf-8 -*-
if False:
    from gluon import *
    from db import *
    from menu import *
    from tables import *
    from gluon.contrib.appconfig import AppConfig
    from gluon.tools import Auth, Service, PluginManager
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T
    db = DAL('sqlite://storage.sqlite')
    myconf = AppConfig(reload=True)
    auth = Auth(db)
    service = Service()
    plugins = PluginManager()
    from agiscore.gui.mic import MenuLateral, MenuMigas
    menu_lateral = MenuLateral(list())
    menu_migas = MenuMigas()
    
from gluon.storage import Storage
from agiscore.gui.unidad_organica import manejo_unidades
from agiscore.gui.carrera_ies import grid_carreras_ies
from agiscore.gui.escuela_media import manejo_escuelas_medias
from agiscore.gui.mic import Accion, grid_simple

#TODO: remove
response.menu = []

menu_lateral.append(
    Accion(T('Configurar Escuela'), URL('editar'),
           auth.has_membership(role=myconf.take('roles.admin'))),
    ['editar'])
menu_lateral.append(
    Accion(T('Unidades'), URL('index'),
           (auth.user is not None)),
    ['index'])
menu_lateral.append(
    Accion(T('Infraestructura'), URL('infraestructura'),
           auth.has_membership(role=myconf.take('roles.admin'))),
    ['infraestructura'])
menu_lateral.append(
    Accion(T('Carreras'), URL('carreras'),
           auth.has_membership(role=myconf.take('roles.admin'))),
    ['carreras'])
menu_lateral.append(
    Accion(T('Asignaturas'), URL('asignaturas'),
           auth.has_membership(role=myconf.take('roles.admin')),
           _title=T("Registro general de asignaturas")),
    ['asignaturas'])
menu_lateral.append(
    Accion(T('Centros enseñanza media'), URL('media'),
           auth.has_membership(role=myconf.take('roles.admin'))),
    ['media'])
menu_lateral.append(
    Accion(T('Seguridad'), URL('appadmin', 'manage', args=['auth']),
           auth.has_membership(role=myconf.take('roles.admin'))),
    [])

@auth.requires_login()
def index():
    C = Storage()
    C.escuela = db.escuela(1)
    # Preparar grid para las unidades
    C.unidades = manejo_unidades(C.escuela, db, T)
    return dict(C=C)

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')))
def editar():
    C = Storage()
    C.escuela = db.escuela(1)
    db.escuela.id.readable = False
    C.form = SQLFORM(db.escuela,
                     record=C.escuela,
                     upload=URL('default', 'download'),
                     submit_button=T("Guardar"))
    C.form.add_button(T("Cancelar"), URL('index'))
    if C.form.process().accepted:
        redirect(URL('index'))
    
    return dict(C=C)

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')))
def carreras():
    C = Storage()
    C.escuela = db.escuela(1)
    
    # escoger carreras a utilizar en la escuela
    C.grid = grid_carreras_ies(C.escuela, db, T)
    
    return dict(C=C)

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')))
def asignaturas():
    '''registro general de asigaturas'''
    C = Storage()
    C.escuela = db.escuela(1)
    
    menu_migas.append(T("Registro de asignaturas"))
    
    # -- construir el grid
    tbl = db.asignatura
    query = (tbl.id > 0)
    
    # permisos
    puede_crear = auth.has_membership(role=myconf.take('roles.admin'))
    puede_editar, puede_borrar = (puede_crear, puede_crear)
    
    tbl.id.readable = False
    
    C.grid = grid_simple(query,
                         create=puede_crear,
                         editable=puede_editar,
                         deletable=puede_borrar)
    
    return dict(C=C)

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')))
def media():
    '''Manejo de las escuelas de enseñanza media'''
    C = Storage()
    C.escuela = db.escuela(1)
    
    C.grid = manejo_escuelas_medias(db, T)
    
    return dict(C=C)

def obtener_municipios():
    """Cuando es llamado por AJAX retorna la lista de municipios según la provincia"""
    from agiscore.db import municipio
    provincia_id = request.vars.provincia_id
    municipios = municipio.obtener_municipios(provincia_id)
    rs = ''
    for muni in municipios:
        op = OPTION(muni.nombre, _value=muni.id)
        rs += op.xml()
    return rs

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')))
def infraestructura():
    db.campus.id.readable = False
    db.edificio.id.readable = False
    db.aula.id.readable = False
    # smargrid se encarga de inicializar estos a los valores corectos
    db.edificio.campus_id.writable = False
    db.aula.edificio_id.writable = False
    manejo = SQLFORM.smartgrid(db.campus,
                               linked_tables=['edificio',
                                              'aula'],
                               csv=False,
                               details=False,
                               # TODO: ver si se puede activar en alguna actulización
                               #       de web2py
                               sortable=False,
                               formname="infraestructura",
                               showbuttontext=False)
    return dict(manejo=manejo)