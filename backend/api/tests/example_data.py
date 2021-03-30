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
from backend.api.models.group import Group
from backend.api.models.has_permission import HasPermission
from backend.api.models.permission import Permission
from backend.api.models.rlc import Rlc
from backend.collab.models import CollabPermission
from backend.collab.static.collab_permissions import get_all_collab_permission_strings
from backend.files.models import FolderPermission
from backend.recordmanagement.models import OriginCountry
from backend.recordmanagement.models.encrypted_client import EncryptedClient
from backend.recordmanagement.models.encrypted_record import EncryptedRecord
from backend.recordmanagement.models.encrypted_record_document import (
    EncryptedRecordDocument,
)
from backend.recordmanagement.models.encrypted_record_message import (
    EncryptedRecordMessage,
)
from backend.recordmanagement.models.record_document_tag import RecordDocumentTag
from backend.recordmanagement.models.record_encryption import RecordEncryption
from backend.recordmanagement.models.record_tag import RecordTag
from backend.static import permissions
from backend.static.encryption import AESEncryption
from backend.static.permissions import get_all_permissions_strings
from backend.api.models import RlcSettings, UserProfile
from random import randint, choice
from staticfiles.folder_permissions import get_all_folder_permissions_strings


# helpers


def add_permissions_to_group(group: Group, permission_name):
    HasPermission.objects.create(
        group_has_permission=group,
        permission_for_rlc=group.from_rlc,
        permission=Permission.objects.get(name=permission_name),
    )


# create
def create_rlc():
    rlc = Rlc.objects.create(
        name="Dummy RLC",
        note="This is a dummy rlc, just for showing how the system works.",
        id=3033,
    )
    RlcSettings.objects.create(rlc=rlc)
    return rlc


def create_fixtures():
    # create countries
    countries = ["Abchasien", "Afghanistan", "Ägypten", "Albanien", "Algerien"]
    [OriginCountry.objects.create(name=country) for country in countries]

    # create permissions
    [
        Permission.objects.get_or_create(name=permission)
        for permission in get_all_permissions_strings()
    ]

    # create record tags
    tags = [
        "Familiennachzug",
        "Dublin IV",
        "Arbeitserlaubnis",
        "Flüchtlingseigenschaft",
        "subsidiärer Schutz",
        "Eheschließung",
        "Verlobung",
    ]
    [RecordTag.objects.create(name=tag) for tag in tags]

    # create record document tags
    tags = ["Official Document", "Pleading", "Proof", "Passport"]
    [RecordDocumentTag.objects.create(name=tag) for tag in tags]

    # create collab permissions
    [
        CollabPermission.objects.get_or_create(name=permission)
        for permission in get_all_collab_permission_strings()
    ]
    # create folder permissions
    [
        FolderPermission.objects.get_or_create(name=permission)
        for permission in get_all_folder_permissions_strings()
    ]


def create_users(rlc):
    users = [
        (
            "ludwig.maximilian@outlook.de",
            "Ludwig Maximilian",
            "1985-05-12",
            "01732421123",
            "Maximilianstrasse 12",
            "München",
            "80539",
        ),
        (
            "xxALIxxstone@hotmail.com",
            "Albert Einstein",
            "1879-3-14",
            "01763425656",
            "Blumengasse 23",
            "Hamburg",
            "83452",
        ),
        (
            "mariecurry53@hotmail.com",
            "Marie Curie",
            "1867-11-7",
            "0174565656",
            "Jungfernstieg 2",
            "Hamburg",
            "34264",
        ),
        (
            "max.mustermann@gmail.com",
            "Maximilian Gustav Mustermann",
            "1997-10-23",
            "0176349756",
            "Schlossallee 100",
            "Grünwald",
            "82031",
        ),
        (
            "petergustav@gmail.com",
            "Peter Klaus Gustav von Guttenberg",
            "1995-3-11",
            "01763423732",
            "Leopoldstrasse 31",
            "Muenchen",
            "80238",
        ),
        (
            "gabi92@hotmail.com",
            "Gabriele Schwarz",
            "1998-12-10",
            "0175647332",
            "Kartoffelweg 12",
            "Muenchen",
            "80238",
        ),
        (
            "rudi343@gmail.com",
            "Rudolf Mayer",
            "1996-5-23",
            "01534423732",
            "Barerstrasse 3",
            "Muenchen",
            "80238",
        ),
        (
            "lea.g@gmx.com",
            "Lea Glas",
            "1985-7-11",
            "01763222732",
            "Argentinische Allee 34",
            "Hamburg",
            "34264",
        ),
        (
            "butterkeks@gmail.com",
            "Bettina Rupprecht",
            "1995-10-11",
            "01765673732",
            "Ordensmeisterstrasse 56",
            "Hamburg",
            "34264",
        ),
        (
            "willi.B@web.de",
            "Willi Birne",
            "1997-6-15",
            "01763425555",
            "Grunewaldstrasse 45",
            "Hamburg",
            "34264",
        ),
        (
            "pippi.langstrumpf@gmail.com",
            "Pippi Langstumpf",
            "1981-7-22",
            "01766767732",
            "Muehlenstraße 12",
            "Muenchen",
            "80238",
        ),
    ]

    created_users = []
    for user in users:
        created_users.append(
            UserProfile.objects.create(
                email=user[0],
                name=user[1],
                phone_number=user[3],
                street=user[4],
                city=user[5],
                postal_code=user[6],
                birthday=user[2],
                rlc=rlc,
                is_active=True,
            )
        )
    return created_users


def create_dummy_users(rlc: Rlc, dummy_password: str = "qwe123") -> [UserProfile]:
    users = []

    # main user
    user = UserProfile.objects.create(
        name="Mr Dummy",
        email="dummy@rlcm.de",
        phone_number="01666666666",
        street="Dummyweg 12",
        city="Dummycity",
        postal_code="00000",
        rlc=rlc,
        birthday="1995-1-1",
        is_superuser=True,
        is_staff=True,
        is_active=True,
    )
    user.set_password(dummy_password)
    user.save()
    users.append(user)

    # other dummy users
    user = UserProfile.objects.create(
        name="Tester 1",
        email="tester1@law-orga.de",
        phone_number="123812382",
        rlc=rlc,
        is_active=True,
    )
    user.set_password("qwe123")
    user.save()
    users.append(user)

    user = UserProfile.objects.create(
        name="Tester 2",
        email="tester2@law-orga.de",
        phone_number="123812383",
        rlc=rlc,
        is_active=True,
    )
    user.set_password("qwe123")
    user.save()
    users.append(user)

    # return
    return users


def create_inactive_user(rlc):
    user = UserProfile(
        name="Mr. Inactive",
        email="inactive@rlcm.de",
        phone_number="1293283882",
        street="Inaktive Strasse",
        city="InAktiv",
        postal_code="29292",
        rlc=rlc,
        birthday="1950-1-1",
    )
    user.set_password("qwe123")
    user.is_active = False
    user.save()


def create_groups(rlc: Rlc, creator: UserProfile, users: [UserProfile]):
    # create users group
    users_group = Group.objects.create(
        creator=creator,
        from_rlc=rlc,
        name="Berater",
        visible=False,
        description="all users",
        note="only add users",
    )

    for i in range(0, randint(0, len(users))):
        users_group.group_members.add(users[i])

    add_permissions_to_group(users_group, permissions.PERMISSION_CAN_CONSULT)
    add_permissions_to_group(users_group, permissions.PERMISSION_VIEW_RECORDS_RLC)

    # create ag group
    ag_group = Group.objects.create(
        creator=users[0],
        from_rlc=rlc,
        name="AG Datenschutz",
        visible=True,
        description="DSGVO",
        note="bitte mithelfen",
    )

    for i in range(0, randint(0, int(len(users) / 2))):
        ag_group.group_members.add(users[i])

    # return
    return [users_group, ag_group]


def create_admin_group(rlc: Rlc, main_user: UserProfile):
    # create admin group
    admin_group = Group.objects.create(
        creator=main_user,
        from_rlc=rlc,
        name="Administratoren",
        visible=False,
        description="haben alle Berechtigungen",
        note="IT ressort",
    )
    admin_group.group_members.add(main_user)

    add_permissions_to_group(admin_group, permissions.PERMISSION_VIEW_PERMISSIONS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_MANAGE_PERMISSIONS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_MANAGE_GROUPS_RLC)
    add_permissions_to_group(admin_group, permissions.PERMISSION_ACCEPT_NEW_USERS_RLC)
    add_permissions_to_group(
        admin_group, permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
    )
    add_permissions_to_group(
        admin_group, permissions.PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC
    )
    add_permissions_to_group(admin_group, permissions.PERMISSION_VIEW_RECORDS_RLC)

    # return
    return admin_group


def create_clients(rlc: Rlc) -> [EncryptedClient]:
    origin_countries = OriginCountry.objects.all()
    clients = [
        (
            "2018-7-12",  # created_on
            "2018-8-28T21:3:0",  # last_edited
            "Bibi Aisha",  # name
            "auf Flucht von Ehemann getrennt worden",  # note
            "01793456542",  # phone number
            "1990-5-1",  # birthday
            choice(origin_countries),  # origin country id
        ),
        (
            (2017, 3, 17),
            "2017-12-24T12:2:0",
            "Mustafa Kubi",
            "möchte eine Ausbildung beginnen",
            None,
            "1998-12-3",
            choice(origin_countries),
        ),
        (
            "2018-1-1",
            "2018-3-3T14:5:0",
            "Ali Baba",
            "fragt wie er seine deutsche Freundin heiraten kann",
            "",
            "1985-6-27",
            choice(origin_countries),
        ),
        (
            "2018-8-1",
            "2018-8-2T16:3:0",
            "Kamila Iman",
            "möchte zu ihrer Schwester in eine andere Aufnahmeeinrichtung ziehen",
            "01562736778",
            "1956-4-3",
            choice(origin_countries),
        ),
        (
            "2017-9-10",
            "2017-10-2T15:3:0",
            "Junis Haddad",
            "Informationen zum Asylverfahren",
            "013345736778",
            "1998-6-2",
            choice(origin_countries),
        ),
        (
            "2017-9-10",
            "2018-9-2T16:3:0",
            "Nael Mousa",
            "Informationen zum Asylverfahren",
            "01444436778",
            "1997-6-4",
            choice(origin_countries),
        ),
        (
            "2017-9-10",
            "2018-1-12T16:3:0",
            "Amir Hamdan",
            "Informationen zum Asylverfahren",
            "01457636778",
            "1996-6-8",
            choice(origin_countries),
        ),
        (
            "2017-9-10",
            "2018-1-2T16:3:0",
            "Amar Yousef",
            "Informationen zum Asylverfahren",
            "01566546778",
            "1995-5-10",
            choice(origin_countries),
        ),
        (
            "2017-9-10",
            "2017-12-2T16:3:0",
            "Tarek Habib",
            "Informationen zum Asylverfahren",
            "013564736778",
            "1994-5-12",
            choice(origin_countries),
        ),
        (
            "2017-9-10",
            "2018-10-2T16:3:0",
            "Kaya Yousif",
            "Informationen zum Asylverfahren",
            "01564586778",
            "1993-4-14",
            choice(origin_countries),
        ),
    ]
    created_clients = []

    for client in clients:
        created_client = EncryptedClient(
            name=client[2],
            from_rlc=rlc,
            created_on=client[0],
            last_edited=client[1],
            birthday=client[5],
            origin_country=client[6],
            note=client[3],
            phone_number=client[4],
        )
        created_client.encrypt(rlc.get_public_key())
        created_client.save()
        created_clients.append(created_client)

    return created_clients


def create_records(
    clients: [EncryptedClient], users: [UserProfile], rlc: Rlc
) -> [EncryptedRecord]:
    assert len(clients) > 9
    tags = RecordTag.objects.all()

    records = [
        (
            choice(users),  # creator id
            "2018-7-12",  # created
            "2018-8-29T13:54:0+00:00",  # last edited
            clients[0],  # client
            "2018-7-10",  # first contact
            "2018-8-14T17:30:0+00:00",  # last contact
            "AZ-123/18",  # record token
            "informationen zum asylrecht",
            "cl",  # status, cl wa op
            [choice(users), choice(users)],  # working on
            [choice(tags), choice(tags)],  # tags
        ),
        (
            choice(users),
            "2018-6-23",
            "2018-8-22T23:3:0+00:00",
            clients[1],
            "2018-6-20",
            "2018-7-10T17:30:0+00:00",
            "AZ-124/18",
            "nicht abgeschlossen",
            "op",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2018-8-24",
            "2018-8-31T1:2:0+00:00",
            clients[2],
            "2018-8-22",
            "2018-8-22T18:30:0+00:00",
            "AZ-125/18",
            "auf Bescheid wartend",
            "wa",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2018-3-10",
            "2018-4-30T19:22:0+00:00",
            clients[3],
            "2018-3-9",
            "2018-3-24T15:54:0+00:00",
            "AZ-126/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "cl",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2017-9-10",
            "2017-10-2T15:3:0+00:00",
            clients[4],
            "2017-9-10",
            "2017-10-2T15:3:0+00:00",
            "AZ-127/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "cl",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2017-9-10",
            "2018-9-2T16:3:0+00:00",
            clients[5],
            "2017-9-10",
            "2018-9-2T16:3:0+00:00",
            "AZ-128/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "wa",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2017-9-10",
            "2018-1-12T16:3:0+00:00",
            clients[6],
            "2017-9-10",
            "2018-1-12T16:3:0+00:00",
            "AZ-129/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "op",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2017-9-10",
            "2018-1-2T16:3:0+00:00",
            clients[7],
            "2017-9-10",
            "2018-1-2T16:3:0+00:00",
            "AZ-130/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "cl",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2017-9-10",
            "2018-12-2T16:3:0+00:00",
            clients[8],
            "2017-9-10",
            "2018-12-2T16:3:0+00:00",
            "AZ-131/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "wa",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2017-9-10",
            "2018-10-2T16:3:0+00:00",
            clients[9],
            "2017-9-10",
            "2018-10-2T16:3:0+00:00",
            "AZ-132/18",
            "Frau noch im Herkunftsland, gut recherchiert und ausfuehrlich dokumentiert",
            "op",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
        (
            choice(users),
            "2017-9-10",
            "2018-10-2T16:3:0+00:00",
            clients[0],
            "2017-9-10",
            "2018-10-2T16:3:0+00:00",
            "AZ-139/18",
            "zweite akte von client 0",
            "op",
            [choice(users), choice(users)],
            [choice(tags), choice(tags)],
        ),
    ]

    created_records = []
    for record in records:
        created_record = EncryptedRecord(
            from_rlc=rlc,
            creator=record[0],
            client=record[3],
            record_token=record[6],
            official_note=record[7],
            state=record[8],
            created_on=record[1],
            first_contact_date=record[4],
            last_edited=record[2],
            last_contact_date=record[5],
        )
        created_record.save()
        for user in record[9]:
            created_record.working_on_record.add(user)
        for tag in record[10]:
            created_record.tagged.add(tag)
        # secure the record
        aes_key = AESEncryption.generate_secure_key()
        users_with_permission = created_record.get_users_with_decryption_keys()
        for user in users_with_permission:
            record_encryption = RecordEncryption(
                user=user, record=created_record, encrypted_key=aes_key
            )
            record_encryption.encrypt(user.get_public_key())
            record_encryption.save()

        created_record.encrypt(aes_key=aes_key)
        created_record.save()
        created_records.append(created_record)
    return created_records


def create_informative_record(
    main_user: UserProfile,
    main_user_password: str,
    clients: [EncryptedClient],
    users: [UserProfile],
    rlc: Rlc,
) -> EncryptedRecord:
    tags = list(RecordTag.objects.all())
    document_tags = list(RecordDocumentTag.objects.all())
    users = [main_user] + users

    # create the informative record
    record = EncryptedRecord(
        from_rlc=rlc,
        creator=main_user,
        client=clients[0],
        record_token="AZ-001/18",
        official_note="best record ever",
        state="op",
        created_on="2018-1-3",
        first_contact_date="2018-1-3",
        last_edited="2019-3-11T9:32:21+00:00",
        last_contact_date="2019-2-28T17:33:0+00:00",
        first_consultation="2018-1-2T23:55:0+00:00",
    )
    record.save()

    # add encrypted data
    record.note = "Mandant moechte dass wir ihn vor Gericht vertreten. Das duerfen wir aber nicht. #RDG"
    record.consultant_team = "Taskforce 417"
    record.lawyer = "RA Guenther-Klaus, Kiesweg 3"
    record.related_persons = "Sozialarbeiter Apfel (Direkt in der Unterkunft)"
    record.contact = "Mail: asksk1@beispiel.de,\n Telefon: 0800 444 55 444"
    record.bamf_token = "QRS-232/2018"
    record.foreign_token = "Vor Gericht: FA93932-1320"
    record.first_correspondence = (
        "Hallo Liebes Team der RLC,\n ich habe folgendes Problem.\nKoennt ihr mir "
        "helfen?\n Vielen Dank"
    )
    record.circumstances = "Kam ueber die Balkanroute, Bruder auf dem Weg verloren, wenig Kontakt zu Familie."
    record.next_steps = "Klage einreichen und gewinnen!"
    record.status_described = "Auf Antwort wartend, anschliessend weitere Bearbeitung."
    record.additional_facts = "Hat noch nie ne Schweinshaxe gegessen."

    # add relations
    record_users = [choice(users), main_user]
    for user in record_users:
        record.working_on_record.add(user)
    for tag in [choice(tags), choice(tags)]:
        record.tagged.add(tag)

    # encrypt the record
    aes_key = AESEncryption.generate_secure_key()
    for user in record_users:
        record_encryption = RecordEncryption(
            user=user, record=record, encrypted_key=aes_key
        )
        record_encryption.encrypt(user.get_public_key())
        record_encryption.save()
    record.encrypt(aes_key=aes_key)
    record.save()

    # add some documents
    document1 = EncryptedRecordDocument.objects.create(
        name="7_1_19__pass.jpg",
        creator=main_user,
        record=record,
        file_size=18839,
        created_on="2019-1-7",
    )
    document1.tagged.add(choice(document_tags))
    document2 = EncryptedRecordDocument.objects.create(
        name="3_10_18__geburtsurkunde.pdf",
        creator=main_user,
        record=record,
        file_size=488383,
        created_on="2018-10-3",
    )
    document2.tagged.add(choice(document_tags))
    document3 = EncryptedRecordDocument.objects.create(
        name="3_12_18__Ablehnungbescheid.pdf",
        creator=main_user,
        record=record,
        file_size=343433,
        created_on="2018-12-3",
    )
    document3.tagged.add(choice(document_tags))
    document4 = EncryptedRecordDocument.objects.create(
        name="1_1_19__Klageschrift.docx",
        creator=main_user,
        record=record,
        file_size=444444,
        created_on="2019-1-1",
    )
    document4.save()

    # add some messages
    message1 = EncryptedRecordMessage(
        sender=main_user,
        record=record,
        created_on="2019-3-11T10:12:21+00:00",
        message="Bitte dringend die Kontaktdaten des Mandanten eintragen.",
    )
    message1.encrypt(main_user, main_user.get_private_key(main_user_password))
    message1.save()
    message2 = EncryptedRecordMessage(
        sender=choice(users),
        record=record,
        created_on="2019-3-12T9:32:21",
        message="Ist erledigt! Koennen wir uns morgen treffen um das zu besprechen?",
    )
    message2.encrypt(main_user, main_user.get_private_key(main_user_password))
    message2.save()
    message3 = EncryptedRecordMessage(
        sender=main_user,
        record=record,
        created_on="2019-3-12T14:7:21",
        message="Klar, einfach direkt in der Mittagspause in der Mensa.",
    )
    message3.encrypt(main_user, main_user.get_private_key(main_user_password))
    message3.save()
    message4 = EncryptedRecordMessage(
        sender=choice(users),
        record=record,
        created_on="2019-3-13T18:7:21",
        message="Gut, jetzt faellt mir aber auch nichts mehr ein.",
    )
    message4.encrypt(main_user, main_user.get_private_key(main_user_password))
    message4.save()

    # return
    return record


def create() -> None:
    dummy_password = "qwe123"
    # fixtures
    create_fixtures()
    # dummy
    rlc = create_rlc()
    dummy = create_dummy_users(rlc)[0]
    # data
    clients = create_clients(rlc)
    users = create_users(rlc)
    create_inactive_user(rlc)
    create_groups(rlc, dummy, users)
    create_admin_group(rlc, dummy)
    create_records(clients, users, rlc)
    create_informative_record(dummy, dummy_password, clients, users, rlc)
