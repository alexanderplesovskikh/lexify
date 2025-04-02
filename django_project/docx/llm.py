"""
Author: Kirill Orlov
"""

'''
This file implements a TextClassifier class for Russian language text classification using pre-trained transformer models. Key features:

1. Model Management:
   - Supports two pre-trained Russian language models for sequence classification
   - Handles model initialization with automatic device placement
   - Includes 4-bit quantization for efficient inference

2. Core Functionality:
   - Wraps Hugging Face transformers for classification tasks
   - Provides sentence-level prediction capability
   - Returns probability distribution over classes

3. Technical Implementation:
   - Uses AutoTokenizer and AutoModelForSequenceClassification
   - Implements GPU acceleration with CUDA
   - Applies softmax to convert logits to probabilities
   - Includes model-specific configuration parameters

4. Usage:
   - Default model: 'iproskurina/tda-ruroberta-large-ru-cola'
   - Instantiated classifier is available as 'model' variable
   - predict_sentence() method returns class probabilities and top prediction

The class abstracts away model loading and inference details while providing a simple interface for text classification.
'''

import torch
from typing import Set, List, Iterator, Tuple
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BitsAndBytesConfig
)

class TextClassifier:
    avaliable_models: Set[str] = {
        'iproskurina/tda-ruroberta-large-ru-cola',
        'iproskurina/tda-rubert-ru-cola'
    }

    def _check_model(self, model: str):
        if model not in self.avaliable_models:
            raise Exception(f'Got unknown model "{model}".')

    def _collect_external_params(self, model: str):
        params = dict(
            quantization_config=BitsAndBytesConfig(load_in_4bit=True)
        )
        if model == 'iproskurina/tda-ruroberta-large-ru-cola':
            params['device_map'] = 'auto'
        return params

    def __init__(
        self,
        model: str = 'iproskurina/tda-ruroberta-large-ru-cola'
    ) -> None:
        self._check_model(model)
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model,
            low_cpu_mem_usage=True,
            torch_dtype='auto',
            **self._collect_external_params(model)
        )

    def predict_sentence(self, sent: str) -> str:
        inputs = {
            key: val.to(device='cuda')
            for key, val in self.tokenizer(sent, return_tensors='pt').items()
        }

        with torch.no_grad():
            logits = self.model(**inputs).logits.cpu()
        weights = torch.softmax(logits, 1)[0]
        classes = {
            self.model.config.id2label[pos]: weigth.item()
            for pos, weigth in enumerate(weights)
        }
        return classes, classes[max(classes)]
    
model = TextClassifier('iproskurina/tda-ruroberta-large-ru-cola')