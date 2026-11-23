from app.repositories.class_repository import ClassRepository
from app.repositories.enrollment_repository import EnrollmentRepository


class ClassService:

    @staticmethod
    def get_teaching_classes(lecturer_id):
        return ClassRepository.get_by_lecturer(lecturer_id)

    @staticmethod
    def get_students(class_id, lecturer_id):

        class_section = ClassRepository.get_by_id_and_lecturer(
            class_id, lecturer_id
        )

        if not class_section:
            return None, []

        students = EnrollmentRepository.get_by_class(class_id)

        return class_section, students

    @staticmethod
    def save_grades(class_id, lecturer_id, form_data):

        class_section = ClassRepository.get_by_id_and_lecturer(
            class_id, lecturer_id
        )

        if not class_section:
            return False, "You are not assigned to this class."

        enrollments = EnrollmentRepository.get_by_class(class_id)

        allowed_ids = {item.id for item in enrollments}

        grade_updates = []

        for enrollment in enrollments:

            value = form_data.get(f"grade_{enrollment.id}", "").strip()

            if value == "":
                continue

            try:
                grade = float(value)
            except ValueError:
                return False, f"Invalid grade for enrollment {enrollment.id}."

            if not 0 <= grade <= 10:
                return False, "Grade must be between 0 and 10."

            if enrollment.id not in allowed_ids:
                return False, "Invalid student enrollment."

            grade_updates.append((enrollment.id, grade))

        try:
            EnrollmentRepository.update_grades(grade_updates)
            return True, "Grades saved successfully."

        except Exception:
            return False, "Failed to save grades."
