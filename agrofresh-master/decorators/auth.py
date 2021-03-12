from asgiref.sync import sync_to_async
from django.conf import settings
from django.urls import resolve
from django.contrib.auth import REDIRECT_FIELD_NAME, PermissionDenied
from django.contrib.auth.decorators import user_passes_test
import functools
import inspect


# A django.contrib.auth.decorators replacement to support both async & sync views
#


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def redirect_to_login(request):
        path = request.build_absolute_uri()
        resolved_login_url = resolve(login_url or settings.LOGIN_URL)
        # If the login url is the same scheme and net location then just
        # use the path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if ((not login_scheme or login_scheme == current_scheme) and
            (not login_netloc or login_netloc == current_netloc)):
            path = request.get_full_path()

        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(path, resolved_login_url, redirect_field_name)

    def decorator(view_func):
        if inspect.iscoroutinefunction(view_func):
            @functools.wraps(view_func)
            async def _wrapped_async_view(request, *args, **kwargs):
                if not inspect.iscoroutinefunction(test_func):
                    test_result = await sync_to_async(test_func)(request.user)
                else:
                    test_result = await test_func(request.user)

                if test_result:
                    return await view_func(request, *args, **kwargs)
                return redirect_to_login(request)

            return _wrapped_async_view

        else:
            @functools.wraps(view_func)
            def _wrapped_sync_view(request, *args, **kwargs):
                if test_func(request.user):
                    return view_func(request, *args, **kwargs)
                return redirect_to_login(request)

            return _wrapped_sync_view

    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(perm, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        # First check if the user has the permission (even anon users)
        if user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)


# A django.contrib.admin.views.decorators replacement to support both async & sync views
#


def staff_member_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                          login_url='admin:login'):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
