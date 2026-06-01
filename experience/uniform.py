from typing import Generic, TypeVar

UniformType = TypeVar('UniformType')

class Uniform(Generic[UniformType]):
    '''class for single uniform in single shader program'''
    
    def __init__(self, name: str, init_data: UniformType):
        self._name = name
        self._data = init_data
        self._location = None

    @property
    def name(self): return self._name

    @property
    def data(self): return self._data
    @data.setter
    def data(self, new_data: UniformType): self._data = new_data

    @property
    def location(self): return self._location
    @location.setter
    def location(self, new_location: int): self._location = new_location