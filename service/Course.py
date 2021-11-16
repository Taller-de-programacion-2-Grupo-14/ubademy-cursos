from requests import HTTPError

from exceptions.CourseException import *


class CourseService:
    def __init__(self, database, usersClient):
        self.db = database
        self.userClient = usersClient

    def addCourse(self, courseInfo):
        course = self.db.getCoursesCreatedBy(courseInfo["user_id"])
        if course and courseInfo["name"] in course:
            raise CourseAlreadyExists(courseInfo["name"])
        return self.db.addCourse(courseInfo)

    def getCourse(self, courseId):
        course = self.db.getCourse(courseId)
        if course is None:
            raise CourseDoesNotExist
        return course

    def getCourses(self, courseFilters):
        return self.db.getCourses(courseFilters)

    def deleteCourse(self, deleteCourse):
        self._courseExists(deleteCourse)
        self._isTheCourseCreator(deleteCourse)
        self.db.deleteCourse(deleteCourse)

    def editCourseInfo(self, courseNewInfo):
        self._courseExists(courseNewInfo)
        self._isTheCourseCreator(courseNewInfo)
        self.db.editCourse(courseNewInfo)

    def addCollaborator(self, collaborator):
        self._courseExists(collaborator)
        if collaborator["user_id"] in self.db.getCourseCollaborators(
            collaborator["id"]
        ):
            raise IsAlreadyACollaborator(self.db.getCourseName(collaborator["id"]))
        self.db.addCollaborator(collaborator)

    def removeCollaborator(self, removeCollaborator):
        self._courseExists(removeCollaborator)
        if removeCollaborator["user_to_remove"] not in self.db.getCourseCollaborators(
            removeCollaborator["id"]
        ):
            raise IsNotACollaborator(self.db.getCourseName(removeCollaborator["id"]))
        if removeCollaborator["user_id"] == removeCollaborator[
            "user_to_remove"
        ] or self._isTheCourseCreator(removeCollaborator, raiseException=False):
            self.db.removeCollaborator(removeCollaborator)
        else:
            raise InvalidUserAction

    def _isTheCourseCreator(self, courseData, raiseException=True):
        if courseData["user_id"] == self.db.getCourseCreator(courseData["id"]):
            return True

        if raiseException:
            raise InvalidUserAction
        return False

    def _courseExists(self, data):
        if self.db.getCourse(data["id"]) is None:
            raise CourseDoesNotExist

    def getUser(self, userId):
        try:
            return self.userClient.getUser(userId)
        except HTTPError as e:
            print(f"exception while getting user f{e}")
            raise UserNotFound()

    def getBatchUsers(self, ids: list):
        return self.userClient.getBatchUsers(ids).get("users", {})
