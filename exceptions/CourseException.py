from fastapi import status


class CourseException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class CourseAlreadyExists(CourseException):
    def __init__(self, courseName):
        super().__init__(
            status.HTTP_400_BAD_REQUEST, f"Course '{courseName}' already exists"
        )


class CourseDoesNotExist(CourseException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, "Course does not exist")


class InvalidUserAction(CourseException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Invalid user action")


class IsAlreadyACollaborator(CourseException):
    def __init__(self, courseName):
        super().__init__(
            status.HTTP_208_ALREADY_REPORTED,
            f"The user is already a collaborator of the course '{courseName}'",
        )


class IsNotACollaborator(CourseException):
    def __init__(self, courseName):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"The user is not a collaborator of the course '{courseName}'",
        )


class UserNotFound(CourseException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, "User not found")


class IsAlreadySubscribed(CourseException):
    def __init__(self):
        super().__init__(
            status.HTTP_208_ALREADY_REPORTED, "You are already subscribed to the course"
        )


class IsNotSubscribed(CourseException):
    def __init__(self):
        super().__init__(
            status.HTTP_404_NOT_FOUND, "You are not subscribed to the course"
        )


class SubscriptionInvalid(CourseException):
    def __init__(self):
        super().__init__(
            status.HTTP_403_FORBIDDEN,
            "You should upgrade your membership to enrole this course",
        )
