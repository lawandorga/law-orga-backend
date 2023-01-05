from django.db.models import Q

from core.records.models import Record, RecordAccess, RecordDeletion, RecordTemplate
from core.seedwork.use_case_layer import finder_function


@finder_function
def record_from_id(actor, v) -> Record:
    return Record.objects.get(id=v, template__rlc__id=actor.org_id)


@finder_function
def template_from_id(actor, v) -> RecordTemplate:
    return RecordTemplate.objects.get(id=v, rlc_id=actor.org_id)


@finder_function
def deletion_from_id(actor, v) -> RecordDeletion:
    return RecordDeletion.objects.get(
        Q(id=v)
        & (
            Q(requestor__org_id=actor.org_id)
            | Q(processor__org_id=actor.org_id)
            | Q(record__template__rlc_id=actor.org_id)
        )
    )


@finder_function
def access_from_id(actor, v) -> RecordAccess:
    return RecordAccess.objects.get(
        Q(id=v)
        & (
            Q(requestor__org_id=actor.org_id)
            | Q(processor__org_id=actor.org_id)
            | Q(record__template__rlc_id=actor.org_id)
        )
    )
