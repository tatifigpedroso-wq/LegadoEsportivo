import streamlit as st
import pandas as pd
import datetime

# Configuração da Página
st.set_page_config(
    page_title="Legado Esportivo® - Gestão Pública do Esporte",
    page_icon="⚽",
    layout="wide"
)

# Barra Lateral - Menu de Navegação
st.sidebar.title("Legado Esportivo®")
st.sidebar.caption("Plataforma de Gestão Pública do Esporte v2.0")

menu = st.sidebar.radio(
    "Módulos da Plataforma:",
    [
        "📊 Dashboard do Secretário",
        "🗺️ Matriz de Priorização Territorial",
        "📋 Diário de Classe Digital (Celular)",
        "🏟️ Reserva de Equipamentos Públicos",
        "🏆 Campeonatos & Jogos Escolares",
        "🥇 Bolsa Atleta Municipal",
        "🪪 Carteirinha Digital do Aluno",
        "📣 Ouvidoria & Manutenção (Voz do Esporte)",
        "📝 Fichas Técnicas & Mapeador de Editais",
        "✅ Checklist de Prestação de Contas (TCE)"
    ]
)

# 1. DASHBOARD DO SECRETÁRIO
if menu == "📊 Dashboard do Secretário":
    st.title("📊 Painel Executivo de Gestão Esportiva")
    st.subheader("Projeto Modelo: Movimenta Territórios (R$ 96.000,00)")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alunos Mantidos", "228 / 240", "95% da Meta")
    col2.metric("Sessões de Aula", "96 realizadas", "100% Executado")
    col3.metric("Taxa de Permanência", "85%", "+5% acima da meta")
    col4.metric("Execução Orçamentária", "R$ 23.850 / R$ 24k", "99,3% no Trimestre")
    
    st.divider()
    st.subheader("Status dos Núcleos Esportivos Comunitários")
    df_nucleos = pd.DataFrame({
        "Núcleo / Bairro": ["Bairro Esperança", "Distrito Vulnerável B", "Zona Rural C", "Bairro Sul D"],
        "Vagas Previstas": [60, 60, 60, 60],
        "Alunos Ativos": [58, 56, 57, 57],
        "Frequência Média (%)": ["88%", "84%", "82%", "86%"],
        "Inclusão PcD": [6, 7, 6, 6]
    })
    st.dataframe(df_nucleos, use_container_width=True)

# 2. MATRIZ DE PRIORIZAÇÃO TERRITORIAL (LEI 14.597/2023)
elif menu == "🗺️ Matriz de Priorização Territorial":
    st.title("🗺️ Calculadora de Priorização Territorial")
    st.caption("Método Legado Esportivo® — Fundamentado na Lei nº 14.597/2023")
    
    col1, col2 = st.columns(2)
    with col1:
        nome_bairro = st.text_input("Nome do Bairro / Território:", "Bairro Esperança")
        vuln = st.slider("Vulnerabilidade Social (Peso 30%):", 1.0, 5.0, 4.0, 0.5)
        vazio = st.slider("Ausência de Oferta Esportiva (Peso 25%):", 1.0, 5.0, 5.0, 0.5)
    with col2:
        seg = st.slider("Segurança do Espaço (Peso 15%):", 1.0, 5.0, 3.0, 0.5)
        viab = st.slider("Viabilidade Logística (Peso 15%):", 1.0, 5.0, 4.0, 0.5)
        parc = st.slider("Potencial de Parcerias (Peso 15%):", 1.0, 5.0, 3.0, 0.5)
        
    nota_final = (vuln * 0.30) + (vazio * 0.25) + (seg * 0.15) + (viab * 0.15) + (parc * 0.15)
    
    st.subheader(f"Nota Ponderada Final do Bairro: **{nota_final:.2f}** / 5.00")
    if nota_final >= 4.0:
        st.success("🟢 PRIORIDADE ALTA: Território altamente recomendado para investimento imediato.")
    elif nota_final >= 3.0:
        st.warning("🟡 PRIORIDADE MÉDIA: Atende aos requisitos, aguardando orçamento.")
    else:
        st.error("🔴 PRIORIDADE BAIXA: Baixa vulnerabilidade ou alta cobertura existente.")

# 3. DIÁRIO DE CLASSE DIGITAL
elif menu == "📋 Diário de Classe Digital (Celular)":
    st.title("📋 Diário de Classe Digital")
    st.caption("Otimizado para o professor registrar frequência pelo celular no campo")
    
    nucleo = st.selectbox("Selecione o Núcleo:", ["Núcleo A - Bairro Esperança", "Núcleo B - Distrito Industrial"])
    data_aula = st.date_input("Data da Aula:", datetime.date.today())
    
    st.subheader("Lista de Chamada dos Alunos")
    alunos = ["Gabriel Santos", "Mariana Oliveira", "Lucas Pereira", "Beatriz Lima", "Enzo Gabriel", "Sophia Silva"]
    
    presencas = {}
    for aluno in alunos:
        presencas[aluno] = st.checkbox(f"✅ Presença: {aluno}", value=True)
        
    if st.button("💾 Salvar Chamada no Sistema"):
        st.success(f"Frequência registrada com sucesso para {sum(presencas.values())} alunos na data {data_aula}!")

# 4. RESERVA DE EQUIPAMENTOS PÚBLICOS
elif menu == "🏟️ Reserva de Equipamentos Públicos":
    st.title("🏟️ Gestão & Agendamento de Equipamentos Públicos")
    st.caption("Transparência no uso de quadras, ginásios e campos municipais")
    
    tab1, tab2 = st.tabs(["Solicitar Reserva", "Quadro de Horários"])
    with tab1:
        st.text_input("Nome do Solicitante / Associação:")
        st.selectbox("Equipamento Desejado:", ["Ginásio Municipal Central", "Campo de Futebol Bairro Esperança", "Quadra Poliesportiva Periferia"])
        st.date_input("Data do Evento/Treino:")
        st.time_input("Horário de Início:")
        if st.button("Enviar Solicitação de Reserva"):
            st.success("Solicitação enviada! A Secretaria analisará a disponibilidade.")
            
    with tab2:
        df_espacos = pd.DataFrame({
            "Equipamento": ["Ginásio Central", "Campo Bairro Esperança", "Quadra Bairro Sul", "Piscina Olímpica"],
            "Status Hoje": ["Disponível", "Reservado (19h-21h)", "Disponível", "Em Manutenção"],
            "Capacidade": ["1.200 pessoas", "22 jogadores", "100 pessoas", "80 banhistas"]
        })
        st.dataframe(df_espacos, use_container_width=True)

# 5. CAMPEONATOS E TORNEIOS
elif menu == "🏆 Campeonatos & Jogos Escolares":
    st.title("🏆 Módulo de Campeonatos e Jogos Escolares")
    st.caption("Gestão de inscrições, chaves e tabelas de classificação")
    
    df_jogos = pd.DataFrame({
        "Modalidade / Torneio": ["Futebol Amador Adulto", "Futsal Sub-15 Escolar", "Vôlei Feminino Master"],
        "Equipes Inscritas": [16, 24, 12],
        "Fase Atual": ["Oitavas de Final", "Fase de Grupos", "Semifinais"],
        "Próxima Rodada": ["Sábado - 09:00", "Sexta - 14:00", "Domingo - 10:00"]
    })
    st.dataframe(df_jogos, use_container_width=True)
    st.button("➕ Cadastrar Novo Campeonato / Equipe")

# 6. BOLSA ATLETA MUNICIPAL
elif menu == "🥇 Bolsa Atleta Municipal":
    st.title("🥇 Programa Bolsa Atleta Municipal")
    st.caption("Controle de concessão de incentivos e prestação de contas de atletas")
    
    df_atletas = pd.DataFrame({
        "Atleta": ["Lucas Andrade", "Camila Silva", "Matheus Oliveira"],
        "Modalidade": ["Atletismo (100m)", "Natação", "Judô Sub-18"],
        "Categoria": ["Estadual", "Nacional", "Estadual"],
        "Valor Mensal": ["R$ 600,00", "R$ 1.200,00", "R$ 600,00"],
        "Prestação de Contas": ["Regular", "Regular", "Pendente (Mês Atual)"]
    })
    st.dataframe(df_atletas, use_container_width=True)

# 7. CARTEIRINHA DIGITAL DO ALUNO
elif menu == "🪪 Carteirinha Digital do Aluno":
    st.title("🪪 Carteirinha Digital & Acesso aos Núcleos")
    st.caption("Identificação segura dos alunos para frequência e piscinas públicas")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📱 [QR CODE DE ACESSO DO ALUNO]")
    with col2:
        st.subheader("Aluno: Gabriel Santos")
        st.write("**Matrícula:** 2026-001")
        st.write("**Núcleo:** Bairro Esperança (Futebol de Campo)")
        st.write("**Responsável:** Maria Santos (CPF: ***.456.789-**)")
        st.success("STATUS: MATRÍCULA ATIVA & EXAME MÉDICO OK")

# 8. OUVIDORIA E MANUTENÇÃO
elif menu == "📣 Ouvidoria & Manutenção (Voz do Esporte)":
    st.title("📣 Ouvidoria e Chamados de Manutenção")
    st.caption("Relato direto da comunidade e professores com envio de fotos")
    
    st.selectbox("Selecione o Equipamento com Problema:", ["Quadra Bairro Esperança", "Ginásio Central", "Campo Periferia"])
    st.selectbox("Tipo de Problema:", ["Iluminação / Lâmpada Queimada", "Alambrado Danificado", "Vazamento / Banheiro", "Piso Irregular"])
    st.text_area("Descreva a situação encontrada:")
    st.file_uploader("Envie uma foto do local (opcional):", type=["jpg", "png"])
    if st.button("Enviar Chamado para a Manutenção"):
        st.success("Chamado registrado no sistema da Secretaria!")

# 9. FICHAS TÉCNICAS E EDITAIS
elif menu == "📝 Fichas Técnicas & Mapeador de Editais":
    st.title("📝 Mapeamento de Editais & Fichas Técnicas")
    
    st.subheader("Propostas e Emendas Parlamentares")
    st.dataframe(pd.DataFrame({
        "Nº Proposta": ["EMD-2026-001", "LC-222-2026"],
        "Fonte / Origem": ["Emenda Parlamentar Federal", "Lei de Incentivo (LC 222/2025)"],
        "Valor Solicitado": ["R$ 150.000,00", "R$ 300.000,00"],
        "Status": ["Em Análise", "Aprovado no Transferegov"]
    }), use_container_width=True)

# 10. CHECKLIST DE PRESTAÇÃO DE CONTAS
elif menu == "✅ Checklist de Prestação de Contas (TCE)":
    st.title("✅ Checklist de Governança e Tribunal de Contas")
    
    items = [
        "Plano de Trabalho aprovado publicado em Diário Oficial",
        "Listas de frequência mensais assinadas pelos alunos/professores",
        "Notas Fiscais liquidadas e conciliadas com extrato bancário",
        "Fotos datadas das sessões de atividades com autorização de imagem",
        "Pesquisa de satisfação comunitária aplicada",
        "Relatório de Execução Físico-Financeiro assinado pelo Secretário"
    ]
    
    for item in items:
        st.checkbox(f"✔️ {item}", value=True)
        
    st.info("Conformidade de Auditoria: 100% dos documentos validados.")