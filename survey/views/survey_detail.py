# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View

from survey.forms import ResponseForm
from survey.models import Category, Survey, Response


# get:渲染考试页面, post:处理考卷
#
class SurveyDetail(View):
    def get(self, request, *args, **kwargs):
        # 获取考卷
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        if survey.template is not None and len(survey.template) > 4:
            # 这里可以使用教师自己添加的模板， 如果教师没有指定模板， 则使用默认模板
            template_name = survey.template
        else:
            template_name = "survey/one_page_survey.html"

        # 如果试卷需要登陆才能回答并且当前没有登陆
        if survey.need_logged_user and not request.user.is_authenticated:
            # 则跳转到登陆界面
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        # 获取所有试题分类
        categories = Category.objects.filter(survey=survey).order_by("order")
        # 实例化试卷表单
        form = ResponseForm(
            survey=survey, user=request.user
        )
        # 传递上下文
        context = {"response_form": form, "survey": survey, "categories": categories}

        # 渲染试卷
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        # 获取试卷
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        # 查看是否数据库中存在之前同一试卷、同一学生的成绩
        last_response = Response.objects.filter(survey=survey, user=request.user)
        # 如果存在，则提示学生不能重复提交试卷
        if last_response:
            return redirect(reverse('repeat-exam'))
        # 如果试卷需要登陆才能提交并且当前没有登陆
        if survey.need_logged_user and not request.user.is_authenticated:
            # 则跳转到登陆界面
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))

        categories = Category.objects.filter(survey=survey).order_by("order")
        # 使用POST中的数据来初始化回答表单ResponseForm
        form = ResponseForm(
            request.POST, survey=survey, user=request.user
        )
        context = {"response_form": form, "survey": survey, "categories": categories}
        # 如果表单验证通过
        if form.is_valid():
            # 保存表单：在数据库中生成新的成绩信息
            response = form.save()

            # 提示学生已经成功录入成绩
            return redirect(
                "survey-confirmation", uuid=response.interview_uuid,
            )

