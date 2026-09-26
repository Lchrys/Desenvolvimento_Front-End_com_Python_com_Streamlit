# AT Sports Analytics (StatsBomb + Streamlit)

# Carrega competições, partidas e eventos do StatsBomb (dados abertos)
# e prepara as colunas usadas nas visualizações e na interface.

import warnings

import pandas as pd
import streamlit as st
from statsbombpy import sb

warnings.filterwarnings("ignore", message="credentials were not supplied")

TIPOS_PT = {
    "Pass": "Passe",
    "Shot": "Finalização",
    "Duel": "Duelo",
    "Interception": "Interceptação",
    "Ball Recovery": "Recuperação de bola",
    "Foul Committed": "Falta cometida",
    "Block": "Bloqueio",
    "Pressure": "Pressão",
    "Carry": "Condução",
    "Dribble": "Drible",
    "Clearance": "Afastamento",
    "Goal Keeper": "Goleiro",
    "Substitution": "Substituição",
    "Injury Stoppage": "Parada por lesão",
}

TIPOS_PADRAO = ["Pass", "Shot", "Duel", "Interception", "Ball Recovery"]

PREFERENCIA_COMPETICAO = "UEFA Euro"
PREFERENCIA_TEMPORADA = "2024"

# Nomes da StatsBomb que no CSV aparecem escrito de outro jeito.
NOMES_PAIS = {
    "United States of America": "United States",
}


def _coord(valor, indice):
    if isinstance(valor, (list, tuple)) and len(valor) > indice:
        try:
            return float(valor[indice])
        except (TypeError, ValueError):
            return None
    return None


@st.cache_data(show_spinner="Carregando competições...", ttl=3600)
def carregar_competicoes():
    df = sb.competitions()
    if "match_available" in df.columns:
        df = df[df["match_available"].notna()].copy()
    return df.sort_values(["competition_name", "season_name"]).reset_index(drop=True)


@st.cache_data(show_spinner="Carregando partidas...", ttl=3600)
def carregar_partidas(competition_id, season_id):
    df = sb.matches(competition_id=int(competition_id), season_id=int(season_id))
    df = df.copy()
    df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    df = df.sort_values("match_date").reset_index(drop=True)
    df["rotulo"] = df.apply(
        lambda r: (
            f"{r['match_date'].date() if pd.notna(r['match_date']) else '?'} | "
            f"{r['home_team']} {r['home_score']} x {r['away_score']} {r['away_team']} "
            f"(#{int(r['match_id'])})"
        ),
        axis=1,
    )
    df["pais_jogo"] = df["stadium_country_name"] if "stadium_country_name" in df.columns else None
    return df


def paises_dos_jogos(partidas, coordenadas):
    vazio = pd.DataFrame()
    if partidas is None or len(partidas) == 0 or "pais_jogo" not in partidas.columns:
        return vazio, []
    if coordenadas is None or len(coordenadas) == 0 or "name" not in coordenadas.columns:
        nomes = partidas["pais_jogo"].dropna().astype(str).unique().tolist()
        return vazio, nomes

    jogos = (
        partidas["pais_jogo"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace(NOMES_PAIS)
        .value_counts()
        .rename_axis("pais")
        .reset_index(name="jogos")
    )
    jogos = jogos[jogos["pais"] != ""]
    if len(jogos) == 0:
        return vazio, []

    coords = coordenadas.rename(columns={"name": "pais"})
    unido = jogos.merge(coords[["pais", "latitude", "longitude"]], on="pais", how="left")

    pontos = unido[unido["latitude"].notna() & unido["longitude"].notna()].copy()
    faltando = unido.loc[~unido["pais"].isin(pontos["pais"]), "pais"].tolist()
    return pontos, faltando


def preparar_eventos(eventos):
    df = eventos.copy()

    if "location" in df.columns:
        df["x"] = df["location"].apply(lambda v: _coord(v, 0))
        df["y"] = df["location"].apply(lambda v: _coord(v, 1))
    else:
        df["x"] = None
        df["y"] = None

    if "pass_end_location" in df.columns:
        df["end_x"] = df["pass_end_location"].apply(lambda v: _coord(v, 0))
        df["end_y"] = df["pass_end_location"].apply(lambda v: _coord(v, 1))
    else:
        df["end_x"] = None
        df["end_y"] = None

    if "shot_end_location" in df.columns:
        df["shot_end_x"] = df["shot_end_location"].apply(lambda v: _coord(v, 0))
        df["shot_end_y"] = df["shot_end_location"].apply(lambda v: _coord(v, 1))

    df["tipo"] = df["type"].map(TIPOS_PT).fillna(df["type"]) if "type" in df.columns else ""

    if "pass_outcome" in df.columns:
        df["passe_completo"] = (df["type"] == "Pass") & (df["pass_outcome"].isna())
    else:
        df["passe_completo"] = df["type"] == "Pass"

    if "shot_outcome" in df.columns:
        df["gol"] = (df["type"] == "Shot") & (df["shot_outcome"] == "Goal")
    else:
        df["gol"] = False

    if "shot_statsbomb_xg" not in df.columns:
        df["shot_statsbomb_xg"] = 0.0
    df["shot_statsbomb_xg"] = pd.to_numeric(df["shot_statsbomb_xg"], errors="coerce").fillna(0.0)

    if "minute" not in df.columns:
        df["minute"] = 0
    df["minute"] = pd.to_numeric(df["minute"], errors="coerce").fillna(0)

    colunas_manter = [
        "id",
        "minute",
        "second",
        "period",
        "timestamp",
        "team",
        "player",
        "position",
        "type",
        "tipo",
        "pass_recipient",
        "pass_outcome",
        "passe_completo",
        "shot_outcome",
        "shot_statsbomb_xg",
        "shot_type",
        "gol",
        "x",
        "y",
        "end_x",
        "end_y",
        "shot_end_x",
        "shot_end_y",
        "play_pattern",
        "under_pressure",
    ]
    existentes = [c for c in colunas_manter if c in df.columns]
    df = df[existentes].copy()
    return df


@st.cache_data(show_spinner="Carregando eventos...", ttl=3600)
def carregar_eventos(match_id):
    brutos = sb.events(match_id=int(match_id))
    return preparar_eventos(brutos)


def filtrar_eventos(
    eventos,
    jogador=None,
    equipe=None,
    tipos=None,
    minuto_inicio=0,
    minuto_fim=120,
    so_completos=False,
    so_gols=False,
):
    df = eventos.copy()

    if equipe and equipe != "Ambas":
        df = df[df["team"] == equipe]
    if jogador and jogador != "Todos":
        df = df[df["player"] == jogador]
    if tipos:
        df = df[df["type"].isin(tipos)]
    df = df[(df["minute"] >= minuto_inicio) & (df["minute"] <= minuto_fim)]
    if so_completos and "passe_completo" in df.columns:
        df = df[(df["type"] != "Pass") | df["passe_completo"]]
    if so_gols:
        df = df[df["gol"]]
    return df.reset_index(drop=True)


def lista_jogadores(eventos, equipe=None):
    if eventos is None or "player" not in eventos.columns:
        return []
    df = eventos
    if equipe and equipe != "Ambas" and "team" in df.columns:
        df = df[df["team"] == equipe]
    return df["player"].dropna().drop_duplicates().sort_values().tolist()


def lista_equipes(eventos, partida=None):
    if partida is not None:
        return [partida["home_team"], partida["away_team"]]
    if eventos is None or "team" not in eventos.columns:
        return []
    return eventos["team"].dropna().drop_duplicates().tolist()


def estatisticas_partida(eventos):
    passes = eventos[eventos["type"] == "Pass"]
    chutes = eventos[eventos["type"] == "Shot"]
    gols_eventos = int(eventos["gol"].sum()) if "gol" in eventos.columns else 0

    n_passes = len(passes)
    n_completos = int(passes["passe_completo"].sum()) if n_passes else 0
    n_chutes = len(chutes)
    xg = float(chutes["shot_statsbomb_xg"].sum()) if n_chutes else 0.0
    conversao = (gols_eventos / n_chutes * 100) if n_chutes else 0.0
    precisao = (n_completos / n_passes * 100) if n_passes else 0.0
    desarmes = len(eventos[eventos["type"].isin(["Duel", "Interception", "Ball Recovery"])])

    return {
        "gols": gols_eventos,
        "chutes": n_chutes,
        "passes": n_passes,
        "passes_completos": n_completos,
        "precisao_passe": precisao,
        "xg": xg,
        "conversao": conversao,
        "desarmes": desarmes,
    }


def estatisticas_jogador(eventos, jogador):
    df = eventos[eventos["player"] == jogador]
    return estatisticas_partida(df)


def resumo_por_jogador(eventos, progresso=None):
    if eventos is None or len(eventos) == 0 or "player" not in eventos.columns:
        return pd.DataFrame()

    base = eventos[eventos["player"].notna()].copy()
    if len(base) == 0:
        return pd.DataFrame()

    grupos = list(base.groupby("player"))
    total = len(grupos)

    linhas = []
    for posicao, (jogador, grupo) in enumerate(grupos, start=1):
        if progresso is not None:
            progresso(posicao / total, jogador)
        stats = estatisticas_partida(grupo)
        equipe = grupo["team"].dropna().iloc[0] if grupo["team"].notna().any() else ""
        linhas.append(
            {
                "jogador": jogador,
                "equipe": equipe,
                "passes": stats["passes"],
                "passes_completos": stats["passes_completos"],
                "precisao_passe": stats["precisao_passe"],
                "chutes": stats["chutes"],
                "gols": stats["gols"],
                "xg": stats["xg"],
                "conversao": stats["conversao"],
                "desarmes": stats["desarmes"],
            }
        )
    return pd.DataFrame(linhas).sort_values("passes", ascending=False).reset_index(drop=True)


def colunas_tabela():
    return [
        "minute",
        "second",
        "period",
        "team",
        "player",
        "tipo",
        "type",
        "pass_recipient",
        "passe_completo",
        "shot_outcome",
        "shot_statsbomb_xg",
        "gol",
        "x",
        "y",
        "end_x",
        "end_y",
    ]


def eventos_para_exibicao(eventos, limite=200, ordem="Minuto (cronológico)"):
    df = eventos.copy()
    if ordem == "xG (maior primeiro)" and "shot_statsbomb_xg" in df.columns:
        df = df.sort_values("shot_statsbomb_xg", ascending=False)
    elif ordem == "Tipo" and "tipo" in df.columns:
        df = df.sort_values(["tipo", "minute"])
    elif "minute" in df.columns:
        df = df.sort_values(["minute", "second"] if "second" in df.columns else ["minute"])
    colunas = [c for c in colunas_tabela() if c in df.columns]
    tabela = df[colunas]
    if limite is None:
        return tabela
    return tabela.head(int(limite))
