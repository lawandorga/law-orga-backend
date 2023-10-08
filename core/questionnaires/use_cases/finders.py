from core.auth.models.org_user import RlcUser
from core.questionnaires.models import QuestionnaireTemplate
from core.questionnaires.models.questionnaire import Questionnaire
from core.questionnaires.models.template import (
    QuestionnaireQuestion,
    QuestionnaireTemplateFile,
)
from core.seedwork.use_case_layer import finder_function


@finder_function
def template_from_id(actor: RlcUser, v: int) -> QuestionnaireTemplate:
    return QuestionnaireTemplate.objects.get(id=v, rlc__id=actor.org_id)


@finder_function
def template_question_from_id(actor: RlcUser, v: int) -> QuestionnaireQuestion:
    return QuestionnaireQuestion.objects.get(id=v, questionnaire__rlc__id=actor.org_id)


@finder_function
def template_file_from_id(actor: RlcUser, v: int) -> QuestionnaireTemplateFile:
    return QuestionnaireTemplateFile.objects.get(
        id=v, questionnaire__rlc__id=actor.org_id
    )


@finder_function
def questionnaire_from_id(actor: RlcUser, v: int) -> Questionnaire:
    return Questionnaire.objects.get(id=v, template__rlc__id=actor.org_id)
