import streamlit as st
import json
import csv
import os
from datetime import datetime

ARQUIVO_FILAMENTOS = 'filamentos.json'
ARQUIVO_HISTORICO = 'historico_orcamentos.csv'

# Configuração da página para mobile
st.set_page_config(page_title="PressStart Calc", page_icon="🎮", layout="centered")

# --- FUNÇÕES DE DADOS ---
def carregar_filamentos():
    if os.path.exists(ARQUIVO_FILAMENTOS):
        try:
            with open(ARQUIVO_FILAMENTOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"PLA Genérico": 120.0, "PETG Genérico": 130.0}

def salvar_filamentos(dados):
    try:
        with open(ARQUIVO_FILAMENTOS, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4)
    except Exception:
        pass

def salvar_historico(dados):
    arquivo_existe = os.path.isfile(ARQUIVO_HISTORICO)
    with open(ARQUIVO_HISTORICO, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        if not arquivo_existe:
            writer.writerow(['ID Orcamento', 'Data', 'Projeto/Cliente', 'Filamentos', 'Custo Producao', 'Lucro R$', 'Mao de Obra', 'Preco Venda'])
        writer.writerow([
            dados['id'],
            datetime.now().strftime("%d/%m/%Y %H:%M"), 
            dados['nome'], 
            dados['filamento_resumo'], 
            f"R$ {dados['custo']:.2f}", 
            f"R$ {dados['lucro']:.2f}", 
            f"R$ {dados['mao_de_obra']:.2f}",
            f"R$ {dados['venda']:.2f}"
        ])

# Inicializa sessão
if 'filamentos_db' not in st.session_state:
    st.session_state.filamentos_db = carregar_filamentos()

# --- INTERFACE ---
st.title("🎮 PressStart Simple Calc")

st.subheader("Dados do Projeto")
nome_projeto = st.text_input("Nome da Peça / Cliente", "Projeto sem nome")

st.divider()
st.subheader("Configuração de Filamentos")

# Filamento Principal
st.markdown("**Filamento Principal**")
col1, col2 = st.columns(2)
with col1:
    tipo_filamento1 = st.selectbox("Selecione o Filamento 1", list(st.session_state.filamentos_db.keys()), key="fil1")
with col2:
    preco_sugerido1 = st.session_state.filamentos_db[tipo_filamento1]
    preco_rolo1 = st.number_input("Custo rolo 1kg (R$)", value=float(preco_sugerido1), step=1.0, key="preco1")
    
col_peso1, col_desp1 = st.columns(2)
with col_peso1:
    peso_peca1 = st.number_input("Peso da peça (g)", min_value=0.0, step=1.0, key="peso1")
with col_desp1:
    peso_desperdicio1 = st.number_input("Suportes/Purgas (g)", min_value=0.0, step=1.0, key="desp1")

# Filamento Secundário (Opcional)
usar_filamento2 = st.checkbox("➕ Adicionar Segundo Filamento (Multicolor/Múltiplas Peças)")
tipo_filamento2 = ""
preco_rolo2 = 0.0
peso_peca2 = 0.0
peso_desperdicio2 = 0.0

if usar_filamento2:
    st.markdown("**Segundo Filamento**")
    col3, col4 = st.columns(2)
    with col3:
        tipo_filamento2 = st.selectbox("Selecione o Filamento 2", list(st.session_state.filamentos_db.keys()), key="fil2")
    with col4:
        preco_sugerido2 = st.session_state.filamentos_db[tipo_filamento2]
        preco_rolo2 = st.number_input("Custo rolo 1kg (R$)", value=float(preco_sugerido2), step=1.0, key="preco2")
        
    col_peso2, col_desp2 = st.columns(2)
    with col_peso2:
        peso_peca2 = st.number_input("Peso da peça (g)", min_value=0.0, step=1.0, key="peso2")
    with col_desp2:
        peso_desperdicio2 = st.number_input("Suportes/Purgas (g)", min_value=0.0, step=1.0, key="desp2")

with st.expander("📝 Cadastrar Novo Filamento no Banco de Dados"):
    novo_nome = st.text_input("Nome do novo filamento")
    novo_preco = st.number_input("Preço (R$)", min_value=0.0, step=1.0)
    if st.button("
