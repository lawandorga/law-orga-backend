import pytest

from core.folders.domain.aggregates.content_upgrade import Content, ContentUpgrade
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.tests.helpers.car import CarWithSecretName
from core.folders.tests.helpers.encryptions import (
    AsymmetricEncryptionTest1,
    AsymmetricEncryptionTest2,
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)
from core.folders.tests.helpers.user import UserObject

# from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
# from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


@pytest.fixture
def encryption_reset():
    EncryptionPyramid.reset_encryption_hierarchies()
    yield


@pytest.fixture
def single_encryption(encryption_reset):
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionTest1)
    yield


@pytest.fixture
def double_encryption(encryption_reset):
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest2)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionTest1)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionTest2)
    yield


@pytest.fixture
def car_content_key():
    car = CarWithSecretName(name="BMW")
    content = Content(
        "My Car",
        car,
    )
    key = content.encrypt()
    yield car, content, key


@pytest.fixture
def folder_upgrade_user(car_content_key):
    car, content, key = car_content_key
    user = UserObject()
    folder = Folder.create("New Folder")
    folder.grant_access(to=user)
    upgrade = ContentUpgrade(folder=folder)
    upgrade.add_content(content, key, user)
    yield folder, upgrade, user


@pytest.fixture
def folder_user(folder_upgrade_user):
    folder, upgrade, user = folder_upgrade_user
    yield folder, user


@pytest.fixture
def upgrade_user(folder_upgrade_user):
    folder, upgrade, user = folder_upgrade_user
    yield upgrade, user