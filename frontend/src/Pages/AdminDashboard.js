
import "./HomePage.css";
import "./AdminDashboard.css";
import AppHeader from "../components/AppHeader";
import { useSelector} from 'react-redux'
import { useState } from "react";
import Login from "../components/Login";
import Welcome from "../components/Welcome";

export default function AdminDashboard() {
  const isLoggedIn = useSelector((state) => state.user.isLoggedIn)
  const userInfo = useSelector((state) => state.user.userInfo)

  const usersTable = [[0, 'ndvanbur@iu.edu', 'Nicholas', 'Van Burk', 'admin'],[1,'jason@iu.edu', 'Jason', 'Radno', 'student'], [2, 'blahberson@fake.edu', 'Blabber', 'McBlabberson', 'teacher']];
  const coursesTable = [[0, 'algorithm design', '32saf', 'professor'], [1, 'underwater basket weaving', '3rjefldaj', 'Curious George']];
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
          {usersTable.map((user) => (
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
                
              </div>
          </div>
            );
}

