# Complaints
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Complaint
from .serializers import ComplaintSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# Attendance
from .models import Attendance
from .serializers import AttendanceSerializer
from datetime import date
# Tasks
from .models import Task
from .serializers import TaskSerializer
# Messages
from .models import Message
from .serializers import MessageSerializer
from django.db.models import Q
# Salary
from rest_framework import viewsets
from .models import Salary
from .serializers import SalarySerializer

# Create views for token obtainment and refreshing
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import action



class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)  # Allow anyone to access this view

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        
        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is authenticated, call the parent method to get tokens
            response = super().post(request, *args, **kwargs)
            
            # Add the user's role to the response
            response.data['role'] = user.is_staff and 'admin' or 'employee'  # Adjust based on your role logic
            return response
        
        # If authentication fails, return an error response
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Users
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  
    permission_classes = [IsAuthenticated]  

    def list(self, request):
        users = self.queryset
        return Response(users.values('id', 'username'))  # Return only id and username

# Complaints
class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]  # Default permission

    def get_permissions(self):
        
        if self.action in ['update', 'partial_update', 'destroy']: #agr ye krna to admin kr skta
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated] #baki user create kr skty just
        return super().get_permissions()

    def perform_create(self, serializer): #jab new complaint create krni ho
        serializer.save(employee=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # Admin
            return Complaint.objects.all()
        return Complaint.objects.filter(employee=user)

# Attendance
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # Employees can only mark attendance for today and only once per day
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user, date=date.today())

    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Attendance.objects.all()  # Admins can see all records
        return Attendance.objects.filter(employee=user)  # Employees can only see their own records

    # Override the destroy method to prevent employees from deleting their attendance records
    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            return self.permission_denied(request, "You cannot delete attendance records.")
        return super().destroy(request, *args, **kwargs)

# Tasks
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser] if self.request.user.is_staff else [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def perform_update(self, serializer):
        # Allow employees to update the 'completed' field on their assigned tasks
        task = self.get_object()
        if self.request.user == task.assigned_to:
            serializer.save()
        else:
            # Raise a permission denied error if the user is not the assigned employee
            raise PermissionDenied("You do not have permission to update this task.")

# Messages
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()  # Added queryset attribute
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')

    def create(self, request, *args, **kwargs):
        recipient_username = request.data.get('recipient')
        content = request.data.get('content')

        if not recipient_username or not content: # agr wo na recipient or na username dyga lekin send message pr click kry ga tab ye..
            return Response({'error': 'Recipient and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipient = User.objects.get(username=recipient_username) # Jo username dia ham ny wo hy database mein ya nahi ye check krta agr nahi hoga to error dy dyga.
        except User.DoesNotExist:
            return Response({'error': 'Recipient does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='conversation/(?P<username>[^/.]+)')
    def conversation(self, request, username=None): #This method retrieves all messages between the logged-in user and the specified user (the conversation).
        try:
            other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=request.user))
        ).order_by('-timestamp')

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Salary
class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Calculate net salary
        basic_salary = serializer.validated_data.get('basic_salary', 0)
        bonuses = serializer.validated_data.get('bonuses', 0)
        deductions = serializer.validated_data.get('deductions', 0)
        net_salary = basic_salary + bonuses - deductions
        
        # If the user is an admin, they can assign the salary to any employee
        if self.request.user.is_staff:
            serializer.save(net_salary=net_salary)  # Admin can set employee in the request
        else:
            # Employees cannot assign salary, but they can view their own
            serializer.save(employee=self.request.user, net_salary=net_salary)






# 

class EmployeeActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        return Response({"message": "Action performed"}, status=status.HTTP_200_OK)


