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

def open_replace_window():
    """Открывает окно для замены символов."""
    replace_window = tk.Toplevel(root)
    replace_window.title("Замена символов")
    replace_window.geometry("500x300")
    replace_window.resizable(False, False)
    
    # Центрирование окна
    replace_window.update_idletasks()
    width = replace_window.winfo_width()
    height = replace_window.winfo_height()
    x = (replace_window.winfo_screenwidth() // 2) - (width // 2)
    y = (replace_window.winfo_screenheight() // 2) - (height // 2)
    replace_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Инструкция
    instruction_label = tk.Label(
        replace_window,
        text="Введите символы для замены. Каждый символ из первого поля\n"
             "будет заменен на соответствующий символ из второго поля.\n"
             "Пример: если ввести 'abc' и 'xyz', то все 'a' заменятся на 'x',\n"
             "'b' на 'y', 'c' на 'z'.",
        justify=tk.LEFT,
        wraplength=450,
        pady=10
    )
    instruction_label.pack(padx=20, pady=(10, 5))
    
    # Поле для символов, которые нужно заменить
    frame1 = tk.Frame(replace_window)
    frame1.pack(padx=20, pady=10, fill=tk.X)
    
    label1 = tk.Label(frame1, text="Символы для замены:", width=20, anchor="w")
    label1.pack(side=tk.LEFT)
    
    replace_from_var = tk.StringVar()
    entry1 = tk.Entry(frame1, textvariable=replace_from_var, width=30)
    entry1.pack(side=tk.LEFT, padx=(10, 0))
    
    # Поле для символов, на которые нужно заменить
    frame2 = tk.Frame(replace_window)
    frame2.pack(padx=20, pady=10, fill=tk.X)
    
    label2 = tk.Label(frame2, text="Заменить на:", width=20, anchor="w")
    label2.pack(side=tk.LEFT)
    
    replace_to_var = tk.StringVar()
    entry2 = tk.Entry(frame2, textvariable=replace_to_var, width=30)
    entry2.pack(side=tk.LEFT, padx=(10, 0))
    
    # Пример
    example_label = tk.Label(
        replace_window,
        text="Пример: 'abc' → 'xyz' заменит все 'a' на 'x', 'b' на 'y', 'c' на 'z'",
        font=("Arial", 9),
        fg="gray",
        justify=tk.LEFT,
        wraplength=450
    )
    example_label.pack(padx=20, pady=5)
    
    # Кнопки
    button_frame = tk.Frame(replace_window)
    button_frame.pack(padx=20, pady=20)
    
    def apply_replace():
        """Применить замену символов."""
        from_chars = replace_from_var.get()
        to_chars = replace_to_var.get()
        
        if not from_chars:
            messagebox.showwarning("Предупреждение", "Введите символы для замены")
            return
        
        if len(from_chars) != len(to_chars):
            messagebox.showwarning("Предупреждение", 
                                 f"Количество символов должно совпадать!\n"
                                 f"Символов для замены: {len(from_chars)}\n"
                                 f"Символов для замены на: {len(to_chars)}")
            return
        
        # Получаем текущий текст
        current_text = text_widget.get("1.0", tk.END).rstrip('\n')
        if not current_text:
            messagebox.showwarning("Предупреждение", "Нет текста для обработки")
            return
        
        # Выполняем замену
        translation_table = str.maketrans(from_chars, to_chars)
        new_text = current_text.translate(translation_table)
        
        # Обновляем текст в поле
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", new_text)
        
        # Показываем статистику
        changes_count = 0
        for char in current_text:
            if char in from_chars:
                changes_count += 1
        
        # Исправленная строка - считаем количество строк правильно
        line_count = new_text.count('\n') + 1
        status_label.config(text=f"Строк: {line_count} (заменено {changes_count} символов)")
        messagebox.showinfo("Успех", f"Заменено {changes_count} символов")
        replace_window.destroy()
    
    def preview_replace():
        """Предпросмотр замены."""
        from_chars = replace_from_var.get()
        to_chars = replace_to_var.get()
        
        if not from_chars:
            messagebox.showwarning("Предупреждение", "Введите символы для замены")
            return
        
        if len(from_chars) != len(to_chars):
            messagebox.showwarning("Предупреждение", 
                                 f"Количество символов должно совпадать!\n"
                                 f"Символов для замены: {len(from_chars)}\n"
                                 f"Символов для замены на: {len(to_chars)}")
            return
        
        # Получаем первые 5 строк текущего текста
        current_text = text_widget.get("1.0", tk.END).rstrip('\n')
        if not current_text:
            messagebox.showwarning("Предупреждение", "Нет текста для обработки")
            return
        
        lines = current_text.split('\n')[:5]
        preview_lines = []
        
        translation_table = str.maketrans(from_chars, to_chars)
        
        for i, line in enumerate(lines):
            new_line = line.translate(translation_table)
            if line != new_line:
                preview_lines.append(f"Строка {i+1}: {line} → {new_line}")
            else:
                preview_lines.append(f"Строка {i+1}: {line} (без изменений)")
        
        # Показываем предпросмотр
        preview_text = "\n".join(preview_lines)
        if len(lines) < 5:
            preview_label.config(text=f"Предпросмотр замены (все строки):\n{preview_text}")
        else:
            preview_label.config(text=f"Предпросмотр замены (первые 5 строк):\n{preview_text}")
    
    apply_btn = tk.Button(button_frame, text="Применить замену", command=apply_replace, width=20)
    apply_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    preview_btn = tk.Button(button_frame, text="Предпросмотр", command=preview_replace, width=15)
    preview_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_btn = tk.Button(button_frame, text="Отмена", command=replace_window.destroy, width=15)
    cancel_btn.pack(side=tk.LEFT)

# Глобальные переменные
current_file_path = None

# --- GUI ---
root = tk.Tk()
root.title("Дубликатор текста с заменой символов")
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

# Кнопка предпросмотра дублирования
preview_duplicate_btn = tk.Button(top_frame, text="Предпросмотр", command=preview_duplicate, width=15)
preview_duplicate_btn.pack(side=tk.LEFT, padx=(0, 10))

# Кнопка дублирования
duplicate_btn = tk.Button(top_frame, text="Дублировать текст", command=duplicate_text, width=20)
duplicate_btn.pack(side=tk.LEFT, padx=(0, 10))

# Кнопка замены символов
replace_btn = tk.Button(top_frame, text="Заменить символы", command=open_replace_window, width=20)
replace_btn.pack(side=tk.LEFT, padx=(0, 10))

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
                     text="Формат: дублирование текста и замена символов",
                     anchor="e")
help_label.pack(side=tk.RIGHT)

# Запуск приложения
root.mainloop()
