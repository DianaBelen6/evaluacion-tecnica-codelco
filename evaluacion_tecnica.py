import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Evaluación Técnica Codelco", layout="wide")
st.title("Evaluación Técnica de Proveedores - Servicios de Reparación de Chancadores")

# ---- Funciones auxiliares ----
def clasificar_puntaje(p):
    if p >= 100:
        return "Excelente", "Cumple"
    elif p >= 90:
        return "Bueno", "Cumple"
    elif p >= 70:
        return "Suficiente", "Cumple"
    elif p >= 50:
        return "Regular", "No Cumple"
    else:
        return "Insuficiente", "No Cumple"

def escenario_adjudicacion(tipo, escenario, clasificacion):
    escenarios = {
        "Servicio": {
            "S1": {
                "Cumple": "CUMPLE",
                "Cumple Back Up": "CUMPLE BACK UP",
                "Cumple Prueba Industrial": "CUMPLE PRUEBA INDUSTRIAL",
                "No Cumple": "NO CUMPLE",
                "No Oferta": "NO OFERTA",
                "No Aplica": "NO APLICA"
            },
            "S2": {
                "Cumple": "CUMPLE",
                "Cumple Prueba Industrial": "CUMPLE PRUEBA INDUSTRIAL",
                "No Cumple": "NO CUMPLE",
                "No Oferta": "NO OFERTA",
                "No Aplica": "NO APLICA"
            },
            "S3": {
                "Cumple": "CUMPLE",
                "No Cumple": "NO CUMPLE",
                "No Oferta": "NO OFERTA",
                "No Aplica": "NO APLICA"
            }
        },
        "Suministro": {
            "S1": {
                "Cumple": "CUMPLE",
                "Cumple Prueba Industrial": "CUMPLE PRUEBA INDUSTRIAL",
                "Cumple Back Up": "CUMPLE BACK UP",
                "No Cumple": "NO CUMPLE",
                "No Oferta": "NO OFERTA",
                "No Aplica": "NO APLICA"
            },
            "S2": {
                "Cumple": "CUMPLE",
                "Cumple Prueba Industrial": "CUMPLE PRUEBA INDUSTRIAL",
                "No Cumple": "NO CUMPLE",
                "No Oferta": "NO OFERTA",
                "No Aplica": "NO APLICA"
            },
            "S3": {
                "Cumple": "CUMPLE",
                "No Cumple": "NO CUMPLE",
                "No Oferta": "NO OFERTA",
                "No Aplica": "NO APLICA"
            }
        }
    }
    return escenarios.get(tipo, {}).get(escenario, {}).get(clasificacion, "NO DEFINIDO")

# ---- Formulario principal ----
st.subheader("Formulario de Evaluación Técnica")

proveedor = st.text_input("Nombre del proveedor a evaluar")

with st.form("form_evaluacion"):
    st.markdown("### 1. Empresa (10%)")
    org = st.slider("1.1 Organización de la empresa", 0, 100)
    exp = st.slider("1.2 Años de experiencia", 0, 100)
    cert = st.slider("1.3 Certificaciones", 0, 100)

    st.markdown("### 2. Metodología de trabajo (30%)")
    prog = st.slider("2.1 Programación reparación", 0, 100)
    ctrl = st.slider("2.2 Control programación", 0, 100)
    proc = st.slider("2.3 Procedimientos reparación", 0, 100)
    orgz = st.slider("2.4 Estructura organizacional", 0, 100)
    cont = st.slider("2.5 Plan de contingencia", 0, 100)
    seg = st.slider("2.6 Seguridad y salud", 0, 100)

    st.markdown("### 5. Propuesta de mejoras / innovación (5%)")
    mejoras = st.slider("5.1 Propuesta de mejoras", 0, 100)

    st.markdown("### Configuración de Escenario")
    tipo_item = st.selectbox("Tipo de ítem", ["Servicio", "Suministro"])
    escenario = st.selectbox("Escenario de adjudicación", ["S1", "S2", "S3"])

    enviar = st.form_submit_button("Evaluar")

# ---- Resultados ----
if enviar:
    puntaje_1 = (org*0.2 + exp*0.4 + cert*0.4) * 0.10
    puntaje_2 = (prog*0.2 + ctrl*0.15 + proc*0.2 + orgz*0.1 + cont*0.15 + seg*0.2) * 0.30
    puntaje_5 = mejoras * 0.05

    total = puntaje_1 + puntaje_2 + puntaje_5
    clasificacion, estado = clasificar_puntaje(total)
    resultado_adjudicacion = escenario_adjudicacion(tipo_item, escenario, estado)

    st.markdown("### 📝 Resultado de Evaluación")
    st.write(f"Proveedor Evaluado: **{proveedor}**")
    st.write(f"**Puntaje Total:** {round(total,2)}")
    st.write(f"**Clasificación TCG:** {clasificacion}")
    st.write(f"**Cumple técnicamente:** {estado}")
    st.write(f"**Escenario de Adjudicación:** {resultado_adjudicacion}")
