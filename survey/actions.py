# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext


def make_published(modeladmin, request, queryset):
    """
    Mark the given survey as published
    """
    count = queryset.update(is_published=True)
    message = ungettext(
        "%(count)d个试卷被成功发布.",
        "%(count)d个试卷被成功发布",
        count,
    ) % {"count": count}
    modeladmin.message_user(request, message)
make_published.short_description = "发布选中考试"


def make_finished(modeladmin, request, queryset):
    """
    Mark the given survey as published
    """
    count = queryset.update(is_published=False)
    message = ungettext(
        "%(count)d个试卷被成功结束.",
        "%(count)d个试卷被成功结束",
        count,
    ) % {"count": count}
    modeladmin.message_user(request, message)
make_finished.short_description = "结束选中考试"

