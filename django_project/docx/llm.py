"""
Author: Kirill Orlov
"""

'''from transformers import AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig, pipeline
import torch

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

def load_model_1():

    # Load the model in 4-bit precision
    model_4bit = AutoModelForSequenceClassification.from_pretrained(
        "iproskurina/tda-ruroberta-large-ru-cola",
        quantization_config=quantization_config,
        device_map="auto"  # Automatically map model to available devices (e.g., GPU if available)
    )

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("iproskurina/tda-ruroberta-large-ru-cola")

    # Create a pipeline for text classification
    pipe = pipeline("text-classification", model=model_4bit, tokenizer=tokenizer)

    return pipe

print(torch.cuda.is_available())

#version 2
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
            logits = self.model(**inputs).logits
        predicted_class_id = logits.argmax().item()
        return self.model.config.id2label[predicted_class_id]
    
model = TextClassifier('iproskurina/tda-ruroberta-large-ru-cola')'''

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