from typing import Any, Callable, Dict, List, Literal, Optional, Type

from django.http import HttpRequest, JsonResponse
from django.urls import path
from pydantic import BaseConfig, BaseModel, ValidationError, create_model

from apps.core.models import UserProfile
from apps.static.service_layer import ServiceResult


class RFC7807(BaseModel):
    type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    internal: Optional[Any] = None
    param_errors: Optional[Dict[str, List[str]]] = None


class Config(BaseConfig):
    orm_mode = True


def validation_error_handler(validation_error: ValidationError) -> RFC7807:
    field_errors: Dict[str, List[str]] = {}
    for error in validation_error.errors():
        if len(error["loc"]) == 1:
            name = str(error["loc"][0])
            if name in field_errors:
                field_errors[name].append(error["msg"])
            else:
                field_errors[name] = [error["msg"]]

    form_error = {"non_field_errors": [], "field_errors": field_errors}
    return RFC7807(
        detail=form_error,
        status=422,
        type="RequestValidationError",
        title="Malformed Request",
        internal=validation_error.errors(),
    )


def validate(request: HttpRequest, schema: Type[BaseModel]):
    data: Dict[str, Any] = {}
    data.update(request.POST)
    data.update(request.GET)
    if request.resolver_match is not None:
        data.update(request.resolver_match.kwargs)
    return schema(**data)


class ErrorResponse(JsonResponse):
    def __init__(
        self,
        type: str,
        title: str,
        status: int,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        internal: Optional[Any] = None,
        param_errors: Optional[Dict[str, List[str]]] = None,
    ):
        error = RFC7807(
            type=type,
            title=title,
            status=status,
            detail=detail or title,
            instance=instance,
            internal=internal,
            param_errors=param_errors,
        )
        super().__init__(data=error.dict(), status=error.status)


class Router:
    def __init__(self):
        self.__routes = []

    @staticmethod
    def generate_view_func(method_route: Dict) -> Callable[..., JsonResponse]:
        def decorator(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            if request.method in method_route:
                return method_route[request.method]["view"](request, *args, **kwargs)
            else:
                return ErrorResponse(
                    title="Method Not Allowed", status=405, type="MethodNotAllowed"
                )

        return decorator

    @property
    def urls(self):
        urls = {}

        for route in self.__routes:
            if route["url"] in urls:
                if route["method"] in urls[route["url"]]:
                    raise ValueError("The same url and method must not exist.")
                else:
                    urls[route["url"]][route["method"]] = route
            else:
                urls[route["url"]] = {route["method"]: route}

        ret = []
        for url, method_route in urls.items():
            for method, route in method_route.items():
                if len(method_route) > 1:
                    view = Router.generate_view_func(method_route)
                    ret.append(path(url, view))
                else:
                    ret.append(path(url, route["view"]))

        return ret

    @staticmethod
    def generate_view(
        func: Callable[..., ServiceResult],
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ) -> Callable:
        def wrapper(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            # set up input
            func_kwargs: Dict[str, Any] = {}
            func_input = func.__code__.co_varnames

            # handle auth
            if auth:
                if not request.user.is_authenticated:
                    return ErrorResponse(
                        type="NotAuthenticated",
                        title="Login Required",
                        detail="You need to be logged in.",
                        status=401,
                    )

                user: UserProfile = request.user  # type: ignore

                if "user" in func_input:
                    func_kwargs["user"] = user

                if "rlc_user" in func_input:
                    if not hasattr(user, "rlc_user"):
                        return ErrorResponse(
                            type="RoleRequired",
                            title="Rlc User Required",
                            detail="You need to have the rlc user role.",
                            status=403,
                        )

                    func_kwargs["rlc_user"] = user.rlc_user

                if "private_key_user" in func_input:
                    func_kwargs["private_key_user"] = user.get_private_key(
                        request=request
                    )

                if "statistics_user" in func_input:
                    if not hasattr(user, "statistic_user"):
                        return ErrorResponse(
                            type="RoleRequired",
                            title="Statistics User Required",
                            detail="You need to have the statistics user role.",
                            status=403,
                        )

                    func_kwargs["statistics_user"] = user.statistic_user

            # validate the input
            if input_schema:
                try:
                    data = validate(request, input_schema)
                except ValidationError as e:
                    return ErrorResponse(**validation_error_handler(e).dict())

                if "data" in func_input:
                    func_kwargs["data"] = data

            # service layer next step
            result: ServiceResult = func(**func_kwargs)

            # log service layer
            # if auth:
            #     log_message = result.message.format(request.user.email)
            # else:
            #     log_message = result.message
            # TODO: log

            # error handling
            if not result.success:
                if error_dict and result.message in error_dict:
                    return error_dict[result.message]
                return ErrorResponse(
                    title=result.value, status=400, type="ServiceError"
                )

            # validate the output
            if output_schema:
                model = create_model(
                    "Output",
                    root=(output_schema, ...),
                )
                try:
                    output_data = model(root=result.value)
                except ValidationError as e:
                    return ErrorResponse(
                        type="OutputError",
                        title="Server Error",
                        internal=e.errors(),
                        status=500,
                    )
                return JsonResponse(output_data.dict()["root"], safe=False)

            # default
            return JsonResponse({})

        return wrapper

    def get(
        self,
        url: str = "",
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "GET", input_schema, output_schema, auth, error_dict)

    def post(
        self,
        url: str = "",
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "POST", input_schema, output_schema, auth, error_dict)

    def put(
        self,
        url: str = "",
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "PUT", input_schema, output_schema, auth, error_dict)

    def delete(
        self,
        url: str = "",
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        return self.api(url, "DELETE", input_schema, output_schema, auth, error_dict)

    def api(
        self,
        url: str = "",
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type] = None,
        auth=False,
        error_dict: Optional[Dict[str, ErrorResponse]] = None,
    ):
        def decorator(func: Callable[..., ServiceResult]):
            view = Router.generate_view(
                func, input_schema, output_schema, auth, error_dict
            )
            self.__routes.append({"url": url, "method": method, "view": view})

        return decorator
