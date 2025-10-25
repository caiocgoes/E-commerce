import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Dashboard E-commerce",  # título da aba
    page_icon="📊",                     # emoji que vai aparecer como ícone
    layout="wide"                       # opcional: deixa o app mais largo
)

#st.sidebar.image(
#    "C:\\Users\\caioc\\Documents\\CURSO_DATA_SCIENCE_COMUNIDADE_DS\\Formação_DS\\Projetos\\Projeto_Ecom_1_Data_Analysis\\ECOM\\e.png",
#    use_column_width=True
#)


# ==============================
# MENU LATERAL
# ==============================
with st.sidebar:
    escolha = option_menu(
        menu_title="Menu",
        options=["Vendas Geral", "Clientes"],
        icons=["sales", "customer-service"],
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0f2242", "border-radius": "0px", "border": "none"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {"color": "white", "font-size": "16px", "text-align": "left", "margin": "5px", "--hover-color": "#133863"},
            "nav-link-selected": {"background-color": "#133863"},
            "menu-title": {"color": "white", "font-size": "20px", "font-weight": "bold"}
        }
    )

# ==============================
# CSS PARA CUSTOMIZAÇÃO
# ==============================
st.markdown("""
<style>
.stApp {background-color: #0f2242; color: white;}
[data-testid="stSidebar"] {background-color: #112d57;}
h1, h2, h3 {color: white;}
.metric-card {background-color: #142b4f; padding: 20px; border-radius: 15px; text-align: left; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);}
.metric-card h3 {font-size: 22px; margin: 0; color: white;}
.metric-card p {font-size: 28px; font-weight: bold; margin: 0; color: white;}
header {visibility: hidden;}         
</style>
""", unsafe_allow_html=True)



# ==============================
# PÁGINA VENDAS GERAL
# ==============================
if escolha == "Vendas Geral":

    st.subheader("VISÃO GERAL DE VENDAS")

    @st.cache_data
    def load_data_vendas():
        df = pd.read_csv(r"C:\Users\caioc\Documents\CURSO_DATA_SCIENCE_COMUNIDADE_DS\PROJETO_ECOM\VENDAS_GERAL_ALTERADO.csv")
        df['produto'] = df['produto'].fillna("Não Encontrado")
        df['categoria'] = df['categoria'].fillna("Não Encontrado")
        df['tipo_pagamento'] = df['tipo_pagamento'].fillna("Não Encontrado")
        df['faturamento'] = df['faturamento'].fillna(0)
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])
        return df

    df = load_data_vendas()

    # ==============================
    # FILTROS SIDEBAR
    # ==============================
    st.sidebar.title("📅 Período")
    min_date = df['data_criacao'].min().date()
    max_date = df['data_criacao'].max().date()
    date_range = st.sidebar.slider("", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="DD/MM/YYYY")
    start, end = date_range
    df = df[(df["data_criacao"] >= pd.to_datetime(start)) & (df["data_criacao"] <= pd.to_datetime(end))]

    st.sidebar.title("📦 Status")
    status = st.sidebar.multiselect("", options=df["status"].unique(), default=df["status"].unique())
    if status:
        df = df[df["status"].isin(status)]

    st.sidebar.title("🏷 Categoria")
    categorias = sorted(df['categoria'].dropna().unique().tolist())
    categorias.insert(0, "Todas")
    categoria = st.sidebar.selectbox("🏷 Selecione a categoria:", categorias)
    if categoria != "Todas":
        df = df[df['categoria'] == categoria]

    # ==============================
    # KPIs
    # ==============================
    col1, col2, col3 = st.columns(3)
    total_pedidos = df['pedido_id'].nunique()
    ticket_medio = df['faturamento'].sum() / total_pedidos if total_pedidos > 0 else 0

    with col1:
        st.markdown(f'<div class="metric-card"><h3>💰 Faturamento</h3><p>R$ {df["faturamento"].sum():,.2f}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>🛒 Total de Pedidos</h3><p>{total_pedidos:,}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>📊 Ticket Médio</h3><p>R$ {ticket_medio:,.2f}</p></div>', unsafe_allow_html=True)

    # ==============================
    # GRÁFICO DE LINHA
    # ==============================
    df_line = df.groupby(df['data_criacao'].dt.date)[["faturamento"]].sum().reset_index().rename(columns={"data_criacao": "Data", "faturamento": "Faturamento"})
    df_line.columns = ["Data", "Faturamento"]
    fig_line = px.area(df_line, x="Data", y="Faturamento")
    fig_line.update_layout(plot_bgcolor="#0f2242", paper_bgcolor="#0f2242", font=dict(color="white"), title=dict(text="📈 Faturamento ao longo do tempo", font=dict(color="white", size=24)))
    st.plotly_chart(fig_line, use_container_width=True)

    # ==============================
    # GRÁFICOS DE PIZZA + TABELA
    # ==============================
    col4, col5, col6 = st.columns([1,1,1.2])

    with col4:
        st.subheader("🏷 Top Categorias com maior faturamento")
        df_cat = df.groupby("categoria")[["faturamento"]].sum().sort_values(by='faturamento', ascending=False).head(5).reset_index()
        fig_cat = px.pie(df_cat, values="faturamento", names="categoria")
        fig_cat.update_layout(plot_bgcolor="#0f2242", paper_bgcolor="#0f2242", font=dict(color="white"), legend=dict(font=dict(color="white")))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col5:
        st.subheader("💳 Faturamento por método de pagamento")
                                
            # Filtra valores válidos
        df_pgto = df[
            df['tipo_pagamento'].notna() &
            (~df['tipo_pagamento'].isin(['Não Encontrado', 'not_defined']))
        ]

        # Agrega faturamento por tipo de pagamento
        df_pgto = (
            df_pgto.groupby("tipo_pagamento")[["faturamento"]]
            .sum()
            .sort_values(by="faturamento", ascending=False)
            .reset_index()
        )

        # Calcula porcentagem para controlar rótulos
        total = df_pgto["faturamento"].sum()
        df_pgto["pct"] = df_pgto["faturamento"] / total

        # Cria gráfico
        fig_pgto = px.pie(
            df_pgto,
            values="faturamento",
            names="tipo_pagamento",
        )

        # Mostra rótulos só para fatias maiores
        fig_pgto.update_traces(
            textinfo="percent+label",
            textfont_size=14,
            textposition="inside",
            insidetextorientation="horizontal",
            texttemplate=[
                f"{name}<br>{pct:.1%}" if pct > 0.03 else ""
                for name, pct in zip(df_pgto["tipo_pagamento"], df_pgto["pct"])
            ],
            hovertemplate="%{label}: %{percent:.1%}<br>R$ %{value:,.2f}<extra></extra>"
        )

        # Layout escuro e harmônico
        fig_pgto.update_layout(
            plot_bgcolor="#0f2242",
            paper_bgcolor="#0f2242",
            font=dict(color="white"),
            legend=dict(font=dict(color="white")),
            margin=dict(t=50, b=50, l=50, r=50)
        )

        st.plotly_chart(fig_pgto, use_container_width=True)
    with col6:
        st.subheader("📋 Faturamento e Pedidos por Produto")
        df_faturamento = df.groupby("produto").agg(faturamento=("faturamento", "sum"), total_pedidos=("pedido_id", "nunique")).reset_index()
        df_faturamento = df_faturamento[df_faturamento['produto'] != "Não Encontrado"].sort_values(by="faturamento", ascending=False)
        fig_table = go.Figure(data=[go.Table(header=dict(values=["<b>Produto</b>", "<b>Faturamento (R$)</b>", "<b>Total de Pedidos</b>"], fill_color="#142b4f", font=dict(color="white", size=14), align="center"),
                                     cells=dict(values=[df_faturamento['produto'], df_faturamento['faturamento'], df_faturamento['total_pedidos']], fill_color=[["#0f2242", "#112d57"] * (len(df_faturamento)//2 + 1)], align="center", font=dict(color="white", size=12), format=["", ",.2f", ",d"]))])
        fig_table.update_layout(margin=dict(l=0,r=10,t=50,b=10), paper_bgcolor="#0f2242", width=2000, height=500)
        st.plotly_chart(fig_table, use_container_width=True)


# ==============================
# PÁGINA CLIENTES
# ==============================
elif escolha == "Clientes":

    st.subheader("VISÃO DE CLIENTES")

    @st.cache_data
    def load_data_clientes():
        df = pd.read_csv(r"C:\Users\caioc\Documents\CURSO_DATA_SCIENCE_COMUNIDADE_DS\PROJETO_ECOM\VENDAS_CLIENTE_VENDEDOR_CIDADE.csv")
        df['estado'] = df['estado'].fillna("Não Encontrado")
        df['latitude'] = df['latitude'].fillna("Não Encontrado")
        df['longitude'] = df['longitude'].fillna("Não Encontrado")
        df['DIA'] = pd.to_datetime(df['DIA'], errors='coerce')
        return df

    df = load_data_clientes()
    df_pedidos = df.groupby("pedido", as_index=False).agg({
        "DIA":"first",
        "faturamento": "first",
        "vendedor": "first",
        "cliente": "first",
        "estado": "first",
        "latitude": "first",
        "longitude": "first"
    })

    # ==============================
    # FILTROS SIDEBAR CLIENTES
    # ==============================
    st.sidebar.title("📅 Período")
    min_date = df['DIA'].min().date()
    max_date = df['DIA'].max().date()
    date_range = st.sidebar.slider("", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="DD/MM/YYYY")
    start, end = date_range
    df = df[(df["DIA"] >= pd.to_datetime(start)) & (df["DIA"] <= pd.to_datetime(end))]
    df_pedidos = df_pedidos[(df_pedidos["DIA"] >= pd.to_datetime(start)) & (df_pedidos["DIA"] <= pd.to_datetime(end))]

    st.sidebar.title("🏳️ Estado")
    df = df[df['estado'] != "Não Encontrado"]
    df_pedidos = df_pedidos[df_pedidos['estado'] != "Não Encontrado"]
    estados = sorted(df['estado'].unique().tolist())
    estados.insert(0, "Tudo")
    estado = st.sidebar.selectbox("Selecione o estado:", estados)
    if estado != "Tudo":
        df = df[df['estado'] == estado]
        df_pedidos = df_pedidos[df_pedidos['estado'] == estado]

    # ==============================
    # KPIs CLIENTES
    # ==============================
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>👤 Total de clientes</h3><p>{df["cliente"].nunique():,}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>🗣 Total de vendedores</h3><p>{df["vendedor"].nunique():,}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>🏳️ Total de estados</h3><p>{df["estado"].nunique():,}</p></div>', unsafe_allow_html=True)

    # ==============================
    # GRÁFICO DE CLIENTES E MAPAS
    # ==============================
    col4, col5 = st.columns([1,1])

    # ----- Tabela por cliente -----
    with col4:
        st.subheader("📋 Faturamento, ticket médio por cliente")
        cliente_stats = df_pedidos.groupby("cliente").agg(faturamento_total=("faturamento", "sum"), ticket_medio=("faturamento", "mean")).reset_index().sort_values(by="faturamento_total", ascending=False)
        cliente_stats = cliente_stats[cliente_stats['cliente'] != "Não Encontrado"]
        fig_table = go.Figure(data=[go.Table(header=dict(values=["<b>Cliente</b>", "<b>Faturamento (R$)</b>", "<b>Ticket Médio</b>"], fill_color="royalblue", font=dict(color="white", size=14), align="center"),
                                           cells=dict(values=[cliente_stats['cliente'], cliente_stats['faturamento_total'], cliente_stats['ticket_medio']],
                                                      fill_color=[["#0f2242", "#112d57"]*(len(cliente_stats)//2 + 1)],
                                                      align="center", font=dict(color="white", size=12), format=["", ",.2f", ",.2f"]))])
        fig_table.update_layout(margin=dict(l=0,r=10,t=50,b=10), paper_bgcolor="#0f2242", width=2000, height=500)
        st.plotly_chart(fig_table, use_container_width=True)

    # ----- Mapa de bolhas -----
    with col5:
        st.subheader("🌐 Faturamento por região")
        df_pedidos_mapa = df_pedidos.groupby("pedido", as_index=False).agg({"faturamento": "first", "latitude": "first", "longitude": "first"})
        mapa_bolhas = px.scatter_mapbox(df_pedidos_mapa, lat="latitude", lon="longitude", size="faturamento",
                                       color=np.log1p(df_pedidos_mapa["faturamento"]), color_continuous_scale="YlOrBr",
                                       hover_data={"faturamento": True}, zoom=3, center={"lat": -15.8, "lon": -47.9}, height=550, width=900)
        mapa_bolhas.update_traces(marker=dict(sizemode="area", sizeref=2.*max(df_pedidos_mapa["faturamento"])/(40.**2), sizemin=3))
        mapa_bolhas.update_layout(mapbox_style="open-street-map", paper_bgcolor="#0f2242", plot_bgcolor="#0f2242", font=dict(color="white"))
        st.plotly_chart(mapa_bolhas, use_container_width=False)

    # ----- Tabela de vendedores -----
    col6, col7 = st.columns([1,1])
    with col6:
        st.subheader("📋 Faturamento, ticket médio e total de pedidos por vendedor")
        vendedor_stats = df_pedidos.groupby("vendedor").agg(faturamento_total=("faturamento", "sum"), total_pedidos=("pedido", "count"), ticket_medio=("faturamento", "mean")).reset_index().sort_values(by='faturamento_total', ascending=False)
        vendedor_stats = vendedor_stats[vendedor_stats['vendedor'] != "Não Encontrado"]
        fig = go.Figure(data=[go.Table(header=dict(values=["<b>Vendedor</b>", "<b>Faturamento (R$)</b>", "<b>Total de Pedidos</b>", "<b>Ticket Médio</b>"],
                                                   fill_color="royalblue", font=dict(color="white", size=14), align="center"),
                                       cells=dict(values=[vendedor_stats['vendedor'], vendedor_stats['faturamento_total'], vendedor_stats['total_pedidos'], vendedor_stats['ticket_medio']],
                                                  fill_color=[["#0f2242","#112d57"]*(len(vendedor_stats)//2 + 1)],
                                                  align="center", font=dict(color="white", size=12), format=["",",.2f",",d",",.2f"]))])
        fig.update_layout(margin=dict(l=0,r=10,t=50,b=10), paper_bgcolor="#0f2242", width=2000, height=500)
        st.plotly_chart(fig, use_container_width=True)

    # ----- Gráfico faturamento por estado -----
    with col7:
        st.subheader("📈 Faturamento por estado")
        estado_stats = df_pedidos.groupby("estado").agg(faturamento_total=("faturamento", "sum"), total_pedidos=("pedido", "count"), ticket_medio=("faturamento", "mean")).reset_index().sort_values(by='faturamento_total', ascending=False)
        top_estados = estado_stats.head(5)
        norm = plt.Normalize(top_estados['faturamento_total'].min(), top_estados['faturamento_total'].max())
        colors = plt.cm.viridis(norm(top_estados['faturamento_total']))
        def format_milhar_milhao(valor):
            if valor >= 1_000_000:
                return f'{valor / 1_000_000:.1f} mi'
            else:
                return f'{valor / 1_000:.1f} mil'
        fig_f = plt.figure(figsize=(12,7))
        ax = sns.barplot(x='faturamento_total', y='estado', data=top_estados, palette=colors)
        for i, (valor, estado) in enumerate(zip(top_estados['faturamento_total'], top_estados['estado'])):
            ax.text(valor + 0.01*top_estados['faturamento_total'].max(), i, format_milhar_milhao(valor), va='center', fontsize=10, color='white')
        ax.set_xlim(0, top_estados['faturamento_total'].max() * 1.15)
        ax.set_facecolor("#0f2242")
        fig_f.patch.set_facecolor("#0f2242")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        ax.set_xlabel("")
        ax.set_ylabel("")
        st.pyplot(fig_f)
