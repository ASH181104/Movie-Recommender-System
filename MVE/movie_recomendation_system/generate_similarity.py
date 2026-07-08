import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading movie_list.pkl...")
movies = pickle.load(open('movie_list.pkl', 'rb'))

print("Cleaning tags...")
def clean_tags(text):
    if isinstance(text, str):
        return text.replace(' ', '').replace('[', '').replace(']', '').replace(',', ' ').replace('\'', '')
    return str(text)

movies['clean_tags'] = movies['tags'].apply(clean_tags)

print("Vectorizing...")
cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(movies['clean_tags']).toarray()

print("Calculating similarity...")
similarity = cosine_similarity(vector)

print("Saving similarity.pkl...")
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Done!")
