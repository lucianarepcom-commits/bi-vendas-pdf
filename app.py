import plotly.express as px

# lista de vendas já extraída pelo seu código
df = pd.DataFrame(dados_vendas)

if not df.empty:

    # ➤ KPIs no topo
    total_vendas = df["Valor Unitário"].apply(lambda x: float(x.replace(",", "."))).sum()
    total_clientes = df["Cliente"].nunique()
    total_itens = df["Produto"].count()

    st.metric("💰 Total vendido", f"R$ {total_vendas:,.2f}")
    st.metric("👥 Clientes únicos", total_clientes)
    st.metric("📦 Itens vendidos", total_itens)

    # ➤ Top 10 Clientes
    top_clientes = df.groupby("Cliente").size().sort_values(ascending=False).head(10).reset_index(name="Quantidade")
    fig1 = px.bar(top_clientes, x="Cliente", y="Quantidade", title="Top 10 Clientes que mais compram")
    st.plotly_chart(fig1)

    # ➤ Top 10 Produtos
    top_produtos = df.groupby("Produto").size().sort_values(ascending=False).head(10).reset_index(name="Quantidade")
    fig2 = px.bar(top_produtos, x="Produto", y="Quantidade", title="Top 10 Produtos mais vendidos")
    st.plotly_chart(fig2)

    # ➤ Vendas por período
    df["Data"] = pd.to_datetime(df["Data"])
    vendas_tempo = df.groupby(df["Data"].dt.to_period("M")).size().reset_index(name="Quantidade")
    vendas_tempo["Data"] = vendas_tempo["Data"].dt.to_timestamp()
    fig3 = px.line(vendas_tempo, x="Data", y="Quantidade", title="Vendas por mês")
    st.plotly_chart(fig3)
