# Complaints
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Complaint
from .serializers import ComplaintSerializer
# Attendance
from .models import Attendance
from .serializers import AttendanceSerializer
from datetime import date
# Team
from .models import Team, Task, Message
from .serializers import TeamSerializer, TaskSerializer, MessageSerializer
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

# Complaints
class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can interact with the API

    # Override this method to ensure employees can only submit complaints on their behalf
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    # Admins should be able to view all complaints, but employees can only view their own
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # Admin
            return Complaint.objects.all()  # Admins can see all complaints
        return Complaint.objects.filter(employee=user)  # Employees only see their own complaints

# Attendance
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # Ensure employees can only mark attendance for today and only once per day
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user, date=date.today())

    # Admins can see all attendance records; employees can only see their own
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

# Team
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    # Ensure that the user creating a team becomes the team leader
    def perform_create(self, serializer):
        serializer.save(leader=self.request.user)

    # Admins can view all teams, but employees can only view the teams they're in
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Team.objects.all()
        return Team.objects.filter(members=user) | Team.objects.filter(leader=user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Get the team and assigned_to from validated data
        team = serializer.validated_data['team']
        assigned_to = serializer.validated_data['assigned_to']

        # Ensure that only the team leader can assign tasks
        if self.request.user == team.leader:
            # Assign the current user to assigned_by
            serializer.save(assigned_by=self.request.user, assigned_to=assigned_to)
        else:
            raise PermissionError("Only the team leader can assign tasks.")

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user) | Task.objects.filter(team__members=user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        team = serializer.validated_data['team']
        # Ensure that only team members can send messages
        if self.request.user in team.members.all() or self.request.user == team.leader:
            serializer.save(sender=self.request.user)  # Set the sender to the authenticated user
        else:
            raise PermissionError("You must be a member of the team to send a message.")

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Message.objects.all()
        return Message.objects.filter(team__members=user) | Message.objects.filter(team__leader=user)


# Salary
class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)  # Automatically set the employee to the current user

    def get_queryset(self):
        # Allow employees to view only their own salary
        if self.request.user.is_staff:
            return Salary.objects.all()
        return Salary.objects.filter(employee=self.request.user)


# Create views for token obtainment and refreshing
class CustomTokenObtainPairView(TokenObtainPairView):

    pass

class EmployeeActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Your code logic here
        return Response({"message": "Action performed"}, status=status.HTTP_200_OK)