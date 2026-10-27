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

# Inicializa sessão de filamentos
if 'filamentos_db' not in st.session_state:
    st.session_state.filamentos_db = carregar_filamentos()

# --- INTERFACE ---
st.title("🎮 PressStart Simple Calc")

aba_calculadora, aba_cliente = st.tabs(["⚙️ Calculadora", "📱 Visão do Cliente"])

with aba_calculadora:
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

    # --- CÁLCULOS ---
    if st.button("Calcular e Salvar Histórico", use_container_width=True, type="primary"):
        if peso_peca1 > 0 or peso_peca2 > 0:
            # Custo Material 1
            custo_mat1 = peso_peca1 * (preco_rolo1 / 1000)
            custo_sup1 = peso_desperdicio1 * (preco_rolo1 / 1000)
            
            # Custo Material 2
            custo_mat2 = peso_peca2 * (preco_rolo2 / 1000) if usar_filamento2 else 0.0
            custo_sup2 = peso_desperdicio2 * (preco_rolo2 / 1000) if usar_filamento2 else 0.0
            
            # Produção
            custo_maquina = (horas_impressao * 1.50) if usa_energia else 0.0
            custo_producao_base = custo_mat1 + custo_sup1 + custo_mat2 + custo_sup2 + custo_maquina
            
            if usa_ams: 
                custo_producao_base *= 1.10
                
            # Lucro e Venda
            valor_lucro = custo_producao_base * (margem_lucro / 100)
            preco_venda_final = custo_producao_base + valor_lucro + mao_de_obra

            # ID do Orçamento baseado no momento exato
            id_orcamento = datetime.now().strftime("%Y%m%d%H%M")
            
            # String de resumo para o recibo/histórico
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
            
            salvar_historico(dados_atuais)
            st.session_state.ultimo_calculo = dados_atuais
            
            st.success(f"Cálculo salvo! Orçamento Nº: {id_orcamento}")
            st.info(f"**Custo:** R$ {custo_producao_base:.2f} | **Lucro:** R$ {valor_lucro:.2f} | **Acabamento:** R$ {mao_de_obra:.2f} | **Venda Final:** R$ {preco_venda_final:.2f}")
        else:
            st.error("Insira o peso de pelo menos uma peça para calcular.")

with aba_cliente:
    if 'ultimo_calculo' in st.session_state:
        dados = st.session_state.ultimo_calculo
        
        linha_acabamento = ""
        if dados['mao_de_obra'] > 0:
            linha_acabamento = f"<p><b>ACABAMENTO/PINTURA:</b> <span style='float: right;'>Incluído</span></p>"

        # HTML + CSS para emular o recibo formatado na tela
        recibo_html = f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; color: black; font-family: sans-serif;">
            <h2 style="text-align: center; color: #e30613;
