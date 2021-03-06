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
from agiscore.gui.mic import Accion, grid_simple
from agiscore import tools

# TODO: remove
response.menu = []

menu_lateral.append(Accion(T('Asignación de aulas'),
                           URL('index', args=[request.args(0)]),
                           True),
                    ['index'])
menu_lateral.append(Accion(T('Codificación de los estudiantes'),
                           URL('codificacion', args=[request.args(0)]),
                           auth.has_membership(role=myconf.take('roles.admin')) or
                           auth.has_membership(role=myconf.take('roles.oexamen'))),
                    ['codificacion'])
menu_lateral.append(Accion(T('Asignación de notas'),
                           URL('notas', args=[request.args(0)]),
                           True),
                    ['notas'])
menu_lateral.append(Accion(T('Reporte de notas'),
                           URL('notas_reporte', args=[request.args(0)]),
                           auth.has_membership(role=myconf.take('roles.admin')) or
                           auth.has_membership(role=myconf.take('roles.admdocente'))),
                    ['notas_reporte'])
menu_lateral.append(Accion(T('Distribución por aulas'),
                           URL('distribucion', args=[request.args(0)]),
                           True),
                    ['distribucion'])

@auth.requires_login()
def index():
    """Configuración de las aulas"""
    C = Storage()
    C.examen = db.examen(int(request.args(0)))
    C.asignatura = C.examen.asignatura_id
    C.evento = db.evento(C.examen.evento_id)
    C.ano = db.ano_academico(C.evento.ano_academico_id)
    C.unidad = db.unidad_organica(C.ano.unidad_organica_id)
    C.escuela = db.escuela(C.unidad.escuela_id)

    # breadcumbs
    u_link = Accion(C.unidad.abreviatura or C.unidad.nombre,
                    URL('unidad', 'index', args=[C.unidad.id]),
                    True)  # siempre dentro de esta funcion
    menu_migas.append(u_link)
    a_links = Accion(T('Años académicos'),
                     URL('unidad', 'index', args=[C.unidad.id]),
                     True)
    menu_migas.append(a_links)
    e_link = Accion(C.evento.nombre,
                    URL('evento','index', args=[C.evento.id]),
                    True)
    menu_migas.append(e_link)
    menu_migas.append(db.examen._format(C.examen))
    menu_migas.append(T('Asignación de aulas'))
    
    # -- permisos
    puede_borrar = auth.has_membership(role=myconf.take('roles.admin'))
    puede_crear = auth.has_membership(role=myconf.take('roles.admin'))
    puede_editar = auth.has_membership(role=myconf.take('roles.admin'))
    
    # -- configurar grid
    tbl = db.examen_aula
    query = (tbl.id > 0) & (tbl.examen_id == C.examen.id)
    
    if 'new' in request.args:
        tbl.examen_id.default = C.examen.id
        tbl.examen_id.writable = False
        
        estan_set = (db.aula.id > 0) & (db.aula.id == db.examen_aula.aula_id)
        estan_set &= (db.examen_aula.examen_id == C.examen.id)
        estan = [a.id for a in db(estan_set).select(db.aula.id)]
        a_set  = (db.aula.id > 0) & (db.aula.disponible == True)
        a_set &= (~db.aula.id.belongs(estan))
        posibles = IS_IN_DB(db(a_set), db.aula.id, '%(nombre)s', zero=None)
        db.examen_aula.aula_id.requires = posibles
    
    C.titulo = "{}: {}".format(T("Aulas para el exámen"),
                               db.examen._format(C.examen))
    # -- configurar los campos
    tbl.id.readable = False
    tbl.examen_id.readable = False
    
    # -- datos de capacidad
    from agiscore.db.examen import obtener_candidaturas, obtener_aulas
    from agiscore.db.aula import capacidad_total
    C.a_examinar = len(obtener_candidaturas(C.examen.id))
    C.a_capacidad = capacidad_total(obtener_aulas(C.examen.id))
    
    C.grid = grid_simple(query,
                         create=puede_crear,
                         editable=puede_editar,
                         deletable=puede_borrar,
                         searchable=False,
                         history=False,
                         args=request.args[:1])
    
    return dict(C=C)

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')) or
               auth.has_membership(role=myconf.take('roles.profesor')) or
               auth.has_membership(role=myconf.take('roles.oexamen')))
def notas():
    '''Asignación de las notas'''
    C = Storage()
    C.examen = db.examen(int(request.args(0)))
    C.asignatura = C.examen.asignatura_id
    C.evento = db.evento(C.examen.evento_id)
    C.ano = db.ano_academico(C.evento.ano_academico_id)
    C.unidad = db.unidad_organica(C.ano.unidad_organica_id)
    C.escuela = db.escuela(C.unidad.escuela_id)

    # breadcumbs
    u_link = Accion(C.unidad.abreviatura or C.unidad.nombre,
                    URL('unidad', 'index', args=[C.unidad.id]),
                    True)  # siempre dentro de esta funcion
    menu_migas.append(u_link)
    a_links = Accion(T('Años académicos'),
                     URL('unidad', 'index', args=[C.unidad.id]),
                     True)
    menu_migas.append(a_links)
    e_link = Accion(C.evento.nombre,
                    URL('evento','index', args=[C.evento.id]),
                    True)
    menu_migas.append(e_link)
    menu_migas.append(db.examen._format(C.examen))
    menu_migas.append(T('Asignación de notas'))

    from agiscore.gui.nota import form_editar_nota, grid_asignar_nota
    if 'new' in request.args:
        if not request.vars.estudiante_id:
            raise HTTP(404)
        est = db.estudiante(int(request.vars.estudiante_id))
        # el componente que envuelve al formulario y el formulario en si
        c, f = form_editar_nota(C.examen, est)
        if f.process().accepted:
            session.flash = T('Nota actualizada')
            redirect(URL('notas', args=[C.examen.id]))
        C.grid = c
    else:
        
        C.grid = grid_asignar_nota(C.examen)
    
    return dict(C=C)

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')) or
               auth.has_membership(role=myconf.take('roles.admdocente')))
def notas_reporte():
    '''Reporte de las notas de los estudiantes para este examen'''
    C = Storage()
    C.examen = db.examen(int(request.args(0)))
    C.asignatura = C.examen.asignatura_id
    C.evento = db.evento(C.examen.evento_id)
    C.ano = db.ano_academico(C.evento.ano_academico_id)
    C.unidad = db.unidad_organica(C.ano.unidad_organica_id)
    C.escuela = db.escuela(C.unidad.escuela_id)

    # breadcumbs
    u_link = Accion(C.unidad.abreviatura or C.unidad.nombre,
                    URL('unidad', 'index', args=[C.unidad.id]),
                    True)  # siempre dentro de esta funcion
    menu_migas.append(u_link)
    a_links = Accion(T('Años académicos'),
                     URL('unidad', 'index', args=[C.unidad.id]),
                     True)
    menu_migas.append(a_links)
    e_link = Accion(C.evento.nombre,
                    URL('evento','index', args=[C.evento.id]),
                    True)
    menu_migas.append(e_link)
    menu_migas.append(T('Reporte de resultados'))

    C.titulo = "{} - {}".format(db.examen._format(C.examen), C.evento.nombre)
    from agiscore.db import nota as nota_model
    nota_model.crear_entradas(C.examen.id)
    
    query  = (db.nota.examen_id == C.examen.id)
    query &= (db.nota.estudiante_id == db.estudiante.id)
    query &= (db.estudiante.persona_id == db.persona.id)
    query &= (db.candidatura.estudiante_id == db.nota.estudiante_id)
    
    # preparar campos
    for f in db.nota:
        f.readable = False
    for f in db.persona:
        f.readable = False
    for f in db.estudiante:
        f.readable = False
    for f in db.candidatura:
        f.readable = False
    db.candidatura.numero_inscripcion.readable = True
    db.candidatura.numero_inscripcion.label = T('#INS')
    db.persona.nombre_completo.readable = True
    db.persona.nombre_completo.label = T("Nombre")
    db.nota.valor.readable = True
    db.nota.valor.label = T("Nota")
    
    campos = [db.candidatura.numero_inscripcion,
              db.persona.nombre_completo,
              db.nota.valor]
    text_lengths={'persona.nombre_completo': 50}
    exportadores = dict(xml=False, html=False, csv_with_hidden_cols=False,
        csv=False, tsv_with_hidden_cols=False, tsv=False, json=False,
        PDF=(tools.ExporterPDF, 'PDF'))
    
    if request.vars._export_type:
        response.context = C
    
    C.grid = grid_simple(query,
                         orderby=[db.persona.nombre_completo],
                         maxtextlengths=text_lengths,
                         exportclasses=exportadores,
                         csv=True,
                         fields=campos,
                         create=False,
                         editable=False,
                         deletable=False,
                         history=False,
                         args=request.args[:1])
    
    
    return dict(C=C)

@auth.requires(auth.has_membership(role=myconf.take('roles.admin')))
def codificacion():
    C = Storage()
    C.examen = db.examen(int(request.args(0)))
    C.asignatura = C.examen.asignatura_id
    C.evento = db.evento(C.examen.evento_id)
    C.ano = db.ano_academico(C.evento.ano_academico_id)
    C.unidad = db.unidad_organica(C.ano.unidad_organica_id)
    C.escuela = db.escuela(C.unidad.escuela_id)

    # breadcumbs
    u_link = Accion(C.unidad.abreviatura or C.unidad.nombre,
                    URL('unidad', 'index', args=[C.unidad.id]),
                    True)  # siempre dentro de esta funcion
    menu_migas.append(u_link)
    a_links = Accion(T('Años académicos'),
                     URL('unidad', 'index', args=[C.unidad.id]),
                     True)
    menu_migas.append(a_links)
    e_link = Accion(C.evento.nombre,
                    URL('evento','index', args=[C.evento.id]),
                    True)
    menu_migas.append(e_link)
    menu_migas.append(db.examen._format(C.examen))
    menu_migas.append(T('Codificación de los estudiantes'))
    
    # -- configuración del grid
    query = ((db.examen_aula_estudiante.examen_id == C.examen.id) & 
            (db.estudiante.id == db.examen_aula_estudiante.estudiante_id) & 
            (db.persona.id == db.estudiante.persona_id) & 
            (db.candidatura.estudiante_id == \
                db.examen_aula_estudiante.estudiante_id))
    
    exportadores = dict(xml=False, html=False, csv_with_hidden_cols=False,
        csv=False, tsv_with_hidden_cols=False, tsv=False, json=False,
        PDF=(tools.ExporterPDF, 'PDF'))
    
    text_lengths={'persona.nombre_completo': 50,
                  'persona.uuid': 100}
    
    # --conf campos
    for f in db.persona:
        f.readable = False
    db.persona.nombre_completo.readable = True
    db.persona.numero_identidad.readable = True
    db.persona.uuid.readable = True
    db.persona.uuid.label = 'UUID'
    for f in db.examen_aula_estudiante:
        f.readable = False
    db.examen_aula_estudiante.aula_id.readable = True
    for f in db.estudiante:
        f.readable = False
    for f in db.candidatura:
        f.readable = False
    campos=[db.persona.nombre_completo,
            db.persona.numero_identidad,
            db.persona.uuid,
            db.examen_aula_estudiante.aula_id]
    C.titulo = T('Codificación de los estudiantes')
    
    if request.vars._export_type:
        response.context = C
    
    C.grid = grid_simple(query,
                         fields=campos,
                         orderby=[db.persona.nombre_completo,
                                  db.examen_aula_estudiante.aula_id],
                         csv=True,
                         searchable=True,
                         create=False,
                         history=False,
                         maxtextlengths=text_lengths,
                         exportclasses=exportadores,
                         args=request.args[:1])
    
    return dict(C=C)

@auth.requires_login()
def distribucion():
    '''Distribución de estudiantes por aulas'''
    C = Storage()
    C.examen = db.examen(int(request.args(0)))
    C.asignatura = C.examen.asignatura_id
    C.evento = db.evento(C.examen.evento_id)
    C.ano = db.ano_academico(C.evento.ano_academico_id)
    C.unidad = db.unidad_organica(C.ano.unidad_organica_id)
    C.escuela = db.escuela(C.unidad.escuela_id)

    # breadcumbs
    u_link = Accion(C.unidad.abreviatura or C.unidad.nombre,
                    URL('unidad', 'index', args=[C.unidad.id]),
                    True)  # siempre dentro de esta funcion
    menu_migas.append(u_link)
    a_links = Accion(T('Años académicos'),
                     URL('unidad', 'index', args=[C.unidad.id]),
                     True)
    menu_migas.append(a_links)
    e_link = Accion(C.evento.nombre,
                    URL('evento','index', args=[C.evento.id]),
                    True)
    menu_migas.append(e_link)
    menu_migas.append(db.examen._format(C.examen))
    menu_migas.append(T('Distribución por aulas'))
    
    C.titulo = "{} - {}".format(T("Distribución de los estudiantes por aulas"),
                               db.examen._format(C.examen))
    
    from agiscore.db.examen_aula_estudiante import distribuir_estudiantes
    
    puede_distribuir  = auth.has_membership(role=myconf.take('roles.oexamen'))
    puede_distribuir |= auth.has_membership(role=myconf.take('roles.admin')) 
    # distribuir a los estudiantes por las aulas que tenemos definidas
    C.distribuir_link = Accion(CAT(SPAN('', _class='glyphicon glyphicon-hand-up'),
                         ' ',
                         T("Distribuir aulas")),
                     URL('distribucion',
                         args=[C.examen.id],
                         vars={'_distribuir': '1'}),
                     puede_distribuir,
                     _class="btn btn-default")
    if request.vars._distribuir:
        distribuir_estudiantes(C.examen.id)
        redirect(URL('distribucion', args=[C.examen.id]))
    
    cantidad = db(db.examen_aula_estudiante.examen_id == C.examen.id).count()
    if cantidad > 0:
        # --configurar el grid
        tbl = db.examen_aula_estudiante
        query = ((db.examen_aula_estudiante.examen_id == C.examen.id) & 
            (db.estudiante.id == db.examen_aula_estudiante.estudiante_id) & 
            (db.persona.id == db.estudiante.persona_id) & 
            (db.candidatura.estudiante_id == \
                db.examen_aula_estudiante.estudiante_id))
        
        # -- conf de los campos
        for fd in db.persona:
            fd.readable = False
        db.persona.nombre_completo.readable = True
        db.persona.numero_identidad.readable = True
        db.persona.numero_identidad.label = T("#IDENT")
        for fd in tbl:
            fd.readable = False
        tbl.aula_id.readable = True
        for fd in db.estudiante:
            fd.readable = False
        for f in db.candidatura:
            f.readable = False
        db.persona.nombre_completo.label = T('Nombre')
        campos=[db.persona.numero_identidad,
                db.persona.nombre_completo,
                tbl.aula_id]
        
        text_lengths={'persona.nombre_completo': 50,
                      'persona.numero_identidad': 15}
        exportadores = dict(xml=False, html=False, csv_with_hidden_cols=False,
                            csv=False, tsv_with_hidden_cols=False, tsv=False,
                            json=False, PDF=(tools.ExporterPDF, 'PDF'),
#                             XLS=(candidatura.EAEXLS, 'XLS')
                           )
        
        if request.vars._export_type:
            if C.examen.fecha is None or C.examen.inicio is None or C.examen.fin is None:
                myvars = Storage(request.vars)
                del myvars["_export_type"]
                session.flash = T('No se han definido los parámetros del exámen')
                redirect(URL('distribucion', vars=myvars, args=[C.examen.id]))
            response.context = C
        
        C.grid = grid_simple(query,
                             orderby=[db.persona.nombre_completo],
                             create=False,
                             maxtextlengths=text_lengths,
                             fields=campos,
                             csv=True,
                             history=False,
                             exportclasses=exportadores,
                             searchable=True,
                             args=request.args[:1])
    else:
        # --poner un mensaje
        msg_t = T("¡Avizo!")
        msg = T('''
        No se han asignado aulas a este examen, las asignadas no son 
        suficiente o no se realizó la distrubución.
        ''')
        msg = CAT(P(msg),P(Accion(T('Configuración de aulas'),
                                  URL('index', args=[request.args(0)]),
                                  True,
                                  _class="btn btn-default alert-link")),
                  P(C.distribuir_link))
        C.grid = DIV(H4(msg_t), msg,_class="alert alert-danger",
                     _role="alert")
    
    return dict(C=C)
