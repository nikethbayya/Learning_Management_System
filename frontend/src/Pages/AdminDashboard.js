
import "./HomePage.css";
import "./AdminDashboard.css";
import AppHeader from "../components/AppHeader";
import { useSelector} from 'react-redux'
import Login from "../components/Login";
import Welcome from "../components/Welcome";

export default function AdminDashboard() {
  const isLoggedIn = useSelector((state) => state.user.isLoggedIn)
  const userInfo = useSelector((state) => state.user.userInfo)
  const rows = 5
  const usersTable = [[1,2],[3,4],[5,6],[7,8],[9,10]];
  return (
    

    <div>
        <AppHeader />
        <div className="page-container">
        <button>Users</button>
        <button>Courses</button>
        <table>
          <tr>
            <th>Name</th>
            <th>Email</th>
          </tr>
          {usersTable.map((user) => (
            <tr>
              <td>{user[0]}</td>
              <td>{user[1]}</td>
            </tr>
          ))}


        </table>

        </div>
    </div>
  );

}

