import pygame
import math
import numpy as np
from utils import ColorScheme, performance_monitor

def mandelbrot_iteration(c, max_iter):
    """
    Calcula el número de iteraciones para un punto c en el conjunto de Mandelbrot
    
    Args:
        c: Número complejo
        max_iter: Máximo número de iteraciones
        
    Returns:
        Número de iteraciones antes de divergencia
    """
    z = 0
    n = 0
    
    while abs(z) <= 2 and n < max_iter:
        z = z * z + c
        n += 1
    
    return n

def mandelbrot_smooth(c, max_iter):
    """
    Versión suavizada que retorna un valor continuo para mejor coloreo
    """
    z = 0
    n = 0
    
    while abs(z) <= 2 and n < max_iter:
        z = z * z + c
        n += 1
    
    if n < max_iter:
        # Suavizar usando logaritmos para transiciones continuas
        smooth_n = n + 1 - math.log(math.log(abs(z)))/math.log(2)
        return smooth_n
    
    return max_iter

def get_color_palette(iteration, max_iter, palette_type="default"):
    """
    Genera colores basados en el número de iteraciones
    
    Args:
        iteration: Número de iteraciones
        max_iter: Máximo de iteraciones
        palette_type: Tipo de paleta de colores
        
    Returns:
        Tupla RGB del color
    """
    if iteration >= max_iter:
        return (0, 0, 0)  # Negro para puntos en el conjunto
    
    # Normalizar iteración
    t = iteration / max_iter
    
    if palette_type == "fire":
        # Paleta de fuego (rojo-amarillo-blanco)
        if t < 0.5:
            r = int(255 * (2 * t))
            g = int(255 * (2 * t) ** 2)
            b = 0
        else:
            r = 255
            g = 255
            b = int(255 * (2 * t - 1))
        return (r, g, b)
    
    elif palette_type == "ocean":
        # Paleta oceánica (azul-cyan-blanco)
        r = int(t * 100)
        g = int(t * 200)
        b = int(255 * (0.5 + 0.5 * t))
        return (r, g, b)
    
    elif palette_type == "psychedelic":
        # Paleta psicodélica con funciones trigonométricas
        r = int(128 + 127 * math.sin(t * math.pi * 4))
        g = int(128 + 127 * math.sin(t * math.pi * 4 + 2))
        b = int(128 + 127 * math.sin(t * math.pi * 4 + 4))
        return (r, g, b)
    
    else:  # default
        # Paleta clásica en escala de grises con toque azul
        intensity = int(255 * t)
        return (intensity, intensity // 2, 255 - intensity)

def mandelbrot_optimized(surface, iterations, zoom=1.0, offset_x=0, offset_y=0, palette="default"):
    """
    Versión optimizada del conjunto de Mandelbrot
    
    Args:
        surface: Superficie donde renderizar
        iterations: Máximo número de iteraciones
        zoom: Factor de zoom
        offset_x, offset_y: Desplazamiento del centro
        palette: Tipo de paleta de colores
    """
    width, height = surface.get_size()
    max_iter = max(10, min(iterations, 1000))  # Limitar iteraciones para rendimiento
    
    # Parámetros de la región del plano complejo
    x_min, x_max = -2.5 / zoom + offset_x, 1.5 / zoom + offset_x
    y_min, y_max = -1.5 / zoom + offset_y, 1.5 / zoom + offset_y
    
    # Usar numpy para optimización si está disponible
    try:
        # Crear grilla de números complejos
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        
        # Inicializar Z y contador de iteraciones
        Z = np.zeros_like(C)
        M = np.zeros(C.shape, dtype=int)
        
        # Iteración vectorizada
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C[mask]
            M[mask] = i
        
        # Convertir a superficie pygame
        surface.lock()
        for y_pixel in range(height):
            for x_pixel in range(width):
                color = get_color_palette(M[y_pixel, x_pixel], max_iter, palette)
                surface.set_at((x_pixel, y_pixel), color)
        surface.unlock()
        
    except ImportError:
        # Fallback sin numpy
        mandelbrot_basic(surface, iterations, zoom, offset_x, offset_y, palette)

def mandelbrot_basic(surface, iterations, zoom=1.0, offset_x=0, offset_y=0, palette="default"):
    """
    Implementación básica sin dependencias externas
    """
    width, height = surface.get_size()
    max_iter = max(10, min(iterations, 500))
    
    # Región del plano complejo
    x_min, x_max = -2.5 / zoom + offset_x, 1.5 / zoom + offset_x
    y_min, y_max = -1.5 / zoom + offset_y, 1.5 / zoom + offset_y
    
    surface.lock()
    
    try:
        for x_pixel in range(width):
            for y_pixel in range(height):
                # Mapear pixel a coordenada compleja
                real = x_min + (x_max - x_min) * x_pixel / width
                imag = y_min + (y_max - y_min) * y_pixel / height
                c = complex(real, imag)
                
                # Calcular iteraciones
                iter_count = mandelbrot_iteration(c, max_iter)
                
                # Obtener color
                color = get_color_palette(iter_count, max_iter, palette)
                surface.set_at((x_pixel, y_pixel), color)
    
    finally:
        surface.unlock()

def mandelbrot_julia_morph(surface, iterations, morph_factor=0.0):
    """
    Morfeo entre conjunto de Mandelbrot y Julia
    
    Args:
        surface: Superficie donde renderizar
        iterations: Número de iteraciones
        morph_factor: 0.0 = Mandelbrot, 1.0 = Julia
    """
    width, height = surface.get_size()
    max_iter = max(10, min(iterations, 200))
    
    # Parámetro Julia que cambia con morph_factor
    julia_c = complex(-0.7 + morph_factor * 0.4, 0.27015 * morph_factor)
    
    surface.lock()
    
    try:
        for x_pixel in range(width):
            for y_pixel in range(height):
                # Coordenadas complejas
                real = 3.0 * (x_pixel - width / 2) / (width * 0.5)
                imag = 2.0 * (y_pixel - height / 2) / (height * 0.5)
                
                if morph_factor < 0.5:
                    # Más Mandelbrot
                    c = complex(real, imag)
                    z = 0
                else:
                    # Más Julia
                    c = julia_c
                    z = complex(real, imag)
                
                # Iteración estándar
                n = 0
                while abs(z) <= 2 and n < max_iter:
                    z = z * z + c
                    n += 1
                
                # Color con efecto de morfeo
                color = get_color_palette(n, max_iter, "psychedelic")
                surface.set_at((x_pixel, y_pixel), color)
    
    finally:
        surface.unlock()

def draw(surface, iterations):
    """
    Función principal para dibujar el conjunto de Mandelbrot
    
    Args:
        surface: Superficie de pygame donde dibujar
        iterations: Número máximo de iteraciones
    """
    start_time = pygame.time.get_ticks()
    
    # Limpiar superficie
    surface.fill((0, 0, 0))
    
    # Seleccionar método según número de iteraciones
    if iterations <= 50:
        palette = "default"
        mandelbrot_basic(surface, iterations, 1.0, 0, 0, palette)
    elif iterations <= 100:
        palette = "fire"
        mandelbrot_basic(surface, iterations, 1.0, 0, 0, palette)
    else:
        palette = "ocean"
        try:
            mandelbrot_optimized(surface, iterations, 1.0, 0, 0, palette)
        except:
            mandelbrot_basic(surface, iterations, 1.0, 0, 0, palette)
    
    # Registrar tiempo de renderizado
    render_time = (pygame.time.get_ticks() - start_time) / 1000.0
    performance_monitor.add_render_time(render_time)
    
    # Mostrar información de rendimiento si el renderizado es lento
    if render_time > 2.0:
        font = pygame.font.Font(None, 24)
        warning_text = font.render(f"Renderizado lento: {render_time:.1f}s", True, ColorScheme.WARNING)
        surface.blit(warning_text, (10, 10))

def draw_zoomed(surface, iterations, zoom_center=(0, 0), zoom_level=1.0):
    """
    Dibuja el conjunto con zoom hacia una región específica
    
    Args:
        surface: Superficie donde dibujar
        iterations: Número de iteraciones
        zoom_center: Centro del zoom (parte real, parte imaginaria)
        zoom_level: Factor de zoom
    """
    mandelbrot_basic(surface, iterations, zoom_level, zoom_center[0], zoom_center[1])

def get_interesting_regions():
    """
    Retorna regiones interesantes para explorar en el conjunto de Mandelbrot
    """
    return [
        {"name": "Vista completa", "center": (0, 0), "zoom": 1.0},
        {"name": "Bahía principal", "center": (-0.75, 0), "zoom": 4.0},
        {"name": "Valle de caballos marinos", "center": (-0.745, 0.1), "zoom": 50.0},
        {"name": "Espiral de Misiurewicz", "center": (-0.77568377, 0.13646737), "zoom": 200.0},
        {"name": "Mini Mandelbrot", "center": (-0.16, 1.0407), "zoom": 100.0},
        {"name": "Antena", "center": (-1.25, 0), "zoom": 10.0}
    ]

def get_fractal_info():
    """Retorna información sobre el conjunto de Mandelbrot"""
    return {
        "name": "Conjunto de Mandelbrot",
        "description": "Conjunto fractal descubierto por Benoit Mandelbrot",
        "formula": "z(n+1) = z(n)² + c",
        "complexity": "O(width × height × iterations)",
        "recommended_max_iterations": 1000,
        "mathematical_properties": [
            "Frontera fractal con dimensión ≈ 2",
            "Conectado pero no simplemente conectado",
            "Contiene copias infinitas de sí mismo"
        ],
        "interesting_points": get_interesting_regions()
    }