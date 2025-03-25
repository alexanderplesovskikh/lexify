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

