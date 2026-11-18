import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Encuesta de Pertinencia — Fonoaudiología",
    page_icon="📋",
    layout="centered"
)

# ============================================================
# CONEXIÓN Y GUARDADO CON ST-GSHEETS-CONNECTION
# ============================================================
def guardar_respuesta(poblacion, datos):
    """Guarda una fila usando la conexión nativa de Streamlit para Google Sheets"""
    try:
        # 1. Conectar a Google Sheets usando los secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 2. Leer los datos existentes de la hoja (ttl=0 fuerza a leer datos frescos)
        df_existente = conn.read(worksheet=poblacion, ttl=0)
        
        # 3. Crear el diccionario con la nueva fila
        nueva_fila = {"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Poblacion": poblacion}
        nueva_fila.update(datos)
        
        # 4. Agregar la nueva fila al DataFrame existente
        df_nuevo = pd.concat([df_existente, pd.DataFrame([nueva_fila])], ignore_index=True)
        
        # 5. Actualizar (sobrescribir) la hoja con el nuevo DataFrame
        conn.update(worksheet=poblacion, data=df_nuevo)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# ============================================================
# ESTADO DE SESIÓN
# ============================================================
if "poblacion" not in st.session_state:
    st.session_state.poblacion = None
if "enviado" not in st.session_state:
    st.session_state.enviado = False

# ============================================================
# UTILIDAD DE VALIDACIÓN
# ============================================================
def validar_campos(obligatorios, nombre_formulario):
    faltantes = [campo for campo, valor in obligatorios.items() if valor is None or valor == "" or valor == []]
    if faltantes:
        st.error(f"⚠️ Faltan campos obligatorios en {nombre_formulario}: {', '.join(faltantes)}")
        return False
    return True

# ============================================================
# PANTALLA DE INICIO / FILTRO
# ============================================================
def pantalla_inicio():
    st.title("📋 Encuesta de Pertinencia — Fonoaudiología")
    st.markdown("""
    Esta encuesta busca recoger información para la **renovación del registro calificado**
    del programa de Fonoaudiología. Sus respuestas son confidenciales y se usarán
    únicamente con fines académicos.

    **Tiempo estimado:** 5–8 minutos.
    """)
    st.divider()
    poblacion = st.radio(
        "**Seleccione su perfil:**",
        ["Aspirante (estudiante de 10° u 11°)", "Sector externo (empleador/institución)", "Egresado"],
        index=None,
        key="filtro_inicio"
    )
    if poblacion:
        if st.button("Comenzar encuesta", type="primary", use_container_width=True):
            if poblacion.startswith("Aspirante"):
                st.session_state.poblacion = "Aspirantes"
            elif poblacion.startswith("Sector"):
                st.session_state.poblacion = "Sector_Externo"
            else:
                st.session_state.poblacion = "Egresados"
            st.rerun()

# ============================================================
# INSTRUMENTO A — ASPIRANTES
# ============================================================
def encuesta_aspirantes():
    st.title("📋 Encuesta para Aspirantes")
    st.caption("Estudiantes de 10° y 11°")

    with st.form("form_aspirantes"):
        st.subheader("Módulo 0. Identificación")
        codigo = st.text_input("Código anónimo (asignado por el encuestador) *", key="a_codigo")
        grado = st.selectbox("Grado que cursa *", ["10°", "11°"], index=None, key="a_grado")
        municipio = st.text_input("Municipio/Departamento *", key="a_municipio")
        tipo_inst = st.selectbox("Tipo de institución *", ["Pública", "Privada"], index=None, key="a_tipo")

        st.divider()
        st.subheader("Módulo 1. Conocimiento del programa")
        conoce = st.radio(
            "¿Conocía la carrera de Fonoaudiología antes de esta encuesta? *",
            ["Sí, sé qué hace un fonoaudiólogo", "Solo he oído el nombre", "No la conocía"],
            index=None, key="a_conoce"
        )
        entiende = st.slider("¿Qué tanto entiende qué hace un fonoaudiólogo? (1=Nada, 5=Mucho) *", 1, 5, 3, key="a_entiende")
        info_clara = st.slider("¿La información recibida sobre el programa es clara y suficiente? (1–5) *", 1, 5, 3, key="a_info")

        st.divider()
        st.subheader("Módulo 2. Atractivo vocacional")
        atractivo = st.slider("¿Qué tanto le atrae trabajar evaluando e interviniendo problemas de audición, habla, lenguaje o voz? (1–5) *", 1, 5, 3, key="a_atractivo")
        aspectos = st.multiselect(
            "¿Qué aspectos le resultan más atractivos? *",
            ["Ayudar a personas con dificultades de comunicación", "Trabajar en salud o educación",
             "Posibilidad de trabajo en diferentes entornos", "Salario y estabilidad laboral"],
            key="a_aspectos"
        )
        aspecto_otro = st.text_input("Otro aspecto (opcional)", key="a_aspecto_otro")
        dudas = st.multiselect(
            "¿Qué le haría dudar de estudiar Fonoaudiología? *",
            ["Costo de la matrícula", "Desconocimiento de la profesión", "Ubicación de la universidad",
             "Duración del programa", "No veo campo laboral claro"],
            key="a_dudas"
        )
        duda_otra = st.text_input("Otra duda (opcional)", key="a_duda_otra")

        st.divider()
        st.subheader("Módulo 3. Valor del semestre y expectativa salarial")
        st.info("El valor promedio de un semestre de Fonoaudiología en Colombia ronda los **$5.500.000**.")
        influencia_costo = st.radio(
            "¿Qué tanto influye este valor en su decisión de estudiar la carrera? *",
            ["Mucho (factor decisivo)", "Algo (lo considero)", "Poco", "No lo sé"],
            index=None, key="a_costo"
        )
        st.caption("Salario mínimo actual: $1.750.000")
        expectativa_salario = st.radio(
            "¿Cuánto cree que gana al mes un fonoaudiólogo recién graduado? *",
            ["Menos de $1.750.000", "Entre $1.750.000 y $2.300.000",
             "Entre $2.300.001 y $3.000.000", "Más de $3.000.000", "No tengo idea"],
            index=None, key="a_salario"
        )

        st.divider()
        st.subheader("Módulo 4. Pertinencia regional")
        necesidad = st.radio(
            "¿Considera que en su región se necesitan profesionales que atiendan trastornos de la comunicación? *",
            ["Sí", "No", "No sabe"], index=None, key="a_necesidad"
        )
        instituciones = st.radio(
            "¿Conoce instituciones en su región donde podría trabajar un fonoaudiólogo? *",
            ["Sí, conozco varias", "Conozco pocas", "No conozco"], index=None, key="a_instituciones"
        )

        st.divider()
        st.subheader("Módulo 5. Pregunta abierta")
        comentario = st.text_area("¿Qué información adicional le gustaría recibir sobre la carrera?", key="a_comentario")

        enviado = st.form_submit_button("Enviar encuesta", type="primary", use_container_width=True)

        if enviado:
            obligatorios = {
                "código": codigo, "grado": grado, "municipio": municipio, "tipo de institución": tipo_inst,
                "conoce carrera": conoce, "aspectos atractivos": aspectos, "dudas": dudas,
                "influencia costo": influencia_costo, "expectativa salario": expectativa_salario,
                "necesidad regional": necesidad, "conoce instituciones": instituciones
            }
            if validar_campos(obligatorios, "Aspirantes"):
                datos = {
                    "codigo": codigo, "grado": grado, "municipio": municipio, "tipo_institucion": tipo_inst,
                    "conoce_carrera": conoce, "entiende_rol": entiende, "info_clara": info_clara,
                    "atractivo_vocacional": atractivo,
                    "aspectos_atractivos": ", ".join(aspectos + ([aspecto_otro] if aspecto_otro else [])),
                    "dudas": ", ".join(dudas + ([duda_otra] if duda_otra else [])),
                    "influencia_costo": influencia_costo, "expectativa_salario": expectativa_salario,
                    "necesidad_regional": necesidad, "conoce_instituciones": instituciones,
                    "comentario": comentario
                }
                if guardar_respuesta("Aspirantes", datos):
                    st.success("✅ Respuesta enviada correctamente. ¡Gracias!")
                    st.session_state.enviado = True
                    st.rerun()

# ============================================================
# INSTRUMENTO B — SECTOR EXTERNO
# ============================================================
def encuesta_sector_externo():
    st.title("📋 Encuesta para Sector Externo")
    st.caption("Empleadores / Instituciones de práctica")

    with st.form("form_externo"):
        st.subheader("Módulo 0. Identificación")
        codigo = st.text_input("Código anónimo *", key="b_codigo")
        tipo_inst = st.selectbox(
            "Tipo de institución *",
            ["IPS / Clínica / Hospital", "Institución educativa", "Empresa / ARL", "Consultorio independiente", "Otro"],
            index=None, key="b_tipo"
        )
        municipio = st.text_input("Municipio/Departamento *", key="b_municipio")
        cargo = st.text_input("Cargo de quien responde *", key="b_cargo")

        st.divider()
        st.subheader("Módulo 1. Vinculación con el programa")
        practicas = st.radio(
            "¿Ha tenido estudiantes de Fonoaudiología en práctica formativa? *",
            ["Sí, actualmente", "Sí, en el pasado", "No"], index=None, key="b_practicas"
        )
        contratado = st.radio(
            "¿Ha contratado egresados del programa? *",
            ["Sí, actualmente", "Sí, en el pasado", "No"], index=None, key="b_contratado"
        )

        st.divider()
        st.subheader("Módulo 2. Evaluación de competencias")
        st.caption("Seleccione 'No aplica' si no ha observado esa competencia en egresados del programa.")
        opciones_comp = ["No aplica", "1 - Muy deficiente", "2", "3", "4", "5 - Excelente"]
        audicion = st.selectbox("Evaluación e intervención en audición *", opciones_comp, index=None, key="b_audicion")
        lenguaje = st.selectbox("Evaluación e intervención en lenguaje *", opciones_comp, index=None, key="b_lenguaje")
        habla = st.selectbox("Evaluación e intervención en habla *", opciones_comp, index=None, key="b_habla")
        voz = st.selectbox("Evaluación e intervención en voz *", opciones_comp, index=None, key="b_voz")
        deglucion = st.selectbox("Evaluación e intervención en deglución *", opciones_comp, index=None, key="b_deglucion")
        interdisciplinario = st.selectbox("Trabajo interdisciplinario *", opciones_comp, index=None, key="b_inter")
        comunicacion = st.selectbox("Comunicación con usuarios y familias *", opciones_comp, index=None, key="b_comunicacion")

        st.divider()
        st.subheader("Módulo 3. Salario y relación con la formación")
        st.caption("Salario mínimo actual: $1.750.000")
        rango_salarial = st.radio(
            "¿Cuál es el rango salarial mensual que ofrece su institución a un fonoaudiólogo recién egresado? *",
            ["$1.750.000 o menos", "$1.750.001 – $2.300.000", "$2.300.001 – $2.900.000",
             "$2.900.001 – $3.500.000", "Más de $3.500.000", "No aplica"],
            index=None, key="b_rango"
        )
        st.info("El semestre de Fonoaudiología cuesta en promedio **$5.500.000**.")
        proporcion = st.radio(
            "¿Considera que el salario del mercado es proporcional a la inversión y competencias de los egresados? *",
            ["Sí, es proporcional", "No, el salario es bajo frente a la inversión",
             "No, el salario es alto para el nivel observado", "No sabe"],
            index=None, key="b_proporcion"
        )

        st.divider()
        st.subheader("Módulo 4. Brechas formativas")
        brechas = st.multiselect(
            "¿Qué área debería reforzar el programa? *",
            ["Tecnología audiológica avanzada", "Atención temprana", "Población adulta mayor",
             "Investigación", "Gestión y administración en salud", "Habilidades blandas"],
            key="b_brechas"
        )
        brecha_otra = st.text_input("Otra área (opcional)", key="b_brecha_otra")

        st.divider()
        st.subheader("Módulo 5. Relación docencia-servicio")
        canal = st.radio(
            "¿Existe un canal formal de comunicación con el programa para retroalimentar prácticas? *",
            ["Sí, permanente", "Sí, ocasional", "No existe", "No sabe"], index=None, key="b_canal"
        )
        dispuesto = st.radio(
            "¿Estaría dispuesto/a a participar en mesas técnicas o comités curriculares? *",
            ["Sí", "No", "Tal vez"], index=None, key="b_dispuesto"
        )

        st.divider()
        st.subheader("Módulo 6. Pregunta abierta")
        recomendacion = st.text_area("¿Qué recomendación haría al programa?", key="b_recomendacion")

        enviado = st.form_submit_button("Enviar encuesta", type="primary", use_container_width=True)

        if enviado:
            obligatorios = {
                "código": codigo, "tipo de institución": tipo_inst, "municipio": municipio, "cargo": cargo,
                "prácticas": practicas, "contratado": contratado, "audición": audicion, "lenguaje": lenguaje,
                "habla": habla, "voz": voz, "deglución": deglucion, "interdisciplinario": interdisciplinario,
                "comunicación": comunicacion, "rango salarial": rango_salarial, "proporcionalidad": proporcion,
                "brechas": brechas, "canal": canal, "dispuesto": dispuesto
            }
            if validar_campos(obligatorios, "Sector Externo"):
                datos = {
                    "codigo": codigo, "tipo_institucion": tipo_inst, "municipio": municipio, "cargo": cargo,
                    "practicas": practicas, "contratado": contratado, "audicion": audicion,
                    "lenguaje": lenguaje, "habla": habla, "voz": voz, "deglucion": deglucion,
                    "interdisciplinario": interdisciplinario, "comunicacion": comunicacion,
                    "rango_salarial": rango_salarial, "proporcionalidad": proporcion,
                    "brechas": ", ".join(brechas + ([brecha_otra] if brecha_otra else [])),
                    "canal_comunicacion": canal, "dispuesto_comite": dispuesto, "recomendacion": recomendacion
                }
                if guardar_respuesta("Sector_Externo", datos):
                    st.success("✅ Respuesta enviada correctamente. ¡Gracias!")
                    st.session_state.enviado = True
                    st.rerun()

# ============================================================
# INSTRUMENTO C — EGRESADOS
# ============================================================
def encuesta_egresados():
    st.title("📋 Encuesta para Egresados")

    with st.form("form_egresados"):
        st.subheader("Módulo 0. Identificación")
        codigo = st.text_input("Código anónimo *", key="c_codigo")
        anio = st.text_input("Año de grado *", key="c_anio")
        municipio = st.text_input("Municipio/Departamento de residencia *", key="c_municipio")

        st.divider()
        st.subheader("Módulo 1. Situación laboral")
        area = st.radio(
            "¿Se desempeña actualmente en un área propia de la Fonoaudiología? *",
            ["Sí, área clínica/asistencial", "Sí, área educativa", "Sí, área administrativa/gestión",
             "Sí, área de investigación/docencia", "Sí, en otra área relacionada",
             "No, trabajo en algo no relacionado", "No estoy empleado/a"],
            index=None, key="c_area"
        )
        tiempo_empleo = st.radio(
            "¿Cuánto tardó en conseguir su primer empleo relacionado con la carrera? *",
            ["Menos de 6 meses", "Entre 6 y 12 meses", "Más de 12 meses", "Aún no he tenido empleo en el área"],
            index=None, key="c_tiempo"
        )
        vinculacion = st.radio(
            "Tipo de vinculación actual *",
            ["Término indefinido", "Término fijo", "Prestación de servicios", "Independiente", "No aplica"],
            index=None, key="c_vinculacion"
        )

        st.divider()
        st.subheader("Módulo 2. Salario y retorno de la inversión")
        st.caption("Salario mínimo actual: $1.750.000")
        salario_actual = st.radio(
            "¿En qué rango se encuentra su salario mensual actual? *",
            ["Menos de $1.750.000", "$1.750.000 – $2.300.000", "$2.300.001 – $2.900.000",
             "$2.900.001 – $3.500.000", "Más de $3.500.000", "No aplica"],
            index=None, key="c_salario"
        )
        st.info("El semestre cuesta en promedio **$5.500.000** (~$44.000.000 por 8 semestres).")
        retorno = st.radio(
            "¿Considera que la inversión ha valido la pena frente a sus ingresos actuales? *",
            ["Sí, totalmente", "Parcialmente", "No, el retorno ha sido bajo", "No lo sé"],
            index=None, key="c_retorno"
        )
        satisfaccion = st.radio(
            "¿Qué tan satisfecho está con su remuneración actual? *",
            ["Muy satisfecho", "Satisfecho", "Neutral", "Insatisfecho", "Muy insatisfecho"],
            index=None, key="c_satisfaccion"
        )

        st.divider()
        st.subheader("Módulo 3. Competencias adquiridas (1=Nada, 5=Completamente)")
        audiologia = st.slider("Realizar evaluaciones audiológicas básicas de forma autónoma *", 1, 5, 3, key="c_audiologia")
        lenguaje_inf = st.slider("Diseñar y ejecutar planes de intervención en lenguaje infantil *", 1, 5, 3, key="c_lenguaje")
        voz_adulto = st.slider("Manejar trastornos de la voz en población adulta *", 1, 5, 3, key="c_voz")
        deglucion_comp = st.slider("Evaluar y tratar trastornos de la deglución *", 1, 5, 3, key="c_deglucion")
        interdisc = st.slider("Trabajar en equipos interdisciplinarios *", 1, 5, 3, key="c_interdisc")
        evidencia = st.slider("Aplicar evidencia científica en la toma de decisiones clínicas *", 1, 5, 3, key="c_evidencia")

        st.divider()
        st.subheader("Módulo 4. Brechas formativas")
        brechas = st.multiselect(
            "¿Qué tema considera que faltó o fue insuficiente en su formación? *",
            ["Tecnología audiológica avanzada", "Atención temprana", "Rehabilitación vocal",
             "Deglución / disfagia", "Investigación", "Gestión y emprendimiento",
             "Habilidades comunicativas con familias"],
            key="c_brechas"
        )
        brecha_otra = st.text_input("Otro tema (opcional)", key="c_brecha_otra")

        st.divider()
        st.subheader("Módulo 5. Pertinencia retroactiva")
        reelegiria = st.radio(
            "Si pudiera volver a elegir, ¿estudiaría Fonoaudiología en la misma institución? *",
            ["Sí", "No", "Tal vez"], index=None, key="c_reelegiria"
        )
        recomienda = st.radio(
            "¿Recomendaría el programa a un estudiante de colegio? *",
            ["Sí", "No", "Tal vez"], index=None, key="c_recomienda"
        )

        st.divider()
        st.subheader("Módulo 6. Pregunta abierta")
        sugerencia = st.text_area("¿Qué debería cambiar el programa para ser más pertinente?", key="c_sugerencia")

        enviado = st.form_submit_button("Enviar encuesta", type="primary", use_container_width=True)

        if enviado:
            obligatorios = {
                "código": codigo, "año": anio, "municipio": municipio, "área": area,
                "tiempo empleo": tiempo_empleo, "vinculación": vinculacion,
                "salario": salario_actual, "retorno": retorno, "satisfacción": satisfaccion,
                "brechas": brechas, "reelegiría": reelegiria, "recomienda": recomienda
            }
            if validar_campos(obligatorios, "Egresados"):
                datos = {
                    "codigo": codigo, "anio_grado": anio, "municipio": municipio,
                    "area_desempeno": area, "tiempo_primer_empleo": tiempo_empleo,
                    "vinculacion": vinculacion, "salario_actual": salario_actual,
                    "retorno_inversion": retorno, "satisfaccion_salarial": satisfaccion,
                    "competencia_audiologia": audiologia, "competencia_lenguaje": lenguaje_inf,
                    "competencia_voz": voz_adulto, "competencia_deglucion": deglucion_comp,
                    "competencia_interdisciplinario": interdisc, "competencia_evidencia": evidencia,
                    "brechas": ", ".join(brechas + ([brecha_otra] if brecha_otra else [])),
                    "reelegiria": reelegiria, "recomienda": recomienda, "sugerencia": sugerencia
                }
                if guardar_respuesta("Egresados", datos):
                    st.success("✅ Respuesta enviada correctamente. ¡Gracias!")
                    st.session_state.enviado = True
                    st.rerun()

# ============================================================
# ENRUTADOR PRINCIPAL
# ============================================================
if st.session_state.enviado:
    st.balloons()
    st.success("🎉 ¡Gracias por completar la encuesta!")
    if st.button("Volver al inicio"):
        st.session_state.poblacion = None
        st.session_state.enviado = False
        st.rerun()
elif st.session_state.poblacion == "Aspirantes":
    encuesta_aspirantes()
elif st.session_state.poblacion == "Sector_Externo":
    encuesta_sector_externo()
elif st.session_state.poblacion == "Egresados":
    encuesta_egresados()
else:
    pantalla_inicio()
