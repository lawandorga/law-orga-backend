#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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
from rest_framework.views import APIView
from rest_framework.response import Response
import os

from backend.static.emails import EmailSender
from ..models.rlc import Rlc
from ..serializers.rlc import RlcOnlyNameSerializer
from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__EMAIL__NO_EMAIL_PROVIDED


class SendEmailViewSet(APIView):
    def post(self, request):
        if "email" in request.data:
            email = request.data["email"]
        else:
            raise CustomError(ERROR__API__EMAIL__NO_EMAIL_PROVIDED)
        # EmailSender.send_email_notification([email], 'SYSTEM NOTIFICATION', 'There was a change')
        EmailSender.test_send(email)
        return Response()


class GetRlcsViewSet(APIView):
    authentication_classes = ()
    # TODO: why is everybody allowed?
    permission_classes = ()

    def get(self, request):
        # TODO: what is this? why exclude?
        if "ON_HEROKU" in os.environ and "ON_DEPLOY" in os.environ:
            rlcs = Rlc.objects.all().exclude(name="Dummy RLC").order_by("name")
        else:
            rlcs = Rlc.objects.all().order_by("name")
        # TODO: why not return a json response? turn a list into a json list like: return json.dumps([1,2,3])
        serialized = RlcOnlyNameSerializer(rlcs, many=True).data
        return Response(serialized)
