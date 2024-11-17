from neo4j import GraphDatabase
import pandas as pd

# Neo4j connection setup
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "test_password"

class Neo4jExporter:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def export_graph(self):
        with self.driver.session() as session:
            nodes = session.run("MATCH (n) RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties")
            relationships = session.run("MATCH (n)-[r]->(m) RETURN id(n) AS source, id(m) AS target, type(r) AS type")

            # Convert results to DataFrames
            nodes_df = pd.DataFrame([dict(record) for record in nodes])
            relationships_df = pd.DataFrame([dict(record) for record in relationships])
            return nodes_df, relationships_df

if __name__ == "__main__":
    exporter = Neo4jExporter(URI, USERNAME, PASSWORD)
    nodes_df, relationships_df = exporter.export_graph()
    exporter.close()

    # Save to CSV
    nodes_df.to_csv("nodes.csv", index=False)
    relationships_df.to_csv("relationships.csv", index=False)
    print("Graph exported successfully")
