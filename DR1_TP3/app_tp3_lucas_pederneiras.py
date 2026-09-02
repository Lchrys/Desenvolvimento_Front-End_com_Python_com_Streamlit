# TP3 - Desenvolvimento Front-End com Python (com Streamlit)
# Turismo Rio - Data.Rio (via aérea e via marítima, 2006-2019)

# IA (Grok 4.6 high-performance) foi usada como apoio na escrita e revisão do código

# ------------------------------------------------------------------------------------------------

# io: lê e grava o XLS em memória (BytesIO)
# time: deixa o spinner visível por alguns segundos
# pandas: trata as tabelas
# plotly: pizza, histograma e scatter
# streamlit: interface
# xlwt: gera o XLS do download

import io
import time
import pandas as pd
import plotly.express as px
import streamlit as st
import xlwt

# ------------------------------------------------------------------------------------------------

# Meses na ordem do calendário (filtros e gráfico de linha)
MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Nomes de continente que aparecem nas planilhas
CONTINENTES = [
    "África",
    "América Central",
    "América Central e Caribe",
    "América do Norte",
    "América do Sul",
    "Ásia",
    "Europa",
    "Oceania",
    "Oriente Médio",
    "Países não especificados"]

# Troca "-", vazio ou texto inválido por 0
def limpar_numero(valor):
    if valor == "-" or valor == "" or pd.isna(valor):
        return 0
    try:
        return float(valor)
    except Exception:
        texto = str(valor).strip().replace(" ", "")
        try:
            return float(texto)
        except Exception:
            return 0


# Descobre se o arquivo é aéreo ou marítimo pelo nome (2675 e 2676)
def descobrir_via(nome_arquivo):
    nome = nome_arquivo.lower()
    if "2676" in nome:
        return "Marítima"
    if "2675" in nome:
        return "Aérea"
    return "Não identificada"


# Junta "América Central e Caribe" no mesmo grupo
def padronizar_continente(nome):
    if nome == "América Central e Caribe":
        return "América Central"
    return nome


# Formata número com ponto de milhar (ex.: 1.234)
def formatar_numero(valor):
    return f"{int(valor):,.0f}".replace(",", ".")


# 1) Escolha dos datasets e explicação do objetivo e motivação
# Mostra os datasets do Data.Rio, o objetivo, a motivação e o que o app faz
def mostrar_explicacao():
    st.header("Datasets, objetivo e motivação")
    st.write(
        """
        **Datasets escolhidos** (portal [Data.Rio](https://www.data.rio/): seção Turismo):

        1. [Chegada mensal de turistas por via aérea, segundo continentes e países
           de residência permanente (2006–2019)](https://www.data.rio/documents/a6c6c3ff7d1947a99648494e0745046d/about)
        2. [Chegada mensal de turistas por via marítima, segundo continentes e países
           de residência permanente (2006–2019)](https://www.data.rio/documents/45fa86aa30374bfabd369e6d64179071/about)

        **Objetivo:**
        Construir um painel interativo que permita explorar o fluxo de turistas
        internacionais que chegaram ao Rio de Janeiro ao longo de 14 anos,
        comparando as vias aérea e marítima com recortes por continente, país,
        ano e mês.

        **Motivação:**
        O Rio de Janeiro é um dos principais destinos turísticos do mundo,
        recebendo milhões de visitantes por ano. Entender de onde vêm esses
        turistas, quando chegam e por qual via é essencial para o
        planejamento do setor. Os dois datasets se complementam: a via aérea
        concentra o maior volume de chegadas, enquanto a via marítima revela o
        perfil dos passageiros de cruzeiros, segmento com sazonalidade e
        distribuição geográfica distintas.

        **Funcionalidades e visualizações implementadas:**
        - Upload de arquivos XLS e processamento com barra de progresso
        - Filtros interativos por via, continente, ano e mês (radio, checkbox, dropdowns)
        - Tabela interativa com ordenação e seleção de colunas
        - Download dos dados filtrados em formato XLS
        - Color picker (cor de fundo e cor da fonte)
        - Cache para evitar reprocessamento dos arquivos
        - Persistência de preferências via Session State
        - Gráficos simples: barras (por ano), linhas (por mês) e pizza (por continente)
        - Gráficos avançados: histograma e scatter plot
        - Métricas resumidas: total de registros, soma e média de chegadas
        """
    )


# 2) Upload de arquivo XLS
# Campo para enviar um ou mais XLS do Data.Rio
def mostrar_upload():
    st.header("Upload")
    return st.file_uploader(
        "Envie um arquivo XLS de turismo do Data.Rio",
        type=["xls"],
        accept_multiple_files=True,
    )


# 3) Filtro de dados e seleção
# Mostra o dataset e recorta com radio, checkbox e dropdowns
def mostrar_filtros(dados):
    st.header("Filtro de dados e seleção")
    st.write("Dataset carregado:")
    st.dataframe(dados, use_container_width=True)

    # Três colunas: radio, dropdowns e seleção de colunas
    col_f1, col_f2, col_f3 = st.columns(3)

    # Radio: via aérea, marítima ou ambas
    with col_f1:
        via_escolhida = st.radio("Via de acesso", ["Ambas"] + sorted(dados["via"].unique().tolist()))

    # Dropdowns: ano e mês
    with col_f2:
        ano_escolhido = st.selectbox("Ano", ["Todos"] + sorted(dados["ano"].unique().tolist()))
        mes_escolhido = st.selectbox("Mês", ["Todos"] + MESES)

    # Dropdown: quais colunas aparecem na tabela
    with col_f3:
        colunas = st.multiselect("Colunas visíveis", list(dados.columns), default=list(dados.columns))

    # Checkbox: marca os continentes do recorte
    st.write("Continentes:")
    continentes = sorted(dados["continente"].unique().tolist())
    continentes_marcados = []
    cols_chk = st.columns(min(len(continentes), 4))
    for idx, item in enumerate(continentes):
        with cols_chk[idx % len(cols_chk)]:
            if st.checkbox(item, value=True):
                continentes_marcados.append(item)

    # Aplica os filtros nas linhas 
    filtrado = dados.copy()
    if via_escolhida != "Ambas":
        filtrado = filtrado[filtrado["via"] == via_escolhida]
    if len(continentes_marcados) > 0:
        filtrado = filtrado[filtrado["continente"].isin(continentes_marcados)]
    if ano_escolhido != "Todos":
        filtrado = filtrado[filtrado["ano"] == ano_escolhido]
    if mes_escolhido != "Todos":
        filtrado = filtrado[filtrado["mes"] == mes_escolhido]

    # Se nenhuma coluna for marcada, mostra todas
    if len(colunas) == 0:
        colunas = list(filtrado.columns)
    tabela = filtrado[colunas]
    return filtrado, tabela


# 4) Tabela interativa
# Exibe o recorte; o usuário pode ordenar e buscar nas colunas
def mostrar_tabela(tabela):
    st.header("Tabela")
    st.dataframe(tabela, use_container_width=True)


# 5) Download dos dados filtrados em XLS
# Monta o arquivo em memória e oferece o botão de download
def gerar_xls(df):
    livro = xlwt.Workbook()
    aba = livro.add_sheet("filtrado")
    # Primeira linha: nomes das colunas
    for j, coluna in enumerate(df.columns):
        aba.write(0, j, str(coluna))
    # Demais linhas: valores da tabela
    for i in range(len(df)):
        for j, coluna in enumerate(df.columns):
            valor = df.iloc[i, j]
            if pd.isna(valor):
                continue
            if isinstance(valor, (int, float)):
                aba.write(i + 1, j, float(valor))
            else:
                aba.write(i + 1, j, str(valor))
    # BytesIO guarda o XLS na memória para o botão de download
    arquivo = io.BytesIO()
    livro.save(arquivo)
    return arquivo.getvalue()


# Botão que baixa o recorte filtrado
def mostrar_download(tabela):
    st.header("Download")
    st.download_button(
        "Baixar dados filtrados (.xls)",
        data=gerar_xls(tabela),
        file_name="turismo_rio_filtrado.xls",
        mime="application/vnd.ms-excel")


# 6) Barra de progresso e spinner
# Lê cada XLS enviado mostrando progresso e um spinner
def processar_com_progresso(arquivos):
    lista_df = []
    barra = st.progress(0)
    with st.spinner("Processando o arquivo XLS..."):
        for i, arq in enumerate(arquivos):
            lista_df.append(ler_arquivo_xls(arq.getvalue(), arq.name))
            barra.progress((i + 1) / (len(arquivos) + 1))
        # sleep deixa o spinner visível por alguns segundos
        time.sleep(4)
        barra.progress(1.0)
    # Junta todos os arquivos numa tabela só
    return pd.concat(lista_df, ignore_index=True)


# 7) Color picker
# Dois seletores: cor de fundo e cor da fonte
def mostrar_cores():
    st.header("Cores")
    # Dois pickers lado a lado
    col1, col2 = st.columns(2)
    with col1:
        cor_fundo = st.color_picker("Cor de fundo:", value="#000000")
        if cor_fundo:
            st.write(f"Cor de fundo: {cor_fundo}")
    with col2:
        cor_fonte = st.color_picker("Cor da fonte:", value="#FFFFFF")
        if cor_fonte:
            st.write(f"Cor da fonte: {cor_fonte}")


# 8) Cache
# Guarda a leitura do XLS para não processar de novo
@st.cache_data
def ler_arquivo_xls(conteudo, nome_arquivo):
    via = descobrir_via(nome_arquivo)
    # BytesIO faz o pandas ler os bytes do upload como arquivo
    planilha = pd.ExcelFile(io.BytesIO(conteudo), engine="xlrd")
    lista = []

    # Cada aba com nome de ano (2006, 2007, ...) é uma tabela
    for aba in planilha.sheet_names:
        if aba.isdigit() == False:
            continue

        ano = int(aba)
        df = pd.read_excel(planilha, sheet_name=aba, header=None)

        # Procura a linha em que estão os meses (Janeiro ... Dezembro)
        linha_cabecalho = None
        for i in range(len(df)):
            valores = df.iloc[i].astype(str).tolist()
            if "Janeiro" in valores and "Dezembro" in valores:
                linha_cabecalho = i
                break

        if linha_cabecalho is None:
            continue

        # Guarda o número da coluna de cada mês
        colunas_mes = {}
        for col in range(len(df.columns)):
            nome_col = str(df.iloc[linha_cabecalho, col]).strip()
            if nome_col in MESES:
                colunas_mes[col] = nome_col

        continente_atual = "Não informado"

        # Lê as linhas de país até o rodapé (Fonte, Nota, etc.)
        for i in range(linha_cabecalho + 1, len(df)):
            nome = str(df.iloc[i, 0]).strip()
            if nome == "" or nome == "nan":
                continue

            nome_minusculo = nome.lower()
            if (
                nome_minusculo.startswith("fonte")
                or nome_minusculo.startswith("nota")
                or nome_minusculo.startswith("dispon")
                or nome_minusculo.startswith("(")
            ):
                break

            # Pula o total geral; linha de continente só atualiza o grupo
            if nome == "Total":
                continue
            if nome in CONTINENTES:
                continente_atual = padronizar_continente(nome)
                continue

            for col, mes in colunas_mes.items():
                lista.append(
                    {
                        "via": via,
                        "ano": ano,
                        "continente": continente_atual,
                        "pais": nome,
                        "mes": mes,
                        "chegadas": limpar_numero(df.iloc[i, col]),
                    }
                )

    return pd.DataFrame(lista)


# 9) Session State
# Guarda os dados carregados enquanto a pessoa navega
def iniciar_sessao():
    if "dados" not in st.session_state:
        st.session_state["dados"] = None


# 10) Gráficos simples
# Barras por ano, linhas por mês e pizza por continente
def mostrar_graficos_simples(filtrado):
    st.header("Gráficos simples")
    col_g1, col_g2 = st.columns(2)
    # Barras
    with col_g1:
        st.subheader("Chegadas por ano")
        por_ano = filtrado.groupby("ano")["chegadas"].sum()
        st.bar_chart(por_ano)
    # Linhas
    with col_g2:
        st.subheader("Chegadas por mês")
        por_mes = filtrado.groupby("mes")["chegadas"].sum().reindex(MESES).dropna()
        st.line_chart(por_mes)

    # Pizza
    st.subheader("Distribuição por continente")
    por_continente = filtrado.groupby("continente")["chegadas"].sum().reset_index()
    fig_pie = px.pie(por_continente, names="continente", values="chegadas")
    st.plotly_chart(fig_pie, use_container_width=True)


# 11) Gráficos avançados
# Histograma das chegadas e scatter por ano e continente
def mostrar_graficos_avancados(filtrado):
    st.header("Gráficos avançados")
    col_a1, col_a2 = st.columns(2)
    # Histograma
    with col_a1:
        st.subheader("Histograma")
        fig_hist = px.histogram(filtrado, x="chegadas")
        st.plotly_chart(fig_hist, use_container_width=True)
    # Scatter
    with col_a2:
        st.subheader("Scatter")
        fig_scatter = px.scatter(filtrado, x="ano", y="chegadas", color="continente")
        st.plotly_chart(fig_scatter, use_container_width=True)


# 12) Métricas básicas
# Contagem de registros, soma e média das chegadas
def mostrar_metricas(tabela):
    st.header("Métricas")
    c1, c2, c3 = st.columns(3)
    c1.metric("Registros filtrados", formatar_numero(len(tabela)))
    c2.metric(
        "Total de chegadas",
        formatar_numero(tabela["chegadas"].sum()) if "chegadas" in tabela.columns else "—",
    )
    c3.metric(
        "Média de chegadas por registro",
        formatar_numero(tabela["chegadas"].mean()) if "chegadas" in tabela.columns and len(tabela) > 0 else "—",
    )


# Configuração da página (para ficar mais organizado visualmnete no streamlit)
st.set_page_config(page_title="Turismo Rio (Data.Rio)", layout="wide")
iniciar_sessao()

st.title("TP3 - Desenvolvimento Front-End com Python (com Streamlit)")
st.subheader("Turismo Rio de Janeiro")
st.caption("Chegada de turistas internacionais por via aérea e marítima · Dados: Data.Rio (2006–2019)")

mostrar_explicacao()
mostrar_cores()
arquivo = mostrar_upload()
# Só processa de novo se o arquivo enviado for diferente do anterior
if arquivo:
    nomes = [arq.name for arq in arquivo]
    if st.session_state.get("arquivos_lidos") != nomes:
        st.session_state["dados"] = processar_com_progresso(arquivo)
        st.session_state["arquivos_lidos"] = nomes

# Sem arquivo, a tela para aqui
if st.session_state["dados"] is None:
    st.write("Nenhum arquivo foi carregado")
    st.stop()

dados = st.session_state["dados"]
filtrado, tabela = mostrar_filtros(dados)
mostrar_metricas(tabela)
mostrar_tabela(tabela)
mostrar_download(tabela)
mostrar_graficos_simples(filtrado)
mostrar_graficos_avancados(filtrado)