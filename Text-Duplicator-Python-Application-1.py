import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

def setup_clipboard_bindings(widget):
    """Настроить привязки для копирования/вставки/вырезания и SelectAll."""
    def gen(event_name):
        return lambda e: (widget.event_generate(event_name), "break")
    
    # Windows/Linux: Ctrl
    widget.bind("<Control-c>", gen("<<Copy>>"))
    widget.bind("<Control-v>", gen("<<Paste>>"))
    widget.bind("<Control-x>", gen("<<Cut>>"))
    widget.bind("<Control-a>", lambda e: (widget.tag_add("sel", "1.0", "end"), "break"))
    
    # macOS: Command
    widget.bind("<Command-c>", gen("<<Copy>>"))
    widget.bind("<Command-v>", gen("<<Paste>>"))
    widget.bind("<Command-x>", gen("<<Cut>>"))
    widget.bind("<Command-a>", lambda e: (widget.tag_add("sel", "1.0", "end"), "break"))
    
    # При клике — ставим фокус в виджет
    widget.bind("<Button-1>", lambda e: widget.focus_set())
    
    # Контекстное меню (правый клик)
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Копировать", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_command(label="Вырезать", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_separator()
    menu.add_command(label="Выделить всё", command=lambda: widget.tag_add("sel", "1.0", "end"))
    
    def show_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    widget.bind("<Button-3>", show_menu)
    widget.bind("<Control-Button-1>", show_menu)  # для macOS

def load_code_file():
    """Загружает текстовый файл и отображает его в текстовом поле."""
    path = filedialog.askopenfilename(
        filetypes=[
            ("Text files", "*.txt;*.py;*.js;*.java;*.cpp;*.c;*.html;*.css;*.md"),
            ("Python files", "*.py"),
            ("All files", "*.*")
        ]
    )
    if not path:
        return
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
        return
    
    # Отображаем имя файла
    filename_label.config(text=f"Файл: {os.path.basename(path)}")
    
    # Сохраняем путь для сохранения
    global current_file_path
    current_file_path = path
    
    # Отображаем содержимое
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", content)
    
    # Показываем количество строк
    line_count = content.count('\n') + 1
    status_label.config(text=f"Строк: {line_count}")

def duplicate_text():
    """Дублирует текст указанное количество раз."""
    try:
        duplicate_count = int(duplicate_var.get())
        if duplicate_count < 1:
            raise ValueError("Количество дублирований должно быть положительным")
    except ValueError as e:
        messagebox.showerror("Ошибка", f"Некорректное количество дублирований: {e}")
        return
    
    # Получаем исходный текст
    original_text = text_widget.get("1.0", tk.END).rstrip('\n')
    if not original_text.strip():
        messagebox.showwarning("Пустой текст", "Текст для обработки пустой")
        return
    
    # Дублируем текст
    duplicated_text = (original_text + '\n') * duplicate_count
    duplicated_text = duplicated_text.rstrip('\n')
    
    # Обновляем текст в поле
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", duplicated_text)
    
    # Показываем количество строк после обработки
    line_count = duplicated_text.count('\n') + 1
    status_label.config(text=f"Строк: {line_count} (дублировано {duplicate_count} раз)")

def save_duplicated_text():
    """Сохраняет дублированный текст в новый файл."""
    if not text_widget.get("1.0", tk.END).strip():
        messagebox.showwarning("Пустой текст", "Нет текста для сохранения")
        return
    
    # Предлагаем сохранить как новый файл
    if current_file_path:
        default_name = os.path.splitext(current_file_path)[0] + "_duplicated" + os.path.splitext(current_file_path)[1]
    else:
        default_name = "duplicated_text.txt"
    
    save_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[
            ("Text files", "*.txt"),
            ("Python files", "*.py"),
            ("All files", "*.*")
        ],
        initialfile=default_name
    )
    
    if not save_path:
        return
    
    try:
        content = text_widget.get("1.0", tk.END)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("Успех", f"Файл сохранен:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

def clear_text():
    """Очищает текстовое поле."""
    text_widget.delete("1.0", tk.END)
    filename_label.config(text="Файл: не выбран")
    status_label.config(text="Строк: 0")
    global current_file_path
    current_file_path = None

def preview_duplicate():
    """Предпросмотр дублирования текста."""
    try:
        duplicate_count = int(duplicate_var.get())
        if duplicate_count < 1:
            raise ValueError("Количество дублирований должно быть положительным")
    except ValueError as e:
        messagebox.showerror("Ошибка", f"Некорректное количество дублирований: {e}")
        return
    
    # Получаем первые 5 строк для предпросмотра
    original_text = text_widget.get("1.0", tk.END).rstrip('\n')
    if not original_text.strip():
        return
    
    lines = original_text.split('\n')[:5]
    preview_lines = []
    
    for i, line in enumerate(lines):
        preview_lines.append(f"Строка {i+1}: {line}")
    
    # Показываем предпросмотр
    preview_text = "\n".join(preview_lines)
    if len(lines) < 5:
        preview_label.config(text=f"Предпросмотр (все строки):\n{preview_text}\n\nБудет дублировано {duplicate_count} раз")
    else:
        preview_label.config(text=f"Предпросмотр (первые 5 строк):\n{preview_text}\n\nБудет дублировано {duplicate_count} раз")

# Глобальные переменные
current_file_path = None

# --- GUI ---
root = tk.Tk()
root.title("Дубликатор текста")
root.geometry("1000x700")

# Верхняя панель управления
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=10, pady=10)

# Загрузка файла
load_btn = tk.Button(top_frame, text="Загрузить файл", command=load_code_file, width=20)
load_btn.pack(side=tk.LEFT, padx=(0, 10))

# Поле для ввода количества дублирований
duplicate_frame = tk.Frame(top_frame)
duplicate_frame.pack(side=tk.LEFT, padx=(0, 10))

duplicate_label = tk.Label(duplicate_frame, text="Дублировать:")
duplicate_label.pack(side=tk.LEFT)

duplicate_var = tk.StringVar(value="2")  # Значение по умолчанию
duplicate_entry = tk.Entry(duplicate_frame, textvariable=duplicate_var, width=5)
duplicate_entry.pack(side=tk.LEFT, padx=(5, 0))

times_label = tk.Label(duplicate_frame, text="раз")
times_label.pack(side=tk.LEFT, padx=(5, 0))

# Кнопка предпросмотра
preview_btn = tk.Button(top_frame, text="Предпросмотр", command=preview_duplicate, width=15)
preview_btn.pack(side=tk.LEFT, padx=(0, 10))

# Кнопка дублирования
duplicate_btn = tk.Button(top_frame, text="Дублировать текст", command=duplicate_text, width=20)
duplicate_btn.pack(side=tk.LEFT, padx=(0, 10))

# Кнопка сохранения
save_btn = tk.Button(top_frame, text="Сохранить результат", command=save_duplicated_text, width=20)
save_btn.pack(side=tk.LEFT, padx=(0, 10))

# Кнопка очистки
clear_btn = tk.Button(top_frame, text="Очистить", command=clear_text, width=15)
clear_btn.pack(side=tk.LEFT)

# Метка с именем файла
filename_label = tk.Label(root, text="Файл: не выбран", anchor="w")
filename_label.pack(fill=tk.X, padx=10, pady=(0, 5))

# Основное текстовое поле
text_frame = tk.Frame(root)
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

text_widget = scrolledtext.ScrolledText(
    text_frame,
    wrap=tk.NONE,
    font=("Consolas", 11),
    undo=True
)
text_widget.pack(fill=tk.BOTH, expand=True)

# Настройка буфера обмена
setup_clipboard_bindings(text_widget)

# Метка предпросмотра
preview_label = tk.Label(root, 
                         text="Предпросмотр: загрузите файл и нажмите 'Предпросмотр'",
                         anchor="w", 
                         justify=tk.LEFT, 
                         relief=tk.SUNKEN, 
                         bg="#f0f0f0")
preview_label.pack(fill=tk.X, padx=10, pady=(5, 5))

# Статусная строка
status_frame = tk.Frame(root)
status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

status_label = tk.Label(status_frame, text="Строк: 0", anchor="w")
status_label.pack(side=tk.LEFT)

help_label = tk.Label(status_frame,
                     text="Формат: весь текст будет дублирован указанное количество раз",
                     anchor="e")
help_label.pack(side=tk.RIGHT)

# Запуск приложения
root.mainloop()
