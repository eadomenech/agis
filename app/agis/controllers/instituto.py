# -*- coding: utf-8 -*-

from applications.agis.modules import tools
from applications.agis.modules.db import escuela
from applications.agis.modules.db import unidad_organica
from applications.agis.modules.db import regimen_uo
from applications.agis.modules.db import carrera_uo
from applications.agis.modules.db import ano_academico as a_academico
from applications.agis.modules.db import departamento as dpto
from applications.agis.modules.db import nivel_academico as nivel
from applications.agis.modules.db import asignatura
from applications.agis.modules.db import plan_curricular
from applications.agis.modules.db import plazas
from applications.agis.modules.db import evento

sidenav.append(
    [T('Escuela'), # Titulo del elemento
     URL('configurar_escuela'), # url para el enlace
     ['configurar_escuela'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Unidades organicas'), # Titulo del elemento
     URL('gestion_uo'), # url para el enlace
     ['gestion_uo'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Régimen a realizar en la UO'), # Titulo del elemento
     URL('asignar_regimen'), # url para el enlace
     ['asignar_regimen'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Carreras a impartir en las UO'), # Titulo del elemento
     URL('asignar_carrera'), # url para el enlace
     ['asignar_carrera'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Gestión de Años Académicos'), # Titulo del elemento
     URL('ano_academico'), # url para el enlace
     ['ano_academico'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Departamentos'), # Titulo del elemento
     URL('departamentos'), # url para el enlace
     ['departamentos'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Niveles Académicos'), # Titulo del elemento
     URL('nivel_academico'), # url para el enlace
     ['nivel_academico'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Asignaturas'), # Titulo del elemento
     URL('asignaturas'), # url para el enlace
     ['asignaturas'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Planes Curriculares'), # Titulo del elemento
     URL('planes_curriculares'), # url para el enlace
     ['planes_curriculares'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Plazas a otorgar'), # Titulo del elemento
     URL('plazas_estudiantes'), # url para el enlace
     ['plazas_estudiantes'],] # en funciones estará activo este item
)
sidenav.append(
    [T('Eventos'), # Titulo del elemento
     URL('eventos'), # url para el enlace
     ['eventos'],] # en funciones estará activo este item
)

def index():
    redirect(URL('configurar_escuela'))
    return dict(message="hello from instituto.py")

@auth.requires_membership('administrators')
def plazas_estudiantes():
    manejo = plazas.obtener_manejo()
    #TODO: mantener chequeado con los cambios
    response.view="instituto/nivel_academico.html"
    return dict( sidenav=sidenav,manejo=manejo )

@auth.requires_membership('administrators')
def nivel_academico():
    manejo = nivel.obtener_manejo()
    return dict( sidenav=sidenav,manejo=manejo )

@auth.requires_membership('administrators')
def ano_academico():
    manejo = a_academico.obtener_manejo()
    return dict( sidenav=sidenav,manejo=manejo )

@auth.requires_membership('administrators')
def asignaturas():
    manejo = asignatura.obtener_manejo()
    return dict( sidenav=sidenav,manejo=manejo )

@auth.requires_membership('administrators')
def planes_curriculares():
    manejo = plan_curricular.obtener_manejo()
    response.view = "instituto/asignaturas.html"
    return dict( sidenav=sidenav,manejo=manejo )

@auth.requires_membership('administrators')
def eventos():
    manejo = evento.obtener_manejo()
    response.view = "instituto/asignaturas.html"
    return dict( sidenav=sidenav,manejo=manejo )

@auth.requires_membership('administrators')
def departamentos():
    manejo = dpto.obtener_manejo()
    return dict( sidenav=sidenav,manejo=manejo )

@auth.requires_membership('administrators')
def configurar_escuela():
    """Presenta formulario con los datos de la escuela y su sede cetral"""
    instituto = escuela.obtener_escuela()
    db.escuela.id.readable = False
    db.escuela.id.writable = False

    form_escuela = SQLFORM( db.escuela,instituto,formstyle='bootstrap' )
    response.title = T("Configurar escuela")
    if form_escuela.process(dbio=False).accepted:
        form_escuela.vars.codigo=escuela.calcular_codigo_escuela( db.escuela._filter_fields( form_escuela.vars ) )
        db( db.escuela.id==instituto.id ).update( **db.escuela._filter_fields( form_escuela.vars ) )
        db.commit()
        unidad_organica.actualizar_codigos()
        session.flash = T( "Cambios guardados" )
        redirect('configurar_escuela')
    return dict(form_escuela=form_escuela,sidenav=sidenav)

@auth.requires_membership('administrators')
def asignar_carrera():
    """
    Permite asignarle carreras a las unidades organicas
    """
    esc = escuela.obtener_escuela()
    select_uo = unidad_organica.widget_selector(escuela_id=esc.id)
    if 'unidad_organica_id' in request.vars:
        unidad_organica_id = int(request.vars.unidad_organica_id)
    else:
        unidad_organica_id = escuela.obtener_sede_central().id
    db.carrera_uo.unidad_organica_id.default = unidad_organica_id
    db.carrera_uo.unidad_organica_id.writable = False
    db.carrera_uo.unidad_organica_id.readable = False
    db.carrera_uo.id.readable = False
    db.carrera_uo.id.writable = False
    query = ( db.carrera_uo.unidad_organica_id == unidad_organica_id )
    if 'new' in request.args:
        # preparar para agregar un nuevo elemento
        posibles_carreras = carrera_uo.obtener_posibles(unidad_organica_id)
        if posibles_carreras:
            db.carrera_uo.descripcion_id.requires = IS_IN_SET( posibles_carreras, zero=None )
        else:
            session.flash = T("Ya se han asociados todas las posibles carreras a la UO")
            redirect(URL('asignar_carrera',vars={'unidad_organica_id': unidad_organica_id}))
    manejo = tools.manejo_simple( query,editable=False )
    return dict( sidenav=sidenav, select_uo=select_uo, manejo=manejo )

@auth.requires_membership('administrators')
def asignar_regimen():
    esc = escuela.obtener_escuela()
    select_uo = unidad_organica.widget_selector(escuela_id=esc.id)
    if 'unidad_organica_id' in request.vars:
        unidad_organica_id = int(request.vars.unidad_organica_id)
    else:
        unidad_organica_id = escuela.obtener_sede_central().id
    db.regimen_unidad_organica.unidad_organica_id.default = unidad_organica_id
    db.regimen_unidad_organica.unidad_organica_id.writable = False
    db.regimen_unidad_organica.id.readable = False
    query = (db.regimen_unidad_organica.unidad_organica_id ==  unidad_organica_id)
    if 'new' in request.args:
        # preparar para agregar un nuevo elemento
        posibles_regimenes = regimen_uo.obtener_posibles_en_instituto(unidad_organica_id)
        if posibles_regimenes:
            db.regimen_unidad_organica.regimen_id.requires = IS_IN_SET( posibles_regimenes, zero=None )
        else:
            session.flash = T("Ya se han asociados todos los posibles regímenes a la UO")
            redirect(URL('asignar_regimen',vars={'unidad_organica_id': unidad_organica_id}))
    manejo = tools.manejo_simple(query,editable=False)
    return dict(sidenav=sidenav,manejo=manejo,select_uo=select_uo)

@auth.requires_membership('administrators')
def gestion_uo():
    """Vista para la gestión de las unidades organicas"""
    esc = escuela.obtener_escuela()
    manejo = unidad_organica.obtener_manejo(esc.id)
    return dict(manejo=manejo,sidenav=sidenav)
