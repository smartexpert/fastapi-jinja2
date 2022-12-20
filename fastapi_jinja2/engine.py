import inspect
import os
from functools import wraps
from typing import Any, Optional, Union, Callable
import typing

import fastapi
from fastapi.templating import Jinja2Templates #from chameleon import PageTemplateLoader, PageTemplate

from fastapi_jinja2.exceptions import FastAPIJinja2Exception, FastAPIJinja2NotFoundException

from starlette.datastructures import URL

__templates: Optional[Any] = None
template_path: Optional[str] = None

try:
    import jinja2

    # @contextfunction renamed to @pass_context in Jinja 3.0, to be removed in 3.1
    if hasattr(jinja2, "pass_context"):
        pass_context = jinja2.pass_context
    else:  # pragma: nocover
        pass_context = jinja2.contextfunction
except ImportError:  # pragma: nocover
    jinja2 = None  # type: ignore

def global_init(template_folder: str = "templates", auto_reload=False, cache_init=True,default_prefix_https=False):
    global __templates, template_path

    if __templates and cache_init:
        return

    if not template_folder:
        msg = f'The template_folder must be specified.'
        raise FastAPIJinja2Exception(msg)

    if not os.path.isdir(template_folder):
        msg = f"The specified template folder must be a folder, it's not: {template_folder}"
        raise FastAPIJinja2Exception(msg)

    template_path = template_folder
    __templates = Jinja2Templates(directory=template_folder)

    if default_prefix_https:
        @pass_context
        def https_url_for(context: dict, name: str, **path_params: typing.Any) -> str:
            request = context["request"]
            http_url = request.url_for(name, **path_params)            
            # Replace 'http' with 'https'
            return http_url.replace("http", "https", 1)
        __templates.env.globals["url_for"] = https_url_for
    
    __templates.env.globals["URL"] = URL


def clear():
    global __templates, template_path
    __templates = None
    template_path = None


def render(template_file: str, **template_data: dict) -> str:
    if not __templates:
        raise FastAPIJinja2Exception("You must call global_init() before rendering templates.")
    print("template_data:",template_data)
    #page: PageTemplate = __templates[template_file]
    #return page.render(encoding='utf-8', **template_data)
    return __templates.TemplateResponse(template_file,template_data)


def response(template_file: str, mimetype='text/html', status_code=200, **template_data) -> fastapi.Response:
    html = render(template_file, **template_data)
    return fastapi.Response(content=html, media_type=mimetype, status_code=status_code)


def template(template_file: Optional[Union[Callable, str]] = None, mimetype: str = 'text/html', is_fragment=False):
    """
    Decorate a FastAPI view method to render an HTML response.

    :param str template_file: Optional, the Chameleon template file (path relative to template folder, *.jinja).
    :param str mimetype: The mimetype response (defaults to text/html).
    :return: Decorator to be consumed by FastAPI
    """

    wrapped_function = None
    if callable(template_file):
        wrapped_function = template_file
        template_file = None

    def response_inner(f):
        nonlocal template_file
        global template_path

        if not template_path:
            template_path = 'templates'
            # raise FastAPIJinja2Exception("Cannot continue: fastapi_chameleon.global_init() has not been called.")

        if not template_file:
            # Use the default naming scheme: template_folder/module_name/function_name.jinja
            module = f.__module__
            if '.' in module:
                module = module.split('.')[-1]
            view = f.__name__
            template_file = f'{module}/{view}.html' if is_fragment == False else f'{module}/fragments/{view}.html'

            if not os.path.exists(os.path.join(template_path, template_file)):
                template_file = f'{module}/{view}.jinja' if is_fragment == False else f'{module}/fragments/{view}.jinja'

        @wraps(f)
        def sync_view_method(*args, **kwargs):
            try:
                response_val = f(*args, **kwargs)
                if type(response_val) == dict:
                    response_val['request'] = __get_request(*args, **kwargs) #kwargs['request']
                    return __render_response(template_file, response_val, mimetype)
                else:
                    return response_val
            except FastAPIJinja2NotFoundException as nfe:
                return __render_response(nfe.template_file, {}, 'text/html', 404)

        @wraps(f)
        async def async_view_method(*args, **kwargs):
            try:
                response_val = await f(*args, **kwargs)
                if type(response_val) == dict:
                    response_val['request'] = __get_request(*args, **kwargs) #kwargs['request']
                    #Enable for debugging
                    # print("Args",args)
                    # print("Kwords",kwargs)
                    return __render_response(template_file, response_val, mimetype)
                else:
                    return response_val
            except FastAPIJinja2NotFoundException as nfe:
                return __render_response(nfe.template_file, {}, 'text/html', 404)

        if inspect.iscoroutinefunction(f):
            return async_view_method
        else:
            return sync_view_method

    return response_inner(wrapped_function) if wrapped_function else response_inner


def __render_response(template_file, response_val, mimetype, status_code: int = 200) -> fastapi.Response:
    # source skip: assign-if-exp
    if isinstance(response_val, fastapi.Response):
        return response_val

    if template_file and not isinstance(response_val, dict):
        msg = f"Invalid return type {type(response_val)}, we expected a dict or fastapi.Response as the return value."
        raise FastAPIJinja2Exception(msg)

    model = response_val
    #html = render(template_file, **model)
    #return fastapi.Response(content=html, media_type=mimetype, status_code=status_code)
    return __templates.TemplateResponse(template_file,model)


def not_found(four04template_file: str = 'errors/404.jinja'):
    msg = 'The URL resulted in a 404 response.'

    if four04template_file and four04template_file.strip():
        raise FastAPIJinja2NotFoundException(msg, four04template_file)
    else:
        raise FastAPIJinja2NotFoundException(msg)

def __get_request(*args, **kwargs):
    for arg in args:
        if isinstance(arg, fastapi.Request):
            return arg
    for kwarg in kwargs:
        if isinstance(kwargs[kwarg], fastapi.Request):
            return kwargs[kwarg]
    print(args)
    print(kwargs)    

    raise FastAPIJinja2Exception("No FastAPI.Request object passed from Path Operation Function. Include a parameter 'request: Request' in the Path Operation Function")
    return kwargs.get('request', None)

def fragment(*args, **kwargs):
    response_val = template(*args, is_fragment=True, **kwargs)
    return response_val