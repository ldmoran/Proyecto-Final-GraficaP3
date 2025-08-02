import pygame
import datetime
import os
import json

class ColorScheme:
    """Esquema de colores moderno para la aplicación"""
    
    # Colores principales
    BACKGROUND = (25, 25, 35)
    PANEL_BG = (35, 35, 45)
    PANEL_BORDER = (60, 60, 70)
    
    # Colores de texto
    TEXT = (220, 220, 220)
    TITLE = (255, 255, 255)
    INFO_TEXT = (180, 180, 190)
    CONTROL_TEXT = (160, 160, 170)
    
    # Colores de botones
    BUTTON_NORMAL = (50, 50, 60)
    BUTTON_HOVER = (70, 70, 80)
    BUTTON_PRESSED = (40, 40, 50)
    BUTTON_BORDER = (100, 100, 110)
    
    # Colores especiales
    SELECTED_HIGHLIGHT = (0, 150, 255)
    ERROR = (200, 50, 50)
    SUCCESS = (50, 200, 50)
    WARNING = (255, 180, 0)
    
    # Controles deslizantes
    SLIDER_TRACK = (60, 60, 70)
    SLIDER_HANDLE = (0, 150, 255)
    
    # Colores de fractales
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)

class ScreenshotManager:
    """Maneja la captura y guardado de imágenes"""
    
    def __init__(self):
        self.screenshots_dir = "capturas"
        self.ensure_directory()
        
    def ensure_directory(self):
        """Crea el directorio de capturas si no existe"""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            print(f"📁 Directorio creado: {self.screenshots_dir}")
    
    def save_screenshot(self, surface):
        """Guarda una captura de pantalla con timestamp"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshots_dir}/fractal_{timestamp}.png"
            
            pygame.image.save(surface, filename)
            print(f"✅ Captura guardada: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error guardando captura: {e}")
            return None
    
    def save_fractal_only(self, fractal_surface, fractal_name, iterations):
        """Guarda solo el fractal sin la UI"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshots_dir}/{fractal_name}_{iterations}iter_{timestamp}.png"
            
            pygame.image.save(fractal_surface, filename)
            print(f"✅ Fractal guardado: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error guardando fractal: {e}")
            return None

class ConfigManager:
    """Maneja la configuración de la aplicación"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "window_width": 1200,
            "window_height": 800,
            "fps_limit": 60,
            "default_fractal": "Koch",
            "max_iterations": {
                "Koch": 7,
                "Sierpinski": 8,
                "Mandelbrot": 100,
                "Julia": 100,
                "Árbol": 12
            },
            "auto_save_interval": 0,  # 0 = desactivado
            "quality_mode": "high",  # low, medium, high
            "enable_antialiasing": True,
            "enable_caching": True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Carga la configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Combinar con configuración por defecto
                    config = self.default_config.copy()
                    config.update(loaded_config)
                    return config
            else:
                return self.default_config.copy()
                
        except Exception as e:
            print(f"⚠️ Error cargando configuración: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """Guarda la configuración actual"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print("✅ Configuración guardada")
            
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
    
    def get(self, key, default=None):
        """Obtiene un valor de configuración"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Establece un valor de configuración"""
        self.config[key] = value

class PerformanceMonitor:
    """Monitorea el rendimiento de la aplicación"""
    
    def __init__(self):
        self.frame_times = []
        self.max_samples = 60  # Mantener últimos 60 frames
        self.render_times = []
        
    def add_frame_time(self, frame_time):
        """Añade tiempo de frame"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
    
    def add_render_time(self, render_time):
        """Añade tiempo de renderizado"""
        self.render_times.append(render_time)
        if len(self.render_times) > self.max_samples:
            self.render_times.pop(0)
    
    def get_average_fps(self):
        """Calcula FPS promedio"""
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
    
    def get_average_render_time(self):
        """Calcula tiempo de renderizado promedio"""
        if not self.render_times:
            return 0
        return sum(self.render_times) / len(self.render_times)
    
    def is_performance_good(self):
        """Determina si el rendimiento es bueno"""
        avg_fps = self.get_average_fps()
        return avg_fps >= 30  # Considerar bueno si >= 30 FPS

class MathUtils:
    """Utilidades matemáticas para fractales"""
    
    @staticmethod
    def distance(p1, p2):
        """Calcula distancia entre dos puntos"""
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    
    @staticmethod
    def lerp(a, b, t):
        """Interpolación lineal"""
        return a + (b - a) * t
    
    @staticmethod
    def clamp(value, min_val, max_val):
        """Limita un valor entre min y max"""
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def map_range(value, from_min, from_max, to_min, to_max):
        """Mapea un valor de un rango a otro"""
        from_range = from_max - from_min
        to_range = to_max - to_min
        scaled = (value - from_min) / from_range
        return to_min + (scaled * to_range)
    
    @staticmethod
    def smooth_step(t):
        """Función de suavizado"""
        return t * t * (3 - 2 * t)

class Logger:
    """Sistema de logging simple"""
    
    def __init__(self, filename="fractal_visualizer.log"):
        self.filename = filename
        self.log_to_file = True
        
    def log(self, level, message):
        """Registra un mensaje"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"
        
        # Imprimir en consola
        print(log_message)
        
        # Guardar en archivo si está habilitado
        if self.log_to_file:
            try:
                with open(self.filename, 'a', encoding='utf-8') as f:
                    f.write(log_message + '\n')
            except Exception as e:
                print(f"Error escribiendo log: {e}")
    
    def info(self, message):
        """Log de información"""
        self.log("INFO", message)
    
    def warning(self, message):
        """Log de advertencia"""
        self.log("WARNING", message)
    
    def error(self, message):
        """Log de error"""
        self.log("ERROR", message)
    
    def debug(self, message):
        """Log de debug"""
        self.log("DEBUG", message)

class FractalCache:
    """Sistema de caché para fractales renderizados"""
    
    def __init__(self, max_size=50):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []  # Para LRU
    
    def get_key(self, fractal_name, iterations, width, height, transforms=None):
        """Genera clave única para el caché"""
        transform_key = ""
        if transforms:
            transform_key = f"_s{transforms.scale:.2f}_a{transforms.angle:.1f}_o{transforms.offset[0]},{transforms.offset[1]}"
        
        return f"{fractal_name}_{iterations}_{width}x{height}{transform_key}"
    
    def get(self, key):
        """Obtiene superficie del caché"""
        if key in self.cache:
            # Actualizar orden de acceso (LRU)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, surface):
        """Guarda superficie en caché"""
        # Limpiar caché si está lleno
        if len(self.cache) >= self.max_size:
            # Remover el menos recientemente usado
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        # Añadir nueva entrada
        self.cache[key] = surface.copy()  # Hacer copia para evitar modificaciones
        self.access_order.append(key)
    
    def clear(self):
        """Limpia todo el caché"""
        self.cache.clear()
        self.access_order.clear()
    
    def get_memory_usage(self):
        """Estima uso de memoria del caché (aproximado)"""
        total_pixels = 0
        for surface in self.cache.values():
            total_pixels += surface.get_width() * surface.get_height()
        
        # Estimar bytes (4 bytes por pixel RGBA)
        return total_pixels * 4

def format_file_size(bytes_size):
    """Formatea tamaño de archivo en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def validate_fractal_parameters(fractal_name, iterations):
    """Valida parámetros de fractal"""
    max_iterations = {
        "Koch": 7,
        "Sierpinski": 8,
        "Mandelbrot": 1000,
        "Julia": 1000,
        "Árbol": 15
    }
    
    if fractal_name not in max_iterations:
        return False, f"Fractal '{fractal_name}' no reconocido"
    
    if iterations < 0:
        return False, "Las iteraciones no pueden ser negativas"
    
    if iterations > max_iterations[fractal_name]:
        return False, f"Máximo {max_iterations[fractal_name]} iteraciones para {fractal_name}"
    
    return True, "Parámetros válidos"

# Instancia global del logger
logger = Logger()

# Instancia global del caché
fractal_cache = FractalCache()

# Instancia global del monitor de rendimiento
performance_monitor = PerformanceMonitor()