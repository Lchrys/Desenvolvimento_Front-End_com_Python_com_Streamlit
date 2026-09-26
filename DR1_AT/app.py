# AT Sports Analytics (StatsBomb + Streamlit)

# Página inicial: pergunta de pesquisa, contexto e visão do campeonato.
# Layout com colunas, expander, container e sidebar.

import streamlit as st

from src.dados import filtrar_eventos
from src.interface import (
    cabecalho_partida,
    configurar_pagina,
    metadados_partida,
    mostrar_mapa_paises,
    mostrar_sidebar,
    resumo_com_progresso,
)
from src.visualizacoes import gols_por_equipe_df, scatter_campeonato

configurar_pagina()

st.title("DR1_AT - Sports Analytics com Streamlit :soccer:")
st.subheader("Construção ofensiva a partir de passes, finalizações e xG")

with st.container():
    st.write(
        """
        O dashboard examina, em uma partida, quais jogadores mais influenciam o
        ataque, seja pelo volume e pela qualidade dos passes, seja pela
        eficiência das finalizações (chutes, gols e xG). Os filtros da barra
        lateral repetem essa análise para o campeonato, a temporada e o jogo
        selecionados.
        """
    )
    st.caption(
        "Observação: o xG (gols esperados) corresponde à probabilidade de uma "
        "finalização resultar em gol, em uma escala de 0 a 1, estimada pela "
        "StatsBomb a partir da distância, do ângulo e do contexto do chute. Ou "
        "seja, o indicador da partida soma esses valores e permite confrontar o "
        "que o recorte tendia a marcar com o que de fato ocorreu."
    )

with st.expander("Por que Streamlit"):
    st.markdown(
        """
        O Streamlit, utilizado neste projeto, transforma um script Python em uma
        interface web interativa sem exigir HTML, CSS ou JavaScript. A
        arquitetura de execução reexecuta o script a cada interação do usuário
        (rerun); com isso, o cache evita novas chamadas à StatsBomb e o Session
        State mantém os filtros quando se passa de uma página a outra.

        Em relação a outras bibliotecas, o Dash permite callbacks por componente
        e, em contrapartida, demanda mais código. O Panel é mais flexível na
        integração com ferramentas científicas, embora o layout exija
        configuração adicional. O Voila publica um notebook Jupyter com pouco
        trabalho, porém se mostra limitado quando a aplicação precisa de barra
        lateral e de várias páginas. Portanto, para o tipo de exploração pedida
        neste trabalho, com filtros, mapas e navegação entre telas, o Streamlit
        foi a opção adotada.

        Essa simplicidade traz restrições: cálculos pesados dependem de cache
        para não atrasar a tela, o layout permanece limitado aos containers, sem
        CSS próprio, e não há callback por componente como no Dash, logo um
        gráfico não pode ser atualizado isoladamente.
        """
    )

with st.container():
    st.subheader("Visualizações espaciais como complemento às tabelas de eventos")
    st.write(
        """
        A tabela de eventos descreve o minuto e o tipo da ação, mas não a
        posição no campo, e um volante com muitos passes certos pode estar
        apenas reciclando a bola no meio. Em suma, os mapas de passe, de
        finalização (com o tamanho do ponto proporcional ao xG) e de calor
        tornam essa diferença visível e servem de apoio à leitura tática, à
        escalação e ao ajuste de marcação.
        """
    )

ctx = mostrar_sidebar()
partida = ctx["partida"]
f"{partida['home_team']} × {partida['away_team']} | {st.session_state['equipe_filtro']} | {st.session_state['jogador_filtro']}"

st.divider()
cabecalho_partida(ctx)
with st.expander("Ficha da partida (JSON)"):
    st.json(metadados_partida(ctx))

eventos_metricas = filtrar_eventos(
    ctx["eventos"],
    jogador=st.session_state["jogador_filtro"],
    equipe=st.session_state["equipe_filtro"],
    tipos=None,
    minuto_inicio=st.session_state["minuto_inicio"],
    minuto_fim=st.session_state["minuto_fim"],
    so_completos=st.session_state["so_completos"],
    so_gols=st.session_state["so_gols"],
)

resumo = resumo_com_progresso(eventos_metricas)
if len(resumo) > 0:
    top = resumo.iloc[0]
    st.success(
        f"Neste recorte, {top['jogador']} ({top['equipe']}) lidera em passes "
        f"({int(top['passes'])}), com {top['xg']:.2f} xG e {int(top['gols'])} gol(s)."
    )

    st.subheader("Ranking do recorte")
    st.write(resumo.head(8))

st.header("Panorama da temporada")
n_partidas = len(ctx["partidas"])
gols_temporada = int(ctx["partidas"]["home_score"].sum() + ctx["partidas"]["away_score"].sum())
media_gols = gols_temporada / max(n_partidas, 1)
c1, c2, c3 = st.columns(3)
c1.write(f"Partidas: {n_partidas}")
c2.write(f"Gols na temporada: {gols_temporada}")
c3.write(f"Média de gols por jogo: {media_gols:.2f}")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Gols por equipe")
    gols_equipe = gols_por_equipe_df(ctx["partidas"])
    if len(gols_equipe) > 0:
        st.bar_chart(gols_equipe.set_index("equipe"))
with col_b:
    st.subheader("Relação entre gols do mandante e do visitante")
    fig_scatter = scatter_campeonato(ctx["partidas"])
    if fig_scatter is not None:
        evento = st.plotly_chart(
            fig_scatter,
            width="stretch",
            on_select="rerun",
            selection_mode="points",
            key="scatter_placar_plotly",
        )
        if len(evento.selection.points) > 0:
            ponto = evento.selection.points[0]
            rotulo = ponto.get("hovertext") or ponto.get("hover_name")
            if not rotulo:
                indice = ponto.get("point_index")
                if indice is not None and int(indice) < len(ctx["partidas"]):
                    rotulo = ctx["partidas"].iloc[int(indice)]["rotulo"]
                else:
                    casa = ponto.get("x")
                    fora = ponto.get("y")
                    mesmo_placar = ctx["partidas"][
                        (ctx["partidas"]["home_score"] == casa)
                        & (ctx["partidas"]["away_score"] == fora)
                    ]
                    if len(mesmo_placar) > 0:
                        rotulo = mesmo_placar.iloc[0]["rotulo"]
            if rotulo:
                st.info(str(rotulo))
                if rotulo != st.session_state.get("rotulo_partida"):
                    st.session_state["rotulo_partida"] = rotulo
                    st.rerun()

colunas_tab = [
    c
    for c in ["match_date", "home_team", "home_score", "away_score", "away_team", "stadium"]
    if c in ctx["partidas"].columns
]
if len(ctx["partidas"]) > 0:
    mais_gols = ctx["partidas"].copy()
    mais_gols["gols_total"] = mais_gols["home_score"] + mais_gols["away_score"]
    mais_gols = mais_gols.sort_values("gols_total", ascending=False)
    st.caption("As cinco partidas com mais gols na temporada")
    st.table(mais_gols[colunas_tab].head(5))

mostrar_mapa_paises(ctx["partidas"])
