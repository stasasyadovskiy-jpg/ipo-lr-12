import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime

# Импорт классов из оригинального кода
import sys
import os
sys.path.append('.')

# Определяем минимальную версию классов на случай отсутствия main.py
class Client:
    def __init__(self, name, cargo_weight, is_vip=False):
        self.name = name
        self.cargo_weight = cargo_weight
        self.is_vip = is_vip

class Vehicle:
    def __init__(self, vehicle_id, capacity):
        self.vehicle_id = vehicle_id
        self.capacity = capacity
        self.current_load = 0
        self.clients = []

class Ship(Vehicle):
    def __init__(self, name, vehicle_id, capacity):
        super().__init__(vehicle_id, capacity)
        self.name = name
        self.type = "Корабль"

class Truck(Vehicle):
    def __init__(self, color, vehicle_id, capacity, name=""):
        super().__init__(vehicle_id, capacity)
        self.color = color
        self.name = name
        self.type = "Грузовик"

class TransportCompany:
    def __init__(self, name):
        self.vehicles = []
        self.clients = []
        self.name = name

def load_data():
    try:
        with open("data.json", "r", encoding='utf-8') as file:
            return json.load(file)
    except:
        return {"vehicles": [], "clients": []}

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class TransportCompanyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Транспортная Компания")
        self.root.geometry("1000x600")
        
        self.company = TransportCompany("Транспортная Компания")
        self.load_data()
        self.create_widgets()
        self.update_tables()
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            data = load_data()
            
            # Клиенты
            if "clients" in data:
                for client_data in data["clients"]:
                    client = Client(
                        client_data.get("Имя", ""),
                        client_data.get("Вес груза", 0),
                        client_data.get("Вип статус", False)
                    )
                    self.company.clients.append(client)
            
            # Транспорт
            if "vehicles" in data:
                for vehicle_data in data["vehicles"]:
                    vehicle_type = vehicle_data.get("Тип", "")
                    vehicle_id = vehicle_data.get("Номер транспортного средства", "")
                    capacity = vehicle_data.get("Возможная загруженность", 0)
                    
                    if vehicle_type == "Корабль":
                        name = vehicle_data.get("Название", "")
                        vehicle = Ship(name, vehicle_id, capacity)
                    elif vehicle_type == "Грузовик":
                        color = vehicle_data.get("Цвет", "черный")
                        vehicle = Truck(color, vehicle_id, capacity)
                    else:
                        vehicle = Vehicle(vehicle_id, capacity)
                    
                    vehicle.current_load = vehicle_data.get("Нынешняя загруженность", 0)
                    self.company.vehicles.append(vehicle)
        except:
            pass
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Верхняя панель с кнопками
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
                # В toolbar после существующих кнопок добавьте:
        buttons = [
            ("➕ Клиент", self.add_client),
            ("🚚 Транспорт", self.add_vehicle),
            ("📦 Загрузить", self.load_cargo_to_vehicle),  # НОВАЯ КНОПКА
            ("📊 Распределить", self.optimize),
            ("📁 Экспорт", self.export_data),
            ("❓ О программе", self.show_about),
        ]
        
        for text, command in buttons:
            btn = ttk.Button(toolbar, text=text, command=command, width=12)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Панель с таблицами
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица клиентов
        clients_frame = ttk.Frame(notebook)
        notebook.add(clients_frame, text="Клиенты")
        self.create_table(clients_frame, "clients")
        
        # Таблица транспорта
        vehicles_frame = ttk.Frame(notebook)
        notebook.add(vehicles_frame, text="Транспорт")
        self.create_table(vehicles_frame, "vehicles")
        
        # Статусная строка
        self.status = tk.StringVar(value="Готово")
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def create_table(self, parent, table_type):
        """Создание таблицы"""
        if table_type == "clients":
            columns = ("Имя", "Вес груза (кг)", "VIP")
            tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor=tk.CENTER)
            
            tree.bind("<Double-1>", lambda e: self.edit_client())
            self.clients_tree = tree
            
        else:  # vehicles
            columns = ("ID", "Тип", "Грузоподъемность", "Загружено", "Свободно")
            tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
            
            col_widths = [100, 100, 120, 100, 100]
            for col, width in zip(columns, col_widths):
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor=tk.CENTER)
            
            tree.bind("<Double-1>", lambda e: self.edit_vehicle())
            self.vehicles_tree = tree
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_tables(self):
        """Обновление таблиц"""
        # Клиенты
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        for client in self.company.clients:
            vip = "Да" if client.is_vip else "Нет"
            self.clients_tree.insert("", tk.END, values=(client.name, client.cargo_weight, vip))
        
        # Транспорт
        for item in self.vehicles_tree.get_children():
            self.vehicles_tree.delete(item)
        
        for vehicle in self.company.vehicles:
            vehicle_type = getattr(vehicle, 'type', 'Транспорт')
            free = vehicle.capacity - vehicle.current_load
            self.vehicles_tree.insert("", tk.END, values=(
                vehicle.vehicle_id, vehicle_type, vehicle.capacity,
                vehicle.current_load, free
            ))
    
    def add_client(self):
        """Добавление клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить клиента")
        dialog.geometry("300x250")
        
        ttk.Label(dialog, text="Имя клиента:*").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Вес груза (кг):*").pack(pady=5)
        weight_entry = ttk.Entry(dialog, width=30)
        weight_entry.pack(pady=5)
        
        vip_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="VIP клиент", variable=vip_var).pack(pady=10)
        
        def save():
            name = name_entry.get().strip()
            weight = weight_entry.get().strip()
            
            # Валидация
            if len(name) < 2:
                messagebox.showerror("Ошибка", "Имя должно быть не менее 2 символов")
                return
            
            if not name.isalpha():
                messagebox.showerror("Ошибка", "Имя должно содержать только буквы")
                return
            
            try:
                weight = int(weight)
                if not 1 <= weight <= 10000:
                    messagebox.showerror("Ошибка", "Вес должен быть от 1 до 10000 кг")
                    return
            except:
                messagebox.showerror("Ошибка", "Вес должен быть числом")
                return
            
            # Сохранение
            client = Client(name, weight, vip_var.get())
            self.company.clients.append(client)
            
            # Сохранение в файл
            data = load_data()
            if "clients" not in data:
                data["clients"] = []
            
            data["clients"].append({
                "Имя": name,
                "Вес груза": weight,
                "Вип статус": vip_var.get()
            })
            
            save_data(data)
            self.update_tables()
            self.status.set(f"Клиент '{name}' добавлен")
            dialog.destroy()
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
        name_entry.focus()
        
        def perform_loading():
            if not client_combo or not vehicle_combo:
                messagebox.showerror("Ошибка", "Нет клиентов или транспорта")
                dialog.destroy()
                return
            
            client_name = client_var.get()
            vehicle_id = vehicle_var.get()
            
            # Находим клиента
            client = None
            for c in self.company.clients:
                if c.name == client_name:
                    client = c
                    break
            
            # Находим транспорт
            vehicle = None
            for v in self.company.vehicles:
                if v.vehicle_id == vehicle_id:
                    vehicle = v
                    break
            
            if not client or not vehicle:
                messagebox.showerror("Ошибка", "Не удалось найти клиента или транспорт")
                dialog.destroy()
                return
            
            # Проверяем, поместится ли груз
            if vehicle.current_load + client.cargo_weight <= vehicle.capacity:
                # Загружаем груз
                vehicle.current_load += client.cargo_weight
                vehicle.clients.append(client)
                
                # Обновляем файл данных
                try:
                    data = load_data()
                    
                    # Находим транспорт в данных
                    for v_data in data.get("vehicles", []):
                        if v_data.get("Номер транспортного средства") == vehicle_id:
                            # Обновляем загрузку
                            v_data["Нынешняя загруженность"] = vehicle.current_load
                            
                            # Добавляем клиента
                            if "Клиенты" not in v_data:
                                v_data["Клиенты"] = []
                            
                            v_data["Клиенты"].append({
                                "name": client.name,
                                "cargo_weight": client.cargo_weight,
                                "is_vip": client.is_vip
                            })
                            break
                    
                    save_data(data)
                    
                    self.update_tables()
                    self.status.set(f"Груз клиента '{client_name}' загружен в '{vehicle_id}'")
                    messagebox.showinfo("Успех", 
                                      f"Груз {client.cargo_weight} кг успешно загружен!\n"
                                      f"Осталось места: {vehicle.capacity - vehicle.current_load} кг")
                    dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
            else:
                free_space = vehicle.capacity - vehicle.current_load
                messagebox.showwarning("Недостаточно места", 
                                     f"Не хватает места в транспорте!\n"
                                     f"Нужно: {client.cargo_weight} кг\n"
                                     f"Свободно: {free_space} кг\n"
                                     f"Выберите другой транспорт или распределите грузы")
        
        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        if client_combo and vehicle_combo:
            ttk.Button(btn_frame, text="Загрузить", command=perform_loading).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        
        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        if client_combo and vehicle_combo:
            ttk.Button(btn_frame, text="Загрузить", command=perform_loading).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    def load_cargo_to_vehicle(self):
            dialog = tk.Toplevel(self.root)
            dialog.title("Загрузка груза")
            dialog.geometry("400x300")
            
            # Выбор клиента
            ttk.Label(dialog, text="Выберите клиента:").pack(pady=10)
            
            client_var = tk.StringVar()
            if not self.company.clients:
                ttk.Label(dialog, text="Нет доступных клиентов", foreground="red").pack()
                client_combo = None
            else:
                client_names = [c.name for c in self.company.clients]
                client_combo = ttk.Combobox(dialog, textvariable=client_var, 
                                        values=client_names, state="readonly")
                client_combo.pack(pady=5)
                client_combo.current(0)
            
            # Выбор транспорта
            ttk.Label(dialog, text="Выберите транспорт:").pack(pady=10)
            
            vehicle_var = tk.StringVar()
            if not self.company.vehicles:
                ttk.Label(dialog, text="Нет доступного транспорта", foreground="red").pack()
                vehicle_combo = None
            else:
                vehicle_ids = [v.vehicle_id for v in self.company.vehicles]
                vehicle_combo = ttk.Combobox(dialog, textvariable=vehicle_var,
                                            values=vehicle_ids, state="readonly")
                vehicle_combo.pack(pady=5)
                vehicle_combo.current(0)
        
        def perform_loading():
            if not client_combo or not vehicle_combo:
                messagebox.showerror("Ошибка", "Нет клиентов или транспорта")
                dialog.destroy()
                return
            
            client_name = client_var.get()
            vehicle_id = vehicle_var.get()
            
            # Находим клиента
            client = None
            for c in self.company.clients:
                if c.name == client_name:
                    client = c
                    break
            
            # Находим транспорт
            vehicle = None
            for v in self.company.vehicles:
                if v.vehicle_id == vehicle_id:
                    vehicle = v
                    break
            
            if not client or not vehicle:
                messagebox.showerror("Ошибка", "Не удалось найти клиента или транспорт")
                dialog.destroy()
                return
            
            # Проверяем, поместится ли груз
            if vehicle.current_load + client.cargo_weight <= vehicle.capacity:
                # Загружаем груз
                vehicle.current_load += client.cargo_weight
                vehicle.clients.append(client)
                
                # Обновляем файл данных
                try:
                    data = load_data()
                    
                    # Находим транспорт в данных
                    for v_data in data.get("vehicles", []):
                        if v_data.get("Номер транспортного средства") == vehicle_id:
                            # Обновляем загрузку
                            v_data["Нынешняя загруженность"] = vehicle.current_load
                            
                            # Добавляем клиента
                            if "Клиенты" not in v_data:
                                v_data["Клиенты"] = []
                            
                            v_data["Клиенты"].append({
                                "name": client.name,
                                "cargo_weight": client.cargo_weight,
                                "is_vip": client.is_vip
                            })
                            break
                    
                    save_data(data)
                    
                    self.update_tables()
                    self.status.set(f"Груз клиента '{client_name}' загружен в '{vehicle_id}'")
                    messagebox.showinfo("Успех", 
                                      f"Груз {client.cargo_weight} кг успешно загружен!\n"
                                      f"Осталось места: {vehicle.capacity - vehicle.current_load} кг")
                    dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
            else:
                free_space = vehicle.capacity - vehicle.current_load
                messagebox.showwarning("Недостаточно места", 
                                     f"Не хватает места в транспорте!\n"
                                     f"Нужно: {client.cargo_weight} кг\n"
                                     f"Свободно: {free_space} кг\n"
                                     f"Выберите другой транспорт или распределите грузы")
    def add_vehicle(self):
        """Добавление транспорта"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить транспорт")
        dialog.geometry("300x300")
        
        ttk.Label(dialog, text="Тип транспорта:").pack(pady=5)
        type_var = tk.StringVar(value="Грузовик")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, 
                                 values=["Грузовик", "Корабль"], state="readonly")
        type_combo.pack(pady=5)
        
        ttk.Label(dialog, text="ID транспорта:*").pack(pady=5)
        id_entry = ttk.Entry(dialog, width=30)
        id_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Грузоподъемность (кг):*").pack(pady=5)
        capacity_entry = ttk.Entry(dialog, width=30)
        capacity_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Цвет/Название:*").pack(pady=5)
        details_entry = ttk.Entry(dialog, width=30)
        details_entry.pack(pady=5)
        
        def save():
            vehicle_id = id_entry.get().strip()
            capacity = capacity_entry.get().strip()
            details = details_entry.get().strip()
            
            if not vehicle_id:
                messagebox.showerror("Ошибка", "Введите ID транспорта")
                return
            
            try:
                capacity = int(capacity)
                if capacity <= 0:
                    messagebox.showerror("Ошибка", "Грузоподъемность должна быть > 0")
                    return
            except:
                messagebox.showerror("Ошибка", "Грузоподъемность должна быть числом")
                return
            
            if not details:
                messagebox.showerror("Ошибка", "Введите цвет или название")
                return
            
            # Создание транспорта
            if type_var.get() == "Грузовик":
                vehicle = Truck(details, vehicle_id, capacity)
            else:
                vehicle = Ship(details, vehicle_id, capacity)
            
            self.company.vehicles.append(vehicle)
            
            # Сохранение в файл
            data = load_data()
            if "vehicles" not in data:
                data["vehicles"] = []
            
            vehicle_data = {
                "Номер транспортного средства": vehicle_id,
                "Возможная загруженность": capacity,
                "Нынешняя загруженность": 0,
                "Клиенты": []
            }
            
            if isinstance(vehicle, Ship):
                vehicle_data["Тип"] = "Корабль"
                vehicle_data["Название"] = details
            else:
                vehicle_data["Тип"] = "Грузовик"
                vehicle_data["Цвет"] = details
            
            data["vehicles"].append(vehicle_data)
            save_data(data)
            
            self.update_tables()
            self.status.set(f"Транспорт '{vehicle_id}' добавлен")
            dialog.destroy()
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
        id_entry.focus()
    
    def edit_client(self):
        """Редактирование клиента"""
        selection = self.clients_tree.selection()
        if not selection:
            return
        
        item = self.clients_tree.item(selection[0])
        name = item['values'][0]
        
        # Находим клиента
        for client in self.company.clients:
            if client.name == name:
                # Простое удаление и повторное добавление
                if messagebox.askyesno("Редактирование", f"Удалить клиента '{name}' и создать нового?"):
                    self.company.clients.remove(client)
                    self.update_tables()
                    self.add_client()
                break
    
    def edit_vehicle(self):
        """Редактирование транспорта"""
        selection = self.vehicles_tree.selection()
        if not selection:
            return
        
        item = self.vehicles_tree.item(selection[0])
        vehicle_id = item['values'][0]
        
        # Находим транспорт
        for vehicle in self.company.vehicles:
            if vehicle.vehicle_id == vehicle_id:
                if messagebox.askyesno("Редактирование", f"Удалить транспорт '{vehicle_id}' и создать новый?"):
                    self.company.vehicles.remove(vehicle)
                    self.update_tables()
                    self.add_vehicle()
                break
    
    def optimize(self):
        """Оптимизация распределения грузов"""
        if not self.company.clients:
            messagebox.showwarning("Ошибка", "Нет клиентов")
            return
        
        if not self.company.vehicles:
            messagebox.showwarning("Ошибка", "Нет транспорта")
            return
        
        # Простая оптимизация: сортируем по весу и распределяем
        vip_clients = sorted([c for c in self.company.clients if c.is_vip], 
                            key=lambda x: x.cargo_weight, reverse=True)
        regular_clients = sorted([c for c in self.company.clients if not c.is_vip], 
                                key=lambda x: x.cargo_weight, reverse=True)
        
        all_clients = vip_clients + regular_clients
        
        # Сбрасываем загрузку
        for vehicle in self.company.vehicles:
            vehicle.current_load = 0
            vehicle.clients = []
        
        # Распределение
        vehicles_sorted = sorted(self.company.vehicles, key=lambda v: v.capacity, reverse=True)
        
        for client in all_clients:
            assigned = False
            for vehicle in vehicles_sorted:
                if vehicle.current_load + client.cargo_weight <= vehicle.capacity:
                    vehicle.current_load += client.cargo_weight
                    vehicle.clients.append(client)
                    assigned = True
                    break
            
            if not assigned:
                self.status.set(f"Груз клиента {client.name} не поместился")
        
        # Показываем результаты
        result = "Результаты распределения:\n"
        used_vehicles = 0
        total_cargo = 0
        
        for vehicle in vehicles_sorted:
            if vehicle.current_load > 0:
                used_vehicles += 1
                total_cargo += vehicle.current_load
                result += f"\n{vehicle.vehicle_id}: {vehicle.current_load}/{vehicle.capacity} кг\n"
        
        result += f"\nИспользовано: {used_vehicles} из {len(self.company.vehicles)}"
        result += f"\nПеревезено: {total_cargo} кг"
        
        messagebox.showinfo("Результаты", result)
        self.update_tables()
        self.status.set("Распределение завершено")
    
    def export_data(self):
        """Экспорт данных"""
        if not self.company.clients and not self.company.vehicles:
            messagebox.showwarning("Ошибка", "Нет данных для экспорта")
            return
        
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Экспорт данных транспортной компании\n")
                f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                
                f.write("Клиенты:\n")
                f.write("-"*30 + "\n")
                for client in self.company.clients:
                    vip = "VIP" if client.is_vip else ""
                    f.write(f"{client.name}: {client.cargo_weight} кг {vip}\n")
                
                f.write("\nТранспорт:\n")
                f.write("-"*30 + "\n")
                for vehicle in self.company.vehicles:
                    free = vehicle.capacity - vehicle.current_load
                    f.write(f"{vehicle.vehicle_id}: {vehicle.current_load}/{vehicle.capacity} кг (свободно: {free} кг)\n")
            
            self.status.set(f"Данные экспортированы в {filename}")
            messagebox.showinfo("Успех", f"Данные сохранены в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def show_about(self):
        """Окно 'О программе'"""
        about_text = (
            "Транспортная Компания\n\n"
            "Лабораторная работа №12\n"
            "Разработчик: [Ваше ФИО]\n\n"
            "Программа для управления транспортной\n"
            "компанией и оптимизации грузоперевозок."
        )
        messagebox.showinfo("О программе", about_text)


def main():
    root = tk.Tk()
    app = TransportCompanyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()