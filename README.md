# Визуализация параметрических поверхностей

## 1. Введение

**Цель работы:** Разработка интерактивного 3D-визуализатора для изучения параметрических поверхностей с возможностью настройки параметров и сохранения результатов.

**Используемые технологии:** Python, библиотеки Pygame и NumPy.

**Особенности проекта:**
- Поддержка 5 типов поверхностей.
- Реализация перспективной проекции.
- Интерактивное управление.

## 2. Теоретическая часть

### 2.1. Параметрические поверхности

Параметрические поверхности задаются функцией:

```
F(u,v) = (x(u,v), y(u,v), z(u,v)),  где u ∈ [a, b], v ∈ [c, d]
```

Пример — уравнение морской раковины:

![изображение](https://github.com/user-attachments/assets/bbd19849-a740-4039-8c48-9f680ab5ff66)


### 2.2. Математические основы

#### Проекция 3D → 2D

Используется перспективная проекция:

![изображение](https://github.com/user-attachments/assets/9481a093-f7e2-461a-8b04-c12099f67305)


#### Матрицы поворота

Поворот вокруг оси X:

![изображение](https://github.com/user-attachments/assets/368b15bd-0a72-42e4-bc42-e1c1e53888df)


Поворот вокруг оси Y:

![изображение](https://github.com/user-attachments/assets/f2030e0e-58b8-4789-8a23-bfe13fbcb470)


#### Нормализация векторов

![изображение](https://github.com/user-attachments/assets/b222e489-e75b-4a8e-9882-3bb1c48d78f1)


## 3. Реализация

### 3.1. Архитектура проекта

**Библиотеки:**
- `Pygame` — графический интерфейс, обработка событий.
- `NumPy` — математика и массивы.
- `sys`, `datetime` — вспомогательные модули.

**Ключевые модули:**
- **Генерация поверхностей** - `seashell_surface`, `mobius_surface`, `torus_surface`, `spiral_surface`, `helical_surface`
- Каждая функция принимает параметры `u`, `v`, `alpha`, `beta` и возвращает координаты точки `(x, y, z)` в 3D-пространстве:
  ```python
  def mobius_surface(u, v, alpha, beta):
      u_rad = np.radians(u)
      x = (alpha + v * np.cos(u_rad / 2)) * np.cos(u_rad)
      y = (alpha + v * np.cos(u_rad / 2)) * np.sin(u_rad)
      z = beta * v * np.sin(u_rad / 2)
      return x, y, z
  ```

- **Настройка камеры** - `setup_camera`
- Инициализирует позицию камеры в сферических координатах и базисные векторы (`right`, `up`, `forward`):
  ```python
  theta = np.radians(60)
  phi = np.radians(30)
  x_cam = r * np.sin(theta) * np.cos(phi)
  y_cam = r * np.sin(theta) * np.sin(phi)
  z_cam = r * np.cos(theta)
  ```

- **Проекция 3D → 2D** - `project_point`
- Преобразует мировые координаты в экранные с учётом перспективы:
  ```python
  def project_point(x, y, z, width, height, perspective=True, d=1000):
      x_rot, y_rot, z_rot = rotate_to_camera(x, y, z)
      if perspective:
          factor = d / (z_rot + 1e-5)
          x_proj = x_rot * factor * scale + width // 2
          y_proj = -y_rot * factor * scale + height // 2
      else:
          x_proj = x_rot * scale + width // 2
          y_proj = -y_rot * scale + height // 2
      return [int(x_proj), int(y_proj), np.sqrt(x_rot**2 + y_rot**2 + z_rot**2)]
  ```

- **Рендеринг поверхности** - `render_surface`
- Генерирует сетку точек, проецирует их на экран и рисует полигоны с Z-буферизацией:
  ```python
  polygons = []
  for i in range(len(u_range) - 1):
      for j in range(len(v_range) - 1):
          p1 = poly_points[i][j]
          p2 = poly_points[i][j + 1]
          p3 = poly_points[i + 1][j + 1]
          p4 = poly_points[i + 1][j]
          if None not in (p1, p2, p3, p4):
              avg_depth = (p1[2] + p2[2] + p3[2] + p4[2]) / 4
              polygons.append((avg_depth, [p1[:2], p2[:2], p3[:2], p4[:2]]))
  polygons.sort(key=lambda x: -x[0])
  ```

- Графический интерфейс (`draw_control_panel`, `draw_menu_buttons`):
    Кнопки для выбора поверхности (`surface_button_rects`).
    Слайдеры параметров (`alpha`, `beta`, `разрешение сетки`).
    Обработчик событий мыши для интерактивного управления.

### 3.2. Ключевые алгоритмы

#### Сетка
```python
u_range = np.linspace(0, 2 * np.pi, res_u)
v_range = np.linspace(0, 2 * np.pi, res_v)
```

#### Z-буферизация

Сортировка полигонов по средней глубине (avg_depth).

#### Перспективная проекция

Учитывает расстояние до камеры:

```
x_proj = (d * x / z) * scale + center_x
```

#### Вращение сцены

Обновление углов `theta`, `phi` и пересчёт базиса камеры.

## 4. Результаты работы

### 4.1. Примеры визуализации


> **Спиральная поверхность**
> 
> Параметры: Scale = 0.1, V-Resolution = 16, U-Resolution = 76, Detail = 0.13
> 
> ![изображение](https://github.com/user-attachments/assets/e1e66c4e-8904-4a4e-be06-7c11cdd55241)


> **Лента Мёбиуса**
> 
> Параметры: Scale = 0.8, V-Resolution = 88, U-Resolution = 84, Detail = 0.59
> 
> ![изображение](https://github.com/user-attachments/assets/f54f90c1-9ab0-403a-9b36-6f34a6728031)

> **Тор**
> 
> Параметры: Scale = 1.2, V-Resolution = 116, U-Resolution = 92, Detail = 0.43
> 
> ![изображение](https://github.com/user-attachments/assets/d4cb7406-5bea-45d8-a494-a2b02500144e)


> **Морская раковина**
> 
> Параметры: Scale = 0.3, V-Resolution = 72, U-Resolution = 72, Detail = 0.06
> 
> ![изображение](https://github.com/user-attachments/assets/01026a5c-9eb0-4ee6-bd2e-c837810d6cbb)

### 4.2. Интерактивные возможности

- Изменение параметров в реальном времени.
- Сохранение скриншота (кнопка `Save`).

## 5. Заключение

**Итоги:** Реализован инструмент для интерактивного изучения параметрических поверхностей.

**Проблемы и решения:**
- Оптимизация рендеринга при высоком разрешении.
- Корректная обработка граничных параметров.

**Дальнейшие шаги:**
- Анимация и автовращение.
- Свободная камера и произвольное перемещение.
