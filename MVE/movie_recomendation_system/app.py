import streamlit as st
import pickle
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

# Function to set a black futuristic digital-themed background
# Function to set a professional dark streaming theme
def set_bg():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');

        /* Dark Premium Gradient Background */
        .stApp {
            background: radial-gradient(circle at top, #13112b 0%, #090814 60%, #05040a 100%);
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }

        /* Title Logo Styling */
        h1 {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800;
            text-align: center;
            background: linear-gradient(135deg, #c084fc 0%, #6366f1 50%, #4f46e5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 52px;
            letter-spacing: -1.5px;
            margin-bottom: 10px !important;
        }

        /* Select Box Styling */
        div[data-testid="stSelectbox"] > div {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(12px);
            padding: 4px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div[data-testid="stSelectbox"] > div:hover {
            border-color: rgba(99, 102, 241, 0.4) !important;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.1);
        }
        div[data-testid="stSelectbox"] span {
            color: #e2e8f0 !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Recommendation Button Styling */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 28px !important;
            font-size: 15px !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5) !important;
            background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%) !important;
        }
        div.stButton > button:first-child:active {
            transform: translateY(0px) !important;
        }

        /* Movie Container Cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 16px !important;
            padding: 14px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-6px) !important;
            border-color: rgba(99, 102, 241, 0.25) !important;
            background: rgba(255, 255, 255, 0.04) !important;
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4) !important;
        }

        /* Inner Button inside Cards */
        .stContainer button {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #e2e8f0 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        .stContainer button:hover {
            background: rgba(99, 102, 241, 0.2) !important;
            border-color: #6366f1 !important;
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()  # Apply background & styling

# Function to fetch movie details from TMDb API with caching to make it instant
@st.cache_data
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&append_to_response=watch/providers"
    
    # Fallback in case of API failure or connection drop
    fallback = {
        'poster': "https://via.placeholder.com/500x750?text=No+Image",
        'runtime': 'N/A',
        'rating': 0.0,
        'overview': 'Movie details are currently unavailable (connection issue).',
        'providers': []
    }
    
    try:
        from requests.adapters import HTTPAdapter
        from urllib3.util import Retry
        
        # Configure automatic retries with a small backoff factor for rate-limiting protection
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # Make the request with a timeout
        response = session.get(url, timeout=4)
        response.raise_for_status()
        data = response.json()
    except Exception:
        # Return fallback dictionary instead of throwing exception and crashing
        return fallback
    
    poster_path = data.get('poster_path')
    poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else fallback['poster']
    
    # Extract Watch Providers (US)
    providers = []
    us_providers = data.get('watch/providers', {}).get('results', {}).get('US', {})
    if 'flatrate' in us_providers:
        providers.extend([p['provider_name'] for p in us_providers['flatrate']])
    
    return {
        'poster': poster_url,
        'runtime': data.get('runtime', 'N/A'),
        'rating': round(data.get('vote_average', 0), 1),
        'overview': data.get('overview', 'No overview available.'),
        'providers': list(set(providers))[:3] # Show up to 3 streaming services
    }

# Function to get movie recommendations (optimized with ThreadPoolExecutor)
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    top_movies = distances[1:6]

    def get_details(item):
        idx, sim_score = item
        movie_id = movies.iloc[idx].movie_id
        details = fetch_movie_details(movie_id)
        # Create a copy so we don't accidentally mutate the cached result dictionary
        details_copy = details.copy()
        details_copy['title'] = movies.iloc[idx].title
        details_copy['similarity'] = round(sim_score * 100, 2)
        return details_copy

    # Fetch all 5 movies concurrently using threads to reduce network latency
    with ThreadPoolExecutor(max_workers=5) as executor:
        recommendations = list(executor.map(get_details, top_movies))

    return recommendations

# Load the movie dataset and similarity matrix with caching
@st.cache_resource
def load_data():
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

if isinstance(movies, pd.DataFrame):
    movie_titles = movies['title'].values
else:
    raise ValueError("movie_list.pkl does not contain a valid DataFrame!")

# Streamlit UI with futuristic styling
st.markdown("<h1>🎬 CINEVERSE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-family: Inter, sans-serif; font-size: 16px; margin-top: -15px; margin-bottom: 35px;'>Discover your next favorite movie powered by advanced AI recommendations</p>", unsafe_allow_html=True)

selected_movie = st.selectbox(
    '',
    movie_titles,
    index=None,  # Makes it unselected initially
    placeholder="🎬 Enter your preference...",  # This makes it appear inside the select box
)

@st.dialog("Movie Details", width="large")
def show_movie_details(rec):
    # Format streaming providers
    providers_text = ", ".join(rec['providers']) if rec['providers'] else "VOD / Rent Only"
    
    # Custom HTML/CSS card for premium UI layout inside the modal
    html_content = f"""
    <div style="
        display: flex; 
        flex-direction: row; 
        gap: 28px; 
        background-color: #0c0b15; 
        padding: 24px; 
        border-radius: 18px; 
        border: 1px solid rgba(255, 255, 255, 0.08); 
        box-shadow: 0px 12px 36px rgba(0, 0, 0, 0.6);
        align-items: flex-start;
        font-family: 'Inter', sans-serif;
        color: #f1f5f9;
    ">
        <!-- Left: Poster Column -->
        <div style="flex-shrink: 0; width: 220px;">
            <img src="{rec['poster']}" style="
                width: 100%; 
                border-radius: 12px; 
                border: 1px solid rgba(255, 255, 255, 0.1); 
                box-shadow: 0px 8px 24px rgba(0,0,0,0.5);
                object-fit: cover;
            "/>
        </div>
        
        <!-- Right: Content Column -->
        <div style="flex-grow: 1;">
            <h1 style="
                margin-top: 0; 
                margin-bottom: 10px; 
                color: #ffffff; 
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 32px;
                font-weight: 800;
                background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: left;
            ">{rec['title']}</h1>
            
            <div style="display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;">
                <span style="
                    background: rgba(99, 102, 241, 0.12); 
                    color: #818cf8; 
                    padding: 5px 12px; 
                    border-radius: 8px; 
                    font-size: 13px; 
                    font-weight: 600; 
                    border: 1px solid rgba(99, 102, 241, 0.25);
                ">🎯 {rec['similarity']}% Match</span>
                
                <span style="
                    background: rgba(245, 158, 11, 0.12); 
                    color: #fbbf24; 
                    padding: 5px 12px; 
                    border-radius: 8px; 
                    font-size: 13px; 
                    font-weight: 600; 
                    border: 1px solid rgba(245, 158, 11, 0.25);
                ">⭐ {rec['rating']} Rating</span>
                
                <span style="
                    background: rgba(14, 165, 233, 0.12); 
                    color: #38bdf8; 
                    padding: 5px 12px; 
                    border-radius: 8px; 
                    font-size: 13px; 
                    font-weight: 600; 
                    border: 1px solid rgba(14, 165, 233, 0.25);
                ">🕒 {rec['runtime']} min</span>
            </div>
            
            <div style="
                background: rgba(255, 255, 255, 0.02); 
                padding: 16px; 
                border-radius: 12px; 
                border: 1px solid rgba(255, 255, 255, 0.05); 
                margin-bottom: 20px;
            ">
                <span style="color: #94a3b8; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">📺 Available to Stream</span><br/>
                <span style="font-size: 15px; font-weight: 500; color: #e2e8f0; display: inline-block; margin-top: 4px;">{providers_text}</span>
            </div>
            
            <div style="line-height: 1.6; font-size: 14px;">
                <span style="color: #94a3b8; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">🎬 Synopsis</span>
                <p style="margin-top: 6px; color: #cbd5e1; font-family: 'Inter', sans-serif;">{rec['overview']}</p>
            </div>
        </div>
    </div>
    """
    st.html(html_content)

if st.button('🔍 Show Recommendation'):
    if not selected_movie:
        st.warning("Please select a movie from the dropdown first!")
    else:
        st.session_state['recommendations'] = recommend(selected_movie)

if 'recommendations' in st.session_state:
    st.markdown("<h3 style='margin-top: 40px; margin-bottom: 20px; font-family: \"Plus Jakarta Sans\", sans-serif; color: #f1f5f9; font-weight: 700;'>Recommended Movies</h3>", unsafe_allow_html=True)
    # Display movie recommendations in a row
    cols = st.columns(5)
    for i, rec in enumerate(st.session_state['recommendations']):
        with cols[i]:
            with st.container(border=True):
                # Title with a clean clamped font layout
                st.markdown(f"<h4 style='color: #f1f5f9; font-family: \"Plus Jakarta Sans\", sans-serif; font-size: 15px; font-weight: 700; margin: 0 0 12px 0; min-height: 40px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;'>{rec['title']}</h4>", unsafe_allow_html=True)
                st.image(rec['poster'], use_container_width=True)
                st.write("") # spacing
                
                # Using a button to trigger the dialog
                if st.button("✨ Details", key=f"more_info_{i}", use_container_width=True):
                    show_movie_details(rec)
