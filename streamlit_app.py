import streamlit as st
import pandas as pd
import datetime

# Configuração da Página
st.set_page_config(
    page_title="SMEL Toledo — Gestão da Secretaria de Esportes e Lazer",
    page_icon="⚽",
    layout="wide"
)

# ---------------------------------------------------------
# AUTENTICAÇÃO E BASE DE DADOS EM MEMÓRIA DEDICADA
# ---------------------------------------------------------
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# 1. ESPAÇOS ESPORTIVOS
if "espacos" not in st.session_state:
    st.session_state.espacos = pd.DataFrame([
        {"Nome": "Ginásio Alcides Pan", "Tipo": "Ginásio Poliesportivo", "Bairro": "Vila Industrial", "Condição": "Boa", "Última Vistoria": "2026-10-15", "Acessível": "Sim"},
        {"Nome": "Complexo Hugo Zeni", "Tipo": "Complexo / Piscina", "Bairro": "Jardim La Salle", "Condição": "Boa", "Última Vistoria": "2026-09-20", "Acessível": "Sim"},
        {"Nome": "Campo Vila Panorama", "Tipo": "Campo de Futebol", "Bairro": "Vila Panorama", "Condição": "Regular", "Última Vistoria": "2026-10-01", "Acessível": "Parcial"}
    ])

# 2. TURMAS
if "turmas" not in st.session_state:
    st.session_state.turmas = pd.DataFrame([
        {"Código": "TUR-001", "Modalidade": "Futebol de Campo", "Núcleo": "Vila Panorama", "Horário": "Seg/Qua 08:30", "Professor": "Prof. Carlos Silva", "Alunos": 30},
        {"Código": "TUR-002", "Modalidade": "Futsal Sub-13", "Núcleo": "Alcides Pan", "Horário": "Ter/Qui 14:00", "Professor": "Profa. Amanda Lima", "Alunos": 28},
        {"Código": "TUR-003", "Modalidade": "Voleibol Feminino", "Núcleo": "Hugo Zeni", "Horário": "Seg/Qua 16:00", "Professor": "Prof. Roberto Nunes", "Alunos": 25}
    ])

# 3. AGENDA
if "agenda" not in st.session_state:
    st.session_state.agenda = pd.DataFrame([
        {"Data": "2026-11-10", "Evento": "Abertura dos Jogos Escolares de Toledo", "Local": "Ginásio Alcides Pan", "Responsável": "SMEL Toledo"},
        {"Data": "2026-11-15", "Evento": "Torneio Comunitário de Futsal", "Local": "Quadra Vila Panorama", "Responsável": "Associação de Bairro"}
    ])

# 4. EQUIPE
if "equipe" not in st.session_state:
    st.session_state.equipe = pd.DataFrame([
        {"Nome": "Carlos Silva", "Cargo": "Prof. Educação Física", "Núcleo": "Vila Panorama", "Carga Horária": "40h/sem"},
        {"Nome": "Amanda Lima", "Cargo": "Profª Educação Física", "Núcleo": "Ginásio Alcides Pan", "Carga Horária": "40h/sem"}
    ])

# 5. ENTIDADES
if "entidades" not in st.session_state:
    st.session_state.entidades = pd.DataFrame([
        {"Entidade": "Associação de Moradores da Vila Panorama", "CNPJ": "01.234.567/0001-89", "Presidente": "João Pedroso", "Status": "Regular"},
        {"Entidade": "Liga de Futebol Amador de Toledo", "CNPJ": "02.345.678/0001-90", "Presidente": "Sérgio Mendes", "Status": "Regular"}
    ])

# 6. PROJETOS
if "projetos" not in st.session_state:
    st.session_state.projetos = pd.DataFrame([
        {"Projeto": "Movimenta Territórios Toledo", "Orçamento": "R$ 96.000,00", "Beneficiários": 240, "Execução": "75%"},
        {"Projeto": "Atleta do Futuro", "Orçamento": "R$ 150.000,00", "Beneficiários": 450, "Execução": "60%"}
    ])

# 7. FUNDO MUNICIPAL
if "fundo" not in st.session_state:
    st.session_state.fundo = pd.DataFrame([
        {"Item": "Material Esportivo / Bolas", "Valor": 45000.0, "Fonte": "FME Próprio", "Status": "Pago"},
        {"Item": "Manutenção de Quadras e LED", "Valor": 120000.0, "Fonte": "Emenda Parlamentar", "Status": "Em Execução"}
    ])

# 8. NOTÍCIAS E PUBLICAÇÕES
if "publicacoes" not in st.session_state:
    st.session_state.publicacoes = [
        {"Data": "2026-10-28", "Título": "Inscrições Abertas - Jogos Escolares", "Categoria": "Edital / Evento", "Conteúdo": "Inscrições abertas para a fase municipal até 15/11."},
        {"Data": "2026-10-20", "Título": "Reforma do Campo da Vila Panorama", "Categoria": "Obras", "Conteúdo": "Início da iluminação em LED e revitalização do gramado."}
    ]

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
    st.sidebar.success("🟢 Você está no Modo Gestão (Pode editar tudo na tela)")
    if st.sidebar.button("Sair do Modo Gestão"):
        st.session_state.admin_logado = False
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
# 1. PAINEL EXECUTIVO (CALCULADO AUTOMATICAMENTE)
# ---------------------------------------------------------
if menu == "📊 Painel Executivo":
    st.title("📊 Painel Executivo — SMEL Toledo")
    st.caption("Resumo dinâmico da gestão municipal do esporte")
    
    total_alunos = st.session_state.turmas["Alunos"].sum() if not st.session_state.turmas.empty else 0
    total_turmas = len(st.session_state.turmas)
    total_espacos = len(st.session_state.espacos)
    total_fundo = st.session_state.fundo["Valor"].sum() if not st.session_state.fundo.empty else 0.0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Alunos", f"{total_alunos} Atendidos")
    col2.metric("Turmas Ativas", f"{total_turmas} Turmas")
    col3.metric("Espaços Mapeados", f"{total_espacos} Equipamentos")
    col4.metric("Fundo Executado", f"R$ {total_fundo:,.2f}")
    
    st.divider()
    st.subheader("📌 Resumo dos Projetos Ativos")
    st.dataframe(st.session_state.projetos, use_container_width=True)

# ---------------------------------------------------------
# 2. TURMAS & ESCOLINHAS
# ---------------------------------------------------------
elif menu == "📋 Turmas & Escolinhas":
    st.title("📋 Turmas e Escolinhas Esportivas")
    
    st.dataframe(st.session_state.turmas, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Adicionar Nova Turma (Direto na Tela)")
        with st.form("form_turma", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            cod = col1.text_input("Código da Turma (Ex: TUR-005):")
            mod = col2.text_input("Modalidade:")
            nuc = col3.text_input("Núcleo / Bairro:")
            
            col4, col5, col6 = st.columns(3)
            hor = col4.text_input("Horário (Ex: Seg/Qua 10:00):")
            prof = col5.text_input("Professor Responsável:")
            qtd = col6.number_input("Nº de Alunos Vagas:", min_value=1, value=30)
            
            if st.form_submit_button("💾 Cadastrar Turma"):
                nova = pd.DataFrame([{"Código": cod, "Modalidade": mod, "Núcleo": nuc, "Horário": hor, "Professor": prof, "Alunos": qtd}])
                st.session_state.turmas = pd.concat([st.session_state.turmas, nova], ignore_index=True)
                st.success("✅ Turma cadastrada!")
                st.rerun()

# ---------------------------------------------------------
# 3. AGENDA & CALENDÁRIO
# ---------------------------------------------------------
elif menu == "📅 Agenda & Calendário":
    st.title("📅 Agenda & Calendário Esportivo")
    
    st.dataframe(st.session_state.agenda, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Adicionar Evento na Agenda")
        with st.form("form_agenda", clear_on_submit=True):
            d_evt = st.date_input("Data do Evento:", datetime.date.today())
            n_evt = st.text_input("Nome do Evento / Campeonato:")
            l_evt = st.text_input("Local de Realização:")
            r_evt = st.text_input("Organização / Responsável:")
            
            if st.form_submit_button("💾 Incluir na Agenda Pública"):
                nova_ag = pd.DataFrame([{"Data": str(d_evt), "Evento": n_evt, "Local": l_evt, "Responsável": r_evt}])
                st.session_state.agenda = pd.concat([st.session_state.agenda, nova_ag], ignore_index=True)
                st.success("✅ Evento adicionado à agenda!")
                st.rerun()

# ---------------------------------------------------------
# 4. ESPAÇOS ESPORTIVOS
# ---------------------------------------------------------
elif menu == "🏟️ Espaços Esportivos":
    st.title("🏟️ Espaços Esportivos Municipais")
    
    st.dataframe(st.session_state.espacos, use_container_width=True)
    
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
                novo_e = pd.DataFrame([{"Nome": n_esp, "Tipo": t_esp, "Bairro": b_esp, "Condição": c_esp, "Última Vistoria": str(v_esp), "Acessível": a_esp}])
                st.session_state.espacos = pd.concat([st.session_state.espacos, novo_e], ignore_index=True)
                st.success("✅ Espaço cadastrado com sucesso!")
                st.rerun()

# ---------------------------------------------------------
# 5. EQUIPE & PROFESSORES
# ---------------------------------------------------------
elif menu == "👥 Equipe & Professores":
    st.title("👥 Quadro de Servidores e Professores")
    
    st.dataframe(st.session_state.equipe, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Cadastrar Novo Integrante da Equipe")
        with st.form("form_equipe", clear_on_submit=True):
            n_prof = st.text_input("Nome do Servidor/Professor:")
            c_prof = st.text_input("Cargo / Função:")
            nuc_prof = st.text_input("Núcleo Principal de Atuação:")
            ch_prof = st.text_input("Carga Horária (Ex: 40h/sem):")
            
            if st.form_submit_button("💾 Salvar Servidor"):
                novo_p = pd.DataFrame([{"Nome": n_prof, "Cargo": c_prof, "Núcleo": nuc_prof, "Carga Horária": ch_prof}])
                st.session_state.equipe = pd.concat([st.session_state.equipe, novo_p], ignore_index=True)
                st.success("✅ Servidor cadastrado!")
                st.rerun()

# ---------------------------------------------------------
# 6. ENTIDADES & ASSOCIAÇÕES
# ---------------------------------------------------------
elif menu == "🏢 Entidades & Associações":
    st.title("🏢 Entidades e Ligas Esportivas Parceiras")
    
    st.dataframe(st.session_state.entidades, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Cadastrar Entidade Parceira")
        with st.form("form_entidade", clear_on_submit=True):
            ent_nome = st.text_input("Nome da Associação / Liga:")
            ent_cnpj = st.text_input("CNPJ:")
            ent_pres = st.text_input("Presidente / Responsável:")
            ent_stat = st.selectbox("Status Cadastral:", ["Regular (Certificada)", "Em Análise", "Pendente de Documentação"])
            
            if st.form_submit_button("💾 Registrar Entidade"):
                nova_ent = pd.DataFrame([{"Entidade": ent_nome, "CNPJ": ent_cnpj, "Presidente": ent_pres, "Status": ent_stat}])
                st.session_state.entidades = pd.concat([st.session_state.entidades, nova_ent], ignore_index=True)
                st.success("✅ Entidade registrada!")
                st.rerun()

# ---------------------------------------------------------
# 7. PROJETOS & PROGRAMAS
# ---------------------------------------------------------
elif menu == "🚀 Projetos & Programas":
    st.title("🚀 Projetos Estratégicos do Esporte")
    
    st.dataframe(st.session_state.projetos, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Lançar Novo Projeto Estratégico")
        with st.form("form_projeto", clear_on_submit=True):
            p_nome = st.text_input("Nome do Projeto:")
            p_orc = st.text_input("Orçamento Estimado (Ex: R$ 50.000,00):")
            p_ben = st.number_input("Meta de Beneficiários:", min_value=1, value=100)
            p_exe = st.text_input("Percentual de Execução (Ex: 30%):")
            
            if st.form_submit_button("💾 Salvar Projeto"):
                novo_proj = pd.DataFrame([{"Projeto": p_nome, "Orçamento": p_orc, "Beneficiários": p_ben, "Execução": p_exe}])
                st.session_state.projetos = pd.concat([st.session_state.projetos, novo_proj], ignore_index=True)
                st.success("✅ Projeto adicionado!")
                st.rerun()

# ---------------------------------------------------------
# 8. FUNDO MUNICIPAL DO ESPORTE
# ---------------------------------------------------------
elif menu == "💰 Fundo Municipal do Esporte":
    st.title("💰 Lançamentos do Fundo Municipal (FME)")
    
    st.dataframe(st.session_state.fundo, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Lançar Nova Despesa / Empenho")
        with st.form("form_fundo", clear_on_submit=True):
            f_item = st.text_input("Item / Elemento de Despesa:")
            f_val = st.number_input("Valor (R$):", min_value=0.0, value=1000.0)
            f_fon = st.selectbox("Fonte de Recurso:", ["FME Próprio", "Emenda Parlamentar", "Lei de Incentivo", "Convênio Estadual"])
            f_st = st.selectbox("Status:", ["Empenhado", "Em Execução", "Pago"])
            
            if st.form_submit_button("💾 Lançar no Fundo"):
                novo_f = pd.DataFrame([{"Item": f_item, "Valor": f_val, "Fonte": f_fon, "Status": f_st}])
                st.session_state.fundo = pd.concat([st.session_state.fundo, novo_f], ignore_index=True)
                st.success("✅ Lançamento financeiro registrado!")
                st.rerun()

# ---------------------------------------------------------
# 9. PORTAL DA TRANSPARÊNCIA & NOTÍCIAS
# ---------------------------------------------------------
elif menu == "📢 Portal da Transparência & Notícias":
    st.title("📢 Portal da Transparência & Notícias")
    
    if st.session_state.admin_logado:
        st.subheader("➕ Nova Publicação Oficial (Direto na Tela)")
        with st.form("form_noticia", clear_on_submit=True):
            tit = st.text_input("Título:")
            cat = st.selectbox("Categoria:", ["Edital / Evento", "Notícia", "Obras", "Aviso"])
            cont = st.text_area("Conteúdo da Mensagem:")
            
            if st.form_submit_button("🚀 Publicar no Portal"):
                st.session_state.publicacoes.insert(0, {"Data": str(datetime.date.today()), "Título": tit, "Categoria": cat, "Conteúdo": cont})
                st.success("✅ Notícia publicada no portal público!")
                st.rerun()
        st.divider()
        
    st.subheader("📰 Publicações Ativas para a Sociedade")
    for item in st.session_state.publicacoes:
        with st.expander(f"📌 [{item['Data']}] {item['Título']} ({item['Categoria']})"):
