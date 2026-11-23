from app.extensions import db
from app.models.enrollment import Enrollment


class EnrollmentRepository:

    @staticmethod
    def get_by_class(class_id):
        return Enrollment.query.filter_by(
            class_id=class_id
        ).all()

    @staticmethod
    def get_by_id(enrollment_id):
        return db.session.get(Enrollment, enrollment_id)

    @staticmethod
    def update_grades(grade_updates):

        try:
            for enrollment_id, grade in grade_updates:
                enrollment = db.session.get(
                    Enrollment, enrollment_id
                )

                if enrollment:
                    enrollment.grade = grade

            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            raise
