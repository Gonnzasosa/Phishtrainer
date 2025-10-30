import json, random, pathlib
import streamlit as st

st.set_page_config(page_title="PhishTrainer", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# ========== CSS =============
CSS = """
<style>
:root {
  --bg:#0b1120; --card:#111827; --text:#e6f0f5; --muted:#a7b0c0;
  --accent1:#44ffa1; --accent2:#39b9ff;
}
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 800px at 20% 0%, rgba(68,255,161,0.06), transparent 40%),
              radial-gradient(1000px 700px at 100% 0%, rgba(57,185,255,0.07), transparent 40%),
              var(--bg) !important;
}
h1,h2,h3,h4,h5,h6,p,span,div {font-family: Inter, sans-serif !important; color: var(--text);}
.block-container {padding-top: 2rem; padding-bottom: 3rem;}
.card { background: rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.1); border-radius:14px; padding:1.25rem; box-shadow: 0 10px 30px rgba(0,0,0,.35); }
.badge { display:inline-block; padding:.25rem .6rem; border-radius:999px; border:1px solid rgba(255,255,255,.15); color:var(--muted); background:rgba(255,255,255,.06); font-size:.85rem;}
.kpi {font-size:2rem; font-weight:700; background:linear-gradient(90deg,var(--accent1),var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.email { background: #0f172a; border-radius:12px; border:1px solid rgba(255,255,255,.08); padding:1rem; }
.email .hdr { color:var(--muted); font-size:.9rem; margin-bottom:.25rem;}
.email .subj { font-weight:700; margin:.2rem 0 .6rem 0; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ========== LOAD DATA ==========
DATA_PATH = pathlib.Path(__file__).with_name("emails_dataset.json")
EMAILS = json.loads(DATA_PATH.read_text(encoding="utf-8"))

LEVEL_MAP = {"Principiante":"basic", "Intermedio":"mid", "Avanzado":"advanced"}

for k,v in {"stage":"level","level":None,"order":[],"index":0,"score":0,"answers":[]}.items():
    if k not in st.session_state: st.session_state[k]=v

def start_level(level_human):
    st.session_state.level = LEVEL_MAP[level_human]
    pool = [e for e in EMAILS if e["level"]==st.session_state.level]
    st.session_state.order = random.sample(range(len(pool)), len(pool))
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.stage = "quiz"
    st.session_state.pool = pool

def reset_all():
    st.session_state.stage="level"; st.session_state.level=None; st.session_state.index=0; st.session_state.score=0; st.session_state.answers=[]

# ========== HEADER ==========
c1,c2 = st.columns([1,5])
with c1:
    st.image("assets/logo.svg", width=200)
with c2:
    st.markdown("<div style='margin-top:12px' class='badge'>Entrenador anti-phishing</div>", unsafe_allow_html=True)
    st.markdown("### Identificá correos falsos como un analista SOC 🔐")

st.write("")

# ========== LEVEL SELECT ==========
if st.session_state.stage == "level":
    st.markdown("## Elegí tu nivel")
    colA,colB,colC = st.columns(3)
    with colA:
        st.markdown("<div class='card'><b>Principiante</b><br/>Señales claras, ejemplos básicos.</div>", unsafe_allow_html=True)
        if st.button("Iniciar Principiante"): start_level("Principiante"); st.rerun()
    with colB:
        st.markdown("<div class='card'><b>Intermedio</b><br/>Lookalikes y técnicas sutiles.</div>", unsafe_allow_html=True)
        if st.button("Iniciar Intermedio"): start_level("Intermedio"); st.rerun()
    with colC:
        st.markdown("<div class='card'><b>Avanzado</b><br/>Spear phishing y MFA fraudulento.</div>", unsafe_allow_html=True)
        if st.button("Iniciar Avanzado"): start_level("Avanzado"); st.rerun()

# ========== QUIZ ==========
elif st.session_state.stage == "quiz":
    pool = st.session_state.pool
    if st.session_state.index < len(pool):
        email = pool[ st.session_state.order[ st.session_state.index ] ]

        st.markdown(f"<span class='badge'>Nivel: {st.session_state.level.title()}</span>", unsafe_allow_html=True)
        st.markdown("<div class='email'>", unsafe_allow_html=True)
        st.markdown(f"<div class='hdr'>De: <b>{email['sender']}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subj'>{email['subject']}</div>", unsafe_allow_html=True)
        st.write(email["body"])
        st.markdown("</div>", unsafe_allow_html=True)

        choice = st.radio("¿Qué tipo de correo es?",
                          ["Phishing","Legítimo","No estoy seguro"], horizontal=True)

        if st.button("Confirmar"):
            gold = email["label"]
            pred = "phishing" if choice=="Phishing" else ("legitimo" if choice=="Legítimo" else "doubt")
            correct = (pred == gold)
            points = 10 if correct else (3 if pred=="doubt" else 0)
            st.session_state.score += points
            st.session_state.answers.append({"id":email["id"],"choice":pred,"correct":gold,"pts":points})
            st.session_state.index += 1
            st.rerun()

    else:
        total = len(pool)*10
        score_pct = round(100*st.session_state.score/total)
        correct = sum(1 for a in st.session_state.answers if a["choice"]==a["correct"])
        unsure = sum(1 for a in st.session_state.answers if a["choice"]=="doubt")

        st.markdown("## ✅ Resultados")
        st.write(f"**Puntaje:** {st.session_state.score}/{total} ({score_pct}%)")
        st.write(f"Correctas: {correct}/{len(pool)}")
        st.write(f"Dudas: {unsure}")

        st.download_button("Descargar resultados (JSON)",
            data=json.dumps(st.session_state.answers,ensure_ascii=False,indent=2),
            file_name="phishtrainer_resultados.json", mime="application/json")

        if st.button("Volver a elegir nivel"):
            reset_all(); st.rerun()
