# -*- coding: utf-8 -*-

from django import template

register = template.Library()


def collapse_form(form, category):
    # 用于在前端呈现出可以展开/收起的问题种类列表
    categories_with_error = set()
    for field in form:
        if field.errors:
            categories_with_error.add(field.field.widget.attrs["category"])
    if category.name in categories_with_error:
        return "in"
    return ""


register.filter("collapse_form", collapse_form)


# 计算有多少个问题
class CounterNode(template.Node):
    def __init__(self):
        self.count = 0

    def render(self, context):
        self.count += 1
        return self.count


@register.tag
def counter(parser, token):
    return CounterNode()
