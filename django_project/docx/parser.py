"""
Author: Alexander Plesovskikh
"""

'''
This file implements a text processing pipeline for document analysis with HTML parsing and sentence tokenization capabilities. Key components:

1. HTML Processing:
   - Uses BeautifulSoup to parse and clean HTML content
   - Splits document into main text and references sections
   - Handles special cases like tables, footnotes and formatting tags

2. Text Segmentation:
   - Identifies reference sections using predefined keywords
   - Tokenizes text into paragraphs and sentences
   - Merges incorrectly split sentences based on punctuation rules

3. Text Cleaning:
   - Removes URLs and excessive whitespace
   - Filters out short non-meaningful text fragments
   - Normalizes text for further processing

4. Key Features:
   - NLTK-based sentence tokenization with Russian support
   - Smart handling of nested structures (brackets, quotes)
   - Special processing for list items and reference sections
   - Configurable tag filtering (exclude_tags, ref_tags)

The pipeline takes HTML input and produces cleaned, segmented text ready for linguistic analysis and reference processing.
'''

#imports
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
from re import sub

#downloads
from nltk import download
download('punkt_tab')

#Parser global vars
ref_keyword_list = set(['списокиспользованныхисточников', 
                    'списокиспользуемыхисточников', 
                    'списокисточников', 
                    'списоклитературы', 
                    'публикации',
                    'references',
                    'списоклитетатуры',
                    'списокиспользуемойлитературы',
                    'cписокиспользованныхисточников',
                    'ссылкиналитературу'])

exclude_tags = {'img', 'table', 'thead', 'tr', 'th', 'em', 'strong', 's', 'ul', 'ol', 'a', 'font', 'b', 'i', 'span', 'div', 'li'}

ref_tags = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


def get_only_alphas(input_str):
    return ''.join([char for char in input_str if char.isalpha()])


def get_html_string(file_name):
    with open(file_name, 'r', encoding="utf-8") as f:
        return f.read()
    

def get_bs4_repr(html_string):
    return BeautifulSoup(html_string, 'html.parser')
    
    
def text_references_split(soup_object):
    soup_object_body = soup_object.find('body') #returns body tag as well
    if not soup_object_body:
        return [], []
    
    for tag_name in ['table', 'div']:
        if tag_name == 'table':
            for tag in soup_object_body.find_all(tag_name):
                tag.decompose()
        if tag_name == 'div':
            for tag in soup_object_body.find_all(tag_name, {'title': ['footers', 'footer']}):
                tag.decompose()

    for footnote in soup_object_body.find_all('div', id='sdfootnote1'):
        footnote.decompose()
    
    
    tag_name, tag_text = [], []

    
    for tag in soup_object_body.find_all():
        if tag.name not in exclude_tags:
            for child in tag.findChildren():
                if child.name == 'br':
                    child.replace_with(' ')
            tag_name.append(tag.name)
            tag_text.append(tag.text)

    count_possible_refs = []

    for index, el in reversed(list(enumerate(tag_text))):
        if get_only_alphas(tag_text[index].lower()) in ref_keyword_list:
            count_possible_refs.append(index)
            break
               
    texts, refs = [], []

    is_ref_start = False

    for para_id in range(len(tag_text)):

        if len(count_possible_refs)>0:
            if para_id == count_possible_refs[0]:
                is_ref_start = True
                texts.append(tag_text[para_id])
                continue
            if para_id > count_possible_refs[0] and tag_name[para_id] in ref_tags:
                is_ref_start = False

        if tag_name[para_id] == 'li':
            text_to_append = " " + tag_text[para_id] + " "
        else:
            text_to_append = tag_text[para_id]
        
        if is_ref_start:
            refs.append(text_to_append.strip())
        else:
            texts.append(text_to_append)

    return texts, refs

def sents_tokenizer_split(texts, text_id):
    return sent_tokenize(texts[text_id])

def get_sents_per_para(texts):
    sents_tokenized_per_para = []
    for text_id in range(len(texts)):
        sents = sents_tokenizer_split(texts, text_id)
        for sent in sents:
            sents_tokenized_per_para.append(sent)
    return sents_tokenized_per_para

def merge_raw_sents(sent_text_list):
    split_merged_sents = []
    len_of_tokenized_sents = len(sent_text_list)
    skip_next_sent = 0
    
    for i in range(len_of_tokenized_sents):
    
        curr_text = sent_text_list[i]
        
        if skip_next_sent > 0:
            skip_next_sent = skip_next_sent - 1
            continue
    
        for next_sent_id in range(len_of_tokenized_sents-i-1):

            current_sent_repr = sent_text_list[i+next_sent_id]
            next_sent_repr = sent_text_list[i+1+next_sent_id]
    
            if (current_sent_repr.strip()[-1] in [".", "!", "?"] and next_sent_repr.strip()[0].islower()==True) or (current_sent_repr.strip()[-1] in [".", "!", "?"] and next_sent_repr.strip()[0] in [";", ":", "{", "}", "(", ")", "/"]) or ("(" in current_sent_repr and ")" not in current_sent_repr and ")" in next_sent_repr) or ("[" in current_sent_repr and "]" not in current_sent_repr and "]" in next_sent_repr) or ("{" in current_sent_repr and "}" not in next_sent_repr and "}" in next_sent_repr):
                skip_next_sent += 1
                if next_sent_repr.strip()[0] in [";", ":", ")"]:
                    curr_text = curr_text + "" + next_sent_repr                
                else:
                    curr_text = curr_text + " " + next_sent_repr
    
            else:
                split_merged_sents.append(curr_text.strip())
                break
            
    return split_merged_sents

def clean_urls(string):
    return sub(r'https?://\S+', '', string)

def clean_whitespaces(string):
    return sub(r'\s+', ' ', string)

def get_clean_sentences(string):
    return clean_whitespaces((clean_urls(string)).strip())

def form_list_of_clean_sents(array):
    return [get_clean_sentences(element) if len(get_clean_sentences(element)) > 10 else '<#excluded#>' for element in array]