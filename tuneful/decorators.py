import json
from functools import wraps

from flask import request, Response

def accept(mimetype):
    def decorator(func):
        """
        Decorator which returns a 406 Not Acceptable if the client won't accept 
        a certain mimetype
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "application/json" in request.accept_mimetypes:
                return func(*args, **kwargs)
            message = "Request must accept {} data".format(mimetype)
            data = json.dumps({"message": message})
            return Response(data, 406, mimetype="application/json")
        return wrapper
    return decorator

def require(mimetype):
    def decorator(func):
        """
        Decorator which returns a 415 Unsupported Media Type if the client sends
        something other than a certain mimetype
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if (request.mimetype ==  mimetype):
                return func(*args, **kwargs)
            message = "Request must contain {} data".format(mimetype)
            data = json.dumps({"message": message})
            return Response(data, 415, mimetype="application/json")
        return wrapper
    return decorator

def existence():
    def decorator(func):
        """
        Decorator which will check for an entity's existence against a model's
        table and return a 404 if it does not exist
        """
        @wraps(func)
        def wrapper(id, item):
            item = session.query(table).get(id)

            if not item:
                message = "{} does not exist and cannot be deleted".format(id)
                data = json.dumps({"message": message})
                return Response(data, 404, mimetype="application/json")
            return func(id, item)
        return wrapper
    return decorator



