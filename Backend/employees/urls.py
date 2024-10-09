# Complaints
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet
# Attendance
from .views import AttendanceViewSet
# Messages
from .views import MessageViewSet
# Salary
from .views import SalaryViewSet
# Tasks
from .views import TaskViewSet
# JWT
from .views import EmployeeActionView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView
#
from .views import UserViewSet
#

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet)                   # Compalaints
router.register(r'attendance', AttendanceViewSet)                  # Attendance

router.register(r'salary', SalaryViewSet)                          # Salary
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'tasks', TaskViewSet)                             # tasks
router.register(r'users', UserViewSet, basename='user')            # users

urlpatterns = [
    path('', include(router.urls)),  # Includes all the API routes for complaints
    path('employee-action/', EmployeeActionView.as_view(), name='employee_action'), 
    
]



