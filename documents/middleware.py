"""
Middleware para forzar cambio de contraseña temporal
"""
from django.shortcuts import redirect

class ForcePasswordChangeMiddleware:
    """Fuerza el cambio de contraseña para usuarios con TempPass123!"""
    
    EXEMPT_PATHS = [
        '/logout/',
        '/change-password/',
        '/static/',
        '/media/',
        '/api/',
        '/admin/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Si el usuario está autenticado
        if request.user.is_authenticated:
            # Verificar si la ruta está en la lista de excepciones
            path = request.path
            is_exempt = any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
            
            if not is_exempt:
                # Verificar si tiene contraseña temporal
                if request.user.check_password("TempPass123!"):
                    return redirect('change_password_required')
        
        response = self.get_response(request)
        return response


