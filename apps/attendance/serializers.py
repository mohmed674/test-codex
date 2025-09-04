# apps/attendance/serializers.py
# ERP_CORE/attendance/serializers.py

from __future__ import annotations

from rest_framework import serializers

from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "check_in",
            "check_out",
            "status",
            "notes",
        ]
