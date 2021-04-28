from functools import wraps
from typing import Any, Tuple, Union, TypeVar, Callable
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError
from enum import Enum
from chalice import Response

class status(tuple, Enum):   
    success = "SUCCESS", 1000, 200
    failure = "FAILURE", 1005, 500
    invalid = "INVALID", 1100, 500
    unauth = 'NOT AUTHORISED', 1400, 403
    error = "ERROR", 1500, 500

class CustomResponse:
    @staticmethod
    def responseFormat1(result : Union[list, str, dict], status) -> Tuple[Any, int]:
        return Response(body={'result' : result, 'status' : status[0], 'status_code' : status[1]},
                        status_code=status[2],
                        headers={'Content-Type': 'application/json'})
    
    @staticmethod
    def responseFormat2(result : Union[list, str], type : str, status) -> Tuple[Any, int]:
        return Response(body={'status' : status[0], 'result' : result, 'newuser' : type,'status_code' : status[1]},
                        status_code=status[2],
                        headers={'Content-Type': 'application/json'})


# For Type hinting
F = TypeVar('F', bound=Callable[..., Any])


class Utils:

    @staticmethod
    def getParams(request, params : tuple) -> Callable[[F], F]:
        def decorated(f : F) -> F:
            @wraps(f)
            def wrapper(*args, **kwargs) -> Tuple[Any, int]:
                try:
                    data = {i : request.query_params.get(i) for i in params}
                    if None in data.values():
                        return CustomResponse.responseFormat1("Please include all valid parameters", status.invalid)
                    return f(data, *args, **kwargs)
                except Exception as e:
                    return CustomResponse.responseFormat1(str(e), status.error)
            return wrapper

        return decorated
    
    @staticmethod
    def getBody(request, elements : dict) -> Callable[[F], F]:       
        def decorated(f : F) -> F:
            @wraps(f)
            def wrapper(*args, **kwargs) -> Tuple[Any, int]:
                try:
                    received = request.json_body
                    if received:
                        if sorted(received.keys()) == sorted(elements.keys()):
                            for i, j in received.items():
                                if type(j) not in elements[i]:
                                    return CustomResponse.responseFormat1("Datatypes not valid", status.invalid)
                            return f(received, *args, **kwargs)
                        return CustomResponse.responseFormat1("Please include all valid key value pairs", status.invalid)
                    return CustomResponse.responseFormat1("Please include body", status.invalid)
                except Exception as e:
                    return CustomResponse.responseFormat1(str(e), status.error)
            return wrapper

        return decorated

    @staticmethod
    def isUserWithArgsPOST(request, nosql, secret, elements : dict):      
        def decorated(f):
            @wraps(f)
            @Utils.getBody(request, elements)
            def wrapper(body, *args, **kwargs):
                try:
                    token = request.headers['Authorization']
                except KeyError:
                    return CustomResponse.responseFormat1("No token", status.unauth)
                else:
                    try:
                        data = jwt.decode(token, secret, algorithms=['HS256'])
                    except DecodeError:
                        return CustomResponse.responseFormat1("Token Decode Error", status.unauth)
                    except ExpiredSignatureError:
                        return CustomResponse.responseFormat1("Expired Token", status.unauth)
                    else:
                        if nosql.check(data['username']):
                            if nosql.getValue(data['username'] + '_token') == token:
                                return f(data['username'], body, *args, **kwargs)
                            return CustomResponse.responseFormat1("Old Token", status.unauth)
                        return CustomResponse.responseFormat1("Invalid User", status.unauth)
                    return CustomResponse.responseFormat1("No token", status.unauth)
            return wrapper
        return decorated
    
    @staticmethod
    def isUserWithArgsGET(request, nosql, secret, params : dict):      
        def decorated(f):
            @wraps(f)
            @Utils.getParams(request, params)
            def wrapper(params, *args, **kwargs):
                try:
                    token = request.headers['Authorization']
                except KeyError:
                    return CustomResponse.responseFormat1("No token", status.unauth)
                else:
                    try:
                        data = jwt.decode(token, secret, algorithms=['HS256'])
                    except DecodeError:
                        return CustomResponse.responseFormat1("Token Decode Error", status.unauth)
                    except ExpiredSignatureError:
                        return CustomResponse.responseFormat1("Expired Token", status.unauth)
                    else:
                        if nosql.check(data['username']):
                            if nosql.getValue(data['username'] + '_token') == token:
                                return f(data['username'], params, *args, **kwargs)
                            return CustomResponse.responseFormat1("Old Token", status.unauth)
                        return CustomResponse.responseFormat1("Invalid User", status.unauth)
                    return CustomResponse.responseFormat1("No token", status.unauth)
            return wrapper
        return decorated
    
    @staticmethod
    def isUserWithArgs(request, nosql, secret):     
        def decorated(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                try:
                    token = request.headers['Authorization']
                except KeyError:
                    return CustomResponse.responseFormat1("No token", status.unauth)
                else:
                    try:
                        data = jwt.decode(token, secret, algorithms=['HS256'])
                    except DecodeError:
                        return CustomResponse.responseFormat1("Token Decode Error", status.unauth)
                    except ExpiredSignatureError:
                        return CustomResponse.responseFormat1("Expired Token", status.unauth)
                    else:
                        if nosql.check(data['username']):
                            if nosql.getValue(data['username'] + '_token') == token:
                                return f(data['username'], *args, **kwargs)
                            return CustomResponse.responseFormat1("Old Token", status.unauth)
                        return CustomResponse.responseFormat1("Invalid User", status.unauth)
            return wrapper
        return decorated