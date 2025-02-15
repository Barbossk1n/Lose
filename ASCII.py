from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import filedialog, Scale, Button, Label, HORIZONTAL, VERTICAL, RIGHT, LEFT, Y, X, BOTH, NW
from threading import Thread
import queue
import time  # Добавляем модуль time

# Очередь для передачи данных между потоками
image_queue = queue.Queue()

# Функция для создания ASCII-арта из изображения
def create_ascii_image(image, tile_width, tile_height):
    ascii_image = Image.new("RGB", (image.width, image.height), "white")
    draw = ImageDraw.Draw(ascii_image)
    font = ImageFont.load_default()  # Используем стандартный шрифт

    for y in range(0, image.height, tile_height):
        for x in range(0, image.width, tile_width):
            box = (x, y, x + tile_width, y + tile_height)
            image_part = image.crop(box)
            r, g, b = image_part.getpixel((0, 0))  # Берем цвет из первого пикселя
            draw.rectangle(box, fill=(r, g, b))
            draw.text((x, y), "█", fill=(r, g, b), font=font)

    return ascii_image

# Функция для обновления ASCII-арта в реальном времени
def update_ascii_art():
    global image, tile_size
    tile_size = scale.get()

    # Ограничиваем частоту обновления
    if not hasattr(update_ascii_art, "last_update"):
        update_ascii_art.last_update = 0
    current_time = int(time.time() * 1000)  # Получаем текущее время в миллисекундах
    if current_time - update_ascii_art.last_update < 100:  # Обновляем не чаще чем раз в 100 мс
        return
    update_ascii_art.last_update = current_time

    # Запускаем обработку в отдельном потоке
    Thread(target=process_image_thread, args=(image, tile_size), daemon=True).start()

# Функция для обработки изображения в отдельном потоке
def process_image_thread(image, tile_size):
    ascii_image = create_ascii_image(image, tile_size, tile_size)
    image_queue.put(ascii_image)

# Функция для загрузки изображения
def load_image():
    global image
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if file_path:
        image = Image.open(file_path)
        tk_image = ImageTk.PhotoImage(image)
        original_canvas.create_image(0, 0, anchor=NW, image=tk_image)
        original_canvas.image = tk_image  # Сохраняем ссылку
        original_canvas.config(scrollregion=original_canvas.bbox("all"))  # Обновляем область прокрутки
        update_ascii_art()

# Функция для сохранения ASCII-арта
def save_ascii_art():
    global image, tile_size
    ascii_image = create_ascii_image(image, tile_size, tile_size)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp"), ("GIF files", "*.gif")],
    )
    if file_path:
        ascii_image.save(file_path)
        print(f"Изображение сохранено как {file_path}")

# Функция для обработки изменения размеров окна
def on_resize(event):
    # Обновляем размеры контейнеров и скроллов
    original_canvas.config(width=event.width // 2, height=event.height - 100)
    ascii_canvas.config(width=event.width // 2, height=event.height - 100)

# Функция для проверки очереди и обновления интерфейса
def check_queue():
    try:
        while True:
            ascii_image = image_queue.get_nowait()
            tk_ascii_image = ImageTk.PhotoImage(ascii_image)
            ascii_canvas.create_image(0, 0, anchor=NW, image=tk_ascii_image)
            ascii_canvas.image = tk_ascii_image  # Сохраняем ссылку
            ascii_canvas.config(scrollregion=ascii_canvas.bbox("all"))  # Обновляем область прокрутки
    except queue.Empty:
        pass
    root.after(100, check_queue)  # Проверяем очередь каждые 100 мс

# Основная функция
def main():
    global image, tile_size, scale, original_canvas, ascii_canvas, root

    # Инициализация главного окна
    root = tk.Tk()
    root.title("ASCII Art Generator")

    # Устанавливаем окно в "максимизированный" режим (полноэкранный с доступной верхней панелью)
    root.state("zoomed")

    #Загрузка иконки приложения
    try:
        #Указываем путь
        icon_image = ImageTk.PhotoImage(file="D:\\Python\\Skrydge\\Lessons\\icon\\P.png")
        root.iconphoto(True, icon_image)
    except Exception as e:
        print(f"Произошла ошибка загрузки сторонней иконки!")

    # Загрузка изображения по умолчанию
    try:
        image = Image.open("read")
    except FileNotFoundError:
        image = Image.new("RGB", (100, 100), "white")  # Заглушка, если изображение не найдено

    # Панель управления
    control_panel = tk.Frame(root)
    control_panel.pack(side="bottom", fill="x", pady=10)

    # Кнопка для загрузки изображения
    load_button = Button(control_panel, text="Загрузить изображение", command=load_image)
    load_button.pack(side="left", padx=10)

    # Слайдер для изменения размера ASCII-арта
    scale = Scale(control_panel, from_=1, to=50, orient=HORIZONTAL, label="Размер ASCII-арта", command=lambda _: update_ascii_art())
    scale.set(10)  # Значение по умолчанию
    scale.pack(side="left", padx=755)

    # Кнопка для сохранения ASCII-арта
    save_button = Button(control_panel, text="Сохранить ASCII-арт", command=save_ascii_art)
    save_button.pack(side="right", padx=10)

    # Контейнер для оригинального изображения и ASCII-арта
    image_frame = tk.Frame(root)
    image_frame.pack(side="top", fill="both", expand=True)

    # Оригинальное изображение с прокруткой
    original_frame = tk.Frame(image_frame)
    original_frame.pack(side="left", fill="both", expand=True)

    original_canvas = tk.Canvas(original_frame)
    original_canvas.pack(side="left", fill="both", expand=True)

    original_scroll_y = tk.Scrollbar(original_frame, orient=VERTICAL, command=original_canvas.yview)
    original_scroll_y.pack(side="right", fill="y")
    original_scroll_x = tk.Scrollbar(original_frame, orient=HORIZONTAL, command=original_canvas.xview)
    original_scroll_x.pack(side="bottom", fill="x")

    original_canvas.configure(yscrollcommand=original_scroll_y.set, xscrollcommand=original_scroll_x.set)
    original_canvas.bind("<Configure>", lambda e: original_canvas.configure(scrollregion=original_canvas.bbox("all")))

    # ASCII-арт с прокруткой
    ascii_frame = tk.Frame(image_frame)
    ascii_frame.pack(side="right", fill="both", expand=True)

    ascii_canvas = tk.Canvas(ascii_frame)
    ascii_canvas.pack(side="left", fill="both", expand=True)

    ascii_scroll_y = tk.Scrollbar(ascii_frame, orient=VERTICAL, command=ascii_canvas.yview)
    ascii_scroll_y.pack(side="right", fill="y")
    ascii_scroll_x = tk.Scrollbar(ascii_frame, orient=HORIZONTAL, command=ascii_canvas.xview)
    ascii_scroll_x.pack(side="bottom", fill="x")

    ascii_canvas.configure(yscrollcommand=ascii_scroll_y.set, xscrollcommand=ascii_scroll_x.set)
    ascii_canvas.bind("<Configure>", lambda e: ascii_canvas.configure(scrollregion=ascii_canvas.bbox("all")))

    # Обработка изменения размеров окна
    root.bind("<Configure>", on_resize)

    # Запуск проверки очереди
    root.after(100, check_queue)

    # Инициализация интерфейса
    load_image()  # Загружаем изображение по умолчанию
    root.mainloop()

if __name__ == "__main__":
    main()