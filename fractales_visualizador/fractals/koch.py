import pygame
import math
from utils import ColorScheme

def koch_curve(p1, p2, depth, surface, color=None, line_width=1):
    """
    Genera la curva de Koch recursivamente con mejor calidad visual
    
    Args:
        p1, p2: Puntos inicial y final del segmento
        depth: Profundidad de recursión
        surface: Superficie donde dibujar
        color: Color de la línea (opcional)
        line_width: Grosor de la línea
    """
    if color is None:
        color = ColorScheme.WHITE
    
    if depth == 0:
        # Caso base: dibujar línea simple
        try:
            # Usar coordenadas enteras para mejor compatibilidad
            start_pos = (int(round(p1[0])), int(round(p1[1])))
            end_pos = (int(round(p2[0])), int(round(p2[1])))
            
            # Verificar que las coordenadas estén en rango válido
            width, height = surface.get_size()
            if (0 <= start_pos[0] <= width and 0 <= start_pos[1] <= height and
                0 <= end_pos[0] <= width and 0 <= end_pos[1] <= height):
                
                # Dibujar línea estándar
                pygame.draw.line(surface, color, start_pos, end_pos, line_width)
                    
        except (ValueError, OverflowError, pygame.error):
            # Manejar casos de overflow o errores de pygame
            pass
    else:
        # Calcular puntos intermedios con mayor precisión
        x1, y1 = float(p1[0]), float(p1[1])
        x5, y5 = float(p2[0]), float(p2[1])
        
        # Dividir el segmento en tres partes iguales
        dx = (x5 - x1) / 3.0
        dy = (y5 - y1) / 3.0
        
        # Puntos del primer y segundo tercio
        x2, y2 = x1 + dx, y1 + dy
        x4, y4 = x1 + 2.0 * dx, y1 + 2.0 * dy
        
        # Punto del pico del triángulo equilátero
        # Calcular el centro del segmento medio
        mid_x = (x2 + x4) * 0.5
        mid_y = (y2 + y4) * 0.5
        
        # Vector perpendicular para formar el triángulo equilátero
        # Usar la altura de un triángulo equilátero: sqrt(3)/2 * lado
        side_length = math.sqrt(dx * dx + dy * dy)
        height = side_length * math.sqrt(3.0) * 0.5
        
        # Vector unitario perpendicular
        if side_length > 0:
            perp_x = -(dy / side_length) * height
            perp_y = (dx / side_length) * height
        else:
            perp_x = perp_y = 0
        
        x3 = mid_x + perp_x
        y3 = mid_y + perp_y
        
        # Llamadas recursivas para los cuatro segmentos
        koch_curve((x1, y1), (x2, y2), depth - 1, surface, color, line_width)
        koch_curve((x2, y2), (x3, y3), depth - 1, surface, color, line_width)
        koch_curve((x3, y3), (x4, y4), depth - 1, surface, color, line_width)
        koch_curve((x4, y4), (x5, y5), depth - 1, surface, color, line_width)

def koch_snowflake(center, radius, depth, surface, color=None, line_width=1):
    """
    Dibuja un copo de nieve de Koch completo con mejor precisión
    
    Args:
        center: Centro del copo de nieve
        radius: Radio del triángulo circunscrito
        depth: Profundidad de las curvas de Koch
        surface: Superficie donde dibujar
        color: Color del copo (opcional)
        line_width: Grosor de la línea
    """
    if color is None:
        color = ColorScheme.CYAN
    
    cx, cy = float(center[0]), float(center[1])
    radius = float(radius)
    
    # Calcular los tres vértices del triángulo equilátero
    angle_offset = -math.pi * 0.5  # Empezar con un vértice hacia arriba
    vertices = []
    
    for i in range(3):
        angle = angle_offset + i * 2.0 * math.pi / 3.0
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    
    # Dibujar las tres curvas de Koch que forman el copo
    for i in range(3):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % 3]
        koch_curve(p1, p2, depth, surface, color, line_width)

def draw(surface, iterations):
    """
    Función principal para dibujar la curva de Koch con mejor calidad
    
    Args:
        surface: Superficie de pygame donde dibujar
        iterations: Número de iteraciones/profundidad
    """
    # Limpiar superficie
    surface.fill((0, 0, 0, 0))
    
    width, height = surface.get_size()
    
    # Configuración adaptativa basada en el tamaño de la ventana
    margin = min(width, height) * 0.1
    
    # Ajustar grosor de línea según el tamaño y profundidad
    base_line_width = max(1, min(3, width // 400))
    line_width = max(1, base_line_width - iterations // 3)
    
    # Modo 1: Curva de Koch simple (horizontal)
    if iterations <= 4:
        # Centrar mejor la curva
        y_center = height * 0.5
        line_length = width - 2 * margin
        
        p1 = (margin, y_center)
        p2 = (margin + line_length, y_center)
        
        # Color que cambia con las iteraciones con mejor progresión
        intensity = min(255, 120 + iterations * 25)
        color = (intensity, intensity, 255)
        
        koch_curve(p1, p2, iterations, surface, color, line_width)
    
    # Modo 2: Copo de nieve de Koch (para iteraciones más altas)
    else:
        center = (width * 0.5, height * 0.5)
        # Ajustar radio para que se vea completo con margen
        radius = min(width, height) * 0.35
        
        # Color especial para el copo de nieve con variación
        depth_factor = min(1.0, (iterations - 4) / 3.0)
        color_variation = int(depth_factor * 50)
        color = (
            max(0, ColorScheme.CYAN[0] - color_variation),
            ColorScheme.CYAN[1],
            min(255, ColorScheme.CYAN[2] + color_variation)
        )
        
        koch_snowflake(center, radius, iterations - 4, surface, color, line_width)
    
    # Información de rendimiento para iteraciones altas
    if iterations > 6:
        try:
            font = pygame.font.Font(None, 24)
            complexity = 4 ** iterations
            warning_text = "Complejidad alta: " + str(complexity) + " segmentos"
            text_surface = font.render(warning_text, True, ColorScheme.WARNING)
            surface.blit(text_surface, (10, 10))
        except:
            pass

def draw_interactive(surface, iterations, mouse_pos=None, animation_time=0):
    """
    Versión interactiva mejorada que responde al mouse y animaciones
    
    Args:
        surface: Superficie donde dibujar
        iterations: Profundidad de la curva
        mouse_pos: Posición del mouse para efectos interactivos
        animation_time: Tiempo para animaciones
    """
    surface.fill((0, 0, 0, 0))
    
    width, height = surface.get_size()
    
    # Efecto de color animado más suave
    time_factor = math.sin(animation_time * 0.002) * 0.3 + 0.7
    base_color = (
        int(80 + time_factor * 175),
        int(120 + time_factor * 135),
        255
    )
    
    # Grosor de línea adaptativo
    line_width = max(1, min(3, width // 300))
    
    # Adaptación al mouse mejorada
    if mouse_pos and iterations <= 4:
        mouse_x, mouse_y = mouse_pos
        
        # Efecto más sutil y suave
        center_x, center_y = width * 0.5, height * 0.5
        offset_x = (mouse_x - center_x) / width
        offset_y = (mouse_y - center_y) / height
        
        # Curvatura adaptativa basada en la posición del mouse
        curve_strength = 0.2 * math.sqrt(offset_x * offset_x + offset_y * offset_y)
        curve_strength = min(curve_strength, 0.3)
        
        y_base = height * 0.5
        y_offset = offset_y * height * 0.1
        
        p1 = (width * 0.1, y_base + y_offset + curve_strength * height * 0.2)
        p2 = (width * 0.9, y_base + y_offset - curve_strength * height * 0.2)
        
        koch_curve(p1, p2, iterations, surface, base_color, line_width)
    else:
        # Modo estándar
        draw(surface, iterations)

def get_fractal_info():
    """Retorna información detallada sobre la curva de Koch"""
    return {
        "name": "Curva de Koch",
        "description": "Fractal clásico creado por Helge von Koch en 1904",
        "complexity": "O(4^n) donde n es la profundidad",
        "recommended_max_depth": 7,
        "mathematical_properties": [
            "Longitud infinita con área finita",
            "Dimensión fractal ≈ 1.26186",
            "Auto-similar a diferentes escalas",
            "Perímetro infinito del copo de nieve"
        ],
        "construction_rule": "Cada segmento se divide en 3 partes, la central se reemplaza por 2 lados de un triángulo equilátero",
        "scaling_factor": 1/3,
        "rotation_angle": 60  # grados
    }

def calculate_length(depth, initial_length=1.0):
    """Calcula la longitud teórica de la curva de Koch"""
    if depth == 0:
        return initial_length
    return initial_length * ((4.0 / 3.0) ** depth)

def calculate_points_count(depth):
    """Calcula el número de puntos en la curva"""
    if depth == 0:
        return 2
    # Fórmula: 2 + sum(3 * 4^i for i in range(depth))
    return 2 + 3 * (4 ** depth - 1) // 3

def get_performance_metrics(depth):
    """Retorna métricas de rendimiento para una profundidad dada"""
    points = calculate_points_count(depth)
    segments = points - 1 if points > 1 else 0
    
    return {
        "depth": depth,
        "points": points,
        "segments": segments,
        "relative_length": calculate_length(depth),
        "memory_estimate_kb": (points * 16) / 1024,  # Estimación aproximada
        "recommended": depth <= 7
    }

def optimize_depth_for_resolution(width, height):
    """Sugiere la profundidad óptima basada en la resolución"""
    pixel_count = width * height
    
    if pixel_count < 100000:  # Resolución baja
        return 4
    elif pixel_count < 500000:  # Resolución media
        return 5
    elif pixel_count < 2000000:  # Resolución alta
        return 6
    else:  # Resolución muy alta
        return 7