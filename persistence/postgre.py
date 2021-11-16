from sqlalchemy.orm import Session
from sqlalchemy import text
from models.courses import Courses
from models.colaborators import Colaborators
from models.enrolled import Enrolled


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
        )
        self.session.add(c)
        self.session.commit()

    def getCourse(self, courseId):
        course = self.session.query(Courses).get(courseId)
        if not course:
            return None
        dic_course = {
            "name": course.name,
            "exams": course.exams,
            "creator_id": course.creator_id,
            "type": course.type,
            "subscription": course.subscription,
            "description": course.description,
            "hashtags": course.hashtags,
            "location": course.location,
            "cancelled": course.cancelled,
        }
        return dic_course

    def getCourses(self, courseFilters):
        offset = courseFilters["offset"]
        limit = courseFilters["limit"]
        where_clause = "WHERE cancelled = 0"
        filters = courseFilters["filters"]
        endings = f"OFFSET {offset} LIMIT {limit}"
        if filters:
            where_clause += " AND "
            for k, v in filters.items():
                if k == "offset" or k == "limit":
                    pass
                if type(v) == int:
                    filter = f"{k} = {v}"
                else:
                    filter = f"{k} LIKE '%{v}%'"
                if where_clause != "WHERE cancelled = 0 AND ":
                    where_clause += " AND "
                where_clause += filter
        query = f"SELECT * FROM courses {where_clause} {endings}"
        result = self.session.execute(text(query))
        courses = self.parse_result(result)
        return courses

    def deleteCourse(self, deleteCourse):
        id = deleteCourse["id"]
        course = self.session.query(Courses).get(id)
        course.cancelled = 1
        self.session.commit()

    def editCourse(self, courseNewInfo):
        id = courseNewInfo["id"]
        course = self.session.query(Courses).get(id)
        if "name" in courseNewInfo:
            course.name = courseNewInfo["name"]
        if "type" in courseNewInfo:
            course.type = courseNewInfo["type"]
        if "location" in courseNewInfo:
            course.location = courseNewInfo["location"]
        if "description" in courseNewInfo:
            course.description = courseNewInfo["description"]
        if "hashtags" in courseNewInfo:
            course.hashtags = courseNewInfo["hashtags"]
        self.session.commit()

    def addCollaborator(self, collaborator):
        new_colab = Colaborators(
            id_colaborator=collaborator["user_id"], id_course=collaborator["id"]
        )
        self.session.add(new_colab)
        self.session.commit()

    def removeCollaborator(self, collaborator):
        colab = self.session.query(Colaborators).get(
            (collaborator["user_to_remove"], collaborator["id"])
        )
        self.session.delete(colab)
        self.session.commit()

    def getCourseCollaborators(self, courseId):
        colabs_course = self.session.query(Colaborators).filter(
            Colaborators.id_course == courseId
        )
        colaborators = []
        if not colabs_course.first():
            return colaborators
        for c in colabs_course:
            colaborators.append(c.id_colaborator)
        return colaborators

    def addSubscriber(self, id_course, subscriber_id):
        enrollment = Enrolled(
            id_course=id_course, id_student=subscriber_id, status="on course"
        )
        self.session.add(enrollment)
        self.session.commit()

    def removeSubscriber(self, course_id, subscriber_id):
        suscriber = self.session.query(Courses).get((course_id, subscriber_id))
        self.session.delete(suscriber)
        self.session.commit()

    def getMyCourses(self, user_id):
        result = self.session.query(Courses).filter(Courses.creator_id == user_id)
        courses = self.parse_result(result)
        return courses

    def parse_result(self, result):
        courses = []
        if not result:
            return courses
        for r in result:
            courses.append(r._asdict())
        return courses

    def getMySubscriptions(self, user_id):
        query = f"SELECT * FROM (SELECT id_course AS sarasa FROM enrolled WHERE id_student = {user_id}) as studentCourses JOIN courses AS c ON c.id = studentCourses.sarasa"
        result = self.session.execute(text(query))
        subscriptions = self.parse_result(result)
        return subscriptions


# My Subscriptions

# SELECT *
#   FROM (SELECT id AS courseId FROM enrolled WHERE id_student = {subscriberId}) as studentCourses
#   JOIN courses AS c
#   ON c.id = studentCourses.courseId


# Collaborators

# SELECT *
#   FROM (SELECT id AS courseId FROM colaborators WHERE id = {courseId}) as courseCollabs
#   JOIN courses AS c
#   ON c.id = courseCollabs.courseId


# Students

# SELECT *
#   FROM (SELECT id AS courseId FROM enrolled WHERE id = {courseId}) as courseStuds
#   JOIN courses AS c
#   ON c.id = courseStuds.courseId


# Created Courses

# SELET * FROM courses WHERE creator_id = {userId}
