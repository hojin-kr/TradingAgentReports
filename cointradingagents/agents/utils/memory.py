import chromadb
from chromadb.config import Settings


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.config = config
        if config.get("llm_provider", "").lower() == "ollama":
            try:
                import ollama
                base_url = config.get("ollama_base_url", "http://localhost:11434")
                self.client = ollama.Client(host=base_url)
                self.embedding = "nomic-embed-text"
                self.use_ollama = True
            except ImportError:
                raise ImportError(
                    "ollama package is required for Ollama support. "
                    "Please install it with: pip install ollama"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Ollama client: {str(e)}")
        else:
            from openai import OpenAI
            if config.get("backend_url", "") == "http://localhost:11434/v1":
                self.embedding = "nomic-embed-text"
            else:
                self.embedding = "text-embedding-3-small"
            self.client = OpenAI(base_url=config.get("backend_url", "https://api.openai.com/v1"))
            self.use_ollama = False
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """Get embedding for a text"""
        if self.use_ollama:
            # Ollama client uses embed() method (singular, not embeddings)
            import ollama
            try:
                # Ollama embed() method uses 'input' parameter, not 'prompt'
                response = self.client.embed(model=self.embedding, input=text)
                # Ollama returns EmbedResponse object with 'embeddings' (plural) attribute
                # Handle EmbedResponse object - embeddings is a list of lists
                if hasattr(response, 'embeddings'):
                    # embeddings is a list of lists, get the first list
                    if isinstance(response.embeddings, list) and len(response.embeddings) > 0:
                        return response.embeddings[0]
                    else:
                        return response.embeddings
                # Handle 'embedding' (singular) attribute for backward compatibility
                elif hasattr(response, 'embedding'):
                    embedding = response.embedding
                    # If it's a list of lists, get the first list
                    if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                        return embedding[0]
                    return embedding
                # Handle dict format
                elif isinstance(response, dict):
                    if 'embeddings' in response:
                        embeddings = response['embeddings']
                        if isinstance(embeddings, list) and len(embeddings) > 0:
                            return embeddings[0] if isinstance(embeddings[0], list) else embeddings
                        return embeddings
                    elif 'embedding' in response:
                        embedding = response['embedding']
                        if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                            return embedding[0]
                        return embedding
                # Handle list format
                elif isinstance(response, list):
                    if len(response) > 0:
                        # If list contains EmbedResponse objects, extract embeddings
                        if hasattr(response[0], 'embeddings'):
                            embeddings = response[0].embeddings
                            return embeddings[0] if isinstance(embeddings, list) and len(embeddings) > 0 else embeddings
                        elif hasattr(response[0], 'embedding'):
                            embedding = response[0].embedding
                            if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                                return embedding[0]
                            return embedding
                        else:
                            return response[0] if not isinstance(response[0], list) or len(response[0]) == 0 or not isinstance(response[0][0], list) else response[0][0]
                    else:
                        return []
                else:
                    return response
            except (AttributeError, ollama.ResponseError) as e:
                # Handle AttributeError (method doesn't exist) or ResponseError (model not found)
                if isinstance(e, ollama.ResponseError) and "not found" in str(e).lower():
                    # Model not found - try to pull the model first
                    try:
                        print(f"Warning: Embedding model '{self.embedding}' not found. Attempting to pull it...")
                        try:
                            self.client.pull(self.embedding)
                        except Exception as pull_init_error:
                            print(f"Warning: Failed to pull model '{self.embedding}': {str(pull_init_error)}")
                            raise pull_init_error
                        # Retry after pulling
                        response = self.client.embed(model=self.embedding, input=text)
                        # Handle EmbedResponse object - embeddings is a list of lists
                        if hasattr(response, 'embeddings'):
                            if isinstance(response.embeddings, list) and len(response.embeddings) > 0:
                                return response.embeddings[0]
                            else:
                                return response.embeddings
                        elif hasattr(response, 'embedding'):
                            embedding = response.embedding
                            if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                                return embedding[0]
                            return embedding
                        elif isinstance(response, dict):
                            if 'embeddings' in response:
                                embeddings = response['embeddings']
                                return embeddings[0] if isinstance(embeddings, list) and len(embeddings) > 0 else embeddings
                            elif 'embedding' in response:
                                embedding = response['embedding']
                                return embedding[0] if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list) else embedding
                        elif isinstance(response, list):
                            if len(response) > 0:
                                if hasattr(response[0], 'embeddings'):
                                    embeddings = response[0].embeddings
                                    return embeddings[0] if isinstance(embeddings, list) and len(embeddings) > 0 else embeddings
                                elif hasattr(response[0], 'embedding'):
                                    embedding = response[0].embedding
                                    return embedding[0] if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list) else embedding
                                else:
                                    return response[0] if not isinstance(response[0], list) or len(response[0]) == 0 or not isinstance(response[0][0], list) else response[0][0]
                            else:
                                return []
                        else:
                            return response
                    except Exception as pull_error:
                        # If pull fails, try embeddings() method
                        try:
                            response = self.client.embeddings(model=self.embedding, prompt=text)
                            # Handle EmbedResponse object - embeddings is a list of lists
                            if hasattr(response, 'embeddings'):
                                if isinstance(response.embeddings, list) and len(response.embeddings) > 0:
                                    return response.embeddings[0]
                                else:
                                    return response.embeddings
                            elif hasattr(response, 'embedding'):
                                embedding = response.embedding
                                if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                                    return embedding[0]
                                return embedding
                            elif isinstance(response, dict):
                                if 'embeddings' in response:
                                    embeddings = response['embeddings']
                                    return embeddings[0] if isinstance(embeddings, list) and len(embeddings) > 0 else embeddings
                                elif 'embedding' in response:
                                    embedding = response['embedding']
                                    return embedding[0] if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list) else embedding
                            elif isinstance(response, list):
                                if len(response) > 0:
                                    if hasattr(response[0], 'embeddings'):
                                        embeddings = response[0].embeddings
                                        return embeddings[0] if isinstance(embeddings, list) and len(embeddings) > 0 else embeddings
                                    elif hasattr(response[0], 'embedding'):
                                        embedding = response[0].embedding
                                        return embedding[0] if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list) else embedding
                                    else:
                                        return response[0] if not isinstance(response[0], list) or len(response[0]) == 0 or not isinstance(response[0][0], list) else response[0][0]
                                else:
                                    return []
                            else:
                                return response
                        except Exception:
                            # If all methods fail, return zero vector as fallback
                            print(f"Warning: Failed to get embedding model '{self.embedding}'. Error: {str(pull_error)}. Using zero vector as fallback.")
                            # Return a zero vector (typical embedding dimension is 768 for nomic-embed-text)
                            return [0.0] * 768
                else:
                    # Fallback to embeddings() if embed() doesn't exist
                    try:
                        response = self.client.embeddings(model=self.embedding, prompt=text)
                        # Handle EmbedResponse object - embeddings is a list of lists
                        if hasattr(response, 'embeddings'):
                            if isinstance(response.embeddings, list) and len(response.embeddings) > 0:
                                return response.embeddings[0]
                            else:
                                return response.embeddings
                        elif hasattr(response, 'embedding'):
                            embedding = response.embedding
                            if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                                return embedding[0]
                            return embedding
                        elif isinstance(response, dict):
                            if 'embeddings' in response:
                                embeddings = response['embeddings']
                                return embeddings[0] if isinstance(embeddings, list) and len(embeddings) > 0 else embeddings
                            elif 'embedding' in response:
                                embedding = response['embedding']
                                return embedding[0] if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list) else embedding
                        elif isinstance(response, list):
                            if len(response) > 0:
                                if hasattr(response[0], 'embeddings'):
                                    embeddings = response[0].embeddings
                                    return embeddings[0] if isinstance(embeddings, list) and len(embeddings) > 0 else embeddings
                                elif hasattr(response[0], 'embedding'):
                                    embedding = response[0].embedding
                                    return embedding[0] if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list) else embedding
                                else:
                                    return response[0] if not isinstance(response[0], list) or len(response[0]) == 0 or not isinstance(response[0][0], list) else response[0][0]
                            else:
                                return []
                        else:
                            return response
                    except Exception as e2:
                        # If all methods fail, return zero vector as fallback
                        print(f"Warning: Failed to get embedding from Ollama: {str(e2)}. Using zero vector as fallback.")
                        return [0.0] * 768
        else:
            response = self.client.embeddings.create(
                model=self.embedding, input=text
            )
            return response.data[0].embedding

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
