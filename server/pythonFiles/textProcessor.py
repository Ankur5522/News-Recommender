import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import spacy
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Download NLTK data
# nltk.download('stopwords')
# nltk.download('wordnet')

nlp = spacy.load("en_core_web_trf")

def clean_text(text):
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d', ' ', text)
    
    tokens = text.lower().split()

    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]

    return ' '.join(lemmatized_words)

# TF-IDF Extraction
def extract_keywords_tfidf(text, max_features=20):
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()
    keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
    return sorted(keywords, key=lambda x: x[1], reverse=True)

# Named Entity Recognition
def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Topic Modeling (LDA)
def extract_topics_lda(text, num_topics=3):
    words = [word for word in text.split() if word.isalpha()]
    dictionary = corpora.Dictionary([words])
    corpus = [dictionary.doc2bow(words)]
    lda = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    topics = lda.print_topics(num_words=5)
    return topics

if __name__ == "__main__":
    import sys
    raw_text = sys.stdin.read()

    cleaned_text = clean_text(raw_text)

    keywords = extract_keywords_tfidf(cleaned_text)

    entities = extract_entities(cleaned_text)

    topics = extract_topics_lda(cleaned_text)

    result = {
        "keywords": keywords,
        "entities": entities,
        "topics": topics
    }

    print(json.dumps(result))
