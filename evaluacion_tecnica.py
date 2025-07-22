import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Evaluación Técnica Codelco", layout="wide")

# ---------- ENCABEZADO ---------- #
st.title("Formulario de Evaluación Técnica - Codelco")

# Información del evaluador
evaluador = st.text_input("Nombre del evaluador")
division = st.selectbox("División", ["Andina", "Chuquicamata", "El Teniente", "Radomiro Tomic", "Ministro Hales"])
tipo = st.selectbox("Tipo de ítem evaluado", ["Servicio", "Suministro"])

# ---------- EVALUACIÓN DE SERVICIOS ---------- #
if tipo == "Servicio":
    st.subheader("Evaluación técnica - Servicios")

    criterios = [
        ("1.1 Organización de la empresa", 0.02),
        ("1.2 Años de experiencia", 0.04),
        ("1.3 Certificaciones", 0.04),
        ("2.1 Programación de reparación y turnos", 0.06),
        ("2.2 Control de programación de actividades", 0.045),
        ("2.3 Procedimiento de reparación", 0.06),
        ("2.4 Estructura organizacional del servicio", 0.03),
        ("2.5 Plan de contingencia", 0.045),
        ("2.6 Sistema de aseguramiento de calidad y seguridad", 0.06),
        ("3.1 Equipamiento mínimo requerido", 0.09),
        ("3.2 Mantenimiento y disponibilidad de equipos", 0.06),
        ("3.3 Certificación de equipos y herramientas", 0.06),
        ("3.4 Layout del taller", 0.045),
        ("3.5 Capacidad instalada", 0.045),
        ("4.1 Admin. contrato - Nivel estudios", 0.0375),
        ("4.1 Admin. contrato - Experiencia", 0.0375),
        ("4.2 Calidad - Nivel estudios", 0.025),
        ("4.2 Calidad - Experiencia", 0.025),
        ("4.3 Prevención - Nivel estudios", 0.0125),
        ("4.3 Prevención - Experiencia", 0.0125),
        ("4.4 Jefe taller - Nivel estudios", 0.025),
        ("4.4 Jefe taller - Experiencia", 0.025),
        ("4.5 Técnico mecánico - Nivel estudios", 0.02),
        ("4.5 Técnico mecánico - Experiencia", 0.08),
        ("4.6 Soldador - Nivel estudios", 0.02),
        ("4.6 Soldador - Experiencia", 0.08),
        ("5. Propuesta de mejoras/innovación", 0.05)
    ]

    puntaje_total = 0
    suma_ponderaciones = sum(p for _, p in criterios)
    if abs(suma_ponderaciones - 1.0) > 0.001:
        st.warning(f"⚠️ Las ponderaciones no suman 1.0 (suma actual: {suma_ponderaciones:.3f})")

    for criterio, peso in criterios:
        valor = st.slider(criterio, 0, 100, 70, key=criterio)
        puntaje_total += valor * peso
        comentario = st.text_area(f"Comentario sobre {criterio}", key=f"comentario_{criterio}")

    st.metric("Puntaje ponderado total", round(puntaje_total, 2))

# ---------- EVALUACIÓN DE SUMINISTROS ---------- #
else:
    st.subheader("Evaluación técnica - Suministros")

    st.markdown("**Producto ofertado por segmento**")
    opciones_producto = ["No Aplica", "No Oferta", "No Cumple", "Cumple", "Cumple Prueba Industrial", "Cumple Back Up"]

    s1 = st.selectbox("Producto ofertado - Segmento S1", opciones_producto)
    s2 = st.selectbox("Producto ofertado - Segmento S2", opciones_producto)
    s3 = st.selectbox("Producto ofertado - Segmento S3", opciones_producto)

    st.markdown("**Aspectos diferenciadores**")
    a2 = st.slider("2. Plan Aseguramiento de Calidad (TEC-04)", 0, 100, 70)
    comentario_a2 = st.text_area("Comentario sobre Aseguramiento de Calidad", key="comentario_a2")
    a3 = st.slider("3. Asistencia Técnica Postventa (TEC-03)", 0, 100, 70)
    comentario_a3 = st.text_area("Comentario sobre Asistencia Técnica Postventa", key="comentario_a3")
    a41 = st.slider("4.1 Plan de Entrega (TEC-05)", 0, 100, 70)
    comentario_a41 = st.text_area("Comentario sobre Plan de Entrega", key="comentario_a41")
    a42 = st.slider("4.2 Plan de Contingencias (TEC-06)", 0, 100, 70)
    comentario_a42 = st.text_area("Comentario sobre Plan de Contingencias", key="comentario_a42")

    ponderado = a2 * 0.3 + a3 * 0.3 + a41 * 0.2 + a42 * 0.2
    st.metric("Puntaje ponderado total (aspectos 2–4)", round(ponderado, 2))

    st.markdown("---")
    st.markdown("**Resumen de evaluación de producto ofertado**")
    st.write(f"Segmento S1: {s1}")
    st.write(f"Segmento S2: {s2}")
    st.write(f"Segmento S3: {s3}")

# ---------- GUARDAR RESULTADOS ---------- #

if st.button("Guardar evaluación"):
    datos = {
        "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Evaluador": evaluador,
        "División": division,
        "Tipo": tipo
    }

    if tipo == "Servicio":
        for criterio, _ in criterios:
            puntaje = st.session_state.get(criterio, None)
            comentario = st.session_state.get(f"comentario_{criterio}", "")
            datos[f"{criterio} (Puntaje)"] = puntaje
            datos[f"{criterio} (Comentario)"] = comentario
        datos["Puntaje Total"] = round(puntaje_total, 2)

    else:
        datos["Producto S1"] = s1
        datos["Producto S2"] = s2
        datos["Producto S3"] = s3
        datos["2. Plan Aseguramiento de Calidad (Puntaje)"] = a2
        datos["2. Plan Aseguramiento de Calidad (Comentario)"] = comentario_a2
        datos["3. Asistencia Técnica Postventa (Puntaje)"] = a3
        datos["3. Asistencia Técnica Postventa (Comentario)"] = comentario_a3
        datos["4.1 Plan de Entrega (Puntaje)"] = a41
        datos["4.1 Plan de Entrega (Comentario)"] = comentario_a41
        datos["4.2 Plan de Contingencias (Puntaje)"] = a42
        datos["4.2 Plan de Contingencias (Comentario)"] = comentario_a42
        datos["Puntaje Total"] = round(ponderado, 2)

    df = pd.DataFrame([datos])
    try:
        df.to_csv("evaluaciones.csv", mode='a', header=not pd.read_csv("evaluaciones.csv").empty, index=False)
    except FileNotFoundError:
        df.to_csv("evaluaciones.csv", index=False)

    st.success("✅ Evaluación guardada en 'evaluaciones.csv'")

