from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Courses, Events, User, Assignments
from utils import convert_user_role
from app import db

assignment = Blueprint('assignments', __name__)


@assignment.route('/createAssignment', methods=["POST"])
@jwt_required()
def createAssignment():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    data = request.json
    role = convert_user_role(str(user.role))
    

    if role == "Student":
        return {"msg": "Students cannot create assignments."}, 401
    
    required_params = ["title", "description", "course_id"]


    missing_params = [param for param in required_params if param not in data]

    if missing_params:
        return jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}), 400
    
    title = data["title"]
    description = data["description"]
    courseID = data["course_id"]
    
    course = Courses.query.get(courseID)

    if not course:
        return {"msg": "Course not found."}, 401

    courseInstructor = course.instructor

    if courseInstructor.id != user.id and role != "Admin":
        return {"msg": "You do not teach this course."}, 401
    

    new_assignment = Events(title=title, description=description,course_id=courseID)

    db.session.add(new_assignment)

    db.session.commit()
    return make_response(jsonify(msg="Assignment Created"), 200)

@assignment.route('/deleteAssignment', methods=["DELETE"])
@jwt_required()
def deleteAssignment():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    data = request.json
    role = convert_user_role(str(user.role))
    

    required_params = ["assignment_id"]

    missing_params = [param for param in required_params if param not in data]

    if missing_params:
        return jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}), 400
    
    assignmentID = data["assignment_id"]

    if role == "Student":
        return {"msg": "Students cannot update events."}, 401

    if assignmentID == "":
        return {"msg": "Please verify eventID"}, 401

    assignment = Events.query.filter_by(id=assignmentID).first()

    if not assignment:
        return {"msg": "Could not find Assignment."}, 401

    assignmentCourseID = assignment.course_id

    assignmentCourse = Courses.query.filter_by(id=assignmentCourseID).first()

    if not assignmentCourse:
        return {"msg": "Course ID of event is incorrect"}, 401

    eventCourseInstructor = assignmentCourse.instructor

    if eventCourseInstructor.id != user.id and role == "Instructor":
        return {"msg": "You do not teach this course."}, 401

    db.session.delete(assignment)

    db.session.commit()
    return make_response(jsonify(msg="Assignment Deleted"), 200)

@assignment.route('/assignments/<assignment_id>', methods=['POST'])
@jwt_required()
def getAssignment(assignment_id):
    resp = []
    assignment = Assignments.query.filter_by(assignment_id=assignment_id).first()
    resp.append({
        "title": assignment.title,
        "description": assignment.description,
        "course_id": assignment.course_id,
        })
    return make_response(jsonify(events=resp), 200)