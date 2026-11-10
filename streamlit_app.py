import streamlit as st
import pandas as pd
import datetime
import requests
import json

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
    page_title="SMEL Toledo — Gestão Integrada do Esporte e Lazer",
    page_icon="⚽",
    layout="wide"
)

# ---------------------------------------------------------
# SISTEMA DE SENHA DO GESTOR (GRAVADA NA PLANILHA 'config')
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
    return "smel2026"  # Senha padrão inicial caso a aba config ainda não tenha registro

senha_atual_gestor = obter_senha_gestor()

# ---------------------------------------------------------
# SESSÃO / CONTROLE DE ACESSO
# ---------------------------------------------------------
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# ---------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title("🏛️ SMEL Toledo")
st.sidebar.caption("Secretaria Municipal de Esportes e Lazer")
st.sidebar.markdown("---")

st.sidebar.subheader("🔒 Acesso da Gestão")

if not st.session_state.admin_logado:
    senha_digitada = st.sidebar.text_input("Senha de Gestor:", type="password")
    if st.sidebar.button("Entrar no Modo Gestão"):
        if senha_digitada == senha_atual_gestor:
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
    
    # FERRAMENTA DE TROCA DE SENHA DO GESTOR
    with st.sidebar.expander("🔑 Alterar Senha do Gestor"):
        with st.form("form_troca_senha"):
            nova_senha = st.text_input("Nova Senha:", type="password")
            confirma_senha = st.text_input("Confirmar Nova Senha:", type="password")
            btn_trocar = st.form_submit_button("Salvar Nova Senha")
            if btn_trocar:
                if not nova_senha or len(nova_senha) < 4:
                    st.error("A nova senha deve ter pelo menos 4 caracteres.")
                elif nova_senha != confirma_senha:
                    st.error("As senhas digitadas não conferem.")
                else:
                    if salvar_no_google_sheets("config", ["senha_gestor", nova_senha]):
                        st.success("✅ Senha alterada com sucesso!")
                        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Atualizar Dados da Planilha"):
    st.cache_data.clear()
    st.rerun()
st.sidebar.markdown("---")

# ---------------------------------------------------------
# MENU DINÂMICO BASEADO NO PERFIL DE ACESSO
# ---------------------------------------------------------
if st.session_state.admin_logado:
    # Menu completo para Gestores
    opcoes_menu = [
        "📊 Painel Executivo & Metas",
        "🗺️ Mapa de Cobertura Territorial",
        "📋 Turmas & Escolinhas",
        "📅 Agenda & Calendário",
        "🏟️ Espaços & Vistorias de Segurança",
        "👥 Equipe & Professores",
        "💬 Chamados Internos da Equipe",
        "📅 Planejamento Anual das Modalidades",
        "📢 Ouvidoria Cidadã & Sugestões",
        "🏢 Entidades & Associações (MROSC)",
        "🚀 Projetos & Programas",
        "💰 Fundo Municipal do Esporte (FME)",
        "📢 Portal da Transparência & Notícias"
    ]
else:
    # Menu operacional e público (SEM dados financeiros e projetos)
    opcoes_menu = [
        "🗺️ Mapa de Cobertura Territorial",
        "📋 Turmas & Escolinhas",
        "📅 Agenda & Calendário",
        "🏟️ Espaços & Vistorias de Segurança",
        "👥 Equipe & Professores",
        "💬 Solicitações & Chamados da Equipe",
        "📅 Planejamento Anual das Modalidades",
        "📢 Ouvidoria Cidadã & Sugestões",
        "📢 Portal da Transparência & Notícias"
    ]

menu = st.sidebar.radio("Navegação:", opcoes_menu)

# Coordenadas aproximadas dos bairros/núcleos de Toledo (PR) para o Mapa
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
# 1. PAINEL EXECUTIVO & METAS (EXCLUSIVO GESTOR)
# ---------------------------------------------------------
if menu == "📊 Painel Executivo & Metas":
    st.title("📊 Painel Executivo & Acompanhamento de Metas")
    st.caption("Visão estratégica e orçamentária da Secretaria Municipal de Esportes e Lazer")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    df_fundo = carregar_aba("fundo", ["Item", "Valor", "Fonte", "Status"])
    df_projetos = carregar_aba("projetos", ["Projeto", "Orçamento", "Beneficiários", "Execução"])

    total_alunos = int(pd.to_numeric(df_turmas["Alunos"], errors='coerce').sum()) if not df_turmas.empty and "Alunos" in df_turmas.columns else 0
    total_turmas = len(df_turmas)
    total_espacos = len(df_espacos)
    total_fundo = float(pd.to_numeric(df_fundo["Valor"], errors='coerce').sum()) if not df_fundo.empty and "Valor" in df_fundo.columns else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alunos em Atendimento", f"{total_alunos} Atendidos")
    col2.metric("Turmas Ativas", f"{total_turmas} Turmas")
    col3.metric("Espaços Cadastrados", f"{total_espacos} Equipamentos")
    col4.metric("Fundo Executado", f"R$ {total_fundo:,.2f}")
    
    st.divider()
    st.subheader("🎯 Acompanhamento de Metas de Projetos")
    st.dataframe(df_projetos, use_container_width=True)

# ---------------------------------------------------------
# 2. MAPA DE COBERTURA TERRITORIAL
# ---------------------------------------------------------
elif menu == "🗺️ Mapa de Cobertura Territorial":
    st.title("🗺️ Mapa de Cobertura do Atendimento da SMEL")
    st.caption("Visualização geográfica das turmas e equipamentos esportivos em Toledo (PR)")
    
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    
    pontos_mapa = []
    
    # 1. Adicionar espaços esportivos
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
            
    # 2. Adicionar turmas por núcleo
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

    st.markdown("""
    💡 **Análise de Vazios Territoriais:** 
    Regiões e bairros sem pontos no mapa indicam áreas prioritárias para a expansão de novas turmas ou instalação de núcleos esportivos comunitários.
    """)

# ---------------------------------------------------------
# 3. TURMAS & ESCOLINHAS
# ---------------------------------------------------------
elif menu == "📋 Turmas & Escolinhas":
    st.title("📋 Turmas e Escolinhas Esportivas")
    df_turmas = carregar_aba("turmas", ["Código", "Modalidade", "Núcleo", "Horário", "Professor", "Alunos"])
    st.dataframe(df_turmas, use_container_width=True)
    
    st.divider()
    st.subheader("📄 Diário de Classe para Impressão")
    st.caption("Gere a folha de presença em papel para preenchimento em quadra/campo sem necessidade de celular pessoal.")
    if not df_turmas.empty:
        turma_sel = st.selectbox("Selecione a Turma:", df_turmas["Código"] + " - " + df_turmas["Modalidade"] + " (" + df_turmas["Núcleo"] + ")")
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
            | 06 | | | | | | | | | | | | | | | | | |
            | 07 | | | | | | | | | | | | | | | | | |
            | 08 | | | | | | | | | | | | | | | | | |
            """)
            st.info("💡 Você pode imprimir esta página diretamente usando o atalho Ctrl+P do computador da secretaria ou ginásio.")
    
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
            qtd = col6.number_input("Nº de Alunos Vagas:", min_value=1, value=30)
            
            if st.form_submit_button("💾 Salvar na Planilha"):
                if salvar_no_google_sheets("turmas", [cod, mod, nuc, hor, prof, qtd]):
                    st.success("✅ Turma salva com sucesso na planilha!")
                    st.rerun()

# ---------------------------------------------------------
# 4. AGENDA & CALENDÁRIO
# ---------------------------------------------------------
elif menu == "📅 Agenda & Calendário":
    st.title("📅 Agenda & Calendário Esportivo Oficial")
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
# 5. ESPAÇOS & VISTORIAS DE SEGURANÇA
# ---------------------------------------------------------
elif menu == "🏟️ Espaços & Vistorias de Segurança":
    st.title("🏟️ Espaços Esportivos & Vistorias de Segurança")
    df_espacos = carregar_aba("espacos", ["Nome", "Tipo", "Bairro", "Condição", "Última Vistoria", "Acessível"])
    st.dataframe(df_espacos, use_container_width=True)
    
    st.divider()
    st.subheader("📋 Checklist Rápido de Vistoria de Segurança")
    st.caption("Preenchimento nos computadores dos ginásios para avaliar piso, iluminação e integridade.")
    with st.form("form_vistoria"):
        col_v1, col_v2 = st.columns(2)
        v_espaco = col_v1.text_input("Espaço Esportivo Vistoriado:")
        v_data = col_v2.date_input("Data da Vistoria:", datetime.date.today())
        
        c1, c2, c3, c4 = st.columns(4)
        ch_piso = c1.checkbox("Piso em condições seguras")
        ch_luz = c2.checkbox("Iluminação adequada")
        ch_redes = c3.checkbox("Traves/Tabelas/Redes seguras")
        ch_socorros = c4.checkbox("Kit Primeiros Socorros disponível")
        
        v_obs = st.text_area("Observações Técnicas / Danos detectados:")
        if st.form_submit_button("Salvar Registro de Vistoria"):
            status_calc = "Boa" if (ch_piso and ch_luz and ch_redes) else "Necessita Reforma"
            if salvar_no_google_sheets("espacos", [v_espaco, "Vistoria Realizada", "Toledo", status_calc, str(v_data), "Sim" if ch_socorros else "Não"]):
                st.success("✅ Vistoria registrada com sucesso!")
                st.rerun()

# ---------------------------------------------------------
# 6. EQUIPE & PROFESSORES
# ---------------------------------------------------------
elif menu == "👥 Equipe & Professores":
    st.title("👥 Quadro de Servidores e Professores")
    df_equipe = carregar_aba("equipe", ["Nome", "Cargo", "Núcleo", "Carga Horária"])
    st.dataframe(df_equipe, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Cadastrar Novo Integrante da Equipe (Gestão)")
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
# 7. CHAMADOS INTERNOS DA EQUIPE (CANAL DE ESCUTA)
# ---------------------------------------------------------
elif "Chamados" in menu or "Solicitações" in menu:
    st.title("💬 Canal de Escuta & Solicitações da Equipe")
    st.caption("Espaço para professores e servidores enviarem pedidos de materiais, reparos e sugestões com retorno da gestão.")
    
    df_chamados = carregar_aba("chamados", ["Data", "Servidor", "Núcleo", "Tipo", "Descrição", "Status", "Retorno Gestão"])
    st.dataframe(df_chamados, use_container_width=True)
    
    st.divider()
    st.subheader("➕ Abrir Nova Solicitação / Chamado")
    with st.form("form_novo_chamado", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        serv_nome = col_c1.text_input("Seu Nome:")
        serv_nuc = col_c2.text_input("Seu Núcleo / Modalidade:")
        
        tipo_solic = st.selectbox("Tipo de Demanda:", [
            "📦 Pedido de Materiais (Bolas, coletes, redes)",
            "🛠️ Manutenção Urgente na Quadra/Espaço",
            "💡 Sugestão Pedagógica / Nova Turma",
            "❓ Outra Solicitação"
        ])
        detalhe = st.text_area("Descreva com clareza o que você precisa:")
        
        if st.form_submit_button("📨 Enviar Solicitação para a Gestão"):
            if salvar_no_google_sheets("chamados", [
                str(datetime.date.today()), serv_nome, serv_nuc, tipo_solic, detalhe, "Pendente", "Aguardando análise da coordenação"
            ]):
                st.success("✅ Solicitação enviada! A equipe gestora acompanhará e atualizará o status aqui.")
                st.rerun()
                
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("🛠️ Responder / Atualizar Chamado (Exclusivo Gestor)")
        with st.form("form_resp_chamado"):
            c_idx = st.text_input("Linha ou Nome do Solicitante:")
            novo_status = st.selectbox("Novo Status:", ["Em Análise", "Aprovado / Em Cotação", "Atendido / Concluído", "Não Aprovado"])
            resp_txt = st.text_area("Mensagem de Retorno para o Servidor:")
            if st.form_submit_button("💾 Atualizar Status"):
                if salvar_no_google_sheets("chamados", [str(datetime.date.today()), f"Retorno: {c_idx}", "-", "Atualização", resp_txt, novo_status, resp_txt]):
                    st.success("✅ Retorno registrado com sucesso!")
                    st.rerun()

# ---------------------------------------------------------
# 8. PLANEJAMENTO ANUAL DAS MODALIDADES (ANO SEGUINTE)
# ---------------------------------------------------------
elif menu == "📅 Planejamento Anual das Modalidades":
    st.title("📅 Planejamento Anual da Modalidade (Previsão para o Próximo Ano)")
    st.caption("Previsão anual de viagens, campeonatos e insumos necessários para subsidiar o orçamento e licitações com antecedência.")
    
    df_plan = carregar_aba("planejamento_anual", ["Modalidade", "Professor", "Competições Previstas", "Transporte/Hospedagem", "Materiais Solicitados"])
    st.dataframe(df_plan, use_container_width=True)
    
    st.divider()
    st.subheader("➕ Inserir Planejamento da sua Modalidade")
    with st.form("form_planejamento_anual", clear_on_submit=True):
        col_p1, col_p2 = st.columns(2)
        p_mod = col_p1.text_input("Modalidade Esportiva:")
        p_prof = col_p2.text_input("Professor Responsável:")
        
        p_comp = st.text_area("Campeonatos e Torneios que a equipe pretende disputar (Nome, Cidade e Mês previsto):")
        p_transp = st.text_area("Previsão de Logística (Ex: 2 viagens em van, 1 viagem em ônibus com hospedagem):")
        p_materiais = st.text_area("Materiais e Insumos necessários para o ano todo (Ex: 20 bolas, 30 uniformes, 4 redes):")
        
        if st.form_submit_button("💾 Salvar Planejamento Anual"):
            if salvar_no_google_sheets("planejamento_anual", [p_mod, p_prof, p_comp, p_transp, p_materiais]):
                st.success("✅ Planejamento anual salvo! A gestão utilizará estes dados para o planejamento orçamentário.")
                st.rerun()

# ---------------------------------------------------------
# 9. OUVIDORIA CIDADÃ ANÔNIMA
# ---------------------------------------------------------
elif menu == "📢 Ouvidoria Cidadã & Sugestões":
    st.title("📢 Ouvidoria Cidadã & Sugestões da Comunidade")
    st.caption("Canal aberto para a sociedade enviar sugestões de modalidades, elogios ou alertas sobre equipamentos públicos.")
    
    with st.form("form_ouvidoria", clear_on_submit=True):
        st.write("💬 **Sua manifestação é anônima e ajuda a melhorar o esporte em Toledo!**")
        tipo_ouvidoria = st.selectbox("Tipo de Manifestação:", [
            "💡 Sugestão de nova turma ou modalidade no bairro",
            "⚠️ Alerta de problema em praça ou ginásio público",
            "👏 Elogio às atividades da SMEL",
            "❓ Outro comentário"
        ])
        bairro_cidadao = st.text_input("Bairro / Região de Toledo:")
        mensagem_cidadao = st.text_area("Escreva sua mensagem:")
        
        if st.form_submit_button("🚀 Enviar de Forma Anônima"):
            if salvar_no_google_sheets("ouvidoria", [
                str(datetime.date.today()), tipo_ouvidoria, bairro_cidadao, mensagem_cidadao, "Pendente"
            ]):
                st.success("✅ Muito obrigado! Sua manifestação foi recebida com sucesso pela equipe da SMEL Toledo.")
                st.rerun()
                
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("🔍 Manifestações Recebidas (Painel da Gestão)")
        df_ouv = carregar_aba("ouvidoria", ["Data", "Tipo", "Bairro", "Mensagem", "Status"])
        st.dataframe(df_ouv, use_container_width=True)

# ---------------------------------------------------------
# 10. ENTIDADES & ASSOCIAÇÕES (EXCLUSIVO GESTOR)
# ---------------------------------------------------------
elif menu == "🏢 Entidades & Associações (MROSC)":
    st.title("🏢 Entidades e Ligas Esportivas Parceiras")
    df_entidades = carregar_aba("entidades", ["Entidade", "CNPJ", "Presidente", "Status"])
    st.dataframe(df_entidades, use_container_width=True)
    
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
# 11. PROJETOS & PROGRAMAS (EXCLUSIVO GESTOR)
# ---------------------------------------------------------
elif menu == "🚀 Projetos & Programas":
    st.title("🚀 Projetos Estratégicos do Esporte")
    df_projetos = carregar_aba("projetos", ["Projeto", "Orçamento", "Beneficiários", "Execução"])
    st.dataframe(df_projetos, use_container_width=True)
    
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
# 12. FUNDO MUNICIPAL DO ESPORTE (EXCLUSIVO GESTOR)
# ---------------------------------------------------------
elif menu == "💰 Fundo Municipal do Esporte (FME)":
    st.title("💰 Lançamentos do Fundo Municipal do Esporte (FME)")
    df_fundo = carregar_aba("fundo", ["Item", "Valor", "Fonte", "Status"])
    st.dataframe(df_fundo, use_container_width=True)
    
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
# 13. PORTAL DA TRANSPARÊNCIA & NOTÍCIAS
# ---------------------------------------------------------
elif menu == "📢 Portal da Transparência & Notícias":
    st.title("📢 Portal da Transparência & Notícias")
    df_noticias = carregar_aba("publicacoes", ["Data", "Título", "Categoria", "Conteúdo"])
    
    if st.session_state.admin_logado:
        st.subheader("➕ Nova Publicação Oficial (Gestão)")
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
