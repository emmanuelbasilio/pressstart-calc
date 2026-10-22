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
        with open(ARQUIVO_FILAMENTOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"PLA Genérico": 120.0, "PETG Genérico": 130.0}

def salvar_filamentos(dados):
    with open(ARQUIVO_FILAMENTOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

def salvar_historico(dados):
    arquivo_existe = os.path.isfile(ARQUIVO_HISTORICO)
    with open(ARQUIVO_HISTORICO, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        if not arquivo_existe:
            writer.writerow(['Data', 'Projeto/Cliente', 'Filamento', 'Custo Producao', 'Lucro R$', 'Preco Venda'])
        writer.writerow([
            datetime.now().strftime("%d/%m/%Y %H:%M"), 
            dados['nome'], 
            dados['filamento'], 
            f"R$ {dados['custo']:.2f}", 
            f"R$ {dados['lucro']:.2f}", 
            f"R$ {dados['venda']:.2f}"
        ])

# Inicializa sessão de filamentos
if 'filamentos_db' not in st.session_state:
    st.session_state.filamentos_db = carregar_filamentos()

# --- INTERFACE ---
st.title("🎮 PressStart Simple Calc")

# Abas para separar a parte interna do cliente
aba_calculadora, aba_cliente = st.tabs(["⚙️ Calculadora", "📱 Visão do Cliente"])

with aba_calculadora:
    st.subheader("Dados do Projeto")
    nome_projeto = st.text_input("Nome da Peça / Cliente", "Projeto sem nome")
    
    st.divider()
    st.subheader("Configuração do Filamento")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_filamento = st.selectbox("Filamento Salvo", list(st.session_state.filamentos_db.keys()))
    with col2:
        preco_sugerido = st.session_state.filamentos_db[tipo_filamento]
        preco_rolo = st.number_input("Custo do rolo 1kg (R$)", value=float(preco_sugerido), step=1.0)
    
    with st.expander("➕ Cadastrar Novo Filamento"):
        novo_nome = st.text_input("Nome do novo filamento")
        novo_preco = st.number_input("Preço (R$)", min_value=0.0, step=1.0)
        if st.button("Salvar Filamento"):
            if novo_nome:
                st.session_state.filamentos_db[novo_nome] = novo_preco
                salvar_filamentos(st.session_state.filamentos_db)
                st.success(f"{novo_nome} salvo!")
                st.rerun()

    st.divider()
    col_peso, col_desp = st.columns(2)
    with col_peso:
        peso_peca = st.number_input("Peso da peça (g)", min_value=0.0, step=1.0)
    with col_desp:
        peso_desperdicio = st.number_input("Suportes/Purgas (g)", min_value=0.0, step=1.0)
        
    col_horas, col_lucro = st.columns(2)
    with col_horas:
        horas_impressao = st.number_input("Tempo (horas)", min_value=0.0, step=0.5)
    with col_lucro:
        margem_lucro = st.number_input("Margem de Lucro (%)", min_value=0.0, value=100.0, step=5.0)

    st.divider()
    usa_energia = st.checkbox("Incluir energia/desgaste (R$ 1,50/h)", value=True)
    usa_ams = st.checkbox("Utilizar AMS / Multicolor (+10% custo)")

    # --- CÁLCULOS ---
    if st.button("Calcular e Salvar Histórico", use_container_width=True, type="primary"):
        if peso_peca > 0:
            custo_por_grama = preco_rolo / 1000
            custo_material_util = peso_peca * custo_por_grama
            custo_suportes = peso_desperdicio * custo_por_grama
            custo_maquina = (horas_impressao * 1.50) if usa_energia else 0.0
            
            custo_producao = custo_material_util + custo_suportes + custo_maquina
            if usa_ams: custo_producao *= 1.10
                
            valor_lucro = custo_producao * (margem_lucro / 100)
            preco_venda = custo_producao + valor_lucro

            dados_atuais = {
                "nome": nome_projeto, "filamento": tipo_filamento, "horas": horas_impressao,
                "custo": custo_producao, "lucro": valor_lucro, "venda": preco_venda
            }
            
            salvar_historico(dados_atuais)
            st.session_state.ultimo_calculo = dados_atuais
            
            st.success("Cálculo salvo no histórico!")
            st.info(f"**Custo de Produção:** R$ {custo_producao:.2f} | **Lucro:** R$ {valor_lucro:.2f} | **Venda:** R$ {preco_venda:.2f}")
        else:
            st.error("Insira o peso da peça para calcular.")

with aba_cliente:
    if 'ultimo_calculo' in st.session_state:
        dados = st.session_state.ultimo_calculo
        
        # HTML + CSS para emular o recibo formatado na tela
        recibo_html = f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; color: black; font-family: sans-serif;">
            <h2 style="text-align: center; color: #e30613; margin-bottom: 0;">PRESS START 3D</h2>
            <p style="text-align: center; font-size: 12px; color: #666; margin-top: 0;">SERVIÇOS DE IMPRESSÃO 3D</p>
            <p style="text-align: center; font-size: 14px; font-weight: bold; color: #333;">📱 (19) 97199-9114 <br> 📸 @pressstart_3d</p>
            <hr style="border-top: 1px dashed #ccc;">
            <p><b>PROJETO:</b> <span style="float: right;">{dados['nome'].upper()}</span></p>
            <p><b>MATERIAL:</b> <span style="float: right;">{dados['filamento']}</span></p>
            <p><b>TEMPO EST.:</b> <span style="float: right;">{dados['horas']} horas</span></p>
            <hr style="border-top: 1px dashed #ccc;">
            <h4 style="text-align: center; margin-bottom: 0;">TOTAL A PAGAR</h4>
            <h1 style="text-align: center; color: #e30613; margin-top: 5px;">R$ {dados['venda']:.2f}</h1>
            <p style="text-align: center; font-size: 10px; color: #999;">Orçamento válido por 7 dias.<br>Data: {datetime.now().strftime("%d/%m/%Y")}</p>
        </div>
        """
        st.markdown(recibo_html, unsafe_allow_html=True)
        st.caption("📸 Tire um print desta tela para enviar ao cliente.")
    else:
        st.warning("Faça um cálculo na aba anterior para gerar o orçamento.")