import pygame

BUTTON_WIDTH = 140
BUTTON_HEIGHT = 35
BUTTON_MARGIN = 10

BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)

fractals = ["Koch", "Sierpinski", "Mandelbrot", "Julia", "Árbol"]

# Crea un diccionario con la posición de cada botón
def get_button_rects():
    rects = {}
    for i, name in enumerate(fractals):
        rect = pygame.Rect(10, 10 + i * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
        rects[name] = rect
    return rects

# Dibuja los botones y la información actual
def draw_ui(screen, selected, iterations, scale, angle):
    font = pygame.font.SysFont("Arial", 16)
    rects = get_button_rects()

    for name, rect in rects.items():
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        color = BUTTON_HOVER if is_hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect)
        text = font.render(name, True, TEXT_COLOR)
        screen.blit(text, (rect.x + 10, rect.y + 8))

        if name == selected:
            pygame.draw.rect(screen, (0, 200, 0), rect, 2)  # Borde verde

    # Info extra
    info_y = 10 + len(fractals) * (BUTTON_HEIGHT + BUTTON_MARGIN) + 20
    info_texts = [
        f"Fractal: {selected}",
        f"Iteraciones: {iterations}",
        f"Zoom: {scale:.2f}",
        f"Ángulo: {angle}°",
        "↑ ↓: Iteraciones",
        "+/-: Zoom | R/E: Rotar",
        "Click y arrastra para mover",
        "S: Guardar imagen"
    ]
    for i, txt in enumerate(info_texts):
        info = font.render(txt, True, (220, 220, 220))
        screen.blit(info, (10, info_y + i * 20))

# Detecta si se hizo clic en un botón de fractal
def get_selected_fractal(mouse_pos):
    rects = get_button_rects()
    for name, rect in rects.items():
        if rect.collidepoint(mouse_pos):
            return name
    return None
