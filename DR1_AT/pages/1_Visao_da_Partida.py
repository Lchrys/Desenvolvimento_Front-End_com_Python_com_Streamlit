# AT Sports Analytics (StatsBomb + Streamlit)

# Página da partida: estatísticas, tabela de eventos, mapas mplsoccer e gráficos extras.

import streamlit as st

from src.dados import (
    estatisticas_partida,
    eventos_para_exibicao,
    filtrar_eventos,
)
from src.interface import (
    botao_download,
    cabecalho_partida,
    configurar_pagina,
    formulario_eventos,
    glossario_metricas,
    mostrar_figura,
    mostrar_metricas_partida,
    mostrar_sidebar,
    resumo_com_progresso,
)
from src.visualizacoes import (
    boxplot_altair,
    linha_eventos_plotly,
    mapa_calor,
    mapa_chutes,
    mapa_passes,
    pizza_eventos,
    scatter_passes_xg,
    subplots_passes_xg,
)

configurar_pagina()
ctx = mostrar_sidebar()

st.title("Visão da partida")
cabecalho_partida(ctx)

st.write(
    """
    Esta tela concentra as estatísticas da partida selecionada, a tabela de
    eventos e os mapas do campo. O formulário abaixo define o recorte aplicado
    à tabela, ao download e às visualizações.
    """
)

formulario_eventos()

filtros_comuns = dict(
    jogador=st.session_state["jogador_filtro"],
    equipe=st.session_state["equipe_filtro"],
    minuto_inicio=st.session_state["minuto_inicio"],
    minuto_fim=st.session_state["minuto_fim"],
    so_completos=st.session_state["so_completos"],
    so_gols=st.session_state["so_gols"],
)

eventos_metricas = filtrar_eventos(ctx["eventos"], tipos=None, **filtros_comuns)
eventos = filtrar_eventos(ctx["eventos"], tipos=st.session_state["tipos_evento"], **filtros_comuns)

mostrar_metricas_partida(estatisticas_partida(eventos_metricas))
glossario_metricas()
st.caption(
    "Os indicadores acima consideram todo o recorte de equipe, jogador e minuto, "
    "independentemente dos tipos de evento escolhidos no formulário. "
    "Logo, desmarcar um tipo altera a tabela e os mapas, mas não os cartões."
)

st.subheader("Eventos da partida")
st.caption(
    "A tabela lista passes, finalizações, duelos e os demais tipos marcados no "
    "formulário, na ordem selecionada e até o limite informado."
)
tabela = eventos_para_exibicao(eventos, st.session_state["n_eventos"], st.session_state.get("ordem_tabela", "Minuto (cronológico)"))
st.dataframe(tabela, width="stretch")
if len(tabela) > 0:
    if "gol" in tabela.columns and tabela["gol"].any():
        destaque = tabela[tabela["gol"]].head(8)
        st.caption("Gols do recorte")
    elif "shot_statsbomb_xg" in tabela.columns:
        destaque = tabela.sort_values("shot_statsbomb_xg", ascending=False).head(8)
        st.caption("Maiores xG do recorte (não houve gol neste filtro)")
    else:
        destaque = tabela.head(8)
        st.caption("Primeiros eventos do recorte")
    st.table(destaque)
botao_download(
    eventos_para_exibicao(eventos, limite=None, ordem=st.session_state.get("ordem_tabela", "Minuto (cronológico)")),
    ctx["match_id"],
)

aba1, aba2, aba3, aba4 = st.tabs(["Mapa de passes", "Mapa de chutes", "Mapa de calor", "Relações estatísticas"])

with aba1:
    mostrar_figura(
        mapa_passes(
            eventos,
            titulo="Mapa de passes da partida",
            cor_campo=st.session_state["cor_campo"],
            limite=st.session_state["n_eventos"],
        )
    )

with aba2:
    mostrar_figura(mapa_chutes(eventos, titulo="Mapa de finalizações (tamanho = xG)"))

with aba3:
    mostrar_figura(mapa_calor(eventos, "Mapa de calor das ações"))

with aba4:
    resumo = resumo_com_progresso(eventos_metricas)
    st.caption("Volume de passes em relação ao xG de cada jogador.")
    mostrar_figura(scatter_passes_xg(resumo))
    fig_sub = subplots_passes_xg(resumo)
    if fig_sub is not None:
        st.caption("Quem mais passou versus o xG desses mesmos jogadores.")
        st.plotly_chart(fig_sub, width="stretch")
    box_altair = boxplot_altair(resumo)
    if box_altair is not None:
        st.caption("Como os passes se distribuem em cada equipe.")
        st.altair_chart(box_altair, width="stretch", key="boxplot_passes")
    fig_linha = linha_eventos_plotly(eventos)
    if fig_linha is not None:
        st.caption("Em quais minutos o recorte gerou mais ações.")
        st.plotly_chart(fig_linha, width="stretch")
    fig_pizza = pizza_eventos(eventos)
    if fig_pizza is not None:
        st.caption("Composição dos tipos de evento no filtro atual.")
        st.plotly_chart(fig_pizza, width="stretch")
