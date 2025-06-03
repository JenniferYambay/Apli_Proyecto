from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from websitelicto import views

from .views import SugerenciasAPIView

from .views import ProductorListView, CrearPago, UsuarioDetailView, ProductorDetailView
from .views import CrearEntrega, PagoListView
from .views import UsuarioAPI, IniciarSesion, ToggleEstadoUsuario, CrearProductor
from .views import ReporteEntregasView, ReportePagosView

from .views import PrecioView, CrearPrecio  # Asegúrate de importar la nueva vista

from django.urls import path
from .views import PredictProductionView
from .views import recover_password

from .views import reset_password
from websitelicto.views import PasswordResetConfirmView
from .views import verificar_entrega_diaria


router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: HttpResponse("Bienvenido a la API. Visita /usuarios para explorar los usuarios.")),
    path('api/', include(router.urls)),  # Endpoints bajo /api/

    # Página principal con React
    path('', TemplateView.as_view(template_name="index.html")),

    path("api/entregas/", CrearEntrega.as_view(), name="crear_entrega"),

    path('api/precios/', PrecioView.as_view(), name='listar_precios'),  # GET para obtener precios
    path('api/precios/crear/', CrearPrecio.as_view(), name='crear_precio'),  # POST para crear precios

    path('usuarios/', UsuarioAPI.as_view(), name='usuarios_api'),
    path('usuarios/<int:pk>/toggle/', ToggleEstadoUsuario.as_view(), name='toggle_estado_usuario'),
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuario_detalle'),
    path('usuarios/login/', IniciarSesion.as_view(), name='iniciar_sesion'),
      path('usuarios/recover-password/', recover_password, name='recover_password'),

    path('api/productores/', ProductorListView.as_view(), name='productores-list'),
    path('api/productores/<int:pk>/', ProductorDetailView.as_view(), name='productor-detail'),
    path('api/productores/crear/', CrearProductor.as_view(), name='crear-productor'),
    
    path('api/pagos/', PagoListView.as_view(), name='pagos-list'),
    path("api/pagos/crear/", CrearPago.as_view(), name="crear-pago"),  # POST (crear pago)
    
    path("reportes/entregas/", ReporteEntregasView.as_view(), name="reporte-entregas"),
    path("reportes/pagos/", ReportePagosView.as_view(), name="reporte-pagos"),
  path('predict/', PredictProductionView.as_view(), name='predict'),

   path('api/verificar-entrega/', verificar_entrega_diaria),
    path('usuarios/reset-password/', reset_password, name='reset_password'),
     path('usuarios/reset-password-confirm/', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
 path('api/sugerencias/', SugerenciasAPIView.as_view(), name='sugerencias'),
]



#urlpatterns += [
   # path('usuarios/reset-password/', reset_password, name='reset_password'),
   #  path('usuarios/reset-password-confirm/', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
#]#
