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
# ESTADO DE AUTENTICAÇÃO E DADOS DA SESSÃO
# ---------------------------------------------------------
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

if "espacos" not in st.session_state:
    st.session_state.espacos = pd.DataFrame([
        {
            "Nome": "Ginásio de Esportes Alcides Pan",
            "Tipo": "Ginásio Poliesportivo",
            "Bairro": "Vila Industrial",
            "Condição": "Boa",
            "Última Vistoria": "2026-10-15",
            "Acessível": "Sim"
        },
        {
            "Nome": "Complexo Esportivo Hugo Zeni",
            "Tipo": "Quadra / Piscina",
            "Bairro": "Jardim La Salle",
            "Condição": "Boa",
            "Última Vistoria": "2026-09-20",
            "Acessível": "Sim"
        },
        {
            "Nome": "Campo de Futebol Vila Panorama",
            "Tipo": "Campo de Futebol",
            "Bairro": "Vila Panorama",
            "Condição": "Regular",
            "Última Vistoria": "2026-10-01",
            "Acessível": "Parcial"
        }
    ])

if "publicacoes" not in st.session_state:
    st.session_state.publicacoes = [
        {
            "Data": "2026-10-28",
            "Título": "Abertura das Inscrições para os Jogos Escolares de Toledo",
            "Categoria": "Edital / Evento",
            "Conteúdo": "A SMEL Toledo informa que estão abertas as inscrições para os Jogos Escolares Municipais. Prazo até 15/11."
        },
        {
            "Data": "2026-10-20",
            "Título": "Reforma do Campo Comunitário da Vila Panorama",
            "Categoria": "Obras e Infraestrutura",
            "Conteúdo": "Início dos trabalhos de revitalização do gramado e iluminação em LED no núcleo esportivo da Vila Panorama."
        }
    ]

# ---------------------------------------------------------
# BARRA LATERAL - NAVEGAÇÃO E LOGIN
# ---------------------------------------------------------
st.sidebar.title("🏛️ SMEL Toledo")
st.sidebar.caption("Secretaria Municipal de Esportes e Lazer — Toledo/PR")
st.sidebar.markdown("---")

# ÁREA DE LOGIN DA EQUIPE
st.sidebar.subheader("🔒 Acesso Restrito")

if not st.session_state.admin_logado:
    senha_input = st.sidebar.text_input("Senha da Equipe SMEL:", type="password", key="input_senha")
    if st.sidebar.button("Entrar como Gestor"):
        if senha_input == "smel2026":
            st.session_state.admin_logado = True
            st.sidebar.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.sidebar.error("❌ Senha incorreta.")
else:
    st.sidebar.success("🟢 Modo Gestão Ativo (Equipe SMEL)")
    if st.sidebar.button("Sair (Modo Cidadão)"):
        st.session_state.admin_logado = False
        st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Módulos do Portal:",
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

st.sidebar.markdown("---")
if st.session_state.admin_logado:
    st.sidebar.warning("🛠️ **Atenção**: Você está no modo de edição. Todas as alterações serão salvas no portal.")
else:
    st.sidebar.info("👁️ **Modo Cidadão**: Visualização pública das informações oficiais de Toledo.")

# ---------------------------------------------------------
# 1. PAINEL EXECUTIVO
# ---------------------------------------------------------
if menu == "📊 Painel Executivo":
    st.title("📊 Painel Executivo — SMEL Toledo")
    st.caption("Visão Geral da Gestão da Secretaria Municipal de Esportes e Lazer")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alunos Atendidos", "3.420", "+12% este mês")
    col2.metric("Turmas Ativas", "86 Turmas", "14 Núcleos")
    col3.metric("Espaços Mapeados", f"{len(st.session_state.espacos)} Equipamentos", "100% Monitorados")
    col4.metric("Execução do Fundo (FME)", "R$ 485.000", "68% do Orçamento")
    
    st.divider()
    st.subheader("📌 Resumo dos Projetos em Andamento")
    df_resumo = pd.DataFrame({
        "Projeto / Programa": ["Movimenta Territórios", "Atleta do Futuro", "Esporte na Terceira Idade", "Reforma de Ginásios"],
        "Território / Bairro": ["Vila Panorama", "Jardim Coopagro", "Vila Industrial", "Vários Núcleos"],
        "Beneficiários Atendidos": [240, 450, 180, "Toda a Comunidade"],
        "Status": ["Em Execução", "Em Execução", "Em Execução", "Fase de Obras"]
    })
    st.dataframe(df_resumo, use_container_width=True)

# ---------------------------------------------------------
# 2. TURMAS & ESCOLINHAS
# ---------------------------------------------------------
elif menu == "📋 Turmas & Escolinhas":
    st.title("📋 Consulta de Turmas e Escolinhas")
    st.caption("Locais, modalidades e quadro de frequências")
    
    if st.session_state.admin_logado:
        tab1, tab2 = st.tabs(["Lista Geral de Turmas", "✏️ Lançar Frequência (Exclusivo Equipe)"])
    else:
        tab1, = st.tabs(["Lista Geral de Turmas"])
    
    with tab1:
        st.subheader("Turmas Ativas no Município")
        df_turmas = pd.DataFrame({
            "Código": ["TUR-001", "TUR-002", "TUR-003", "TUR-004"],
            "Modalidade": ["Futebol de Campo", "Futsal Sub-13", "Voleibol Feminino", "Ginástica 60+"],
            "Núcleo / Bairro": ["Vila Panorama", "Alcides Pan (Vila Ind.)", "Hugo Zeni (La Salle)", "Coopagro"],
            "Horário": ["Seg/Qua 08:30", "Ter/Qui 14:00", "Seg/Qua 16:00", "Ter/Qui 08:00"],
            "Professor": ["Prof. Carlos Silva", "Profa. Amanda Lima", "Prof. Roberto Nunes", "Profa. Juliana Costa"],
            "Vagas Preenchidas": ["30 / 30", "28 / 30", "25 / 25", "40 / 40"]
        })
        st.dataframe(df_turmas, use_container_width=True)
        
    if st.session_state.admin_logado:
        with tab2:
            st.subheader("📝 Diário de Classe Digital em Campo")
            turma_sel = st.selectbox("Selecione a Turma:", ["TUR-001 - Futebol (Vila Panorama)", "TUR-002 - Futsal (Alcides Pan)"])
            data_aula = st.date_input("Data da Aula:", datetime.date.today())
            
            alunos = ["Gabriel Santos", "Mariana Oliveira", "Lucas Pereira", "Beatriz Lima", "Enzo Gabriel", "Sophia Silva"]
            presencas = {}
            for aluno in alunos:
                presencas[aluno] = st.checkbox(f"✅ Presença: {aluno}", value=True)
                
            if st.button("💾 Salvar Chamada"):
                st.success(f"Frequência registrada com sucesso para {sum(presencas.values())} alunos na data {data_aula}!")

# ---------------------------------------------------------
# 3. AGENDA & CALENDÁRIO
# ---------------------------------------------------------
elif menu == "📅 Agenda & Calendário":
    st.title("📅 Agenda & Calendário Esportivo de Toledo")
    st.caption("Programação oficial de eventos, campeonatos e atividades abertas ao público")
    
    df_agenda = pd.DataFrame({
        "Data": ["2026-11-10", "2026-11-15", "2026-11-20", "2026-12-05"],
        "Evento / Atividade": ["Abertura dos Jogos Escolares de Toledo", "Torneio Comunitário de Futsal", "Festival da Terceira Idade", "Corrida Rústica de Fim de Ano"],
        "Local": ["Ginásio Alcides Pan", "Quadra Vila Panorama", "Complexo Hugo Zeni", "Parque Ecológico Diva Paim Barth"],
        "Responsável": ["SMEL Toledo", "Associação de Bairro", "SMEL Toledo", "SMEL / Parcerias"]
    })
    st.dataframe(df_agenda, use_container_width=True)

# ---------------------------------------------------------
# 4. ESPAÇOS ESPORTIVOS
# ---------------------------------------------------------
elif menu == "🏟️ Espaços Esportivos":
    st.title("🏟️ Espaços Esportivos Municipais de Toledo")
    st.caption("Mapeamento público de ginásios, quadras e núcleos esportivos")
    
    st.subheader("📋 Equipamentos Cadastrados")
    st.dataframe(st.session_state.espacos, use_container_width=True)
    
    if st.session_state.admin_logado:
        st.divider()
        st.subheader("➕ Novo Registro de Espaço (Exclusivo Gestão)")
        
        with st.form("form_novo_espaco", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                nome_espaco = st.text_input("Nome do Espaço / Equipamento:", placeholder="Ex: Quadra Poliesportiva Bairro Sul")
                tipo_espaco = st.selectbox("Tipo:", ["Quadra Poliesportiva", "Ginásio Poliesportivo", "Campo de Futebol", "Complexo / Piscina", "Pista de Atletismo", "Centro de Lutas"])
                bairro_espaco = st.text_input("Bairro / Localidade:", placeholder="Ex: Jardim Coopagro")
            with col_b:
                condicao_espaco = st.selectbox("Condição do Equipamento:", ["Boa", "Regular", "Necessita Reparo / Reforma", "Interditado"])
                vistoria_espaco = st.date_input("Última Vistoria:", datetime.date.today())
                acessivel_espaco = st.selectbox("Acessibilidade PcD:", ["Sim", "Parcial", "Não"])
                
            btn_salvar = st.form_submit_button("💾 Salvar Novo Espaço Esportivo")
            
            if btn_salvar:
                if nome_espaco and bairro_espaco:
                    novo_dado = pd.DataFrame([{
                        "Nome": nome_espaco,
                        "Tipo": tipo_espaco,
                        "Bairro": bairro_espaco,
                        "Condição": condicao_espaco,
                        "Última Vistoria": str(vistoria_espaco),
                        "Acessível": acessivel_espaco
                    }])
                    st.session_state.espacos = pd.concat([st.session_state.espacos, novo_dado], ignore_index=True)
                    st.success(f"✅ Espaço '{nome_espaco}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("⚠️ Preencha o Nome e o Bairro do equipamento.")
    else:
        st.info("ℹ️ Para solicitar manutenção ou registrar um novo espaço esportivo, procure a equipe técnica da SMEL Toledo.")

# ---------------------------------------------------------
# 5. EQUIPE & PROFESSORES
# ---------------------------------------------------------
elif menu == "👥 Equipe & Professores":
    st.title("👥 Quadro de Pessoal e Professores")
    st.caption("Equipe técnica e pedagógica a serviço da população de Toledo")
    
    df_equipe = pd.DataFrame({
        "Nome do Servidor/Prof.": ["Carlos Silva", "Amanda Lima", "Roberto Nunes", "Juliana Costa", "Marcos Oliveira"],
        "Cargo / Função": ["Prof. Educação Física", "Profª Educação Física", "Coordenador Técnico", "Profª Ginástica", "Inspetor de Equipamentos"],
        "Núcleo Principal": ["Vila Panorama", "Ginásio Alcides Pan", "Sede SMEL", "Jardim Coopagro", "Geral"],
        "Carga Horária": ["40h/semana", "40h/semana", "40h/semana", "20h/semana", "40h/semana"]
    })
    st.dataframe(df_equipe, use_container_width=True)

# ---------------------------------------------------------
# 6. ENTIDADES & ASSOCIAÇÕES
# ---------------------------------------------------------
elif menu == "🏢 Entidades & Associações":
    st.title("🏢 Entidades Esportivas Parceiras")
    st.caption("Associações de bairro e ligas parceiras da Prefeitura de Toledo")
    
    df_entidades = pd.DataFrame({
        "Entidade / Liga": ["Associação de Moradores da Vila Panorama", "Liga de Futebol Amador de Toledo", "Clube de Terceira Idade Vida Ativa", "Associação de Paradesporto de Toledo"],
        "CNPJ": ["01.234.567/0001-89", "02.345.678/0001-90", "03.456.789/0001-01", "04.567.890/0001-12"],
        "Presidente / Resp.": ["João Pedroso", "Sérgio Mendes", "Clara Antunes", "Dr. Fernando Luz"],
        "Status Cadastral": ["Regular (Certificada)", "Regular (Certificada)", "Regular (Certificada)", "Regular (Certificada)"]
    })
    st.dataframe(df_entidades, use_container_width=True)

# ---------------------------------------------------------
# 7. PROJETOS & PROGRAMAS
# ---------------------------------------------------------
elif menu == "🚀 Projetos & Programas":
    st.title("🚀 Projetos Estratégicos — SMEL Toledo")
    st.caption("Transparência e metas dos programas municipais de esporte")
    
    st.subheader("Projeto Modelo: Movimenta Territórios Toledo")
    st.markdown("""
    * **Orçamento Total**: R$ 96.000,00
    * **Metas Físicas**: 240 alunos atendidos em 4 núcleos periféricos da cidade.
    * **Legislação Norteadora**: Fundamentado na Lei Geral do Esporte (Lei nº 14.597/2023).
    * **Indicadores**: Frequência mínima de 80% e 96 sessões de treinamento por núcleo/ano.
    """)
    st.progress(0.75, text="Execução Físico-Financeira do Projeto: 75% Concluído")

# ---------------------------------------------------------
# 8. FUNDO MUNICIPAL DO ESPORTE
# ---------------------------------------------------------
elif menu == "💰 Fundo Municipal do Esporte":
    st.title("💰 Fundo Municipal do Esporte (FME Toledo)")
    st.caption("Transparência na aplicação dos recursos públicos no esporte")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Receita Orçamentária 2026", "R$ 750.000,00", "Dotação Própria")
    col2.metric("Emendas Parlamentares", "R$ 300.000,00", "Transferegov")
    col3.metric("Recursos Liquidados", "R$ 485.000,00", "64,6% Executado")
    
    st.divider()
    st.subheader("Detalhamento das Despesas Liquidadas")
    df_fundo = pd.DataFrame({
        "Elemento de Despesa": ["Material Esportivo / Bolas e Coletes", "Manutenção de Quadras e LED", "Arbitragem dos Jogos Escolares", "Bolsa Atleta Municipal"],
        "Valor Empenhado": ["R$ 45.000,00", "R$ 120.000,00", "R$ 35.000,00", "R$ 180.000,00"],
        "Fonte de Recurso": ["FME Próprio", "Emenda Parlamentar", "FME Próprio", "FME Próprio"],
        "Status": ["Pago", "Em Execução", "Pago", "Pagamento Mensal (Regular)"]
    })
    st.dataframe(df_fundo, use_container_width=True)

# ---------------------------------------------------------
# 9. PORTAL DA TRANSPARÊNCIA & NOTÍCIAS
# ---------------------------------------------------------
elif menu == "📢 Portal da Transparência & Notícias":
    st.title("📢 Portal da Transparência & Publicações da SMEL")
    st.caption("Informações e editais oficiais para a população de Toledo")
    
    if st.session_state.admin_logado:
        st.subheader("➕ Alimentar o Sistema (Exclusivo Equipe SMEL)")
        with st.form("form_nova_pub", clear_on_submit=True):
            tit_pub = st.text_input("Título da Publicação:")
            cat_pub = st.selectbox("Categoria:", ["Edital / Chamamento", "Notícia", "Resultado de Campeonato", "Aviso de Manutenção / Interdição"])
            cont_pub = st.text_area("Conteúdo da Publicação para a Sociedade:")
            
            if st.form_submit_button("🚀 Publicar no Portal Público"):
                if tit_pub and cont_pub:
                    st.session_state.publicacoes.insert(0, {
                        "Data": str(datetime.date.today()),
                        "Título": tit_pub,
                        "Categoria": cat_pub,
                        "Conteúdo": cont_pub
                    })
                    st.success("✅ Publicação realizada com sucesso!")
                    st.rerun()
                else:
                    st.error("⚠️ Preencha o título e o conteúdo antes de publicar.")
        st.divider()
    else:
        st.info("ℹ️ Para publicar avisos ou editais, a equipe deve efetuar login no menu lateral.")
        
    st.subheader("📰 Publicações Ativas para a População de Toledo")
    for item in st.session_state.publicacoes:
        with st.expander(f"📌 [{item['Data']}] {item['Título']} ({item['Categoria']})"):
            st.write(item["Conteúdo"])
            st.caption(f"Publicado por SMEL Toledo em {item['Data']}")
