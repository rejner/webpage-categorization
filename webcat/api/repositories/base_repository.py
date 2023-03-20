import abc

class BaseRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id):
        pass

    @abc.abstractmethod
    def get_all(self):
        pass

    @abc.abstractmethod
    def update(self, entity):
        pass

    @abc.abstractmethod
    def delete(self, id):
        pass

    @abc.abstractmethod
    def create(self, entity):
        pass

