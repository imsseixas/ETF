import streamlit as st
import storage
import scraper
import ai_engine
import pandas as pd

st.set_page_config(page_title="Financial Platform IA", layout="wide")
st.title("📈 Dashboard Analítico - IA Financeira")

storage.init_db()

st.sidebar.markdown("### Configurações")
api_key = st.sidebar.text_input("Sua Chave API (Gemini)", type="password")
if api_key:
    ai_engine.configure_api(api_key)
    st.sidebar.success("API Key Carregada!")
else:
    st.sidebar.warning("Insira a API Key para liberar a Inteligência Artificial.")

st.sidebar.markdown("---")
st.sidebar.info("A raspagem usa Selenium otimizado. Note que sites como br.investing.com possuem bloqueios severos (Cloudflare) que podem retornar 0 eventos.")

tab1, tab2, tab3 = st.tabs(["📅 Calendário", "🤖 Veredito Setorial IA", "🔗 Monitor Inteligente"])

with tab1:
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader("Eventos Econômicos Locais")
    with col2:
        if st.button("🪄 Raspar Agora", use_container_width=True):
            with st.spinner("Acionando bot Selenium em background..."):
                count = scraper.scrape_economic_calendar()
                if count > 0:
                    st.success(f"{count} eventos atualizados no banco!")
                else:
                    st.error("0 eventos raspados. O Cloudflare bloqueou o robô ou não há eventos.")
                    
    events = storage.get_today_events()
    if events:
        df = pd.DataFrame(events)
        # Ocultamos a coluna ID e Timestamp para ficar clean
        if 'id' in df.columns:
            df = df.drop(columns=['id', 'timestamp'])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("O banco de dados está vazio. Pressione 'Raspar Agora' para popular a agenda.")

with tab2:
    st.subheader("Integração Gemini: Cruzamento Macro vs Micro")
    st.write("A IA lê os dados raspados na Tab 1 e gera um veredito instantâneo das expectativas para hoje.")
    
    if st.button("Gerar Análise Profunda"):
        if not api_key:
            st.error("Chave API ausente.")
        else:
            events = storage.get_today_events()
            if not events:
                st.warning("Não há dados macro para analisar. Faça a raspagem primeiro.")
            else:
                with st.spinner("O Gemini está analisando o impacto macroeconômico..."):
                    result = ai_engine.generate_verdict(events)
                    st.markdown("---")
                    st.markdown(result)

with tab3:
    st.subheader("Fila de Processamento Customizado (Options / ML Local)")
    st.write("Aqui você cadastra as URLs que o injetor Selenium vai varrer diariamente (Ex: TradingView AMEX-SOXS).")
    
    with st.form("add_url_form"):
        new_url = st.text_input("Nova URL para Monitoramento Contínuo")
        submit = st.form_submit_button("Inserir na Fila")
        if submit and new_url:
            st.success(f"A URL '{new_url}' foi posta na fila do injetor com sucesso.")
            # Futuramente: inserir no banco de dados na tabela monitored_urls
