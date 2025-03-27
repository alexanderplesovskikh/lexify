from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from time import time

#Login
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from .models import UserToken

#upload_word_to_server imports
from uuid import uuid4
import os
from subprocess import run
from zipfile import ZipFile
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

#Streaming HTTP Response
from django.http import StreamingHttpResponse
from json import dumps

#Parser, refrences and rule-based checking
from .parser import *
from .rules import RulesChecker
from .references import *
from .highlight import *
checker = RulesChecker.from_json('docx/static/excluded.json')

from .llm import *
import io
import tempfile
import numpy as np

#If used disallowed method -> show page 403.html (not ready yet)
method_not_allowed = HttpResponse("Method not allowed") #replace with not allowed page in future releases

#Render static index.html
def get_main_page(request):
    return render(request, 'index.html')

def get_faq_page(request):
    return render(request, 'faq.html')

#Render static check.html
def get_check_page(request):
    return render(request, 'check.html')

def get_frame_page(request):
    return render(request, 'frame.html')

#Render static login.html
def get_login_page(request):
    return render(request, 'login.html')

#Render static disable-js.html
def get_no_js_page(request):
    return render(request, 'disable-js.html')

def get_profile(request):
    return render(request, 'profile.html')

def get_howto(request):
    return render(request, 'howto.html')

def get_yandex(request):
    return render(request, 'yandex_f5638e83fe6e6dce.html')

robots_txt_content = """
User-Agent: *
Disallow: /admin/
"""

def get_file(request):
    zip_file = open('/home/project/Documents/L.zip', 'rb')
    response = HttpResponse(zip_file, content_type='application/force-download; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'L.zip'
    return response

def robots_txt(request):
    return HttpResponse(robots_txt_content, content_type="text/plain")

def sitemap(request):
    return HttpResponse("""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"> 
        <url>
            <loc>https://app.lexiqo.ru/</loc>
            <lastmod>01.01.2024</lastmod>
            <changefreq>monthly</changefreq>
            <priority>0.8</priority>
        </url>
        <url>
            <loc>https://app.lexiqo.ru/check/</loc>
            <lastmod>01.01.2024</lastmod>
            <changefreq>weekly</changefreq>
            <priority>0.9</priority>
        </url>
    </urlset>""", content_type="application/xml")


#Login funcs
def login_required_custom(view_func):
    """
    Author: Vlad Golub
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user:
            return JsonResponse({'error': 'Authorization required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapped_view

@csrf_exempt
def send_verification_code(request):
    """
    Author: Vlad Golub
    """
    email = request.GET['email']
   
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email является обязательным'})
    if '@' not in email:
        return JsonResponse({'status': 'error', 'message': 'Email не является валидным'})
    code = get_random_string(length=6, allowed_chars='0123456789qwertyuiopasdfghjklzxcvbnm')
    user, created = UserToken.objects.get_or_create(email=email)
    user.code = code
    user.token = None
    user.save()
    send_mail(
        'Код подтверждения от Lexify',
        f'Ваш код подтверждения: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    mail_provider = email.split('@')[-1]
    mail_links = {
        'gmail.com': 'https://mail.google.com',
        'yandex.ru': 'https://mail.yandex.ru',
        'vk.com': 'https://vk.mail.ru',
        'rambler.ru': 'https://mail.rambler.ru',
        'yahoo.com': 'https://mail.yahoo.com',
        'mail.ru': 'https://e.mail.ru',
        'outlook.com': 'https://outlook.live.com/mail'
    }
    mail_link = mail_links.get(mail_provider, '/')

    return JsonResponse({'status': 'ok', 'message': 'Отправили Вам код подтверждения на почту', 'link': mail_link})

@csrf_exempt
def verify_code(request):
    """
    Author: Vlad Golub
    """
    email = request.GET['email']
    code = request.GET['code']

    if not (email and code):
        return JsonResponse({'status': 'error', 'message': 'Email и код являются обязательными'})

    user = get_object_or_404(UserToken, email=email)

    if user.code == code:
        token = uuid4().hex
        user.token = token
        user.code = None
        user.save()

        return JsonResponse({'status': 'ok', 'token': token})

    return JsonResponse({'status': 'error', 'message': 'Неверный код'})

@login_required_custom
@csrf_exempt
def test_view(request):
    """
    Author: Vlad Golub
    """
    return JsonResponse({'message': 'You are logged in!'})

def accept_changes_in_word(file_content):
    """
    Author: Alexander Plesovskikh
    """

    # Unzip the Word file to extract XML
    with ZipFile(io.BytesIO(file_content), 'r') as docx_zip:
        with docx_zip.open('word/document.xml') as document_file:
            xml_content = document_file.read()

            root = ET.fromstring(xml_content)

            # Define the namespace for Word elements
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

            # Remove all <w:del> elements
            for parent in root.findall(".//w:del/..", namespaces):
                for del_tag in parent.findall("w:del", namespaces):
                    parent.remove(del_tag)

            # Unwrap all <w:ins> elements
            for parent in root.findall(".//w:ins/..", namespaces):
                for ins_tag in parent.findall("w:ins", namespaces):
                    # Добавляем детей ins_tag к parent
                    ins_tag_index = list(parent).index(ins_tag)
                    for child in list(ins_tag):
                        parent.insert(ins_tag_index, child)
                        ins_tag_index += 1
                    parent.remove(ins_tag)

            # Write changes back to document.xml
            modified_xml_content = ET.tostring(root, encoding='utf-8', xml_declaration=True)

    # Create a new DOCX file in memory
    output = io.BytesIO()
    with ZipFile(output, 'w') as new_docx_zip:
        # Write the modified document.xml
        new_docx_zip.writestr('word/document.xml', modified_xml_content)

        # Add all other files from the original DOCX
        with ZipFile(io.BytesIO(file_content), 'r') as original_docx_zip:
            for file_info in original_docx_zip.infolist():
                # Skip the modified document.xml
                if file_info.filename == 'word/document.xml':
                    continue
                # Read the original file content and write it to the new DOCX
                new_docx_zip.writestr(file_info.filename, original_docx_zip.read(file_info.filename))

    output.seek(0)  # Move the cursor to the beginning of the BytesIO object
    return output.getvalue()  # Return the modified DOCX content


def libreoffice_convert_to_html(word_bytes):

    """
    Author: Alexander Plesovskikh & Max Khomin
    """

    temp_docx = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
   

    temp_docx.write(word_bytes)
    temp_docx.flush()  # Ensure all data is written
    temp_docx_path = temp_docx.name  # Get the path to the temporary .docx file
   

    try:
        # Выполнение команды напрямую без скрипта Bash
        command = [
            "libreoffice",
            "--headless",
            "--convert-to", "html:HTML:EmbedImages",
            "--outdir", os.path.dirname(temp_docx.name),
            temp_docx_path
        ]
        
        result = run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Ошибка при конвертации:", result.stderr)
            return False
        
        temp_html_path = temp_docx_path.replace(".docx", ".html")
        
        # Read the HTML file
        with open(temp_html_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()

            return html_content

    finally:
        temp_docx.close()  # Close the .docx file
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)  # Remove the .docx file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
      


def add_ids_to_html(html):
    """
    Author: Alexander Plesovskikh
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Use a counter for IDs to speed up unique ID generation
    counter = 0
    
    # Iterate over all elements and add an ID if missing
    for element in soup.find_all(True):
        if not element.get('id'):
            element['id'] = f'e_ftre3elemidsftr3d_{counter}'
            counter += 1

        if element.has_attr('align'):
            if element.has_attr('style'):
                element['style'] = element['style'] + f"; text-align: {element['align']};"
            else:
                element['style'] = f"text-align: {element['align']};"

        if element.has_attr('face'):
            if element.has_attr('style'):
                element['style'] = element['style'] + f"; font-family: {element['face']};"
            else:
                element['style'] = f"font-family: {element['face']};"

        if element.has_attr("href"):
            if not element['href'].startswith("#"):
                element['target'] = '_blank'
        
        if element.name == 'table':
            if element.has_attr('class'):
                element['class'] = element['class'] + " table"
            else:
                element['class'] = "table"
            
            div_responsive = soup.new_tag('div', **{'class': 'table-responsive'})
            element.insert_before(div_responsive)
            div_responsive.append(element)

        if element.has_attr('style'):
            if 'position: absolute;' in element['style']:
                element['style'] = element['style'] + "; position: static;"

        
        

    return str(soup)


import concurrent.futures
from json import dumps

def process_ref(ref_id, ref):
    """
    Author: Alexander Plesovskikh & Tatyana Romanova
    """
    cleaned_ref = remove_line_breaks(remove_prefix(ref))
    checked_ref = func(cleaned_ref, 'ГОСТ')
    status = 1
    data = {
        'text': ref, 
        'rule': checked_ref, 
        'id': f'ref_{ref_id}', 
        'status': status
    }
    insert_paragraph(ref, True)
    return [ref_id, dumps(data).encode('utf-8') + b'<specTeg>']

def parallel_process_refs(refs):
    """
    Author: Alexander Plesovskikh
    """
    results = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        future_to_ref = {executor.submit(process_ref, ref_id, ref): (ref_id, ref) for ref_id, ref in enumerate(refs)}
        
        for future in concurrent.futures.as_completed(future_to_ref):
            results.append(future.result())
    
    return results

def process_find_sent(sent_id, sent, file):
    """
    Author: Max Khomin
    """
    found = find_sentence_in_html(file, sent)
    return {sent_id: found}

def parallel_process_find(file, array):
    """
    Author: Alexander Plesovskikh
    """
    results = {}

    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as executor:
        future_to_ref = {executor.submit(process_find_sent, sent_id, sent, file): (sent_id, sent) for sent_id, sent in enumerate(array)}

        for future in concurrent.futures.as_completed(future_to_ref):
            result_dict = future.result()  # This will be a dictionary {sent_id: found}
            results.update(result_dict) 
    
    return results

def stream2(html_file, is_ml, biblio_style_get):

    print(biblio_style_get)
    
    """
    Author: Alexander Plesovskikh
    """

   
    data = {
        "id": "init_1", 
        "text": html_file
    }
    json_data = dumps(data).encode('utf-8')
    yield json_data + b'<specTeg>'

   

    soup_object = get_bs4_repr(html_file)

    texts, refs = text_references_split(soup_object)

    raw_sents = get_sents_per_para(texts)

    sentencized_sents = merge_raw_sents(raw_sents)

    cleaned_sents = form_list_of_clean_sents(sentencized_sents)



    '''result_refs = parallel_process_refs(refs)
    sorted_refs = sorted(result_refs, key=lambda x: x[0])

    for i in sorted_refs:
        yield i[1]'''


   

    
    found_all = parallel_process_find(html_file, sentencized_sents)


    all_sents_checked = len(cleaned_sents)

    data = {    'text': f"{all_sents_checked}", 
                'rule': "", 
                'id': 'sys_0',
                'rule_status': 'num_sents',
                'found': ""
                }
            
    data_new = dumps(data).encode('utf-8')

    yield  data_new + b'<specTeg>'


    for text_id, text in enumerate(cleaned_sents):

        
        data = {'text': f"{text}", 
                'rule': "", 
                'id': f'sys_1_{text_id}',
                'rule_status': '',
                'found': ""
                }
                
        data_new = dumps(data).encode('utf-8') 

        yield  data_new + b'<specTeg>'
  
   
    for text_id, text in enumerate(cleaned_sents):

        if text == '<#excluded#>':
            continue

      
        insert_paragraph(text, False)
      
        rule_checker_result = checker.grep_text(" " + text + " ")
      

        if rule_checker_result[0] == True:

            found = found_all[text_id][0]

            rule_to_send = rule_checker_result[1]

            if rule_to_send.endswith(";"):
                rule_to_send = rule_to_send[:-1] + "."
          
            data = {
                'text': f'{text}', 
                'rule': rule_to_send, 
                'id': f'text_{text_id}',
                'rule_status': 'rule_error',
                'found': found
                }
            
            data_new = dumps(data).encode('utf-8')

            yield  data_new + b'<specTeg>'
          
        
        if rule_checker_result[0] == False:

            if is_ml == "1":

          
                llm_result = model.predict_sentence(text)[0]['Unacceptable']
                llm_label = 'Возможно, лингвистически неприемлемое предложение c вероятностью (%): '
                llm_score = np.round(llm_result*100,2)
            
            
                #model2res = model.predict_sentence(text)
            

                if llm_score > 85:
                    
                    found = found_all[text_id][0]

                
                    data = {
                        'text': f'{text}', 
                        'rule': f'{llm_label}{str(llm_score).replace(".", ",")}', 
                        'id': f'text_{text_id}',
                        'rule_status': 'llm_error',
                        'found': found
                        }
                    
                    data_new = dumps(data).encode('utf-8')              

                    yield data_new + b'<specTeg>'

    
    for ref_id, ref in enumerate(refs):
        try:
            cleaned_ref = remove_line_breaks(remove_prefix(ref))
            checked_ref = func(cleaned_ref, biblio_style_get)

            status = 1

            data = {
                'text': ref, 
                'rule': checked_ref, 
                'id': f'ref_{ref_id}', 
                'status': status
            }

            insert_paragraph(ref, True)
        
            data_new = dumps(data).encode('utf-8') 
            print('biblio yes')
            yield data_new + b'<specTeg>'
        except Exception as e:
            print('biblio error: ', e)
            checked_ref = {
                'status': 'unknown',
                'messages': ['Error while checking this reference'],
                'output': ['Error']
            }
            data = {
                'text': ref, 
                'rule': checked_ref, 
                'id': f'ref_{ref_id}', 
                'status': 1
            }

            insert_paragraph(ref, True)
            data_new = dumps(data).encode('utf-8') 
            print('biblio yes')
            yield data_new + b'<specTeg>'
            continue


@method_decorator(csrf_exempt, name='dispatch')
class UploadDocxView(View):
    async def post(self, request, *args, **kwargs):
        """
        Author: Vlad Golub
        """
        if request.method != 'POST':
            print('no post')
            return method_not_allowed
        else:
            try:
                is_ml = request.POST['is_ml']
                biblio_style_get = request.POST['biblio']
                file = request.FILES['file']
                if not file or not file.name.endswith('.docx'):
                    return JsonResponse({'status': "error", 'type': 'preload', 'message': f'Тип файла .{file.name.split(".")[-1]} не поддерживается'}, status=500)
                else:
                    docx_accepted_file = accept_changes_in_word(file.read())
                    libre_result = libreoffice_convert_to_html(docx_accepted_file)  
                    if libre_result == False:
                        return JsonResponse({'status': "error", 'type': 'preload', 'message': 'Не удалось конвертировать файл'}, status=500)
                      
                    front_html = add_ids_to_html(libre_result)
                  
                    response = StreamingHttpResponse(stream2(front_html, is_ml, biblio_style_get), content_type='application/json')
                    response['Content-Disposition'] = 'inline; filename="output.html"'
                    return response
            except Exception as e:
                print(f'error {str(e)}')
                return JsonResponse({'status': "error", 'message': str(e)})
 


#db imports
from datetime import datetime
from .models import Paragraph
from .models import AnalysisLog

def insert_paragraph(text, is_reference):
    """
    Author: Vlad Golub
    """
    timestamp = int(datetime.now().timestamp())
    paragraph = Paragraph.objects.create(content=text, is_reference=is_reference, timestamp=timestamp)
    return paragraph


def libreoffice_convert_to_pdf(uniq, outdir):

    """
    Author: Alexander Plesovskikh & Max Khomin
    """

    temp_docx_path = outdir + uniq  # Get the path to the temporary .docx file
   
    try:
        # Выполнение команды напрямую без скрипта Bash
        command = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", outdir,
            temp_docx_path
        ]
        
        result = run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Ошибка при конвертации:", result.stderr)
            return False

    finally:
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)


import pdfkit
import datetime as dt

@csrf_exempt
def form_report(request):
    if request.method != 'POST':
        print('no post')
        return method_not_allowed
    else:
      
        unique_string = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid4()}"
        outdir = '/home/project/Documents/Lexify02/django_project/docx/static/pdfs/'

        email_s = request.POST['email']
        html_s = request.POST['html']
        errors_s = request.POST['errors']
        size_s = request.POST['size']
        time_s = request.POST['time']
        name_s = request.POST['name']
        bites_s = request.POST['bites']
        all_sent_parser = request.POST['all_sents']
        allerrHTML = request.POST['allerrHTML']
        allerrRef = request.POST['allerrRef']

        all_sent_parser = all_sent_parser.split("<abhgf5678ug%&$fvghji76tredcvbjiu7y6tf>")

        found_llm = float(request.POST['llmerr'])
        found_rule = float(request.POST['ruleerr'])
        found_style = float(request.POST['styleerr'])
        found_all = float(request.POST['overallsents'])
       
        doc_path = outdir + unique_string + '.docx'

        clean_sentences = all_sent_parser

        #correct_sentences_count = int(found_all) - int(found_llm) - int(found_rule)
        #confidence_correct = 100
        ##incorrect_sentences_count = int(found_rule) + int(found_llm)
        #confidence_incorrect = 100
        #correct_sources_count = 1
        #confidence_correct_sources = 1
        #incorrect_sources_count = 1
        ##confidence_incorrect_sources = 1
        checker_email = email_s

        '''create_report_docx(doc_path, clean_sentences,
                           correct_sentences_count, confidence_correct,
                        incorrect_sentences_count, confidence_incorrect,
                        correct_sources_count, confidence_correct_sources,
                        incorrect_sources_count, confidence_incorrect_sources,
                        checker_email, bites_s, name_s, int(float(found_all)))'''


       


        AnalysisLog.objects.create(email=email_s, 
                                   report_text=html_s, 
                                   error_count=errors_s,
                                   file_name=name_s,
                                   file_chars=size_s,
                                   file_time=time_s,
                                   file_hash=unique_string)
        
        '''libreoffice_convert_to_pdf(unique_string + '.docx', outdir)'''


        pattern = r'(<[^>]* data-bs-title="([^"]*)"[^>]*>)'

        # Function to replace the match with the content before the corresponding tag
        def replace_title(match):
            full_tag = match.group(1)  # The entire tag with data-bs-title
            title_content = match.group(2)  # The content of data-bs-title
            return f'''(<span class="err_in">{title_content}</span>) {full_tag}'''  # Place the content before the tag

        # Replace all occurrences in the HTML string
        modified_html = re.sub(pattern, replace_title, allerrHTML)


        now = dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))  # Дата в UTC+3
        all_mistakes = int(float(found_all))
        all_rules = int(float(found_rule))
        all_llm = int(float(found_llm))
        all_style = int(float(found_style))

        percent_llm = 0
        try:
            percent_llm = np.round(all_llm / (all_llm+all_rules) * 100, 2) if all_mistakes != 0 else 0
        except:
            percent_llm = 0

        percent_rule = 0
        try:
            percent_rule = np.round(all_rules / (all_llm+all_rules) * 100, 2) if all_mistakes != 0 else 0
        except:
            percent_rule = 0

        # Convert HTML string to PDF
        pdfkit.from_string(f'''<!DOCTYPE html>
                            <html lang="ru">
                            <head>
                                <meta charset="UTF-8">
                           <style> 
                           
                           ''' + """@media print { .pagebreak { page-break-before: always; } } .err_in {text-decoration: underline dotted red; font-family: 'Trebuchet MS', sans-serif; color: red; font-size: 12pt;}" + ".alert{ text-decoration: underline dotted red; font-family: 'Trebuchet MS', sans-serif; color: red; font-size: 12pt; } h2,h3 { color:#355d8f } h2,hr{margin:2rem 0}body{margin:0;padding:0;font-family:'Trebuchet MS','Helvetica Neue',Helvetica,sans-serif;line-height:1.6;color:#333}ol,ol>ul,ul{padding-left:2rem}h2{text-align:center;font-size:18pt}h3{margin:1.5rem 0;font-size:16pt;border-bottom:2px solid #e0e0e0;padding-bottom:.5rem}.alert,.err_in,li,p{font-size:12pt}p{margin:.8rem 0}strong{color:#2c3e50}a{color:#355d8f;text-decoration:none;transition:.3s}a:hover{text-decoration:underline}ol,ul{margin:1rem 0}li{margin:.5rem 0}ul ul{margin-top:.5rem;margin-bottom:.5rem}ol>ul{list-style:none;margin:1rem 0}ol>ul li::before{content:"—";color:#355d8f;display:inline-block;width:1.5em;margin-left:-1.5em;font-weight:900;font-size:1.1em;position:relative;top:-.1em}ol>ul li p{margin-left:.5rem;display:inline-block}hr{border:0;border-top:1px solid #ddd}.alert,.err_in{text-decoration:underline dotted red;font-family:'Trebuchet MS',sans-serif;color:red}""" + f'''
                           
                           </style>
                           </head>
                            <body>
                           
                           <div style="font-family: 'Trebuchet MS', 'Helvetica Neue', Helvetica, sans-serif; padding: 4rem;">
                           
                           <h2 style="text-align: center; color: #355d8fff;">Отчет о проверке лингвистической приемлемости</h2>
                           <p style="text-align: center;"><i>Отчет предоставлен сервисом «Lexify»</i></p>
                           <br>
                           <hr>
                           <br>
                           <h3>Информация о документе</h3>
                           <p><strong>Название:</strong> {name_s}</p>
                           <p><strong>Автор:</strong> <a href="mailto:{email_s}" target="_blank">{email_s}</a></p>
                           <p><strong>Размер документа:</strong> {str(np.round(int(bites_s)/1000000*1000, 2))} КБ</p>
                           <p><strong>Число символов в тексте:</strong> {len(" ".join(all_sent_parser))}</p>
                           <p><strong>Число слов в тексте:</strong> {len((" ".join(all_sent_parser)).split(" "))}</p>
                           <p><strong>Число предложений в тексте:</strong> {len(all_sent_parser)}</p>
                           <br>
                           <hr>
                           <br>
                           <h3>Информация об отчете</h3>
                           <p><strong>Дата составления отчета:</strong> {now.strftime("%d.%m.%Y %H:%M:%S")} (UTC+3)</p>
                           <p><strong>ID документа:</strong> <a href="https://app.lexiqo.ru/view?id={unique_string}" target="_blank">{unique_string}</a></p>
                           <ol>
                           <li><p><strong>Всего ошибок:</strong> {all_rules+all_llm} (100,0 %), <i>из них:</i></p></li>
                           <ul>
                           <li><p><strong><i>предложения, нарушающие правила:</i></strong> {all_rules} ({str(percent_rule).replace(".", ",")} %)</p></li>
                           <li><p><strong><i>предложения, помеченные ИИ как ошибочные с вероятностью ≥ 85 %:</i></strong> {all_llm} ({str(percent_llm).replace(".", ",")} %)</p></li>
                           </ul>
                           <li><p><strong><i>Ошибки в оформлении документа:</i></strong> {all_style}</p></li>
                           </ol>
                           <br>
                           <hr>
                           <br>
                           <div class="pagebreak"> </div>
                           <h3>Текст документа</h3>
                           <br><div>{modified_html}</div><br>
                           <br>
                           <hr>
                           <br>
                           <h3>Список используемых источников</h3>
                           <br><div>{allerrRef}</div><br>


                           


                           </div>

                           </body>
                            </html>

                           ''', f'''/home/project/Documents/Lexify02/django_project/docx/static/pdfs/{unique_string}.pdf''')
        
       
    return JsonResponse({'status':'ok', 'name':unique_string})


from .models import AnalysisLog

def get_logs_by_email(email):
    """
    Retrieve all AnalysisLog entries that match the given email.

    :param email: The email address to filter by.
    :return: A QuerySet of AnalysisLog entries.
    """
    logs = AnalysisLog.objects.filter(email=email).values_list('id', 'email', 'date', 'error_count', 'file_name', 'file_hash')
    return logs

@csrf_exempt
def get_user_docks(request):
    email_s = request.POST['email']
    works = list(reversed(list(get_logs_by_email(email_s))))

    all_work_string = ""

    for work in works:
        date_here = work[2].strftime("%d.%m.%Y %H:%M")
        all_work_string += f"""
<div class="row align-items-center new">
    <div class="col-sm-6"><p class="text-center mb05"><i class="bi bi-file-earmark"></i> {work[4]}</p></div>
    <div class="col-sm-2"><p class="text-center mb05"><i class="bi bi-calendar"></i> {date_here}</p></div>
    <div class="col-sm-2"><p class="text-center mb05"><span class="error_badge"><i class="bi bi-bug-fill"></i> {work[3]}</span></p></div>
    <div class="col-sm-2"><p class="text-center mb05">
    <a href="/view?id={work[5]}" class="btn btn-sm btn-light" title="View"><i class="bi bi-eye"></i></a>
    <a href="/static/pdfs/{work[5]}.pdf" target="_blank" class="btn btn-sm btn-light" title="Download"><i class="bi bi-arrow-bar-down"></i></a>
    <!--<a href="#" class="btn btn-sm btn-light" title="Share"><i class="bi bi-share"></i></a>-->
    </p></div>
</div>
<hr>
"""
    
    status = str(len(works))

    all_work_string = """<div id="all_lines">""" + all_work_string + """</div>"""
 
    return JsonResponse({'status':status, 'all_work_string': all_work_string})

import re

def view_report(request):

    #Not implemented: disallow to access someone's docuemnts!

    log_id = request.GET.get('id')

    try:
        # Retrieve the AnalysisLog instance by ID
        log_entry = AnalysisLog.objects.get(file_hash=log_id)
        content_get = log_entry.report_text  # Return the email field
        content_get = content_get.replace('<span onclick="getReport()" id="uniqueGetReport" class="btn btn-sm btn-primary">Скачать отчет <i class="bi bi-download"></i></span>', "")
        content_get = content_get.replace('<span id="buttonGetDocSpin"><i style="top: 0;" class="c-inline-spinner"></i></span>', "")
        # Define the pattern to find the substring
        pattern = r'(<input type="range" class="form-range".*?)(>)'
        content_get = re.sub(pattern, r'\1 disabled\2', content_get)
        content_get = content_get.replace('<form class="d-flex" role="search">', '<form class="d-flex" role="search" style="margin-bottom:0px;">')
        content_get = content_get.replace ("data-bs-title=", "title=")
    except AnalysisLog.DoesNotExist:
        content_get = '<meta http-equiv="refresh" content="0; url=https://app.lexiqo.ru/profile" />'
    

    return HttpResponse(content_get, content_type="text/html")
