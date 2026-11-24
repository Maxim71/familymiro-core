# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import ConstructionLayer, ConstructionSection

class ConstructionLayerSerializer(serializers.ModelSerializer):
    """
    📊 INDUSTRIAL VALIDATOR WITH STRICT CODE STATUSES (SECTION 3)
    """
    # Список разрешенных ИТР-статусов для Колонки C
    ALLOWED_STATUSES = ["В процессе", "На проверке", "Замечания", "Акт передан"]

    inspection_status = serializers.CharField(write_only=True, default="В процессе")
    floor = serializers.CharField(write_only=True, default="1")
    size_dimensions = serializers.CharField(write_only=True, default="D=150")
    structure_type = serializers.CharField(write_only=True, default="Проход через ПГП")
    local_coords = serializers.CharField(write_only=True, default="По центру")

    class Meta:
        model = ConstructionLayer
        fields = [
            'section', 'filename', 'axes', 'room', 'file_extension', 
            'inspection_status', 'floor', 'size_dimensions', 'structure_type', 'local_coords'
        ]

    def validate_inspection_status(self, value):
        # 🔥 РЕАЛИЗАЦИЯ ВАЛИДАЦИИ УЧАСТКА 3: Защита от некорректного ввода статуса АОСР
        if value not in self.ALLOWED_STATUSES:
            raise serializers.ValidationError(
                f"🚨 ИТР-КРАШ: Недопустимый статус АОСР! Разрешены только: {', '.join(self.ALLOWED_STATUSES)}"
            )
        return value
