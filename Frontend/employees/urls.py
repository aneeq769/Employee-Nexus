# Complaints
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet
# Attendance
from .views import AttendanceViewSet
# Team
from .views import TeamViewSet, TaskViewSet, MessageViewSet
# Salary
from .views import SalaryViewSet
# JWT
from .views import EmployeeActionView, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'employees', ComplaintViewSet)    # Compalaints
router.register(r'attendance', AttendanceViewSet)  # Attendance

router.register(r'teams', TeamViewSet)             # Team #
router.register(r'tasks', TaskViewSet)             # Team #
router.register(r'messages', MessageViewSet)       # Team #

router.register(r'salary', SalaryViewSet)          # Salary

urlpatterns = [
    path('', include(router.urls)),  # Includes all the API routes for complaints
     path('employee-action/', EmployeeActionView.as_view(), name='employee_action'), 
]
