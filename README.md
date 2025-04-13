# Learning Management System (LMS)

Welcome to the Learning Management System (LMS) — a comprehensive platform designed to revolutionize the online learning experience. 
This system facilitates seamless interaction between instructors and students, offering tools for course management, enrollment, assessments, and progress tracking. 
Whether you're an educator aiming to disseminate knowledge or a learner seeking structured courses, this LMS provides the infrastructure to support your educational journey.

## 📁 Project Structure

```
Learning_Management_System/
├── backend/       # Backend logic and API endpoints
├── frontend/      # Frontend user interface
├── demo_data.sql  # Sample SQL data for testing
├── .gitignore
```

## 🚀 Features

- **User Authentication**: Secure login and registration for students and instructors.
- **User Roles**: Supports multiple user roles including Admins, Instructors, and Students.
- **Course Management**: Admins and Instructors can create, update, and delete courses.
- **Enrollment System**: Students can enroll in available courses.
- **Content Delivery**: Instructors can upload course materials and assignments.​
- **Assessment Module**: Create and take quizzes or exams.
- **Progress Tracking**: Monitor student progress and view grades.
- **Responsive Design**: Accessible on various devices.

## 🛠️ Technologies Used

- **Frontend**:
  - HTML, CSS, JavaScript
  - React.js
- **Backend**:
  - Python
  - Django Framework
- **Database**:
  - PostgreSQL
- **Others**:
  - RESTful APIs
  - JWT for authentication

## 🖥️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nikethbayya/Learning_Management_System.git
   cd Learning_Management_System
   ```

2. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Set up the frontend**:
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

4. **Access the application**:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000/api/`

## 🧪 Sample Data

To populate the database with sample data:

```bash
psql -U your_username -d your_database -f demo_data.sql
```

*Ensure PostgreSQL is installed and replace `your_username` and `your_database` with your credentials.*
