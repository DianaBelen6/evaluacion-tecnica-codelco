import streamlit as st
import pandas as pd
import datetime as dt
import io
import os
import uuid
 
# =============================================================
# CONFIGURACIÓN BÁSICA
# =============================================================
st.set_page_config(page_title="Evaluación Técnica Codelco", layout="wide")
 
# ---------- Estilos (CSS simple) ---------- #
STYLES = """
<style>
    .main > div {padding-top: 1rem;}
    .kpi-card {border-radius: 16px; padding: 1rem 1.25rem; box-shadow: 0 6px 16px rgba(0,0,0,0.08);}
    .muted {color: #6b7280; font-size: 0.9rem;}
    .section-title {margin-top: 0.25rem;}
    .small {font-size: 0.85rem;}
    .tag {display:inline-block; padding:0.1rem 0.5rem; border-radius:999px; background:#eef2ff; color:#3730a3; font-weight:600;}
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)
 
# =============================================================
# PARÁMETROS Y UMBRALES
# =============================================================
DIVISIONES = ["Andina", "Chuquicamata", "El Teniente", "Radomiro Tomic", "Ministro Hales"]
TIPOS = ["Servicio", "Suministro"]
 
# Rangos de interpretación (ajustables)
THRESHOLDS = [
    (80, "Cumple"),
    (60, "Cumple Back Up"),
    (40, "Cumple Prueba Industrial"),
    (1,  "No Cumple"),
    (0,  "No Oferta / No Aplica"),
]
 
SEGMENT_RESULT_OPTS = [
    "No Aplica", "No Oferta", "No Cumple", "Cumple",
    "Cumple Prueba Industrial", "Cumple Back Up"
]
 
# Criterios Servicio (etiqueta, peso)
CRITERIOS_SERVICIO = [
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
    ("5. Propuesta de mejoras/innovación", 0.05),
]
 
# Aspectos Suministro (etiqueta, peso)
ASPECTOS_SUMINISTRO = [
    ("2. Plan Aseguramiento de Calidad (TEC-04)", 0.30),
    ("3. Asistencia Técnica Postventa (TEC-03)", 0.30),
    ("4.1 Plan de Entrega (TEC-05)", 0.20),
    ("4.2 Plan de Contingencias (TEC-06)", 0.20),
]
 
# =============================================================
# FUNCIONES AUXILIARES
# =============================================================
 
def evaluate_band(score: float) -> str:
    for thr, label in THRESHOLDS:
        if score >= thr:
            return label
    return THRESHOLDS[-1][1]
 
 
def safe_append_csv(df: pd.DataFrame, path: str) -> None:
    """Append a DataFrame to CSV, creating it if it doesn't exist."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        df.to_csv(path, mode="a", header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(path, index=False, encoding="utf-8")
 
 
def df_to_download_bytes(df: pd.DataFrame, fmt: str = "csv") -> bytes:
    if fmt == "csv":
        return df.to_csv(index=False).encode("utf-8")
    elif fmt == "xlsx":
        bio = io.BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Evaluaciones")
        return bio.getvalue()
    else:
        raise ValueError("Formato no soportado")
 
 
def total_weight(items):
    return round(sum(w for _, w in items), 4)
 
# =============================================================
# SIDEBAR (Identificación y controles)
# =============================================================
with st.sidebar:
    st.markdown("### Configuración")
    if st.button("➕ Nueva evaluación"):
        st.session_state.clear()
        st.experimental_rerun()
 
    st.markdown("---")
    st.markdown("**Umbrales de interpretación**")
    for thr, label in THRESHOLDS:
        st.markdown(f"- ≥ **{thr}**: {label}")
 
# =============================================================
# ENCABEZADO
# =============================================================
st.title("Formulario de Evaluación Técnica – Codelco")
colA, colB, colC, colD = st.columns([2,2,2,2])
 
with colA:
    evaluador = st.text_input("Nombre del evaluador")
with colB:
    division = st.selectbox("División", DIVISIONES)
with colC:
    tipo = st.selectbox("Tipo de ítem evaluado", TIPOS)
with colD:
    fecha_eval = st.date_input("Fecha de evaluación", value=dt.date.today())
 
st.caption("Los puntajes de criterios van de 0 a 100. El resultado final muestra el tramo: Cumple / Cumple Back Up / Cumple Prueba Industrial / No Cumple / No Oferta.")
 
# KPI de pesos
peso_serv = total_weight(CRITERIOS_SERVICIO)
peso_sum = total_weight(ASPECTOS_SUMINISTRO)
with st.expander("Ver suma de ponderaciones"):
    st.write({"Servicio": peso_serv, "Suministro": peso_sum})
 
# =============================================================
# CUERPO (evaluación)
# =============================================================
resultado = {}
 
if tipo == "Servicio":
    st.subheader("Evaluación técnica – Servicios")
 
    # Presentación en tarjetas por grupos de 3 criterios por fila
    puntaje_total = 0.0
    cols = st.columns(3)
    for idx, (criterio, peso) in enumerate(CRITERIOS_SERVICIO):
        with cols[idx % 3]:
            score = st.slider(criterio, min_value=0, max_value=100, value=70, key=f"s_{idx}")
            st.caption(f"Ponderación: {peso:.3f}")
            comentario = st.text_area(f"Comentario – {criterio}", key=f"c_{idx}", height=80)
        puntaje_total += score * peso
 
    puntaje_total = round(puntaje_total, 2)
    banda = evaluate_band(puntaje_total)
 
    st.markdown("---")
    k1, k2 = st.columns(2)
    with k1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Puntaje ponderado total", f"{puntaje_total}")
        st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Clasificación", banda)
        st.markdown('</div>', unsafe_allow_html=True)
 
    resultado.update({
        "Puntaje Total": puntaje_total,
        "Clasificación": banda,
    })
 
else:
    st.subheader("Evaluación técnica – Suministros")
 
    st.markdown("**Producto ofertado por segmento**")
    col1, col2, col3 = st.columns(3)
    with col1:
        s1 = st.selectbox("Segmento S1", SEGMENT_RESULT_OPTS)
    with col2:
        s2 = st.selectbox("Segmento S2", SEGMENT_RESULT_OPTS)
    with col3:
        s3 = st.selectbox("Segmento S3", SEGMENT_RESULT_OPTS)
 
    st.markdown("**Aspectos diferenciadores**")
    puntaje_total = 0.0
    cols = st.columns(2)
    aspect_scores = {}
    for idx, (label, peso) in enumerate(ASPECTOS_SUMINISTRO):
        with cols[idx % 2]:
            val = st.slider(label, 0, 100, 70, key=f"a_{idx}")
            st.caption(f"Ponderación: {peso:.2f}")
            comentario = st.text_area(f"Comentario – {label}", key=f"ac_{idx}", height=80)
            aspect_scores[label] = val
            puntaje_total += val * peso
 
    puntaje_total = round(puntaje_total, 2)
    banda = evaluate_band(puntaje_total)
 
    st.markdown("---")
    k1, k2 = st.columns(2)
    with k1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Puntaje ponderado total (aspectos 2–4)", f"{puntaje_total}")
        st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("Clasificación", banda)
        st.markdown('</div>', unsafe_allow_html=True)
 
    st.markdown("---")
    st.markdown("**Resumen de evaluación de producto ofertado**")
    res_seg = {"Producto S1": s1, "Producto S2": s2, "Producto S3": s3}
    st.table(pd.DataFrame([res_seg]))
 
    resultado.update({
        "Puntaje Total": puntaje_total,
        "Clasificación": banda,
        **res_seg,
        **{k + " (Puntaje)": v for k, v in aspect_scores.items()},
    })
 
# =============================================================
# GUARDADO Y DESCARGA
# =============================================================
 
# Validación mínima antes de guardar
def ready_to_save():
    return bool(evaluador and division and tipo)
 
st.markdown("---")
colL, colR = st.columns([3,2])
 
with colL:
    if st.button("💾 Guardar evaluación", use_container_width=True):
        if not ready_to_save():
            st.error("Por favor, complete Evaluador, División y Tipo antes de guardar.")
        else:
            eval_id = str(uuid.uuid4())[:8]
            base = {
                "ID": eval_id,
                "Fecha": dt.datetime.combine(fecha_eval, dt.time.min).strftime("%Y-%m-%d"),
                "Evaluador": evaluador,
                "División": division,
                "Tipo": tipo,
            }
 
            # Reconstruir variables guardadas
            data = {}
            if tipo == "Servicio":
                # scores y comentarios por índice
                puntajes = []
                comentarios = []
                for idx, (crit, _peso) in enumerate(CRITERIOS_SERVICIO):
                    score = st.session_state.get(f"s_{idx}", None)
                    comm = st.session_state.get(f"c_{idx}", "")
                    data[f"{crit} (Puntaje)"] = score
                    data[f"{crit} (Comentario)"] = comm
                    puntajes.append(score)
                    comentarios.append(comm)
 
            else:  # Suministro
                data.update(res_seg)
                for idx, (label, _peso) in enumerate(ASPECTOS_SUMINISTRO):
                    val = st.session_state.get(f"a_{idx}", None)
                    comm = st.session_state.get(f"ac_{idx}", "")
                    data[f"{label} (Puntaje)"] = val
                    data[f"{label} (Comentario)"] = comm
 
            # comunes
            data["Puntaje Total"] = resultado.get("Puntaje Total")
            data["Clasificación"] = resultado.get("Clasificación")
 
            row = {**base, **data}
            df = pd.DataFrame([row])
            try:
                safe_append_csv(df, "evaluaciones.csv")
                st.success("✅ Evaluación guardada en 'evaluaciones.csv'")
            except Exception as e:
                st.error(f"No fue posible guardar el archivo: {e}")
 
with colR:
    # Previsualización resumida
    if resultado:
        st.markdown("**Resumen**")
        resumen = {
            "Evaluador": evaluador or "-",
            "División": division or "-",
            "Tipo": tipo,
            "Fecha": fecha_eval.strftime("%Y-%m-%d"),
            "Puntaje Total": resultado.get("Puntaje Total", "-"),
            "Clasificación": resultado.get("Clasificación", "-"),
        }
        st.json(resumen)
 
    # Botones de descarga on-the-fly (no requiere archivo previo)
    if st.button("Generar archivo para descargar"):
        if not ready_to_save():
            st.error("Complete Evaluador, División y Tipo para generar la descarga.")
        else:
            # Construir el mismo DataFrame que se guardaría
            base = {
                "ID": "preview",
                "Fecha": fecha_eval.strftime("%Y-%m-%d"),
                "Evaluador": evaluador,
                "División": division,
                "Tipo": tipo,
            }
            data = {}
            if tipo == "Servicio":
                for idx, (crit, _peso) in enumerate(CRITERIOS_SERVICIO):
                    score = st.session_state.get(f"s_{idx}", None)
                    comm = st.session_state.get(f"c_{idx}", "")
                    data[f"{crit} (Puntaje)"] = score
                    data[f"{crit} (Comentario)"] = comm
            else:
                # Suministro preview: reconstruir desde estado si existe
                data.update({
                    "Producto S1": st.session_state.get("Segmento S1", ""),
                    "Producto S2": st.session_state.get("Segmento S2", ""),
                    "Producto S3": st.session_state.get("Segmento S3", ""),
                })
                for idx, (label, _peso) in enumerate(ASPECTOS_SUMINISTRO):
                    val = st.session_state.get(f"a_{idx}", None)
                    comm = st.session_state.get(f"ac_{idx}", "")
                    data[f"{label} (Puntaje)"] = val
                    data[f"{label} (Comentario)"] = comm
 
            data["Puntaje Total"] = resultado.get("Puntaje Total")
            data["Clasificación"] = resultado.get("Clasificación")
            df_prev = pd.DataFrame([{**base, **data}])
 
            csv_bytes = df_to_download_bytes(df_prev, fmt="csv")
            xlsx_bytes = df_to_download_bytes(df_prev, fmt="xlsx")
 
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv_bytes,
                file_name=f"evaluacion_tecnica_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                label="⬇️ Descargar Excel",
                data=xlsx_bytes,
                file_name=f"evaluacion_tecnica_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
 
# =============================================================
# NOTAS FINALES
# =============================================================
st.markdown("---")
st.markdown("<span class='muted'>Versión profesional del formulario con validación, clasificación por tramos y exportación.</span>", unsafe_allow_html=True)
