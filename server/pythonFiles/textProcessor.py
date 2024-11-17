import re
import json
import nltk
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import spacy
from keybert import KeyBERT

# Load NLP models
kw_model = KeyBERT()
nlp = spacy.load("en_core_web_sm")

# Clean text function
def clean_text(text):
    text = re.sub(r'\W', ' ', text)
    text = text.replace("\r", "")
    text = re.sub(r'\d', ' ', text)
    tokens = text.lower().split()
    
    lemmatizer = nltk.stem.WordNetLemmatizer()
    stop_words = set(nltk.corpus.stopwords.words('english'))
    filtered_words = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    
    return ' '.join(filtered_words)

# Extract entities using Named Entity Recognition (NER)
def extract_entities(text):
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT"]:
            entities[ent.text] = 1.5 if ent.label_ == "PERSON" else 1.2  # Higher weight for people
    return entities

# Extract keywords with KeyBERT
def extract_keywords_keybert(text, top_n=10):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), top_n=top_n)
    return {kw: weight * 1.3 for kw, weight in keywords}  # Increase weight for multi-word keyphrases

# Topic Modeling (LDA)
def extract_topics_lda(text, num_topics=3):
    words = [word for word in text.split() if word.isalpha()]
    dictionary = corpora.Dictionary([words])
    corpus = [dictionary.doc2bow(words)]
    lda = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    
    topics = lda.print_topics(num_words=5)
    topic_words = {}
    for topic in topics:
        words_weights = topic[1].split(" + ")
        for word_weight in words_weights:
            weight, word = word_weight.split("*")
            word = word.strip('"')
            topic_words[word] = float(weight) * 0.5  # Lower weight for general topics
    
    return topic_words

# Combine tags and weights without redundancy, applying minimum significance threshold
def combine_tags_weights(topics, entities, keybert_keywords, min_weight=0.4):
    combined_tags = {}

    # Add LDA Topics
    for word, weight in topics.items():
        if weight >= min_weight:
            combined_tags[word] = combined_tags.get(word, 0) + weight

    # Add Named Entities
    for word, weight in entities.items():
        combined_tags[word] = combined_tags.get(word, 0) + weight

    # Add KeyBERT Keywords
    for word, weight in keybert_keywords.items():
        combined_tags[word] = combined_tags.get(word, 0) + weight

    # Sort tags by weight
    return sorted(combined_tags.items(), key=lambda x: x[1], reverse=True)

def process_text(raw_text):
    # Clean and process text
    cleaned_text = clean_text(raw_text)

    # Extract tags and weights using NER, KeyBERT, and LDA
    topics = extract_topics_lda(cleaned_text)
    entities = extract_entities(raw_text)  # Use raw text for named entities
    keybert_keywords = extract_keywords_keybert(raw_text)

    # Combine and filter tags by significance
    tags_with_weights = combine_tags_weights(topics, entities, keybert_keywords)

    # Format as JSON output
    result = {
        "tags": [{"tag": tag, "weight": round(weight, 2)} for tag, weight in tags_with_weights]
    }

    return json.dumps(result, indent=4)

if __name__ == "__main__":
    import sys
    raw_text = sys.stdin.read()

    # Clean and process text
    cleaned_text = clean_text(raw_text)

    # Extract tags and weights using NER, KeyBERT, and LDA
    topics = extract_topics_lda(cleaned_text)
    entities = extract_entities(raw_text)  # Use raw text for named entities
    keybert_keywords = extract_keywords_keybert(raw_text)

    # Combine and filter tags by significance
    tags_with_weights = combine_tags_weights(topics, entities, keybert_keywords)

    # Format as JSON output
    result = {
        "tags": [{"tag": tag, "weight": round(weight, 2)} for tag, weight in tags_with_weights]
    }

    print(json.dumps(result, indent=4))