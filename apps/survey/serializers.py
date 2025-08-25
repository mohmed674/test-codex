from rest_framework import serializers
from .models import Survey, SurveyQuestion, SurveyChoice, SurveyResponse, Answer


class SurveyChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyChoice
        fields = ['id', 'choice_text']


class SurveyQuestionSerializer(serializers.ModelSerializer):
    surveychoice_set = SurveyChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = ['id', 'question_text', 'question_type', 'surveychoice_set']


class SurveySerializer(serializers.ModelSerializer):
    surveyquestion_set = SurveyQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'created_at', 'surveyquestion_set']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer_text', 'selected_choice']


class SurveyResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)

    class Meta:
        model = SurveyResponse
        fields = ['id', 'survey', 'submitted_at', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = SurveyResponse.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(response=response, **answer_data)
        return response
