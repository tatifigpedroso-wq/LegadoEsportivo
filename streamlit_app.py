import streamlit as st
import pandas as pd
import datetime
import requests
import json

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SMEL Toledo — Sistema Municipal de Esportes e Lazer",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# DESIGN SYSTEM / CSS CORPORATIVO PERSONALIZADO (DARK SIDEBAR + CLEAN DASHBOARD)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Estilização Geral da Página */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Barra Lateral Dark Corporativa */
    [data-testid="stSidebar"] {
        background-color: #0f232e !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }
    
    /* Botões da Sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1e3a4b !important;
        color: #ffffff !important;
        border: 1px solid #335369 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #059669 !important;
        border-color: #059669 !important;
        color: #ffffff !important;
    }

    /* Cards de Navegação (Bento Grid) */
    .module-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .module-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.06);
        border-color: #cbd5e1;
    }
    .module-icon {
        font-size: 26px;
        background-color: #f1f5f9;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        margin-bottom: 14px;
    }
    .module-title {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 6px;
    }
    .module-desc {
        font-size: 13.5px;
        color: #64748b;
        line-height: 1.45;
        margin-bottom: 16px;
    }
    
    /* Cards de Métricas do Topo */
    .metric-card-top {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .metric-label-top {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.5px;
    }
    .metric-value-top {
        font-size: 28px;
        font-weight: 800;
        color: #0f232e;
        margin-top: 4px;
    }
    
    /* Header Institucional */
    .header-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXÃO COM O GOOGLE SHEETS VIA APPS SCRIPT
# ---------------------------------------------------------
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbzso112s24zmUDyHAZFGlm8BNIBp2p-_PmYbbmtkdSKhMD3OCer3A3NxvOrPvyEg492/exec"

@st.cache_data(ttl=60)
def carregar_aba(nome_aba, colunas_padrao):
    """Lê os dados da planilha em TEMPO REAL com cache de 60s para fluidez instantânea."""
    try:
        res = requests.get(f"{URL_APPS_SCRIPT}?aba={nome_aba}", timeout=10)
        if res.status_code == 200:
            dados = res.json()
            if not dados or len(dados) <= 1:
                return pd.DataFrame(columns=colunas_padrao)
            headers = [str(c).strip() for c in dados[0]]
            rows = dados[1:]
            df = pd.DataFrame(rows, columns=headers)
            for col in colunas_padrao:
                if col not in df.columns:
                    df[col] = ""
            return df[colunas_padrao]
        else:
            return pd.DataFrame(columns=colunas_padrao)
    except Exception:
        return pd.DataFrame(columns=colunas_padrao)

def salvar_no_google_sheets(nome_aba, lista_valores):
    """Envia dados via POST para salvar na planilha e limpa o cache imediatamente."""
    try:
        payload = {"aba": nome_aba, "linha": lista_valores}
        res = requests.post(URL_APPS_SCRIPT, json=payload, timeout=10)
        if res.status_code == 200:
            st.cache_data.clear()
            return True
        else:
            st.error(f"Erro ao salvar: Status {res.status_code}")
            return False
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

# ---------------------------------------------------------
# SISTEMA DE CONTROLE DE ACESSO & SENHA DO GESTOR
# ---------------------------------------------------------
def obter_senha_gestor():
    try:
        df_cfg = carregar_aba("config", ["Chave", "Valor"])
        if not df_cfg.empty:
            linha = df_cfg[df_cfg["Chave"] == "senha_gestor"]
            if not linha.empty:
                val = str(linha.iloc[-1]["Valor"]).strip()
                if val:
                    return val
    except Exception:
        pass
    return "smel2026"

senha_atual_gestor = obter_senha_gestor()

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

if "menu_selecionado" not in st.session_state:
    st.session_state.menu_selecionado = "Visão geral"

def navegar_para(modulo):
    st.session_state.menu_selecionado = modulo

# ---------------------------------------------------------
# BARRA LATERAL (SIDEBAR INSTITUCIONAL IDÊNTICA AO PROTÓTIPO)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='padding: 10px 0 20px 0;'>
        <div style='font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #94a3b8; text-transform: uppercase;'>Município de Toledo</div>
        <div style='font-size: 20px; font-weight: 800; color: #ffffff; line-height: 1.2;'>Secretaria de Esportes e Lazer</div>
        <div style='font-size: 12px; color: #38bdf8; font-weight: 600; margin-top: 4px;'>SMEL • Gestão Integrada</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Lista de Menu
    menu_itens = [
        ("Visão geral", "🏠"),
        ("Mapa de Cobertura", "🗺️"),
        ("Turmas & Escolinhas", "📋"),
        ("Agenda & Calendário", "📅"),
        ("Espaços Esportivos", "🏟️"),
        ("Equipe & Professores", "👥"),
        ("Solicitações da Equipe", "💬"),
        ("Planejamento Anual", "📑"),
        ("Ouvidoria Cidadã", "📢"),
        ("Portal de Notícias", "📰")
    ]
    
    if st.session_state.admin_logado:
        menu_itens.extend([
            ("Entidades (MROSC)", "🏢"),
            ("Projetos Estratégicos", "🚀"),
            ("Fundo Municipal (FME)", "💰")
        ])
        
    for item, icone in menu_itens:
        if st.sidebar.button(f"{icone}  {item}", key=f"btn_{item}", use_container_width=True):
            navegar_para(item)
            st.rerun()

    st.markdown("---")
    
    # Área de Acesso da Gestão
    st.subheader("🔒 Acesso da Gestão")
    if not st.session_state.admin_logado:
        senha_dig = st.text_input("Senha de Gestor:", type="password", key="input_senha_gestor")
        if st.button("Entrar no Modo Gestão"):
            if senha_dig == senha_atual_gestor:
                st.session_state.admin_logado = True
                st.success("Modo Gestão Ativado!")
                st.rerun()
            else:
                st.error("Senha incorreta.")
    else:
        st.success("🟢 Modo Gestão Ativo")
        if st.button("Sair do Modo Gestão"):
            st.session_state.admin_logado = False
            st.rerun()
            
        with st.expander("🔑 Alterar Senha do Gestor"):
            with st.form("form_trocar_senha_painel"):
                n_senha = st.text_input("Nova Senha:", type="password")
                c_senha = st.text_input("Confirmar Senha:", type="password")
                if st.form_submit_button("Salvar Nova Senha"):
                    if len(n_senha) >= 4 and n_senha == c_senha:
                        if salvar_no_google_sheets("config", ["senha_gestor", n_senha]):
                            st.success("Senha alterada na planilha!")
                            st.rerun()
                    else:
                        st.error("Senhas inválidas ou não conferem.")

    st.markdown("---")
    if st.button("🔄 Atualizar Planilha"):
        st.cache_data.clear()
        st.rerun()
        
    st.markdown("""
    <div style='font-size: 11px; color: #64748b; padding-top: 20px; line-height: 1.4;'>
        <strong>SMEL Toledo v2.4</strong><br>
        Sistema Municipal de Esportes e Lazer<br>
        Gestão Baseada em Dados
    </div>
    """, unsafe_allow_html=True)

# Coordenadas aproximadas dos bairros de Toledo
COORDENADAS_TOLEDO = {
    "Centro": [-24.7248, -53.7431],
    "Vila Nova": [-24.7150, -53.7320],
    "Jardim Panorama": [-24.7450, -53.7220],
    "Jardim Porto Alegre": [-24.7080, -53.7550],
    "Jardim Coopagro": [-24.7490, -53.7650],
    "Santa Clara": [-24.7320, -53.7120],
    "São Francisco": [-24.7180, -53.7680],
    "Vila Pioneiro": [-24.7310, -53.7280],
    "Europa / América": [-24.7410, -53.7510],
    "Gisela": [-24.7290, -53.7580],
    "Bocaina": [-24.6850, -53.8100],
    "Dez de Maio": [-24.6500, -53.8900],
    "Novo Sarandi": [-24.6200, -53.9400]
}

modulo_atual = st.session_state.menu_selecionado

# ---------------------------------------------------------
# 1. TELA: VISÃO GERAL (DASHBOARD BENTO GRID IDÊNTICO À IMAGEM)
# ---------------------------------------------------------
if modulo_atual == "Visão geral":
    # Header Principal
    st.markdown("""
    <div class="header-box">
        <div>
            <div style="font-size: 13px; font-weight: 700; color: #0284c7; text-transform: uppercase; letter-spacing: 0.5px;">Painel de Controle Municipal</div>
            <h1 style="font-size: 28px; font-weight: 800; color: #0f172a; margin: 4px 0 6px 0;">Plataforma Integrada da SMEL Toledo</h1>
            <div style="font-size: 14.5px; color: #64748b;">Acompanhamento das turmas, instalações, equipe técnica e governança do esporte toledano.</div>
        </div>
        <div style="text-align: right;">
            <span style="background-color: #ecfdf5; color: #059669; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 13px; border: 1px solid #a7f3d0;">
                ● Sistema Conectado em Tempo Real
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregamento de Métricas
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    df_fundo = carregar_aba("fundo", ["Item", "Valor", "Fonte", "Status"])
    
    total_alunos = int(pd.to_numeric(df_turmas["Alunos"], errors='coerce').sum()) if not df_turmas.empty and "Alunos" in df_turmas.columns else 0
    total_turmas = len(df_turmas)
    total_espacos = len(df_espacos)
    total_fundo = float(pd.to_numeric(df_fundo["Valor"], errors='coerce').sum()) if not df_fundo.empty and "Valor" in df_fundo.columns else 0.0

    # Linha de Métricas no Topo
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Total de Alunos</div>
            <div class="metric-value-top">{total_alunos:,}</div>
            <div style="font-size: 12px; color: #10b981; font-weight: 600; margin-top: 4px;">↑ Atendimentos Ativos</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Turmas Ofertadas</div>
            <div class="metric-value-top">{total_turmas}</div>
            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Em diversos núcleos</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Instalações Mapeadas</div>
            <div class="metric-value-top">{total_espacos}</div>
            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Ginásios, campos e piscinas</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Fundo Executado</div>
            <div class="metric-value-top">R$ {total_fundo:,.2f}</div>
            <div style="font-size: 12px; color: #0284c7; font-weight: 600; margin-top: 4px;">Recursos Aplicados</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin: 36px 0 16px 0; font-size: 20px; font-weight: 700; color: #0f172a;'>Módulos Operacionais do Sistema</h3>", unsafe_allow_html=True)

    # Grid de Módulos (Bento Grid)
    grid_col1, grid_col2, grid_col3 = st.columns(3)
    
    with grid_col1:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">🗺️</div>
                <div class="module-title">Mapa de Cobertura</div>
                <div class="module-desc">Visualize geograficamente onde estão os ginásios e turmas ativas da SMEL e identifique bairros sem atendimento.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Mapa Territorial →", key="card_mapa", use_container_width=True):
            navegar_para("Mapa de Cobertura")
            st.rerun()

    with grid_col2:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">📋</div>
                <div class="module-title">Turmas & Diário de Classe</div>
                <div class="module-desc">Acompanhe as modalidades, horários e gere a lista de chamada pronta para impressão (sem exigir celular pessoal).</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Turmas e Diários →", key="card_turmas", use_container_width=True):
            navegar_para("Turmas & Escolinhas")
            st.rerun()

    with grid_col3:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">🏟️</div>
                <div class="module-title">Espaços & Vistorias</div>
                <div class="module-desc">Diagnóstico das quadras, acessibilidade PcD e preenchimento de checklist de segurança em poucos cliques.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Gestão de Espaços →", key="card_espacos", use_container_width=True):
            navegar_para("Espaços Esportivos")
            st.rerun()

    grid_col4, grid_col5, grid_col6 = st.columns(3)
    
    with grid_col4:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">💬</div>
                <div class="module-title">Canal da Equipe</div>
                <div class="module-desc">Espaço institucional para professores e servidores solicitarem materiais ou reparos com retorno formal da gestão.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Chamados Internos →", key="card_chamados", use_container_width=True):
            navegar_para("Solicitações da Equipe")
            st.rerun()

    with grid_col5:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">📑</div>
                <div class="module-title">Planejamento Anual</div>
                <div class="module-desc">Registro prévio das competições, viagens e materiais do próximo ano para alimentar o orçamento e licitações no prazo.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Planejamento Anual →", key="card_plan", use_container_width=True):
            navegar_para("Planejamento Anual")
            st.rerun()

    with grid_col6:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">📢</div>
                <div class="module-title">Ouvidoria Cidadã</div>
                <div class="module-desc">Canal anônimo para a sociedade de Toledo enviar sugestões de modalidades, elogios e alertas sobre praças esportivas.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Consultar Ouvidoria →", key="card_ouv", use_container_width=True):
            navegar_para("Ouvidoria Cidadã")
            st.rerun()

# ---------------------------------------------------------
# 2. TELA: MAPA DE COBERTURA TERRITORIAL
# ---------------------------------------------------------
elif modulo_atual == "Mapa de Cobertura":
    st.title("🗺️ Mapa de Cobertura do Atendimento da SMEL")
    st.caption("Visualização geográfica das turmas e equipamentos esportivos em Toledo (PR)")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    
    pontos_mapa = []
    
    if not df_espacos.empty:
        for _, row in df_espacos.iterrows():
            bairro = str(row["Bairro"]).strip()
            nome = str(row["Nome"]).strip()
            tipo = str(row["Tipo"]).strip()
            
            coord = None
            for k in COORDENADAS_TOLEDO:
                if k.lower() in bairro.lower() or bairro.lower() in k.lower():
                    coord = COORDENADAS_TOLEDO[k]
                    break
            if not coord:
                coord = COORDENADAS_TOLEDO["Centro"]
                
            pontos_mapa.append({
                "Local": f"🏟️ {nome} ({tipo})",
                "Bairro": bairro,
                "Tipo": "Equipamento Esportivo",
                "lat": coord[0] + (hash(nome) % 100) * 0.0001,
                "lon": coord[1] + (hash(nome + "lon") % 100) * 0.0001
            })
            
    if not df_turmas.empty:
        for _, row in df_turmas.iterrows():
            nucleo = str(row["Núcleo"]).strip()
            mod = str(row["Modalidade"]).strip()
            
            coord = None
            for k in COORDENADAS_TOLEDO:
                if k.lower() in nucleo.lower() or nucleo.lower() in k.lower():
                    coord = COORDENADAS_TOLEDO[k]
                    break
            if not coord:
                coord = COORDENADAS_TOLEDO["Centro"]
                
            pontos_mapa.append({
                "Local": f"⚽ Turma de {mod}",
                "Bairro": nucleo,
                "Tipo": "Núcleo de Atendimento",
                "lat": coord[0] + (hash(mod + nucleo) % 100) * 0.0001,
                "lon": coord[1] + (hash(mod + nucleo + "lon") % 100) * 0.0001
            })

    if pontos_mapa:
        df_geo = pd.DataFrame(pontos_mapa)
        st.map(df_geo, latitude="lat", longitude="lon", size=30, zoom=12)
        st.subheader("📍 Locais e Atendimentos Identificados:")
        st.dataframe(df_geo[["Local", "Bairro", "Tipo"]], use_container_width=True)
    else:
        st.info("Nenhum local ou turma com endereço mapeado até o momento. Cadastre turmas e espaços com seus respectivos bairros!")

# ---------------------------------------------------------
# 3. TELA: TURMAS & ESCOLINHAS
# ---------------------------------------------------------
elif modulo_atual == "Turmas & Escolinhas":
    st.title("📋 Turmas e Escolinhas Esportivas")
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    st.dataframe(df_turmas, use_container_width=True)
    
    st.divider()
    st.subheader("📄 Diário de Classe para Impressão")
    st.caption("Gere a folha de presença oficial para uso em quadra/campo no papel sem exigir celular pessoal.")
    if not df_turmas.empty:
        opcoes_turmas = (
            df_turmas["Código"].astype(str) + " - " + 
            df_turmas["Modalidade"].astype(str) + " (" + 
            df_turmas["Núcleo"].astype(str) + ")"
        )
        turma_sel = st.selectbox("Selecione a Turma:", opcoes_turmas)
        if st.button("🖨️ Visualizar Folha de Chamada Pronta"):
            st.markdown(f"""
            ### 🏛️ PREFEITURA DE TOLEDO - SMEL
            **Diário de Presença Oficial - Turma:** {turma_sel}  
            **Mês de Referência:** ____________________ | **Professor(a):** ____________________  
            
            | Nº | Nome do Aluno | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | Observações |
            |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
            | 01 | | | | | | | | | | | | | | | | | |
            | 02 | | | | | | | | | | | | | | | | | |
            | 03 | | | | | | | | | | | | | | | | | |
            | 04 | | | | | | | | | | | | | | | | | |
            | 05 | | | | | | | | | | | | | | | | | |
            """)
            st.info("💡 Pressione Ctrl+P no navegador do computador do ginásio ou secretaria para imprimir a lista.")
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Adicionar Nova Turma (Gestão)")
        with st.form("form_turma", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            cod = col1.text_input("Código da Turma (Ex: TUR-005):")
            mod = col2.text_input("Modalidade:")
            nuc = col3.text_input("Núcleo / Bairro:")
            
            col4, col5, col6 = st.columns(3)
            hor = col4.text_input("Horário (Ex: Seg/Qua 10:00):")
            prof = col5.text_input("Professor Responsável:")
            qtd = col6.number_input("Nº de Vagas:", min_value=1, value=30)
            
            if st.form_submit_button("💾 Salvar na Planilha"):
                if salvar_no_google_sheets("turmas", [cod, mod, nuc, hor, prof, qtd]):
                    st.success("✅ Turma salva com sucesso!")
                    st.rerun()

# ---------------------------------------------------------
# 4. TELA: AGENDA & CALENDÁRIO
# ---------------------------------------------------------
elif modulo_atual == "Agenda & Calendário":
    st.title("📅 Agenda & Calendário Esportivo Oficial")
    df_agenda = carregar_aba("agenda", ["Data", "Evento", "Local", "Responsável"])
    st.dataframe(df_agenda, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Adicionar Evento na Agenda")
        with st.form("form_agenda", clear_on_submit=True):
            d_evt = st.date_input("Data do Evento:", datetime.date.today())
            n_evt = st.text_input("Nome do Evento / Torneio:")
            l_evt = st.text_input("Local:")
            r_evt = st.text_input("Responsável:")
            
            if st.form_submit_button("💾 Incluir na Agenda"):
                if salvar_no_google_sheets("agenda", [str(d_evt), n_evt, l_evt, r_evt]):
                    st.success("✅ Evento adicionado!")
                    st.rerun()

# ---------------------------------------------------------
# 5. TELA: ESPAÇOS ESPORTIVOS
# ---------------------------------------------------------
elif modulo_atual == "Espaços Esportivos":
    st.title("🏟️ Espaços Esportivos & Vistorias de Segurança")
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    st.dataframe(df_espacos, use_container_width=True)
    
    st.divider()
    st.subheader("📋 Checklist Rápido de Vistoria")
    with st.form("form_vistoria"):
        col_v1, col_v2 = st.columns(2)
        v_espaco = col_v1.text_input("Espaço Esportivo Vistoriado:")
        v_data = col_v2.date_input("Data da Vistoria:", datetime.date.today())
        
        c1, c2, c3, c4 = st.columns(4)
        ch_piso = c1.checkbox("Piso seguro")
        ch_luz = c2.checkbox("Iluminação ok")
        ch_redes = c3.checkbox("Redes/Traves firmes")
        ch_socorros = c4.checkbox("Kit Primeiros Socorros")
        
        if st.form_submit_button("Salvar Vistoria"):
            status_calc = "Boa" if (ch_piso and ch_luz and ch_redes) else "Necessita Reforma"
            if salvar_no_google_sheets("espacos", [v_espaco, "Vistoria Realizada", "Toledo", status_calc, str(v_data), "Sim" if ch_socorros else "Não"]):
                st.success("✅ Vistoria registrada!")
                st.rerun()

# ---------------------------------------------------------
# 6. TELA: EQUIPE & PROFESSORES
# ---------------------------------------------------------
elif modulo_atual == "Equipe & Professores":
    st.title("👥 Quadro de Servidores e Professores")
    df_equipe = carregar_aba("equipe", ["Nome", "Cargo", "Núcleo", "Carga Horária"])
    st.dataframe(df_equipe, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Cadastrar Integrante (Gestão)")
        with st.form("form_equipe", clear_on_submit=True):
            n_prof = st.text_input("Nome:")
            c_prof = st.text_input("Cargo:")
            nuc_prof = st.text_input("Núcleo:")
            ch_prof = st.text_input("Carga Horária:")
            
            if st.form_submit_button("💾 Salvar Servidor"):
                if salvar_no_google_sheets("equipe", [n_prof, c_prof, nuc_prof, ch_prof]):
                    st.success("✅ Servidor cadastrado!")
                    st.rerun()

# ---------------------------------------------------------
# 7. TELA: SOLICITAÇÕES DA EQUIPE (CANAL DE ESCUTA)
# ---------------------------------------------------------
elif modulo_atual == "Solicitações da Equipe":
    st.title("💬 Canal de Escuta & Solicitações da Equipe")
    st.caption("Envie demandas de materiais, reparos e sugestões com retorno da gestão.")
    
    df_chamados = carregar_aba("chamados", ["Data", "Servidor", "Núcleo", "Tipo", "Descrição", "Status", "Retorno Gestão"])
    st.dataframe(df_chamados, use_container_width=True)
    
    st.divider()
    st.subheader("➕ Abrir Novo Chamado")
    with st.form("form_novo_chamado", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        serv_nome = col_c1.text_input("Seu Nome:")
        serv_nuc = col_c2.text_input("Seu Núcleo:")
        tipo_solic = st.selectbox("Tipo:", ["Materiais (Bolas/coletes)", "Manutenção na Quadra", "Sugestão de Turma", "Outro"])
        detalhe = st.text_area("Descrição da Demanda:")
        
        if st.form_submit_button("📨 Enviar para a Gestão"):
            if salvar_no_google_sheets("chamados", [str(datetime.date.today()), serv_nome, serv_nuc, tipo_solic, detalhe, "Pendente", "Em análise"]):
                st.success("✅ Solicitação enviada!")
                st.rerun()

# ---------------------------------------------------------
# 8. TELA: PLANEJAMENTO ANUAL
# ---------------------------------------------------------
elif modulo_atual == "Planejamento Anual":
    st.title("📑 Planejamento Anual da Modalidade")
    st.caption("Previsão anual de viagens e materiais para orientar licitações prévias.")
    
    df_plan = carregar_aba("planejamento_anual", ["Modalidade", "Professor", "Competições Previstas", "Transporte/Hospedagem", "Materiais Solicitados"])
    st.dataframe(df_plan, use_container_width=True)
    
    st.divider()
    st.subheader("➕ Inserir Planejamento Anual")
    with st.form("form_planejamento_anual", clear_on_submit=True):
        col_p1, col_p2 = st.columns(2)
        p_mod = col_p1.text_input("Modalidade:")
        p_prof = col_p2.text_input("Professor:")
        p_comp = st.text_area("Competições Previstas (Nome, Cidade, Mês):")
        p_transp = st.text_area("Transporte/Hospedagem necessária:")
        p_materiais = st.text_area("Materiais para os 12 meses:")
        
        if st.form_submit_button("💾 Salvar Planejamento"):
            if salvar_no_google_sheets("planejamento_anual", [p_mod, p_prof, p_comp, p_transp, p_materiais]):
                st.success("✅ Planejamento registrado!")
                st.rerun()

# ---------------------------------------------------------
# 9. TELA: OUVIDORIA CIDADÃ
# ---------------------------------------------------------
elif modulo_atual == "Ouvidoria Cidadã":
    st.title("📢 Ouvidoria Cidadã & Sugestões")
    st.caption("Canal anônimo para a população de Toledo sugerir modalidades ou alertar reformas.")
    
    with st.form("form_ouvidoria", clear_on_submit=True):
        tipo_ouvidoria = st.selectbox("Tipo:", ["Sugestão de Turma", "Alerta de Problema em Praça", "Elogio", "Outro"])
        bairro_cidadao = st.text_input("Bairro:")
        mensagem_cidadao = st.text_area("Mensagem:")
        
        if st.form_submit_button("🚀 Enviar de Forma Anônima"):
            if salvar_no_google_sheets("ouvidoria", [str(datetime.date.today()), tipo_ouvidoria, bairro_cidadao, mensagem_cidadao, "Pendente"]):
                st.success("✅ Manifestação recebida!")
                st.rerun()
                
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("🔍 Painel de Manifestações (Gestão)")
        df_ouv = carregar_aba("ouvidoria", ["Data", "Tipo", "Bairro", "Mensagem", "Status"])
        st.dataframe(df_ouv, use_container_width=True)

# ---------------------------------------------------------
# 10. TELA: PORTAL DE NOTÍCIAS
# ---------------------------------------------------------
elif modulo_atual == "Portal de Notícias":
    st.title("📰 Portal da Transparência & Notícias")
    df_noticias = carregar_aba("publicacoes", ["Data", "Título", "Categoria", "Conteúdo"])
    
    if st.session_state.admin_logado:
        st.subheader("➕ Nova Publicação")
        with st.form("form_noticia", clear_on_submit=True):
            tit = st.text_input("Título:")
            cat = st.selectbox("Categoria:", ["Edital / Evento", "Notícia", "Obras", "Aviso"])
            cont = st.text_area("Conteúdo:")
            if st.form_submit_button("🚀 Publicar"):
                if salvar_no_google_sheets("publicacoes", [str(datetime.date.today()), tit, cat, cont]):
                    st.success("✅ Publicado!")
                    st.rerun()
        st.divider()
        
    if not df_noticias.empty:
        for _, item in df_noticias.iterrows():
            with st.expander(f"📌 [{item['Data']}] {item['Título']} ({item['Categoria']})"):
                st.write(item["Conteúdo"])
    else:
        st.info("Nenhuma publicação ativa.")

# ---------------------------------------------------------
# 11. MÓDULOS DE GESTÃO EXCLUSIVOS (MROSC, PROJETOS, FUNDO)
# ---------------------------------------------------------
elif modulo_atual == "Entidades (MROSC)":
    st.title("🏢 Entidades & Associações Parceiras (MROSC)")
    df_entidades = carregar_aba("entidades", ["Entidade", "CNPJ", "Presidente", "Status"])
    st.dataframe(df_entidades, use_container_width=True)
    with st.form("form_entidade", clear_on_submit=True):
        ent_nome = st.text_input("Nome da Associação:")
        ent_cnpj = st.text_input("CNPJ:")
        ent_pres = st.text_input("Presidente:")
        ent_stat = st.selectbox("Status:", ["Regular", "Em Análise", "Pendente"])
        if st.form_submit_button("💾 Salvar Entidade"):
            if salvar_no_google_sheets("entidades", [ent_nome, ent_cnpj, ent_pres, ent_stat]):
                st.success("✅ Entidade registrada!")
                st.rerun()

elif modulo_atual == "Projetos Estratégicos":
    st.title("🚀 Projetos Estratégicos")
    df_projetos = carregar_aba("projetos", ["Projeto", "Orçamento", "Beneficiários", "Execução"])
    st.dataframe(df_projetos, use_container_width=True)
    with st.form("form_projeto", clear_on_submit=True):
        p_nome = st.text_input("Nome do Projeto:")
        p_orc = st.text_input("Orçamento:")
        p_ben = st.number_input("Beneficiários:", min_value=1, value=100)
        p_exe = st.text_input("Execução (%):")
        if st.form_submit_button("💾 Salvar Projeto"):
            if salvar_no_google_sheets("projetos", [p_nome, p_orc, p_ben, p_exe]):
                st.success("✅ Projeto registrado!")
                st.rerun()

elif modulo_atual == "Fundo Municipal (FME)":
    st.title("💰 Fundo Municipal do Esporte (FME)")
    df_fundo = carregar_aba("fundo", ["Item", "Valor", "Fonte", "Status"])
    st.dataframe(df_fundo, use_container_width=True)
    with st.form("form_fundo", clear_on_submit=True):
        f_item = st.text_input("Item de Despesa:")
        f_val = st.number_input("Valor (R$):", min_value=0.0, value=1000.0)
        f_fon = st.selectbox("Fonte:", ["FME Próprio", "Emenda Parlamentar", "Lei de Incentivo", "Convênio"])
        f_st = st.selectbox("Status:", ["Empenhado", "Em Execução", "Pago"])
        if st.form_submit_button("💾 Salvar Lançamento"):
            if salvar_no_google_sheets("fundo", [f_item, f_val, f_fon, f_st]):
                st.success("✅ Lançamento gravado!")
                st.rerun()
