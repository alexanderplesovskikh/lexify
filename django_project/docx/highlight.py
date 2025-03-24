"""
Author: Max Khomin
"""

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

'''
from docz import Document
from docz.shared import Inches
from docz.enum.section import WD_ORIENT
from docz.shared import Pt, Cm, RGBColor
from docz.enum.dml import MSO_THEME_COLOR
import tempfile

import numpy as np

def create_report_docx(doc_path, clean_sentences, correct_sentences_count, confidence_correct,
                       incorrect_sentences_count, confidence_incorrect,
                       correct_sources_count, confidence_correct_sources,
                       incorrect_sources_count, confidence_incorrect_sources,
                       checker_email, filesize, filetitle, found_all):


    def create_pie_chart(data, title, labels, colors,
                    inner_text_color='white',
                    outer_text_color='black'):

        plt.rcParams.update({
            'font.size': 8,
            'font.family': 'sans-serif',
            'axes.titlesize': 9,
            'axes.titlepad': 3
        })

        fig = plt.figure(figsize=(2.45, 2.45), dpi=300, facecolor='white')
        ax = fig.add_axes([0.01, 0.01, 0.95, 0.88])

        # Построение диаграммы
        wedges, _, autotexts = plt.pie(
            data,
            colors=colors,
            radius=0.92,
            startangle=90,
            counterclock=False,
            autopct=lambda p: f'{p:.1f} %'.replace('.', ','),
            pctdistance=0.7,
            textprops={
                'color': inner_text_color,
                'fontsize': 7.5,
                'weight': 'bold'
            },
            wedgeprops={'linewidth': 0.3}
        )

        # Настройка легенды
        ax.legend(
            wedges,
            ['Корректные', 'Некорректные'],
            loc='lower center',
            bbox_to_anchor=(0.5, -0.12),
            frameon=False,
            fontsize=8,
            ncol=2
        )

        # Настройка заголовка
        plt.title(
            title,
            fontsize=9,
            pad=2,
            y=1.02
        )

        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png', bbox_inches='tight', dpi=300)
        plt.close()

        return img_stream




    # Получаем метаданные о документе
    file_size = filesize
    title = filetitle
    total_words = sum(len(sentence.split()) for sentence in clean_sentences)
    total_chars = sum(len(sentence) for sentence in clean_sentences)
    total_sentences = found_all
    total_sources_count = correct_sources_count + incorrect_sources_count

    # Процент корректных и некорректных предложений
    total_percentage_correct = correct_sentences_count / total_sentences if total_sentences > 0 else 0
    total_percentage_incorrect = incorrect_sentences_count / total_sentences if total_sentences > 0 else 0

    # Процент корректных и некорректных источников
    total_percentage_correct_sources = correct_sources_count / total_sources_count if total_sources_count > 0 else 0
    total_percentage_incorrect_sources = incorrect_sources_count / total_sources_count if total_sources_count > 0 else 0

    doc = Document()

    # Установка шрифта для всего документа на Calibri
    for style in doc.styles:
        if style.name in ['Normal', 'Heading1', 'Heading2', 'Heading3']:
            style.font.name = 'Calibri'

    # Установка размера страницы формата A4 и полей
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.orientation = WD_ORIENT.PORTRAIT
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(1.5)

    doc.add_heading(f'Отчет о проверке лингвистической приемлемости', level=1).alignment = 1
    doc.add_paragraph()

    p = doc.add_paragraph()
    run = p.add_run('Отчет предоставлен сервисом «Lexify»')
    run.italic = True

    # Горизонтальная линия
    p = doc.add_paragraph()
    run = p.add_run('--- ' * 33)
    run.font.color.rgb = RGBColor(192, 192, 192)
    p.alignment = 1

    def add_bold_paragraph(doc, label, value, value_color=None):
        """
        Добавляет параграф с жирным текстом для label и значением value.
        Возможность задать цвет текста для value через параметр value_color.
        """
        p = doc.add_paragraph()

        # Метка (жирный текст)
        run_label = p.add_run(label)
        run_label.bold = True

        # Значение (опциональный цвет)
        run_value = p.add_run(value)
        run_value.bold = False
        if value_color:
            run_value.font.color.rgb = RGBColor(*value_color)

    # Дополнительная функция для форматирования уверенности в процентах
    def format_confidence(percentage):
        return f'{percentage:.2f}'.replace('.', ',') + ' %'


    table = doc.add_table(rows=1, cols=2)
    left_cell = table.cell(0, 0)
    right_cell = table.cell(0, 1)

    # Добавление информации о документе
    add_bold_paragraph(left_cell, 'Название: ', title)
    add_bold_paragraph(left_cell, 'Автор: ', checker_email)
    add_bold_paragraph(left_cell, 'Проверяющий: ', checker_email)

    heading_para = right_cell.add_paragraph()
    heading_run = heading_para.add_run('Информация о документе')
    heading_run.font.name = 'Calibri'
    heading_run.font.size = Pt(13)
    heading_run.font.color.theme_color = MSO_THEME_COLOR.ACCENT_1
    heading_run.font.bold = True
    add_bold_paragraph(right_cell, 'Размер документа: ', f'{str(np.round(int(file_size)/1000000, 1))} МБ')
    add_bold_paragraph(right_cell, 'Число символов в тексте: ', f'{total_chars}')
    add_bold_paragraph(right_cell, 'Число слов в тексте: ', f'{total_words}')
    add_bold_paragraph(right_cell, 'Число предложений: ', f'{total_sentences}')

    # Горизонтальная линия
    p = doc.add_paragraph()
    run = p.add_run('--- ' * 33)
    run.font.color.rgb = RGBColor(192, 192, 192)
    p.alignment = 1

    # Информация об отчете
    doc.add_heading('Информация об отчете', level=2)
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))  # Дата в UTC+3
    add_bold_paragraph(doc, 'Дата составления отчета: ', f'{now.strftime("%d.%m.%Y %H:%M:%S")} (UTC+3)')

    # Создание таблицы для заполнения отчета с диаграммами
    table = doc.add_table(rows=2, cols=2)
    left_cell = table.cell(0, 0)
    # Левая верхняя ячейка таблицы - корректные и некорректные предложения
    add_bold_paragraph(left_cell, 'Корректных предложений: ',
                   f'{correct_sentences_count} ({total_percentage_correct * 100:.1f} %)'.replace(".", ","),
                   value_color=(0, 128, 0))
    #add_bold_paragraph(left_cell, 'Уверенность: ', format_confidence(confidence_correct))

    add_bold_paragraph(left_cell, 'Некорректных предложений: ',
                   f'{incorrect_sentences_count} ({total_percentage_incorrect * 100:.1f} %)'.replace(".", ","),
                   value_color=(255, 0, 0))
    #add_bold_paragraph(left_cell, 'Уверенность: ', format_confidence(confidence_incorrect))

    # Правая верхняя ячейка таблицы - диаграмма предложений
    img_stream = create_pie_chart([correct_sentences_count, incorrect_sentences_count],
                                 'Предложения', ['Корректные', 'Некорректные'],
                                 ['#4CAF50', '#FF5252'],
                                 inner_text_color='white',
                                 outer_text_color='black')
    right_cell_1 = table.cell(0, 1)
    right_cell_1.paragraphs[0].add_run().add_picture(img_stream, width=Inches(2.3))

    # Левая нижняя ячейка таблицы - корректные и некорректные источники
    left_cell_2 = table.cell(1, 0)
    add_bold_paragraph(left_cell_2, 'Корректных источников: ',
                   f'{correct_sources_count} ({total_percentage_correct_sources * 100:.1f} %)'.replace(".", ","),
                   value_color=(0, 128, 0))
    #add_bold_paragraph(left_cell_2, 'Уверенность: ', format_confidence(confidence_correct_sources))

    add_bold_paragraph(left_cell_2, 'Некорректных источников: ',
                   f'{incorrect_sources_count} ({total_percentage_incorrect_sources * 100:.1f} %)'.replace(".", ","),
                   value_color=(255, 0, 0))
    #add_bold_paragraph(left_cell_2, 'Уверенность: ', format_confidence(confidence_incorrect_sources))

    # Правая нижняя ячейка таблицы - диаграмма источников
    img_stream_sources = create_pie_chart([correct_sources_count, incorrect_sources_count],
                                        'Источники', ['Корректные', 'Некорректные'],
                                        ['#4CAF50', '#FF5252'],
                                        inner_text_color='white',
                                        outer_text_color='black')
    right_cell_2 = table.cell(1, 1)
    right_cell_2.paragraphs[0].paragraph_format.space_before = Pt(8)
    right_cell_2.paragraphs[0].add_run().add_picture(img_stream_sources, width=Inches(2.3))

    # Новый раздел для "Непроверяемой области"
    doc.add_heading('Непроверяемая область', level=2)
    p = doc.add_paragraph()
    run = p.add_run('Текст, который был исключен из проверки. Возможные ошибки в данном фрагменте текста не учтены в итоговых статистических показателях.')
    run.font.color.rgb = RGBColor(192, 192, 192)
    # Заглушка для текста, который нужно подтянуть из документа
    doc.add_paragraph('Пример текста, который должен быть извлечен из документа, например, титул или содержание.')


    # Сохранение файла отчета
    report_filename = doc_path
    doc.save(report_filename)
'''
