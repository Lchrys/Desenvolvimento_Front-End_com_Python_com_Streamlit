# TP2 - Desenvolvimento Front-End com Python (com Streamlit)

O objetivo deste trabalho é construir um dashboard interativo de COVID-19 no Brasil, explorando visualizações nativas do Streamlit e bibliotecas como Matplotlib, Seaborn, Altair, Plotly e PyDeck.

Os dados vêm do [Painel Coronavírus](https://covid.saude.gov.br/) do Ministério da Saúde: 12 CSVs `HIST_PAINEL_COVIDBR` (duas partes por ano, 2020–2025), reunidos em um único DataFrame.

## Como rodar

```bash
cd DR1_TP2
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
