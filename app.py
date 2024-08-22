from collections import Counter
from flask import Flask, render_template, request
from dotenv import load_dotenv
import urllib.request
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()  

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

artistas = {
    "Ed Sheeran": "6eUKZXaKkcviH0Ku9w2n3V",
    "Queen": "1dfeR4HaWDbWqFHLkxsg1d",
    "Ariana Grande": "66CXWjxzNUsdJxJ2JdwvnR",
    "Maroon 5": "04gDigrS5kc9YWfZHwBETP",
    "Imagine Dragons": "53XhwfbYqKCa1cC15pYq2q",
    "Eminem": "7dGJo4pcD2V6oG8kP0tJRR",
    "Lady Gaga": "1HY2Jd0NmPuamShAr6KMms",
    "Coldplay": "4gzpq5DPGxSnKTe4SA8HAU",
    "Beyonce": "6vWDO969PvNqNYHIOW5v0m",
    "Bruno Mars": "0du5cEVh5yTK9QJze8zA0C",
    "Rihanna": "5pKCCKE2ajJHZ9KAiaK11H",
    "Shakira": "0EmeFodog0BfCgMzAIvKQp",
    "Justin Bieber": "1uNFoZAHBGtllmzznpCI3s",
    "Demi Lovato": "6S2OmqARrzebs0tKUEyXyp",
    "Taylor Swift": "06HL4z0CvFAxyc27GXpf02"
}

def obter_seguidores(artista):
    return artista['followers']

def formartar_seguidores(value):
    return "{:,}".format(value).replace(",", ".")

informacoes_artistas = []

for nome, id_artista in artistas.items():
    dados_artista = sp.artist(id_artista)
    informacoes_artistas.append({
        'name': dados_artista['name'],
        'followers': dados_artista['followers']['total'],
        'genres': dados_artista['genres'],
        'image_url': dados_artista['images'][0]['url'] if dados_artista['images'] else '/path/to/default/image.jpg',
        'popularity': dados_artista['popularity']
    })

tierlist_pop = sorted(
    [artista for artista in informacoes_artistas if 'pop' in artista['genres']],
    key=obter_seguidores,
    reverse=True # ordem descendente
)

generos = [genero for artista in informacoes_artistas for genero in artista['genres']]
generos_contagem = Counter(generos)

ranking_generos = generos_contagem.most_common(5) # top 5 gêneros mais comuns

@app.template_filter('formartar_seguidores')
def formartar_seguidores_filter(value):
    return "{:,}".format(value).replace(",", ".")

@app.route("/obter_rankings", methods=["POST"])
def obter_rankings():
    data = {
        "tierlist_pop": tierlist_pop,
        "ranking_generos": ranking_generos
    }

    url = "http://localhost:5000/callback"  
    try:
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(data)
        jsondataasbytes = jsondata.encode('utf-8')   
        req.add_header('Content-Length', len(jsondataasbytes))
    
        response = urllib.request.urlopen(req, jsondataasbytes)
        return f"Rankings enviados com sucesso! Status: {response.status}"
    except Exception as e:
        return f"Ocorreu um erro ao enviar os rankings: {str(e)}"

@app.route("/")
def home():
    return render_template("rankings.html", tierlist_pop=tierlist_pop, ranking_generos=ranking_generos)

if __name__ == "__main__":
    app.run(debug=True)