"""
Author: Tatyana Romanova
"""

'''
from regex import fullmatch
import re

eng_journal = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))))(?P<name>[\w :;,?!-–+=«»\._’\"\'—]+)( // (?P<container>((([\w :;,?!-–+=«»\._’\"\'—]+\. )[\w :;,?!-–+=«»\._’\"\']+, )|([\w :;,?!-–+=«»\._’\"\'—]+?\. ))))((?P<year>\d{4})\. )((?:(?P<VolNo>Vol\. [\w ()–-]+, (No. [\w ()–-]+))\. |(?P<Vol>Vol\. [\w ()–-]+)\. |(?P<No>No. [\w ()–-]+)\. |))((?P<pages>(?:(P\. [\w –-]+)|)))\.'
rus_journal = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))))(?P<name>[\w :;,?!-–+=«»\._’—]+)( // (?P<container>([\w :;,?!-–+=«»\._’—]+?\. )))((?P<year>(([\w :;,?!-–+=«»\._’—]+, )?\d{4}))\. )((?:(?P<ТомNo>Т\. \d+([–-]?\d+)?, (№ \d+([–-]?\d+)?))\. |(?P<Vol>Т\. \d+([–-]?\d+)?)\. |(?P<No>№ \d+([–-]?\d+)?)\. |))((?P<pages>(?:(С\. \d+([–-]?(?:(\d+|es)))?)|)))\.'
eng_book = r'(?P<author>((([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. )|((([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.)))))(?P<name>[\w :;,?!-–+=«»\._’\"\'—]+\. )((?P<year>(([\w :;,?!-–+=«»\._’—]+, )?\d{4}))\. )(?:(?P<Vol>Vol\. [\w ()–-]+)\. |)(?P<pages>(?:(P\. [\w –-]+|\d+ p)))\.'
rus_book = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))))(?P<name>[\w :;,?!-–+=«»\._’—]+\. )((?P<year>(([\w :;,?!-–+=«»\._’—]+, )?\d{4}))\. )(?:(?P<Tom>Т\. [\w ()–-]+)\. |)(?P<pages>(?:(С\. \d+(–\d+)?)|\d+ с))\.'
url = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))|))(?P<name>[\w :;,?!-–+=«»\._’\"\'—]+) \[Electronic resource]\. ((?P<year>\d{4})\. )?URL: (?P<URL>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))( \(accessed: (?P<acc_date>\d\d\.\d\d\.\d\d\d\d)\))?\.'

patterns = [
            [eng_journal, 'Статья из журнала (англ.)'],
            [rus_journal, 'Статья из журнала (рус.)'],
            [eng_book, 'Книга (англ.)'],
            [rus_book, 'Книга (рус.)'],
            [url, 'Электронный ресурс']
            ]

def split_volno(match, dictionary):
    if 'VolNo' in dictionary.keys() and match.group('VolNo') != None:
      m = re.match(r'(?P<Vol>Vol\. [\w ()–-]+), (?P<No>No. [\w ()–-]+)', match.group('VolNo').strip())
      dictionary['Vol'] = m.group('Vol').strip()
      dictionary['No'] = m.group('No').strip()
      dictionary['VolNo'] = None

def split_tomno(match, dictionary):
    if 'TomNo' in dictionary.keys() and match.group('TomNo') != None:
      m = re.match(r'(?P<Vol>Т\. [\w ()–-]+), (?P<No>№ [\w ()–-]+)', match.group('TomNo').strip())
      dictionary['Vol'] = m.group('Vol').strip()
      dictionary['No'] = m.group('No').strip()
      dictionary['TomNo'] = None

def split_container(match, dictionary):
    if 'container' in dictionary.keys() and match.group('container') != None and re.match(r'([\w :;,?!-–+=«»\._’\"\']+\.) ([\w :;,?!-–+=«»_’\"\']+),', match.group('container').strip()) != None:
      m = re.match(r'(?P<container>[\w :;,?!-–+=«»\._’\"\']+\.) (?P<publisher>[\w :;,?!-–+=«»_’\"\']+),', match.group('container').strip())
      dictionary['container'] = m.group('container').strip()
      dictionary['publisher'] = m.group('publisher').strip()

def split_year(match, dictionary):
    if 'year' in dictionary.keys() and match.group('year') != None and re.match(r'([\w :;,?!-–+=«»_’\"\']+), (\d{4})', match.group('year').strip()) != None:
      m = re.match(r'(?P<publisher>[\w :;,?!-–+=«»_’\"\']+), (?P<year>\d{4})', match.group('year').strip())
      dictionary['publisher'] = m.group('publisher').strip()
      dictionary['year'] = m.group('year').strip()

def split_groups(match):
    dictionary = match.groupdict()
    split_volno(match, dictionary)
    split_tomno(match, dictionary)
    split_container(match, dictionary)
    split_year(match, dictionary)
    filtered = {k: v for k, v in dictionary.items() if (v is not None) and (v != '')}
    return filtered

def check_patterns(input_string):
    result = {}
    for pattern, description in patterns:
        match = fullmatch(pattern, input_string.strip())
        if match:
            filtered = split_groups(match)
            result[description] = filtered
            return result
    return result

def remove_prefix(s):
    # Regular expression to match 1 or 3 digits followed by a dot at the beginning of the string and a space (optional)
    return re.sub(r'^\d{1,3}\.\s*', '', s)

def remove_line_breaks(s):
    return s.replace('\n', ' ')
'''

from crossref.restful import Works
from habanero import Crossref
import crossref
from doi2bib.crossref import get_bib_from_doi
import re
import regex
import bibtexparser
from citeproc.source.bibtex import BibTeX
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem
from citeproc import formatter
from io import StringIO

eng_journal = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))))(?P<name>[\w :;,?!-–+=«»\._’\"\'—]+)( // (?P<container>((([\w :;,?!-–+=«»\._’\"\'—]+\. )[\w :;,?!-–+=«»\._’\"\']+, )|([\w :;,?!-–+=«»\._’\"\'—]+?\. ))))((?P<year>\d{4})\. )((?:(?P<VolNo>Vol\. [\w ()–-]+, (No. [\w ()–-]+))\. |(?P<Vol>Vol\. [\w ()–-]+)\. |(?P<No>No. [\w ()–-]+)\. |))((?P<pages>(?:(P\. [\w –-]+)|)))\.'

rus_journal = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))))(?P<name>[\w :;,?!-–+=«»\._’—]+)( // (?P<container>([\w :;,?!-–+=«»\._’—]+?\. )))((?P<year>(([\w :;,?!-–+=«»\._’—]+, )?\d{4}))\. )((?:(?P<ТомNo>Т\. \d+([–-]?\d+)?, (№ \d+([–-]?\d+)?))\. |(?P<Vol>Т\. \d+([–-]?\d+)?)\. |(?P<No>№ \d+([–-]?\d+)?)\. |))((?P<pages>(?:(С\. \d+([–-]?(?:(\d+|es)))?)|)))\.'

eng_book = r'(?P<author>((([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. )|((([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.)))))(?P<name>[\w :;,?!-–+=«»\._’\"\'—]+\. )((?P<year>(([\w :;,?!-–+=«»\._’—]+, )?\d{4}))\. )(?:(?P<Vol>Vol\. [\w ()–-]+)\. |)(?P<pages>(?:(P\. [\w –-]+|\d+ p)))\.'

rus_book = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))))(?P<name>[\w :;,?!-–+=«»\._’—]+\. )((?P<year>(([\w :;,?!-–+=«»\._’—]+, )?\d{4}))\. )(?:(?P<Tom>Т\. [\w ()–-]+)\. |)(?P<pages>(?:(С\. \d+(–\d+)?)|\d+ с))\.'

url = r'(?P<author>(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})? ?et al\. |(([\p{Lu}][\p{Ll}]+[- ]?){1,}(([\p{Lu}]\.-?){0,})?, ){0,2}(([\p{Lu}][\p{Ll}]+[- \.]?){1,}(([\p{Lu}]\.-?){1,}|\.))|))(?P<name>[\w :;,?!-–+=«»\._’\"\'—]+) \[Electronic resource]\. ((?P<year>\d{4})\. )?URL: (?P<URL>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))( \(accessed: (?P<acc_date>\d\d\.\d\d\.\d\d\d\d)\))?\.'

patterns = [
            [eng_journal, 'Статья из журнала'],
            [rus_journal, 'Статья из журнала'],
            [eng_book, 'Книга'],
            [rus_book, 'Книга'],
            [url, 'Электронный ресурс']
            ]

def check_patterns(input_string):
    result = {}
    for pattern, description in patterns:
        match = regex.fullmatch(pattern, input_string.strip())
        if match:
            filtered = split_groups(match)
            result[description] = filtered
            return result
    return result

import re

def remove_prefix(s):
    # Regular expression to match 1 or 3 digits followed by a dot at the beginning of the string and a space (optional)
    return re.sub(r'^\d{1,3}\.\s*', '', s)

def remove_line_breaks(s):
    return s.replace('\n', ' ')

def split_volno(match, dictionary):
    if 'VolNo' in dictionary.keys() and match.group('VolNo') != None:
        m = re.match(r'(?P<Vol>Vol\. [\w ()–-]+), (?P<No>No. [\w ()–-]+)', match.group('VolNo').strip())
        dictionary['Vol'] = m.group('Vol').strip()
        dictionary['No'] = m.group('No').strip()
        dictionary['VolNo'] = None

def split_tomno(match, dictionary):
    if 'TomNo' in dictionary.keys() and match.group('TomNo') != None:
        m = re.match(r'(?P<Vol>Т\. [\w ()–-]+), (?P<No>№ [\w ()–-]+)', match.group('TomNo').strip())
        dictionary['Vol'] = m.group('Vol').strip()
        dictionary['No'] = m.group('No').strip()
        dictionary['TomNo'] = None

def split_container(match, dictionary):
    if 'container' in dictionary.keys() and match.group('container') != None and re.match(r'([\w :;,?!-–+=«»\._’\"\']+\.) ([\w :;,?!-–+=«»_’\"\']+),', match.group('container').strip()) != None:
      m = re.match(r'(?P<container>[\w :;,?!-–+=«»\._’\"\']+\.) (?P<publisher>[\w :;,?!-–+=«»_’\"\']+),', match.group('container').strip())
      dictionary['container'] = m.group('container').strip()
      dictionary['publisher'] = m.group('publisher').strip()

def split_year(match, dictionary):
    if 'year' in dictionary.keys() and match.group('year') != None and re.match(r'([\w :;,?!-–+=«»_’\"\']+), (\d{4})', match.group('year').strip()) != None:
        m = re.match(r'(?P<publisher>[\w :;,?!-–+=«»_’\"\']+), (?P<year>\d{4})', match.group('year').strip())
        dictionary['publisher'] = m.group('publisher').strip()
        dictionary['year'] = m.group('year').strip()

def split_groups(match):
    dictionary = match.groupdict()
    split_volno(match, dictionary)
    split_tomno(match, dictionary)
    split_container(match, dictionary)
    split_year(match, dictionary)
    filtered = {k: v for k, v in dictionary.items() if (v is not None) and (v != '')}
    return filtered


'''
# глобальные переменные

cr = Crossref()
works = Works()

# путь на папку со стилями
path = 'docx/static/csl/'

# словарик доступных стилей
# необходимо указать название файлика со стилем
csl = {
    'APA 7th': 'apa-numeric-superscript-brackets.csl',
    'APA 6th': 'apa-old-doi-prefix.csl',
    'ГОСТ': 'gost-r-7-0-5-2008-numeric.csl',
  }

examples = {
    'APA 7th': [
        ['Статья', 'Fehmi, M., Baganne, A. and Tourki, R. (2016) ‘A New Network on Chip Design Dedicated to Multicast Service’, International Journal of Advanced Computer Science and Applications, 7(4). Available at: https://doi.org/10.14569/ijacsa.2016.070414.']
    ],

    'APA 6th': [
        ['Статья', 'Fehmi, M., Baganne, A. and Tourki, R. (2016) ‘A New Network on Chip Design Dedicated to Multicast Service’, International Journal of Advanced Computer Science and Applications, 7(4). Available at: https://doi.org/10.14569/ijacsa.2016.070414.']
    ],

    'ГОСТ': [
        ['Статья', 'Chatmen M., Baganne A., Tourki R. A New Network on Chip Design Dedicated to Multicast Service // Int. J. Adv. Comput. Sci. Appl. 2016. Vol. 7, No. 4. P. 104–116.'],
        ['Книга', 'Dally W.J., Towles B.P. Principles and Practices of Interconnection Networks. Elsevier, 2003. 581 p.'],
        ['Электронный ресурс', 'Codescape MIPS SDK [Electronic resource]. URL: https://www.mips.com/develop/tools/codescape-mips-sdk/ (accessed: 30.11.2018).']
    ]
}

# функция обработка источника
def func(ref, style_nm='ГОСТ'):
    if style_nm == "ГОСТ":
        res = check_patterns(ref)
        if len(res) != 0:
            print("Cоответствие ГОСТ.")
        else:
            print("Несоответствие ГОСТ.")

    path_csl = path + csl[style_nm]

    attempt = 0
    n = 5
    # поиск статьи по ссылке
    # у меня тут периодически падало все, поставила счетчик попыток
    while attempt < n:
        try:
            result = cr.works(query=ref)
            break
        except Exception as e:
            attempt += 1
            if attempt == n:
                print("Достигнуто максимальное число попыток подключения к серверу.")
                return

    # ищем doi
    if result["message"]["items"]:
        doi = result["message"]["items"][0].get("DOI", "DOI не найден")
    else:
        print("Источник не найден в базе DOI.")
        print(f"Примеры оформления в стиле {style_nm}:")
        return

    ref_dict = works.doi(doi)

    # проверяем, то ли вообще нашли по doi -- содержится ли в исходной ссылке название статьи
    if (len(ref_dict["title"]) == 0) or (not ref_dict["title"][0] in ref):
        if (len(ref_dict["original-title"]) == 0) or (
            not ref_dict["original-title"][0] in ref
        ):
            print("Источник не найден в базе DOI.")
            print(f"Примеры оформления в стиле {style_nm}:")
            for ex in examples[style_nm]:
                print(f"  {ex[0]}: {ex[1]}")
            return

    bibtex_entry = get_bib_from_doi(doi)[1]

    bibtex_file = StringIO(bibtex_entry)

    bibtex_source = BibTeX(bibtex_file, encoding="ascii")

    # Выбор стиля
    # указываем путь на csl-файл
    style = CitationStylesStyle(path_csl, validate=False)

    bibliography = CitationStylesBibliography(style, bibtex_source, formatter.plain)

    # вытягиваем ключ для определения конкретной ссылки
    key_pattern = r"{(\w+),"
    key = re.search(key_pattern, bibtex_entry).groups()[0]

    citation_item = CitationItem(key)
    citation = Citation([citation_item])

    bibliography.register(citation)

    for item in bibliography.bibliography():
        s = remove_prefix(re.sub("\.{2,}", ".", str(item)))
        if s == ref:
            print("Ссылка оформлена корректно.")
        else:
            print("Возможны неточности в оформлении.")
            print("Вариант оформления:")
            print(f"  {s}")
        return
'''

def detect_language(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    clean_text = url_pattern.sub('', text)
    latin_pattern = re.compile(r'[a-zA-Z]')
    cyrillic_pattern = re.compile(r'[а-яА-Я]')
    latin_count = len(latin_pattern.findall(clean_text))
    cyrillic_count = len(cyrillic_pattern.findall(clean_text))
    if latin_count > cyrillic_count:
        return 'en'
    else:
        return 'ru'


from time import sleep

# глобальные переменные

cr = Crossref()
works = Works()

# путь на папку со стилями
path = 'docx/static/csl/'

# словарик доступных стилей
# необходимо указать название файлика со стилем
csl = {
    'Гарвард': 'harvard-cite-them-right.csl',
    'ГОСТ': 'gost-r-7-0-5-2008-numeric_replaced_to_No.csl',
    'IEEE': 'ieee.csl',
    'MDPI': 'multidisciplinary-digital-publishing-institute.csl',
    'Elsevier': 'elsevier-with-titles.csl',
    'Springer': 'springer-basic-author-date.csl'
  }

examples = {

    'ru': {
        'Статья': 'Макаров А. Д. Некоторые актуальные аспекты, касающиеся подготовки и публикации научных статей // Региональные аспекты управления, экономики и права Северо-западного федерального округа России. 2018. С. 180–188.',
        'Книга': 'Шамбрук Дж., Рассел Д. В. Молекулярное клонирование: лабораторное пособие / Дж. Шамбрук, Д. В. Рассел, 3-е изд., Москва: Проспект, 2001. 999 c.',
        'Электронный ресурс': 'Elibrary [Электронный ресурс]. URL: https://elibrary.ru/ (дата обращения: 30.11.2018).'
    },

    'en': {
        'Статья': 'Hisakata R., Nishida S., Johnston A. An adaptable metric shapes perceptual space // Current Biology. 2016. No. 14 (26). P. 1911–1915.',
        'Книга': 'Sambrook J., Russell D. W. Molecular cloning: a laboratory manual / J. Sambrook, D. W. Russell, Cold Spring Harbor, NY: CSHL Press, 2001. 999 p.',
        'Электронный ресурс': 'Codescape MIPS SDK [Electronic resource]. URL: https://www.mips.com/develop/tools/codescape-mips-sdk/ (accessed: 30.11.2018).'
    },

    'IEEE': {
        'Статья': 'R. Hisakata, S. Nishida, and A. Johnston, “An adaptable metric shapes perceptual space,” Curr. Biol., vol. 26, no. 14, pp. 1911–1915, Jul. 2016, doi: 10.1016/j.cub.2016.05.047.',
        'Книга': 'J. Sambrook and D. W. Russell, Molecular cloning: a laboratory manual, 3rd ed. Cold Spring Harbor, NY: CSHL Press, 2001.',
        'Электронный ресурс': '"Codescape MIPS SDK." mips.com. https://www.mips.com/develop/tools/codescape-mips-sdk/ (accessed November 30, 2018).'
    },

    'MDPI': {
        'Статья': 'Hisakata, R.; Nishida, S.; Johnston, A. An Adaptable Metric Shapes Perceptual Space. Curr. Biol. 2016, 26, 1911–1915, doi:10.1016/j.cub.2016.05.047',
        'Книга': 'Sambrook, J.; Russell, D.W. Molecular Cloning: A Laboratory Manual; 3rd ed.; CSHL Press: Cold Spring Harbor, NY, 2001; ISBN 0879695773.',
        'Электронный ресурс': 'Codescape MIPS SDK. https://www.mips.com/develop/tools/codescape-mips-sdk/ (accessed on 30 November 2018).'
    },

    'Elsevier': {
        'Статья': 'R. Hisakata, S. Nishida, A. Johnston, An adaptable metric shapes perceptual space, Curr. Biol. 26 (2016) 1911–1915. https://doi.org/10.1016/j.cub.2016.05.047.',
        'Книга': 'J. Sambrook, D.W. Russell, Molecular cloning: a laboratory manual, 3rd ed., CSHL Press, Cold Spring Harbor, NY, 2001.',
        'Электронный ресурс': 'Codescape MIPS SDK. <https://www.mips.com/develop/tools/codescape-mips-sdk/>, 2018 (accessed 30.11.18).'
    },

    'Springer': {
        'Статья': 'Hisakata R, Nishida S, Johnston A (2016) An adaptable metric shapes perceptual space. Curr Biol 26:1911–1915. https://doi.org/10.1016/j.cub.2016.05.047.',
        'Книга': 'Sambrook J, Russell DW (2001) Molecular cloning: a laboratory manual, 3rd edn. CSHL Press, Cold Spring Harbor, NY.',
        'Электронный ресурс': 'Codescape MIPS SDK. https://www.mips.com/develop/tools/codescape-mips-sdk/. Accessed 30 Nov 2018'
    }
}

# функция обработка источника
def func(ref, style_nm):
    res = {
        'status': 'unknown',
        'messages': [],
        'output': []
    }
    
    lang_ref = detect_language(ref)

    print(lang_ref)

    if style_nm == 'ГОСТ':
        check_res = check_patterns(ref)
        if len(check_res) != 0:
            res['messages'].append('Cоответствие ГОСТ.')
            # print('Cоответствие ГОСТ.')
        else:
            res['messages'].append('Несоответствие ГОСТ.')
            # print('Несоответствие ГОСТ.')

    path_csl = path+csl[style_nm]

    attempt = 0
    n = 2
    # поиск статьи по ссылке
    # у меня тут периодически падало все, поставила счетчик попыток
    while attempt < n:
        try:
            sleep(0.1)
            result = cr.works(query=ref)
            break
        except Exception as e:
            attempt += 1
            if attempt == n:
                res['messages'].append('Достигнуто максимальное число попыток подключения к серверу.')

                if style_nm == 'ГОСТ':
                    print(examples[lang_ref])
                    res['output'].append(examples[lang_ref])
                    print(res['output'])
                else:
                    res['output'].append(examples[style_nm])
                return
        sleep(0.1)

    # ищем doi
    if result['message']['items']:
        doi = result['message']['items'][0].get('DOI', 'DOI не найден')
    else:
        res['messages'].append('Источник не найден в базе DOI.')
        if style_nm == 'ГОСТ':
            res['output'].append(examples[lang_ref])
        else:
            res['output'].append(examples[style_nm])
        return res

    ref_dict = works.doi(doi)

    # проверяем, то ли вообще нашли по doi -- содержится ли в исходной ссылке название статьи
    if (len(ref_dict['title']) == 0) or (not ref_dict['title'][0] in ref):
        if (len(ref_dict['original-title']) == 0) or (not ref_dict['original-title'][0] in ref):
            res['messages'].append('Источник не найден в базе DOI.')

            if style_nm == 'ГОСТ':
                res['output'].append(examples[lang_ref])
            else:
                res['output'].append(examples[style_nm])
            return res

    bibtex_entry = get_bib_from_doi(doi)[1]

    bibtex_file = StringIO(bibtex_entry)

    bibtex_source = BibTeX(bibtex_file, encoding="ascii")

    # Выбор стиля
    # указываем путь на csl-файл
    style = CitationStylesStyle(path_csl, validate=False)

    bibliography = CitationStylesBibliography(style, bibtex_source, formatter.plain)

    # вытягиваем ключ для определения конкретной ссылки
    key_pattern = r"{(\w+),"
    key = re.search(key_pattern, bibtex_entry).groups()[0]

    citation_item = CitationItem(key)
    citation = Citation([citation_item])

    bibliography.register(citation)

    for item in bibliography.bibliography():
        s = remove_prefix(re.sub('\.{2,}', '.', str(item)))
        s = s.replace('?.', '?') # если название источника заканчивается вопросительным знаком, то в стиле MDPI получается два знака подряд, на этот случай проверяем и заменсяем
        s = s.replace('?,', '?')
        if s == ref:
            res['status'] = 'correct'
            res['output'].append(s)
        else:
            res['status'] = 'incorrect'
            res['output'].append(s)
        return res