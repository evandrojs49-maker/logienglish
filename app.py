import streamlit as st
import google.generativeai as genai
import random
from gtts import gTTS
import base64
import io

# --- CONFIGURAÇÃO DA IA (SUA CHAVE JÁ APLICADA) ---
GOOGLE_API_KEY = "AIzaSyBceTMk-vUoayhGofyyGUN7ZwT3Spg8o4k"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="LogiEnglish AI v5.0", layout="wide")

# --- ESTILO PARA O CELULAR (TABLET) ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 12px; height: 3.5em; border: 2px solid #f0f2f6; }
    .stButton>button:hover { border-color: #0083B8; color: #0083B8; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO PARA GERAR FRASE COM IA ---
def gerar_frase_ia(nivel):
    prompt = f"""
    Gere uma frase de logística (fretagem, embarque, rotas) em inglês para o nível de dificuldade {nivel} de 5.
    Retorne EXATAMENTE neste formato, sem explicações extras:
    portugues: [tradução]
    ingles: [frase original]
    dica: [explicação técnica do termo de logística usado]
    """
    try:
        response = model.generate_content(prompt)
        linhas = response.text.strip().split('\n')
        dados = {}
        for linha in linhas:
            if ':' in linha:
                chave, valor = linha.split(':', 1)
                dados[chave.strip().lower()] = valor.strip()
        return dados
    except:
        return {"portugues": "Erro na IA", "ingles": "AI Error", "dica": "Verifique a chave API"}

# --- FUNÇÃO DE ÁUDIO ---
def tocar_audio(texto, lang='en'):
    try:
        tts = gTTS(text=texto, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        html_audio = f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
        st.markdown(html_audio, unsafe_allow_html=True)
    except: pass

# --- INTERFACE ---
st.title("🏗️ LogiEnglish AI")
st.caption("Treinamento de Inglês para Logística (Embarcador)")

# Barra Lateral
nivel = st.sidebar.select_slider("Dificuldade:", options=[1, 2, 3, 4, 5], value=1)

if 'f_obj' not in st.session_state or st.sidebar.button("Novo Desafio 🤖"):
    with st.spinner("O Gemini está gerando sua frase técnica..."):
        st.session_state.f_obj = gerar_frase_ia(nivel)
        st.session_state.construcao = []
        # Limpa pontuação para os blocos
        txt = st.session_state.f_obj['ingles'].replace('?', '').replace('.', '').replace(',', '')
        st.session_state.blocos_atual = txt.split()
        random.shuffle(st.session_state.blocos_atual)

f = st.session_state.f_obj

# Área de Pergunta e Áudio Completo
c1, c2 = st.columns([4, 1])
with c1:
    st.info(f"### Traduza: **{f.get('portugues', '...')}**")
with c2:
    if st.button("Ouvir Tudo 🔊", use_container_width=True):
        tocar_audio(f.get('ingles', ''))

st.write("---")

# Exibição dos Blocos (Layout responsivo para Tablet)
st.write("#### Selecione os blocos na ordem correta:")
n_cols = 4
cols = st.columns(n_cols)
for i, palavra in enumerate(st.session_state.blocos_atual):
    with cols[i % n_cols]:
        if st.button(palavra, key=f"b_{i}", use_container_width=True):
            tocar_audio(palavra)
            st.session_state.construcao.append(palavra)
            st.rerun()

# Área de Resposta
st.write("---")
frase_montada = " ".join(st.session_state.construcao)
st.markdown(f"#### Sua Resposta:\n > **{frase_montada if frase_montada else '...'}**")

# Validação
alvo = f.get('ingles', '').replace('?', '').replace('.', '').replace(',', '').strip().lower()
if len(st.session_state.construcao) >= len(alvo.split()) and alvo != "":
    if frase_montada.strip().lower() == alvo:
        st.balloons()
        st.success("🎯 **Correto!**")
        st.info(f"💡 **Dica Técnica:** {f.get('dica', '')}")
        if st.button("Próxima Frase ➡️"):
            st.session_state.pop('f_obj')
            st.rerun()
    else:
        st.error("❌ Ordem incorreta. Clique em Limpar.")

if st.button("Limpar Tudo 🔄"):
    st.session_state.construcao = []
    st.rerun()