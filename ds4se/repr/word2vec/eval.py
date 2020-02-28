# AUTOGENERATED! DO NOT EDIT! File to edit: dev/19_repr.word2vec.eval.ipynb (unless otherwise specified).

__all__ = ['Vectorizor', 'BertVectorizor']

# Cell
# Imports
import numpy as np

from abc import ABC, abstractmethod

from pathlib import Path

from transformers import pipeline

# Cell
class Vectorizor(ABC):

    def __init__(self, vectorizor):
        self.vectorizor = vectorizor
        super().__init__()

    @abstractmethod
    def vectorize(self, inpt):
        pass

# Cell
class BertVectorizor(Vectorizor):
    """
        Vectorization subclass that handles vectorizing using BERT
    """
    def vectorize(self, inpt):
        return np.array(self.vectorizor("public static void main"))