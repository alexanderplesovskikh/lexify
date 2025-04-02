"""
Author: Max Khomin
"""

'''
This file contains HTML text processing utilities for the Lexify application, with three main functions for finding sentences in HTML content while preserving their original formatting with HTML tags:

1. find_sentence_in_html():
   - Finds a single sentence in HTML while maintaining original tags and whitespace
   - Returns a list containing the matched sentence with its HTML markup

2. find_sentences_in_html2():
   - Generator version that processes multiple sentences sequentially
   - Yields each found sentence with its HTML markup one at a time
   - More memory efficient for large documents

3. find_sentences_in_html3():
   - Most advanced version that processes multiple sentences simultaneously
   - Returns a dictionary mapping original sentences to their HTML-preserved versions
   - Uses regex for more robust whitespace handling
   - Removes found sentences from search set to avoid duplicates

Key features:
- Preserves HTML tags and whitespace while matching text content
- Handles cases where sentences are split by HTML tags
- Multiple implementations for different use cases
- Memory-efficient generator pattern available
'''

from re import sub, match

def find_sentence_in_html(html_content, sentence):
    '''
    Функция принимает на вход прочитанные данные html-файла (html_content) и строку sentence.
    Возвращает список строк, в котором каждая строка содержит sentence и
    html-тэги, которые в html файле находятся внутри строки sentence.
    '''

    # Удаляем все пробельные символы из искомого предложения
    sentence = sub(r'\s+', '', sentence)

    output_sentences = []
    sentence_length = len(sentence)

    i = 0
    while i < len(html_content):
       
        # Если текущий символ совпадает с первым символом искомого предложения
        if html_content[i] == sentence[0]:
            start_index = i
            sentence_to_output = []  # Сброс предыдущего результата
            sentence_index = 0  # Индекс в искомом предложении

            # Пробуем собрать предложение, включая теги
            while i < len(html_content) and sentence_index < sentence_length:
                if html_content[i] == sentence[sentence_index]:
                    sentence_to_output.append(html_content[i])  # Собираем предложение
                    sentence_index += 1  # Переход к следующему символу предложения
                elif match(r'\s+', html_content[i]):
                    sentence_to_output.append(html_content[i])
                elif html_content[i] == '<':  # Обработка HTML-тега
                    while i < len(html_content) and html_content[i] != '>':
                        sentence_to_output.append(html_content[i])  # Собираем тег
                        i += 1
                    if i < len(html_content):
                        sentence_to_output.append('>')  # Закрывающий тег
                else:
                    break  # Совпадение прервалось, выходим из цикла

                i += 1  # Переходим к следующему символу

            # Если совпали все символы предложения
            if sentence_index == sentence_length:
                output_sentences.append(''.join(sentence_to_output))
                #print(output_sentences)
                return output_sentences

            # Сброс состояния, если не нашли полное совпадение
            i = start_index + 1  # Продолжаем с символа после начала предложения
        else:
            i += 1  # Переходим к следующему символу

    #if output_sentences:
        #return output_sentences
    else:
        return "Предложение не найдено"
    

def find_sentences_in_html2(html_content, sentences):
    '''
    Функция принимает на вход прочитанные данные html-файла (html_content) и массив строк sentences.
    Возвращает генератор, который поочередно передает строки из sentence вместе с html-тэгами и пробельными символами
    в том виде, в котором они представлены в html-файле.
    '''

    # Удаляем все пробельные символы из первого искомого предложения
    sentence_to_find = 0
    sentence = sub(r'\s+', '', sentences[sentence_to_find])
    sentence_length = len(sentence)

    i = 0
    while i < len(html_content):

        # Если текущий символ совпадает с первым символом искомого предложения
        if html_content[i] == sentence[0]:
            start_index = i
            sentence_to_output = ''  # Сброс предыдущего результата
            sentence_index = 0  # Индекс в искомом предложении

            # Пробуем собрать предложение, включая теги
            while i < len(html_content) and sentence_index < sentence_length:
                if html_content[i] == sentence[sentence_index]:
                    sentence_to_output += html_content[i]  # Собираем предложение
                    sentence_index += 1  # Переход к следующему символу предложения
                elif match(r'\s+', html_content[i]):
                    sentence_to_output += html_content[i]
                elif html_content[i] == '<':  # Обработка HTML-тега
                    while i < len(html_content) and html_content[i] != '>':
                        sentence_to_output += html_content[i]  # Собираем тег
                        i += 1
                    if i < len(html_content):
                        sentence_to_output += '>'  # Закрывающий тег
                else:
                    break  # Совпадение прервалось, выходим из цикла

                i += 1  # Переходим к следующему символу

            # Если совпали все символы предложения
            if sentence_index == sentence_length:
                yield sentence_to_output  # Возвращаем результат поиска
                sentence_to_find += 1
                if sentence_to_find < len(sentences):
                    sentence = sub(r'\s+', '', sentences[sentence_to_find])
                    sentence_length = len(sentence)
                else:
                    return 'Все предложения найдены'

            # Сброс состояния, если не нашли полное совпадение
            i = start_index + 1  # Продолжаем с символа после начала предложения
        else:
            i += 1  # Переходим к следующему символу

    return 'Поиск завершен'

import re

def find_sentences_in_html3(html_content, sentences):
    '''
    Функция принимает на вход прочитанные данные html-файла (html_content) и список строк sentences.
    Возвращает словарь, в котором ключи — строки из sentences, а значения — списки строк, содержащих 
    соответствующее предложение и HTML-теги.
    '''
    
    # Создаем набор предложений для быстрого поиска
    sentence_set = {re.sub(r'\s+', '', sentence): sentence for sentence in sentences}
    output_sentences = {sentence: [] for sentence in sentences}
    
    # Проходим по HTML-контенту
    i = 0
    while i < len(html_content):
        # Проверяем, есть ли текущий символ в начале какого-либо предложения
        for sentence_key in list(sentence_set.keys()):
            # Проверяем, что ключ не пустой
            if sentence_key and html_content[i] == sentence_key[0]:
                start_index = i
                sentence_to_output = []  # Сброс предыдущего результата
                sentence_index = 0  # Индекс в искомом предложении

                # Пробуем собрать предложение, включая теги
                while i < len(html_content) and sentence_index < len(sentence_key):
                    if html_content[i] == sentence_key[sentence_index]:
                        sentence_to_output.append(html_content[i])  # Собираем предложение
                        sentence_index += 1  # Переход к следующему символу предложения
                    elif re.match(r'\s+', html_content[i]):
                        sentence_to_output.append(html_content[i])
                    elif html_content[i] == '<':  # Обработка HTML-тега
                        while i < len(html_content) and html_content[i] != '>':
                            sentence_to_output.append(html_content[i])  # Собираем тег
                            i += 1
                        if i < len(html_content):
                            sentence_to_output.append('>')  # Закрывающий тег
                    else:
                        break  # Совпадение прервалось, выходим из цикла

                    i += 1  # Переходим к следующему символу

                # Если совпали все символы предложения
                if sentence_index == len(sentence_key):
                    output_sentences[sentence_set[sentence_key]].append(''.join(sentence_to_output))
                    # Удаляем предложение из набора, чтобы избежать повторного поиска
                    del sentence_set[sentence_key]

                # Сброс состояния, если не нашли полное совпадение
                i = start_index + 1  # Продолжаем с символа после начала предложения
                break  # Выходим из цикла по предложениям, чтобы начать с нового символа
        else:
            i += 1  # Переходим к следующему символу

    return output_sentences if any(output_sentences.values()) else "Предложения не найдены"



# Get PDF file
import os
import datetime as dt
import io
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib import use
use('agg')