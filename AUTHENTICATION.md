# SmartSense - Authentication & Security Guide

## 🔐 Authentication System

The SmartSense system now has complete access control to ensure students cannot access admin features and all user data is validated properly.

---

## 👥 User Types

### 1. **Admin Users**
- Full access to all system features
- Can manage students (register, view, delete)
- Access to dashboard, analytics, and reports
- Cannot mark attendance (admin-only function)

### 2. **Student Users**
- Can mark their own attendance using face recognition
- Cannot access admin dashboard
- Cannot view/edit/delete student records
- Cannot access analytics or reports

---

## 🚀 Login Credentials

### Admin Account
```
Username: admin
Password: admin123
```
**⚠️ IMPORTANT:** Change this password after first login!

### Student Accounts
For existing students:
```
Username: [Student's Roll Number]
Password: [Student's Roll Number]
```

**Example:** If roll number is `2`, then:
- Username: `2`
- Password: `2`

---

## 📝 How to Use

### For Admins:

1. **Login**
   - Go to http://127.0.0.1:8000/login/
   - Enter admin credentials
   - You'll be redirected to the Admin Dashboard

2. **Register New Students**
   - Navigate to "Students" → "Register Student"
   - Fill in student details (name, roll number, email, department, phone)
   - Capture student's face using webcam
   - System will create user account automatically
   - Student can login immediately with roll number as username/password

3. **Manage Students**
   - View all students
   - Delete (deactivate) students
   - View individual student attendance records

4. **View Analytics**
   - Access Dashboard for overall statistics
   - View Attendance Records with filters
   - Export CSV reports
   - View Student Analytics

### For Students:

1. **Login**
   - Go to http://127.0.0.1:8000/login/
   - Username: Your roll number
   - Password: Your roll number (change if needed)
   - You'll be redirected to Mark Attendance page

2. **Mark Attendance**
   - Allow camera access
   - Position your face in the frame
   - Click "Capture & Mark Attendance"
   - First capture = Entry time
   - Second capture (same day) = Exit time

3. **Late Entry Detection**
   - Entry before/at 9:30 AM = Present (On time)
   - Entry after 9:30 AM = Late

---

## 🔒 Security Features Implemented

### 1. **Access Control**
- ✅ Admin-only views protected with `@admin_required` decorator
- ✅ Student views protected with `@student_required` decorator
- ✅ Unauthorized access redirects to login or appropriate page
- ✅ Students cannot delete rows or access admin features

### 2. **Registration Validation**
- ✅ **Name validation:**
  - Minimum 3 characters
  - Only letters and spaces allowed
  - Case-insensitive duplicate check

- ✅ **Email validation:**
  - Proper email format required (regex pattern)
  - Duplicate email check

- ✅ **Phone validation:**
  - Must be exactly 10 digits
  - Duplicate phone check

- ✅ **Roll Number validation:**
  - Duplicate roll number check
  - Used as unique username

- ✅ **Face validation:**
  - Face must be detected in photo
  - No face = registration rejected

### 3. **User Account Management**
- ✅ Automatic user account creation during student registration
- ✅ Default password = roll number (students should change it)
- ✅ Email validation to prevent duplicates
- ✅ Proper first name/last name extraction from full name

---

## 🛠️ Management Scripts

### Create Admin User
If you need to create a new admin account:
```bash
cd c:\Users\nalla\Desktop\SmartSense_BTech_Project\AttendanceSystem
.venv\Scripts\python create_admin.py
```

### Create User Accounts for Existing Students
If you have students registered before authentication was added:
```bash
.venv\Scripts\python create_student_users.py
```

---

## 🎯 Navigation Menu

The navigation menu adapts based on user type:

### Admin Menu:
- Home
- Mark Attendance
- Dashboard (Admin only)
- Students (Admin only)
- Records (Admin only)
- Analytics (Admin only)
- User Dropdown (with Admin badge)
- Logout

### Student Menu:
- Home
- Mark Attendance
- User Dropdown
- Logout

---

## ⚙️ Technical Implementation

### Decorators Used:

**`@admin_required`**
- Checks if user is authenticated AND is_staff
- Redirects to login if not authenticated
- Shows error message if student tries to access

**`@student_required`**
- Checks if user is authenticated
- Redirects to login if not authenticated

### URLs:
- `/login/` - Login page
- `/logout/` - Logout and redirect to home
- `/students/` - Student list (admin only)
- `/students/register/` - Register student (admin only)
- `/attendance/mark-page/` - Mark attendance (authenticated users)
- `/attendance/dashboard/` - Admin dashboard (admin only)
- `/attendance/records/` - Attendance records (admin only)
- `/attendance/export-csv/` - Export CSV (admin only)
- `/attendance/analytics/` - Student analytics (admin only)

---

## 🐛 Troubleshooting

### Can't Login?
- Check your username and password
- Admin: `admin` / `admin123`
- Student: Use your roll number for both

### Getting "Access Denied" Message?
- Students cannot access admin features
- Make sure you're logged in as admin to access dashboard/analytics

### Student Registration Not Creating User?
- Make sure all validation passes
- Check that roll number doesn't already exist
- Email must be unique
- Phone must be 10 digits

### Forgot to Create Admin User?
Run: `.venv\Scripts\python create_admin.py`

---

## 📊 System Status

✅ **Completed Features:**
- Full authentication system
- Admin/Student access control
- Comprehensive validation
- Duplicate detection for all fields
- Automatic user account creation
- Login/Logout functionality
- Role-based navigation menu
- Security decorators on all views

---

## 🔄 Next Steps (Optional Enhancements)

- [ ] Password change functionality
- [ ] Password reset via email
- [ ] Student profile page
- [ ] Attendance history for students
- [ ] Email notifications
- [ ] Two-factor authentication
- [ ] Session timeout settings

---

**System Ready! 🎉**

All security measures are now in place. Students cannot access admin features, and all data is properly validated before registration.
