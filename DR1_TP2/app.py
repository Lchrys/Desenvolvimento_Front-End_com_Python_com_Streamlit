import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
from plotly.subplots import make_subplots
import pydeck as pdk

st.title("TP2 - Desenvolvimento Front-End com Python (com Streamlit)")
st.subheader("Dashboard COVID-19 Brasil")

# PROCESSAMENTO
# Aqui decidi juntar todos os dados em um único Df
# junta os 12 CSVs do MS (2 partes por ano, 2020-2025) num único DataFrame
# cache_data evita reler todas linhas a cada rerun do Streamlit
# sep=";" porque o painel usa ponto e vírgula

@st.cache_data
def carregar_dados():
    arquivos = [
        "HIST_PAINEL_COVIDBR_2020_Parte1_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2020_Parte2_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2021_Parte1_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2021_Parte2_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2022_Parte1_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2022_Parte2_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2023_Parte1_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2023_Parte2_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2024_Parte1_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2024_Parte2_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2025_Parte1_05set2025.csv",
        "HIST_PAINEL_COVIDBR_2025_Parte2_05set2025.csv"
    ]

    lista_dfs = []
    for arquivo in arquivos:
        df_temp = pd.read_csv(f"dados_covid/{arquivo}", sep=";")
        lista_dfs.append(df_temp)

    return pd.concat(lista_dfs, ignore_index=True)

df = carregar_dados()
df["data"] = pd.to_datetime(df["data"])

# Ao logo deste TP, percebeu-se que os dados estavam sendo misturados, pois a semana epidemiológica 
# cai na virada do ano pertence a um ano só, então o ano do calendário precisa ser ajustado nos dois sentidos:
# - 01/01/2021 ainda é a semana 53 de 2020;
# - 31/12/2023 já é a semana 1 de 2024.
# Sem isso, esses dias caem em rótulos como "2021-S53" ou "2023-S01" e aparecem no
# lugar errado da linha do tempo, criando quedas e saltos falsos nos gráficos.
df["anoEpi"] = df["data"].dt.year

janeiro_da_semana_anterior = (df["data"].dt.month == 1) & (df["semanaEpi"] >= 52)
df.loc[janeiro_da_semana_anterior, "anoEpi"] = df["anoEpi"] - 1

dezembro_da_semana_seguinte = (df["data"].dt.month == 12) & (df["semanaEpi"] == 1)
df.loc[dezembro_da_semana_seguinte, "anoEpi"] = df["anoEpi"] + 1

# semanaEpi se repete todo ano; ano+semana impede misturar 2020-S01 com 2021-S01
df["anoSemana"] = (
    df["anoEpi"].astype(str)
    + "-S"
    + df["semanaEpi"].astype(int).astype(str).str.zfill(2))

# Último dia da série, usado para ler os totais acumulados
ultima_data = df["data"].max()
print(df)

# VISUALIZAÇÃO
# apenas para saber se os dados carregados estão corretos (de 2020-2025)
# OBS: percebe-se que há nulos
st.write("Primeiras 10 linhas:")
st.dataframe(df.head(10))

st.write("Últimas 10 linhas:")
st.dataframe(df.tail(10))


# EXERCÍCIO 1

st.header("1. Importância da Visualização de Dados:")
st.subheader("Explique a importância da visualização de dados no contexto de uma pandemia como a COVID-19. Como essas visualizações podem ajudar gestores de saúde pública e a população em geral a tomar decisões informadas?")

# VISUALIZAÇÃO
st.write("""
A visualização de dados é essencial durante uma pandemia porque transforma números 
complexos em informações fáceis de entender. Gráficos de casos e óbitos ajudam 
gestores de saúde pública a identificar tendências, como picos de contaminação, 
e tomar decisões rápidas, como reforçar restrições ou aumentar leitos hospitalares e 
recursos (debates comuns na época).
Para a população, essas visualizações tornam a situação da pandemia mais clara, 
ajudando as pessoas a entender o risco em sua região e a importância de medidas 
de prevenção. Sem gráficos, seria muito mais difícil interpretar milhares de 
linhas de dados brutos.
""")


# EXERCÍCIO 2

st.header("2. Gráfico de Barras com Streamlit:")
st.subheader("Usando os dados de casos novos de COVID-19 por semana epidemiológica de notificação, crie um gráfico de barras em Streamlit que mostre a evolução semanal dos casos em um determinado estado. Indique o estado escolhido e explique sua escolha.")

# PROCESSAMENTO
# Estado escolhido: São Paulo, porque o gráfico de barras mostra semanas de pico
# acima de 100 mil casos novos, o que deixa as ondas visíveis.
estado_escolhido = "SP"

# Município nulo = dado agregado do estado
df_estado = df[(df["estado"] == estado_escolhido) & (df["codmun"].isna())]
casos_semana = df_estado.groupby("anoSemana")["casosNovos"].sum()
print(casos_semana)

# VISUALIZAÇÃO
st.write(f"Estado selecionado: **{estado_escolhido}**")
st.bar_chart(casos_semana)

st.write("""
O estado escolhido foi São Paulo. No gráfico de barras, as semanas de pico 
passam de 100 mil casos novos, com o maior valor na semana 2021-S24 (cerca de 
120 mil), o que torna as ondas da série fáceis de identificar.
As barras mostram ondas bem definidas, e não um crescimento contínuo: o pico 
mais alto está em 2021, e depois as barras caem e ficam baixas até o fim da série.
""")


# EXERCÍCIO 3

st.header("3. Gráfico de Linha com Streamlit:")
st.subheader("Crie um gráfico de linha utilizando Streamlit para representar o número de óbitos acumulados por COVID-19 ao longo das semanas epidemiológicas de notificação para todo o Brasil. Explique como a curva de óbitos acumulados pode ser interpretada.")

# PROCESSAMENTO
df_brasil = df[df["regiao"] == "Brasil"]
obitos_semana = df_brasil.groupby("anoSemana")["obitosAcumulado"].max()
print(obitos_semana)

# VISUALIZAÇÃO
st.line_chart(obitos_semana)

st.write("""
A curva de óbitos acumulados representa o total de mortes registradas desde o 
início da pandemia, chegando a cerca de 717 mil no fim da série. A inclinação 
mostra o ritmo dos registros: quando a linha sobe rapidamente, muitos óbitos foram 
notificados naquele período; quando fica mais achatada, o número de novos óbitos 
por semana diminuiu.
Os trechos mais inclinados estão no primeiro semestre de 2021, quando o total sai 
de cerca de 203 mil na semana 2021-S01 para 524 mil na semana 2021-S26.
""")


# EXERCÍCIO 4

st.header("4. Gráfico de Área com Streamlit:")
st.subheader("Utilizando os dados de casos acumulados por COVID-19, crie um gráfico de área em Streamlit para comparar a evolução dos casos em três estados diferentes. Explique as diferenças observadas entre os estados escolhidos.")

# PROCESSAMENTO
# Três estados diferentes, para comparar o ritmo de crescimento
estados_area = ["SP", "RJ", "AM"]

df_estados = df[(df["estado"].isin(estados_area)) & (df["codmun"].isna())]
casos_area = df_estados.groupby(["anoSemana", "estado"])["casosAcumulado"].max().reset_index()

# Formato "wide" (uma coluna por estado) para o st.area_chart
casos_area_pivot = casos_area.pivot(index="anoSemana", columns="estado", values="casosAcumulado")

# Ordena os estados do maior para o menor volume, calculando isso a partir dos
# dados: assim as áreas menores são desenhadas por último e ficam visíveis.
maximo_por_estado = casos_area_pivot.max()
ordem_estados = maximo_por_estado.sort_values(ascending=False).index
casos_area_pivot = casos_area_pivot[ordem_estados]
print(casos_area_pivot)

# VISUALIZAÇÃO
# stack="layered" sobrepõe as áreas com transparência. Sem isso, o Streamlit
# empilha as séries e o total de São Paulo esconde os demais estados.
st.area_chart(casos_area_pivot, stack="layered")

st.write("""
Como o gráfico usa casos acumulados, as três curvas apenas crescem ao longo do 
tempo. No fim da série São Paulo chega a cerca de 7,0 milhões de casos, o Rio de 
Janeiro a 3,0 milhões e o Amazonas a 650 mil, então a área de São Paulo é sempre 
a mais alta das três.
Os trechos mais inclinados de cada área indicam as semanas em que os casos 
cresceram mais rápido, e os trechos quase horizontais indicam semanas com poucos 
casos novos registrados. As áreas são sobrepostas, e não empilhadas, para que as 
três curvas sejam lidas a partir da mesma base.
""")


# EXERCÍCIO 5

st.header("5. Mapa com Streamlit:")
st.subheader("Crie um mapa interativo utilizando a função st.map do Streamlit que mostre a distribuição dos casos acumulados de COVID-19 por município em um estado específico. Explique como esse tipo de visualização pode ajudar na análise geográfica da pandemia.")

# PROCESSAMENTO
# Coordenadas obtidas no Google Maps para 5 municípios do estado.
# A coluna codmun do dataset usa o código IBGE de 6 dígitos (sem o dígito verificador).
estado_mapa = "RJ"

dados_mapa = pd.DataFrame({
    "municipio": ["Rio de Janeiro", "Niterói", "Duque de Caxias", "Nova Iguaçu", "Petrópolis"],
    "codmun": [330455, 330330, 330170, 330350, 330390],
    "latitude": [-22.9068, -22.8833, -22.7856, -22.7592, -22.5112],
    "longitude": [-43.1729, -43.1036, -43.3117, -43.4511, -43.1779]
})

# Casos acumulados de cada município no último dia da série.
# Aqui não serve usar max(): nas linhas de município o dataset tem dias em que o
# acumulado vem dobrado ou zerado, então o maior valor da coluna não é o total real.
casos = []
for codigo in dados_mapa["codmun"]:
    df_municipio = df[(df["codmun"] == codigo) & (df["data"] == ultima_data)]
    casos.append(df_municipio["casosAcumulado"].iloc[0])

dados_mapa["casosAcumulado"] = casos

# Círculo proporcional aos casos, com o maior município em 3000 metros de raio
maximo = dados_mapa["casosAcumulado"].max()
dados_mapa["tamanho_circulo"] = dados_mapa["casosAcumulado"] / maximo * 3000
print(dados_mapa)

# VISUALIZAÇÃO
st.write(f"Estado selecionado: **{estado_mapa}**")
st.map(dados_mapa, latitude="latitude", longitude="longitude", size="tamanho_circulo")

st.write("""
O mapa mostra cinco municípios do Rio de Janeiro, com o tamanho do círculo 
proporcional aos casos acumulados de cada um. As coordenadas de latitude e 
longitude foram obtidas no Google Maps. O recorte é desses cinco pontos, e não 
de todos os municípios do estado.
Entre eles, apenas o círculo da capital aparece grande, enquanto os outros quatro 
ficam pequenos: os casos acumulados deste recorte estão concentrados no município 
do Rio de Janeiro. Esse tipo de visualização mostra a distribuição dos casos sobre 
o território, e não apenas em uma lista de valores, permitindo localizar onde estão 
os municípios mais afetados e como eles se posicionam em relação aos vizinhos.
""")


# EXERCÍCIO 6

st.header("6. Visualização com Matplotlib:")
st.subheader("Utilize a biblioteca Matplotlib para criar um gráfico de barras que mostre a comparação entre os casos novos e os óbitos novos de COVID-19 por estado na semana epidemiológica mais recente disponível. Explique o que os dados sugerem sobre a relação entre casos e óbitos.")

# PROCESSAMENTO
df_estados_todos = df[df["codmun"].isna() & df["estado"].notna()]

# As últimas semanas do dataset têm tudo zerado, então procuramos a semana mais
# recente que ainda registrou algum caso ou óbito.
casos_novos = df_estados_todos["casosNovos"].fillna(0)
obitos_novos = df_estados_todos["obitosNovos"].fillna(0)
df_com_registro = df_estados_todos[(casos_novos != 0) | (obitos_novos != 0)]

data_mais_recente = df_com_registro["data"].max()
semana_mais_recente = df_com_registro[df_com_registro["data"] == data_mais_recente]["anoSemana"].iloc[0]

df_semana_recente = df_estados_todos[df_estados_todos["anoSemana"] == semana_mais_recente]
resumo_estados = df_semana_recente.groupby("estado")[["casosNovos", "obitosNovos"]].sum()
print(semana_mais_recente)
print(resumo_estados)

# VISUALIZAÇÃO
fig, ax = plt.subplots(figsize=(12, 6))
resumo_estados.plot(kind="bar", ax=ax)
ax.set_title(f"Casos Novos vs Óbitos Novos por Estado - Semana {semana_mais_recente}")
ax.set_xlabel("Estado")
ax.set_ylabel("Quantidade")
st.pyplot(fig)

st.write("""
O gráfico compara casos novos e óbitos novos por estado na semana mais recente com 
registros no dataset, indicada no título. São Paulo tem a barra de casos mais alta, 
pouco acima de 2.000, seguido pelo Rio de Janeiro.
As barras de óbitos novos ficam rentes ao eixo em todos os estados, porque nessa 
semana os óbitos registrados são poucos diante do número de casos. Por isso este 
gráfico permite comparar o volume de casos entre os estados, mas não a relação 
entre casos e óbitos: na escala dos casos, os óbitos ficam indistinguíveis de zero.
""")


# EXERCÍCIO 7

st.header("7. Boxplot com Seaborn:")
st.subheader("Usando a biblioteca Seaborn, crie um boxplot que compare a distribuição dos casos novos de COVID-19 por semana epidemiológica entre três regiões do Brasil (Norte, Nordeste, Sudeste). Explique as principais diferenças observadas.")

# PROCESSAMENTO
# os dados regionais são registrados por estado, então os estados são somados por região
df_regioes = df[(df["regiao"].isin(["Norte", "Nordeste", "Sudeste"])) &
                (df["estado"].notna()) & (df["codmun"].isna())]
df_regioes = df_regioes.groupby(["regiao", "anoSemana"], as_index=False)["casosNovos"].sum()
print(df_regioes)

# VISUALIZAÇÃO
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_regioes, x="regiao", y="casosNovos", ax=ax)
ax.set_title("Distribuição de Casos Novos por Região")
ax.set_xlabel("Região")
ax.set_ylabel("Casos Novos")
st.pyplot(fig)

st.write("""
Cada ponto do gráfico é uma semana epidemiológica: o valor no eixo vertical é a 
soma dos casos novos daquela semana na região. O boxplot resume todas as semanas 
da série em uma caixa por região.
A linha no meio da caixa é a mediana: metade das semanas teve menos casos que 
esse valor, e a outra metade teve mais. A caixa vai do 1º ao 3º quartil, ou seja, 
das 25% semanas mais baixas até as 25% mais altas, e concentra as semanas "típicas". 
Os traços verticais (bigodes) vão até as semanas ainda consideradas dentro da 
variação comum. Os pontos isolados são outliers, ou seja, semanas bem acima ou bem abaixo 
desse intervalo.
A caixa do Sudeste é a mais alta e a mais alongada, com a mediana acima das outras 
duas, pois nas semanas comuns essa região registra mais casos e também varia mais de 
uma semana para outra. O Nordeste fica no meio. O Norte tem a caixa mais baixa e 
mais estreita, com a menor variação entre as semanas.
As três regiões têm muitos pontos acima do bigode superior. São as semanas de pico, 
e o ponto mais alto do gráfico pertence ao Sudeste (maior volume de casos).
Também há pontos abaixo de zero: semanas em que a soma de casosNovos ficou negativa 
porque o acumulado foi corrigido para baixo na fonte.
""")


# EXERCÍCIO 8

st.header("8. Gráfico de Área com Altair:")
st.subheader("Crie um gráfico de área em Altair para mostrar a evolução dos casos novos de COVID-19 por semana epidemiológica de notificação em uma determinada região do Brasil. Explique a escolha da região e as tendências observadas nos dados.")

# PROCESSAMENTO
# Região escolhida: Nordeste, a segunda com maior volume de casos entre as três
# regiões comparadas no boxplot da questão 7.
regiao_escolhida = "Nordeste"

df_regiao_altair = df[(df["regiao"] == regiao_escolhida) &
                      (df["estado"].notna()) & (df["codmun"].isna())]
df_regiao_altair = df_regiao_altair.groupby("anoSemana", as_index=False)["casosNovos"].sum()
print(df_regiao_altair)

# VISUALIZAÇÃO
grafico_area = alt.Chart(df_regiao_altair).mark_area(opacity=0.6).encode(
    x="anoSemana:N",
    y="casosNovos:Q"
).properties(
    title=f"Casos Novos por Semana Epidemiológica - {regiao_escolhida}",
    width=700,
    height=400
)

st.altair_chart(grafico_area)

st.write("""
A região escolhida foi o Nordeste, que no boxplot da questão 7 aparece como a 
segunda em volume de casos novos semanais entre as três regiões comparadas.
O gráfico mostra os casos novos semanais da região ao longo de toda a série. A área 
evidencia ondas separadas, e não um crescimento contínuo, a maior delas está no 
início de 2022, quando a área atinge o topo do eixo, com pouco mais de 250 mil 
casos em uma única semana, e há uma onda anterior menor em meados de 2021, em torno 
da metade dessa altura.
Entre as ondas a área cai para perto de zero, o que permite identificar tanto os 
momentos de alta quanto os períodos de poucos registros. E novamente, como visto,
é possível identificar a queda a partir de 2023 e estabilidade de novos casos.
""")


# EXERCÍCIO 9

st.header("9. Heatmap com Altair:")
st.subheader("Desenvolva um heatmap em Altair que mostre a correlação entre casos novos, óbitos novos e leitos hospitalares ocupados (caso os dados estejam disponíveis) em um determinado estado. Explique as possíveis correlações observadas.")

# PROCESSAMENTO
# O dataset não tem leitos ocupados, e Recuperadosnovos / emAcompanhamentoNovos
# vêm vazios nas linhas de estado. A terceira variável é casosAcumulado, que existe
# no recorte estadual e mede o total de casos até aquele dia.
estado_heatmap = "SP"

df_estado_heatmap = df[(df["estado"] == estado_heatmap) & (df["codmun"].isna())]

correlacao = df_estado_heatmap[
    ["casosNovos", "obitosNovos", "casosAcumulado"]
].corr().reset_index()
correlacao = correlacao.melt(id_vars="index")
correlacao.columns = ["variavel_1", "variavel_2", "correlacao"]
correlacao["correlacao"] = correlacao["correlacao"].round(2)
print(correlacao)

# VISUALIZAÇÃO
heatmap = alt.Chart(correlacao).mark_rect().encode(
    x="variavel_1:O",
    y="variavel_2:O",
    color="correlacao:Q"
)

numeros = alt.Chart(correlacao).mark_text().encode(
    x="variavel_1:O",
    y="variavel_2:O",
    text="correlacao:Q"
)

st.altair_chart((heatmap + numeros).properties(
    title=f"Correlação - {estado_heatmap} (casos novos, óbitos novos e casos acumulados)",
    width=400,
    height=400
))

st.write("""
O dataset não possui leitos hospitalares ocupados. A terceira variável usada foi 
casosAcumulado, o total de casos até cada dia, que está preenchida nas linhas de 
estado. O recorte é São Paulo.
A diagonal vale 1,00, porque é a correlação de cada variável consigo mesma.
Casos novos e óbitos novos têm correlação 0,82: na série inteira os dois sobem e 
descem juntos. Isso não aparece no gráfico da questão 6, que mostra só uma semana 
e na qual as barras de óbitos ficam rentes ao eixo.
Casos acumulados correlaciona de forma negativa com casos novos (−0,43) e com 
óbitos novos (−0,47). Isso aparece porque o acumulado só cresce ao longo da série, 
enquanto os valores novos ficam menores depois das ondas de 2021 e 2022.
""")


# EXERCÍCIO 10

st.header("10. Gráfico de Pizza com Plotly:")
st.subheader("Usando Plotly, crie um gráfico de pizza (pie chart) que mostre a distribuição percentual dos casos acumulados de COVID-19 entre as cinco regiões do Brasil. Explique o que os dados revelam sobre a distribuição geográfica dos casos.")

# PROCESSAMENTO
# Nível estadual para poder somar por região
df_regioes_pizza = df[(df["estado"].notna()) & (df["codmun"].isna())]

data_mais_recente = df_regioes_pizza["data"].max()
df_recente = df_regioes_pizza[df_regioes_pizza["data"] == data_mais_recente]
casos_por_regiao = df_recente.groupby("regiao")["casosAcumulado"].sum().reset_index()
print(casos_por_regiao)

# VISUALIZAÇÃO
fig_pie = px.pie(casos_por_regiao,
                 names="regiao",
                 values="casosAcumulado",
                 title="Distribuição Percentual de Casos Acumulados por Região")

st.plotly_chart(fig_pie)

st.write("""
O gráfico de pizza mostra como o total de casos acumulados se reparte entre as 
cinco regiões do Brasil. A distribuição geográfica não é uniforme: o Sudeste 
concentra 40,0% dos registros, e as outras quatro regiões dividem o restante.
O Sudeste, sozinho, fica quase no dobro do Sul (21,1%) e em mais que o dobro do 
Nordeste (19,4%). Sul e Nordeste ficam próximos um do outro, com o Sul um pouco 
à frente. O Centro-Oeste tem 11,7% e o Norte, 7,7%, a menor fatia.
Somando Sudeste e Sul, mais de 60% dos casos acumulados do país estão no eixo 
Sul–Sudeste. Norte e Centro-Oeste juntos não chegam a 20%.
Essas fatias são volume absoluto de casos registrados, não casos por habitante.
""")


# EXERCÍCIO 11

st.header("11. Subplots com Plotly:")
st.subheader("Crie subplots em Plotly que mostrem, lado a lado, gráficos de barras comparando os casos novos e os óbitos novos de COVID-19 por semana epidemiológica em duas diferentes regiões do Brasil. Explique as diferenças observadas entre as regiões.")

# PROCESSAMENTO
regiao_1 = "Sudeste"
regiao_2 = "Norte"

df_r1 = df[(df["regiao"] == regiao_1) & (df["estado"].notna()) & (df["codmun"].isna())]
df_r2 = df[(df["regiao"] == regiao_2) & (df["estado"].notna()) & (df["codmun"].isna())]

resumo_r1 = df_r1.groupby("anoSemana")[["casosNovos", "obitosNovos"]].sum().reset_index()
resumo_r2 = df_r2.groupby("anoSemana")[["casosNovos", "obitosNovos"]].sum().reset_index()
print(resumo_r1)
print(resumo_r2)

# VISUALIZAÇÃO
fig1 = px.bar(resumo_r1,
              x="anoSemana",
              y=["casosNovos", "obitosNovos"],
              barmode="group")

fig2 = px.bar(resumo_r2,
              x="anoSemana",
              y=["casosNovos", "obitosNovos"],
              barmode="group")

fig_subplot = make_subplots(
    rows=1, cols=2,
    subplot_titles=(regiao_1, regiao_2),
    shared_yaxes=True
)

for trace in fig1.data:
    fig_subplot.add_trace(trace, row=1, col=1)

# A legenda do segundo painel é omitida para não repetir as mesmas séries
for trace in fig2.data:
    trace.showlegend = False
    fig_subplot.add_trace(trace, row=1, col=2)

fig_subplot.update_layout(
    title_text="Comparação de Casos Novos e Óbitos Novos por Semana Epidemiológica",
    barmode="group"
)

st.plotly_chart(fig_subplot)

st.write("""
Os dois painéis compartilham a mesma escala no eixo Y, então a altura das barras 
pode ser comparada diretamente entre as regiões. As barras do Norte ficam bem mais 
baixas que as do Sudeste no pico, pois o Sudeste passa de 500 mil casos novos em uma 
semana, enquanto o Norte não chega a 100 mil.
As duas regiões têm o pico de casos novos na mesma semana, no início de 2022, e 
apresentam ondas nos mesmos períodos. Nos dois painéis as barras de óbitos novos 
são muito menores que as de casos e ficam quase rentes ao eixo.
""")


# EXERCÍCIO 12

st.header("12. Mapa Interativo com PyDeck:")
st.subheader("Utilize PyDeck para criar um mapa interativo que mostre a densidade populacional ajustada para os casos acumulados de COVID-19 por município em uma determinada região do Brasil. Explique como a densidade populacional pode influenciar a disseminação da COVID-19.")

# PROCESSAMENTO
# Região escolhida: Nordeste.
# Coordenadas obtidas no Google Maps para 5 municípios da região.
# A coluna codmun do dataset usa o código IBGE de 6 dígitos (sem o dígito verificador).
dados_pydeck = pd.DataFrame({
    "municipio": ["Salvador - BA", "Recife - PE", "Fortaleza - CE", "Natal - RN", "São Luís - MA"],
    "codmun": [292740, 261160, 230440, 240810, 211130],
    "latitude": [-12.9777, -8.0476, -3.7319, -5.7945, -2.5307],
    "longitude": [-38.5016, -34.8770, -38.5267, -35.2110, -44.3068]
})

# Casos acumulados e população de cada município no último dia da série.
# Aqui não serve usar max(): nas linhas de município o dataset tem dias em que o
# acumulado vem dobrado ou zerado, então o maior valor da coluna não é o total real.
casos = []
populacoes = []
for codigo in dados_pydeck["codmun"]:
    df_municipio = df[(df["codmun"] == codigo) & (df["data"] == ultima_data)]
    casos.append(df_municipio["casosAcumulado"].iloc[0])
    populacoes.append(df_municipio["populacaoTCU2019"].iloc[0])

dados_pydeck["casosAcumulado"] = casos
dados_pydeck["populacao"] = populacoes

# Indicador ajustado pela população: casos por 100 mil habitantes
# Arredondado para o tooltip não mostrar um número com várias casas decimais
dados_pydeck["casos_por_100k"] = (dados_pydeck["casosAcumulado"] / dados_pydeck["populacao"] * 100000).round(0)

# Raio proporcional ao indicador, com o maior município em 20 km
maximo_100k = dados_pydeck["casos_por_100k"].max()
dados_pydeck["raio"] = dados_pydeck["casos_por_100k"] / maximo_100k * 20000
print(dados_pydeck)

# VISUALIZAÇÃO
nordeste_initial_view = pdk.ViewState(
    latitude=-8.0,
    longitude=-40.0,
    zoom=5,
    pitch=0
)

layer1 = pdk.Layer(
    "ScatterplotLayer",
    data=dados_pydeck,
    get_position=["longitude", "latitude"],
    get_radius="raio",
    get_fill_color=[255, 0, 0, 140],
    pickable=True
)

deck = pdk.Deck(
    initial_view_state=nordeste_initial_view,
    layers=[layer1],
    tooltip={"text": "{municipio}\nCasos por 100 mil hab: {casos_por_100k}"}
)

st.pydeck_chart(deck)

st.write("""
O mapa mostra cinco municípios do Nordeste, com o tamanho do círculo proporcional 
aos casos acumulados por 100 mil habitantes. As coordenadas de latitude e longitude 
foram obtidas no Google Maps, e o valor de cada município aparece ao passar o mouse 
sobre o círculo. O recorte é desses cinco pontos, e não de todos os municípios da 
região.
Recife tem o maior indicador do grupo, com 19.259 casos por 100 mil habitantes, 
seguido de Natal (18.221) e Fortaleza (15.978). Salvador fica em 12.399, e São Luís 
tem o menor, com 7.332. Como o indicador é ajustado pela população, o círculo maior 
não é o do município com mais casos registrados (Fortaleza, com cerca de 427 mil), 
e sim o daquele com mais casos por habitante.
O mapa não mede densidade (habitantes por km²). Ele compara municípios de tamanhos 
diferentes pela taxa. Em áreas mais densas as pessoas ficam mais próximas, o que 
pode favorecer a transmissão; por isso a taxa por 100 mil habitantes é mais 
adequada do que o número absoluto para essa comparação.
""")
