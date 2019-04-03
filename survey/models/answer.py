# -*- coding: utf-8 -*-


import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .question import Question
from .response import Response

LOGGER = logging.getLogger(__name__)


# 保存学生提交答案（一个问题的）
class Answer(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_("问题"),
        related_name="answers",
    )
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        verbose_name=_("提交"),
        related_name="answers",
    )
    created = models.DateTimeField(_("创建日期"), auto_now_add=True)
    updated = models.DateTimeField(_("更新日期"), auto_now=True)
    body = models.TextField(_("回答内容"), blank=True, null=True)
    score = models.IntegerField(_("得分"), blank=True, null=True, default=0)

    def __init__(self, *args, **kwargs):
        try:
            question = Question.objects.get(pk=kwargs["question_id"])
        except KeyError:
            question = kwargs.get("question")
        body = kwargs.get("body")
        if question and body:
            self.check_answer_body(question, body)
        super(Answer, self).__init__(*args, **kwargs)

    @property
    def values(self):
        if len(self.body) < 3 or self.body[0:3] != "[u'":
            return [self.body]
        #  We do not use eval for security reason but it could work with :
        #  eval(self.body)
        #  It would permit to inject code into answer though.
        values = []
        raw_values = self.body.split("', u'")
        nb_values = len(raw_values)
        for i, value in enumerate(raw_values):
            if i == 0:
                value = value[3:]
            if i + 1 == nb_values:
                value = value[:-2]
            values.append(value)
        return values

    def check_answer_body(self, question, body):
        if question.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
            choices = question.get_clean_choices()
            if body:
                if body[0] == "[":
                    answers = []
                    for i, part in enumerate(body.split("'")):
                        if i % 2 == 1:
                            answers.append(part)
                else:
                    answers = [body]
            for answer in answers:
                if answer not in choices:
                    msg = "Impossible answer '{}'".format(body)
                    msg += " should be in {} ".format(choices)
                    raise ValidationError(msg)

    def __str__(self):
        return "{} to '{}' : '{}'".format(
            self.__class__.__name__, self.question, self.body
        )
