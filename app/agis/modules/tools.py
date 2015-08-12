#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import cStringIO
import xlsxwriter
from gluon import *
from gluon.sqlhtml import ExportClass
from gluon.contrib.fpdf import FPDF, HTMLMixin

class MyFPDF(FPDF, HTMLMixin):

    def add_font(self, name, style, path):
        path = self.font_map(path)
        super(MyFPDF, self).add_font(name, style, path, uni=True)

    def font_map(self, path):
        request = current.request
        if path.startswith('/%s/static/' % request.application):
            return os.path.join(request.folder, path.split('/', 2)[2])
        return 'http%s://%s%s' % (request.is_https and 's' or '', request.env.http_host, path)

class CustomExporter(ExportClass):
    label = ''
    file_ext = ''
    content_type = ''
    file_name = ''

    def __init__(self, rows):
        super(CustomExporter, self).__init__(rows)
        request = current.request
        request.vars._export_filename = self.file_name or request.function

class ExporterXLS(CustomExporter):
    label = 'XLS'
    file_ext = "xls"
    content_type = "application/xls"
    file_name = ""

    def __init__(self, rows):
        super(ExporterXLS, self).__init__(rows)
        self.output = cStringIO.StringIO()
        self.workbook = xlsxwriter.Workbook(self.output, {'in_memory': True})
        request = current.request
        response = current.response
        request.vars._export_filename = self.file_name or request.function

class ExporterPDF(CustomExporter):
    label = 'PDF'
    file_ext = "pdf"
    content_type = "application/pdf"

    def __init__(self, rows):
        super(ExporterPDF, self).__init__(rows)

    def export(self):
        request = current.request
        response = current.response
        pdf = MyFPDF()
        pdf.add_page()
        pdf.add_font('dejavu','', '/agis/static/fonts/DejaVuSansCondensed.ttf')
        pdf.add_font('dejavu','B', '/agis/static/fonts/DejaVuSansCondensed-Bold.ttf')
        pdf.set_font('dejavu', '', 12)
        filename = '%s/%s.pdf' % (request.controller,request.function)
        if os.path.exists(os.path.join(request.folder,'views',filename)):
            html=response.render(filename, dict(rows=self.rows))
        else:
            html=BODY(BEAUTIFY(response._vars)).xml()
        pass
        pdf.write_html(html)
        return XML(pdf.output(dest='S'))

def inicializar_administrador():
    db = current.db
    auth = current.auth
    admin_rol = db.auth_group.insert(role='administrators')
    admin_user = db.auth_user.insert(
        email="admin@example.com",
        password=db.auth_user.password.validate('admin')[0],
    )
    db.auth_membership.insert(group_id=admin_rol,user_id=admin_user)
    db.commit()
    auth.login_bare('admin@example.com','admin')

def probar_base_de_datos():
    """Retorna True si la base de datos ya esta inicializada"""
    db = current.db
    if db(db.auth_user.id > 0).count() > 0:
        return True
    # en cc retornar Falso
    return False

def selector(consulta, campos, nombre_modelo, vars={}):
    """Define un GRID que puede ser utilizado para seleccionar uno de sus elementos
    que es entonces pasado como parametro en el query string a el cotrolador/funcion especificado.

    consulta: query a ejecutar
    campos: campos a mostrar en el grid
    nombre_modelo: nombre a utilizar para generar el parametro ID del enlace de selección
    vars: parametros adicionales.
    """
    def enlaces(fila):
        response = current.response
        request = current.request
        T = current.T
        vars = response.context
        vars[response.nombre_modelo] = fila.id
        return A(I('', _class='icon-chevron-right'), _class="btn", _title=T("Seleccionar"),
                 _href=URL(c=request.controller,f=request.function,
                           vars=vars))
    response = current.response
    response['context'] = vars
    response['nombre_modelo'] = nombre_modelo
    enlaces = [dict(header='',body=enlaces)]
    return manejo_simple(consulta, enlaces=enlaces,
                         campos=campos, crear=False,
                         borrar=False, editable=False,
                         buscar=True,)

def manejo_simple(conjunto,
        orden=[],longitud_texto=100,editable=True,enlaces=[],buscar=False,
        campos=None,crear=True,borrar=True, csv=False, exportadores={},
        ):
    manejo = SQLFORM.grid(query=conjunto,
        details=False,
        csv=csv,
        fields=campos,
        searchable=buscar,
        create=crear,
        deletable=borrar,
        editable=editable,
        showbuttontext=False,
        links=enlaces,
        exportclasses=exportadores,
        maxtextlength=longitud_texto,
        orderby=orden,
        formstyle='bootstrap',
    )
    return manejo

def inicializar_base_datos():
    db = current.db
    request = current.request
    # academic regions
    db.region_academica.import_from_csv_file(
        open(os.path.join(request.folder,'db_region_academica.csv'), 'r')
    )
    db.provincia.import_from_csv_file(
        open(os.path.join(request.folder,'db_provincia.csv'), 'r')
    )
    region = db.region_academica[1]
    escuela = db.escuela.insert(nombre='ESCUELA (DEFECTO)',
        region_academica_id=region.id,
        clasificacion='10',
        naturaleza='1',
        codigo_registro='000',
        codigo='07101000'
    )
    tmp_prov = db.provincia[1]
    unidad_organica_id = db.unidad_organica.insert(nombre='SEDE CENTRAL (DEFECTO)',
        provincia_id=tmp_prov.id,
        nivel_agregacion='0',
        clasificacion='20',
        codigo_registro='000',
        codigo_escuela='00',
        escuela_id=escuela
    )
    db.descripcion_carrera.import_from_csv_file(
        open(os.path.join(request.folder,'careers_des.csv'), 'r')
    )
    # municipios
    db.municipio.import_from_csv_file(
        open(os.path.join(request.folder,'db_municipality.csv'), 'r')
    )
    # comunas
    db.comuna.import_from_csv_file(
        open(os.path.join(request.folder,'db_commune.csv'), 'r')
    )
    # regímenes
    db.regimen.import_from_csv_file(
        open(os.path.join(request.folder,'db_regime.csv'), 'r')
    )
    # tipos de enseñanza media
    db.tipo_escuela_media.import_from_csv_file(
        open(os.path.join(request.folder,'db_middle_school_type.csv'), 'r')
    )
    db.tipo_documento_identidad.bulk_insert([
       {'nombre': 'BILHETE DE IDENTIDADE'},
       {'nombre': 'PASAPORTE'},
    ])
    # tipos de discapacidad
    db.discapacidad.import_from_csv_file(
       open(os.path.join(request.folder,'db_special_education.csv'), 'r')
    )
    db.commit()
    from applications.agis.modules.db import ano_academico
    nombre = ano_academico.ano_actual()
    db.ano_academico.insert(nombre=nombre,unidad_organica_id=unidad_organica_id)
    db.commit()

requerido = [IS_NOT_EMPTY(error_message=current.T('Información requerida'))]
