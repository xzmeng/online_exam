# -*- coding: utf-8 -*-

from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from .survey import Survey


# 问题种类


class Category(models.Model):

    name = models.CharField(_("种类名称"), max_length=400)
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name=_("试卷"),
        related_name="categories",
    )
    order = models.IntegerField(_("显示顺序"), blank=True, null=True)
    description = models.CharField(
        _("描述"), max_length=2000, blank=True, null=True
    )

    class Meta(object):
        # pylint: disable=too-few-public-methods
        verbose_name = _("种类")
        verbose_name_plural = _("种类")

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))
