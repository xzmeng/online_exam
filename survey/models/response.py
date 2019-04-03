 # -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .survey import Survey

try:
    from django.conf import settings

    if settings.AUTH_USER_MODEL:
        user_model = settings.AUTH_USER_MODEL
    else:
        user_model = User
except (ImportError, AttributeError):
    user_model = User


class Response(models.Model):

    """
        A Response object is a collection of questions and answers with a
        unique interview uuid.
    """

    created = models.DateTimeField(_("提交时间"), auto_now_add=True)
    updated = models.DateTimeField(_("更新时间"), auto_now=True)
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name=_("试卷"),
        related_name="responses",
    )
    user = models.ForeignKey(
        user_model,
        on_delete=models.SET_NULL,
        verbose_name=_("学生"),
        null=True,
        blank=True,
    )
    interview_uuid = models.CharField(_("唯一标识符"), max_length=36)
    score = models.IntegerField(
        verbose_name=_("成绩"),
        null=True,
        blank=True,
        default=0,
    )

    class Meta(object):
        verbose_name = _("学生成绩")
        verbose_name_plural = _("学生成绩")

    def get_absolute_url(self):
        return reverse('score-detail', kwargs={'response_id': self.id})

    def __str__(self):
        msg = "{1} 对试卷 {0} 的提交".format(self.survey, self.user)
        msg += "(日期:{})".format(self.created)
        return msg
