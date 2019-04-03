# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from .category import Category
from .survey import Survey

try:  # pragma: no cover
    from _collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

LOGGER = logging.getLogger(__name__)


# 选项帮助信息
CHOICES_HELP_TEXT = _(
    '只有在使用Radio，Select时候才会使用到choices字段'
)


# 验证教师输入的问题选项是否有效
def validate_choices(choices):
    """  Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    values = choices.split(",")
    empty = 0
    for value in values:
        if value.replace(" ", "") == "":
            empty += 1
    if len(values) < 2 + empty:
        msg = "选项里面需要输入一系列选项并且以逗号（英文中的逗号）分开"
        msg += "，选项个数至少为2个。"
        raise ValidationError(msg)


class SortAnswer(object):
    CARDINAL = "cardinal"
    ALPHANUMERIC = "alphanumeric"


class Question(models.Model):

    TEXT = "text"
    SHORT_TEXT = "short-text"
    RADIO = "radio"
    SELECT = "select"
    SELECT_IMAGE = "select_image"
    SELECT_MULTIPLE = "select-multiple"
    INTEGER = "integer"

    # 所有可以选择的问题的类型
    # 暂时只使用了选择按钮和下拉框
    QUESTION_TYPES = (
        # (TEXT, _("多行文本")),
        # (SHORT_TEXT, _("单行文本")),
        (RADIO, _("选择按钮")),
        (SELECT, _("选择下拉框")),
        # (SELECT_MULTIPLE, _("多选")),
        # (SELECT_IMAGE, _("图片下拉框")),
        # (INTEGER, _("整数")),
    )

    text = models.TextField(_("内容"))
    order = models.IntegerField(_("顺序"))
    required = models.BooleanField(_("必需"))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name=_("问题类别"),
        blank=True,
        null=True,
        related_name="questions",
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name=_("所属试卷"),
        related_name="questions",
    )
    type = models.CharField(
        _("类型"), max_length=200, choices=QUESTION_TYPES, default=TEXT
    )
    choices = models.TextField(
        _("选项"), blank=True, null=True, help_text=CHOICES_HELP_TEXT
    )
    answer = models.CharField(
        _("答案"), max_length=200, blank=True, null=True
    )
    score = models.IntegerField(
        _("分值"), help_text='The score of the question', null=True, blank=True
    )

    class Meta(object):
        verbose_name = _("问题")
        verbose_name_plural = _("问题")
        ordering = ("survey", "order")

    def save(self, *args, **kwargs):
        if self.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
            validate_choices(self.choices)
        super(Question, self).save(*args, **kwargs)

    def get_clean_choices(self):
        """ Return split and stripped list of choices with no null values. """
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(","):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    @property
    def answers_as_text(self):
        # 将回答以字符串列表的形式返回
        answers_as_text = []
        for answer in self.answers.all():
            for value in answer.values:
                answers_as_text.append(value)
        return answers_as_text

    @staticmethod
    def standardize(value, group_by_letter_case=None, group_by_slugify=None):
        # 标准化
        if group_by_slugify:
            value = slugify(value)
        if group_by_letter_case:
            value = value.lower()
        return value


    def get_choices(self):
        # 解析选项并且渲染出html
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice, allow_unicode=True), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        msg = "Question '{}' ".format(self.text)
        if self.required:
            msg += "(*) "
        msg += "{}".format(self.get_clean_choices())
        return msg
