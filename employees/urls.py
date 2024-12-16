# Complaints
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet
from .views import AttendanceViewSet
from .views import MessageViewSet
from .views import SalaryViewSet
from .views import TaskViewSet
from .views import EmployeeActionView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import UserViewSet
#

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet)                   
router.register(r'attendance', AttendanceViewSet)                  

router.register(r'salary', SalaryViewSet)                          
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'tasks', TaskViewSet)                             
router.register(r'users', UserViewSet, basename='user')            

urlpatterns = [
    path('', include(router.urls)),  
    path('employee-action/', EmployeeActionView.as_view(), name='employee_action'), 
    
]



