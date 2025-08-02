import pygame
import math
from utils import ColorScheme

class Button:
    """Clase para botones interactivos"""
    
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.Font(None, 20)
        
    def handle_event(self, event, mouse_pos):
        """Maneja eventos del botón"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.is_hovered:
                self.is_pressed = False
                return self.action if self.action else self.text
            self.is_pressed = False
            
        return None
    
    def draw(self, surface):
        """Dibuja el botón"""
        # Color base
        if self.is_pressed:
            color = ColorScheme.BUTTON_PRESSED
        elif self.is_hovered:
            color = ColorScheme.BUTTON_HOVER
        else:
            color = ColorScheme.BUTTON_NORMAL
            
        # Dibujar fondo del botón con bordes redondeados
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, ColorScheme.BUTTON_BORDER, self.rect, 2, border_radius=8)
        
        # Dibujar texto centrado
        text_surface = self.font.render(self.text, True, ColorScheme.TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class Slider:
    """Clase para controles deslizantes"""
    
    def __init__(self, x, y, width, min_val, max_val, initial_val, label=""):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 18)
        
        # Área del handle
        self.handle_radius = 8
        
    def handle_event(self, event, mouse_pos):
        """Maneja eventos del slider"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.update_value(mouse_pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(mouse_pos[0])
    
    def update_value(self, mouse_x):
        """Actualiza el valor basado en la posición del mouse"""
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(relative_x, self.rect.width))
        
        # Calcular nuevo valor
        ratio = relative_x / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        
        # Redondear para valores enteros si es apropiado
        if isinstance(self.min_val, int) and isinstance(self.max_val, int):
            self.val = round(self.val)
    
    def draw(self, surface):
        """Dibuja el slider"""
        # Dibujar pista
        track_rect = pygame.Rect(self.rect.x, self.rect.y + 8, self.rect.width, 4)
        pygame.draw.rect(surface, ColorScheme.SLIDER_TRACK, track_rect, border_radius=2)
        
        # Calcular posición del handle
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + ratio * self.rect.width
        handle_y = self.rect.y + 10
        
        # Dibujar handle
        pygame.draw.circle(surface, ColorScheme.SLIDER_HANDLE, (int(handle_x), handle_y), self.handle_radius)
        pygame.draw.circle(surface, ColorScheme.BUTTON_BORDER, (int(handle_x), handle_y), self.handle_radius, 2)
        
        # Dibujar etiqueta y valor
        if self.label:
            label_text = f"{self.label}: {self.val:.2f}" if isinstance(self.val, float) else f"{self.label}: {self.val}"
            text_surface = self.font.render(label_text, True, ColorScheme.TEXT)
            surface.blit(text_surface, (self.rect.x, self.rect.y - 20))

class UIManager:
    """Maneja toda la interfaz de usuario"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Panel lateral
        self.panel_width = 200
        self.panel_rect = pygame.Rect(0, 0, self.panel_width, screen_height)
        
        # Fractales disponibles
        self.fractals = ["Koch", "Sierpinski", "Mandelbrot", "Julia", "Árbol"]
        
        # Crear botones de fractales
        self.fractal_buttons = []
        for i, fractal in enumerate(self.fractals):
            button = Button(
                10, 50 + i * 45, 180, 35,
                fractal, fractal
            )
            self.fractal_buttons.append(button)
        
        # Botones de acción
        self.action_buttons = [
            Button(10, 300, 85, 30, "Reset", "reset"),
            Button(105, 300, 85, 30, "Guardar", "save"),
        ]
        
        # Información del sistema
        self.info_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 24)
        
        # Controles avanzados (para versiones futuras)
        self.show_advanced = False
        
    def handle_click(self, mouse_pos):
        if not self.panel_rect.collidepoint(mouse_pos):
            return None

        # Revisar botones fractales
        for button in self.fractal_buttons:
            if button.rect.collidepoint(mouse_pos):
                return button.action if button.action else button.text
        
        # Revisar botones de acción
        for button in self.action_buttons:
            if button.rect.collidepoint(mouse_pos):
                return button.action if button.action else button.text

        return None

    
    def update_hover_states(self, mouse_pos):
        """Actualiza los estados de hover de los elementos UI"""
        for button in self.fractal_buttons + self.action_buttons:
            button.is_hovered = button.rect.collidepoint(mouse_pos)
    
    def draw(self, surface, selected_fractal, iterations, max_iterations, scale, angle, render_time):
        """Dibuja toda la interfaz de usuario"""
        # Dibujar panel lateral
        self.draw_panel(surface)
        
        # Dibujar botones de fractales
        self.draw_fractal_buttons(surface, selected_fractal)
        
        # Dibujar botones de acción
        self.draw_action_buttons(surface)
        
        # Dibujar información
        self.draw_info_panel(surface, selected_fractal, iterations, max_iterations, scale, angle, render_time)
        
        # Dibujar controles
        self.draw_controls_info(surface)
        
        # Actualizar estados de hover
        self.update_hover_states(pygame.mouse.get_pos())
    
    def draw_panel(self, surface):
        """Dibuja el panel lateral principal"""
        # Fondo del panel con gradiente simulado
        panel_color = ColorScheme.PANEL_BG
        pygame.draw.rect(surface, panel_color, self.panel_rect)
        
        # Línea separadora
        pygame.draw.line(surface, ColorScheme.PANEL_BORDER, 
                        (self.panel_width, 0), (self.panel_width, self.screen_height), 2)
        
        # Título
        title = self.title_font.render("Fractales", True, ColorScheme.TITLE)
        surface.blit(title, (10, 10))
        
        # Línea bajo el título
        pygame.draw.line(surface, ColorScheme.PANEL_BORDER, (10, 35), (190, 35), 1)
    
    def draw_fractal_buttons(self, surface, selected_fractal):
        """Dibuja los botones de selección de fractales"""
        for button in self.fractal_buttons:
            # Marcar el fractal seleccionado
            if button.text == selected_fractal:
                # Fondo especial para el seleccionado
                highlight_rect = pygame.Rect(button.rect.x - 2, button.rect.y - 2, 
                                           button.rect.width + 4, button.rect.height + 4)
                pygame.draw.rect(surface, ColorScheme.SELECTED_HIGHLIGHT, highlight_rect, border_radius=10)
            
            button.draw(surface)
    
    def draw_action_buttons(self, surface):
        """Dibuja los botones de acción"""
        for button in self.action_buttons:
            button.draw(surface)
    
    def draw_info_panel(self, surface, selected_fractal, iterations, max_iterations, scale, angle, render_time):
        """Dibuja el panel de información"""
        y_offset = 350
        
        # Información del fractal actual
        info_items = [
            f"Fractal: {selected_fractal}",
            f"Iteraciones: {iterations}/{max_iterations}",
            f"Escala: {scale:.2f}x",
            f"Rotación: {angle:.1f}°",
            f"Render: {render_time*1000:.1f}ms" if render_time > 0 else "Render: 0ms",
        ]
        
        for i, text in enumerate(info_items):
            color = ColorScheme.INFO_TEXT
            text_surface = self.info_font.render(text, True, color)
            surface.blit(text_surface, (10, y_offset + i * 22))
    
    def draw_controls_info(self, surface):
        """Dibuja la información de controles"""
        y_offset = 480
        
        # Título de controles
        controls_title = self.info_font.render("Controles:", True, ColorScheme.TITLE)
        surface.blit(controls_title, (10, y_offset))
        
        # Lista de controles
        controls = [
            "↑/↓: Iteraciones",
            "+/-: Zoom",
            "R/E: Rotar",
            "Rueda: Zoom rápido",
            "Arrastrar: Mover",
            "S: Captura",
            "0: Reset",
            "ESC: Salir",
            "F11: Pantalla completa"
        ]
        
        for i, control in enumerate(controls):
            color = ColorScheme.CONTROL_TEXT
            text_surface = self.info_font.render(control, True, color)
            surface.blit(text_surface, (10, y_offset + 25 + i * 18))
    
    def draw_performance_info(self, surface, fps):
        """Dibuja información de rendimiento"""
        y_offset = self.screen_height - 60
        
        perf_title = self.info_font.render("Rendimiento:", True, ColorScheme.TITLE)
        surface.blit(perf_title, (10, y_offset))
        
        fps_text = self.info_font.render(f"FPS: {fps:.1f}", True, ColorScheme.INFO_TEXT)
        surface.blit(fps_text, (10, y_offset + 20))
    
    def draw_progress_bar(self, surface, progress, label="Cargando..."):
        """Dibuja una barra de progreso para operaciones largas"""
        bar_rect = pygame.Rect(10, self.screen_height // 2 - 20, 180, 20)
        
        # Fondo de la barra
        pygame.draw.rect(surface, ColorScheme.SLIDER_TRACK, bar_rect, border_radius=10)
        
        # Progreso
        progress_width = int(bar_rect.width * progress)
        progress_rect = pygame.Rect(bar_rect.x, bar_rect.y, progress_width, bar_rect.height)
        pygame.draw.rect(surface, ColorScheme.SELECTED_HIGHLIGHT, progress_rect, border_radius=10)
        
        # Texto
        text = self.info_font.render(label, True, ColorScheme.TEXT)
        text_rect = text.get_rect(center=(bar_rect.centerx, bar_rect.y - 15))
        surface.blit(text, text_rect)
        
        # Porcentaje
        percent_text = self.info_font.render(f"{progress*100:.0f}%", True, ColorScheme.TEXT)
        percent_rect = percent_text.get_rect(center=bar_rect.center)
        surface.blit(percent_text, percent_rect)