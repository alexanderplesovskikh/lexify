"""
Author: Kirill Orlov
"""

'''
This file implements a text analysis tool for detecting problematic linguistic patterns with the following features:

1. Core Functionality:
   - Checks text for excluded characters, sequences, and words
   - Identifies future tense verbs using pymorphy3 morphological analysis
   - Provides detailed error messages for found issues

2. Pattern Detection:
   - ExcludedSequence: Finds forbidden character sequences
   - ExcludedWord: Detects prohibited words with context awareness
   - Future verb detection through morphological parsing

3. Technical Implementation:
   - Uses dataclasses for pattern storage and state management
   - Configurable via JSON input (excluded patterns/rules)
   - Stateful processing of text character-by-character
   - Efficient tracking of multiple pattern types simultaneously

4. Output:
   - Boolean result indicating if errors were found
   - Detailed human-readable error message listing all detected issues
   - Clear separation between different error types (chars, sequences, words, verbs)

The class provides a comprehensive solution for automated text quality control with customizable rules.
'''

import json
from typing import List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

from pymorphy3 import MorphAnalyzer


@dataclass
class ExcludedSequence:
    text: str
    length: int = None
    state: int = 0

    def __post_init__(self):
        self.length = len(self.text)

    def process(self, ch: str):
        if self.text[self.state] == ch:
            self.state += 1
        else:
            self.state = 0 if ch != self.text[0] else 1

        if self.state == self.length:
            self.state = 0
            return self.text
        else:
            return


@dataclass
class ExcludedWord:
    word: str
    pref: Tuple[str] = (' ', '(', '[', '{', '–',)
    suff: Tuple[str] = (' ', ')', ']', '}', ',', ';', ':', '.', '!', '?',)
    cache: str = ''

    def process(self, ch: str):
        if ch in self.pref or ch in self.suff:
            check = self.word == self.cache
            self.cache = ''
            return self.word if check else None
        self.cache += ch


class RulesChecker:
    SKIP_CHARS = (' ', '-', ',', '.', ':',)
    def __init__(
        self,
        excluded_chars: str,
        excluded_sequences: List[ExcludedSequence],
        excluded_words: List[ExcludedWord]
    ):
        self.excluded_chars = excluded_chars
        self.excluded_sequences = excluded_sequences
        self.excluded_words = excluded_words

        self.warn_chars = set()
        self.warn_sequences = set()
        self.warn_words = set()
        self.futr_verbs = set()

        self.morph = MorphAnalyzer()
        self.track_word = ''

    @classmethod
    def from_json(cls, path: str):
        with open(path, 'r') as file:
            cfg_data = json.loads(file.read())
        return cls(
            excluded_chars=''.join([
                x.get('val')
                for x in cfg_data.get('excluded_chars')
            ]),
            excluded_sequences=[
                ExcludedSequence(x.get('val'))
                for x in cfg_data.get('excluded_sequences')
            ],
            excluded_words=[
                ExcludedWord(x.get('val'))
                for x in cfg_data.get('excluded_words')
            ]
        )

    @property
    def message(self):
        base = 'В тексте допущены следующие ошибки:'
        for char in self.warn_chars:
            base += f' - символ {char};'
        for seq in self.warn_sequences:
            base += f' - последовательность символов {seq};'
        for word in self.warn_words:
            base += f' - слово {word};'
        for word in self.futr_verbs:
            base += f' - глагол в будущем времени {word};'
        return base

    def _clear(self):
        self.warn_chars.clear()
        self.warn_sequences.clear()
        self.warn_words.clear()
        self.futr_verbs.clear()
        for excluded in self.excluded_sequences:
            excluded.state = 0
        for excluded in self.excluded_words:
            excluded.state = 0

    def _track_word(self, char: str):
        if char in self.SKIP_CHARS and len(self.track_word) == 0:
            return
        if char in self.SKIP_CHARS and len(self.track_word) > 0:
            pred = max(
                self.morph.parse(self.track_word),
                key=lambda x: x.score
            )
            is_futr_verb = (
                'VERB' in pred.tag
                and 'futr' in pred.tag
            )
            result, self.track_word = (
                self.track_word if is_futr_verb else None,
                ''
            )
            return result
        self.track_word += char
        return


    def grep_text(self, text: str) -> Tuple[int, str]:
        self._clear()
        for ind, char in enumerate(text):
            curr = char.lower()

            if curr in self.excluded_chars:
                self.warn_chars.add(curr)
            for seq in self.excluded_sequences:
                check = seq.process(curr)
                self.warn_sequences.add(check) if check else None
            for word in self.excluded_words:
                check = word.process(curr)
                self.warn_words.add(check) if check else None
            track = self._track_word(curr)
            self.futr_verbs.add(track) if track else None

        if (
            self.warn_chars
            or self.warn_sequences
            or self.warn_words
            or self.futr_verbs
        ):
            return True, self.message
        else:
            return False, 'Ошибок нет'