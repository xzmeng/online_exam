# -*- coding: utf-8 -*-

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


# 试卷信息
class Survey(models.Model):

    name = models.CharField(_("考试名称"), max_length=400)
    description = models.TextField(_("试卷描述"))
    is_published = models.BooleanField(_("是否已经发布"))
    need_logged_user = models.BooleanField(
        _("只有登陆的学生可以回答"), default=True
    )
    template = models.CharField(_("模板"), max_length=255, null=True, blank=True)

    class Meta(object):
        verbose_name = _("试卷")
        verbose_name_plural = _("试卷")

    def __str__(self):
        return self.name

    def latest_answer_date(self):
        min_ = None
        for response in self.responses.all():
            if min_ is None or min_ < response.updated:
                min_ = response.updated
        return min_

    def get_absolute_url(self):
        return reverse("survey-detail", kwargs={"id": self.pk})
