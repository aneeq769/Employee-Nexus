# Complaints
from rest_framework import serializers
from .models import Complaint
# Attendance
from .models import Attendance
# Team
from .models import Team, Task, Message
from django.contrib.auth.models import User
# Salary
from .models import Salary


# Compaints
class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'employee', 'subject', 'description', 'status', 'created_at']
        read_only_fields = ['employee', 'status', 'created_at']  # Set employee and status as read-only for employees

# Attendance
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'status']
        read_only_fields = ['employee', 'date']  # Prevent employees from modifying these fields directly

# Team
class TeamSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True, slug_field='username', queryset=User.objects.all())
    leader = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Team
        fields = ['id', 'team_name', 'leader', 'members']
        read_only_fields = ['leader']  # Make leader read-only since it will be set automatically

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'team', 'assigned_by', 'assigned_to', 'description', 'completed']
        read_only_fields = ['assigned_by']  # Mark assigned_by as read-only


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'team', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp']  # Make sender and timestamp read-only


# Salary
class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['employee', 'basic_salary', 'bonuses', 'deductions', 'net_salary', 'date']
        read_only_fields = ['net_salary']