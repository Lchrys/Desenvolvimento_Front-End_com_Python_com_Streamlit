# AT Sports Analytics (StatsBomb + Streamlit)

# Interface compartilhada: configuração da página, Session State,
# métricas, formulários e download.

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stoggle import stoggle

from src.dados import (
    PREFERENCIA_COMPETICAO,
    PREFERENCIA_TEMPORADA,
    TIPOS_PADRAO,
    TIPOS_PT,
    carregar_competicoes,
    carregar_eventos,
    carregar_partidas,
    lista_equipes,
    lista_jogadores,
    paises_dos_jogos,
    resumo_por_jogador,
)

COR_BOM = "#00C853"
COR_MEDIO = "#FFB300"
COR_RUIM = "#E53935"


def configurar_pagina():
    st.set_page_config(
        page_title="DR1_AT - Sports Analytics com Streamlit",
        page_icon=":soccer:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def iniciar_sessao():
    padroes = {
        "minuto_inicio": 0,
        "minuto_fim": 120,
        "n_eventos": 200,
        "tipos_evento": TIPOS_PADRAO,
        "so_completos": False,
        "so_gols": False,
        "equipe_filtro": "Ambas",
        "jogador_filtro": "Todos",
        "jogador_a": None,
        "jogador_b": None,
        "cor_campo": "#22312b",
        "ordem_tabela": "Minuto (cronológico)",
        "paises_csv": None,
    }
    for chave, valor in padroes.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def _selectbox_seguro(rotulo, opcoes, chave, preferida=None):
    if not opcoes:
        return None
    atual = st.session_state.get(chave)
    if atual not in opcoes:
        st.session_state[chave] = preferida if preferida in opcoes else opcoes[0]
    return st.selectbox(rotulo, opcoes, key=chave)


def _realce(valor, bom, medio):
    if valor >= bom:
        return COR_BOM
    if valor >= medio:
        return COR_MEDIO
    return COR_RUIM


def _aviso_recorte_metricas():
    if st.session_state.get("so_gols"):
        st.warning(
            "O recorte 'Apenas gols' deixa só as finalizações que viraram gol. "
            "Conversão e xG passam a refletir só esses eventos."
        )
    if st.session_state.get("so_completos"):
        st.info(
            "O recorte oculta passes incompletos, então a precisão de passe "
            "neste recorte fica em 100%."
        )


def mostrar_metricas_partida(stats):
    _aviso_recorte_metricas()
    saldo_xg = stats["gols"] - stats["xg"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(
        "Gols",
        stats["gols"],
        delta=f"{saldo_xg:+.2f} vs xG",
        delta_color="normal",
        help="Finalizações com outcome Goal. Gol contra não entra neste cartão.",
    )
    c2.metric(
        "Finalizações",
        stats["chutes"],
        delta_color="off",
        help="Todos os chutes do recorte, inclusive bloqueados e na trave",
    )
    c3.metric("xG", f"{stats['xg']:.2f}", delta_color="off", help="Soma do xG das finalizações")
    c4.metric(
        "Passes",
        stats["passes"],
        delta=f"{int(stats['passes_completos'])} certos",
        delta_color="normal",
    )
    c5.metric("Conversão", f"{stats['conversao']:.1f}%", delta_color="off", help="Gols por chutes")

    style_metric_cards(
        background_color="var(--st-secondary-background-color)",
        border_color="var(--st-secondary-background-color)",
        border_left_color=_realce(stats["conversao"], 20, 10),
        border_radius_px=8,
    )
    st.caption(
        "A faixa colorida segue a conversão: verde a partir de 20%, amarelo a "
        "partir de 10% e vermelho abaixo disso. O delta de Gols compara esses "
        "gols de chute com o xG. Gol contra não entra no cartão."
    )


def mostrar_metricas_jogador(stats, jogador, avisar=True):
    st.caption(f"Indicadores de {jogador}")
    if avisar:
        _aviso_recorte_metricas()
    saldo_xg = stats["gols"] - stats["xg"]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Passes certos",
            stats["passes_completos"],
            delta=f"{stats['precisao_passe']:.1f}% precisão",
            delta_color="normal",
        )
    with c2:
        st.metric("Finalizações", stats["chutes"], delta_color="off")
    with c3:
        st.metric("xG", f"{stats['xg']:.2f}", delta=f"{saldo_xg:+.2f} vs gols", delta_color="normal")
    with c4:
        st.metric("Conversão", f"{stats['conversao']:.1f}%", delta_color="off")

    style_metric_cards(
        background_color="var(--st-secondary-background-color)",
        border_color="var(--st-secondary-background-color)",
        border_left_color=_realce(stats["precisao_passe"], 85, 75),
        border_radius_px=8,
    )
    st.caption(
        "A faixa colorida segue a precisão de passe: verde a partir de 85%, "
        "amarelo a partir de 75% e vermelho abaixo disso."
    )


def mostrar_sidebar():
    iniciar_sessao()

    with st.sidebar:
        st.header("Filtros")

        try:
            competicoes = carregar_competicoes()
        except (OSError, ValueError, KeyError) as erro:
            st.error("Não foi possível carregar as competições do StatsBomb. Verifique a conexão.")
            st.caption(str(erro))
            st.stop()

        nomes = sorted(competicoes["competition_name"].unique().tolist())
        competicao = _selectbox_seguro(
            "Campeonato",
            nomes,
            "nome_competicao",
            PREFERENCIA_COMPETICAO,
        )

        recorte = competicoes[competicoes["competition_name"] == competicao]
        temporadas = recorte["season_name"].tolist()
        temporada = _selectbox_seguro(
            "Temporada",
            temporadas,
            "nome_temporada",
            PREFERENCIA_TEMPORADA,
        )

        linha_comp = recorte[recorte["season_name"] == temporada].iloc[0]
        competition_id = int(linha_comp["competition_id"])
        season_id = int(linha_comp["season_id"])

        try:
            partidas = carregar_partidas(competition_id, season_id)
        except (OSError, ValueError, KeyError) as erro:
            st.error("Não foi possível carregar as partidas desta temporada.")
            st.caption(str(erro))
            st.stop()

        if partidas is None or len(partidas) == 0:
            st.warning("Esta temporada não tem partidas públicas no StatsBomb.")
            st.stop()

        rotulos = partidas["rotulo"].tolist()
        rotulo = _selectbox_seguro("Partida", rotulos, "rotulo_partida", rotulos[-1] if rotulos else None)
        partida = partidas[partidas["rotulo"] == rotulo].iloc[0]
        match_id = int(partida["match_id"])

        try:
            with st.spinner("Preparando os eventos da partida..."):
                eventos = carregar_eventos(match_id)
        except (OSError, ValueError, KeyError) as erro:
            st.error("Não foi possível carregar os eventos desta partida.")
            st.caption(str(erro))
            st.stop()

        equipes = ["Ambas"] + lista_equipes(eventos, partida)

        st.subheader("Recorte rápido")
        _selectbox_seguro("Equipe", equipes, "equipe_filtro", "Ambas")
        jogadores = ["Todos"] + lista_jogadores(eventos, st.session_state["equipe_filtro"])
        _selectbox_seguro("Jogador", jogadores, "jogador_filtro", "Todos")
        st.color_picker("Cor do campo", key="cor_campo")

    st.session_state["competition_id"] = competition_id
    st.session_state["season_id"] = season_id
    st.session_state["match_id"] = match_id

    return {
        "competicoes": competicoes,
        "competicao": competicao,
        "temporada": temporada,
        "competition_id": competition_id,
        "season_id": season_id,
        "partidas": partidas,
        "partida": partida,
        "match_id": match_id,
        "eventos": eventos,
        "jogadores": jogadores,
        "equipes": equipes,
    }


def glossario_metricas():
    stoggle(
        "Glossário das métricas",
        """
        xG é o gol esperado, isto é, a probabilidade associada a cada
        finalização, enquanto a conversão é a razão entre gols de chute e
        finalizações expressa em porcentagem e a precisão de passe mede os
        passes completos sobre o total tentado. Gol contra não entra no cartão
        de gols. O delta vs xG subtrai o xG acumulado dos gols de chute: valor
        positivo indica finalização acima do esperado. A faixa da partida segue
        a conversão (20% / 10%) e a do jogador, a precisão de passe (85% / 75%).
        Os desarmes somam duelos, interceptações e recuperações de bola.
        """,
    )


def resumo_com_progresso(eventos, rotulo="Calculando indicadores por jogador..."):
    barra = st.progress(0, rotulo)

    def atualizar(fracao, jogador):
        barra.progress(min(fracao, 1.0), f"{rotulo} {jogador}")

    resumo = resumo_por_jogador(eventos, progresso=atualizar)
    barra.empty()
    return resumo


def formulario_eventos():
    st.subheader("Formulário de recorte")
    with st.form("form_eventos"):
        c1, c2, c3 = st.columns(3)
        with c1:
            n_eventos = st.number_input(
                "Quantidade de eventos na tabela",
                min_value=10,
                max_value=3000,
                value=int(st.session_state["n_eventos"]),
                step=10,
            )
        with c2:
            intervalo = st.slider(
                "Intervalo de minutos",
                min_value=0,
                max_value=120,
                value=(int(st.session_state["minuto_inicio"]), int(st.session_state["minuto_fim"])),
            )
            ordem = st.radio(
                "Ordenar a tabela por",
                ["Minuto (cronológico)", "xG (maior primeiro)", "Tipo"],
                horizontal=True,
                index=["Minuto (cronológico)", "xG (maior primeiro)", "Tipo"].index(st.session_state["ordem_tabela"]),
            )
        with c3:
            tipos = st.multiselect(
                "Tipos de evento",
                list(TIPOS_PT.keys()),
                default=st.session_state["tipos_evento"],
                format_func=lambda t: TIPOS_PT.get(t, t),
            )
            so_completos = st.checkbox("Ocultar passes incompletos", value=st.session_state["so_completos"])
            so_gols = st.checkbox("Apenas gols", value=st.session_state["so_gols"])

        enviado = st.form_submit_button("Aplicar recorte")

    if enviado:
        st.session_state["n_eventos"] = int(n_eventos)
        st.session_state["minuto_inicio"] = int(intervalo[0])
        st.session_state["minuto_fim"] = int(intervalo[1])
        st.session_state["tipos_evento"] = tipos if tipos else TIPOS_PADRAO
        st.session_state["so_completos"] = so_completos
        st.session_state["so_gols"] = so_gols
        st.session_state["ordem_tabela"] = ordem
        st.success("Recorte aplicado e salvo na sessão.")


def formulario_comparacao(jogadores):
    nomes = [j for j in jogadores if j != "Todos"]
    if len(nomes) < 2:
        st.info("É preciso pelo menos dois jogadores na partida para comparar.")
        return None, None

    with st.form("form_comparacao"):
        c1, c2 = st.columns(2)
        idx_a = nomes.index(st.session_state["jogador_a"]) if st.session_state["jogador_a"] in nomes else 0
        idx_b = nomes.index(st.session_state["jogador_b"]) if st.session_state["jogador_b"] in nomes else min(1, len(nomes) - 1)
        with c1:
            jogador_a = st.selectbox("Jogador A", nomes, index=idx_a)
        with c2:
            jogador_b = st.selectbox("Jogador B", nomes, index=idx_b)
        comparar = st.form_submit_button("Comparar jogadores")

    if comparar:
        if jogador_a == jogador_b:
            st.warning("Escolha dois jogadores diferentes.")
            return None, None
        st.session_state["jogador_a"] = jogador_a
        st.session_state["jogador_b"] = jogador_b
        return jogador_a, jogador_b

    if st.session_state["jogador_a"] in nomes and st.session_state["jogador_b"] in nomes:
        return st.session_state["jogador_a"], st.session_state["jogador_b"]
    return nomes[0], nomes[1]


def botao_download(eventos, match_id):
    csv = eventos.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar eventos filtrados (CSV)",
        data=csv,
        file_name=f"eventos_partida_{match_id}.csv",
        mime="text/csv",
    )


def metadados_partida(ctx):
    partida = ctx["partida"]
    data = partida["match_date"]
    return {
        "competicao": ctx["competicao"],
        "temporada": ctx["temporada"],
        "match_id": int(ctx["match_id"]),
        "mandante": None if pd.isna(partida.get("home_team")) else str(partida["home_team"]),
        "visitante": None if pd.isna(partida.get("away_team")) else str(partida["away_team"]),
        "placar": {
            "casa": int(partida["home_score"]),
            "fora": int(partida["away_score"]),
        },
        "estadio": None if "stadium" not in partida or pd.isna(partida["stadium"]) else str(partida["stadium"]),
        "fase": None if "competition_stage" not in partida or pd.isna(partida["competition_stage"]) else str(partida["competition_stage"]),
        "data": None if pd.isna(data) else str(pd.Timestamp(data).date()),
    }


def mostrar_mapa_paises(partidas):
    from src.visualizacoes import mapa_paises_pydeck

    st.subheader("Países onde houve jogos")
    st.write(
        "Cada ponto é um país em que houve jogo desta competição e desta "
        "temporada (país do estádio). Para o mapa aparecer, envie o arquivo "
        "countries.csv que está na pasta do projeto."
    )

    arquivo = st.file_uploader("Enviar CSV de países", type=["csv"], key="csv_paises")
    if arquivo is not None:
        enviado = pd.read_csv(arquivo)
        if "name" in enviado.columns and "latitude" in enviado.columns and "longitude" in enviado.columns:
            st.session_state["paises_csv"] = enviado
            st.success("CSV de países carregado.")
        else:
            st.warning("O CSV precisa das colunas name, latitude e longitude.")

    coordenadas = st.session_state.get("paises_csv")
    if coordenadas is None:
        st.info("Envie o countries.csv para ver o mapa.")
        return

    pontos, faltando = paises_dos_jogos(partidas, coordenadas)
    deck = mapa_paises_pydeck(pontos)
    if deck is not None:
        st.pydeck_chart(deck, width="stretch")
    else:
        st.info("Não há país com coordenada neste recorte.")

    if faltando:
        st.text("Sem coordenada no CSV:\n" + "\n".join(faltando))


def cabecalho_partida(ctx):
    partida = ctx["partida"]
    st.subheader("Partida selecionada")
    c1, c2, c3 = st.columns(3)
    c1.write(f"Competição: {ctx['competicao']}")
    c2.write(f"Temporada: {ctx['temporada']}")
    c3.write(f"Data: {partida['match_date'].date() if pd.notna(partida['match_date']) else 'sem data'}")
    st.write(
        f"{partida['home_team']} {partida['home_score']} × {partida['away_score']} {partida['away_team']}"
    )
    extras = []
    if "stadium" in partida and pd.notna(partida["stadium"]):
        extras.append(f"Estádio: {partida['stadium']}")
    if "competition_stage" in partida and pd.notna(partida["competition_stage"]):
        extras.append(f"Fase: {partida['competition_stage']}")
    if extras:
        st.caption(" · ".join(extras))


def mostrar_figura(fig):
    if fig is None:
        st.info("Não há eventos suficientes para este gráfico com o recorte atual.")
        return
    st.pyplot(fig, width="stretch")
    plt.close(fig)
