# -*- coding: utf-8 -*-

import logging
import uuid

from django import forms
from django.forms import models
from django.urls import reverse
from django.utils.text import slugify

from survey.models import Answer, Question, Response
from survey.signals import survey_completed

LOGGER = logging.getLogger(__name__)


# 该表单渲染试卷页面，并且通过它保存学生提交的答案/成绩
class ResponseForm(models.ModelForm):

    # 使用不同的html组件来渲染试卷
    WIDGETS = {
        # Question.TEXT: forms.Textarea,
        # Question.SHORT_TEXT: forms.TextInput,
        Question.RADIO: forms.RadioSelect,
        Question.SELECT: forms.Select,
        # Question.SELECT_IMAGE: ImageSelectWidget,
        # Question.SELECT_MULTIPLE: forms.CheckboxSelectMultiple,
    }

    class Meta(object):
        model = Response
        fields = ()

    def __init__(self, *args, **kwargs):
        # 获取试卷信息和学生信息
        self.survey = kwargs.pop("survey")
        self.user = kwargs.pop("user")

        super(ResponseForm, self).__init__(*args, **kwargs)
        # 生成同一学生同一试卷的唯一标识符
        self.uuid = uuid.uuid4().hex

        # 将关联到改试卷的所有问题动态添加到试卷表单中
        data = kwargs.get("data")
        for question in self.survey.questions.all():
            self.add_question(question, data)

    def _get_preexisting_response(self):
        # 查看同一学生是否之前提交过该试卷
        # 如果有则返回，没有或者学生未登陆则返回None
        if not self.user.is_authenticated:
            return None
        try:
            return Response.objects.get(user=self.user, survey=self.survey)
        except Response.DoesNotExist:
            LOGGER.debug(
                "No saved response for '%s' for user %s", self.survey, self.user
            )
            return None

    def _get_preexisting_answer(self, question):
        # 获取该学生之前回答过的信息
        response = self._get_preexisting_response()
        if response is None:
            return None
        try:
            return Answer.objects.get(question=question, response=response)
        except Answer.DoesNotExist:
            return None

    def get_question_initial(self, question, data):
        """ Get the initial value that we should use in the Form

        :param Question question: The question
        :param dict data: Value from a POST request.
        :rtype: String or None  """
        initial = None
        answer = self._get_preexisting_answer(question)
        if answer:
            # Initialize the field with values from the database if any
            if question.type == Question.SELECT_MULTIPLE:
                initial = []
                if answer.body == "[]":
                    pass
                elif "[" in answer.body and "]" in answer.body:
                    initial = []
                    unformated_choices = answer.body[1:-1].strip()
                    for unformated_choice in unformated_choices.split(","):
                        choice = unformated_choice.split("'")[1]
                        initial.append(slugify(choice))
                else:
                    # Only one element
                    initial.append(slugify(answer.body))
            else:
                initial = answer.body
        if data:
            # Initialize the field field from a POST request, if any.
            # Replace values from the database
            initial = data.get("question_%d" % question.pk)
        return initial

    def get_question_widget(self, question):
        # 获取问题需要的html组件
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    def get_question_choices(self, question):
        # 获得所有问题选项
        qchoices = None
        if question.type not in [Question.TEXT, Question.SHORT_TEXT, Question.INTEGER]:
            # 如果使用多选按钮：
            qchoices = question.get_choices()
            # 如果使用多选下拉框：
            if question.type in [Question.SELECT, Question.SELECT_IMAGE]:
                qchoices = tuple([("", "-------------")]) + qchoices
        return qchoices

    def get_question_field(self, question, **kwargs):
        # 在表单上动态生成每个问题的选项/回答输入框
        FIELDS = {
            Question.TEXT: forms.CharField,
            Question.SHORT_TEXT: forms.CharField,
            Question.SELECT_MULTIPLE: forms.MultipleChoiceField,
            Question.INTEGER: forms.IntegerField,
        }
        # logging.debug("Args passed to field %s", kwargs)
        try:
            return FIELDS[question.type](**kwargs)
        except KeyError:
            return forms.ChoiceField(**kwargs)

    # 添加问题
    def add_question(self, question, data):
        kwargs = {"label": question.text, "required": question.required}
        # 用来初始化问题的内容
        initial = self.get_question_initial(question, data)
        if initial:
            kwargs["initial"] = initial
        choices = self.get_question_choices(question)
        if choices:
            kwargs["choices"] = choices
        widget = self.get_question_widget(question)
        if widget:
            kwargs["widget"] = widget
        field = self.get_question_field(question, **kwargs)
        if question.category:
            field.widget.attrs["category"] = question.category.name
        else:
            field.widget.attrs["category"] = ""
        # logging.debug("Field for %s : %s", question, field.__dict__)
        self.fields["question_%d" % question.pk] = field

    # 保存提交表单到数据库，并计算成绩
    def save(self, commit=True):
        response = super(ResponseForm, self).save(commit=False)
        response.survey = self.survey
        response.interview_uuid = self.uuid
        if self.user.is_authenticated:
            response.user = self.user
        response.save()
        # response "raw" data as dict (for signal)
        data = {
            "survey_id": response.survey.id,
            "interview_uuid": response.interview_uuid,
            "responses": [],
        }
        # 对学生提交中的每个问题答案都将其保存到数据库中，并且关联到本次提交
        for field_name, field_value in list(self.cleaned_data.items()):
            if field_name.startswith("question_"):
                q_id = int(field_name.split("_")[1])
                question = Question.objects.get(pk=q_id)
                answer = self._get_preexisting_answer(question)
                if answer is None:
                    answer = Answer(question=question)
                answer.body = field_value
                if answer.body == question.answer:
                    response.score += question.score
                    answer.score = question.score
                data["responses"].append((answer.question.id, answer.body))
                LOGGER.debug(
                    "Creating answer for question %d of type %s : %s",
                    q_id,
                    answer.question.type,
                    field_value,
                )
                answer.response = response
                answer.save()
        response.save()
        survey_completed.send(sender=Response, instance=response, data=data)
        return response
