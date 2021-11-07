from fastapi import FastAPI, Request, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from persistence.local import DB
from service.Course import CourseService
from controllers.Course import CourseController
from schemas.Schemas import *
from exceptions.CourseException import CourseException
from queryParams.QueryParams import *

app = FastAPI()
courseService = CourseService(DB())
courseController = CourseController(courseService)


@app.post('/courses/create')
def createCourse(createCourseData: CreateCourseSchema):
    return courseController.handleCreate(createCourseData.dict())


@app.get('/courses/{course_id}')
def getCourse(course_id: int):
    return courseController.handleGet(course_id)


@app.get('/courses')
def getCourses(courseFilters: CourseQueryParams = Depends(CourseQueryParams)):
    return courseController.handleGetCourses(courseFilters)


@app.patch('/courses')
def editCourse(courseNewInfo: EditCourseInfoSchema):
    return courseController.handleEdit(courseNewInfo.dict())


@app.delete('/courses')
def deleteCourse(deleteCourseData: DeleteCourseSchema):
    return courseController.handleDelete(deleteCourseData.dict())


@app.post('/courses/collaborators')
def addCollaborator(collaborator: CollaboratorSchema):
    return courseController.handleAddCollaborator(collaborator.dict())


@app.delete('/courses/collaborators')
def removeCollaborator(collaborator: RemoveCollaboratorSchema):
    return courseController.handleRemoveCollaborator(collaborator.dict())


@app.exception_handler(RequestValidationError)
def validationExceptionHandler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    fields = []
    for err in errors:
        value = {'field': err.get('loc', ['invalid field'])[-1], 'message': err.get('msg', '')}
        fields.append(value)
    finalStatus = status.HTTP_400_BAD_REQUEST
    return JSONResponse(
        status_code=finalStatus,
        content=jsonable_encoder({
            "errors": fields,
            "status": finalStatus})
    )


@app.exception_handler(CourseException)
def handle_course_exception(request: Request, exc: CourseException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"message": exc.message, "status": exc.status_code})
    )


@app.exception_handler(Exception)
def handleUnknownException(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=jsonable_encoder(
            {"message": 'Neither God knows what happened...'
                        'just kidding, the error was:' + type(exc).__name__,
             "status": status.HTTP_503_SERVICE_UNAVAILABLE
             })
    )
