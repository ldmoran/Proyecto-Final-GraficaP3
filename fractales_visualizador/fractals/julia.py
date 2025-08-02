def draw(surface, iterations):
    width, height = surface.get_size()
    max_iter = max(10, iterations)  # mínimo 10 iteraciones para ver detalles
    cX, cY = -0.7, 0.27015  # constante Julia

    surface.lock()
    for x in range(width):
        for y in range(height):
            zx = 1.5 * (x - width / 2) / (0.5 * width)
            zy = (y - height / 2) / (0.5 * height)
            iteration = 0

            while zx*zx + zy*zy < 4 and iteration < max_iter:
                tmp = zx*zx - zy*zy + cX
                zy, zx = 2.0*zx*zy + cY, tmp
                iteration += 1

            color_value = 255 - int(iteration * 255 / max_iter)
            color = (color_value, color_value // 2, 255 - color_value)
            surface.set_at((x, y), color)
    surface.unlock()
