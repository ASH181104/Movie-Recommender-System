import streamlit as st
import pickle
import pandas as pd
import requests

# Function to set a black futuristic digital-themed background
def set_bg():
    st.markdown(
        """
        <style>
        /* Black Futuristic Background with Digital Grid */
        .stApp {
            background-color: black;
            background-image: radial-gradient(circle, rgba(0, 255, 255, 0.2) 10%, rgba(0, 0, 0, 1) 80%), 
                              url('https://www.transparenttextures.com/patterns/circuit-board.png');
            background-size: cover;
            background-attachment: fixed;
            color: white;
        }

        /* Title Styling */
        h1 {
            font-family: 'Orbitron', sans-serif;
            text-align: center;
            color: #00ffff;
            font-size: 50px;
            text-shadow: 0px 0px 15px #00ffff, 0px 0px 25px #0077ff;
            letter-spacing: 3px;
        }

        /* Select Box Styling */
        div[data-testid="stSelectbox"] > div {
            background: black;
            border: 2px solid #00ffcc;
            color: white;
            font-size: 18px;
            font-family: 'Orbitron', sans-serif;
            border-radius: 10px;
            padding: 8px;
        }

        /* Button Styling */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #ff00ff, #ff6600);
            color: white;
            font-size: 20px;
            font-family: 'Orbitron', sans-serif;
            border-radius: 10px;
            padding: 12px 25px;
            border: 2px solid white;
            transition: 0.3s ease-in-out;
            text-shadow: 0px 0px 10px white;
            box-shadow: 0px 0px 20px #ff00ff;
        }
        div.stButton > button:first-child:hover {
            background: linear-gradient(90deg, #ff6600, #ff00ff);
            transform: scale(1.1);
            box-shadow: 0px 0px 30px #ff00ff;
        }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True
    )

set_bg()  # Apply background & styling

# Function to fetch the movie poster from TMDb API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')

    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Image"

# Function to get movie recommendations
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# Load the movie dataset and similarity matrix
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

if isinstance(movies, pd.DataFrame):
    movie_titles = movies['title'].values
else:
    raise ValueError("movie_list.pkl does not contain a valid DataFrame!")

# Streamlit UI with futuristic styling
st.markdown("<h1>🚀 MOVIE RECOMMENDER SYSTEM</h1>", unsafe_allow_html=True)

selected_movie = st.selectbox(
    '',
    movie_titles,
    index=None,  # Makes it unselected initially
    placeholder="🎬 Enter your preference...",  # This makes it appear inside the select box
)

if st.button('🔍 Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    # Display movie recommendations in a row
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.markdown(f"<h4 style='color: #ffcc00; text-shadow: 0px 0px 5px #ffcc00;'>{recommended_movie_names[i]}</h4>", unsafe_allow_html=True)
            st.image(recommended_movie_posters[i])
