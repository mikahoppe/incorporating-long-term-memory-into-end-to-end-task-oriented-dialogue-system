from transformers import AutoTokenizer, AutoModel
import torch


def get_embedding(text: str):
    model_name = "distilbert-base-uncased"  # You can choose any model that suits your needs
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt")

    # Generate embeddings
    with torch.no_grad():
        outputs = model(**inputs)

    # Get the embeddings from the last hidden state
    # Here, we use the mean of all token embeddings for simplicity.
    embeddings = outputs.last_hidden_state.mean(dim=1)

    return embeddings
