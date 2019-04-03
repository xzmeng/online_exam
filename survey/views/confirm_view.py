# -*- coding: utf-8 -*-

from django.views.generic import TemplateView


# 提交完成绩后显示的页面：提醒学生提交成功，或者不能重复提交
class ConfirmView(TemplateView):

    template_name = "survey/confirm.html"

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context["uuid"] = kwargs["uuid"]
        return context
