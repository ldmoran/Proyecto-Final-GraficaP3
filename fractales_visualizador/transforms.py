import pygame
import math

class TransformManager:
    """Maneja todas las transformaciones de los fractales"""
    
    def __init__(self):
        self.current_scale = 1.0
        self.angle = 0.0
        self.offset = [0, 0]
        
        # Límites para evitar valores extremos
        self.min_scale = 0.1
        self.max_scale = 50.0
        
    def reset(self):
        """Resetea todas las transformaciones"""
        self.current_scale = 1.0
        self.angle = 0.0
        self.offset = [0, 0]
    
    def scale_factor(self, factor):
        """Aplica un factor de escala"""
        new_scale = self.current_scale * factor
        if self.min_scale <= new_scale <= self.max_scale:
            self.current_scale = new_scale
    
    def scale(self, factor):
        """Alias para scale_factor"""
        self.scale_factor(factor)
    
    def rotate(self, degrees):
        """Rota por grados especificados"""
        self.angle = (self.angle + degrees) % 360
    
    def translate(self, dx, dy):
        """Traslada por dx, dy"""
        self.offset[0] += dx
        self.offset[1] += dy
    
    def apply_transformations(self, surface):
        """Aplica todas las transformaciones a una superficie"""
        if not surface:
            return surface
            
        try:
            original_width, original_height = surface.get_size()
            
            # 1. Escalar con interpolación suave
            if abs(self.current_scale - 1.0) > 0.01:  # Solo escalar si hay diferencia significativa
                new_width = max(1, int(original_width * self.current_scale))
                new_height = max(1, int(original_height * self.current_scale))
                
                # Usar smoothscale solo si la superficie es lo suficientemente grande
                if new_width > 10 and new_height > 10:
                    scaled_surface = pygame.transform.smoothscale(surface, (new_width, new_height))
                else:
                    scaled_surface = pygame.transform.scale(surface, (new_width, new_height))
            else:
                scaled_surface = surface
            
            # 2. Rotar con anti-aliasing
            if abs(self.angle) > 0.1:  # Solo rotar si hay ángulo significativo
                rotated_surface = pygame.transform.rotozoom(scaled_surface, self.angle, 1.0)
            else:
                rotated_surface = scaled_surface
            
            # 3. Crear superficie final con el tamaño original
            final_surface = pygame.Surface((original_width, original_height), pygame.SRCALPHA)
            final_surface.fill((0, 0, 0, 0))
            
            # 4. Calcular posición centrada con offset
            rot_rect = rotated_surface.get_rect()
            center_x = original_width // 2 + self.offset[0]
            center_y = original_height // 2 + self.offset[1]
            
            # Posicionar el fractal transformado
            blit_x = center_x - rot_rect.width // 2
            blit_y = center_y - rot_rect.height // 2
            
            final_surface.blit(rotated_surface, (blit_x, blit_y))
            
            return final_surface
            
        except Exception as e:
            print(f"Error en transformaciones: {e}")
            return surface

            
        except Exception as e:
            print(f"Error en transformaciones: {e}")
            return surface
    
    def get_transform_matrix(self):
        """Retorna la matriz de transformación actual (para uso futuro)"""
        # Convertir a radianes
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Matriz de transformación 2D
        matrix = [
            [self.scale * cos_a, -self.scale * sin_a, self.offset[0]],
            [self.scale * sin_a, self.scale * cos_a, self.offset[1]],
            [0, 0, 1]
        ]
        
        return matrix
    
    def transform_point(self, x, y):
        """Transforma un punto usando las transformaciones actuales"""
        # Aplicar escala
        x *= self.scale
        y *= self.scale
        
        # Aplicar rotación
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        
        # Aplicar traslación
        new_x += self.offset[0]
        new_y += self.offset[1]
        
        return int(new_x), int(new_y)
    
    def inverse_transform_point(self, x, y):
        """Transforma un punto desde coordenadas de pantalla a coordenadas originales"""
        # Aplicar traslación inversa
        x -= self.offset[0]
        y -= self.offset[1]
        
        # Aplicar rotación inversa
        rad = math.radians(-self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        rot_x = x * cos_a - y * sin_a
        rot_y = x * sin_a + y * cos_a
        
        # Aplicar escala inversa
        if abs(self.scale) > 0.001:  # Evitar división por cero
            rot_x /= self.scale
            rot_y /= self.scale
        
        return int(rot_x), int(rot_y)

class AdvancedTransforms:
    """Transformaciones avanzadas para uso futuro"""
    
    @staticmethod
    def apply_perspective(surface, perspective_strength=0.1):
        """Aplica una transformación de perspectiva simple"""
        # Implementación básica de perspectiva
        # Esta función podría expandirse para efectos 3D
        pass
    
    @staticmethod
    def apply_wave_distortion(surface, amplitude=10, frequency=0.1):
        """Aplica una distorsión ondulatoria"""
        # Implementación de distorsión de onda
        # Útil para efectos visuales especiales
        pass
    
    @staticmethod
    def apply_radial_blur(surface, center, strength=5):
        """Aplica un desenfoque radial desde un centro"""
        # Implementación de desenfoque radial
        # Útil para efectos de movimiento
        pass

def lerp(a, b, t):
    """Interpolación lineal entre dos valores"""
    return a + (b - a) * t

def smooth_step(t):
    """Función de suavizado para transiciones"""
    return t * t * (3 - 2 * t)

def ease_in_out(t):
    """Función de suavizado ease-in-out"""
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t