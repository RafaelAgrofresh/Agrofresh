import functools
import inspect

def catch(catch_func):
    assert inspect.isfunction(catch_func)
    def decorator(func):
        assert inspect.isfunction(func)
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    catch_func(e)
            return async_wrapper

        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    catch_func(e)
            return wrapper

    return decorator
