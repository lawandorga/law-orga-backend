from datetime import datetime
from uuid import UUID

from django.db.models import Q
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser, UserProfile
from core.legal.models import LegalRequirement
from core.rlc.models import Org
from core.seedwork.api_layer import Router

from core.internal.api.schemas import OutputArticleList

router = Router()


class OutputMatrixUser(BaseModel):
    _group: str
    matrix_id: str

    model_config = ConfigDict(from_attributes=True)


class OutputChatPage(BaseModel):
    matrix_user: OutputMatrixUser | None


@router.get(url="page/chat/", output_schema=OutputChatPage)
def query__chat_page(user: UserProfile):
    if hasattr(user, "matrix_user"):
        return {"matrix_user": user.matrix_user}
    return {"matrix_user": None}


class OutputOrg(BaseModel):
    name: str
    id: int

    model_config = ConfigDict(from_attributes=True)


class OutputLegalRequirement(BaseModel):
    title: str
    id: int
    content: str
    accept_required: bool

    model_config = ConfigDict(from_attributes=True)


class OutputRegisterPage(BaseModel):
    orgs: list[OutputOrg]
    legal_requirements: list[OutputLegalRequirement]

    model_config = ConfigDict(from_attributes=True)


@router.get(url="page/register/", output_schema=OutputRegisterPage)
def query__register_page():
    data = {
        "orgs": list(Org.objects.all()),
        "legal_requirements": list(
            LegalRequirement.objects.filter(
                Q(accept_required=True) | Q(show_on_register=True)
            )
        ),
    }
    return data


class OutputDashboardRecord(BaseModel):
    folder_uuid: UUID
    uuid: UUID
    identifier: str
    state: str


class OutputDashboardMember(BaseModel):
    name: str
    id: int
    rlcuserid: int


class OutputDashboardQuestionnaire(BaseModel):
    name: str
    folder_uuid: UUID


class OutputDashboardChangedRecord(BaseModel):
    folder_uuid: UUID
    uuid: UUID
    identifier: str
    updated: datetime


class OutputFollowUp(BaseModel):
    time: datetime
    title: str
    folder_uuid: UUID


class OutputDashboardArticle(BaseModel):
    articles: list[OutputArticleList]

    model_config = ConfigDict(from_attributes=True)


class OutputDashboardPage(BaseModel):
    records: None | list[OutputDashboardRecord] = None
    members: None | list[OutputDashboardMember] = None
    questionnaires: None | list[OutputDashboardQuestionnaire] = None
    changed_records: None | list[OutputDashboardChangedRecord] = None
    articles: None | list[OutputDashboardArticle] = None

    model_config = ConfigDict(from_attributes=True)


@router.get(url="page/dashboard/", output_schema=OutputDashboardPage)
def query__dashboard_page(rlc_user: OrgUser):
    return rlc_user.information
