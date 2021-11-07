from fastapi import status


class CourseController:

    def __init__(self, courseService):
        self.service = courseService

    def handleCreate(self, course_create_data):
        self.service.addCourse(course_create_data)
        return {"message": "Course created successfully", "status": status.HTTP_200_OK}

    def handleGet(self, course_id):
        course = self.service.getCourse(course_id)
        return {"info": course, "status": status.HTTP_200_OK}

    def handleGetCourses(self, courseFilters):
        print(courseFilters)
        courses = self.service.getCourses(courseFilters)
        return {"info": courses, "status": status.HTTP_200_OK}

    def handleDelete(self, deleteCourse):
        self.service.deleteCourse(deleteCourse)
        return {"message": "Course deleted correctly", "status": status.HTTP_200_OK}

    def handleEdit(self, courseNewInfo):
        self.service.editCourse(courseNewInfo)
        return {"message": "Course edited correctly", "status": status.HTTP_200_OK}

    def handleAddCollaborator(self, collaborator):
        self.service.addCollaborator(collaborator)
        return {"message": "Collaborator added correctly", "status": status.HTTP_200_OK}

    def handleRemoveCollaborator(self, removeCollaborator):
        self.service.removeCollaborator(removeCollaborator)
        return {"message": "Collaborator correctly removed", "status": status.HTTP_200_OK}