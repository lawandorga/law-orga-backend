from typing import List, Optional, TypedDict, cast

from django.conf import settings

from core.auth.domain.user_key import UserKey
from core.auth.models import StatisticUser
from core.data_sheets.models import DataSheet, DataSheetTemplate
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.models import RlcUser, UserProfile
from core.permissions.static import PERMISSION_RECORDS_ADD_RECORD
from core.questionnaires.models.template import QuestionnaireTemplate
from core.records.models.record import RecordsRecord
from core.records.use_cases.record import create_record as uc_create_record
from core.rlc.models import Group, Org
from core.seedwork.repository import RepositoryWarehouse


def create_questionnaire_template(
    org: Org,
    name="Test Template",
    notes="Notes of the test template.",
    save=False,
):
    template = QuestionnaireTemplate.create(name=name, org=org, notes=notes)
    if save:
        template.save()
    return template


def create_raw_org(name="Dummy's Org", pk=1, save=False):
    org = Org.create(name=name, pk=pk)
    if save:
        org.save()
    return org


def create_raw_template(org: Org | None = None, name="Test Template", pk=1):
    assert org is not None
    return DataSheetTemplate.create(name=name, org=org, pk=pk)


def create_raw_org_user(
    org=None,
    email="dummy@law-orga.de",
    name="Mr. Dummy",
    password=settings.DUMMY_USER_PASSWORD,
    email_confirmed=True,
    accepted=True,
    user_pk=1,
    pk=1,
    save=False,
):
    if org is None:
        org = create_raw_org(save=save)
    user = RlcUser.create(
        org=org,
        email=email,
        name=name,
        password=password,
        email_confirmed=email_confirmed,
        accepted=accepted,
        user_pk=user_pk,
        pk=pk,
    )
    user._group_uuids = []
    if save:
        user.save()
    return user


def create_raw_group(
    org=None, name="Test Group", description="A group for testing purposes.", pk=1
):
    if org is None:
        org = create_raw_org()
    group = Group.create(org=org, name=name, description=description, pk=pk)
    return group


def create_raw_folder(
    user: Optional[RlcUser] = None, name="Dummy's Folder", stop_inherit=False
):
    assert user is not None
    folder = Folder.create(name, user.org_id, stop_inherit=stop_inherit)
    folder.grant_access(user)
    return folder


def create_folder(name="Test Folder", user: RlcUser | None = None):
    assert user is not None

    folder = Folder.create(name=name, org_pk=user.org_id)
    folder.grant_access(to=user)
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)
    return {"folder": folder}


def create_org(name="Dummy RLC", save=True):
    org = Org.create(name=name)
    if save:
        org.save()
    return {"org": org}


def create_statistics_user(email="dummy@law-orga.de", name="Dummy 1"):
    user = UserProfile.objects.create(email=email, name=name)
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    statistics_user = StatisticUser.objects.create(user=user)
    return {
        "user": user,
        "username": user.email,
        "email": user.email,
        "password": settings.DUMMY_USER_PASSWORD,
        "statistics_user": statistics_user,
    }


def create_user(email="dummy@law-orga.de", name="Mr. Dummy"):
    user = UserProfile.objects.create(email=email, name=name)
    user.set_password(settings.DUMMY_USER_PASSWORD)
    user.save()
    return user


class CreateRlcUserData(TypedDict):
    org: Org
    user: UserProfile
    username: str
    email: str
    password: str
    rlc_user: RlcUser
    private_key: str
    public_key: bytes


def create_rlc_user(
    email="dummy@law-orga.de",
    name="Dummy 1",
    rlc=None,
    accepted=True,
    password=settings.DUMMY_USER_PASSWORD,
    save=True,
) -> CreateRlcUserData:
    if rlc is None:
        rlc = create_org("Dummy's Org", save=save)["org"]
    user = UserProfile.objects.create(email=email, name=name)
    user.set_password(password)
    if save:
        user.save()
    rlc_user = RlcUser(user=user, email_confirmed=True, accepted=accepted, org=rlc)
    rlc_user.generate_keys(password)
    if save:
        rlc_user.save()
    private_key = (
        UserKey.create_from_dict(rlc_user.key)
        .decrypt_self(password)
        .key.get_private_key()
        .decode("utf-8")
    )
    return {
        "org": rlc,
        "user": user,
        "username": user.email,
        "email": user.email,
        "password": settings.DUMMY_USER_PASSWORD,
        "rlc_user": rlc_user,
        "private_key": private_key,
        "public_key": user.get_public_key(),
    }


class CreateGroupData(TypedDict):
    group: Group


def create_group(
    user: RlcUser, name="Test Group", description="Just for testing."
) -> CreateGroupData:
    group = Group.create(org=user.org, name=name, description=description)
    group.save()
    group.add_member(user)
    group.generate_keys()
    group.save()
    return {"group": group}


def create_record_template(org=None):
    if org is None:
        org = create_org()["org"]
    template = DataSheetTemplate.objects.create(rlc=org, name="Record Template")
    return {"template": template, "org": org}


def create_data_sheet(template=None, users: Optional[List[UserProfile]] = None):
    assert users and len(users) > 0
    if template is None:
        template = DataSheetTemplate.objects.create(
            rlc=users[0].rlc, name="Record Template"
        )
    user = users[0].rlc_user
    folder = create_folder(user=user)["folder"]

    record = DataSheet(template=template)
    record.set_folder(folder)
    record.generate_key(user)
    record.save()

    for u in users[1:]:
        folder.grant_access(u.rlc_user, user)
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)

    return {"record": record}


def create_record(token="AZ-TEST", user: Optional[RlcUser] = None):
    if user is None:
        full_user = create_rlc_user()
        user = full_user["rlc_user"]
    user.grant(PERMISSION_RECORDS_ADD_RECORD)
    folder_uuid = uc_create_record(user, token)
    record = RecordsRecord.objects.get(folder_uuid=folder_uuid)
    return {"record": record, "user": user}
