import numpy as np
from numpy.linalg import norm

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (norm(a) * norm(b))