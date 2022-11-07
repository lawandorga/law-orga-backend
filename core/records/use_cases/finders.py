from core.records.models import QuestionnaireTemplate, Record


def record_from_id(actor, v) -> Record:
    return Record.objects.get(id=v, template__rlc__id=actor.org_id)


def questionnaire_template_from_id(actor, v) -> QuestionnaireTemplate:
    return QuestionnaireTemplate.objects.get(id=v, rlc__id=actor.org_id)