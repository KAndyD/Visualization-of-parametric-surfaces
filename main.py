import pygame  # Импорт библиотеки Pygame для создания графического интерфейса и работы с окнами
import numpy as np  # Импорт NumPy для работы с массивами и математическими функциями
import sys  # Импорт sys для доступа к системным функциям, таким как завершение программы
import datetime  # Импорт datetime для работы с датой и временем, используется при сохранении скриншотов


# ------------------- ПАРАМЕТРИЧЕСКИЕ ПОВЕРХНОСТИ -------------------

# Описание поверхности в форме морской раковины
def seashell_surface(u, v, alpha, beta):
    u, v = np.radians(u), np.radians(v)  # Преобразование градусов в радианы для тригонометрических функций
    factor = alpha * np.exp(beta * v)  # Вычисление масштабного коэффициента
    x = factor * np.cos(v) * (1 + np.cos(u))  # Вычисление координаты x
    y = factor * np.sin(v) * (1 + np.cos(u))  # Вычисление координаты y
    z = factor * np.sin(u)  # Вычисление координаты z
    return x, y, z  # Возврат координат точки на поверхности


# Лента Мёбиуса
def mobius_surface(u, v, alpha, beta):
    u, v = np.radians(u), v # Преобразование u в радианы
    half_v = v / 2 # Деление v пополам — управляющий параметр для ширины ленты

    # Вычисление координат точки на ленте Мёбиуса:
    x = (alpha + v * np.cos(u / 2)) * np.cos(u) # Модифицированный радиус с искривлением по cos(u/2)
    y = (alpha + v * np.cos(u / 2)) * np.sin(u) # То же самое, но по sin(u)
    z = beta * v * np.sin(u / 2) # z зависит от sin(u/2) — создаёт скручивание
    return x, y, z

# Тор бублик
def torus_surface(u, v, alpha, beta):
    u, v = np.radians(u), np.radians(v)        # Перевод параметров в радианы
    R = alpha                                  # Большой радиус (от центра до кольца)
    r = beta                                   # Малый радиус (само кольцо)
    x = (R + r * np.cos(v)) * np.cos(u)        # x зависит от угла u и положения точки на малом радиусе
    y = (R + r * np.cos(v)) * np.sin(u)        # y аналогично
    z = r * np.sin(v)                          # z отвечает за вертикальное положение точки на кольце
    return x, y, z


def spiral_surface(u, v, alpha, beta):
    u, v = np.radians(u), np.radians(v)
    x = (alpha * 5 + beta * np.cos(v)) * np.cos(u)
    y = (alpha * 5 + beta * np.cos(v)) * np.sin(u)
    z = beta * np.sin(v) + alpha * 2 * u
    return x, y, z


def helical_surface(u, v, alpha, beta):
    u = np.radians(u)  # угол вокруг оси
    steps = 5  # количество полных витков (можно сделать параметром)
    radius = alpha * 5  # радиус лестницы
    height = beta * 10  # высота лестницы

    angle = steps * u  # растяжение u на несколько оборотов
    z = height * v  # подъём по оси Z
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return x, y, z

# Cловарь функций, каждая из которых отвечает за генерацию своей уникальной 3D-поверхности по параметрам u, v
surfaces = {
    "Seashell": seashell_surface,
    "Mobius": mobius_surface,
    "Torus": torus_surface,
    "Spiral": spiral_surface,
    "Helical": helical_surface
}

# Pадаёт допустимые диапазоны значений параметров u и v для каждой поверхности
surface_bounds = {
    "Seashell": ((0, 360), (0, 1080)),
    "Mobius": ((0, 360), (-1, 1)),
    "Torus": ((0, 360), (0, 360)),
    "Spiral": ((0, 720), (0, 720)),
    "Helical": ((0, 360), (-5, 5))
}

current_surface_name = None

# ------------------- НАСТРОЙКИ -------------------
u_limits, v_limits = (0, 360), (0, 360)  # Диапазоны параметров u и v по умолчанию
param_a, param_b = 0.1, 0.05             # Начальные значения параметров alpha и beta (управляют формой поверхности)
a_step = 0.05                            # Шаг изменения параметра alpha при настройке
b_step = 0.01                            # Шаг изменения параметра beta при настройке

res_u, res_v = 64, 64                   # Разрешение сетки по u и v (количество шагов по каждому параметру)

width, height = 1000, 800              # Размер окна визуализации (ширина и высота)

# Цвета (тёмная тема)
BG_COLOR = (15, 15, 25)                 # Цвет фона (тёмно-синий)
LINE_COLOR = (80, 80, 120, 255)         # Цвет линий сетки (приглушённый синий с полной прозрачностью)
POLY_COLOR = (30, 144, 255, 90)         # Цвет граней полигонов поверхности (голубой с прозрачностью)
AXIS_COLORS = [(255, 85, 85), (85, 255, 85), (85, 170, 255)]  # Цвета осей координат (X — красный, Y — зелёный, Z — синий)
BUTTON_COLOR = (40, 40, 60)             # Цвет кнопок в обычном состоянии
BUTTON_HOVER_COLOR = (60, 60, 90)       # Цвет кнопок при наведении
BUTTON_TEXT_COLOR = (255, 255, 255)     # Цвет текста на кнопках
TEXT_COLOR = (180, 180, 200)            # Цвет основного текста (светло-серый)


# ------------------- КАМЕРА -------------------
def setup_camera():
    theta = np.radians(60)                     # Угол наклона камеры вниз в радианах (60 градусов)
    phi = np.radians(30)                       # Угол поворота камеры в горизонтальной плоскости (30 градусов)
    r = 250                                    # Расстояние от камеры до центра сцены

    x_cam = r * np.sin(theta) * np.cos(phi)    # Координата X позиции камеры в сферических координатах
    y_cam = r * np.sin(theta) * np.sin(phi)    # Координата Y позиции камеры в сферических координатах
    z_cam = r * np.cos(theta)                  # Координата Z позиции камеры в сферических координатах

    forward = np.array([-x_cam, -y_cam, -z_cam])       # Вектор направления взгляда камеры (из позиции камеры в центр)
    forward /= np.linalg.norm(forward)                 # Нормализация вектора взгляда

    tmp = np.array([0, 0, 1]) if abs(forward[2]) < 0.999 else np.array([0, 1, 0])
    # Временный вектор "вверх" — выбирается для предотвращения вырождения при почти вертикальном взгляде

    right = np.cross(forward, tmp)            # Вектор "вправо", вычисляется как векторное произведение взгляда и временного вектора
    right /= np.linalg.norm(right)            # Нормализация вектора "вправо"

    up = np.cross(right, forward)             # Вектор "вверх", вычисляется как векторное произведение "вправо" и взгляда

    return np.array([x_cam, y_cam, z_cam]), right, up, forward  # Возврат позиции камеры и трёх ортонормированных векторов

x_cam, right, up, forward = setup_camera()    # Получение позиции камеры и базисных векторов направления


# ------------------- ПРОЕКЦИЯ -------------------
def rotate_to_camera(x, y, z):
    rot_matrix = np.array([right, up, forward])  # Матрица из трёх векторов камеры: "вправо", "вверх", "вперёд"
    vec = np.array([x - x_cam[0], y - x_cam[1], z - x_cam[2]])  # Вектор от позиции камеры до заданной точки
    return rot_matrix @ vec  # Умножение матрицы поворота на вектор — переход в систему координат камеры

def project_point(x, y, z, width, height, scale=50, perspective=True, d=1000):
    x, y, z = rotate_to_camera(x, y, z)  # Преобразование точки в координатную систему камеры

    if z <= 1e-3:                        # Исключение точек, находящихся за камерой или слишком близко к ней
        return None

    if perspective:                     # Условие для перспективной проекции
        factor = d / z                  # Масштабный коэффициент, уменьшающий размер при удалении
        x_proj = x * factor * scale + width // 2   # Перевод координаты X в экранные координаты
        y_proj = -y * factor * scale + height // 2 # Перевод координаты Y в экранные координаты (ось Y направлена вниз)
    else:                               # Ветвь для ортографической (плоской) проекции
        x_proj = x * scale + width // 2
        y_proj = -y * scale + height // 2

    distance = np.sqrt(x ** 2 + y ** 2 + z ** 2)  # Расстояние до точки от камеры в её системе координат
    return [int(x_proj), int(y_proj), distance]  # Возврат экранных координат и расстояния до точки


def project_line(start, end, color):
    p1 = project_point(*start, width, height)  # Проецирование начальной точки линии
    p2 = project_point(*end, width, height)    # Проецирование конечной точки линии

    if p1 and p2:                              # Проверка, что обе точки находятся перед камерой
        avg_depth = (p1[2] + p2[2]) / 2         # Средняя глубина линии для сортировки по удалённости
        return (avg_depth, p1, p2, color)       # Возврат кортежа с глубиной, точками и цветом
    return None                                 # Возврат None, если хотя бы одна точка не видна


# ------------------- GUI -------------------

def create_button(rect, label, font, screen, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)  # Проверка, наведена ли мышь на кнопку
    color = BUTTON_HOVER_COLOR if hovered else BUTTON_COLOR  # Выбор цвета кнопки в зависимости от наведения
    pygame.draw.rect(screen, color, rect, border_radius=6)  # Отрисовка прямоугольной кнопки с закруглёнными углами
    text = font.render(label, True, BUTTON_TEXT_COLOR)  # Создание текстовой поверхности с подписью кнопки
    text_rect = text.get_rect(center=rect.center)  # Центрирование текста внутри кнопки
    screen.blit(text, text_rect)  # Отображение текста на кнопке
    return hovered  # Возврат флага наведения (используется для обработки клика)


def draw_control_panel(screen, font, mouse_pos):
    global res_u, res_v, param_a, param_b  # Использование глобальных параметров

    start_x = 10  # Начальная координата X панели
    start_y = 80  # Начальная координата Y панели
    btn_w = 180  # Ширина основной кнопки параметра
    btn_h = 35  # Высота кнопок
    gap_y = 15  # Вертикальный отступ между строками

    controls = [  # Список всех параметров, которые можно изменять
        ("Scale", param_a, a_step, 'a'),  # Масштаб
        ("V-Resolution", res_v, 4, 'v'),  # Разрешение по v
        ("U-Resolution", res_u, 4, 'u'),  # Разрешение по u
        ("Detail", param_b, b_step, 'b')  # Детализация поверхности
    ]

    control_buttons.clear()  # Очистка словаря кнопок параметров
    plus_buttons.clear()  # Очистка кнопок увеличения
    minus_buttons.clear()  # Очистка кнопок уменьшения

    for i, (label, val, step, key) in enumerate(controls):  # Обработка каждого элемента панели
        y = start_y + i * (btn_h + gap_y)  # Расчёт Y координаты строки

        ctrl_rect = pygame.Rect(start_x, y, btn_w, btn_h)  # Прямоугольник основной кнопки
        control_buttons[key] = ctrl_rect  # Сохранение кнопки в словарь по ключу
        pygame.draw.rect(screen, BUTTON_COLOR, ctrl_rect, border_radius=6)  # Отрисовка основной кнопки
        text = font.render(label, True, BUTTON_TEXT_COLOR)  # Рендер текста названия параметра
        screen.blit(text, (ctrl_rect.x + 10, ctrl_rect.y + 6))  # Отображение названия параметра слева

        plus_rect = pygame.Rect(start_x + btn_w + 10, y, 40, btn_h)  # Прямоугольник кнопки "+"
        minus_rect = pygame.Rect(start_x + btn_w + 60, y, 40, btn_h)  # Прямоугольник кнопки "-"
        plus_buttons[key] = plus_rect  # Сохранение "+" кнопки
        minus_buttons[key] = minus_rect  # Сохранение "-" кнопки

        for rect, sign in [(plus_rect, "+"), (minus_rect, "-")]:  # Отрисовка "+" и "-"
            hovered = rect.collidepoint(mouse_pos)  # Проверка наведения на кнопку
            color = BUTTON_HOVER_COLOR if hovered else BUTTON_COLOR  # Цвет по наведению
            pygame.draw.rect(screen, color, rect, border_radius=6)  # Отрисовка кнопки
            sign_text = font.render(sign, True, BUTTON_TEXT_COLOR)  # Рендер текста (“+” или “-”)
            sign_rect = sign_text.get_rect(center=rect.center)  # Центрирование знака
            screen.blit(sign_text, sign_rect)  # Отображение знака на кнопке

        val_str = f"{val:.2f}" if isinstance(val, float) else str(val)  # Форматирование значения
        val_text = font.render(val_str, True, BUTTON_TEXT_COLOR)  # Рендер значения параметра
        val_x = start_x + btn_w + 110  # Координата X для значения
        val_y = y + (btn_h - val_text.get_height()) // 2  # Центровка по Y
        screen.blit(val_text, (val_x, val_y))  # Отображение значения


def draw_menu_buttons(screen, font, mouse_pos):
    title_text = "Select surface to render"  # Заголовок меню выбора поверхности
    title_render = font.render(title_text, True, TEXT_COLOR)  # Рендер заголовка
    title_rect = title_render.get_rect(center=(width // 2, 40))  # Центровка заголовка по центру экрана
    screen.blit(title_render, title_rect)  # Отображение заголовка

    btn_w, btn_h = 160, 40  # Размеры кнопок меню
    gap_y = 15  # Отступ между кнопками
    total_height = len(surfaces) * (btn_h + gap_y) - gap_y  # Общая высота блока кнопок
    start_y = (height - total_height) // 2  # Начальная Y координата (по центру)

    surface_button_rects.clear()  # Очистка кнопок выбора поверхностей
    mouse_pos = pygame.mouse.get_pos()  # Получение текущей позиции мыши

    for i, name in enumerate(surfaces.keys()):  # Создание кнопки для каждой поверхности
        x = (width - btn_w) // 2  # Центровка по горизонтали
        y = start_y + i * (btn_h + gap_y)  # Расчёт координаты Y
        rect = pygame.Rect(x, y, btn_w, btn_h)  # Прямоугольник кнопки
        surface_button_rects[name] = rect  # Сохранение кнопки
        hovered = rect.collidepoint(mouse_pos)  # Проверка наведения
        color = BUTTON_HOVER_COLOR if hovered else BUTTON_COLOR  # Цвет кнопки
        pygame.draw.rect(screen, color, rect, border_radius=6)  # Отрисовка кнопки
        text = font.render(name, True, BUTTON_TEXT_COLOR)  # Рендер имени поверхности
        text_rect = text.get_rect(center=rect.center)  # Центровка текста
        screen.blit(text, text_rect)  # Отображение текста


def draw_menu_back_and_save(screen, font, mouse_pos):
    back_rect = pygame.Rect(10, 10, 100, 35)  # Прямоугольник кнопки "Back"
    control_buttons['back'] = back_rect  # Сохранение кнопки в словарь
    hovered_back = back_rect.collidepoint(mouse_pos)  # Проверка наведения
    back_color = BUTTON_HOVER_COLOR if hovered_back else BUTTON_COLOR  # Цвет кнопки
    pygame.draw.rect(screen, back_color, back_rect, border_radius=6)  # Отрисовка кнопки
    back_text = font.render("Back", True, BUTTON_TEXT_COLOR)  # Рендер текста
    back_text_rect = back_text.get_rect(center=back_rect.center)  # Центровка текста
    screen.blit(back_text, back_text_rect)  # Отображение текста кнопки

    save_rect = pygame.Rect(width - 110, 10, 100, 35)  # Прямоугольник кнопки "Save"
    control_buttons['save'] = save_rect  # Сохранение кнопки в словарь
    hovered_save = save_rect.collidepoint(mouse_pos)  # Проверка наведения
    save_color = BUTTON_HOVER_COLOR if hovered_save else BUTTON_COLOR  # Цвет кнопки
    pygame.draw.rect(screen, save_color, save_rect, border_radius=6)  # Отрисовка кнопки
    save_text = font.render("Save", True, BUTTON_TEXT_COLOR)  # Рендер текста
    save_text_rect = save_text.get_rect(center=save_rect.center)  # Центровка текста
    screen.blit(save_text, save_text_rect)  # Отображение текста кнопки


# ------------------- ОТРИСОВКА ПОВЕРХНОСТИ -------------------
def render_surface(screen, font, save_to_file=False):
    surface_func = surfaces[current_surface_name]                       # Получение функции текущей поверхности по её имени
    u_range = np.linspace(u_limits[0], u_limits[1], res_u)             # Массив значений параметра u с равномерным шагом
    v_range = np.linspace(v_limits[0], v_limits[1], res_v)             # Массив значений параметра v с равномерным шагом

    poly_points = [[None for _ in v_range] for _ in u_range]           # Инициализация двумерного массива точек проекций

    for i, u in enumerate(u_range):                                    # Перебор всех значений u
        for j, v in enumerate(v_range):                                # Перебор всех значений v
            x, y, z = surface_func(u, v, param_a, param_b)             # Вычисление 3D-координат поверхности в точке (u, v)
            projected = project_point(x, y, z, width, height)          # Проецирование точки на экран
            poly_points[i][j] = projected                              # Сохранение проекции в массив точек

    surface_lines = []  # Инициализация списка отрезков для каркаса

    for i in range(len(u_range)):  # Проход по индексам массива u
        for j in range(len(v_range)):  # Проход по индексам массива v
            curr = poly_points[i][j]  # Текущая проецированная точка
            if curr is None:  # Пропуск, если точка не определена
                continue
            if j < len(v_range) - 1:  # Проверка наличия правого соседа
                right_ = poly_points[i][j + 1]  # Правая соседняя точка
                if right_:  # Проверка на None
                    surface_lines.append([curr, right_, LINE_COLOR])  # Добавление отрезка вправо
            if i < len(u_range) - 1:  # Проверка наличия нижнего соседа
                down = poly_points[i + 1][j]  # Нижняя соседняя точка
                if down:  # Проверка на None
                    surface_lines.append([curr, down, LINE_COLOR])  # Добавление отрезка вниз

    polygons = []  # Инициализация списка полигонов (четырёхугольников)

    for i in range(len(u_range) - 1):  # Проход по строкам (u)
        for j in range(len(v_range) - 1):  # Проход по столбцам (v)
            p1 = poly_points[i][j]  # Левая верхняя точка полигона
            p2 = poly_points[i][j + 1]  # Правая верхняя точка полигона
            p3 = poly_points[i + 1][j + 1]  # Правая нижняя точка полигона
            p4 = poly_points[i + 1][j]  # Левая нижняя точка полигона
            if None not in (p1, p2, p3, p4):  # Проверка на существование всех точек
                avg_depth = (p1[2] + p2[2] + p3[2] + p4[2]) / 4  # Средняя глубина полигона для сортировки
                polygons.append([avg_depth, [p1, p2, p3, p4]])  # Добавление полигона в список

    polygons.sort(key=lambda x: -x[0])  # Сортировка полигонов по убыванию глубины (z-буфер)

    for _, poly in polygons:  # Отрисовка всех полигонов
        points_2d = [(p[0], p[1]) for p in poly]  # Извлечение 2D-координат
        pygame.draw.polygon(screen, POLY_COLOR, points_2d)  # Отрисовка полигона на экране

    for line in surface_lines:  # Отрисовка всех каркасных линий
        p1, p2, color = line  # Извлечение начала, конца и цвета линии
        pygame.draw.line(screen, color, (p1[0], p1[1]), (p2[0], p2[1]))  # Рисование линии между двумя точками

    # Подписи осей
    axes = [  # Определение векторов координатных осей
        (np.array([10, 0, 0]), AXIS_COLORS[0]),  # Ось X — красная
        (np.array([0, 10, 0]), AXIS_COLORS[1]),  # Ось Y — зелёная
        (np.array([0, 0, 10]), AXIS_COLORS[2])  # Ось Z — синяя
    ]

    origin = np.array([0, 0, 0])  # Начало координат
    origin_proj = project_point(*origin, width, height)  # Проецирование начала координат
    if origin_proj:  # Проверка на успешное проецирование
        for axis_vec, color in axes:  # Перебор осей и их цветов
            end = origin + axis_vec  # Конечная точка оси
            end_proj = project_point(*end, width, height)  # Проецирование конца оси
            if end_proj:  # Проверка на None
                pygame.draw.line(screen, color, (origin_proj[0], origin_proj[1]),
                                 (end_proj[0], end_proj[1]), 2)  # Рисование линии оси с толщиной 2


def save_screenshot(screen):
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"  # Формирование уникального имени файла с текущей датой и временем
    pygame.image.save(screen, filename)                                               # Сохранение содержимого экрана в файл PNG
    print(f"Saved screenshot: {filename}")                                            # Вывод сообщения об успешном сохранении

# ------------------- ОСНОВНОЙ ЦИКЛ -------------------

def main():                                                                 # Главная функция запуска визуализатора
    global current_surface_name, u_limits, v_limits, param_a, param_b, res_u, res_v  # Объявление глобальных переменных для параметров и состояния

    pygame.init()                                                           # Инициализация всех модулей Pygame
    screen = pygame.display.set_mode((width, height))                       # Создание окна с заданными размерами
    pygame.display.set_caption("Parametric Surfaces Renderer")             # Установка заголовка окна
    font = pygame.font.SysFont("Arial", 18)                                # Создание шрифта Arial размером 18

    clock = pygame.time.Clock()                                             # Создание объекта для контроля частоты кадров
    running = True                                                          # Флаг основного цикла
    in_menu = True                                                          # Флаг показа стартового меню

    while running:                                                          # Основной игровой цикл
        mouse_pos = pygame.mouse.get_pos()                                  # Получение текущей позиции мыши
        screen.fill(BG_COLOR)                                               # Очистка экрана заданным цветом фона

        for event in pygame.event.get():  # Обработка всех событий в очереди
            if event.type == pygame.QUIT:  # Если нажата кнопка закрытия окна
                running = False  # Завершение основного цикла

            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                if in_menu:  # Если находимся в главном меню
                    for name, rect in surface_button_rects.items():  # Перебор всех кнопок выбора поверхности
                        if rect.collidepoint(mouse_pos):  # Если клик попал в кнопку
                            current_surface_name = name  # Установка выбранного имени поверхности
                            u_limits, v_limits = surface_bounds[name]  # Установка диапазонов параметров u и v
                            param_a, param_b = 0.1, 0.05  # Начальные значения параметров alpha и beta
                            in_menu = False  # Переход в режим отображения поверхности


                else:  # Если не в меню (на экране визуализации)
                    if control_buttons.get('back') and control_buttons['back'].collidepoint(
                            mouse_pos):  # Кнопка "назад"
                        in_menu = True  # Возврат в меню
                        current_surface_name = None  # Сброс текущей поверхности

                    if control_buttons.get('save') and control_buttons['save'].collidepoint(
                            mouse_pos):  # Кнопка "сохранить"
                        save_screenshot(screen)  # Вызов функции сохранения скриншота

                    # Управление параметрами
                    for key in plus_buttons.keys():  # Перебор всех "+" кнопок
                        if plus_buttons[key].collidepoint(mouse_pos):  # Если нажата кнопка "+"
                            if key == 'a':  # Увеличение параметра a
                                param_a += a_step
                            elif key == 'b':  # Увеличение параметра b
                                param_b += b_step
                            elif key == 'u':  # Увеличение разрешения по u (но не более 512)
                                res_u = min(res_u + 4, 512)
                            elif key == 'v':  # Увеличение разрешения по v (но не более 512)
                                res_v = min(res_v + 4, 512)

                        if minus_buttons[key].collidepoint(mouse_pos):  # Если нажата кнопка "-"
                            if key == 'a':  # Уменьшение параметра a (не менее 0.01)
                                param_a = max(0.01, param_a - a_step)
                            elif key == 'b':  # Уменьшение параметра b (не менее 0.001)
                                param_b = max(0.001, param_b - b_step)
                            elif key == 'u':  # Уменьшение разрешения по u (не менее 4)
                                res_u = max(4, res_u - 4)
                            elif key == 'v':  # Уменьшение разрешения по v (не менее 4)
                                res_v = max(4, res_v - 4)

        if in_menu:  # Если активен режим меню
            draw_menu_buttons(screen, font, mouse_pos)  # Отрисовка кнопок выбора поверхности
        else:  # Если активен режим отображения поверхности
            render_surface(screen, font)  # Отрисовка выбранной поверхности
            draw_control_panel(screen, font, mouse_pos)  # Отрисовка панели управления параметрами
            draw_menu_back_and_save(screen, font, mouse_pos)  # Отрисовка кнопок "назад" и "сохранить"

        pygame.display.flip()  # Обновление содержимого экрана
        clock.tick(30)  # Ограничение частоты кадров до 30 FPS

    pygame.quit()  # Завершение работы Pygame
    sys.exit()  # Завершение программы


# ------------------- Глобальные словари для кнопок -------------------
surface_button_rects = {}
control_buttons = {}
plus_buttons = {}
minus_buttons = {}

if __name__ == "__main__":
    main()
