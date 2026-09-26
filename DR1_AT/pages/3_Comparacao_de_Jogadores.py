# AT Sports Analytics (StatsBomb + Streamlit)

# Página de comparação entre dois jogadores (formulário + barras).

import streamlit as st

from src.dados import estatisticas_jogador, filtrar_eventos
from src.interface import (
    cabecalho_partida,
    configurar_pagina,
    formulario_comparacao,
    mostrar_figura,
    mostrar_metricas_jogador,
    mostrar_sidebar,
    resumo_com_progresso,
)
from src.visualizacoes import barras_comparacao, mapa_passes

configurar_pagina()
ctx = mostrar_sidebar()

st.title("Comparação de jogadores")
cabecalho_partida(ctx)

st.write(
    """
    A comparação coloca dois jogadores da mesma partida lado a lado para
    distinguir quem constrói mais o ataque, pelo volume e pela precisão dos
    passes, e quem conclui melhor, pelos chutes, pelo xG e pelos gols.
    Portanto, indicadores e mapas de passe permanecem no mesmo recorte temporal.
    """
)

par = formulario_comparacao(ctx["jogadores"])
if par[0] is None:
    st.stop()

jogador_a, jogador_b = par
filtros_comuns = dict(
    equipe=st.session_state["equipe_filtro"],
    minuto_inicio=st.session_state["minuto_inicio"],
    minuto_fim=st.session_state["minuto_fim"],
    so_completos=st.session_state["so_completos"],
    so_gols=st.session_state["so_gols"],
)

eventos_metricas = filtrar_eventos(ctx["eventos"], tipos=None, **filtros_comuns)
eventos = filtrar_eventos(ctx["eventos"], tipos=st.session_state["tipos_evento"], **filtros_comuns)
resumo = resumo_com_progresso(eventos_metricas)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"### {jogador_a}")
    mostrar_metricas_jogador(estatisticas_jogador(eventos_metricas, jogador_a), jogador_a)
with col_b:
    st.markdown(f"### {jogador_b}")
    mostrar_metricas_jogador(
        estatisticas_jogador(eventos_metricas, jogador_b),
        jogador_b,
        avisar=False,
    )

aba1, aba2 = st.tabs(["Barras absolutas", "Passes lado a lado"])
with aba1:
    fig_bar = barras_comparacao(resumo, jogador_a, jogador_b)
    if fig_bar is not None:
        st.plotly_chart(fig_bar, width="stretch")
with aba2:
    c1, c2 = st.columns(2)
    with c1:
        mostrar_figura(
            mapa_passes(
                filtrar_eventos(eventos, jogador=jogador_a, tipos=["Pass"]),
                titulo=f"Passes de {jogador_a}",
                cor_campo=st.session_state["cor_campo"],
            )
        )
    with c2:
        mostrar_figura(
            mapa_passes(
                filtrar_eventos(eventos, jogador=jogador_b, tipos=["Pass"]),
                titulo=f"Passes de {jogador_b}",
                cor_campo=st.session_state["cor_campo"],
            )
        )
