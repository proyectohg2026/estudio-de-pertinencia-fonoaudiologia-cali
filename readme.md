# Encuesta de Pertinencia — Programa de Fonoaudiología

Aplicación en Streamlit para la aplicación de encuestas a aspirantes, sector externo y egresados, en el marco de la renovación del registro calificado del programa de Fonoaudiología.

## Poblaciones
- Aspirantes (estudiantes de 10° y 11°)
- Sector externo (empleadores / instituciones de práctica)
- Egresados

## Requisitos
- Python 3.10+
- Cuenta de servicio de Google Cloud con acceso a Google Sheets

## Configuración
1. Crear una hoja de cálculo en Google Sheets con tres pestañas: `Aspirantes`, `Sector_Externo`, `Egresados`.
2. Compartir la hoja con el correo de la cuenta de servicio (permiso de editor).
3. Configurar `secrets.toml` con las credenciales y el ID de la hoja.

## Ejecución local
```bash
pip install -r requirements.txt
streamlit run app.py
