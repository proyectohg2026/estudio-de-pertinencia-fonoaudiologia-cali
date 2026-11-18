import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Encuesta de Pertinencia — Fonoaudiología",
    page_icon="📋",
    layout="centered"
)

# Archivos donde se guardarán los datos localmente en la app
ARCHIVO_EXCEL = "respuestas_encuesta.xlsx"

# ============================================================
# FUNCIÓN PARA GUARDAR EN EXCEL/CSV
# ============================================================
def guardar_respuesta(poblacion, datos):
    try:
        # Agregar fecha y hora
        datos["Fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos["Poblacion"] = poblacion
        
        # Convertir a DataFrame
        df_nuevo = pd.DataFrame([datos])
        
        # Si el archivo ya existe, leerlo y concatenar
        if os.path.exists(ARCHIVO_EXCEL):
            df_existente = pd.read_excel(ARCHIVO_EXCEL)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        # Guardar en Excel
        df_final.to_excel(ARCHIVO_EXCEL, index=False)
        
        # Guardar en la sesión para el botón de descarga
        st.session_state["respuestas_acumuladas"] = df_final
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
# BOTÓN DE DESCARGA (Para el administrador)
# ============================================================
def mostrar_boton_descarga():
    if "respuestas_acumuladas" in st.session_state:
        df = st.session_state["respuestas_acumuladas"]
        # Crear archivo en memoria para descarga
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        st.sidebar.download_button(
            label="⬇️ Descargar respuestas (Excel)",
            data=buffer.getvalue(),
            file_name="respuestas_fonoaudiologia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ============================================================
# PANTALLA DE INICIO / FILTRO
# ============================================================
def pantalla_inicio():
    mostrar_boton_descarga()
    st.title("📋 Encuesta de Pertinencia — Fonoaudiología")
    st.markdown("""
    Esta encuesta busca recoger información para la **renovación del registro calificado**
    del programa de Fonoaudiología. Sus respuestas son confidenciales.
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
    mostrar_boton_descarga()
    st.title("📋 Encuesta para Aspirantes")
    
    with st.form("form_aspirantes"):
        # ... (Aquí va exactamente el mismo formulario de aspirantes que ya tenías) ...
        codigo = st.text_input("Código anónimo *", key="a_codigo")
        grado = st.selectbox("Grado que cursa *", ["10°", "11°"], index=None, key="a_grado")
        municipio = st.text_input("Municipio/Departamento *", key="a_municipio")
        tipo_inst = st.selectbox("Tipo de institución *", ["Pública", "Privada"], index=None, key="a_tipo")
        
        st.divider()
        conoce = st.radio("¿Conocía la carrera? *", ["Sí", "Solo el nombre", "No"], index=None, key="a_conoce")
        entiende = st.slider("¿Entiende qué hace un fonoaudiólogo? *", 1, 5, 3, key="a_entiende")
        info_clara = st.slider("¿Información clara? *", 1, 5, 3, key="a_info")
        
        st.divider()
        atractivo = st.slider("¿Atractivo vocacional? *", 1, 5, 3, key="a_atractivo")
        aspectos = st.multiselect("¿Aspectos atractivos? *", ["Ayudar", "Salud/educación", "Diversidad", "Salario"], key="a_aspectos")
        dudas = st.multiselect("¿Qué le haría dudar? *", ["Costo", "Desconocimiento", "Ubicación", "Duración"], key="a_dudas")
        
        st.divider()
        st.info("Semestre promedio: **$5.500.000**.")
        influencia_costo = st.radio("¿Influye el costo? *", ["Mucho", "Algo", "Poco", "No lo sé"], index=None, key="a_costo")
        st.caption("Salario mínimo: $1.750.000")
        expectativa_salario = st.radio("¿Salario de recién graduado? *", ["< $1.75M", "$1.75M-$2.3M", ">$2.3M", "No sé"], index=None, key="a_salario")
        
        st.divider()
        necesidad = st.radio("¿Se necesitan profesionales en su región? *", ["Sí", "No", "No sabe"], index=None, key="a_necesidad")
        instituciones = st.radio("¿Conoce instituciones? *", ["Varias", "Pocas", "Ninguna"], index=None, key="a_instituciones")
        
        comentario = st.text_area("¿Qué información adicional le gustaría recibir?")
        
        enviado = st.form_submit_button("Enviar encuesta", type="primary", use_container_width=True)

        if enviado:
            obligatorios = {"código": codigo, "grado": grado, "municipio": municipio, "tipo": tipo_inst, "conoce": conoce, "aspectos": aspectos, "dudas": dudas, "costo": influencia_costo, "salario": expectativa_salario, "necesidad": necesidad, "instituciones": instituciones}
            if validar_campos(obligatorios, "Aspirantes"):
                datos = {"codigo": codigo, "grado": grado, "municipio": municipio, "tipo_institucion": tipo_inst, "conoce_carrera": conoce, "entiende_rol": entiende, "info_clara": info_clara, "atractivo_vocacional": atractivo, "aspectos_atractivos": ", ".join(aspectos), "dudas": ", ".join(dudas), "influencia_costo": influencia_costo, "expectativa_salario": expectativa_salario, "necesidad_regional": necesidad, "conoce_instituciones": instituciones, "comentario": comentario}
                if guardar_respuesta("Aspirantes", datos):
                    st.success("✅ Respuesta guardada. ¡Gracias!")
                    st.session_state.enviado = True
                    st.rerun()

# ============================================================
# INSTRUMENTO B — SECTOR EXTERNO
# ============================================================
def encuesta_sector_externo():
    mostrar_boton_descarga()
    st.title("📋 Encuesta para Sector Externo")
    
    with st.form("form_externo"):
        # ... (Aquí va exactamente el mismo formulario del sector externo que ya tenías) ...
        codigo = st.text_input("Código anónimo *", key="b_codigo")
        tipo_inst = st.selectbox("Tipo de institución *", ["IPS/Clínica", "Educativa", "Empresa", "Otro"], index=None, key="b_tipo")
        municipio = st.text_input("Municipio *", key="b_municipio")
        cargo = st.text_input("Cargo *", key="b_cargo")
        
        st.divider()
        practicas = st.radio("¿Ha tenido practicantes? *", ["Sí, actual", "Sí, pasado", "No"], index=None, key="b_practicas")
        contratado = st.radio("¿Ha contratado egresados? *", ["Sí, actual", "Sí, pasado", "No"], index=None, key="b_contratado")
        
        st.divider()
        st.caption("Califique de 1 a 5 (o No aplica)")
        opciones_comp = ["No aplica", "1", "2", "3", "4", "5"]
        audicion = st.selectbox("Audición *", opciones_comp, index=None, key="b_audicion")
        lenguaje = st.selectbox("Lenguaje *", opciones_comp, index=None, key="b_lenguaje")
        habla = st.selectbox("Habla *", opciones_comp, index=None, key="b_habla")
        voz = st.selectbox("Voz *", opciones_comp, index=None, key="b_voz")
        deglucion = st.selectbox("Deglución *", opciones_comp, index=None, key="b_deglucion")
        
        st.divider()
        rango_salarial = st.radio("Rango salarial ofrecido *", ["<= $1.75M", "$1.75M-$2.3M", ">$2.3M", "No aplica"], index=None, key="b_rango")
        proporcion = st.radio("¿Salario proporcional a inversión? *", ["Sí", "No, es bajo", "No, es alto", "No sabe"], index=None, key="b_proporcion")
        
        st.divider()
        brechas = st.multiselect("¿Qué reforzar? *", ["Tecnología", "Atención temprana", "Adulto mayor", "Investigación", "Gestión"], key="b_brechas")
        canal = st.radio("¿Canal formal de comunicación? *", ["Sí, permanente", "Sí, ocasional", "No existe"], index=None, key="b_canal")
        
        recomendacion = st.text_area("Recomendaciones para el programa:")
        
        enviado = st.form_submit_button("Enviar encuesta", type="primary", use_container_width=True)

        if enviado:
            obligatorios = {"código": codigo, "tipo": tipo_inst, "municipio": municipio, "cargo": cargo, "practicas": practicas, "contratado": contratado, "audicion": audicion, "lenguaje": lenguaje, "habla": habla, "voz": voz, "deglucion": deglucion, "rango": rango_salarial, "proporcion": proporcion, "brechas": brechas, "canal": canal}
            if validar_campos(obligatorios, "Sector Externo"):
                datos = {"codigo": codigo, "tipo_institucion": tipo_inst, "municipio": municipio, "cargo": cargo, "practicas": practicas, "contratado": contratado, "audicion": audicion, "lenguaje": lenguaje, "habla": habla, "voz": voz, "deglucion": deglucion, "rango_salarial": rango_salarial, "proporcionalidad": proporcion, "brechas": ", ".join(brechas), "canal_comunicacion": canal, "recomendacion": recomendacion}
                if guardar_respuesta("Sector_Externo", datos):
                    st.success("✅ Respuesta guardada. ¡Gracias!")
                    st.session_state.enviado = True
                    st.rerun()

# ============================================================
# INSTRUMENTO C — EGRESADOS
# ============================================================
def encuesta_egresados():
    mostrar_boton_descarga()
    st.title("📋 Encuesta para Egresados")
    
    with st.form("form_egresados"):
        # ... (Aquí va exactamente el mismo formulario de egresados que ya tenías) ...
        codigo = st.text_input("Código anónimo *", key="c_codigo")
        anio = st.text_input("Año de grado *", key="c_anio")
        municipio = st.text_input("Municipio *", key="c_municipio")
        
        st.divider()
        area = st.radio("¿Área de desempeño? *", ["Clínica", "Educativa", "Administrativa", "Otra", "No empleado"], index=None, key="c_area")
        tiempo_empleo = st.radio("¿Tiempo para primer empleo? *", ["< 6 meses", "6-12 meses", "> 12 meses", "Aún no"], index=None, key="c_tiempo")
        vinculacion = st.radio("Tipo de vinculación *", ["Indefinido", "Fijo", "Prestación", "Independiente"], index=None, key="c_vinculacion")
        
        st.divider()
        salario_actual = st.radio("Salario actual *", ["<= $1.75M", "$1.75M-$2.3M", ">$2.3M"], index=None, key="c_salario")
        retorno = st.radio("¿La inversión valió la pena? *", ["Sí", "Parcialmente", "No", "No sé"], index=None, key="c_retorno")
        satisfaccion = st.radio("Satisfacción salarial *", ["Muy satisfecho", "Satisfecho", "Neutral", "Insatisfecho"], index=None, key="c_satisfaccion")
        
        st.divider()
        audiologia = st.slider("Evaluaciones audiológicas *", 1, 5, 3, key="c_audiologia")
        lenguaje_inf = st.slider("Intervención lenguaje infantil *", 1, 5, 3, key="c_lenguaje")
        voz_adulto = st.slider("Trastornos de la voz *", 1, 5, 3, key="c_voz")
        deglucion_comp = st.slider("Trastornos de deglución *", 1, 5, 3, key="c_deglucion")
        
        st.divider()
        brechas = st.multiselect("¿Qué faltó en su formación? *", ["Tecnología", "Atención temprana", "Disfagia", "Investigación", "Gestión"], key="c_brechas")
        reelegiria = st.radio("¿Estudiaría en la misma institución? *", ["Sí", "No", "Tal vez"], index=None, key="c_reelegiria")
        recomienda = st.radio("¿Recomendaría el programa? *", ["Sí", "No", "Tal vez"], index=None, key="c_recomienda")
        
        sugerencia = st.text_area("¿Qué debería cambiar el programa?")
        
        enviado = st.form_submit_button("Enviar encuesta", type="primary", use_container_width=True)

        if enviado:
            obligatorios = {"código": codigo, "anio": anio, "municipio": municipio, "area": area, "tiempo": tiempo_empleo, "vinculacion": vinculacion, "salario": salario_actual, "retorno": retorno, "satisfaccion": satisfaccion, "brechas": brechas, "reelegiria": reelegiria, "recomienda": recomienda}
            if validar_campos(obligatorios, "Egresados"):
                datos = {"codigo": codigo, "anio_grado": anio, "municipio": municipio, "area_desempeno": area, "tiempo_primer_empleo": tiempo_empleo, "vinculacion": vinculacion, "salario_actual": salario_actual, "retorno_inversion": retorno, "satisfaccion_salarial": satisfaccion, "competencia_audiologia": audiologia, "competencia_lenguaje": lenguaje_inf, "competencia_voz": voz_adulto, "competencia_deglucion": deglucion_comp, "brechas": ", ".join(brechas), "reelegiria": reelegiria, "recomienda": recomienda, "sugerencia": sugerencia}
                if guardar_respuesta("Egresados", datos):
                    st.success("✅ Respuesta guardada. ¡Gracias!")
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
