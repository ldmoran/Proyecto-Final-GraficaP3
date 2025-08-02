import pygame
import sys
import time
from fractals import koch, sierpinski, mandelbrot, julia, arbol
from ui.interface import UIManager
from transforms import TransformManager
from utils import ScreenshotManager, ColorScheme

class FractalVisualizer:
    def __init__(self):
        # Configuración de ventana
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.FPS = 60
        
        # Inicialización de pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Visualizador Interactivo de Fractales - Versión Mejorada")
        self.clock = pygame.time.Clock()
        
        # Estados del fractal
        self.selected_fractal = "Koch"
        self.iterations = 3
        self.max_iterations = {"Koch": 7, "Sierpinski": 8, "Mandelbrot": 100, "Julia": 100, "Árbol": 12}
        
        # Managers
        self.ui_manager = UIManager(self.WIDTH, self.HEIGHT)
        self.transform_manager = TransformManager()
        self.screenshot_manager = ScreenshotManager()
        
        # Control de interacción
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.last_render_time = 0
        self.render_cache = {}
        
        # Fractales disponibles
        self.FRACTAL_FUNCTIONS = {
            "Koch": koch.draw,
            "Sierpinski": sierpinski.draw,
            "Mandelbrot": mandelbrot.draw,
            "Julia": julia.draw,
            "Árbol": arbol.draw,
        }
        
        # Área de renderizado del fractal (excluyendo UI)
        self.fractal_area = pygame.Rect(200, 0, self.WIDTH - 200, self.HEIGHT)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                # Si handle_keyboard devuelve False, salir del programa
                if self.handle_keyboard(event) is False:
                    return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)
                
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)
                
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_mouse_wheel(event)
        
        return True

    
    def handle_keyboard(self, event):
        if event.key == pygame.K_UP:
            if self.iterations < self.max_iterations[self.selected_fractal]:
                self.iterations += 1
                self.clear_cache()
        elif event.key == pygame.K_DOWN and self.iterations > 0:
            self.iterations -= 1
            self.clear_cache()
        elif event.key == pygame.K_r:
            self.transform_manager.rotate(5)
        elif event.key == pygame.K_e:
            self.transform_manager.rotate(-5)
        elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
            self.transform_manager.scale_factor(1.1)
        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
            self.transform_manager.scale_factor(0.9)
        elif event.key == pygame.K_s:
            self.screenshot_manager.save_screenshot(self.screen)
        elif event.key == pygame.K_0:
            self.transform_manager.reset()
            self.clear_cache()
        elif event.key == pygame.K_ESCAPE:
            return False
        elif event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()

        return True

    
    def handle_mouse_down(self, event):
        """Maneja clics del mouse"""
        mouse_pos = pygame.mouse.get_pos()
        
        if event.button == 1:  # Click izquierdo
            # Verificar si se hizo clic en la UI
            new_selection = self.ui_manager.handle_click(mouse_pos)
            if new_selection:
                if new_selection in self.FRACTAL_FUNCTIONS:
                    self.selected_fractal = new_selection
                    self.iterations = min(self.iterations, self.max_iterations[self.selected_fractal])
                    self.clear_cache()
                elif new_selection == "reset":
                    self.transform_manager.reset()
                elif new_selection == "save":
                    self.screenshot_manager.save_screenshot(self.screen)
            # Si no hay clic en UI y está en área de fractal, iniciar arrastre
            elif self.fractal_area.collidepoint(mouse_pos):
                self.dragging = True
                self.last_mouse_pos = mouse_pos
                
        elif event.button == 3:  # Click derecho
            self.screenshot_manager.save_screenshot(self.screen)
    
    def handle_mouse_up(self, event):
        """Maneja cuando se suelta el mouse"""
        if event.button == 1:
            self.dragging = False
    
    def handle_mouse_motion(self, event):
        """Maneja movimiento del mouse"""
        if self.dragging and self.fractal_area.collidepoint(event.pos):
            mx, my = event.pos
            dx = mx - self.last_mouse_pos[0]
            dy = my - self.last_mouse_pos[1]
            self.transform_manager.translate(dx, dy)
            self.last_mouse_pos = (mx, my)
    
    def handle_mouse_wheel(self, event):
        """Maneja la rueda del mouse para zoom"""
        if self.fractal_area.collidepoint(pygame.mouse.get_pos()):
            if event.y > 0:
                self.transform_manager.scale(1.1)
            else:
                self.transform_manager.scale(0.9)
    
    def clear_cache(self):
        """Limpia la caché de renderizado"""
        self.render_cache.clear()
    
    def get_cache_key(self):
        """Genera una clave para la caché basada en el estado actual"""
        return (
            self.selected_fractal,
            self.iterations,
            round(self.transform_manager.current_scale, 2),

            round(self.transform_manager.angle),
            tuple(self.transform_manager.offset)
        )
    
    def render_fractal(self):
        """Renderiza el fractal actual con optimizaciones"""
        cache_key = self.get_cache_key()
        
        # Verificar caché para fractales que no cambian (Koch, Sierpinski, Árbol)
        if (self.selected_fractal not in ["Mandelbrot", "Julia"] and 
            cache_key in self.render_cache):
            return self.render_cache[cache_key]
        
        # Crear superficie para el fractal
        fractal_surface = pygame.Surface((self.fractal_area.width, self.fractal_area.height), pygame.SRCALPHA)
        fractal_surface.fill((0, 0, 0, 0))
        
        try:
            # Renderizar el fractal
            start_time = time.time()
            fractal_func = self.FRACTAL_FUNCTIONS[self.selected_fractal]
            
            if self.selected_fractal == "Árbol":
                # El árbol se renderiza directamente sin transformaciones para mejor calidad
                fractal_func(fractal_surface, self.iterations)
                transformed = fractal_surface
            else:
                fractal_func(fractal_surface, self.iterations)
                transformed = self.transform_manager.apply_transformations(fractal_surface)
            
            render_time = time.time() - start_time
            self.last_render_time = render_time
            
            # Guardar en caché si es un fractal estático
            if self.selected_fractal not in ["Mandelbrot", "Julia"]:
                self.render_cache[cache_key] = transformed
            
            return transformed
            
        except Exception as e:
            print(f"Error renderizando fractal {self.selected_fractal}: {e}")
            # Retornar una superficie de error
            error_surface = pygame.Surface((self.fractal_area.width, self.fractal_area.height))
            error_surface.fill(ColorScheme.ERROR)
            font = pygame.font.Font(None, 36)
            text = font.render("Error de renderizado", True, ColorScheme.WHITE)
            error_surface.blit(text, (10, 10))
            return error_surface
    
    def run(self):
        """Loop principal de la aplicación"""
        running = True
        
        while running:
            # Manejar eventos
            running = self.handle_events()
            if not running:
                break
            
            # Limpiar pantalla
            self.screen.fill(ColorScheme.BACKGROUND)
            
            # Renderizar fractal
            fractal_surface = self.render_fractal()
            self.screen.blit(fractal_surface, self.fractal_area.topleft)
            
            # Renderizar UI
            self.ui_manager.draw(
                self.screen,
                self.selected_fractal,
                self.iterations,
                self.max_iterations[self.selected_fractal],
                self.transform_manager.current_scale,  # <-- Aquí el cambio
                self.transform_manager.angle,
                self.last_render_time
            )

            
            # Mostrar FPS en la esquina
            fps = self.clock.get_fps()
            fps_text = pygame.font.Font(None, 24).render(f"FPS: {fps:.1f}", True, ColorScheme.TEXT)
            self.screen.blit(fps_text, (self.WIDTH - 100, 10))
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    try:
        visualizer = FractalVisualizer()
        visualizer.run()
    except Exception as e:
        print(f"Error fatal: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()