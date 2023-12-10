import streamlit as st
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

#taken from this StackOverflow answer: https://stackoverflow.com/a/39225039
import requests

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

genres_mapping = {
    "rock": ['alt-rock', 'alternative', 'emo', 'grunge', 'hard-rock', 'indie',
             'psych-rock', 'punk-rock', 'punk', 'rock-n-roll', 'rock', 'rockabilly'],
    "jazz-blues": ['bluegrass', 'blues', 'country', 'folk', 'gospel', 'honky-tonk',
                   'guitar', 'reggae', 'reggaeton', 'soul', 'jazz'],
    "groovy": ['dance', 'dancehall', 'disco', 'funk', 'groove', 'party', 'r-n-b', 'hip-hop', 'trip-hop'],
    "pop": ['british', 'french', 'german', 'happy', 'indie-pop', 'pop-film', 'pop',
            'power-pop', 'show-tunes', 'singer-songwriter',
            'songwriter', 'spanish', 'swedish', 'synth-pop'],
    "asian": ['anime', 'cantopop', 'j-dance', 'j-idol', 'j-pop', 'j-rock',
              'k-pop', 'malay', 'mandopop'],
    "latin": ['brazil', 'forro', 'latin', 'latino', 'mpb', 'pagode', 'salsa',
              'samba', 'sertanejo', 'ska', 'tango'],
    "metal": ['black-metal', 'death-metal', 'goth', 'grindcore', 'hardcore', 'hardstyle',
              'heavy-metal', 'metal', 'metalcore'],
    "electronic": ['club', 'deep-house', 'drum-and-bass', 'dub', 'dubstep', 'edm',
                   'electro', 'electronic', 'garage', 'house',  'trance'],
    "techno": ['breakbeat', 'chicago-house', 'detroit-techno', 'idm', 'industrial',
               'minimal-techno', 'progressive-house', 'techno'],
    "ambient-classical": ['ambient', 'chill', 'new-age', 'sleep', 'study',
                          'acoustic', 'classical', 'opera', 'piano'],
    "misc": ['afrobeat', 'indian', 'iranian', 'turkish', 'world-music',
             'children', 'comedy', 'disney', 'kids', 'romance', 'sad']
}

# This function takes a subgenre, a "finer genre" and returns the corresponding "coarse" genre.
def subgenre_to_coarse(genre):
    result = '' # default case if nothing is found
    for coarse_genre, subgenres in genres_mapping.items():
        if genre in subgenres:
            result = coarse_genre
            break
    return result


st.title('Spotify Jukebox and 2D Visualizer')

@st.cache_data
def load_data():
    #link = https://drive.google.com/file/d/160yWJMowrf_Gmzj7m2MexDCJ8rhJPOBt/view?usp=drive_link
    file_id = '160yWJMowrf_Gmzj7m2MexDCJ8rhJPOBt'
    destination = './spotify-dataset.csv'
    download_file_from_google_drive(file_id, destination)
    #data_filepath = r"C:\Users\alexg\Downloads\spotify-dataset.csv"
    df_spotify = pd.read_csv(destination)
    df_spotify['track_genre_coarse'] = df_spotify['track_genre'].apply(subgenre_to_coarse)
    #df_spotify = df_spotify.sample(frac=1)
    return df_spotify

def read_values():
    urlparams = st.experimental_get_query_params()
    return {
        "track_id": urlparams["track_id"][0] if "track_id" in urlparams else None,
    }

def save_values():
    st.experimental_set_query_params(
        track_id=str(st.session_state.track_id),
    )

state_values = read_values()
    
data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Done! (using st.cache_data)')



@st.cache_data
def get_track():
    spotify_trackid = random.choice(data['track_id'])
    return spotify_trackid

spotify_trackid = get_track()
#track_id_text = st.text(spotify_trackid)

width = 700
height = 100

spotify_element_html = f'<iframe allowTransparency="true" style="background: #FFFFFF; border-radius:12px;" src="https://open.spotify.com/embed/track/{spotify_trackid}?utm_source=generator" width="{width}" height="{height}" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'

song_text = st.text("Your randomly chosen jukebox song is...")
spotify_element = st.components.v1.html(html=spotify_element_html, width=width+30, height=height)

track_attributes_text = st.text('Attributes for this song:')
track_row = data[data['track_id'] == spotify_trackid].drop(['Unnamed: 0'], axis=1).reset_index(drop=True)
track_row_grouped = track_row.groupby('track_id').agg({'track_genre': lambda x: ", ".join(set(x)), 'track_genre_coarse': lambda x: ", ".join(set(x))}).rename({'track_genre': 'track_genres', 'track_genre_coarse': 'coarse_track_genres'}).reset_index(drop=False)
track_row = track_row.drop(['track_genre', 'track_genre_coarse'], axis=1)
track_row_grouped = track_row_grouped.merge(track_row, on='track_id', how='right').drop('track_id', axis=1).drop_duplicates()
track_attributes_table = st.table(track_row_grouped)

reroll_button = st.button(label="Roll a new song!", on_click=get_track.clear)



options = data.columns[5:-2]


x_dim = st.selectbox(label="X feature", options=options, index=0, key='x_dim', help=None, on_change=None, args=None, kwargs=None)
y_dim = st.selectbox(label="Y feature", options=options, index=0, key='y_dim', help=None, on_change=None, args=None, kwargs=None)
#z_dim = st.selectbox(label="Z feature", options=options, index=0, key='z_dim', help=None, on_change=None, args=None, kwargs=None)



#st.write(st.session_state.x_dim)
#st.write(st.session_state.y_dim)
#st.write(st.session_state.z_dim)




doPlot = st.button(label="Create Plot")

if doPlot:
    plot_state = st.text('Plotting...')
    fig = make_subplots()

    fig = px.scatter(data, x=x_dim, y=y_dim,
              color='track_genre_coarse')
    fig.add_trace(go.Scatter(x=track_row_grouped[x_dim], y=track_row_grouped[y_dim], mode = 'markers',
                         marker_symbol = 'star', marker_color = 'red',
                         marker_size = 20))
    tmp = fig.data[-1]
    tmp2 = fig.data[0]
    fig.data = (tmp, *fig.data[1:-2], tmp2)
    fig.data[0].name = 'Your Track!'
    fig.data[0].showlegend = True


    st.plotly_chart(fig, use_container_width=True, sharing="streamlit", theme="streamlit")
    plot_state.text('Plot done!')
    












