from datetime import timedelta
from redis import Redis
from typing import Optional, Tuple, Union, TypeVar, Callable, Any

# For Type hinting
F = TypeVar('F', bound=Callable[..., Any])

class NoSQL:
    def __init__(self, host=u'localhost', password='', port=6379) -> None:
        self.r = Redis(host=host, password=password, port=port)
        assert self.r.ping(), "Connection Error"
    
    def _errorHandler(func : F) -> F:
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                raise NoSQLError(str(e))
        return wrapper
    
    def _checkType(self, key : str) -> str:
        return self.r.type(key).decode('ascii')
    
    @_errorHandler
    def check(self, key : str) -> bool:
        return self.r.exists(key)

    @_errorHandler
    def setValue(self, key : str, value : str) -> Optional[bool]:      
        return self.r.set(key, value)
    
    @_errorHandler
    def setValueEx(self, key : str, value : str) -> Optional[bool]:      
        return self.r.setex(key, timedelta(minutes=1), value)
    
    @_errorHandler
    def getValue(self, key : str) -> Optional[str]:
        k = None
        if self.r.exists(key):
            if self._checkType(key) == 'string':
                k = self.r.get(key)
            else:
                raise TypeError('Key is not holding the type string')
        if k:
            return k.decode('ascii')
        return None