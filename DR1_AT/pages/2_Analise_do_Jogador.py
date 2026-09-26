# AT Sports Analytics (StatsBomb + Streamlit)

# Página do jogador: seletor, métricas, mapas individuais e download.

import streamlit as st

from src.dados import estatisticas_jogador, eventos_para_exibicao, filtrar_eventos
from src.interface import (
    botao_download,
    cabecalho_partida,
    configurar_pagina,
    mostrar_figura,
    mostrar_metricas_jogador,
    mostrar_sidebar,
)
from src.visualizacoes import mapa_calor, mapa_chutes, mapa_passes

configurar_pagina()
ctx = mostrar_sidebar()

st.title("Análise do jogador")
cabecalho_partida(ctx)

st.write(
    """
    Esta tela recorta um único atleta da partida selecionada e apresenta os
    mesmos indicadores e mapas da visão geral, agora em escala individual.
    """
)

nomes = [j for j in ctx["jogadores"] if j != "Todos"]
if not nomes:
    st.warning("Não há jogadores nos eventos desta partida.")
    st.stop()

atual = st.session_state.get("jogador_filtro")
if atual not in nomes:
    atual = nomes[0]

with st.form("form_jogador"):
    escolhido = st.selectbox(
        "Selecione o jogador",
        nomes,
        index=nomes.index(atual),
    )
    aplicar = st.form_submit_button("Aplicar filtro do jogador")

if aplicar:
    st.session_state["jogador_filtro"] = escolhido

jogador = st.session_state["jogador_filtro"]
if jogador not in nomes:
    jogador = nomes[0]

filtros_comuns = dict(
    jogador=jogador,
    equipe=st.session_state["equipe_filtro"] if st.session_state["equipe_filtro"] != "Ambas" else None,
    minuto_inicio=st.session_state["minuto_inicio"],
    minuto_fim=st.session_state["minuto_fim"],
    so_completos=st.session_state["so_completos"],
    so_gols=st.session_state["so_gols"],
)

eventos_metricas = filtrar_eventos(ctx["eventos"], tipos=None, **filtros_comuns)
eventos = filtrar_eventos(ctx["eventos"], tipos=st.session_state["tipos_evento"], **filtros_comuns)

st.write(f"Jogador em análise: {jogador}")
mostrar_metricas_jogador(estatisticas_jogador(eventos_metricas, jogador), jogador)

aba1, aba2, aba3 = st.tabs(["Passes", "Finalizações", "Mapa de calor"])
with aba1:
    mostrar_figura(
        mapa_passes(
            eventos,
            titulo=f"Passes de {jogador}",
            cor_campo=st.session_state["cor_campo"],
            limite=st.session_state["n_eventos"],
        )
    )
with aba2:
    mostrar_figura(mapa_chutes(eventos, titulo=f"Finalizações de {jogador}"))
with aba3:
    mostrar_figura(mapa_calor(eventos, titulo=f"Onde {jogador} atuou"))

st.subheader("Eventos do jogador")
tabela = eventos_para_exibicao(eventos, st.session_state["n_eventos"])
st.dataframe(tabela, width="stretch")
botao_download(
    eventos_para_exibicao(eventos, limite=None),
    f"{ctx['match_id']}_{jogador.replace(' ', '_')}",
)
