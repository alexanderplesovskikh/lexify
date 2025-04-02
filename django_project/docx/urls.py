'''
This file defines the URL routing configuration for a Django web application with the following endpoints:

1. Core Pages:
   - Main page ("/")
   - Document check page ("/check/")
   - Login page ("/login/")
   - Profile page ("/profile")
   - FAQ page ("/faq")
   - How-to guide ("/howto")

2. Document Processing:
   - File upload endpoint ("/upload_word_to_server/")
   - Report generation ("/form_report/")
   - Report viewing ("/view")
   - User documents retrieval ("/get_user_docks/")
   - File download ("/ss4d")

3. Authentication:
   - Verification code sending ("/send_code/")
   - Code verification ("/verify_code/")

4. Technical Routes:
   - Robots.txt ("/robots.txt")
   - Sitemap ("/sitemap")
   - Yandex verification file
   - No-JS fallback page ("/nojs/")
   - Frame page ("/frame/")

The URL patterns map to corresponding view functions while maintaining named routes for reverse URL lookups.
'''

from django.urls import path

from .views import get_main_page, get_check_page, UploadDocxView, get_login_page, get_no_js_page, get_frame_page, send_verification_code, verify_code, robots_txt, get_profile, get_yandex, sitemap, get_howto
from .views import get_file, form_report, get_user_docks, view_report, get_faq_page
urlpatterns = [
    path("", get_main_page, name="get_main_page"),
    path("check/", get_check_page, name="get_check_page"),
    path("login/", get_login_page, name="get_login_page"),
    path("nojs/", get_no_js_page, name="get_no_js_page"),
    path("frame/", get_frame_page, name="get_frame_page"),
    path("upload_word_to_server/", UploadDocxView.as_view(), name="upload_word_to_server"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path('send_code/', send_verification_code, name='send_code'),
    path('verify_code/', verify_code, name='verify_code'),
    path('profile', get_profile, name='get_profile'),
    path('yandex_f5638e83fe6e6dce.html', get_yandex),
    path('sitemap', sitemap),
    path('howto', get_howto),
    path('ss4d', get_file),
    path('form_report/', form_report, name="form_report"),
    path('get_user_docks/', get_user_docks, name="get_user_docks"),
    path('view', view_report, name="view_report"),
    path('faq', get_faq_page, name="get_faq_page"),
]

"""
Author: Alexander Plesovskikh
"""