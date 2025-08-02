import pygame
import math
import random
from utils import ColorScheme

def draw_triangle(surface, p1, p2, p3, color=None, filled=False, line_width=1):
    """
    Dibuja un triángulo en la superficie con mejor precisión
    
    Args:
        surface: Superficie donde dibujar
        p1, p2, p3: Vértices del triángulo
        color: Color del triángulo
        filled: Si True, rellena el triángulo
        line_width: Grosor de la línea (si no está relleno)
    """
    if color is None:
        color = ColorScheme.WHITE
    
    try:
        # Convertir a coordenadas enteras con redondeo preciso
        points = [
            (int(round(p1[0])), int(round(p1[1]))),
            (int(round(p2[0])), int(round(p2[1]))),
            (int(round(p3[0])), int(round(p3[1])))
        ]
        
        # Verificar que los puntos estén dentro de los límites
        width, height = surface.get_size()
        valid_points = all(
            0 <= x <= width and 0 <= y <= height 
            for x, y in points
        )
        
        if valid_points and len(set(points)) == 3:  # Verificar que no sean colineales
            if filled:
                pygame.draw.polygon(surface, color, points)
            else:
                pygame.draw.polygon(surface, color, points, max(1, line_width))
            
    except (ValueError, OverflowError, pygame.error):
        # Manejar coordenadas inválidas silenciosamente
        pass

def sierpinski_triangle(surface, p1, p2, p3, depth, color=None, variant="outline", min_size=2.0):
    """
    Genera el triángulo de Sierpinski recursivamente con control de calidad
    
    Args:
        surface: Superficie donde dibujar
        p1, p2, p3: Vértices del triángulo inicial
        depth: Profundidad de recursión
        color: Color del triángulo
        variant: "outline", "filled", "gradient"
        min_size: Tamaño mínimo de triángulo para dibujar (en píxeles)
    """
    if color is None:
        color = ColorScheme.WHITE
    
    # Calcular el tamaño del triángulo actual
    triangle_size = max(
        abs(p1[0] - p2[0]), abs(p1[0] - p3[0]), abs(p2[0] - p3[0]),
        abs(p1[1] - p2[1]), abs(p1[1] - p3[1]), abs(p2[1] - p3[1])
    )
    
    # No dibujar triángulos demasiado pequeños
    if triangle_size < min_size:
        return
    
    if depth == 0:
        # Caso base: dibujar triángulo simple
        if variant == "filled":
            draw_triangle(surface, p1, p2, p3, color, filled=True)
        elif variant == "gradient":
            # Efecto de gradiente basado en el tamaño
            intensity = max(50, min(255, int(triangle_size * 2)))
            gradient_color = (intensity, intensity // 2, 255 - intensity // 2)
            draw_triangle(surface, p1, p2, p3, gradient_color, filled=True)
        else:  # outline
            # Ajustar grosor de línea según el tamaño
            line_width = max(1, int(triangle_size / 100))
            draw_triangle(surface, p1, p2, p3, color, filled=False, line_width=line_width)
    else:
        # Calcular puntos medios de cada lado con precisión flotante
        m1 = ((p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5)
        m2 = ((p2[0] + p3[0]) * 0.5, (p2[1] + p3[1]) * 0.5)
        m3 = ((p3[0] + p1[0]) * 0.5, (p3[1] + p1[1]) * 0.5)
        
        # Recursión en los tres subtriángulos externos
        sierpinski_triangle(surface, p1, m1, m3, depth - 1, color, variant, min_size)
        sierpinski_triangle(surface, m1, p2, m2, depth - 1, color, variant, min_size)
        sierpinski_triangle(surface, m3, m2, p3, depth - 1, color, variant, min_size)

def sierpinski_chaos_game(surface, iterations, color=None, fade_effect=False):
    """
    Genera el triángulo de Sierpinski usando el "juego del caos" mejorado
    
    Args:
        surface: Superficie donde dibujar
        iterations: Número de puntos a generar
        color: Color de los puntos
        fade_effect: Si True, aplica efecto de desvanecimiento
    """
    if color is None:
        color = ColorScheme.GREEN
    
    width, height = surface.get_size()
    
    # Vértices del triángulo principal con mejor centrado
    size = min(width, height) * 0.75
    center_x, center_y = width * 0.5, height * 0.5
    
    # Triángulo equilátero centrado
    height_triangle = size * math.sqrt(3) * 0.5
    vertices = [
        (center_x, center_y - height_triangle * 0.667),  # Vértice superior
        (center_x - size * 0.5, center_y + height_triangle * 0.333),  # Inferior izquierdo
        (center_x + size * 0.5, center_y + height_triangle * 0.333)   # Inferior derecho
    ]
    
    # Punto inicial aleatorio dentro del triángulo
    current_point = [
        center_x + random.uniform(-size * 0.25, size * 0.25),
        center_y + random.uniform(-height_triangle * 0.25, height_triangle * 0.25)
    ]
    
    # Optimización: preparar superficie para dibujo rápido
    surface.lock()
    
    try:
        for i in range(iterations):
            # Elegir vértice aleatorio
            target_vertex = random.choice(vertices)
            
            # Mover hacia el punto medio
            current_point[0] = (current_point[0] + target_vertex[0]) * 0.5
            current_point[1] = (current_point[1] + target_vertex[1]) * 0.5
            
            # Dibujar punto después de estabilización
            if i > 20:  # Más iteraciones de estabilización
                x, y = int(round(current_point[0])), int(round(current_point[1]))
                if 0 <= x < width and 0 <= y < height:
                    if fade_effect and i % 3 == 0:
                        # Efecto de desvanecimiento ocasional
                        alpha = max(100, 255 - (i // 1000))
                        fade_color = (*color[:3], alpha) if len(color) > 3 else color
                        surface.set_at((x, y), fade_color)
                    else:
                        surface.set_at((x, y), color)
    
    finally:
        surface.unlock()

def sierpinski_carpet(surface, x, y, size, depth, color=None):
    """
    Genera la alfombra de Sierpinski (variante 2D) mejorada
    
    Args:
        surface: Superficie donde dibujar
        x, y: Posición inicial
        size: Tamaño del cuadrado
        depth: Profundidad de recursión
        color: Color de relleno
    """
    if color is None:
        color = ColorScheme.MAGENTA
    
    # No dibujar cuadrados demasiado pequeños
    if size < 2:
        return
    
    if depth == 0:
        # Dibujar cuadrado relleno con bordes suaves
        rect = pygame.Rect(int(round(x)), int(round(y)), max(1, int(round(size))), max(1, int(round(size))))
        try:
            pygame.draw.rect(surface, color, rect)
        except pygame.error:
            pass
    else:
        # Dividir en 9 subcuadrados, omitir el central
        sub_size = size / 3.0
        
        for i in range(3):
            for j in range(3):
                # Omitir el cuadrado central (1,1)
                if i == 1 and j == 1:
                    continue
                
                new_x = x + i * sub_size
                new_y = y + j * sub_size
                sierpinski_carpet(surface, new_x, new_y, sub_size, depth - 1, color)

def draw(surface, iterations):
    """
    Función principal mejorada para dibujar el triángulo de Sierpinski
    
    Args:
        surface: Superficie de pygame donde dibujar
        iterations: Número de iteraciones/profundidad
    """
    surface.fill((0, 0, 0, 0))
    
    width, height = surface.get_size()
    
    # Configuración adaptativa mejorada
    size = min(width, height) * 0.8
    center_x, center_y = width * 0.5, height * 0.5
    
    # Calcular vértices de triángulo equilátero perfecto
    height_triangle = size * math.sqrt(3) * 0.5
    p1 = (center_x, center_y - height_triangle * 0.667)        # Vértice superior
    p2 = (center_x - size * 0.5, center_y + height_triangle * 0.333)  # Inferior izquierdo
    p3 = (center_x + size * 0.5, center_y + height_triangle * 0.333)  # Inferior derecho
    
    # Calcular tamaño mínimo de triángulo basado en resolución
    min_triangle_size = max(1.0, min(width, height) / (3 ** min(iterations, 6)))
    
    # Seleccionar método y color según iteraciones
    if iterations <= 7:
        # Método recursivo para iteraciones bajas/medias
        # Color que evoluciona con la profundidad
        color_intensity = max(150, 255 - iterations * 15)
        color = (color_intensity, color_intensity, 255)
        
        sierpinski_triangle(surface, p1, p2, p3, iterations, color, "outline", min_triangle_size)
    else:
        # Juego del caos para iteraciones altas (más eficiente y detallado)
        num_points = min(100000, iterations * 8000)
        sierpinski_chaos_game(surface, num_points, ColorScheme.GREEN, fade_effect=True)
    
    # Información de estado para iteraciones altas
    if iterations > 8:
        try:
            font = pygame.font.Font(None, 20)
            triangle_count = 3 ** iterations
            info_text = "Triangulos: " + str(triangle_count)
            text_surface = font.render(info_text, True, ColorScheme.WARNING)
            surface.blit(text_surface, (10, 10))
        except:
            pass

def draw_animated(surface, iterations, animation_time=0):
    """
    Versión animada mejorada del triángulo de Sierpinski
    
    Args:
        surface: Superficie donde dibujar
        iterations: Profundidad
        animation_time: Tiempo para animaciones
    """
    surface.fill((0, 0, 0, 0))
    
    width, height = surface.get_size()
    
    # Efecto de rotación más suave y controlado
    angle = math.sin(animation_time * 0.0008) * 0.15  # Rotación más lenta y sutil
    center_x, center_y = width * 0.5, height * 0.5
    
    # Efecto de pulsación del tamaño
    size_factor = 1.0 + math.sin(animation_time * 0.001) * 0.1
    size = min(width, height) * 0.8 * size_factor
    
    # Calcular vértices con rotación
    height_triangle = size * math.sqrt(3) * 0.5
    base_vertices = [
        (0, -height_triangle * 0.667),
        (-size * 0.5, height_triangle * 0.333),
        (size * 0.5, height_triangle * 0.333)
    ]
    
    rotated_vertices = []
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    
    for vx, vy in base_vertices:
        # Aplicar rotación con matemática optimizada
        rx = vx * cos_a - vy * sin_a
        ry = vx * sin_a + vy * cos_a
        rotated_vertices.append((center_x + rx, center_y + ry))
    
    # Color animado más fluido
    time_factor = math.sin(animation_time * 0.0015) * 0.5 + 0.5
    animated_color = (
        int(120 + time_factor * 135),
        int(80 + time_factor * 175),
        255
    )
    
    # Tamaño mínimo adaptativo
    min_size = max(1.0, min(width, height) / (3 ** min(iterations, 6)))
    
    sierpinski_triangle(surface, *rotated_vertices, iterations, animated_color, "outline", min_size)

def draw_multicolor(surface, iterations):
    """
    Versión multicolor mejorada del triángulo de Sierpinski
    """
    surface.fill((0, 0, 0, 0))
    
    width, height = surface.get_size()
    size = min(width, height) * 0.8
    center_x, center_y = width * 0.5, height * 0.5
    
    # Vértices del triángulo con mejor centrado
    height_triangle = size * math.sqrt(3) * 0.5
    vertices = [
        (center_x, center_y - height_triangle * 0.667),
        (center_x - size * 0.5, center_y + height_triangle * 0.333),
        (center_x + size * 0.5, center_y + height_triangle * 0.333)
    ]
    
    # Paleta de colores mejorada
    colors = [
        ColorScheme.CYAN,
        ColorScheme.MAGENTA, 
        ColorScheme.YELLOW,
        (255, 128, 0),  # Naranja
        (128, 255, 128),  # Verde claro
        (255, 128, 255)   # Rosa
    ]
    
    min_size = max(1.0, min(width, height) / (3 ** min(iterations, 6)))
    
    def sierpinski_multicolor(p1, p2, p3, depth, color_index, level=0):
        # Calcular tamaño actual
        triangle_size = max(
            abs(p1[0] - p2[0]), abs(p1[0] - p3[0]), abs(p2[0] - p3[0]),
            abs(p1[1] - p2[1]), abs(p1[1] - p3[1]), abs(p2[1] - p3[1])
        )
        
        if triangle_size < min_size:
            return
            
        if depth == 0:
            color = colors[color_index % len(colors)]
            # Ajustar intensidad según el nivel
            intensity_factor = max(0.3, 1.0 - level * 0.1)
            adjusted_color = tuple(int(c * intensity_factor) for c in color)
            
            line_width = max(1, int(triangle_size / 100))
            draw_triangle(surface, p1, p2, p3, adjusted_color, filled=False, line_width=line_width)
        else:
            m1 = ((p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5)
            m2 = ((p2[0] + p3[0]) * 0.5, (p2[1] + p3[1]) * 0.5)
            m3 = ((p3[0] + p1[0]) * 0.5, (p3[1] + p1[1]) * 0.5)
            
            sierpinski_multicolor(p1, m1, m3, depth - 1, color_index, level + 1)
            sierpinski_multicolor(m1, p2, m2, depth - 1, color_index + 1, level + 1)
            sierpinski_multicolor(m3, m2, p3, depth - 1, color_index + 2, level + 1)
    
    sierpinski_multicolor(*vertices, iterations, 0)

def get_fractal_info():
    """Retorna información detallada sobre el triángulo de Sierpinski"""
    return {
        "name": "Triángulo de Sierpinski",
        "description": "Fractal creado por Wacław Sierpiński en 1915",
        "complexity": "O(3^n) donde n es la profundidad",
        "recommended_max_depth": 8,
        "mathematical_properties": [
            "Área total tiende a 0 con iteraciones infinitas",
            "Dimensión fractal = log(3)/log(2) ≈ 1.585",
            "Auto-similar con factor de escala 1/2",
            "Perímetro infinito con área finita"
        ],
        "methods": [
            "Recursión geométrica",
            "Juego del caos (Chaos Game)",
            "Sistema de funciones iteradas (IFS)",
            "Eliminación de triángulos centrales"
        ],
        "construction": "Empezar con triángulo, conectar puntos medios, eliminar triángulo central, repetir"
    }

def calculate_triangle_count(depth):
    """Calcula el número de triángulos en la iteración dada"""
    if depth == 0:
        return 1
    return 3 ** depth

def calculate_area_ratio(depth):
    """Calcula la proporción de área cubierta"""
    if depth == 0:
        return 1.0
    return (3.0 / 4.0) ** depth

def calculate_perimeter_ratio(depth):
    """Calcula la proporción del perímetro"""
    if depth == 0:
        return 1.0
    return (3.0 / 2.0) ** depth

def get_zoom_level_info(width, height, iterations):
    """Calcula información sobre el nivel de zoom recomendado"""
    resolution = width * height
    triangle_size = min(width, height) / (3 ** iterations)
    
    return {
        "triangle_size_pixels": triangle_size,
        "visible_detail": triangle_size >= 1.0,
        "recommended_zoom": max(1.0, 2.0 / triangle_size) if triangle_size < 2.0 else 1.0,
        "total_triangles": calculate_triangle_count(iterations),
        "visible_triangles": min(calculate_triangle_count(iterations), resolution // 4)
    }