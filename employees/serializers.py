# Complaints
from rest_framework import serializers
from .models import Complaint
# Attendance
from .models import Attendance
# Team
from django.contrib.auth.models import User
from .models import Task
from datetime import date
# Messages
from .models import Message
# Salary
from .models import Salary


# Compaints
class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'employee', 'subject', 'description', 'status', 'created_at']
        read_only_fields = ['employee', 'created_at']  #The employee is automatically set when a complaint is created, and the creation date is set automatically.

    def update(self, instance, validated_data): #This part of the code simply retrieves the current user making the request, so you can perform checks or grant/deny certain actions based on the user's role or identity.
        request = self.context.get('request')  
        user = request.user if request else None

        # Allow only admins to update the 'status' field
        if 'status' in validated_data and not user.is_staff:
            raise serializers.ValidationError({"status": "You do not have permission to update the status."})

        return super().update(instance, validated_data)

# Attendance
class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'date', 'status']
        read_only_fields = ['employee', 'date']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee.first_name and obj.employee.last_name else obj.employee.username

# Tasks
class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')
    
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'assigned_to',
            'assigned_to_username',
            'status',
            'priority',
            'due_date',
            'created_at',
            'updated_at',
            'completed',  
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

# Messages
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    recipient = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'timestamp', 'content']
        read_only_fields = ['id', 'sender', 'recipient', 'timestamp']

# Salary
class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.username')  

    class Meta:
        model = Salary
        fields = ['id', 'employee', 'employee_name', 'basic_salary', 'bonuses', 'deductions', 'net_salary', 'date']