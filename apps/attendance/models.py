from django.db import models

class Attendance(models.Model):
    evaluation = models.ForeignKey("evaluation.Evaluation", on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.evaluation.employee.name} - {self.status} - {self.date}"
