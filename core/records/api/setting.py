from core.auth.models.org_user import RlcUser
from core.records.use_cases.setting import create_view, delete_view, update_view
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_view(rlc_user: RlcUser, data: schemas.InputCreateView):
    create_view(rlc_user, data.name, data.columns)


@router.put("<uuid:uuid>/")
def command__update_view(rlc_user: RlcUser, data: schemas.InputUpdateView):
    update_view(rlc_user, data.uuid, data.name, data.columns)


@router.delete("<uuid:uuid>/")
def command__delete_view(rlc_user: RlcUser, data: schemas.InputDeleteView):
    delete_view(rlc_user, data.uuid)
