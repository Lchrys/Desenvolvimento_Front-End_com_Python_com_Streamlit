# DR1_AT - Sports Analytics com Streamlit

Dashboard que investiga **quem constrói o ataque em uma partida**: quem mais
influencia o jogo pelo volume e pela qualidade dos passes e pela eficiência
das finalizações (chutes, gols e xG).

Os dados vêm do [StatsBomb Open Data](https://github.com/statsbomb/open-data).
Os campos são desenhados com
[mplsoccer](https://mplsoccer.readthedocs.io/en/latest/gallery/index.html).

## O que contém

- **Início** (`app.py`): pergunta de pesquisa, panorama da temporada, métricas
  da partida e mapa dos países em que houve jogos.
- **Visão da partida**: tabela de eventos, mapas de passe, chute e calor,
  gráficos de relação e download em CSV.
- **Análise do jogador**: indicadores e mapas de um atleta.
- **Comparação de jogadores**: dois atletas lado a lado, com barras e mapas
  de passe.

A barra lateral escolhe campeonato, temporada, partida, equipe, jogador e a
cor do campo. A seleção permanece ao trocar de página.

O mapa de países usa o `countries.csv` da pasta do projeto, obtido de
[google/dspl](https://github.com/google/dspl/blob/master/samples/google/canonical/countries.csv),
com nomes ajustados à StatsBomb (por exemplo, `England` no lugar de
`United Kingdom`). O mapa só aparece depois do upload desse arquivo.

```
DR1_AT/
  app.py
  countries.csv
  requirements.txt
  pages/
  src/
  .streamlit/
```

## Como executar

```bash
cd DR1_AT
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

O app abre em `http://localhost:8501`.
