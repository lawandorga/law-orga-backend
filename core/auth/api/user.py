import json
from json import JSONDecodeError

from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse

from core.auth.models import UserProfile
from core.seedwork.api_layer import ErrorResponse


def command__login(request):
    error = ErrorResponse(
        param_errors={"general": ["E-Mail or password wrong."]},
        status=422,
        err_type="ApiError",
        title="Wrong Combination",
    )

    try:
        body = json.loads(request.body)
        assert "email" in body and "password" in body
    except (JSONDecodeError, AssertionError):
        return error

    try:
        user = UserProfile.objects.get(email=body["email"])
    except ObjectDoesNotExist:
        return error

    if not user.check_password(body["password"]):
        return error

    # check if user active and user accepted in rlc
    if not user.rlc_user.email_confirmed:
        message = "You can not login, yet. Please confirm your email first."
        return JsonResponse({"non_field_errors": [message]}, status=400)

    if not user.rlc_user.is_active:
        message = (
            "You can not login. Your account was deactivated by one of your admins."
        )
        return JsonResponse({"non_field_errors": [message]}, status=400)

    if not user.rlc_user.accepted:
        message = "You can not login, yet. You need to be accepted as member by one of your admins."
        return JsonResponse({"non_field_errors": [message]}, status=400)

    # login
    login(request, user)

    # set private key
    if hasattr(user, "rlc_user"):
        request.session["private_key"] = user.rlc_user.get_private_key(
            password_user=body["password"]
        )

    # return
    return HttpResponse()


def command__logout(request):
    logout(request)

    return HttpResponse()
