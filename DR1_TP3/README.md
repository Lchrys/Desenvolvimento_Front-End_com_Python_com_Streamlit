# TP3 - Turismo Rio (Streamlit)

Painel com a chegada mensal de turistas internacionais no Rio de Janeiro (2006–2019), usando os XLS da seção Turismo do [Data.Rio](https://www.data.rio/):

- [via aérea](https://www.data.rio/documents/a6c6c3ff7d1947a99648494e0745046d/about)
- [via marítima](https://www.data.rio/documents/45fa86aa30374bfabd369e6d64179071/about)

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app_tp3_lucas_pederneiras.py
```

Na tela do streamlit, envie os arquivos XLS baixados do Data.Rio (2675 e 2676) encontrados nos links citados (presentes também na pasta dados).
