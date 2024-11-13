import newspaper
import json

def fetch_article(url):
    article = newspaper.Article(url)
    
    try:
        article.download()
        article.parse()
    except Exception as e:
        return {"error": str(e)}
    
    return {
        "title": article.title,
        "text": article.text
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        articleData = fetch_article(url)
        print(json.dumps(articleData, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "No URL provided"}))
