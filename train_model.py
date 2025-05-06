import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

inputs = [
    "admin", "password123", "hello", "testuser",
    "' OR 1=1 --", "'; DROP TABLE users; --", "' OR 'a'='a", "' UNION SELECT *"
]
labels = [0, 0, 0, 0, 1, 1, 1, 1]  # 0 = safe, 1 = SQLi

vectorizer = TfidfVectorizer(ngram_range=(1,2), analyzer='char')
X = vectorizer.fit_transform(inputs)

model = LogisticRegression()
model.fit(X, labels)

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
