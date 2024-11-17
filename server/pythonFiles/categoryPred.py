import json
import sys
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from safetensors.torch import load_file
import torch

# Paths to your model and associated files
model_path = "../news-classification-model/model.safetensors"
tokenizer_path = "../news-classification-model"
config_path = "../news-classification-model"
special_tokens_path = "../news-classification-model/special_token_map.json"

# Load the Tokenizer
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

# Load Special Tokens (if applicable)
try:
    with open(special_tokens_path, "r") as f:
        special_tokens = json.load(f)
    tokenizer.add_special_tokens(special_tokens)
except FileNotFoundError:
    pass

# Load the Model
state_dict = load_file(model_path)
model = AutoModelForSequenceClassification.from_pretrained(
    config_path,
    state_dict=state_dict,
    torch_dtype=torch.float32
)
model.resize_token_embeddings(len(tokenizer))

# Preprocess Text
def preprocess_text(text, tokenizer, max_length=128):
    return tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )

# Predict Function
def predict(text, model, tokenizer, device="cpu"):
    inputs = preprocess_text(text, tokenizer)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    model = model.to(device)

    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class = torch.argmax(probabilities, dim=-1).item()

    return predicted_class, probabilities

def predict_category(input):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    predicted_class, probabilities = predict(input, model, tokenizer, device)

    print('predicted_class',predicted_class)
    with open(f"{config_path}/config.json", "r") as f:
        config = json.load(f)
    class_names = config.get("id2label", {})
    predicted_class_name = class_names.get(str(predicted_class), "Unknown")
    return predicted_class_name

# Main Script Logic
if __name__ == "__main__":
    # Specify device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Read input from stdin
    input_text = sys.stdin.read()

    # Run prediction
    predicted_class, probabilities = predict(input_text, model, tokenizer, device)

    # Load class names from config.json
    with open(f"{config_path}/config.json", "r") as f:
        config = json.load(f)
    class_names = config.get("id2label", {})

    # Get the predicted class name
    predicted_class_name = class_names.get(str(predicted_class), "Unknown")

    # Output the result as JSON
    result = {"category": predicted_class_name}
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()
