import streamlit as st
import pandas as pd
import datetime
import requests

# ---------------------------------------------------------
# CONFIGURAÇÃO DO APPS SCRIPT (LEITURA E GRAVAÇÃO EM TEMPO REAL)
# ---------------------------------------------------------
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbzso112s24zmUDyHAZFGlm8BNIBp2p-_PmYbbmtkdSKhMD3OCer3A3NxvOrPvyEg492/exec"

def carregar_aba(nome_aba, colunas_padrao):
    """Lê os dados da planilha em TEMPO REAL diretamente via Google Apps Script (sem cache do Google)."""
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
    """Envia os dados via POST para o Google Apps Script gravar na planilha."""
    try:
        payload = {
            "aba": nome_aba,
            "linha": lista_valores
        }
        res = requests.post(URL_APPS_SCRIPT, json=payload, timeout=10)
        if res.status_code == 200:
            st.cache_data.clear()
            return True
        else:
            st.error(f"⚠️ Erro ao gravar (Status {res.status_code})")
            return False
    except Exception as e:
        st.error(f"⚠️ Falha na conexão: {e}")
        return False

# Configuração da Página
st.set_page_config(
    page_title="SMEL Toledo — Gestão da Secretaria de Esportes e Lazer",
    page_icon="⚽",
    layout="wide"
)

# ---------------------------------------------------------
# AUTENTICAÇÃO DE GESTOR
# ---------------------------------------------------------
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# ---------------------------------------------------------
# BARRA LATERAL - NAVEGAÇÃO E LOGIN
# ---------------------------------------------------------
st.sidebar.title("🏛️ SMEL Toledo")
st.sidebar.caption("Secretaria Municipal de Esportes e Lazer")
st.sidebar.markdown("---")

st.sidebar.subheader("🔒 Acesso da Equipe")

if not st.session_state.admin_logado:
    senha_input = st.sidebar.text_input("Senha de Gestor:", type="password")
    if st.sidebar.button("Entrar no Modo Edição"):
        if senha_input == "smel2026":
            st.session_state.admin_logado = True
            st.sidebar.success("✅ Modo Gestão Ativado!")
            st.rerun()
        else:
            st.sidebar.error("❌ Senha incorreta.")
else:
    st.sidebar.success("🟢 Modo Gestão Ativo")
    if st.sidebar.button("Sair do Modo Gestão"):
        st.session_state.admin_logado = False
        st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Atualizar Dados da Planilha"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Módulos do Sistema:",
    [
        "📊 Painel Executivo",
        "📋 Turmas & Escolinhas",
        "📅 Agenda & Calendário",
        "🏟️ Espaços Esportivos",
        "👥 Equipe & Professores",
        "🏢 Entidades & Associações",
        "🚀 Projetos & Programas",
        "💰 Fundo Municipal do Esporte",
        "📢 Portal da Transparência & Notícias"
    ]
)

# ---------------------------------------------------------
# 1. PAINEL EXECUTIVO
# ---------------------------------------------------------
if menu == "📊 Painel Executivo":
    st.title("📊 Painel Executivo — SMEL Toledo")
    st.caption("Resumo dinâmico da gestão municipal do esporte")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    df_fundo = carregar_aba("fundo", ["Item", "Valor", "Fonte", "Status"])
    df_projetos = carregar_aba("projetos", ["Projeto", "Orçamento", "Beneficiários", "Execução"])

    total_alunos = int(pd.to_numeric(df_turmas["Alunos"], errors='coerce').sum()) if not df_turmas.empty and "Alunos" in df_turmas.columns else 0
    total_turmas = len(df_turmas)
    total_espacos = len(df_espacos)
    total_fundo = float(pd.to_numeric(df_fundo["Valor"], errors='coerce').sum()) if not df_fundo.empty and "Valor" in df_fundo.columns else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Alunos", f"{total_alunos} Atendidos")
    col2.metric("Turmas Ativas", f"{total_turmas} Turmas")
    col3.metric("Espaços Mapeados", f"{total_espacos} Equipamentos")
    col4.metric("Fundo Executado", f"R$ {total_fundo:,.2f}")
    
    st.divider()
    st.subheader("📌 Resumo dos Projetos Ativos")
    st.dataframe(df_projetos, use_container_width=True)

# ---------------------------------------------------------
# 2. TURMAS & ESCOLINHAS
# ---------------------------------------------------------
elif menu == "📋 Turmas & Escolinhas":
    st.title("📋 Turmas e Escolinhas Esportivas")
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    st.dataframe(df_turmas, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Adicionar Nova Turma")
        with st.form("form_turma", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            cod = col1.text_input("Código da Turma (Ex: TUR-005):")
            mod = col2.text_input("Modalidade:")
            nuc = col3.text_input("Núcleo / Bairro:")
            
            col4, col5, col6 = st.columns(3)
            hor = col4.text_input("Horário (Ex: Seg/Qua 10:00):")
            prof = col5.text_input("Professor Responsável:")
            qtd = col6.number_input("Nº de Alunos Vagas:", min_value=1, value=30)
            
            if st.form_submit_button("💾 Salvar na Planilha"):
                if salvar_no_google_sheets("turmas", [cod, mod, nuc, hor, prof, qtd]):
                    st.success("✅ Turma salva com sucesso na planilha!")
                    st.rerun()

# ---------------------------------------------------------
# 3. AGENDA & CALENDÁRIO
# ---------------------------------------------------------
elif menu == "📅 Agenda & Calendário":
    st.title("📅 Agenda & Calendário Esportivo")
    df_agenda = carregar_aba("agenda", ["Data", "Evento", "Local", "Responsável"])
    st.dataframe(df_agenda, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Adicionar Evento na Agenda")
        with st.form("form_agenda", clear_on_submit=True):
            d_evt = st.date_input("Data do Evento:", datetime.date.today())
            n_evt = st.text_input("Nome do Evento / Campeonato:")
            l_evt = st.text_input("Local de Realização:")
            r_evt = st.text_input("Organização / Responsável:")
            
            if st.form_submit_button("💾 Incluir na Agenda Pública"):
                if salvar_no_google_sheets("agenda", [str(d_evt), n_evt, l_evt, r_evt]):
                    st.success("✅ Evento adicionado à agenda!")
                    st.rerun()

# ---------------------------------------------------------
# 4. ESPAÇOS ESPORTIVOS
# ---------------------------------------------------------
elif menu == "🏟️ Espaços Esportivos":
    st.title("🏟️ Espaços Esportivos Municipais")
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    st.dataframe(df_espacos, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Novo Equipamento Esportivo")
        with st.form("form_espaco", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            n_esp = col_a.text_input("Nome do Espaço:")
            t_esp = col_a.selectbox("Tipo:", ["Ginásio Poliesportivo", "Quadra Poliesportiva", "Campo de Futebol", "Complexo / Piscina", "Pista de Atletismo"])
            b_esp = col_a.text_input("Bairro:")
            c_esp = col_b.selectbox("Condição:", ["Boa", "Regular", "Necessita Reforma", "Interditado"])
            v_esp = col_b.date_input("Data da Vistoria:", datetime.date.today())
            a_esp = col_b.selectbox("Acessível PcD:", ["Sim", "Parcial", "Não"])
            
            if st.form_submit_button("💾 Cadastrar Espaço"):
                if salvar_no_google_sheets("espacos", [n_esp, t_esp, b_esp, c_esp, str(v_esp), a_esp]):
                    st.success("✅ Espaço cadastrado com sucesso!")
                    st.rerun()

# ---------------------------------------------------------
# 5. EQUIPE & PROFESSORES
# ---------------------------------------------------------
elif menu == "👥 Equipe & Professores":
    st.title("👥 Quadro de Servidores e Professores")
    df_equipe = carregar_aba("equipe", ["Nome", "Cargo", "Núcleo", "Carga Horária"])
    st.dataframe(df_equipe, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Cadastrar Novo Integrante da Equipe")
        with st.form("form_equipe", clear_on_submit=True):
            n_prof = st.text_input("Nome do Servidor/Professor:")
            c_prof = st.text_input("Cargo / Função:")
            nuc_prof = st.text_input("Núcleo Principal de Atuação:")
            ch_prof = st.text_input("Carga Horária (Ex: 40h/sem):")
            
            if st.form_submit_button("💾 Salvar Servidor"):
                if salvar_no_google_sheets("equipe", [n_prof, c_prof, nuc_prof, ch_prof]):
                    st.success("✅ Servidor cadastrado!")
                    st.rerun()

# ---------------------------------------------------------
# 6. ENTIDADES & ASSOCIAÇÕES
# ---------------------------------------------------------
elif menu == "🏢 Entidades & Associações":
    st.title("🏢 Entidades e Ligas Esportivas Parceiras")
    df_entidades = carregar_aba("entidades", ["Entidade", "CNPJ", "Presidente", "Status"])
    st.dataframe(df_entidades, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Cadastrar Entidade Parceira")
        with st.form("form_entidade", clear_on_submit=True):
            ent_nome = st.text_input("Nome da Associação / Liga:")
            ent_cnpj = st.text_input("CNPJ:")
            ent_pres = st.text_input("Presidente / Responsável:")
            ent_stat = st.selectbox("Status Cadastral:", ["Regular (Certificada)", "Em Análise", "Pendente de Documentação"])
            
            if st.form_submit_button("💾 Registrar Entidade"):
                if salvar_no_google_sheets("entidades", [ent_nome, ent_cnpj, ent_pres, ent_stat]):
                    st.success("✅ Entidade registrada!")
                    st.rerun()

# ---------------------------------------------------------
# 7. PROJETOS & PROGRAMAS
# ---------------------------------------------------------
elif menu == "🚀 Projetos & Programas":
    st.title("🚀 Projetos Estratégicos do Esporte")
    df_projetos = carregar_aba("projetos", ["Projeto", "Orçamento", "Beneficiários", "Execução"])
    st.dataframe(df_projetos, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Lançar Novo Projeto Estratégico")
        with st.form("form_projeto", clear_on_submit=True):
            p_nome = st.text_input("Nome do Projeto:")
            p_orc = st.text_input("Orçamento Estimado (Ex: R$ 50.000,00):")
            p_ben = st.number_input("Meta de Beneficiários:", min_value=1, value=100)
            p_exe = st.text_input("Percentual de Execução (Ex: 30%):")
            
            if st.form_submit_button("💾 Salvar Projeto"):
                if salvar_no_google_sheets("projetos", [p_nome, p_orc, p_ben, p_exe]):
                    st.success("✅ Projeto adicionado!")
                    st.rerun()

# ---------------------------------------------------------
# 8. FUNDO MUNICIPAL DO ESPORTE
# ---------------------------------------------------------
elif menu == "💰 Fundo Municipal do Esporte":
    st.title("💰 Lançamentos do Fundo Municipal (FME)")
    df_fundo = carregar_aba("fundo", ["Item", "Valor", "Fonte", "Status"])
    st.dataframe(df_fundo, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Lançar Nova Despesa / Empenho")
        with st.form("form_fundo", clear_on_submit=True):
            f_item = st.text_input("Item / Elemento de Despesa:")
            f_val = st.number_input("Valor (R$):", min_value=0.0, value=1000.0)
            f_fon = st.selectbox("Fonte de Recurso:", ["FME Próprio", "Emenda Parlamentar", "Lei de Incentivo", "Convênio Estadual"])
            f_st = st.selectbox("Status:", ["Empenhado", "Em Execução", "Pago"])
            
            if st.form_submit_button("💾 Lançar no Fundo"):
                if salvar_no_google_sheets("fundo", [f_item, f_val, f_fon, f_st]):
                    st.success("✅ Lançamento financeiro registrado!")
                    st.rerun()

# ---------------------------------------------------------
# 9. PORTAL DA TRANSPARÊNCIA & NOTÍCIAS
# ---------------------------------------------------------
elif menu == "📢 Portal da Transparência & Notícias":
    st.title("📢 Portal da Transparência & Notícias")
    df_noticias = carregar_aba("publicacoes", ["Data", "Título", "Categoria", "Conteúdo"])
    
    if st.session_state.admin_logado:
        st.subheader("➕ Nova Publicação Oficial")
        with st.form("form_noticia", clear_on_submit=True):
            tit = st.text_input("Título:")
            cat = st.selectbox("Categoria:", ["Edital / Evento", "Notícia", "Obras", "Aviso"])
            cont = st.text_area("Conteúdo da Mensagem:")
            
            if st.form_submit_button("🚀 Publicar no Portal"):
                if salvar_no_google_sheets("publicacoes", [str(datetime.date.today()), tit, cat, cont]):
                    st.success("✅ Notícia publicada!")
                    st.rerun()
        st.divider()
        
    st.subheader("📰 Publicações Ativas para a Sociedade")
    if not df_noticias.empty:
        for _, item in df_noticias.iterrows():
            expander_label = f"📌 [{item['Data']}] {item['Título']} ({item['Categoria']})"
            with st.expander(expander_label):
                st.write(item["Conteúdo"])
    else:
        st.info("Nenhuma notícia publicada até o momento.")
