# AUTOGENERATED! DO NOT EDIT! File to edit: dev/17_repr.doc2vec.train.ipynb (unless otherwise specified).

__all__ = []

# Cell
# Imports
import numpy as np
import pandas as pd
import sentencepiece as sp

from pathlib import Path
from tokenizers import ByteLevelBPETokenizer
from tokenizers.processors import BertProcessing

from transformers import pipeline