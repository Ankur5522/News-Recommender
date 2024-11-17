from py2neo import Graph
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv
from torch_geometric.loader import DataLoader

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "test_password"))

# Fetch User and Article data from Neo4j
def fetch_user_article_data():
    query = """
    MATCH (u:User)-[r:HAS_READ]->(a:Article)
    RETURN u.id AS user_id, a.url AS article_url, r.read AS has_read
    """
    results = graph.run(query)
    user_article_data = []
    for record in results:
        user_article_data.append({
            "user_id": record["user_id"],
            "article_url": record["article_url"],
            "has_read": record["has_read"]
        })
    return user_article_data

# Convert data into a graph format compatible with GraphSAGE
def prepare_data_for_graphsage(user_article_data):
    user_map = {}
    article_map = {}
    edges = []
    edge_attr = []
    
    # Map user_id and article_url to unique integers
    for idx, data in enumerate(user_article_data):
        if data["user_id"] not in user_map:
            user_map[data["user_id"]] = len(user_map)
        if data["article_url"] not in article_map:
            article_map[data["article_url"]] = len(article_map)
        
        edges.append((user_map[data["user_id"]], article_map[data["article_url"]]))
        edge_attr.append([data["has_read"]])  # This could represent interaction strength or binary read state
    
    # Convert edges to a 2D tensor (shape: [2, num_edges])
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    edge_attr = torch.tensor(edge_attr, dtype=torch.float)  # Assuming edge_attr contains numeric values
    
    return user_map, article_map, edge_index, edge_attr

# Define a GraphSAGE model
class GraphSAGE(torch.nn.Module):
    def __init__(self, num_features, hidden_channels, out_channels):
        super(GraphSAGE, self).__init__()
        self.conv1 = SAGEConv(num_features, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, out_channels)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return x

# Prepare graph data and train GraphSAGE
def train_graphsage(user_article_data):
    user_map, article_map, edge_index, edge_attr = prepare_data_for_graphsage(user_article_data)
    
    # Prepare features (example with random features, you can replace it with actual features)
    num_users = len(user_map)
    num_articles = len(article_map)
    num_nodes = num_users + num_articles
    features = torch.randn(num_nodes, 128)  # Replace 128 with the actual feature size

    data = Data(x=features, edge_index=edge_index, edge_attr=edge_attr)

    model = GraphSAGE(num_features=128, hidden_channels=64, out_channels=32)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    # Train GraphSAGE
    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        out = model(data)
        # Example of a loss function (to be adjusted based on the task)
        loss = F.mse_loss(out, features)  # Dummy loss function (you should use an appropriate one)
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch}, Loss: {loss.item()}")

    return model, user_map, article_map, data  # Return 'data' here

# Predict recommendations for a user
def recommend_for_user(user_id, model, user_map, article_map, user_article_data, data, top_n=5):
    user_node_id = user_map.get(user_id, None)
    if user_node_id is None:
        return []

    # Get the list of articles the user has already read
    read_articles = set([data["article_url"] for data in user_article_data if data["user_id"] == user_id and data["has_read"]])

    model.eval()
    with torch.no_grad():
        out = model(data)  # Get node embeddings
        
    # Get the embedding for the user
    user_embedding = out[user_node_id].unsqueeze(0)
    
    similarity_scores = []

    # Compute similarity between user embedding and all article embeddings
    for article_url, article_node_id in article_map.items():
        # Skip articles the user has already read
        if article_url in read_articles:
            continue
        
        article_embedding = out[article_node_id].unsqueeze(0)
        similarity = torch.cosine_similarity(user_embedding, article_embedding)
        similarity_scores.append((article_url, similarity.item()))
    
    # Sort articles by similarity score and return the top N recommendations
    recommended_articles = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[:top_n]
    return [article[0] for article in recommended_articles]

if __name__ == "__main__":
    # Fetch user-article data
    user_article_data = fetch_user_article_data()
    
    # Train the GraphSAGE model
    model, user_map, article_map, data = train_graphsage(user_article_data)
    
    # Recommend articles for a specific user
    user_id = "some_user_id"  # Replace with the actual user_id
    recommended_articles = recommend_for_user(user_id, model, user_map, article_map, user_article_data, data)
    print(f"Recommended articles for {user_id}: {recommended_articles}")
