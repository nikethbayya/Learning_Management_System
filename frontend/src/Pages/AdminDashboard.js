
import "./HomePage.css";
import "./AdminDashboard.css";
import AppHeader from "../components/AppHeader";
import { useSelector} from 'react-redux'
import Login from "../components/Login";
import Welcome from "../components/Welcome";

export default function AdminDashboard() {
  const isLoggedIn = useSelector((state) => state.user.isLoggedIn)
  const userInfo = useSelector((state) => state.user.userInfo)
  return (
    

    <div className ="admin-dashboard">
        <AppHeader />
        <br></br>
        <div className="data-view">
        <button>Users</button>
        <button>Courses</button>
        </div>
    </div>
  );

}