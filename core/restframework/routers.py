from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import Route
from rest_framework.routers import SimpleRouter
from rest_framework.routers import escape_curly_brackets


def get_router_class():
    return DefaultRouter if settings.DEBUG else SimpleRouter


def get_router():
    return get_router_class()()


BaseRouter = get_router_class()


class URLForceHyphenRouter(BaseRouter):
    def _get_dynamic_route(self, route, action):
        initkwargs = route.initkwargs.copy()
        initkwargs.update(action.kwargs)

        url_path = escape_curly_brackets(action.url_path)
        url_path = url_path.replace("_", "-")

        return Route(
            url=route.url.replace("{url_path}", url_path),
            mapping=action.mapping,
            name=route.name.replace("{url_name}", action.url_name),
            detail=route.detail,
            initkwargs=initkwargs,
        )
