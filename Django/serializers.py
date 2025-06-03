# serializers.py

from rest_framework import serializers
from .models import Entregas, Productores
from .models import Precios
from .models import Usuarios, Pagos
from django.contrib.auth.hashers import make_password

class EntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entregas
        fields = ['id', 'productor', 'fecha', 'usuario', 'cantidad']
        depth = 1  # Esto muestra los datos completos del productor y usuario

class PrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precios
        fields = ['id', 'fecha', 'precio']

# Para importar los Usuarios
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['id', 'nombre', 'correo', 'rol', 'contrasenia', 'estado']  # Asegurar que "estado" está incluido

    
    # Encriptar la contraseña antes de guardarla
    def create(self, validated_data):
        validated_data['contrasenia'] = make_password(validated_data['contrasenia'])
        return super().create(validated_data)

# Para importar los Productores
class ProductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productores
        fields = ['id', 'cedula', 'nombre', 'contacto', 'direccion'] 

class PagoSerializer(serializers.ModelSerializer):
    nombre_productor = serializers.SerializerMethodField()  # Campo calculado

    class Meta:
        model = Pagos
        fields = ['id', 'productor', 'nombre_productor', 'fecha', 'total']

    def get_nombre_productor(self, obj):
        """ Obtiene el nombre del productor usando la relación con la tabla Productores """
        return obj.productor.nombre if obj.productor else "Desconocido"

class EntregaReporteSerializer(serializers.ModelSerializer):
    productor = serializers.CharField(source="productor.nombre")  # Enviar solo el nombre del productor

    class Meta:
        model = Entregas
        fields = ["id", "fecha", "cantidad", "productor"]

class PagoReporteSerializer(serializers.ModelSerializer):
    productor = serializers.CharField(source="productor.nombre")  # Enviar solo el nombre del productor

    class Meta:
        model = Pagos
        fields = ["id", "fecha", "total", "productor"]


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()