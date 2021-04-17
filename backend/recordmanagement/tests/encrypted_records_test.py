#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.api.tests.statics import StaticTestMethods
from backend.recordmanagement import models as record_models
from backend.static.encryption import AESEncryption
from backend.static.permissions import (
    PERMISSION_CAN_ADD_RECORD_RLC,
    PERMISSION_CAN_CONSULT,
)


class EncryptedRecordTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication_superuser()
        self.base_url = "/api/records/records/"
        self.base_create_record_url = "/api/records/create_record/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][1]["user"],
            self.base_fixtures["users"][2]["user"],
        ]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(
            rlc=self.base_fixtures["rlc"], users=users
        )

        # user 0 can create records
        add_record_permission = api_models.Permission.objects.get(
            name=PERMISSION_CAN_ADD_RECORD_RLC
        )
        has_perm = api_models.HasPermission(
            permission=add_record_permission,
            user_has_permission=self.base_fixtures["users"][0]["user"],

        )
        has_perm.save()

        # all users from group 0 can consult
        can_consult_permission = api_models.Permission.objects.get(
            name=PERMISSION_CAN_CONSULT
        )
        has_perm = api_models.HasPermission(
            permission=can_consult_permission,
            group_has_permission=self.base_fixtures["groups"][0],

        )
        has_perm.save()

    def test_user_has_permission(self):
        user1 = api_models.UserProfile(email="abc1@web.de", name="abc1")
        user1.save()
        user2 = api_models.UserProfile(email="abc2@web.de", name="abc2")
        user2.save()
        user3 = api_models.UserProfile(email="abc3@web.de", name="abc3")
        user3.save()
        record = record_models.EncryptedRecord(record_token="asd123")
        record.save()
        record.working_on_record.add(user1)

        permission = record_models.EncryptedRecordPermission(
            request_from=user2, request_processed=user3, state="gr", record=record
        )
        permission.save()

        self.assertTrue(record.user_has_permission(user1))
        self.assertTrue(record.user_has_permission(user2))

    def test_create_and_get_encrypted_record(self):
        number_of_records_before: int = record_models.EncryptedRecord.objects.count()
        number_of_record_encryptions_before: int = record_models.RecordEncryption.objects.count()
        number_of_clients_before: int = record_models.EncryptedClient.objects.count()
        number_of_notifications_before: int = api_models.Notification.objects.count()

        private_key: bytes = self.base_fixtures["users"][0]["private"]
        client: APIClient = self.base_fixtures["users"][0]["client"]

        record_note = "important record note fpr record AZ 0011/123"
        record_token = "AZ 0011/123"
        origin_country = record_models.OriginCountry.objects.first()
        tag_ids = [
            record_models.RecordTag.objects.all()[0].id,
            record_models.RecordTag.objects.all()[1].id,
        ]
        new_record_object = {
            "client_birthday": "2000-06-12",
            "client_name": "Bruce Wayne",
            "client_note": "",
            "client_phone_number": "12312312",
            "consultants": [
                self.base_fixtures["users"][0]["user"].id,
                self.base_fixtures["users"][1]["user"].id,
            ],
            "first_contact_date": "2020-04-14",
            "origin_country": origin_country.id,
            "record_note": record_note,
            "record_token": record_token,
            "tags": tag_ids,
        }
        response: Response = client.post(
            "/api/records/e_record/",
            new_record_object,
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual(
            number_of_records_before + 1, record_models.EncryptedRecord.objects.count()
        )
        self.assertEqual(
            number_of_clients_before + 1, record_models.EncryptedClient.objects.count()
        )
        self.assertEqual(
            number_of_record_encryptions_before + 2,
            record_models.RecordEncryption.objects.count(),
        )

        self.assertIn("note", response.data)
        self.assertEqual(record_note, response.data["note"])
        self.assertIn("record_token", response.data)
        self.assertEqual(record_token, response.data["record_token"])

        new_record_from_db: record_models.EncryptedRecord = record_models.EncryptedRecord.objects.get(
            pk=response.data["id"]
        )
        self.assertIn(
            self.base_fixtures["users"][0]["user"],
            new_record_from_db.working_on_record.all(),
        )
        self.assertIn(
            self.base_fixtures["users"][1]["user"],
            new_record_from_db.working_on_record.all(),
        )
        self.assertEqual(origin_country, new_record_from_db.client.origin_country)
        self.assertIn(
            record_models.RecordTag.objects.get(pk=tag_ids[0]),
            new_record_from_db.tagged.all(),
        )
        self.assertIn(
            record_models.RecordTag.objects.get(pk=tag_ids[1]),
            new_record_from_db.tagged.all(),
        )

        # check for notifications too
        self.assertEqual(
            number_of_notifications_before + 1, api_models.Notification.objects.count()
        )

        # get record back from db
        response: Response = client.get(
            "/api/records/e_record/" + str(response.data["id"]) + "/",
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(200, response.status_code)

    def test_create_encrypted_record_cant_consult(self):
        number_of_records_before: int = record_models.EncryptedRecord.objects.count()
        private_key: bytes = self.base_fixtures["users"][0]["private"]
        client: APIClient = self.base_fixtures["users"][0]["client"]

        record_note = "important record note fpr record AZ 0011/123"
        record_token = "AZ 0011/123"
        new_record = {
            "client_birthday": "2000-06-12",
            "client_name": "Bruce Wayne",
            "client_note": "",
            "client_phone_number": "12312312",
            "consultants": [
                self.base_fixtures["users"][0]["user"].id,
                self.base_fixtures["users"][3]["user"].id,
            ],
            "first_contact_date": "2020-04-14",
            "origin_country": record_models.OriginCountry.objects.first().id,
            "record_note": record_note,
            "record_token": record_token,
            "tags": [record_models.RecordTag.objects.first().id],
        }
        response: Response = client.post(
            "/api/records/e_record/",
            new_record,
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual(
            number_of_records_before, record_models.EncryptedRecord.objects.count()
        )

    def test_get_encrypted_record(self):
        private_key: bytes = self.base_fixtures["users"][0]["private"]
        client: APIClient = self.base_fixtures["users"][0]["client"]
        record: record_models.EncryptedRecord = self.record_fixtures["records"][0][
            "record"
        ]

        response: Response = client.get(
            "/api/records/e_record/" + str(record.id) + "/",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(200, response.status_code)

    def test_patch_encrypted_record(self):
        private_key: bytes = self.base_fixtures["users"][0]["private"]
        client: APIClient = self.base_fixtures["users"][0]["client"]
        user: api_models.UserProfile = self.base_fixtures["users"][0]["user"]

        all_record_tags = list(record_models.RecordTag.objects.all())
        record_note = "important record note fpr record AZ 0011/123"
        record_token = "AZ 0011/123"
        origin_country = record_models.OriginCountry.objects.first()
        tag_ids = [all_record_tags[0].id, all_record_tags[1].id]
        new_record_object = {
            "client_birthday": "2000-06-12",
            "client_name": "Bruce Wayne",
            "client_note": "",
            "client_phone_number": "12312312",
            "consultants": [
                self.base_fixtures["users"][0]["user"].id,
                self.base_fixtures["users"][1]["user"].id,
            ],
            "first_contact_date": "2020-04-14",
            "origin_country": origin_country.id,
            "record_note": record_note,
            "record_token": record_token,
            "tags": tag_ids,
            "note": record_note,
        }
        response: Response = client.post(
            "/api/records/e_record/",
            new_record_object,
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )

        self.assertEqual(201, response.status_code)
        new_record_from_db: record_models.EncryptedRecord = record_models.EncryptedRecord.objects.get(
            pk=response.data["id"]
        )
        record_key = new_record_from_db.get_decryption_key(user, private_key)
        self.assertEqual(
            record_note, AESEncryption.decrypt(new_record_from_db.note, record_key)
        )

        response: Response = client.patch(
            "/api/records/e_record/" + str(new_record_from_db.id) + "/",
            {
                "record": {
                    "note": "new note",
                    "circumstances": "nothing new to tell",
                    "tagged": [all_record_tags[2].id, all_record_tags[3].id],
                }
            },
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(200, response.status_code)

        new_record_from_db: record_models.EncryptedRecord = record_models.EncryptedRecord.objects.get(
            pk=response.data["record"]["id"]
        )
        self.assertEqual(
            "new note", AESEncryption.decrypt(new_record_from_db.note, record_key)
        )

        response_record_tagged_ids = [
            tag["id"] for tag in response.data["record"]["tagged"]
        ]
        self.assertIn(all_record_tags[2].id, response_record_tagged_ids)
        self.assertIn(all_record_tags[3].id, response_record_tagged_ids)

        # TODO: client stuff

    def test_patch_encrypted_record_error(self):
        private_key: bytes = self.base_fixtures["users"][0]["private"]
        client: APIClient = self.base_fixtures["users"][0]["client"]

        response: Response = client.patch(
            "/api/records/e_record/" + str(123123) + "/",
            {"record": {"note": "new note"}, "client": {}},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)

        record: record_models.EncryptedRecord = self.record_fixtures["records"][0][
            "record"
        ]
        response: Response = client.patch(
            "/api/records/e_record/" + str(record.id) + "/",
            {"record": {"tagged": [40001],}},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)

        response: Response = client.patch(
            "/api/records/e_record/" + str(record.id) + "/",
            {"record": {"some_random_property": "value"}},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)

        response: Response = client.patch(
            "/api/records/e_record/" + str(record.id) + "/",
            {"record": {"tagged": []}},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)

    def test_record_model_patching(self):
        pass
        # test record_model.patch
