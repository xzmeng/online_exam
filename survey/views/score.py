from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from survey.models import Response, Answer


# 学生成绩列表
@login_required()
def score_list(request):
    responses = Response.objects.filter(user=request.user)
    return render(request, 'survey/score_list.html',
                  {'responses': responses})


# 学生成绩详情
@login_required()
def score_detail(request, response_id):
    response = Response.objects.get(pk=response_id)
    answers = Answer.objects.filter(response=response)
    print(answers, type(answers))
    return render(request, 'survey/score_detail.html',
                  {'answers': answers, 'response': response})
