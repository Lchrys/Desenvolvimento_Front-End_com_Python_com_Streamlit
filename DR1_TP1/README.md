# TP1 - Desenvolvimento Front-End com Python (com Streamlit)

O objetivo deste primeiro trabalho é percorrer desde a criação do ambiente virtual para o projeto até o desenvolvimento local de dois dashboards para Streamlit. O primeiro é um script simples com Streamlit e o segundo é um script mais elaborado com Streamlit e Pandas.

As aplicações criadas estão divididas em duas partes, conforme estipulado no TP1.
- A Parte 1 é um script simples de Streamlit com as funcionalidades básicas.
- A Parte 2 é um script mais elaborado de Streamlit que utiliza a biblioteca Pandas e o tema de músicas do Spotify.

Instalação do Streamlit e Pandas
Antes de tudo, para o funcionamento dos scripts é necessária a instalação do Streamlit e Pandas.
Essas dependências estão contidas no arquivo requirements.txt, localizado na raiz do projeto.

1. No VS Code, abra a pasta do projeto.
2. No terminal, crie o ambiente virtual com:
   python -m virtualenv venv
3. Em seguida, ative o ambiente virtual:
   .\venv\Scripts\Activate.ps1
4. Instale as dependências:
   pip install -r requirements.txt

Com isso feito, o projeto está organizado com os seguintes arquivos (botão direto em cima do arquivo '.py' > 'open in integrated terminal'):
- TP1_DR1\Parte 1> streamlit run ex_4.py 
- TP1_DR1\Parte 2> streamlit run ex_5-12.py 

### Parte 1
Para executar a Parte 1, no terminal insira:
streamlit run "Parte 1/ex_4.py"

### Parte 2
Para executar a Parte 2, no terminal insira:
streamlit run "Parte 2/ex_5-12.py"

Na Parte 2, o dataset é carregado a partir do arquivo data/MostStreamedSpotifySongs2024.csv.

O script da Parte 2 utiliza:
- import streamlit as st
- import pandas as pd

### Informações adicionais
- O arquivo de dependências do projeto está em requirements.txt, na raiz do projeto.
- O dataset utilizado na Parte 2 está localizado em data/MostStreamedSpotifySongs2024.csv.