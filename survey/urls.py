# -*- coding: utf-8 -*-

# url 映射信息

from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from survey.views import (ConfirmView, IndexView, SurveyCompleted, SurveyDetail, score)

urlpatterns = [
    path('', IndexView.as_view(), name="survey-list"),
    path('<int:id>/', SurveyDetail.as_view(), name="survey-detail"),
    path('<int:id>/completed/', SurveyCompleted.as_view(), name="survey-completed"),
    path('confirm/<str:uuid>/', ConfirmView.as_view(), name="survey-confirmation"),
    path('score_list', score.score_list, name="score-list"),
    path('score_detail/<int:response_id>', score.score_detail, name="score-detail"),
    path('repeat_exam/', TemplateView.as_view(template_name='survey/repeat_exam.html'), name='repeat-exam')
]
