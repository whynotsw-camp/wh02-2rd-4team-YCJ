from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# TF-IDF 유사도 계산
def calculate_similarity_tfidf(texts, user_keywords):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts + [" ".join(user_keywords)])
    return cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

# NLP 기반 유사도 계산
def calculate_similarity_nlp(texts, user_keywords):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    user_embedding = model.encode(" ".join(user_keywords))
    video_embeddings = model.encode(texts)
    return cosine_similarity([user_embedding], video_embeddings)[0]
