# AT Sports Analytics (StatsBomb + Streamlit)

# Gráficos do campo (mplsoccer) e gráficos estatísticos
# (Matplotlib, Seaborn, Plotly e Altair).

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import seaborn as sns
from mplsoccer import Pitch, VerticalPitch
from plotly.subplots import make_subplots

COR_CAMPO = "#22312b"
COR_LINHA = "#c7d5cc"
COR_PASSE_OK = "#ad993c"
COR_PASSE_ERRO = "#ba4f45"
COR_GOL = "#00e676"
COR_CHUTE = "#ffca28"


def _vazio(df):
    return df is None or len(df) == 0


def mapa_passes(eventos, titulo="Mapa de passes", cor_campo=COR_CAMPO, limite=250):
    passes = eventos[eventos["type"] == "Pass"].dropna(subset=["x", "y", "end_x", "end_y"])
    if _vazio(passes):
        return None

    if len(passes) > limite:
        passes = passes.tail(limite)

    completos = passes[passes["passe_completo"]]
    incompletos = passes[~passes["passe_completo"]]

    pitch = Pitch(pitch_type="statsbomb", pitch_color=cor_campo, line_color=COR_LINHA)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor(cor_campo)

    if len(completos) > 0:
        pitch.arrows(
            completos["x"],
            completos["y"],
            completos["end_x"],
            completos["end_y"],
            width=1.8,
            headwidth=8,
            headlength=8,
            color=COR_PASSE_OK,
            ax=ax,
            label="Passes completos",
        )
    if len(incompletos) > 0:
        pitch.arrows(
            incompletos["x"],
            incompletos["y"],
            incompletos["end_x"],
            incompletos["end_y"],
            width=1.5,
            headwidth=6,
            headlength=5,
            color=COR_PASSE_ERRO,
            ax=ax,
            label="Passes incompletos",
        )

    ax.legend(facecolor=cor_campo, edgecolor="None", labelcolor="white", loc="upper left")
    ax.set_title(titulo, color="white", fontsize=14, pad=8)
    fig.text(
        0.02,
        0.02,
        "As setas ligam a origem ao destino do passe: dourado indica passe "
        "completo e vermelho, passe incompleto. Fonte: StatsBomb.",
        color=COR_LINHA,
        fontsize=8,
    )
    return fig


def mapa_chutes(eventos, titulo="Mapa de finalizações"):
    chutes = eventos[eventos["type"] == "Shot"].dropna(subset=["x", "y"])
    if _vazio(chutes):
        return None

    gols = chutes[chutes["gol"]]
    outros = chutes[~chutes["gol"]]

    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color=COR_CAMPO,
        line_color=COR_LINHA,
    )
    fig, ax = pitch.draw(figsize=(8, 9))
    fig.set_facecolor(COR_CAMPO)

    if len(outros) > 0:
        pitch.scatter(
            outros["x"],
            outros["y"],
            s=outros["shot_statsbomb_xg"] * 900 + 40,
            color=COR_CHUTE,
            edgecolors="white",
            alpha=0.85,
            ax=ax,
            label="Finalização",
        )
    if len(gols) > 0:
        pitch.scatter(
            gols["x"],
            gols["y"],
            s=gols["shot_statsbomb_xg"] * 900 + 80,
            color=COR_GOL,
            edgecolors="white",
            marker="*",
            ax=ax,
            label="Gol",
        )

    ax.legend(facecolor=COR_CAMPO, edgecolor="None", labelcolor="white", loc="upper left")
    ax.set_title(titulo, color="white", fontsize=14, pad=8)
    fig.text(
        0.02,
        0.02,
        "O tamanho do ponto é proporcional ao xG e a estrela verde marca o gol, "
        "no campo ofensivo da StatsBomb.",
        color=COR_LINHA,
        fontsize=8,
    )
    return fig


def mapa_calor(eventos, titulo="Mapa de calor das ações"):
    pontos = eventos.dropna(subset=["x", "y"])
    if len(pontos) < 8:
        return None

    pitch = Pitch(pitch_type="statsbomb", pitch_color=COR_CAMPO, line_color=COR_LINHA, line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor(COR_CAMPO)
    bins = pitch.bin_statistic(pontos["x"], pontos["y"], statistic="count", bins=(10, 8))
    pitch.heatmap(bins, ax=ax, cmap="YlOrRd")
    ax.set_title(titulo, color="white", fontsize=14, pad=8)
    fig.text(
        0.02,
        0.02,
        "O mapa de calor conta as ações por zona do campo, segundo o recorte atual.",
        color=COR_LINHA,
        fontsize=8,
    )
    return fig


def scatter_passes_xg(resumo):
    if _vazio(resumo):
        return None
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.set_theme(style="whitegrid")
    sns.scatterplot(
        data=resumo,
        x="passes",
        y="xg",
        ax=ax,
        color="#26C6DA",
        s=70,
    )
    rotulos = pd.concat(
        [resumo.nlargest(8, "passes"), resumo.nlargest(5, "xg")]
    ).drop_duplicates(subset="jogador")
    for i, linha in enumerate(rotulos.itertuples()):
        nome = str(linha.jogador).split()[-1]
        ax.annotate(
            nome,
            (linha.passes, linha.xg),
            fontsize=8,
            xytext=(6, 6 if i % 2 == 0 else -12),
            textcoords="offset points",
        )
    ax.set_xlabel("Passes")
    ax.set_ylabel("xG acumulado")
    ax.set_title("Relação entre volume de passes e xG por jogador")
    fig.tight_layout()
    return fig


def pizza_eventos(eventos):
    if _vazio(eventos):
        return None
    contagem = eventos["tipo"].value_counts().reset_index()
    contagem.columns = ["tipo", "qtd"]
    fig = px.pie(contagem, names="tipo", values="qtd", hole=0.45, title="Distribuição dos eventos")
    fig.update_layout(template="plotly_dark")
    return fig


def scatter_campeonato(partidas):
    if _vazio(partidas):
        return None
    df = partidas.copy()
    df["gols_total"] = df["home_score"] + df["away_score"]
    fig = px.scatter(
        df,
        x="home_score",
        y="away_score",
        color="gols_total",
        hover_name="rotulo",
        title="Placar: gols do mandante × gols do visitante",
        labels={"home_score": "Gols mandante", "away_score": "Gols visitante", "gols_total": "Gols na partida"},
    )
    fig.update_traces(marker=dict(size=14))
    fig.update_layout(template="plotly_dark")
    fig.update_xaxes(dtick=1, tickformat="d")
    fig.update_yaxes(dtick=1, tickformat="d")
    return fig


def mapa_paises_pydeck(paises):
    if _vazio(paises):
        return None
    df = paises.copy()
    df["raio"] = df["jogos"] * 20000
    vista = pdk.ViewState(
        latitude=float(df["latitude"].mean()),
        longitude=float(df["longitude"].mean()),
        zoom=3,
        pitch=0,
    )
    camada = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_radius="raio",
        get_fill_color=[0, 200, 83, 160],
        pickable=True,
    )
    return pdk.Deck(
        initial_view_state=vista,
        layers=[camada],
        tooltip={"text": "{pais}\n{jogos} jogo(s)"},
    )


def gols_por_equipe_df(partidas):
    if _vazio(partidas):
        return pd.DataFrame()
    casa = partidas.groupby("home_team")["home_score"].sum()
    fora = partidas.groupby("away_team")["away_score"].sum()
    gols = casa.add(fora, fill_value=0).sort_values(ascending=False).reset_index()
    gols.columns = ["equipe", "gols"]
    return gols


def eventos_por_minuto_df(eventos):
    if _vazio(eventos) or "minute" not in eventos.columns:
        return pd.DataFrame()
    return (
        eventos.groupby("minute")
        .size()
        .rename("eventos")
        .reset_index()
        .sort_values("minute")
    )


def boxplot_altair(resumo):
    if _vazio(resumo) or "passes" not in resumo.columns:
        return None

    return (
        alt.Chart(resumo)
        .mark_boxplot(extent="min-max", size=50)
        .encode(
            x=alt.X("equipe:N", title="Equipe"),
            y=alt.Y("passes:Q", title="Passes por jogador"),
            color=alt.Color("equipe:N", legend=None),
            tooltip=["equipe", "jogador", "passes"],
        )
        .properties(title="Boxplot: distribuição de passes", height=280)
        .configure(padding={"left": 12, "right": 12, "top": 12, "bottom": 12})
    )


def linha_eventos_plotly(eventos):
    serie = eventos_por_minuto_df(eventos)
    if _vazio(serie):
        return None
    fig = px.line(
        serie,
        x="minute",
        y="eventos",
        markers=True,
        title="Eventos ao longo dos minutos",
    )
    fig.update_layout(template="plotly_dark")
    return fig


def subplots_passes_xg(resumo, n=8):
    if _vazio(resumo):
        return None
    top = resumo.head(n)
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Passes", "xG"))
    fig.add_trace(go.Bar(x=top["jogador"], y=top["passes"], name="Passes", marker_color="#00C853"), row=1, col=1)
    fig.add_trace(go.Bar(x=top["jogador"], y=top["xg"], name="xG", marker_color="#26C6DA"), row=1, col=2)
    fig.update_layout(
        template="plotly_dark",
        showlegend=False,
        title="Passes e xG dos que mais passaram",
        height=380,
    )
    fig.update_xaxes(tickangle=-35)
    return fig


def barras_comparacao(resumo, jogador_a, jogador_b):
    if _vazio(resumo):
        return None
    cols = ["passes", "passes_completos", "chutes", "xg", "gols", "desarmes"]
    linhas = resumo.set_index("jogador")
    if jogador_a not in linhas.index or jogador_b not in linhas.index:
        return None
    dados = pd.DataFrame(
        {
            "métrica": cols + cols,
            "valor": [linhas.loc[jogador_a, c] for c in cols] + [linhas.loc[jogador_b, c] for c in cols],
            "jogador": [jogador_a] * len(cols) + [jogador_b] * len(cols),
        }
    )
    fig = px.bar(
        dados,
        x="métrica",
        y="valor",
        color="jogador",
        barmode="group",
        title="Comparação absoluta das métricas",
    )
    fig.update_layout(template="plotly_dark")
    return fig
