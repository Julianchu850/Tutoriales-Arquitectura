from django.views import View
from .infra.factories import PaymentFactory
from .services import CompraService
import datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .services import CompraRapidaService, InventarioService, CompraService
from .models import Libro, Inventario, Orden

class CompraView(View):
    """
    CBV: Vista Basada en Clases.
    Actúa como un "Portero": recibe la petición y delega al servicio.
    """

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': f"¡Gracias por su compra! Total: ${total}",
                    'total': total,
                },
            )
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)


from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Libro, Inventario


class CompraRapidaView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def seteup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraRapidaService(procesador_pago=gateway)

    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = float(libro.precio) * 1.19

        return render(request, self.template_name, {
            'libro': libro,
            'total': total
        })

    def post(self, request, libro_id):
        # La lógica de negocio aún reside aquí, pero separada del GET
        libro = get_object_or_404(Libro, id=libro_id)
        inv = Inventario.objects.get(libro=libro)

        if inv.cantidad > 0:
            total = float(libro.precio) * 1.19
            # ... proceso de compra ...
            return HttpResponse("Comprado via CBV")

        return HttpResponse("Error", status=400)
    
    def post(self, request, libro_id):
        service = self.seteup_service()

        try:
            total = service.procesar(libro_id)
            return HttpResponse(f"Compra exitosa. Total: ${total}")
        except ValueError as e:
         return HttpResponse(str(e), status=400)
        

class InventarioView(View):
    template_name = 'tienda_app/inventario.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InventarioService()

    def get(self, request):
        inventario = self.service.obtener_inventario()

        return render(request, self.template_name, {
            'inventario': inventario
        })

    def post(self, request):
        libro_id = request.POST.get('libro_id')
        cantidad = int(request.POST.get('cantidad'))

        self.service.actualizar_cantidad(libro_id, cantidad)

        return redirect(request.path)