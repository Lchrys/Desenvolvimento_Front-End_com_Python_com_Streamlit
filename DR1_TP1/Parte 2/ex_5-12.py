import streamlit as st
import pandas as pd

# EXERCÍCIO 5:
st.title("TP1 - Desenvolvimento Front-End com Python (com Streamlit)")
st.header('\U0001F3B6'"Most Streamed Spotify Songs - 2024")
st.subheader('\U0001F3B6'"'Músicas mais transmitidas do Spotify - 2024'")
st.text("Descrição:")
st.markdown("""
**This dataset presents a comprehensive compilation of the most streamed songs on Spotify in 2024. 
It provides extensive insights into each track's attributes, popularity, and presence on various music platforms, offering a valuable resource for music analysts, enthusiasts, and industry professionals. 
The dataset includes information such as track name, artist, release date, ISRC, streaming statistics, and presence on platforms like YouTube, TikTok, and more.** FONTE: https://www.kaggle.com/datasets/nelgiriyewithana/most-streamed-spotify-songs-2024)
""")

# EXERCÍCIO 6:
# Carregar o dataset e codificação:
file_path = r'..\data\MostStreamedSpotifySongs2024.csv'
spotify_data= pd.read_csv(file_path, encoding='ISO-8859-1')

# Exibir o DataFrame e Table:
st.subheader("**DataFrame** - Músicas mais transmitidas do Spotify - 2024")
st.dataframe(spotify_data)
st.subheader("**Table** - Músicas mais transmitidas do Spotify - 2024")
st.table(spotify_data.head(10)) # Exibição do DataFrame como tabela (limite de 10)

# EXERCÍCIO 7:
# Remove as vírgulas e converte streams para número
spotify_data["Spotify Streams"] = pd.to_numeric(
    spotify_data["Spotify Streams"].str.replace(",", ""))

# Ordena por streams e remove músicas com o mesmo título
top_musicas = (
    spotify_data
    .dropna(subset=["Spotify Streams"])
    .sort_values(by="Spotify Streams", ascending=False)
    .drop_duplicates(subset=["Track"])
    .head(3))

# Exibe as métricas
st.subheader("\U0001F3C6 Top 3 músicas mais escutadas no Spotify até 2024")

for coluna, (_, musica) in zip(st.columns(3), top_musicas.iterrows()):
    with coluna:
        st.metric(
            label=musica["Track"],
            value=f"{int(musica['Spotify Streams']):,}".replace(",", "."),
            delta=f"Artista: {musica['Artist']}")

# EXERCÍCIO 8:
# Exibição do dataframe usando write():
st.write("### Dataframe com Top 3 Músicas - Para mais informações"'\U0001F44D')
st.write(top_musicas) # Aproveitando o exercício anterior

# Exibição markdown usando write():
st.write("### Quem é The Weeknd"'\U00002753')
st.write("*Abel Makkonen Tesfaye*, mais conhecido por seu nome artístico **The Weeknd**, é um cantor, compositor, ator e produtor musical canadense. Conhecido por sua versatilidade sonora e lirismo sombrio, suas músicas exploram temas de escapismo, romance e melancolia, e é frequentemente inspirada em experiências pessoais.")

# Músicas de The Weeknd filtradas pela colunas Artist e;
# Exibição de uma lista com base nas músicas de The Weeknd:
weeknd_musicas = spotify_data[spotify_data['Artist'] == 'The Weeknd']

st.write("### Top 3 Músicas de The Weeknd:"'\U0001F51D')
st.write([
    f"1. {weeknd_musicas.iloc[0]['Track']}",
    f"2. {weeknd_musicas.iloc[1]['Track']}",
    f"3. {weeknd_musicas.iloc[2]['Track']}"
])


#EXERCÍCIO 9:
# Título e texto com magic:
"""
### Quem é Ed Sheeran\U00002753
Edward Christopher Sheeran MBE, mais conhecido como Ed Sheeran é um cantor, compositor, produtor e ator britânico.  Os dois primeiros singles do álbum, "Shape of You" e "Castle on the Hill", bateram recordes em vários países ao estrearem nas duas primeiras posições das paradas. Ele também se tornou o primeiro artista a ter duas músicas estreando no top 10 dos EUA na mesma semana.
"""
# Título e lista com Magic:
"""
### Top 3 Músicas de Ed Sheeran: \U0001F51D
"""
EdSheeran_musicas= spotify_data[spotify_data['Artist'] == 'Ed Sheeran']
([
    f"1. {EdSheeran_musicas.iloc[0]['Track']}",
    f"2. {EdSheeran_musicas.iloc[1]['Track']}",
    f"3. {EdSheeran_musicas.iloc[2]['Track']}"
])

ed_sheeran_musicas = spotify_data[spotify_data['Artist'] == 'Ed Sheeran']
top_ed_sheeran = ed_sheeran_musicas.sort_values(by='Spotify Streams', ascending=False).head(3)
top_the_weeknd = weeknd_musicas.sort_values(by='Spotify Streams', ascending=False).head(3)

# Concatenação dos DataFrames com ordem decrescente por Spotify Streams:
ed_x_wkd = pd.concat([top_ed_sheeran, top_the_weeknd]).sort_values(by='Spotify Streams', ascending=False)

# Exibir o DataFrame:
"""
### 🔥 **Top Músicas de Ed Sheeran e The Weeknd** 🔥
"""
ed_x_wkd

# EXERCÍCIO 10:
# Inserção de imagem, video e audio:

def the_wkd():
    st.write("## 1. Blinding Lights - The Weeknd \U0001F947")
    st.write("4,28 Bilhões")
    st.video("https://www.youtube.com/watch?v=4NRXx6U8ABQ")

def shape():
    st.write("## 2. Shape of You - Ed Sheeran \U0001F948")
    st.write("3,90 Bilhões")
    st.audio(
        "https://upload.wikimedia.org/wikipedia/pt/c/ce/"
        "Ed_Sheeran_-_Shape_of_You_%28áudio%29.ogg"    )

def lewis_capaldi():
    st.write("## 3. Someone You Loved - Lewis Capaldi \U0001F949")
    st.write("3,42 Bilhões")
    st.image(
        "https://upload.wikimedia.org/wikipedia/pt/7/7d/SYL_Lewis.png?utm_source=pt.wikipedia.org&utm_campaign=index&utm_content=thumbnail_unscaled&_=20200117214212",
        caption="Lewis Capaldi - Someone You Loved"    )

# Do EXERCÍCIO 10. Para organizar:
the_wkd()
shape()
lewis_capaldi()

#EXERCÍCIO 11:
# Os unicodes (para gif) foram colocados ao longo do script. GIF a seguir com st.image():
def rick_gif():
    st.image('https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExcXRsMWl5MWpzdnR1Y2tkN2lueThwNmkxNThlNm41bjhlcnl1Z3lsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/olAik8MhYOB9K/giphy.webp')

"""# FIM"""
rick_gif()

#EXERCÍCIO 12:
st.divider()

st.header("🎧 Dashboard Final — Spotify Songs 2024")
st.subheader("📊 Ranking das músicas mais transmitidas")

st.markdown("""
**Este dashboard apresenta uma análise das músicas mais populares do Spotify em 2024.**
Foram utilizados textos formatados, DataFrames, métricas, elementos multimídia,
emojis, comandos Magic e um gráfico para tornar a análise mais visual e informativa.
""")

# Top 10 streams
top_10_grafico = (
    spotify_data
    .dropna(subset=["Spotify Streams"])
    .sort_values(by="Spotify Streams", ascending=False)
    .drop_duplicates(subset=["Track"])
    .head(10)
    [["Track", "Artist", "Spotify Streams"]]
    .copy())


st.subheader("📈 Gráfico: Top 10 músicas com mais streams")


# Define as músicas como rótulos do gráfico
dados_grafico = top_10_grafico.set_index("Track")[["Spotify Streams"]]


st.bar_chart(dados_grafico, use_container_width=True)


st.subheader("📋 Dados utilizados no gráfico")


st.dataframe(
    top_10_grafico,
    use_container_width=True,
    hide_index=True)


st.subheader("🏆 Top 3 músicas mais escutadas")


# Cria três colunas
coluna1, coluna2, coluna3 = st.columns(3)
musica1 = top_musicas.iloc[0]
musica2 = top_musicas.iloc[1]
musica3 = top_musicas.iloc[2]


with coluna1:
    st.metric(
        label=musica1["Track"],
        value=f"{int(musica1['Spotify Streams']):,}".replace(",", "."),
        delta=f"Artista: {musica1['Artist']}"    )
with coluna2:
    st.metric(
        label=musica2["Track"],
        value=f"{int(musica2['Spotify Streams']):,}".replace(",", "."),
        delta=f"Artista: {musica2['Artist']}"    )
with coluna3:
    st.metric(
        label=musica3["Track"],
        value=f"{int(musica3['Spotify Streams']):,}".replace(",", "."),
        delta=f"Artista: {musica3['Artist']}"    )


# Comandos magic
"""
## 🎶 Conclusão


A aplicação utiliza o dataset **Most Streamed Spotify Songs 2024** para apresentar
informações de forma visual, interativa e organizada. O Streamlit permite transformar
dados carregados com Pandas em dashboards com métricas, tabelas, gráficos e multimídia.
"""


[
    "🎵 Dataset com Pandas",
    "📋 DataFrame no Streamlit",
    "📊 Gráfico com st.bar_chart()",
    "🏆 Métricas com st.metric()",
    "🎬 Vídeo, áudio, imagem e GIF"
]
