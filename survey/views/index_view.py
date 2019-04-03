# -*- coding: utf-8 -*-

from django.views.generic import TemplateView

from survey.models import Survey
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# 考试列表
@method_decorator(login_required, name='dispatch')  # 登陆才允许访问
class IndexView(TemplateView):
    template_name = "survey/list.html"

    # 用来渲染模板的上下文： surveys是所有试卷的集合(标记为可见/发布的)
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        surveys = Survey.objects.filter(is_published=True)
        if not self.request.user.is_authenticated:
            surveys = surveys.filter(need_logged_user=False)
        context["surveys"] = surveys
        return context
