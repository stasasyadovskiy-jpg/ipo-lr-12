import json
def load_data():
    with open("data.json", "r", encoding='utf-8') as file:
        data = json.load(file)
        return data
def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class Client:
    def __init__(self, name, cargo_weight, is_vip=False):
        self.name = name
        self.cargo_weight = cargo_weight
        self.is_vip = is_vip

class Vehicle:
    def __init__(self, vehicle_id, capacity):
        self.vehicle_id =  vehicle_id
        self.capacity = capacity
        self.current_load = 0
        self.clients = []
        
    def load_cargo(self, client):
        if self.current_load + client.cargo_weight <= self.capacity:
            self.current_load += client.cargo_weight
            self.clients.append(client)
            print(f"Груз клиента {client.name} загружен в транспорт {self.vehicle_id}")
            return True
        else:
            print(f"Недостаточно места в транспорте {self.vehicle_id} для груза клиента {client.name}")
            return False
    
    def __str__(self):
        return (f"Транспорт ID: {self.vehicle_id}\n"
                f"Грузоподъёмность: {self.capacity}\n"
                f"Текущая загрузка: {self.current_load}\n"
                f"Клиентов: {len(self.clients)}")

class Ship(Vehicle):
    def __init__(self, name, vehicle_id, capacity): 
        super().__init__(vehicle_id, capacity)
        self.name = name
    
    def __str__(self):
        return super().__str__() + f"\nТип: Корабль\nНазвание: {self.name}"

class Truck(Vehicle):
    def __init__(self, color, vehicle_id, capacity, name=""):  
        super().__init__(vehicle_id, capacity)
        self.color = color
        self.name = name
    
    def __str__(self):
        return super().__str__() + f"\nТип: Грузовик\nЦвет: {self.color}"

class TransportCompany:
    def __init__(self, name):
        self.vehicles = []
        self.clients = []
        self.name = name

    def add_vehicle(self, vehicle): 
        self.vehicles.append(vehicle)
        try:
            data = load_data()
        except:
            data = {"vehicles": [], "clients": []}
        vehicle_data = {
            "Номер транспортного средства": vehicle.vehicle_id,
            "Возможная загруженность": vehicle.capacity,
            "Нынешняя загруженность": vehicle.current_load,
            "Клиенты": [{"name": client.name, "cargo_weight": client.cargo_weight, "is_vip": client.is_vip} 
                       for client in vehicle.clients]
        }
        if isinstance(vehicle, Ship):
            vehicle_data["Тип"] = "Корабль"
            vehicle_data["Название"] = vehicle.name
        elif isinstance(vehicle, Truck):
            vehicle_data["Тип"] = "Грузовик"
            vehicle_data["Цвет"] = vehicle.color
        else:
            vehicle_data["type"] = "Vehicle"
        if "vehicles" not in data:
            data["vehicles"] = []
        data["vehicles"].append(vehicle_data)
        save_data(data)
        print(f"Транспорт {vehicle.vehicle_id} успешно добавлен в компанию {self.name}")
        return True

    def list_vehicles(self, detailed=False):
        result = ""
        for i, vehicle in enumerate(self.vehicles, 1):
            if detailed:
                result += f"{i}. {vehicle}\n" + "-"*30 + "\n"
            else:
                result += f"{i}. ID: {vehicle.vehicle_id}, Тип: {type(vehicle).__name__}\n"
        return result if result else "Транспортных средств нет"

    def add_client(self, client): 
        self.clients.append(client)
        try:
            data = load_data()
        except:
            data = {"vehicles": [], "clients": []}
        if "clients" not in data:
            data["clients"] = []
        data["clients"].append({
            "Имя": client.name,
            "Вес груза": client.cargo_weight,
            "Вип статус": client.is_vip
        })
        save_data(data)
        print(f"Клиент {client.name} успешно добавлен")
    def assign_client_to_vehicle(self, client_name, vehicle_id):
        client = None
        for c in self.clients:
            if c.name == client_name:
                client = c
                break
        if not client:
            print(f"Клиент {client_name} не найден")
            return False
        vehicle = None
        for v in self.vehicles:
            if v.vehicle_id == vehicle_id:
                vehicle = v
                break     
        if not vehicle:
            print(f"Транспорт {vehicle_id} не найден")
            return False
        return vehicle.load_cargo(client)

    def optimize_cargo_distribution(self): 
        for vehicle in self.vehicles:
            vehicle.current_load = 0
            vehicle.clients = []
        
        vip_clients = [c for c in self.clients if c.is_vip]
        regular_clients = [c for c in self.clients if not c.is_vip]
        vip_clients_sorted = sorted(vip_clients, key=lambda c: c.cargo_weight, reverse=True)
        regular_clients_sorted = sorted(regular_clients, key=lambda c: c.cargo_weight, reverse=True)
        all_clients_sorted = vip_clients_sorted + regular_clients_sorted
        vehicles_sorted = sorted(self.vehicles, key=lambda v: v.capacity, reverse=True)

        for client in all_clients_sorted:
            client_assigned = False
            for vehicle in vehicles_sorted:
                if vehicle.current_load + client.cargo_weight <= vehicle.capacity:
                    vehicle.current_load += client.cargo_weight
                    vehicle.clients.append(client)
                    client_assigned = True
                    break
            if not client_assigned:
                print(f"Груз клиента {client.name} ({client.cargo_weight} кг) не помещается ни в один транспорт")
        print("\nРезультат распределения грузов:")
        print("=" * 50)
        used_vehicles = 0
        total_cargo = 0
        for vehicle in vehicles_sorted:
            if vehicle.current_load > 0:
                used_vehicles += 1
                total_cargo += vehicle.current_load
                print(f"\nТранспорт {vehicle.vehicle_id}:")
                print(f"  Загружено: {vehicle.current_load}/{vehicle.capacity} кг")
                print(f"  Клиентов: {len(vehicle.clients)}")
                for i, client in enumerate(vehicle.clients, 1):
                    vip_mark = " [VIP]" if client.is_vip else ""
                    print(f"  {i}. {client.name}{vip_mark} - {client.cargo_weight} кг")
        print("\n" + "=" * 50)
        print(f"Использовано транспорта: {used_vehicles} из {len(self.vehicles)}")
        print(f"Перевезено груза: {total_cargo} кг")
        print(f"Обработано клиентов: {sum(len(v.clients) for v in self.vehicles)} из {len(self.clients)}")
        return used_vehicles

def main():
    company = TransportCompany("Транспортная Компания")
    try:
        data = load_data()
    except:
        print("Файл данных не найден, создаем новый")
    while True:
        print("\n===TRANSPORT COMPANY===")
        print("1 - Добавить клиента")
        print("2 - Добавить транспорт")
        print("3 - Вывести список всего транспорта")
        print("4 - Загрузить груз клиента")
        print("5 - Распределить грузы")
        print("6 - Выйти из программы")
        try:
            action = int(input("Выберите действие (1-6): "))
        except ValueError:
            print("Ошибка! Введите число от 1 до 6")
            continue
        if action == 1:
            name = input("Введите имя клиента: ")
            cargo_weight = int(input("Введите вес груза (кг): "))
            is_vip_input = input("VIP клиент? (да/нет): ").lower()
            is_vip = is_vip_input in ['да', 'yes', 'y', '+']
            
            client = Client(name, cargo_weight, is_vip)
            company.add_client(client)
        elif action == 2:
            vehicle_type = input("Выберите тип транспорта (1 - Грузовик, 2 - Корабль): ")
            vehicle_id = input("Введите ID транспорта: ")
            capacity = int(input("Введите грузоподъемность (кг): "))
            if vehicle_type == "1":
                color = input("Введите цвет грузовика: ")
                name = input("Введите название грузовика (необязательно): ")
                vehicle = Truck(color, vehicle_id, capacity, name)
            elif vehicle_type == "2":
                name = input("Введите название корабля: ")
                vehicle = Ship(name, vehicle_id, capacity)
            else:
                print("Неизвестный тип транспорта, создан базовый транспорт")
                vehicle = Vehicle(vehicle_id, capacity)
            company.add_vehicle(vehicle)
        elif action == 3:
            print("\nСписок транспорта:")
            print(company.list_vehicles(detailed=True))
        elif action == 4:
            client_name = input("Введите имя клиента: ")
            vehicle_id = input("Введите ID транспорта: ")
            company.assign_client_to_vehicle(client_name, vehicle_id)
        elif action == 5:
            if not company.clients:
                print("Нет клиентов для распределения")
            elif not company.vehicles:
                print("Нет транспорта для распределения")
            else:
                company.optimize_cargo_distribution()
        elif action == 6:
            print("До встречи!")
            break
        else: 
            print("Пожалуйста, введите число от 1 до 6")

if __name__ == "__main__":
    main()