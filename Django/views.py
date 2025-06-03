import pandas as pd
import numpy as np

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User  # Importar el modelo correcto
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import generics

from rest_framework.decorators import api_view

from .serializers import EntregaSerializer, ProductorSerializer, PagoSerializer, PrecioSerializer, UsuarioSerializer
from .serializers import ProductorSerializer, PagoSerializer
from .models import Usuarios, Entregas, Productores, Precios, Pagos

from .serializers import EntregaReporteSerializer, PagoReporteSerializer

# Para que sume los pagos totales
from django.db.models import Sum

from datetime import date
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import FileUploadSerializer




# Vista para manejar usuarios
class UsuarioAPI(APIView):
    def get(self, request):
        usuarios = Usuarios.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        correo = request.data.get("correo")
        nombre = request.data.get("nombre")
        contrasenia = request.data.get("contrasenia")
        rol = request.data.get("rol", "Moderador")

        if not correo or not nombre or not contrasenia:
            return Response({"error": "Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

        contrasenia_hash = make_password(contrasenia)

        usuario = Usuarios.objects.create(
            correo=correo,
            nombre=nombre,
            contrasenia=contrasenia_hash,
            rol=rol
        )

        return Response({"mensaje": "Usuario creado exitosamente", "usuario_id": usuario.id}, status=status.HTTP_201_CREATED)

# Vista para editar un usuario
class UsuarioDetailView(APIView):
    def get(self, request, pk):
        try:
            usuario = Usuarios.objects.get(pk=pk)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data)
        except Usuarios.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            usuario = Usuarios.objects.get(pk=pk)
            usuario.nombre = request.data.get("nombre")
            usuario.correo = request.data.get("correo")
            usuario.rol = request.data.get("rol")
            usuario.save()
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data)
        except Usuarios.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

# Para cambiar de estado
class ToggleEstadoUsuario(APIView):
    def patch(self, request, pk):
        try:
            usuario = Usuarios.objects.get(pk=pk)
            usuario.estado = not usuario.estado
            usuario.save()
            return Response({"estado": usuario.estado}, status=status.HTTP_200_OK)
        except Usuarios.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class CrearEntrega(APIView):
    def get(self, request):

        entregas = Entregas.objects.all()
        serializer = EntregaSerializer(entregas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        productor_id = request.data.get("productor_id")
        usuario_id = request.data.get("usuario_id")  # Usuario que registra
        cantidad = request.data.get("cantidad")

        # Verifica que los IDs existen en la base de datos
        try:
            productor = Productores.objects.get(id=productor_id)
        except Productores.DoesNotExist:
            return Response({"error": "El productor no existe"}, status=status.HTTP_404_NOT_FOUND)

        try:
            usuario = Usuarios.objects.get(id=usuario_id)  # Si Usuarios está mal escrito, cambia a User
        except Usuarios.DoesNotExist:
            return Response({"error": f"El usuario con ID {usuario_id} no existe"}, status=status.HTTP_404_NOT_FOUND)

        # Crear la entrega
        entrega = Entregas.objects.create(
            productor=productor,
            usuario=usuario,
            cantidad=cantidad,
            fecha=now().date()  # Agregar fecha actual
        )

        serializer = EntregaSerializer(entrega)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Registro de precios
class CrearPrecio(APIView):
    def post(self, request):
        precio = request.data.get("precio")

        if not precio:
            return Response({"error": "Debe ingresar un precio."}, status=status.HTTP_400_BAD_REQUEST)

        fecha = date.today()

        if Precios.objects.filter(fecha=fecha).exists():
            return Response({"error": "Ya existe un precio registrado para hoy."}, status=status.HTTP_400_BAD_REQUEST)

        precio = Precios.objects.create(
            fecha=fecha,
            precio=precio
        )

        serializer = PrecioSerializer(precio)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def get(self, request):
    ultimo_precio = Precios.objects.order_by('-fecha').first()
    if ultimo_precio:
        serializer = PrecioSerializer(ultimo_precio)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"precio": None}, status=status.HTTP_200_OK)

# Vista de Pagos

class ProductorListView(generics.ListCreateAPIView):
    queryset = Productores.objects.all()
    serializer_class = ProductorSerializer

class ProductorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Productores.objects.all()
    serializer_class = ProductorSerializer


# Iniciar sesión 
class IniciarSesion(APIView):
    def post(self, request):
        correo = request.data.get("correo")
        contrasenia = request.data.get("contrasenia")

        if not correo or not contrasenia:
            return Response({"error": "Correo y contraseña son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

        usuario = Usuarios.objects.filter(correo=correo).first()
        
        if usuario:
            # Verificar si el usuario está desactivado
            if not usuario.estado:
                return Response({"error": "Este usuario está desactivado. Contacte al administrador."}, status=status.HTTP_403_FORBIDDEN)

            if check_password(contrasenia, usuario.contrasenia):
                request.session["usuario_id"] = usuario.id  # Guarda el usuario en sesión
                return Response({
                    "mensaje": "Inicio de sesión exitoso",
                    "usuario_id": usuario.id,  # Incluimos el usuario_id en la respuesta
                    "redirect": "/admin"
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Contraseña incorrecta"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class CrearProductor(APIView):
    def post(self, request):
        serializer = ProductorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PagosListView(APIView):
    def get(self, request):
        productor_id = request.query_params.get('productor_id')
        fecha = request.query_params.get('fecha')

        if productor_id and fecha:
            pagos = Pagos.objects.filter(productor_id=productor_id, fecha=fecha)
            serializer = PagoSerializer(pagos, many=True)
            return Response(serializer.data)
        return Response({"error": "Datos incompletos"}, status=400)

class CrearPago(APIView):
    def post(self, request):
        productor_id = request.data.get("productor_id")
        fecha = request.data.get("fecha")
        total = request.data.get("total")

        if not productor_id or not fecha or not total:
            return Response({"error": "Faltan datos obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el productor existe
        productor = get_object_or_404(Productores, id=productor_id)

        # Asegurar que la fecha esté en formato correcto
        try:
            fecha = date.fromisoformat(fecha)  # Convertir a YYYY-MM-DD
        except ValueError:
            return Response({"error": "Formato de fecha incorrecto."}, status=status.HTTP_400_BAD_REQUEST)

        # 🔍 *Verificar si ya existe un pago para este productor en esta fecha*
        if Pagos.objects.filter(productor=productor, fecha=fecha).exists():
            return Response({"error": "⚠ Ya existe un pago registrado para este productor en esta fecha."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Crear el pago
        pago = Pagos.objects.create(
            productor=productor,
            fecha=fecha,
            total=total
        )

        serializer = PagoSerializer(pago)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class PrecioView(APIView):
    def get(self, request):
        precios = Precios.objects.all()
        serializer = PrecioSerializer(precios, many=True)
        return Response(serializer.data)

class PagoListView(generics.ListAPIView):
    queryset = Pagos.objects.all()
    serializer_class = PagoSerializer

class ReporteEntregasView(APIView):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "Debes proporcionar start_date y end_date"}, status=status.HTTP_400_BAD_REQUEST)

        entregas = Entregas.objects.filter(fecha__range=[start_date, end_date])
        serializer = EntregaSerializer(entregas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReportePagosView(APIView):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "Debes proporcionar start_date y end_date"}, status=status.HTTP_400_BAD_REQUEST)

        pagos = Pagos.objects.filter(fecha__range=[start_date, end_date])
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PredictProductionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            # Leer CSV
            df = pd.read_csv(file)
            df.columns = ['date', 'production']
            df['date'] = pd.to_datetime(df['date'])
            df = df.dropna()

            # Último valor conocido
            last_value = df['production'].iloc[-1] if not df.empty else 100
            date_range = pd.date_range(start=start_date, end=end_date)

            predictions = [
                {"date": date.strftime('%Y-%m-%d'), "production": float(last_value + np.random.uniform(-10, 10))}
                for date in date_range
            ]

            return Response({"prediction": predictions}, status=200)
        return Response(serializer.errors, status=400)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Usuarios

@api_view(['POST'])
def recover_password(request):
    correo = request.data.get("correo")

    if not correo:
        return Response({"error": "Debe ingresar un correo."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuarios.objects.get(correo=correo)
    except Usuarios.DoesNotExist:
        return Response({"error": "Correo no registrado."}, status=status.HTTP_404_NOT_FOUND)

    enlace_recuperacion = f"http://127.0.0.1:8000/usuarios/reset-password-confirm/"

    try:
        send_mail(
            subject="Recuperación de contraseña - Asociación San Pedro de Licto",
            message=f"Hola, {usuario.nombre}.\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n{enlace_recuperacion}\n\nSi no solicitaste este cambio, ignora este mensaje.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[correo],
            fail_silently=False,
        )
        return Response({"message": "Correo enviado con instrucciones para restablecer la contraseña."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"No se pudo enviar el correo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'lictoasociacionproductoresde@gmail.com'
EMAIL_HOST_PASSWORD = 'npolcwzvomodqmben'  # la de 16 caracteres
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Usuarios  # Usa tu modelo

@csrf_exempt
@api_view(['POST'])
def reset_password(request):
    correo = request.data.get("correo")
    nueva_contrasena = request.data.get("nueva_contrasena")

    if not correo or not nueva_contrasena:
        return Response({"error": "Correo y contraseña son obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuarios.objects.get(correo=correo)
        usuario.set_password(nueva_contrasena)
        usuario.save()
        return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)
    except Usuarios.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordResetConfirmView(APIView):
    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Contraseña actualizada exitosamente"})
        else:
            return Response({"error": "Token inválido o expirado"}, status=400)



##productor unica entrega 
from rest_framework.decorators import api_view
from .models import Entregas

@api_view(['GET'])
def verificar_entrega_diaria(request):
    productor_id = request.GET.get('productor_id')
    fecha = request.GET.get('fecha')

    if not productor_id or not fecha:
        return Response({"error": "Se requiere productor_id y fecha"}, status=status.HTTP_400_BAD_REQUEST)

    existe_entrega = Entregas.objects.filter(productor_id=productor_id, fecha=fecha).exists()

    return Response({"entregado": existe_entrega}, status=status.HTTP_200_OK)

##
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny

class SugerenciasAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nombre = request.data.get('nombre')
        mensaje = request.data.get('mensaje')

        if not nombre or not mensaje:
            return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)

        asunto = f"Nueva sugerencia de {nombre}"
        contenido = f"Has recibido una nueva sugerencia:\n\nNombre: {nombre}\nMensaje:\n{mensaje}"

        try:
            send_mail(
                asunto,
                contenido,
                'tu-email@gmail.com',  # debe ser igual a EMAIL_HOST_USER
                ['lictoasociacionproductoresde@gmail.com'],
                fail_silently=False,
            )
            return Response({'message': 'Correo enviado correctamente'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error enviando correo:", e)
            return Response({'error': f'Error enviando correo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
