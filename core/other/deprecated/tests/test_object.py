import pytest

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.other.deprecated.content_upgrade import Content
from core.other.deprecated.object import EncryptedObject


def test_is_encrypted(single_encryption, car_content_key):
    car, content, key = car_content_key
    assert car.is_encrypted

    content.decrypt(key)
    assert not car.is_encrypted


def test_encryption_errors(single_encryption):
    class SecretObject(EncryptedObject):
        ENCRYPTED_FIELDS = ["a1", "a2"]

        def __init__(self, a1, a2):
            self.a1 = a1
            self.a2 = a2

    s = SecretObject(OpenBox(data=b"v1"), LockedBox(enc_data=b"v2", key_origin="ST1"))
    assert s.is_encrypted is None

    content = Content("Test", s)
    with pytest.raises(ValueError):
        content.encrypt()


def test_decryption_errors(single_encryption):
    class SecretObject(EncryptedObject):
        ENCRYPTED_FIELDS = ["a1", "a2"]

        def __init__(self, a1, a2):
            self.a1 = a1
            self.a2 = a2

    s = SecretObject(OpenBox(data=b"v1"), OpenBox(data=b"v2"))

    content = Content("Test", s)
    key = content.encrypt()

    s.a1 = OpenBox(data=b"v3")
    with pytest.raises(ValueError):
        content.decrypt(key)