import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

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
    def __init__(self, color, vehicle_id, capacity):
        super().__init__(vehicle_id, capacity)
        self.color = color
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
        data = load_data()
        
        # Клиенты
        for client_data in data.get("clients", []):
            client = Client(
                client_data.get("Имя", ""),
                client_data.get("Вес груза", 0),
                client_data.get("Вип статус", False)
            )
            self.company.clients.append(client)
        
        # Транспорт
        for vehicle_data in data.get("vehicles", []):
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
                continue
            
            vehicle.current_load = vehicle_data.get("Нынешняя загруженность", 0)
            self.company.vehicles.append(vehicle)
    
    def create_widgets(self):
        # Верхняя панель
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        buttons = [
            ("➕ Клиент", self.add_client),
            ("🚚 Транспорт", self.add_vehicle),
            ("📦 Загрузить", self.load_cargo_to_vehicle),
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
        self.create_client_table(clients_frame)
        
        # Таблица транспорта
        vehicles_frame = ttk.Frame(notebook)
        notebook.add(vehicles_frame, text="Транспорт")
        self.create_vehicle_table(vehicles_frame)
        
        # Статусная строка
        self.status = tk.StringVar(value="Готово")
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def create_client_table(self, parent):
        columns = ("Имя", "Вес груза (кг)", "VIP")
        self.clients_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=150, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_vehicle_table(self, parent):
        columns = ("ID", "Тип", "Грузоподъемность", "Загружено", "Свободно")
        self.vehicles_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        col_widths = [100, 100, 120, 100, 100]
        for col, width in zip(columns, col_widths):
            self.vehicles_tree.heading(col, text=col)
            self.vehicles_tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.vehicles_tree.yview)
        self.vehicles_tree.configure(yscrollcommand=scrollbar.set)
        self.vehicles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_tables(self):
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
            free = vehicle.capacity - vehicle.current_load
            self.vehicles_tree.insert("", tk.END, values=(
                vehicle.vehicle_id, vehicle.type, vehicle.capacity,
                vehicle.current_load, free
            ))
    
    def add_client(self):
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
            if len(name) < 2 or not name.replace(" ", "").isalpha():
                messagebox.showerror("Ошибка", "Имя должно быть не менее 2 буквенных символов")
                return
            
            try:
                weight = int(weight)
                if not 1 <= weight <= 10000:
                    messagebox.showerror("Ошибка", "Вес должен быть от 1 до 10000 кг")
                    return
            except:
                messagebox.showerror("Ошибка", "Вес должен быть числом")
                return
            
            client = Client(name, weight, vip_var.get())
            self.company.clients.append(client)
            
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
    
    def load_cargo_to_vehicle(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Загрузка груза")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
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
            if client_names:
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
            if vehicle_ids:
                vehicle_combo.current(0)
        
        def perform_loading():
            if not client_combo or not vehicle_combo:
                messagebox.showerror("Ошибка", "Нет клиентов или транспорта")
                dialog.destroy()
                return
            
            client_name = client_var.get()
            vehicle_id = vehicle_var.get()
            
            # Находим клиента и транспорт
            client = next((c for c in self.company.clients if c.name == client_name), None)
            vehicle = next((v for v in self.company.vehicles if v.vehicle_id == vehicle_id), None)
            
            if not client or not vehicle:
                messagebox.showerror("Ошибка", "Не удалось найти клиента или транспорт")
                dialog.destroy()
                return
            
            if vehicle.current_load + client.cargo_weight <= vehicle.capacity:
                vehicle.current_load += client.cargo_weight
                vehicle.clients.append(client)
                
                try:
                    data = load_data()
                    for v_data in data.get("vehicles", []):
                        if v_data.get("Номер транспортного средства") == vehicle_id:
                            v_data["Нынешняя загруженность"] = vehicle.current_load
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
                    messagebox.showinfo("Успех", f"Груз {client.cargo_weight} кг успешно загружен!")
                    dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
            else:
                free_space = vehicle.capacity - vehicle.current_load
                messagebox.showwarning("Недостаточно места", 
                                     f"Не хватает места в транспорте!\n"
                                     f"Нужно: {client.cargo_weight} кг\n"
                                     f"Свободно: {free_space} кг")
        
        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        if self.company.clients and self.company.vehicles:
            ttk.Button(btn_frame, text="Загрузить", command=perform_loading).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_vehicle(self):
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
            
            if type_var.get() == "Грузовик":
                vehicle = Truck(details, vehicle_id, capacity)
            else:
                vehicle = Ship(details, vehicle_id, capacity)
            
            self.company.vehicles.append(vehicle)
            
            data = load_data()
            if "vehicles" not in data:
                data["vehicles"] = []
            
            vehicle_data = {
                "Номер транспортного средства": vehicle_id,
                "Возможная загруженность": capacity,
                "Нынешняя загруженность": 0,
                "Клиенты": [],
                "Тип": vehicle.type,
                "Название" if isinstance(vehicle, Ship) else "Цвет": details
            }
            
            data["vehicles"].append(vehicle_data)
            save_data(data)
            
            self.update_tables()
            self.status.set(f"Транспорт '{vehicle_id}' добавлен")
            dialog.destroy()
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
        id_entry.focus()
    
    def edit_client(self):
        selection = self.clients_tree.selection()
        if not selection:
            return
        
        name = self.clients_tree.item(selection[0])['values'][0]
        
        for client in self.company.clients:
            if client.name == name:
                if messagebox.askyesno("Редактирование", f"Удалить клиента '{name}' и создать нового?"):
                    self.company.clients.remove(client)
                    self.update_tables()
                    self.add_client()
                break
    
    def edit_vehicle(self):
        selection = self.vehicles_tree.selection()
        if not selection:
            return
        
        vehicle_id = self.vehicles_tree.item(selection[0])['values'][0]
        
        for vehicle in self.company.vehicles:
            if vehicle.vehicle_id == vehicle_id:
                if messagebox.askyesno("Редактирование", f"Удалить транспорт '{vehicle_id}' и создать новый?"):
                    self.company.vehicles.remove(vehicle)
                    self.update_tables()
                    self.add_vehicle()
                break
    
    def optimize(self):
        if not self.company.clients or not self.company.vehicles:
            messagebox.showwarning("Ошибка", "Нет клиентов или транспорта")
            return
        
        vip_clients = sorted([c for c in self.company.clients if c.is_vip], 
                            key=lambda x: x.cargo_weight, reverse=True)
        regular_clients = sorted([c for c in self.company.clients if not c.is_vip], 
                                key=lambda x: x.cargo_weight, reverse=True)
        
        all_clients = vip_clients + regular_clients
        
        for vehicle in self.company.vehicles:
            vehicle.current_load = 0
            vehicle.clients = []
        
        vehicles_sorted = sorted(self.company.vehicles, key=lambda v: v.capacity, reverse=True)
        
        for client in all_clients:
            for vehicle in vehicles_sorted:
                if vehicle.current_load + client.cargo_weight <= vehicle.capacity:
                    vehicle.current_load += client.cargo_weight
                    vehicle.clients.append(client)
                    break
        
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
        about_text = (
            "Транспортная Компания\n\n"
            "Лабораторная работа №12\n"
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