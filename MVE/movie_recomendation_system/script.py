import numpy as np
import pandas as pd

movies=pd.read_csv('tmdb_5000_movies.csv')
credits=pd.read_csv('tmdb_5000_credits.csv')

movies.head()
movies=movies.merge(credits,on="title")
movies.head(1)
#genres
#id
#keywords
#title
#overview
#cast
#crew
movies= movies[['movie_id','title',"overview",'genres','keywords','cast','crew']]
movies['original_language'].value_counts()
movies.info()
movies.head()
movies.isnull().sum()
movies.dropna(inplace=True)
movies.duplicated().sum()
movies.iloc[0].genres
import ast #to change string of list into list

def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name']) 
    return L 

movies.dropna(inplace=True)

movies['genres'] = movies['genres'].apply(convert)
movies.head()
movies['keywords']=movies['keywords'].apply(convert)
movies.head()

def convert3(text):
    L = []
    counter = 0
    for i in ast.literal_eval(text):
        if counter < 3:
            L.append(i['name'])
        counter+=1
    return L  

movies['cast'] = movies['cast'].apply(convert)
movies.head()

def fetch_director(text):
    L = []
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L 
movies['crew'] = movies['crew'].apply(fetch_director)
movies.head()
movies['overview'][0]
movies['overview'] = movies['overview'].apply(lambda x:x.split())
movies.head()
def collapse(L):
    L1 = []
    for i in L:
        L1.append(i.replace(" ",""))
    return L1
movies['cast'] = movies['cast'].apply(collapse)
movies['crew'] = movies['crew'].apply(collapse)
movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)
movies.head()
movies['tags'] = movies['overview'].astype(str) + " " + \
                 movies['genres'].astype(str) + " " + \
                 movies['keywords'].astype(str) + " " + \
                 movies['cast'].astype(str) + " " + \
                 movies['crew'].astype(str)

movies.head()
new_df = movies.drop(columns=['overview','genres','keywords','cast','crew'])

new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))

new_df.head()

from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(max_features=5000, stop_words='english')

# Ensure 'tags' column exists and is a string
if 'tags' in movies.columns:
    movies['tags'] = movies['tags'].astype(str)
    
    # Transform the 'tags' column into a numerical matrix
    vector = cv.fit_transform(movies['tags']).toarray()
    
    print("Transformation Successful! Shape:", vector.shape)
else:
    print("Error: Column 'tags' not found in DataFrame!")

vector.shape
import nltk
from nltk.stem.porter import PorterStemmer

ps = PorterStemmer()  # Initialize the stemmer

def stem(text):
    y = []
    for word in text.split():
        y.append(ps.stem(word))  # Append stemmed word to the list
    return " ".join(y)  # Join the list back into a string

# Ensure 'tags' column exists and is a string
if 'tags' in new_df.columns:
    new_df['tags'] = new_df['tags'].astype(str).fillna("").apply(stem)
    print("Stemming applied successfully!")
else:
    print("Error: 'tags' column not found!")

from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity(vector)  # Compute similarity
print(similarity.shape)  # ✅ Use `.shape` (not `.shape()`)

def recommend(movie):
    # Ensure the movie exists in the DataFrame
    if movie not in new_df['title'].values:
        print(f"Error: '{movie}' not found in the dataset!")
        return
    
    # Get index of the given movie
    index = new_df[new_df['title'] == movie].index[0]

    # Compute similarity scores and sort them
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    # Print top 5 recommendations (excluding the movie itself)
    print(f"Top 5 movie recommendations for '{movie}':")
    for i in distances[1:6]:  
        print(new_df.iloc[i[0]]['title'])  # Correct indexing

        
recommend("Inception")
import pickle

pickle.dump(new_df,open('movie_list.pkl','wb'))
pickle.dump(similarity,open('similarity.pkl','wb'))
print(new_df)
