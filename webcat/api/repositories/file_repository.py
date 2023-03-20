from api_v1 import db
from db_models.file import File
from base_repository import BaseRepository

class FileRepository(BaseRepository):
    def __init__(self):
        BaseRepository.__init__(self, File)
        self.model = File

    def get(self, id: int):
        return self.model.query.get(id)

    def get_all(self):
        return self.model.query.all()

    def create(self, name: str, path: str):
        file = File(name, path)
        db.session.add(file)
        db.session.commit()
        return file

    def delete(self, id: int):
        file = self.get_by_id(id)
        db.session.delete(file)
        db.session.commit()

    def update(self, id: int, name: str, path: str):
        file = self.get_by_id(id)
        file.name = name
        file.path = path
        db.session.commit()
        return file


