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
    if st.button("Salvar Filamento"):
        if novo_nome:
            st.session_state.filamentos_db[novo_nome] = novo_preco
            salvar_filamentos(st.session_state.filamentos_db)
            st.success(f"{novo_nome} salvo!")
            st.rerun()

st.divider()
st.subheader("Produção e Acabamento")

col_horas, col_lucro = st.columns(2)
with col_horas:
    horas_impressao = st.number_input("Tempo de Impressão (horas)", min_value=0.0, step=0.5)
with col_lucro:
    margem_lucro = st.number_input("Margem de Lucro (%)", min_value=0.0, value=100.0, step=5.0)

mao_de_obra = st.number_input("Valor de Acabamento / Pintura (R$) - Inserido no final sem margem", min_value=0.0, step=5.0)

st.divider()
usa_energia = st.checkbox("Incluir energia/desgaste (R$ 1,50/h)", value=True)
usa_ams = st.checkbox("Utilizar AMS / Multicolor (+10% custo na produção)")

# --- AÇÃO DE CÁLCULO ---
if st.button("Calcular e Gerar Orçamento", use_container_width=True, type="primary"):
    if peso_peca1 > 0 or peso_peca2 > 0:
        custo_mat1 = peso_peca1 * (preco_rolo1 / 1000)
        custo_sup1 = peso_desperdicio1 * (preco_rolo1 / 1000)
        
        custo_mat2 = peso_peca2 * (preco_rolo2 / 1000) if usar_filamento2 else 0.0
        custo_sup2 = peso_desperdicio2 * (preco_rolo2 / 1000) if usar_filamento2 else 0.0
        
        custo_maquina = (horas_impressao * 1.50) if usa_energia else 0.0
        custo_producao_base = custo_mat1 + custo_sup1 + custo_mat2 + custo_sup2 + custo_maquina
        
        if usa_ams: 
            custo_producao_base *= 1.10
            
        valor_lucro = custo_producao_base * (margem_lucro / 100)
        preco_venda_final = custo_producao_base + valor_lucro + mao_de_obra

        id_orcamento = datetime.now().strftime("%Y%m%d%H%M")
        
        resumo_filamentos = f"{tipo_filamento1}"
        if usar_filamento2:
            resumo_filamentos += f" + {tipo_filamento2}"

        dados_atuais = {
            "id": id_orcamento,
            "nome": nome_projeto, 
            "filamento_resumo": resumo_filamentos, 
            "horas": horas_impressao,
            "custo": custo_producao_base, 
            "lucro": valor_lucro, 
            "mao_de_obra": mao_de_obra,
            "venda": preco_venda_final
        }
        
        try:
            salvar_historico(dados_atuais)
        except Exception:
            pass 

        st.session_state.ultimo_calculo = dados_atuais
        st.success(f"Orçamento Nº {id_orcamento} calculado com sucesso!")
    else:
        st.error("Insira o peso de pelo menos uma peça para calcular.")


# --- EXIBIÇÃO DO RECIBO ---
if 'ultimo_calculo' in st.session_state:
    st.divider()
    st.subheader("📱 Visão do Cliente (Print)")
    
    # Seletor de Tema
    tema = st.radio("Escolha o visual do orçamento:", ["Claro (Branco)", "Escuro (Noturno)"], horizontal=True)
    
    # Configuração de Cores baseada na escolha
    if tema == "Claro (Branco)":
        bg_color = "#ffffff"
        text_color = "#333333"
        border_color = "#e30613" # Borda vermelha PressStart
        box_shadow = "rgba(0,0,0,0.15)"
        divider_color = "#eeeeee"
        sub_color = "#777777"
        highlight_bg = "#f9f9f9"
    else:
        bg_color = "#1e1e1e"
        text_color = "#ffffff"
        border_color = "#e30613" # Borda vermelha PressStart
        box_shadow = "rgba(0,0,0,0.5)"
        divider_color = "#333333"
        sub_color = "#aaaaaa"
        highlight_bg = "#2a2a2a"

    dados = st.session_state.ultimo_calculo
    
    linha_acabamento = ""
    if dados['mao_de_obra'] > 0:
        linha_acabamento = f"<p style='margin: 8px 0;'><b>ACABAMENTO/PINTURA:</b> <span style='float: right;'>Incluído</span></p>"

    # HTML Melhorado do Recibo (SEM INDENTAÇÃO para não virar código no Streamlit)
    recibo_html = f"""<div style="background-color: {bg_color}; padding: 30px 25px; border-radius: 12px; border: 3px solid {border_color}; box-shadow: 0 10px 25px {box_shadow}; color: {text_color}; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 400px; margin: 10px auto;">
<div style="text-align: center; border-bottom: 2px solid {divider_color}; padding-bottom: 15px; margin-bottom: 20px;">
<h1 style="color: #e30613; margin: 0; font-size: 28px; font-weight: 900; letter-spacing: 1px;">PRESS START 3D</h1>
<p style="font-size: 11px; color: {sub_color}; margin: 2px 0 12px 0; letter-spacing: 2px; text-transform: uppercase;">Serviços de Impressão 3D</p>
<div style="background-color: {highlight_bg}; padding: 8px; border-radius: 6px; display: inline-block;">
<p style="margin: 0; font-size: 13px; font-weight: bold; color: {text_color};">📱 (19) 97199-9114 &nbsp;|&nbsp; 📸 @pressstart_3d</p>
</div>
</div>
<div style="font-size: 15px; line-height: 1.6;">
<p style="margin: 8px 0;"><b>ORÇAMENTO Nº:</b> <span style="float: right; color: {sub_color};">{dados['id']}</span></p>
<p style="margin: 8px 0;"><b>PROJETO:</b> <span style="float: right; font-weight: bold;">{dados['nome'].upper()}</span></p>
<p style="margin: 8px 0;"><b>MATERIAL:</b> <span style="float: right; font-size: 14px;">{dados['filamento_resumo']}</span></p>
<p style="margin: 8px 0;"><b>TEMPO EST.:</b> <span style="float: right;">{dados['horas']} horas</span></p>
{linha_acabamento}
</div>
<div style="margin-top: 20px; border-top: 2px dashed {divider_color}; padding-top: 20px; text-align: center;">
<p style="margin: 0; font-size: 14px; font-weight: bold; color: {sub_color}; text-transform: uppercase;">Total a Pagar</p>
<h1 style="color: #e30613; margin: 5px 0 10px 0; font-size: 38px;">R$ {dados['venda']:.2f}</h1>
<p style="font-size: 11px; color: {sub_color}; margin: 0;">Orçamento válido por 7 dias.<br>Data: {datetime.now().strftime("%d/%m/%Y")}</p>
</div>
</div>"""
    
    st.markdown(recibo_html, unsafe_allow_html=True)
    st.caption("📸 O recibo atualizado está pronto. Você pode alterar a cor e tirar o print.")
