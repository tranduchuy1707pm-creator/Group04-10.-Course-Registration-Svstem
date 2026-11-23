from app.extensions import db
from app.models.class_section import ClassSection


class ClassRepository:

    @staticmethod
    def get_by_lecturer(lecturer_id):
        return ClassSection.query.filter_by(
            lecturer_id=lecturer_id
        ).all()

    @staticmethod
    def get_by_id(class_id):
        return ClassSection.query.filter_by(
            id=class_id
        ).first()

    @staticmethod
    def get_by_id_and_lecturer(class_id, lecturer_id):
        return ClassSection.query.filter_by(
            id=class_id,
            lecturer_id=lecturer_id
        ).first()
      
