
import "./HomePage.css";
import "./AdminDashboard.css";
import AppHeader from "../components/AppHeader";
import { useSelector} from 'react-redux'
import { useState } from "react";
import axios from "axios";
import Login from "../components/Login";
import Welcome from "../components/Welcome";

export default function AdminDashboard() {
  const isLoggedIn = useSelector((state) => state.user.isLoggedIn)
  const userInfo = useSelector((state) => state.user.userInfo)

  
  let [coursesTable, updateCourses] = useState([]);
  let loadCourses = () => {
  axios.get('http://localhost:8000/getAllCourses', {
    headers: {
      Authorization: 'Bearer ' + localStorage.getItem('hoosier_room_token')
    }
  }).then((response) => {
     let courses = response.data.courses;
     let newTable = [];
     for(const [key,value] of Object.entries(courses)){
      newTable.push([value.id, value.description, value.courseNumber, value.instructor]);
     }
     updateCourses(newTable);
}).catch(err => {
  console.log("error getting courses")
})
  }
let [userTable, updateUsers] = useState([]);
let loadUsers = () =>{
  axios.get('http://localhost:8000/getAllUsers', {
    headers: {
      Authorization: 'Bearer ' + localStorage.getItem('hoosier_room_token')
    }
  }).then((response) => {
    let users = response.data.userTable;
    let newTable = [];
    for(const [key,value] of Object.entries(users)){
      newTable.push([value.id, value.email, value.firstName, value.lastName, value.role]);
    }
    updateUsers(newTable);
    
  }).catch(err => {
  console.log("error getting courses")
  })
}
if(userTable.length == 0){loadUsers()}
if(coursesTable.length == 0){loadCourses()}
  const [state, setState] = useState(1);

  function displayView(){
    setState(state * -1);
  }
  const prompt_course_delete = (course_id) => {
    const answer = window.confirm("Are you sure you want to delete course " + course_id + "?");
  }
  const prompt_user_delete = (id) => {
    const answer = window.confirm("Are you sure you want to delete user " + id + "?");
  }
  const handleAddCourse = (e) => {
    e.preventDefault();
    console.log("success");
  }
  if (state === 1) {
  return (
    

    <div>
        <AppHeader />
        <div className="page-container">
        <button>Users</button>
        <button onClick={displayView}>Courses</button>
        <table>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Role</th>
            <th>Delete User?</th>
          </tr>
          {userTable.map((user) => (
            <tr>
              <td>{user[0]}</td>
              <td>{user[1]}</td>
              <td>{user[2]}</td>
              <td>{user[3]}</td>
              <td>{user[4]}</td>
              <td><button onClick={() => prompt_user_delete(user[0])}>Delete</button></td>
            </tr>
          ))}

        </table>
            <button>Add Student</button>
        </div>
    </div>
  );
          }
            return(
              <div>
              <AppHeader />
              <div className="page-container">
              <button onClick = {displayView}>Users</button>
              <button>Courses</button>
              <table>
                <tr>
                  <th>ID</th>
                  <th>Course</th>
                  <th>Course Number</th>
                  <th>Instructor</th>
                  <th>Delete Course?</th>
                </tr>
                {coursesTable.map((course) => (
                  <tr>
                    <td>{course[0]}</td>
                    <td>{course[1]}</td>
                    <td>{course[2]}</td>
                    <td>{course[3]}</td>
                    <td><button onClick={() => prompt_course_delete(course[0])}>Delete</button></td>
                  </tr>
                ))}
      
      
              </table>
                <button onClick={() => document.getElementById("addc").hidden = false}>Add Course</button>
                <form id = "addc" hidden={true} method = "POST" onSubmit={handleAddCourse}>
                  <label>Course Name</label>
                  <input type = "text" name = "course_name"/>
                  <label >Course Number</label>
                  <input type = "text" name = "course_number"/>
                  <label >Instructor</label>
                  <input type = "text" name = "instructor"/>
                  <input type = "submit" value = "Submit"/>
                </form>
              </div>
          </div>
            );
}

