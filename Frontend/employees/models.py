#Complaints
from django.db import models
from django.contrib.auth.models import User
#Attendance
from datetime import date
#


# Complaints
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE)  # Linking to User model
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.subject}"

# Attendance 
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='Present')

    class Meta:
        unique_together = ['employee', 'date']  # Prevent duplicate entries for the same day

    def __str__(self):
        return f"{self.employee.username} - {self.date} - {self.status}"

# Team
class Team(models.Model):
    team_name = models.CharField(max_length=255)
    leader = models.ForeignKey(User, related_name='team_leader', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='team_members')

    def __str__(self):
        return f"{self.team_name} (Leader: {self.leader.username})"

class Task(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task: {self.description} (Assigned to: {self.assigned_to.username})"

class Message(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.team.team_name}: {self.content[:50]}"

# Salary
class Salary(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    date = models.DateField()

    # Optionally, you can add a __str__ method to represent the object
    def __str__(self):
        return f"Salary for {self.employee.username} on {self.date}"