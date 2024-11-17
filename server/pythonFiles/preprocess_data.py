import pandas as pd
import torch
from torch_geometric.data import Data

# Load the graph data
nodes = pd.read_csv("nodes.csv")
edges = pd.read_csv("relationships.csv")

# Create a mapping for node IDs
node_mapping = {old_id: new_id for new_id, old_id in enumerate(nodes["id"])}

# Generate node features (dummy one-hot encoding for simplicity)
features = torch.eye(len(node_mapping))  # Identity matrix as features

# Create edge list
edge_index = torch.tensor([
    [node_mapping[src], node_mapping[dst]] for src, dst in zip(edges["source"], edges["target"])
]).t().contiguous()

# Create graph data object
data = Data(x=features, edge_index=edge_index)

# Save preprocessed data for GraphSAGE
torch.save(data, "graph_data.pt")
print("Graph data preprocessed and saved successfully")
