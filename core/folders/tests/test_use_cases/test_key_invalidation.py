from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork import test_helpers


def test_key_invalidation_on_user_lock(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_org_user(rlc=org)
    u = org_user["rlc_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = DjangoFolderRepository()
    r.save(folder)

    u.lock()
    u.save()

    new_folder = r.retrieve(u.org_id, folder.uuid)

    assert u.locked
    assert new_folder.has_invalid_keys(u)
