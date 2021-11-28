from sqlalchemy.orm import Session
from sqlalchemy import text
from models.courses import Courses
from models.collaborators import Collaborators
from models.enrolled import Enrolled
from models.favoriteCourses import FavoriteCourses
import re

DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 500
EDITABLE_FIELDS = ["name", "description", "location", "hashtags"]
SKIP_FILTERS = [
    "offset",
    "limit",
    "creator_first_name",
    "creator_last_name",
    "first_name",
    "last_name",
]


class DB:
    def __init__(self, engine):
        self.session = Session(engine)

    def addCourse(self, courseInfo):
        name = courseInfo["name"]
        exams = courseInfo["exams"]
        creator_id = courseInfo["user_id"]
        type = courseInfo["type"]
        subscription = courseInfo["subscription"]
        location = courseInfo["location"]
        description = courseInfo["description"]
        hashtags = courseInfo.get("hashtags", "")
        c = Courses(
            name=name,
            exams=exams,
            creator_id=creator_id,
            type=type,
            subscription=subscription,
            description=description,
            hashtags=hashtags,
            location=location,
            cancelled=0,
            blocked=False,
        )
        self.session.add(c)
        self.session.commit()

    def getCourse(self, courseId):
        query = self._buildQuery("courses", filters={"id": courseId})
        course = self._parseResult(
            self.session.execute(text(query))
        )  # In this way we get an array of dicts
        if not course:
            return None
        return course[0]

    def getCourses(self, courseFilters):
        # ToDo: Mostrar los cursos que estan on course
        # En el historico haces esto
        query = self._buildQuery("courses", filters=courseFilters)
        return self._parseResult(self.session.execute(text(query)))

    def deleteCourse(self, courseId):
        query = self._buildQuery(
            "courses", "UPDATE", ["cancelled = 1"], filters={"id": courseId}
        )
        self.session.execute(text(query))
        self.session.commit()

    def editCourse(self, courseNewInfo):
        columns = [
            f"{column} = '{newValue}'"
            for column, newValue in courseNewInfo.items()
            if column in EDITABLE_FIELDS
        ]
        query = self._buildQuery(
            "courses", "UPDATE", columns, filters={"id": courseNewInfo["id"]}
        )
        self.session.execute(text(query))
        self.session.commit()

    def addCollaborator(self, collaborator):
        new_colab = Collaborators(
            id_collaborator=collaborator["user_id"], id_course=collaborator["id"]
        )
        self.session.add(new_colab)
        self.session.commit()

    def removeCollaborator(self, collaborator):
        filters = {
            "id_course": collaborator["id"],
            "id_collaborator": collaborator["user_to_remove"],
        }
        query = self._buildQuery("collaborators", "DELETE", filters=filters)
        self.session.execute(text(query))
        self.session.commit()

    def getCourseUsers(self, courseId, getSubscribers=True):
        table = "enrolled" if getSubscribers else "collaborators"
        column = "id_student" if getSubscribers else "id_collaborator"
        query = self._buildQuery(
            table, columns=[column], filters={"id_course": courseId}
        )
        return {record.id_collaborator for record in self.session.execute(text(query))}

    def addSubscriber(self, id_course, subscriber_id):
        enrollment = Enrolled(
            id_course=id_course, id_student=subscriber_id, status="on course"
        )
        self.session.add(enrollment)
        self.session.commit()

    def removeSubscriber(self, courseId, subscriberId):
        filters = {"id_course": courseId, "id_student": subscriberId}
        query = self._buildQuery("enrolled", "DELETE", filters=filters)
        self.session.execute(text(query))
        self.session.commit()

    def getMySubscriptions(self, userId):
        query = f"SELECT * FROM (SELECT id_course AS courseId FROM enrolled WHERE id_student \
                = {userId}) as studentCourses JOIN courses AS c ON c.id \
                = studentCourses.courseId"
        return self._parseResult(self.session.execute(text(query)))

    def getUsers(self, courseId, userFilters):
        getSubscribers = userFilters["subscribers"]
        table = "enrolled" if getSubscribers else "collaborators"
        column = "id_student" if getSubscribers else "id_collaborator"
        filters = {
            "id_course": courseId,
            "offset": userFilters.get("offset", DEFAULT_OFFSET),
            "limit": userFilters.get("limit", DEFAULT_LIMIT),
        }
        query = self._buildQuery(table, columns=[column], filters=filters)
        self._parseResult(self.session.execute(text(query)))
        return self._parseResult(self.session.execute(text(query)))

    def blockCourse(self, courseId: int):
        query = self._buildQuery(
            "courses", "UPDATE", ["blocked = true"], filters={"id": courseId}
        )
        self.session.execute(text(query))
        self.session.commit()

    def unblockCourse(self, courseId: int):
        query = self._buildQuery(
            "courses", "UPDATE", ["blocked = false"], filters={"id": courseId}
        )
        self.session.execute(text(query))
        self.session.commit()

    def addFavoriteCourse(self, courseId, userId):
        favoriteCourses = FavoriteCourses(course_id=courseId, user_id=userId)
        self.session.add(favoriteCourses)
        self.session.commit()

    def getFavoriteCourses(self, userId):
        query = f"SELECT * FROM (SELECT course_id AS courseId FROM favoriteCourses WHERE user_id \
                = {userId}) as favCourses JOIN courses AS c ON c.id \
                = favCourses.courseId"
        return self._parseResult(self.session.execute(text(query)))

    def removeFavoriteCourse(self, courseId, userId):
        query = self._buildQuery(
            "favoritecourses",
            "DELETE",
            filters={"course_id": courseId, "user_id": userId},
        )
        self.session.execute(text(query))
        self.session.commit()

    def getCoursesLikedBy(self, userId):
        query = self._buildQuery(
            "favoriteCourses", columns=["course_id"], filters={"user_id": userId}
        )
        return {record.course_id for record in self.session.execute(text(query))}

    def _buildQuery(self, tableName, operation="SELECT", columns=None, filters=None):
        operation = operation.upper()
        if columns is None:
            columns = ["*"]
        filtersQuery = self._buildFilterQuery(filters) if filters is not None else ""
        if operation == "SELECT":
            return f"{operation} {', '.join(columns)} FROM {tableName} {filtersQuery}"
        filtersQuery = re.sub(r"(.*)OFFSET.*", r"\1", filtersQuery)
        if operation == "DELETE":
            return f"{operation} FROM {tableName} {filtersQuery}"
        if operation == "UPDATE":
            return f"{operation} {tableName} SET {', '.join(columns + ['updated_on = now()'])} {filtersQuery}"
        if operation == "INSERT":
            return f"{operation} INTO {tableName} VALUES({', '.join(columns)})"

    def _buildFilterQuery(self, filters):
        filterQuery = ""
        for filterName, value in filters.items():
            if filterName in SKIP_FILTERS:
                # A dict does not have an order, this instructions must be at the end of the query
                continue
            if filterQuery:
                filterQuery += " AND "
            else:
                filterQuery += "WHERE "
            if filterName == "free_text":
                filterQuery += (
                    f"(name LIKE '%{value}%' OR description LIKE '%{value}%')"
                )
            elif filterName in {"name", "type", "location", "subscription"}:
                filterQuery += f"{filterName} LIKE '%{value}%'"
            else:
                filterQuery += f"{filterName} = {value}"
        filterQuery += (
            f" OFFSET {filters.get('offset', DEFAULT_OFFSET)} "
            f"LIMIT {filters.get('limit', DEFAULT_LIMIT)}"
        )
        return filterQuery

    def _parseResult(self, result):
        courses = []
        if not result:
            return courses
        for r in result:
            if len(r) == 1:
                courses.append(r[0])
            else:
                courses.append(r._asdict())
        return courses

    def _skipFilter(self, filterName, allowedFilters):
        return filterName in allowedFilters
