import uuid
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils.timezone import now
from datetime import timedelta

# Modelo para Usuarios
class Usuarios(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=False)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=50, null=False, default="Administrador")  # Administrador, Moderador
    contrasenia = models.CharField(max_length=255, null=False)
    estado = models.BooleanField(default=True)  #Activar/desactivar usuarios

    def save(self, *args, **kwargs):
        # Solo encripta la contraseña si no está ya en formato hash
        if not self.contrasenia.startswith('pbkdf2_sha256$'):
            self.contrasenia = make_password(self.contrasenia)
        super(Usuarios, self).save(*args, **kwargs)

    def check_password(self, raw_password):
        """ Método para verificar la contraseña almacenada """
        return check_password(raw_password, self.contrasenia)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "usuarios"

    last_login = models.DateTimeField(null=True, blank=True)


# Modelo para Productores
class Productores(models.Model):
    id = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=10, unique=True, null=False)
    nombre = models.CharField(max_length=100, null=False)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "productores"

# Modelo para Entregas
class Entregas(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    fecha = models.DateField(null=False)

    # Clave foránea para productores
    productor = models.ForeignKey(Productores, on_delete=models.CASCADE, null=False)

    # Clave foránea para productores
    usuario = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True) 

    def __str__(self):
        return f"Entrega de {self.productor}"

    class Meta:
        db_table = "entregas"

# Modelo para Precios de la leche
class Precios(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(null=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f"Precio del {self.fecha} - {self.precio} USD"

    class Meta:
        db_table = "precios"

# Modelo para Pagos
class Pagos(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(null=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    # Clave foránea para productores
    productor = models.ForeignKey(Productores, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"Pago de {self.productor.nombre} - {self.fecha}"

    class Meta:
        db_table = "pagos"

# Modelo para Reportes
class Reportes(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(null=False)
    descripcion = models.TextField(null=False)

    def __str__(self):
        return f"Reporte del {self.fecha}"

    class Meta:
        db_table = "reportes"

