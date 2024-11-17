import pandas as pd
from neo4j import GraphDatabase
from newspaper import Article
import json
from textProcessor import process_text
from categoryPred import predict_category

# Neo4j connection setup
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "test_password"

class NewsGraphUpdater:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def fetch_news(self, urls):
        """
        Fetch news articles using newspaper3k.
        """
        articles = []
        for url in urls[:100]:  # Limit to the first 100 articles
            try:
                article = Article(url)
                article.download()
                article.parse()
                articles.append({
                    "url": url,
                    "title": article.title,
                    "content": article.text,
                    "publish_date": article.publish_date.isoformat() if article.publish_date else None
                })
            except Exception as e:
                print(f"Failed to fetch article from {url}: {e}")
        return articles

    def process_article(self, article):
        """
        Extract tags and predict categories using external scripts.
        """
        try:
            # Use textProcessor.py to extract tags
            
            tags_result = json.loads(process_text(article["content"]))
            tags = tags_result.get("tags", [])

            # Use categoryPred.py to predict category
            category = predict_category(article["content"])

            print('category:', category)

            return {"tags": tags, "category": category}

        except Exception as e:
            print(f"Error processing article {article['url']}: {e}")
            return {"tags": [], "category": None}

    def add_to_graph(self, articles):
        """
        Add articles, tags, and categories to the Neo4j graph.
        """
        with self.driver.session() as session:
            for article in articles:
                # Ensure the article node is merged based on its URL

                session.run(
                    """
                    MERGE (a:Article {url: $url})
                    SET a.category = $category
                    """, 
                    url=article["url"], 
                    category=article["category"],
                )

                # Add category and relationship
                session.run(
                    """
                    MERGE (c:Category {name: $category})
                    """, 
                    category=article["category"]
                )

                session.run(
                    """
                    MATCH (a:Article {url: $url})
                    MATCH (c:Category {name: $category})
                    MERGE (a)-[:BELONGS_TO]->(c)
                    """, 
                    url=article["url"], 
                    category=article["category"]
                )

                # Add tags and relationships (ensure tags are attached to the existing article node)
                for tag in article["tags"]:
                    session.run(
                        """
                        MATCH (a:Article {url: $url})
                        MERGE (t:Tag {name: $tagName})
                        MERGE (a)-[r:HAS_TAG]->(t)
                        SET r.weight = $weight
                        """, 
                        url=article["url"], 
                        tagName=tag["tag"], 
                        weight=tag["weight"]
                    )

                print(f"Added tags and category for article {article['url']}.")

if __name__ == "__main__":
    # Step 1: Read URLs from the Excel file
    try:
        df = pd.read_excel("news_articles.xlsx")  # Replace with your actual file path
        urls = df["url"].dropna().tolist()  # Extract non-null URLs
        print(f"Loaded {len(urls)} URLs from the Excel file.")
    except Exception as e:
        print(f"Failed to read Excel file: {e}")
        exit(1)

    graph_updater = NewsGraphUpdater(URI, USERNAME, PASSWORD)

    try:
        # Step 2: Fetch up to 100 articles from URLs
        fetched_articles = graph_updater.fetch_news(urls)
        print(f"Fetched {len(fetched_articles)} articles.")

        # Step 3: Process each article for tags and categories
        processed_articles = []
        for article in fetched_articles:
            processed_data = graph_updater.process_article(article)
            if processed_data["tags"] and processed_data["category"]:
                article.update(processed_data)
                processed_articles.append(article)

        # Step 4: Add processed articles to the Neo4j graph
        graph_updater.add_to_graph(processed_articles)
        print("Graph updated with new articles.")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        graph_updater.close()
