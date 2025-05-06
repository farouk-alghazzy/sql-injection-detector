import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

inputs = [
    "admin", "user123", "hello", "john_doe", "testaccount", "securelogin", "mypassword", "letmein",
    
    "' OR 1=1 --", "' OR '1'='1", "' UNION SELECT *", "'; DROP TABLE users; --",
    "' OR '' = '", "'; EXEC xp_cmdshell('dir'); --", "\" OR \"\" = \"", "admin'--", "' OR SLEEP(5)#"
]

labels = [
    0, 0, 0, 0, 0, 0, 0, 0,     
    1, 1, 1, 1, 1, 1, 1, 1, 1   
]

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3))
X = vectorizer.fit_transform(inputs)

model = LogisticRegression()
model.fit(X, labels)

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("[+] Training complete. model.pkl and vectorizer.pkl saved.")
