from neo4j import GraphDatabase
import sys
import json

# Neo4j connection setup
URI = "bolt://localhost:7687"  # Update if different
USERNAME = "neo4j"
PASSWORD = "test_password"

class GraphCreator:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def create_graph(self, data):
        with self.driver.session() as session:
            for article in data:
                # Create article node
                session.run(
                    """
                    MERGE (a:Article {url: $url})
                    SET a.category = $category, a.createdAt = $createdAt
                    """, 
                    url=article["url"], 
                    category=article["category"], 
                    createdAt=article["createdAt"]
                )

                # Create or merge category node
                session.run(
                    """
                    MERGE (c:Category {name: $category})
                    """, 
                    category=article["category"]
                )

                # Create relationship between article and category
                session.run(
                    """
                    MATCH (a:Article {url: $url})
                    MATCH (c:Category {name: $category})
                    MERGE (a)-[:BELONGS_TO]->(c)
                    """, 
                    url=article["url"], 
                    category=article["category"]
                )

                # Create user -> article relationship
                session.run(
                    """
                    MATCH (a:Article {url: $url})
                    MERGE (u:User {id: $userId})
                    MERGE (u)-[r:READ]->(a)
                    SET r.timeSpent = $timeSpent
                    """, 
                    userId="user789", 
                    url=article["url"], 
                    timeSpent=article["timeSpent"]
                )

                # Create tags and article -> tag relationships
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

    def normalize_read_weights(self):
        """
        Normalize the timeSpent weights for the READ relationships dynamically.
        """
        with self.driver.session() as session:
            # Step 1: Fetch the maximum timeSpent value
            result = session.run(
                """
                MATCH (:User)-[r:READ]->(:Article)
                RETURN max(r.timeSpent) AS maxTimeSpent
                """
            )
            max_time_spent = result.single()["maxTimeSpent"]

            if max_time_spent and max_time_spent > 0:
                # Step 2: Normalize all timeSpent weights
                session.run(
                    """
                    MATCH (:User)-[r:READ]->(:Article)
                    SET r.timeSpent = r.timeSpent / $maxTimeSpent
                    """, 
                    maxTimeSpent=max_time_spent
                )
                print(f"Normalization completed. Max timeSpent was: {max_time_spent}")
            else:
                print("Normalization skipped. No valid timeSpent values found.")

if __name__ == "__main__":
    # Read JSON data from stdin
    input_data = json.loads(sys.stdin.read())
    graph_creator = GraphCreator(URI, USERNAME, PASSWORD)
    try:
        # Step 1: Create the graph
        graph_creator.create_graph(input_data)
        print("Graph created successfully")

        # Step 2: Normalize the timeSpent weights
        graph_creator.normalize_read_weights()
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        graph_creator.close()
