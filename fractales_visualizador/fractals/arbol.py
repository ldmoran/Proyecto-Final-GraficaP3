import pygame
import math
import random
from utils import ColorScheme

class TreeParameters:
    """Parámetros configurables para diferentes tipos de árboles optimizados"""
    
    # Árbol clásico
    CLASSIC = {
        "angle_left": 25,
        "angle_right": 25,
        "length_factor": 0.7,
        "thickness_factor": 0.8,
        "branches": 2,
        "min_length": 3.0
    }
    
    # Árbol asimétrico
    ASYMMETRIC = {
        "angle_left": 30,
        "angle_right": 20,
        "length_factor": 0.75,
        "thickness_factor": 0.9,
        "branches": 2,
        "min_length": 2.5
    }
    
    # Árbol con muchas ramas
    BUSHY = {
        "angle_left": 20,
        "angle_right": 20,
        "length_factor": 0.6,
        "thickness_factor": 0.7,
        "branches": 3,
        "min_length": 2.0
    }
    
    # Sauce llorón
    WILLOW = {
        "angle_left": 15,
        "angle_right": 15,
        "length_factor": 0.8,
        "thickness_factor": 0.9,
        "branches": 2,
        "droop_factor": 1.5,
        "min_length": 4.0
    }
    
    # Roble robusto
    OAK = {
        "angle_left": 35,
        "angle_right": 35,
        "length_factor": 0.65,
        "thickness_factor": 1.2,
        "branches": 2,
        "min_length": 3.5
    }
    
    # Pino
    PINE = {
        "angle_left": 15,
        "angle_right": 15,
        "length_factor": 0.8,
        "thickness_factor": 0.6,
        "branches": 2,
        "min_length": 2.0
    }

def draw_tree_recursive(surface, x, y, angle, depth, length, params=None, color_mode="gradient", min_branch_size=1.0):
    """
    Dibuja un árbol fractal recursivamente con mejor calidad y optimización
    
    Args:
        surface: Superficie donde dibujar
        x, y: Posición inicial (coordenadas flotantes para precisión)
        angle: Ángulo de la rama en grados
        depth: Profundidad de recursión restante
        length: Longitud de la rama actual
        params: Parámetros del árbol
        color_mode: Modo de coloreo
        min_branch_size: Tamaño mínimo de rama en píxeles
    """
    if params is None:
        params = TreeParameters.CLASSIC
    
    # Condiciones de parada optimizadas
    min_length_threshold = params.get("min_length", 2.0)
    if depth <= 0 or length < max(min_length_threshold, min_branch_size):
        return
    
    # Calcular punto final de la rama con precisión flotante
    angle_rad = math.radians(angle)
    x2 = x + math.cos(angle_rad) * length
    y2 = y - math.sin(angle_rad) * length
    
    # Calcular grosor de la línea de forma más natural
    base_thickness = params.get("thickness_factor", 0.8)
    thickness = max(1, int(depth * base_thickness + length / 20))
    
    # Sistema de colores mejorado
    color = get_branch_color(depth, length, color_mode, params)
    
    # Dibujar la rama con validación de coordenadas
    try:
        start_pos = (int(round(x)), int(round(y)))
        end_pos = (int(round(x2)), int(round(y2)))
        
        # Verificar que las coordenadas estén en rango válido
        width, height = surface.get_size()
        if (0 <= start_pos[0] <= width and 0 <= start_pos[1] <= height and
            0 <= end_pos[0] <= width and 0 <= end_pos[1] <= height):
            
            pygame.draw.line(surface, color, start_pos, end_pos, thickness)
            
            # Añadir efecto de textura para ramas gruesas
            if thickness > 3 and depth > 5:
                # Dibujar línea central más oscura para efecto 3D
                darker_color = tuple(max(0, c - 30) for c in color)
                pygame.draw.line(surface, darker_color, start_pos, end_pos, max(1, thickness - 2))
        
    except (ValueError, OverflowError, pygame.error):
        return
    
    # Recursión para ramas hijas con mejores parámetros
    if depth > 0:
        branch_count = params.get("branches", 2)
        length_factor = params.get("length_factor", 0.7)
        
        if branch_count == 2:
            # Árbol binario tradicional optimizado
            new_length = length * length_factor
            
            # Aplicar factor de sauce llorón si existe
            droop_factor = params.get("droop_factor", 1.0)
            if droop_factor > 1.0 and depth < 4:
                # Las ramas cuelgan más hacia abajo
                angle_modifier = (4 - depth) * 5 * (droop_factor - 1.0)
            else:
                angle_modifier = 0
            
            # Rama izquierda
            left_angle = angle + params.get("angle_left", 25) - angle_modifier
            draw_tree_recursive(surface, x2, y2, left_angle, depth - 1, new_length, 
                              params, color_mode, min_branch_size)
            
            # Rama derecha
            right_angle = angle - params.get("angle_right", 25) - angle_modifier
            draw_tree_recursive(surface, x2, y2, right_angle, depth - 1, new_length, 
                              params, color_mode, min_branch_size)
        
        else:
            # Árbol con múltiples ramas mejorado
            angle_spread = 50 + (branch_count - 2) * 10  # Ángulo adaptativo
            new_length = length * length_factor
            
            for i in range(branch_count):
                if branch_count == 1:
                    branch_angle = angle
                else:
                    # Distribución más natural de las ramas
                    position_factor = i / (branch_count - 1) - 0.5
                    branch_angle = angle + angle_spread * position_factor
                    
                    # Variar longitud ligeramente para cada rama
                    length_variation = 0.9 + 0.2 * abs(position_factor)
                    branch_length = new_length * length_variation
                
                draw_tree_recursive(surface, x2, y2, branch_angle, depth - 1, 
                                  branch_length if branch_count > 1 else new_length, 
                                  params, color_mode, min_branch_size)

def get_branch_color(depth, length, color_mode, params):
    """
    Calcula el color de una rama basado en varios factores
    """
    if color_mode == "gradient":
        # Gradiente más natural del marrón al verde
        depth_factor = depth / 12.0
        length_factor = length / 100.0
        
        if depth_factor > 0.6 or length_factor > 0.5:
            # Tronco y ramas principales - marrón
            brown_intensity = min(1.0, depth_factor + length_factor * 0.3)
            return (
                int(139 * brown_intensity),
                int(69 * brown_intensity),
                int(19 * brown_intensity)
            )
        elif depth_factor > 0.3:
            # Ramas medias - marrón claro
            return (101, 67, 33)
        else:
            # Ramas finas - verde con variación
            green_intensity = 0.7 + 0.3 * (1.0 - depth_factor)
            return (
                int(34 * green_intensity),
                int(139 * green_intensity),
                int(34 * green_intensity)
            )
    
    elif color_mode == "seasonal_spring":
        if depth > 4:
            return (101, 67, 33)  # Marrón para ramas
        else:
            # Verde lima con variación
            spring_greens = [(124, 252, 0), (50, 205, 50), (0, 255, 127)]
            return spring_greens[depth % len(spring_greens)]
    
    elif color_mode == "seasonal_autumn":
        if depth > 4:
            return (139, 69, 19)  # Marrón
        else:
            autumn_colors = [
                (255, 140, 0),   # Naranja
                (255, 69, 0),    # Rojo-naranja
                (255, 215, 0),   # Dorado
                (220, 20, 60),   # Carmesí
                (255, 165, 0),   # Naranja claro
                (178, 34, 34)    # Rojo ladrillo
            ]
            return autumn_colors[(depth + int(length)) % len(autumn_colors)]
    
    elif color_mode == "seasonal_winter":
        # Tonos grises y marrones para árbol invernal
        if depth > 3:
            return (101, 67, 33)  # Marrón
        else:
            gray_intensity = 100 + depth * 20
            return (gray_intensity, gray_intensity, gray_intensity)
    
    elif color_mode == "neon":
        neon_colors = [
            (0, 255, 255),    # Cyan
            (255, 0, 255),    # Magenta
            (255, 255, 0),    # Amarillo
            (0, 255, 0),      # Verde neón
            (255, 0, 127),    # Rosa neón
            (127, 255, 0)     # Verde lima neón
        ]
        return neon_colors[depth % len(neon_colors)]
    
    elif color_mode == "fire":
        # Colores de fuego para efecto dramático
        fire_colors = [
            (255, 0, 0),      # Rojo
            (255, 69, 0),     # Rojo-naranja
            (255, 140, 0),    # Naranja
            (255, 215, 0),    # Dorado
            (255, 255, 0)     # Amarillo
        ]
        return fire_colors[min(depth, len(fire_colors) - 1)]
    
    else:  # default
        return ColorScheme.GREEN

def draw_tree_stochastic(surface, x, y, angle, depth, length, randomness=0.2, seed=None):
    """
    Árbol con elementos aleatorios controlados para mayor naturalidad
    
    Args:
        surface: Superficie donde dibujar
        x, y: Posición inicial
        angle: Ángulo base
        depth: Profundidad
        length: Longitud base
        randomness: Factor de aleatoriedad (0-1)
        seed: Semilla para reproducibilidad
    """
    if seed is not None:
        random.seed(seed + depth * 100)  # Semilla única por nivel
    
    if depth <= 0 or length < 2:
        return
    
    # Variación aleatoria controlada
    angle_variation = random.uniform(-randomness * 20, randomness * 20)
    length_variation = random.uniform(1 - randomness * 0.4, 1 + randomness * 0.3)
    
    actual_angle = angle + angle_variation
    actual_length = length * length_variation
    
    # Calcular punto final
    angle_rad = math.radians(actual_angle)
    x2 = x + math.cos(angle_rad) * actual_length
    y2 = y - math.sin(angle_rad) * actual_length
    
    # Color con variación natural
    if depth > 4:
        brown_variants = [
            (139, 69, 19), (101, 67, 33), (160, 82, 45),
            (120, 60, 30), (150, 75, 40)
        ]
        color = random.choice(brown_variants)
    else:
        green_variants = [
            (34, 139, 34), (0, 128, 0), (50, 205, 50),
            (0, 100, 0), (60, 179, 113), (46, 139, 87)
        ]
        color = random.choice(green_variants)
    
    # Grosor variable con límites
    base_thickness = max(1, int(depth * 0.9))
    thickness = base_thickness + random.randint(-1, 1)
    thickness = max(1, min(thickness, 8))  # Limitar grosor máximo
    
    # Dibujar rama
    try:
        start_pos = (int(round(x)), int(round(y)))
        end_pos = (int(round(x2)), int(round(y2)))
        pygame.draw.line(surface, color, start_pos, end_pos, thickness)
    except (ValueError, OverflowError, pygame.error):
        return
    
    # Recursión con probabilidades variables
    if depth > 0:
        new_length = actual_length * random.uniform(0.6, 0.8)
        
        # Probabilidad de ramificación más realista
        branch_probability = min(0.9, 0.5 + depth * 0.1)
        
        branches_created = 0
        max_branches = 3 if depth > 6 else 2
        
        # Rama izquierda
        if random.random() < branch_probability:
            left_angle = actual_angle + random.uniform(15, 40)
            draw_tree_stochastic(surface, x2, y2, left_angle, depth - 1, 
                               new_length, randomness, seed)
            branches_created += 1
        
        # Rama derecha
        if random.random() < branch_probability:
            right_angle = actual_angle - random.uniform(15, 40)
            draw_tree_stochastic(surface, x2, y2, right_angle, depth - 1, 
                               new_length, randomness, seed)
            branches_created += 1
        
        # Rama central ocasional para árboles complejos
        if (depth > 2 and branches_created < max_branches and 
            random.random() < 0.3):
            center_angle = actual_angle + random.uniform(-10, 10)
            draw_tree_stochastic(surface, x2, y2, center_angle, depth - 1, 
                               new_length * 0.9, randomness, seed)

def draw_tree_wind(surface, x, y, angle, depth, length, wind_strength=0.0, wind_direction=0, time_factor=0):
    """
    Árbol con efecto de viento dinámico mejorado
    
    Args:
        surface: Superficie donde dibujar
        x, y: Posición inicial
        angle: Ángulo base
        depth: Profundidad
        length: Longitud
        wind_strength: Intensidad del viento (0-1)
        wind_direction: Dirección del viento en grados
        time_factor: Factor de tiempo para animación
    """
    if depth <= 0 or length < 2:
        return
    
    # Efecto de viento más realista
    # Las ramas más altas y finas se mueven más
    wind_sensitivity = max(0.1, 1.0 - depth / 12.0)
    wind_oscillation = math.sin(time_factor * 0.01 + depth * 0.5) * 0.5 + 0.5
    
    wind_effect = wind_strength * wind_sensitivity * 25 * wind_oscillation
    wind_angle = angle + wind_effect * math.cos(math.radians(wind_direction - angle))
    
    # Calcular punto final
    angle_rad = math.radians(wind_angle)
    x2 = x + math.cos(angle_rad) * length
    y2 = y - math.sin(angle_rad) * length
    
    # Color y grosor adaptativos
    thickness = max(1, int(depth * 0.8))
    
    if depth > 4:
        color = (139, 69, 19)  # Marrón para tronco
    else:
        # Hojas que cambian de color con el viento
        wind_factor = wind_strength * wind_sensitivity
        base_green = 139
        wind_lightness = int(wind_factor * 40)
        color = (
            min(255, 34 + wind_lightness), 
            min(255, base_green + wind_lightness), 
            34
        )
    
    # Dibujar rama
    try:
        start_pos = (int(round(x)), int(round(y)))
        end_pos = (int(round(x2)), int(round(y2)))
        pygame.draw.line(surface, color, start_pos, end_pos, thickness)
    except (ValueError, OverflowError, pygame.error):
        return
    
    # Recursión con ángulos modificados por viento
    if depth > 0:
        new_length = length * 0.72
        
        # El viento afecta la separación de las ramas
        base_angle_left = 25 + wind_strength * 15
        base_angle_right = 25 + wind_strength * 15
        
        draw_tree_wind(surface, x2, y2, wind_angle + base_angle_left, 
                      depth - 1, new_length, wind_strength, wind_direction, time_factor)
        draw_tree_wind(surface, x2, y2, wind_angle - base_angle_right, 
                      depth - 1, new_length, wind_strength, wind_direction, time_factor)

def draw_tree_seasons(surface, x, y, angle, depth, length, season="spring"):
    """
    Árbol con apariencia estacional mejorada
    """
    seasonal_params = {
        "spring": (TreeParameters.CLASSIC, "seasonal_spring"),
        "summer": (TreeParameters.BUSHY, "gradient"),
        "autumn": (TreeParameters.CLASSIC, "seasonal_autumn"),
        "winter": (TreeParameters.CLASSIC, "seasonal_winter")
    }
    
    params, color_mode = seasonal_params.get(season, seasonal_params["spring"])
    
    if season == "winter":
        # Modificar parámetros para árbol invernal (sin hojas)
        winter_params = params.copy()
        winter_params["thickness_factor"] = 0.6
        winter_params["length_factor"] = 0.8
        params = winter_params
    
    draw_tree_recursive(surface, x, y, angle, depth, length, params, color_mode)

def draw(surface, iterations):
    """
    Función principal mejorada para dibujar el árbol fractal
    
    Args:
        surface: Superficie de pygame donde dibujar
        iterations: Número de iteraciones/profundidad
    """
    # Limpiar superficie
    surface.fill((0, 0, 0, 0))
    
    width, height = surface.get_size()
    
    # Configuración adaptativa del árbol
    start_x = width * 0.5
    start_y = height * 0.9
    initial_angle = 90  # Hacia arriba
    
    # Longitud inicial adaptativa
    base_length = min(width, height) * 0.15
    initial_length = max(20, base_length)
    
    # Tamaño mínimo de rama basado en resolución
    min_branch_size = max(1.0, min(width, height) / 400.0)
    
    # Seleccionar estilo y parámetros según número de iteraciones
    if iterations <= 2:
        # Árbol muy simple
        draw_tree_recursive(surface, start_x, start_y, initial_angle, 
                          iterations, initial_length, TreeParameters.CLASSIC, 
                          "default", min_branch_size)
    
    elif iterations <= 5:
        # Árbol con gradiente básico
        draw_tree_recursive(surface, start_x, start_y, initial_angle, 
                          iterations, initial_length, TreeParameters.CLASSIC, 
                          "gradient", min_branch_size)
    
    elif iterations <= 8:
        # Árbol frondoso con colores estacionales
        draw_tree_recursive(surface, start_x, start_y, initial_angle, 
                          iterations, initial_length, TreeParameters.BUSHY, 
                          "seasonal_spring", min_branch_size)
    
    elif iterations <= 12:
        # Árbol robusto con más ramas
        draw_tree_recursive(surface, start_x, start_y, initial_angle, 
                          iterations, initial_length, TreeParameters.OAK, 
                          "seasonal_autumn", min_branch_size)
    
    else:
        # Árbol estocástico para iteraciones muy altas
        draw_tree_stochastic(surface, start_x, start_y, initial_angle, 
                           min(iterations, 15), initial_length, 0.25, seed=42)
    
    # Información de rendimiento para iteraciones altas
    if iterations > 10:
        try:
            font = pygame.font.Font(None, 20)
            branch_count = 2 ** iterations if iterations <= 15 else "Muy alto"
            info_text = "Ramas: " + str(branch_count)
            text_surface = font.render(info_text, True, ColorScheme.WARNING)
            surface.blit(text_surface, (10, 10))
        except:
            pass

def draw_animated(surface, iterations, animation_time=0):
    """
    Árbol animado mejorado con múltiples efectos
    """
    surface.fill((0, 0, 0, 0))
    
    width, height = surface.get_size()
    start_x = width * 0.5
    start_y = height * 0.9
    initial_angle = 90
    initial_length = min(width, height) * 0.15
    
    # Múltiples efectos de animación combinados
    # 1. Viento principal
    wind_strength = 0.2 + 0.3 * math.sin(animation_time * 0.001)
    wind_direction = 45 + 20 * math.sin(animation_time * 0.0008)
    
    # 2. Crecimiento pulsante sutil
    growth_factor = 1.0 + 0.05 * math.sin(animation_time * 0.002)
    animated_length = initial_length * growth_factor
    
    # 3. Ligera inclinación del tronco
    trunk_sway = 2 * math.sin(animation_time * 0.0005)
    animated_angle = initial_angle + trunk_sway
    
    draw_tree_wind(surface, start_x, start_y, animated_angle, 
                  iterations, animated_length, wind_strength, wind_direction, animation_time)

def get_fractal_info():
    """Retorna información detallada sobre el árbol fractal"""
    return {
        "name": "Árbol Fractal",
        "description": "Estructura ramificada que simula el crecimiento de árboles naturales usando recursión",
        "complexity": "O(branches^depth) - típicamente O(2^n) para árboles binarios",
        "recommended_max_depth": 12,
        "mathematical_properties": [
            "Auto-similar en diferentes escalas",
            "Estructura fractal ramificada con patrón recursivo",
            "Dimensión fractal variable según parámetros de ramificación",
            "Crecimiento exponencial del número de ramas"
        ],
        "variations": [
            "Árbol clásico binario",
            "Árbol con múltiples ramas (3+ ramas por nodo)",
            "Árbol estocástico con elementos aleatorios",
            "Árbol con efectos ambientales (viento, estaciones)",
            "Variantes específicas (roble, sauce, pino)"
        ],
        "tree_types": [name for name in dir(TreeParameters) if not name.startswith('_')],
        "color_modes": [
            "gradient", "seasonal_spring", "seasonal_autumn", 
            "seasonal_winter", "neon", "fire", "default"
        ],
        "construction_rule": "Cada rama se divide en 2+ sub-ramas con ángulos y longitudes específicas"
    }

def calculate_branch_count(depth, branches_per_node=2):
    """Calcula el número total de ramas"""
    if depth <= 0:
        return 0
    return (branches_per_node ** depth - 1) // (branches_per_node - 1) if branches_per_node > 1 else depth

def calculate_total_length(initial_length, depth, length_factor=0.7):
    """Calcula la longitud total de todas las ramas"""
    if depth <= 0:
        return 0
    
    total = 0
    current_length = initial_length
    branches_at_level = 1
    
    for level in range(depth):
        total += current_length * branches_at_level
        current_length *= length_factor
        branches_at_level *= 2  # Asumiendo árbol binario
    
    return total

def get_performance_metrics(depth):
    """Retorna métricas de rendimiento para una profundidad dada"""
    branch_count = calculate_branch_count(depth)
    
    return {
        "depth": depth,
        "total_branches": branch_count,
        "complexity_class": "Exponencial O(2^n)",
        "memory_estimate_kb": (branch_count * 32) / 1024,  # Estimación
        "recommended": depth <= 12,
        "performance_tier": (
            "Excelente" if depth <= 6 else
            "Bueno" if depth <= 9 else
            "Aceptable" if depth <= 12 else
            "Lento"
        )
    }