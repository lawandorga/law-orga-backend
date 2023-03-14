from typing import List

from django.db import connection

from core.auth.models import RlcUser, StatisticUser
from core.seedwork.api_layer import Router
from core.seedwork.statistics import execute_statement
from . import schemas

router = Router()


@router.api(
    url='rlc_members/',
    output_schema=list[schemas.OutputOrgMembers]
)
def query__org_members(statistics_user: StatisticUser):
    statement = """
            select
                core_org.name as rlc_name,
                count(distinct core_rlcuser.id) as member_amount
            from core_rlcuser
            inner join core_org on core_org.id = core_rlcuser.org_id
            group by core_rlcuser.org_id, core_org.name;
            """
    data = execute_statement(statement)
    data = list(map(lambda x: {"name": x[0], "amount": x[1]}, data))
    return data


@router.api(
    url="records_created_and_closed/",
    output_schema=List[schemas.OutputRecordsCreatedClosed],
)
def get_records_created_and_closed(rlc_user: RlcUser):
    if connection.vendor == "sqlite":
        statement = """
        select t1.month as month, t2.month as month, created, closed
        from (
        select strftime('%Y/%m', r.created) as month, count(*) as created
        from core_record r
        left join core_recordtemplate t on t.id = r.template_id
        where t.rlc_id = {}
        group by strftime('%Y/%m', r.created), t.rlc_id
        ) t1
        left outer join (
        select strftime('%Y/%m', se.closed_at) as month, count(*) as closed
        from core_recordstateentry se
        left join core_record r on se.record_id = r.id
        left join core_recordtemplate t on t.id = r.template_id
        where se.value = 'Closed'
        and t.rlc_id = {}
        group by strftime('%Y/%m', se.closed_at), t.rlc_id
        ) t2 on t1.month = t2.month
        order by t1.month
        """.format(
            rlc_user.org.id, rlc_user.org.id
        )
    else:
        statement = """
        select t1.month as month, t2.month as month, created, closed
        from (
        select to_char(r.created, 'YYYY/MM') as month, count(*) as created
        from core_record r
        left join core_recordtemplate t on t.id = r.template_id
        where t.rlc_id = {}
        group by to_char(r.created, 'YYYY/MM'), t.rlc_id
        ) t1
        full outer join (
        select to_char(se.closed_at, 'YYYY/MM') as month, count(*) as closed
        from core_recordstateentry se
        left join core_record r on se.record_id = r.id
        left join core_recordtemplate t on t.id = r.template_id
        where se.value = 'Closed'
        and t.rlc_id = {}
        group by to_char(se.closed_at, 'YYYY/MM'), t.rlc_id
        ) t2 on t1.month = t2.month
        order by t1.month
        """.format(
            rlc_user.org.id, rlc_user.org.id
        )
    data = execute_statement(statement)
    data = list(
        map(
            lambda x: {
                "month": x[0] or x[1],
                "created": x[2] or 0,
                "closed": x[3] or 0,
            },
            data,
        )
    )
    return data
