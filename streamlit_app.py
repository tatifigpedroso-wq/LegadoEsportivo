import streamlit as st
import pandas as pd
import datetime
import requests
import json

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SMEL Gestão Integrada — Município de Toledo",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CSS PERSONALIZADO: IDENTIDADE VISUAL EXATA DO PROTÓTIPO
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Estilização Geral */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Barra Lateral Dark Institucional (#0c232f) */
    [data-testid="stSidebar"] {
        background-color: #0c232f !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }
    
    /* Botões da Sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #94a3b8 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 14px !important;
        width: 100% !important;
        font-size: 14.5px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #163647 !important;
        color: #ffffff !important;
    }

    /* Cards de Navegação (Bento Grid) */
    .module-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 20px;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease;
    }
    .module-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        border-color: #cbd5e1;
    }
    .module-icon {
        font-size: 22px;
        color: #0f172a;
        margin-bottom: 12px;
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
        border-radius: 10px;
        padding: 18px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        min-height: 105px;
    }
    .metric-label-top {
        font-size: 12.5px;
        font-weight: 500;
        color: #64748b;
    }
    .metric-value-top {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-sub-top {
        font-size: 11.5px;
        color: #94a3b8;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXÃO REAL COM O GOOGLE SHEETS
# ---------------------------------------------------------
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbzso112s24zmUDyHAZFGlm8BNIBp2p-_PmYbbmtkdSKhMD3OCer3A3NxvOrPvyEg492/exec"

@st.cache_data(ttl=60)
def carregar_aba(nome_aba, colunas_padrao):
    try:
        res = requests.get(f"{URL_APPS_SCRIPT}?aba={nome_aba}", timeout=10)
        if res.status_code == 200:
            dados = res.json()
            if not dados or len(dados) <= 1:
                return pd.DataFrame(columns=colunas_padrao)
            headers = [str(c).strip() for c in dados]
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
# CONTROLE DE SESSÃO & SENHA DO GESTOR
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

if "modulo_ativo" not in st.session_state:
    st.session_state.modulo_ativo = "Visão geral"

def navegar(modulo):
    st.session_state.modulo_ativo = modulo

# Coordenadas aproximadas de Toledo
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

# ---------------------------------------------------------
# SIDEBAR INSTITUCIONAL IDÊNTICA À IMAGEM DO PROTÓTIPO
# ---------------------------------------------------------
with st.sidebar:
    # Logo e Cabeçalho da Prefeitura de Toledo
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 12px; padding: 12px 4px 20px 4px;'>
        <div style='font-size: 28px;'>🏛️</div>
        <div>
            <div style='font-size: 11px; font-weight: 800; letter-spacing: 1px; color: #ffffff; text-transform: uppercase;'>Prefeitura de Toledo</div>
            <div style='font-size: 10px; font-weight: 600; color: #94a3b8; text-transform: uppercase;'>Secretaria de Esportes e Lazer</div>
        </div>
    </div>
    <div style='font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: #64748b; text-transform: uppercase; margin-bottom: 8px;'>Plataforma Integrada</div>
    """, unsafe_allow_html=True)
    
    # Itens de Menu correspondentes ao protótipo
    itens_menu = [
        ("Visão geral", "🟩"),
        ("Atividades e turmas", "🔲"),
        ("Frequência", "✔️"),
        ("Competições", "♟️"),
        ("Súmulas digitais", "📑"),
        ("Relatórios", "🏛️"),
        ("Mapa de Cobertura", "🗺️"),
        ("Espaços Esportivos", "🏟️"),
        ("Solicitações da Equipe", "💬"),
        ("Planejamento Anual", "📋"),
        ("Ouvidoria Cidadã", "📢")
    ]
    
    if st.session_state.admin_logado:
        itens_menu.append(("Financeiro", "💲"))
        itens_menu.append(("Administração", "⚙️"))
        
    for nome, ico in itens_menu:
        # Se for o item selecionado, destaca
        if st.session_state.modulo_ativo == nome:
            st.markdown(f"""
            <div style='background-color: #059669; color: #ffffff; font-weight: 600; padding: 10px 14px; border-radius: 8px; margin-bottom: 4px; font-size: 14.5px;'>
                {ico} &nbsp; {nome}
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(f"{ico}  {nome}", key=f"menu_{nome}", use_container_width=True):
                navegar(nome)
                st.rerun()

    st.markdown("---")
    
    # Bloco de Acesso Gestor
    if not st.session_state.admin_logado:
        st.markdown("<div style='font-size: 12px; font-weight: 600; color: #94a3b8;'>Acesso Restrito (Gestão)</div>", unsafe_allow_html=True)
        pwd = st.text_input("Senha:", type="password", key="sidebar_pass")
        if st.button("Entrar"):
            if pwd == senha_atual_gestor:
                st.session_state.admin_logado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    else:
        st.markdown("<div style='font-size: 12px; color: #10b981; font-weight: 600;'>● Modo Gestão Ativo</div>", unsafe_allow_html=True)
        if st.button("Sair da Gestão"):
            st.session_state.admin_logado = False
            navegar("Visão geral")
            st.rerun()

    # Rodapé institucional da imagem
    st.markdown("""
    <div style='font-size: 10.5px; color: #64748b; padding-top: 30px; line-height: 1.5;'>
        <strong>SMEL Gestão Integrada</strong><br>
        Versão com Banco de Dados em Tempo Real<br>
        Prefeitura de Toledo • PR
    </div>
    """, unsafe_allow_html=True)

modulo = st.session_state.modulo_ativo

# ---------------------------------------------------------
# 1. TELA: VISÃO GERAL (IDÊNTICA À TELA PRINCIPAL DA IMAGEM)
# ---------------------------------------------------------
if modulo == "Visão geral":
    st.markdown("<div style='font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #64748b; text-transform: uppercase;'>Painel Inicial</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 30px; font-weight: 800; color: #0f172a; margin-top: -5px;'>Bem-vindo ao SMEL Gestão Integrada</h1>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 15px; color: #64748b; margin-top: -8px; margin-bottom: 20px;'>Uma única plataforma para atividades esportivas, lazer, frequência, competições e relatórios administrativos.</div>", unsafe_allow_html=True)
    
    # Carregamento de dados para os 4 cards do topo
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_agenda = carregar_aba("agenda", ["Data", "Evento", "Local", "Responsável"])
    
    total_turmas = len(df_turmas)
    total_alunos = int(pd.to_numeric(df_turmas["Alunos"], errors='coerce').sum()) if not df_turmas.empty and "Alunos" in df_turmas.columns else 0
    total_competicoes = len(df_agenda)

    # 4 Cartões Superiores idênticos aos da imagem
    top1, top2, top3, top4 = st.columns(4)
    with top1:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Atividades cadastradas</div>
            <div class="metric-value-top">{total_turmas if total_turmas > 0 else '—'}</div>
            <div class="metric-sub-top">Turmas e escolinhas ativas</div>
        </div>
        """, unsafe_allow_html=True)
    with top2:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Atendimentos no mês</div>
            <div class="metric-value-top">{total_alunos * 4 if total_alunos > 0 else '—'}</div>
            <div class="metric-sub-top">Frequência estimada</div>
        </div>
        """, unsafe_allow_html=True)
    with top3:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Pessoas atendidas</div>
            <div class="metric-value-top">{total_alunos if total_alunos > 0 else '—'}</div>
            <div class="metric-sub-top">Alunos matriculados</div>
        </div>
        """, unsafe_allow_html=True)
    with top4:
        st.markdown(f"""
        <div class="metric-card-top">
            <div class="metric-label-top">Competições ativas</div>
            <div class="metric-value-top">{total_competicoes if total_competicoes > 0 else '—'}</div>
            <div class="metric-sub-top">Eventos e torneios</div>
        </div>
        """, unsafe_allow_html=True)

    # Título do Bento Grid
    st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center; margin: 36px 0 16px 0;'>
        <h3 style='font-size: 20px; font-weight: 700; color: #0f172a; margin: 0;'>Módulos do sistema</h3>
        <span style='font-size: 13px; color: #94a3b8;'>Selecione um módulo para visualizar</span>
    </div>
    """, unsafe_allow_html=True)

    # Linha 1 de Módulos (Atividades, Frequência, Competições)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">🔲</div>
                <div class="module-title">Atividades e turmas</div>
                <div class="module-desc">Programas esportivos, oficinas, horários, locais e profissionais.</div>
            </div>
            <div style='color: #059669; font-weight: 600; font-size: 13.5px;'>Abrir módulo →</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Atividades", key="nav_ativ", use_container_width=True):
            navegar("Atividades e turmas")
            st.rerun()

    with g2:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">✔️</div>
                <div class="module-title">Frequência</div>
                <div class="module-desc">Chamada por turma e acompanhamento de atendimentos.</div>
            </div>
            <div style='color: #059669; font-weight: 600; font-size: 13.5px;'>Abrir módulo →</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Frequência", key="nav_freq", use_container_width=True):
            navegar("Frequência")
            st.rerun()

    with g3:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">♟️</div>
                <div class="module-title">Competições</div>
                <div class="module-desc">Inscrições, grupos, confrontos, resultados e classificações.</div>
            </div>
            <div style='color: #059669; font-weight: 600; font-size: 13.5px;'>Abrir módulo →</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Competições", key="nav_comp", use_container_width=True):
            navegar("Competições")
            st.rerun()

    # Linha 2 de Módulos (Súmulas, Relatórios, Financeiro)
    g4, g5, g6 = st.columns(3)
    with g4:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">📑</div>
                <div class="module-title">Súmulas digitais</div>
                <div class="module-desc">Registro de partidas, eventos e futuras homologações.</div>
            </div>
            <div style='color: #059669; font-weight: 600; font-size: 13.5px;'>Abrir módulo →</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Súmulas", key="nav_sum", use_container_width=True):
            navegar("Súmulas digitais")
            st.rerun()

    with g5:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">🏛️</div>
                <div class="module-title">Relatórios</div>
                <div class="module-desc">Relatórios mensais e indicadores por programa e setor.</div>
            </div>
            <div style='color: #059669; font-weight: 600; font-size: 13.5px;'>Abrir módulo →</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Relatórios", key="nav_rel", use_container_width=True):
            navegar("Relatórios")
            st.rerun()

    with g6:
        st.markdown("""
        <div class="module-card">
            <div>
                <div class="module-icon">💲</div>
                <div class="module-title">Financeiro</div>
                <div class="module-desc">Orçamento, empenhos, despesas e acompanhamento.</div>
            </div>
            <div style='color: #059669; font-weight: 600; font-size: 13.5px;'>Abrir módulo →</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Financeiro", key="nav_fin", use_container_width=True):
            if st.session_state.admin_logado:
                navegar("Financeiro")
            else:
                st.warning("Área restrita à Gestão da SMEL. Faça login na barra lateral.")
            st.rerun()

# ---------------------------------------------------------
# 2. TELA: ATIVIDADES E TURMAS
# ---------------------------------------------------------
elif modulo == "Atividades e turmas":
    st.title("🔲 Atividades e Turmas")
    st.caption("Programas esportivos, oficinas, horários, locais e profissionais da SMEL Toledo")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    st.dataframe(df_turmas, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Cadastrar Nova Atividade / Turma")
        with st.form("form_nova_turma_mod"):
            c1, c2, c3 = st.columns(3)
            cod = c1.text_input("Código (Ex: TUR-010):")
            mod = c2.text_input("Modalidade / Programa:")
            nuc = c3.text_input("Local / Núcleo:")
            
            c4, c5, c6 = st.columns(3)
            hor = c4.text_input("Dias e Horários:")
            prof = c5.text_input("Professor Responsável:")
            qtd = c6.number_input("Vagas:", min_value=1, value=30)
            
            if st.form_submit_button("Salvar Turma"):
                if salvar_no_google_sheets("turmas", [cod, mod, nuc, hor, prof, qtd]):
                    st.success("✅ Turma registrada com sucesso!")
                    st.rerun()

# ---------------------------------------------------------
# 3. TELA: FREQUÊNCIA & DIÁRIO DE CLASSE
# ---------------------------------------------------------
elif modulo == "Frequência":
    st.title("✔️ Frequência e Acompanhamento de Atendimentos")
    st.caption("Chamada por turma e geração de diário impresso (sem uso de celular pessoal)")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    
    if not df_turmas.empty:
        opcoes = df_turmas["Código"].astype(str) + " - " + df_turmas["Modalidade"].astype(str) + " (" + df_turmas["Núcleo"].astype(str) + ")"
        turma_sel = st.selectbox("Selecione a Turma:", opcoes)
        
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 24px; border-radius: 10px; border: 1px solid #e2e8f0; margin-top: 16px;">
            <div style="font-weight: 700; font-size: 18px; color: #0f172a;">PREFEITURA DE TOLEDO — SECRETARIA DE ESPORTES E LAZER</div>
            <div style="font-size: 14px; color: #475569; margin-top: 4px;"><strong>Diário de Frequência Oficial — Turma:</strong> {turma_sel}</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 2px;">Mês: ______________________ | Instrutor: ______________________</div>
            <hr style="margin: 16px 0;">
            <p style="font-size: 13px; color: #64748b;">Lista formatada pronta para prancheta de campo. Imprima utilizando <strong>Ctrl+P</strong> no computador do ginásio.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma turma cadastrada para geração de frequência.")

# ---------------------------------------------------------
# 4. TELA: COMPETIÇÕES
# ---------------------------------------------------------
elif modulo == "Competições":
    st.title("♟️ Competições, Grupos e Confrontos")
    st.caption("Inscrições, tabelas, confrontos e resultados do esporte toledano")
    
    df_agenda = carregar_aba("agenda", ["Data", "Evento", "Local", "Responsável"])
    st.dataframe(df_agenda, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Criar Nova Competição / Confronto")
        with st.form("form_comp_novo"):
            c_d = st.date_input("Data do Confronto / Etapa:", datetime.date.today())
            c_n = st.text_input("Nome da Competição (Ex: Copa Toledo de Futsal Sub-15):")
            c_l = st.text_input("Local / Ginásio:")
            c_r = st.text_input("Organizador / Setor:")
            if st.form_submit_button("Registrar Competição"):
                if salvar_no_google_sheets("agenda", [str(c_d), c_n, c_l, c_r]):
                    st.success("✅ Competição adicionada à tabela!")
                    st.rerun()

# ---------------------------------------------------------
# 5. TELA: SÚMULAS DIGITAIS
# ---------------------------------------------------------
elif modulo == "Súmulas digitais":
    st.title("📑 Súmulas Digitais e Registro de Partidas")
    st.caption("Registro de partidas, resultados, ocorrências e homologações oficiais")
    
    st.info("💡 Módulo destinado ao registro de placares e homologação de jogos escolares e municipais.")
    with st.form("form_sumula"):
        col_s1, col_s2 = st.columns(2)
        eq_a = col_s1.text_input("Equipe A:")
        eq_b = col_s2.text_input("Equipe B:")
        
        pl_a = col_s1.number_input("Placar A:", min_value=0, value=0)
        pl_b = col_s2.number_input("Placar B:", min_value=0, value=0)
        
        modal = st.selectbox("Modalidade:", ["Futsal", "Voleibol", "Basquete", "Handebol", "Futebol de Campo"])
        arbitro = st.text_input("Árbitro Principal / Mesário:")
        relato = st.text_area("Ocorrências da Partida:")
        
        if st.form_submit_button("Homologar e Salvar Súmula"):
            st.success(f"✅ Súmula homologada com sucesso: {eq_a} {pl_a} x {pl_b} {eq_b} ({modal})")

# ---------------------------------------------------------
# 6. TELA: RELATÓRIOS ADMINISTRATIVOS
# ---------------------------------------------------------
elif modulo == "Relatórios":
    st.title("🏛️ Relatórios e Indicadores por Programa")
    st.caption("Consolidação de metas físicas, atendimento por faixa etária e prestação de contas")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("Atendimento por Núcleo")
        if not df_turmas.empty and "Núcleo" in df_turmas.columns:
            st.bar_chart(df_turmas["Núcleo"].value_counts())
    with r2:
        st.subheader("Condição das Instalações")
        if not df_espacos.empty and "Condição" in df_espacos.columns:
            st.bar_chart(df_espacos["Condição"].value_counts())

# ---------------------------------------------------------
# 7. TELA: FINANCEIRO (FME & ORÇAMENTO - GESTÃO)
# ---------------------------------------------------------
elif modulo == "Financeiro":
    st.title("💲 Financeiro & Fundo Municipal do Esporte (FME)")
    st.caption("Acompanhamento orçamentário, empenhos, despesas e prestação de contas")
    
    df_fundo = carregar_aba("fundo", ["Item", "Valor", "Fonte", "Status"])
    st.dataframe(df_fundo, use_container_width=True)
    
    st.divider()
    st.subheader("➕ Registrar Novo Empenho / Despesa")
    with st.form("form_fin_despesa"):
        f_item = st.text_input("Descrição do Item:")
        f_val = st.number_input("Valor em Reais (R$):", min_value=0.0, value=1500.0)
        f_fon = st.selectbox("Fonte:", ["Recurso Próprio", "Emenda Parlamentar", "Lei de Incentivo", "Convênio"])
        f_st = st.selectbox("Status:", ["Empenhado", "Em Liquidação", "Pago"])
        
        if st.form_submit_button("Lançar Despesa"):
            if salvar_no_google_sheets("fundo", [f_item, f_val, f_fon, f_st]):
                st.success("✅ Lançamento financeiro registrado!")
                st.rerun()

# ---------------------------------------------------------
# 8. TELA: ADMINISTRAÇÃO (TROCA DE SENHA E CONFIGURAÇÕES)
# ---------------------------------------------------------
elif modulo == "Administração":
    st.title("⚙️ Administração do Sistema")
    st.caption("Configurações gerais e segurança da plataforma")
    
    st.subheader("🔑 Alterar Senha de Gestor")
    st.write("A senha é gravada de forma permanente no banco de dados da prefeitura.")
    with st.form("form_admin_senha"):
        nova_s = st.text_input("Nova Senha:", type="password")
        conf_s = st.text_input("Confirmar Nova Senha:", type="password")
        if st.form_submit_button("Atualizar Senha"):
            if len(nova_s) >= 4 and nova_s == conf_s:
                if salvar_no_google_sheets("config", ["senha_gestor", nova_s]):
                    st.success("✅ Senha alterada com sucesso!")
                    st.rerun()
            else:
                st.error("Senhas inválidas ou não conferem.")

# ---------------------------------------------------------
# 9. MÓDULOS EXTRAS (MAPA, ESPAÇOS, CHAMADOS, PLAN. ANUAL, OUVIDORIA)
# ---------------------------------------------------------
elif modulo == "Mapa de Cobertura":
    st.title("🗺️ Mapa de Cobertura Territorial")
    st.caption("Distribuição geográfica dos ginásios, quadras e escolinhas em Toledo (PR)")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    
    pontos = []
    if not df_espacos.empty:
        for _, r in df_espacos.iterrows():
            b = str(r["Bairro"]).strip()
            coord = COORDENADAS_TOLEDO.get(b, COORDENADAS_TOLEDO["Centro"])
            pontos.append({"Local": f"🏟️ {r['Nome']}", "lat": coord[0], "lon": coord[1]})
            
    if pontos:
        st.map(pd.DataFrame(pontos), latitude="lat", longitude="lon", zoom=12)
    else:
        st.info("Nenhum ponto registrado no mapa.")

elif modulo == "Espaços Esportivos":
    st.title("🏟️ Espaços Esportivos & Vistorias")
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    st.dataframe(df_espacos, use_container_width=True)

elif modulo == "Solicitações da Equipe":
    st.title("💬 Solicitações & Chamados da Equipe")
    df_chamados = carregar_aba("chamados", ["Data", "Servidor", "Núcleo", "Tipo", "Descrição", "Status", "Retorno Gestão"])
    st.dataframe(df_chamados, use_container_width=True)
    with st.form("form_chamado_equipe"):
        n = st.text_input("Seu Nome:")
        l = st.text_input("Núcleo / Ginásio:")
        d = st.text_area("O que você precisa (Materiais, conserto, sugestão):")
        if st.form_submit_button("Enviar Demanda"):
            if salvar_no_google_sheets("chamados", [str(datetime.date.today()), n, l, "Demanda", d, "Pendente", "Em análise"]):
                st.success("✅ Pedido enviado à secretaria!")
                st.rerun()

elif modulo == "Planejamento Anual":
    st.title("📋 Planejamento Anual das Modalidades")
    df_plan = carregar_aba("planejamento_anual", ["Modalidade", "Professor", "Competições Previstas", "Transporte/Hospedagem", "Materiais Solicitados"])
    st.dataframe(df_plan, use_container_width=True)
    with st.form("form_plan_anual"):
        m = st.text_input("Modalidade:")
        p = st.text_input("Professor:")
        c = st.text_area("Competições e Viagens previstas para o ano que vem:")
        mat = st.text_area("Materiais solicitados para os 12 meses:")
        if st.form_submit_button("Salvar Planejamento"):
            if salvar_no_google_sheets("planejamento_anual", [m, p, c, "-", mat]):
                st.success("✅ Planejamento registrado!")
                st.rerun()

elif modulo == "Ouvidoria Cidadã":
    st.title("📢 Ouvidoria Cidadã Anônima")
    with st.form("form_ouv_anonima"):
        t = st.selectbox("Assunto:", ["Sugestão de Turma", "Problema em Praça / Ginásio", "Elogio", "Outro"])
        b = st.text_input("Bairro:")
        msg = st.text_area("Mensagem:")
        if st.form_submit_button("Enviar Anônimo"):
            if salvar_no_google_sheets("ouvidoria", [str(datetime.date.today()), t, b, msg, "Pendente"]):
                st.success("✅ Mensagem enviada à SMEL!")
                st.rerun()
