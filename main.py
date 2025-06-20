import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import configparser
from dataclasses import dataclass

# Clases DTO (Data Transfer Objects)
@dataclass
class RefugiadoDTO:
    id_refugiado: int = None
    nombre: str = None
    identificacion: str = None
    numero_de_contacto: str = None
    email: str = None
    id_ciudad_despiazamiento: int = None
    motivo_despiazamiento: str = None
    id_ciudad_refugio: int = None

@dataclass
class VoluntarioDTO:
    id_voluntario: int = None
    nombre: str = None
    identificacion: str = None
    id_ciudad: int = None
    id_albergue: int = None
    profesion: str = None

class RefugeeManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Refugiados - Integrado con MySQL Workbench")
        self.root.geometry("1200x800")
        
        # Cargar configuración de la base de datos
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        # Conectar a la base de datos
        self.db_connection = self.connect_to_database()
        if not self.db_connection:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos. Verifica config.ini")
            self.root.destroy()
            return
        
        # Crear pestañas
        self.create_tabs()
        
        # Cargar datos iniciales
        self.load_initial_data()
    
    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host=self.config['mysql']['host'],
                user=self.config['mysql']['user'],
                password=self.config['mysql']['password'],
                database=self.config['mysql']['database'],
                port=self.config['mysql']['port']
            )
            return connection
        except Error as e:
            messagebox.showerror("Error de conexión", f"Error al conectar a MySQL Workbench: {e}")
            return None
    
    def create_tabs(self):
        self.tab_control = ttk.Notebook(self.root)
        
        # Pestañas
        self.tab_refugees = ttk.Frame(self.tab_control)
        self.tab_shelters = ttk.Frame(self.tab_control)
        self.tab_cities = ttk.Frame(self.tab_control)
        self.tab_volunteers = ttk.Frame(self.tab_control)
        self.tab_reports = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_refugees, text='Refugiados')
        self.tab_control.add(self.tab_shelters, text='Albergues')
        self.tab_control.add(self.tab_cities, text='Ciudades')
        self.tab_control.add(self.tab_volunteers, text='Voluntarios')
        self.tab_control.add(self.tab_reports, text='Reportes')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Configurar cada pestaña
        self.setup_refugees_tab()
        self.setup_shelters_tab()
        self.setup_cities_tab()
        self.setup_volunteers_tab()
        self.setup_reports_tab()
    
    def setup_refugees_tab(self):
        # Frame para formulario
        form_frame = ttk.LabelFrame(self.tab_refugees, text="Formulario de Refugiado")
        form_frame.pack(pady=10, padx=10, fill="x")
        
        # Campos del formulario
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.refugee_name = ttk.Entry(form_frame)
        self.refugee_name.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Identificación:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.refugee_id = ttk.Entry(form_frame)
        self.refugee_id.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Número de contacto:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.refugee_contact = ttk.Entry(form_frame)
        self.refugee_contact.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.refugee_email = ttk.Entry(form_frame)
        self.refugee_email.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Ciudad de desplazamiento:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.displacement_city = ttk.Combobox(form_frame, state="readonly")
        self.displacement_city.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Motivo de desplazamiento:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.displacement_reason = ttk.Combobox(form_frame, state="readonly", values=[
            "Conflicto armado", "Desastres naturales", "Violencia social", 
            "Persecución política", "Desplazamiento forzado por bandas"
        ])
        self.displacement_reason.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Ciudad de refugio:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.refuge_city = ttk.Combobox(form_frame, state="readonly")
        self.refuge_city.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        # Botones CRUD
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Agregar", command=self.add_refugee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.update_refugee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_refugee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_refugee_form).pack(side="left", padx=5)
        
        # Tabla de refugiados
        table_frame = ttk.LabelFrame(self.tab_refugees, text="Lista de Refugiados")
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        columns = ("ID", "Nombre", "Identificación", "Contacto", "Email", 
                 "Ciudad Origen", "Motivo", "Ciudad Refugio", "Albergue")
        
        self.refugees_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.refugees_table.heading(col, text=col)
            self.refugees_table.column(col, width=120, anchor="center")
        
        self.refugees_table.column("Nombre", width=150)
        self.refugees_table.column("Motivo", width=180)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.refugees_table.yview)
        self.refugees_table.configure(yscrollcommand=scrollbar.set)
        
        self.refugees_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar evento de selección
        self.refugees_table.bind("<<TreeviewSelect>>", self.on_refugee_select)

    def setup_shelters_tab(self):
        # Implementación similar a setup_refugees_tab pero para albergues
        form_frame = ttk.LabelFrame(self.tab_shelters, text="Formulario de Albergue")
        form_frame.pack(pady=10, padx=10, fill="x")
        
        # Campos del formulario
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.shelter_name = ttk.Entry(form_frame)
        self.shelter_name.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Ciudad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.shelter_city = ttk.Combobox(form_frame)
        self.shelter_city.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Dirección:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.shelter_address = ttk.Entry(form_frame)
        self.shelter_address.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Capacidad:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.shelter_capacity = ttk.Entry(form_frame)
        self.shelter_capacity.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Ciudad de procedencia:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.shelter_origin_city = ttk.Entry(form_frame)
        self.shelter_origin_city.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        # Botones CRUD
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Agregar", command=self.add_shelter).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.update_shelter).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_shelter).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_shelter_form).pack(side="left", padx=5)
        
        # Tabla de albergues
        table_frame = ttk.LabelFrame(self.tab_shelters, text="Lista de Albergues")
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        columns = ("ID", "Nombre", "Ciudad", "Dirección", "Capacidad", "Procedencia")
        
        self.shelters_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.shelters_table.heading(col, text=col)
            self.shelters_table.column(col, width=120, anchor="center")
        
        self.shelters_table.column("Nombre", width=150)
        self.shelters_table.column("Dirección", width=200)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.shelters_table.yview)
        self.shelters_table.configure(yscrollcommand=scrollbar.set)
        
        self.shelters_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar evento de selección
        self.shelters_table.bind("<<TreeviewSelect>>", self.on_shelter_select)

    # Mueve estos métodos FUERA de setup_shelters_tab, al mismo nivel que setup_shelters_tab
    def add_shelter(self):
        try:
            # Obtener valores del formulario
            name = self.shelter_name.get()
            city = self.shelter_city.get()
            address = self.shelter_address.get()
            capacity = self.shelter_capacity.get()
            origin_city = self.shelter_origin_city.get()
            
            # Validar campos
            if not all([name, city, address, capacity, origin_city]):
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
                return
            
            # Obtener ID de la ciudad seleccionada
            city_id = int(city.split(" - ")[0])
            
            # Insertar en la base de datos
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO albergues (nombre, id_ciudad, direccion_del_albergue, 
                                       personas_albergadas, ciudad_de_procedencia)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, city_id, address, capacity, origin_city))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Albergue agregado correctamente")
            self.load_shelters()
            self.clear_shelter_form()
        except Error as e:
            messagebox.showerror("Error", f"Error al agregar albergue: {e}")

    def update_shelter(self):
        selected_item = self.shelters_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un albergue para actualizar")
            return
        
        try:
            shelter_id = self.shelters_table.item(selected_item)['values'][0]
            
            # Obtener valores del formulario
            name = self.shelter_name.get()
            city = self.shelter_city.get()
            address = self.shelter_address.get()
            capacity = self.shelter_capacity.get()
            origin_city = self.shelter_origin_city.get()
            
            # Validar campos
            if not all([name, city, address, capacity, origin_city]):
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
                return
            
            # Obtener ID de la ciudad seleccionada
            city_id = int(city.split(" - ")[0])
            
            # Actualizar en la base de datos
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE albergues 
                SET nombre = %s, id_ciudad = %s, direccion_del_albergue = %s, 
                    personas_albergadas = %s, ciudad_de_procedencia = %s
                WHERE id_albergue = %s
            """, (name, city_id, address, capacity, origin_city, shelter_id))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Albergue actualizado correctamente")
            self.load_shelters()
        except Error as e:
            messagebox.showerror("Error", f"Error al actualizar albergue: {e}")   

    def delete_shelter(self):
        selected_item = self.shelters_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un albergue para eliminar")
            return
        confirmation = messagebox.askyesno("Confirmación", "¿Está seguro de eliminar este albergue?")
        if not confirmation:
            return
        try:
            shelter_id = self.shelters_table.item(selected_item)['values'][0]
            
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM albergues WHERE id_albergue = %s", (shelter_id,))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Albergue eliminado correctamente")
            self.load_shelters()
            self.clear_shelter_form() 
        except Error as e:
            messagebox.showerror("Error", f"Error al eliminar albergue: {e}")

    def clear_shelter_form(self):
        self.shelter_name.delete(0, tk.END)
        self.shelter_city.set('')
        self.shelter_address.delete(0, tk.END)
        self.shelter_capacity.delete(0, tk.END)
        self.shelter_origin_city.delete(0, tk.END)

    def on_shelter_select(self, event):
        selected_item = self.shelters_table.focus()
        if selected_item:
            shelter_data = self.shelters_table.item(selected_item)['values']
            self.shelter_name.delete(0, tk.END)
            self.shelter_name.insert(0, shelter_data[1])
            # Buscar ciudad en el combobox
            if shelter_data[2]:
                for i, city in enumerate(self.shelter_city['values']):
                    if shelter_data[2] in city:
                        self.shelter_city.current(i)
                        break
            self.shelter_address.delete(0, tk.END)
            self.shelter_address.insert(0, shelter_data[3])
            self.shelter_capacity.delete(0, tk.END)
            self.shelter_capacity.insert(0, shelter_data[4])
            self.shelter_origin_city.delete(0, tk.END)
            self.shelter_origin_city.insert(0, shelter_data[5])

   
    def setup_cities_tab(self):
        # Implementación similar para ciudades
        # Frame para formulario
        form_frame = ttk.LabelFrame(self.tab_cities, text="Formulario de Ciudad")
        form_frame.pack(pady=10, padx=10, fill="x")
        
        # Campos del formulario
        ttk.Label(form_frame, text="Departamento:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.city_department = ttk.Entry(form_frame)
        self.city_department.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Ciudad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.city_name = ttk.Entry(form_frame)
        self.city_name.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Localidad:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.city_locality = ttk.Entry(form_frame)
        self.city_locality.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Habitantes:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.city_population = ttk.Entry(form_frame)
        self.city_population.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Botones CRUD
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Agregar", command=self.add_city).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.update_city).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_city).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_city_form).pack(side="left", padx=5)
        
        # Tabla de ciudades
        table_frame = ttk.LabelFrame(self.tab_cities, text="Lista de Ciudades")
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        columns = ("ID", "Departamento", "Ciudad", "Localidad", "Habitantes")
        
        self.cities_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.cities_table.heading(col, text=col)
            self.cities_table.column(col, width=120, anchor="center")
        
        self.cities_table.column("Departamento", width=150)
        self.cities_table.column("Ciudad", width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.cities_table.yview)
        self.cities_table.configure(yscrollcommand=scrollbar.set)
        
        self.cities_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar evento de selección
        self.cities_table.bind("<<TreeviewSelect>>", self.on_city_select)
    def add_city(self):
            try:
                # Obtener valores del formulario
                department = self.city_department.get()
                city = self.city_name.get()
                locality = self.city_locality.get()
                population = self.city_population.get()
                
                # Validar campos
                if not all([department, city, locality, population]):
                    messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
                    return
                
                # Crear DTO
                city_dto = {
                    'departamento': department,
                    'ciudad': city,
                    'localidad': locality,
                    'cantidad_de_habitantes': int(population)
                }
                
                # Insertar en la base de datos
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    INSERT INTO ciudades (departamento, ciudad, localidad, cantidad_de_habitantes)
                    VALUES (%s, %s, %s, %s)
                """, (city_dto['departamento'], city_dto['ciudad'], city_dto['localidad'], city_dto['cantidad_de_habitantes']))
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Éxito", "Ciudad agregada correctamente")
                self.load_cities_table()
                self.clear_city_form()
            except Error as e:
                messagebox.showerror("Error", f"Error al agregar ciudad: {e}")

    def update_city(self): 
        selected_item = self.cities_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una ciudad para actualizar")
            return
        try:
            city_id = self.cities_table.item(selected_item)['values'][0]
            
            # Obtener valores del formulario
            department = self.city_department.get()
            city = self.city_name.get()
            locality = self.city_locality.get()
            population = self.city_population.get()
            
            # Validar campos
            if not all([department, city, locality, population]):
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
                return
            
            # Crear DTO
            city_dto = {
                'id_ciudad': city_id,
                'departamento': department,
                'ciudad': city,
                'localidad': locality,
                'cantidad_de_habitantes': int(population)
            }
            
            # Actualizar en la base de datos
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE ciudades 
                SET departamento = %s, ciudad = %s, localidad = %s, cantidad_de_habitantes = %s
                WHERE id_ciudad = %s
            """, (city_dto['departamento'], city_dto['ciudad'], city_dto['localidad'], 
                  city_dto['cantidad_de_habitantes'], city_dto['id_ciudad']))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Ciudad actualizada correctamente")
            self.load_cities_table()
        except Error as e:
            messagebox.showerror("Error", f"Error al actualizar ciudad: {e}")
    def delete_city(self):
        selected_item = self.cities_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una ciudad para eliminar")
            return
        
        confirmation = messagebox.askyesno("Confirmación", "¿Está seguro de eliminar esta ciudad?")
        if not confirmation:
            return
        
        try:
            city_id = self.cities_table.item(selected_item)['values'][0]
            
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM ciudades WHERE id_ciudad = %s", (city_id,))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Ciudad eliminada correctamente")
            self.load_cities_table()
            self.clear_city_form()
        except Error as e:
            messagebox.showerror("Error", f"Error al eliminar ciudad: {e}")
    def clear_city_form(self):
            self.city_department.delete(0, tk.END)
            self.city_name.delete(0, tk.END)
            self.city_locality.delete(0, tk.END)
            self.city_population.delete(0, tk.END)


    def setup_volunteers_tab(self):
        # Implementación similar para voluntarios
         # Frame para formulario
        form_frame = ttk.LabelFrame(self.tab_volunteers, text="Formulario de Voluntario")
        form_frame.pack(pady=10, padx=10, fill="x")
        
        # Campos del formulario
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.volunteer_name = ttk.Entry(form_frame)
        self.volunteer_name.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Identificación:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.volunteer_id = ttk.Entry(form_frame)
        self.volunteer_id.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Ciudad:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.volunteer_city = ttk.Combobox(form_frame)
        self.volunteer_city.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Albergue:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.volunteer_shelter = ttk.Combobox(form_frame)
        self.volunteer_shelter.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Profesión:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.volunteer_profession = ttk.Entry(form_frame)
        self.volunteer_profession.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Botones CRUD
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Agregar", command=self.add_volunteer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.update_volunteer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_volunteer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_volunteer_form).pack(side="left", padx=5)
        
        # Tabla de voluntarios
        table_frame = ttk.LabelFrame(self.tab_volunteers, text="Lista de Voluntarios")
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        columns = ("ID", "Nombre", "Identificación", "Ciudad", "Albergue", "Profesión")
        
        self.volunteers_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.volunteers_table.heading(col, text=col)
            self.volunteers_table.column(col, width=120, anchor="center")
        
        self.volunteers_table.column("Nombre", width=150)
        self.volunteers_table.column("Profesión", width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.volunteers_table.yview)
        self.volunteers_table.configure(yscrollcommand=scrollbar.set)
        
        self.volunteers_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar evento de selección
        self.volunteers_table.bind("<<TreeviewSelect>>", self.on_volunteer_select)

    def add_volunteer(self):
        try:
            # Obtener valores del formulario
            name = self.volunteer_name.get()
            identification = self.volunteer_id.get()
            city = self.volunteer_city.get()
            shelter = self.volunteer_shelter.get()
            profession = self.volunteer_profession.get()
            
            # Validar campos
            if not all([name, identification, city, profession]):
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios excepto albergue")
                return
            
            # Crear DTO
            volunteer = VoluntarioDTO(
                nombre=name,
                identificacion=identification,
                id_ciudad=int(city.split(" - ")[0]),
                id_albergue=int(shelter.split(" - ")[0]) if shelter else None,
                profesion=profession
            )
            
            # Insertar en la base de datos
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO voluntarios (Nombre, identificacion, id_ciudad, id_albergue, Profesion)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                volunteer.nombre, volunteer.identificacion, volunteer.id_ciudad,
                volunteer.id_albergue, volunteer.profesion
            ))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Voluntario agregado correctamente")
            self.load_volunteers()
            self.clear_volunteer_form()
        except Error as e:
            messagebox.showerror("Error", f"Error al agregar voluntario: {e}")

    def update_volunteer(self):
        selected_item = self.volunteers_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un voluntario para actualizar")
            return
        
        try:
            volunteer_id = self.volunteers_table.item(selected_item)['values'][0]
            
            # Obtener valores del formulario
            name = self.volunteer_name.get()
            identification = self.volunteer_id.get()
            city = self.volunteer_city.get()
            shelter = self.volunteer_shelter.get()
            profession = self.volunteer_profession.get()
            
            # Validar campos
            if not all([name, identification, city, profession]):
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios excepto albergue")
                return
            
            # Crear DTO
            volunteer = VoluntarioDTO(
                id_voluntario=volunteer_id,
                nombre=name,
                identificacion=identification,
                id_ciudad=int(city.split(" - ")[0]),
                id_albergue=int(shelter.split(" - ")[0]) if shelter else None,
                profesion=profession
            )
            
            # Actualizar en la base de datos
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE voluntarios 
                SET Nombre = %s, identificacion = %s, id_ciudad = %s, 
                    id_albergue = %s, Profesion = %s
                WHERE id_voluntario = %s
            """, (
                volunteer.nombre, volunteer.identificacion, volunteer.id_ciudad,
                volunteer.id_albergue, volunteer.profesion, volunteer.id_voluntario
            ))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Voluntario actualizado correctamente")
            self.load_volunteers()
        except Error as e:
            messagebox.showerror("Error", f"Error al actualizar voluntario: {e}")

    def delete_volunteer(self):
        selected_item = self.volunteers_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un voluntario para eliminar")
            return
        try:
            volunteer_id = self.volunteers_table.item(selected_item)['values'][0]
            
            # Confirmar eliminación
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este voluntario?"):
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM voluntarios WHERE id_voluntario = %s", (volunteer_id,))
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Éxito", "Voluntario eliminado correctamente")
                self.load_volunteers()
                self.clear_volunteer_form()
        except Error as e:
            messagebox.showerror("Error", f"Error al eliminar voluntario: {e}")

    def clear_volunteer_form(self):
        self.volunteer_name.delete(0, tk.END)
        self.volunteer_id.delete(0, tk.END)
        self.volunteer_city.set('')
        self.volunteer_shelter.set('')
        self.volunteer_profession.delete(0, tk.END)


        
    
    def setup_reports_tab(self):
        report_frame = ttk.LabelFrame(self.tab_reports, text="Reportes y Procedimientos")
        report_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Botones para reportes
        ttk.Button(report_frame, text="Distribución de Refugiados", 
                  command=self.generate_refugee_distribution_report).pack(pady=5, fill="x", padx=20)
        
        ttk.Button(report_frame, text="Voluntarios por Ciudad", 
                  command=self.generate_volunteers_by_city_report).pack(pady=5, fill="x", padx=20)
        
        ttk.Button(report_frame, text="Actualizar Estadísticas de Albergues", 
                  command=self.execute_shelter_stats_procedure).pack(pady=5, fill="x", padx=20)
        
        # Área para mostrar resultados
        self.report_text = tk.Text(report_frame, height=20, wrap="word")
        self.report_text.pack(fill="both", expand=True, pady=10, padx=10)
        
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
    
    def load_initial_data(self):
        self.load_cities()
        self.load_shelters()
        self.load_refugees()
        self.load_volunteers()
        self.load_cities_table()
        
        # Cargar combobox de ciudades para albergues
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id_ciudad, ciudad, departamento FROM ciudades ORDER BY ciudad")
        cities = cursor.fetchall()
        city_values = [f"{city[0]} - {city[1]} ({city[2]})" for city in cities]
        self.shelter_city['values'] = city_values
        self.volunteer_city['values'] = city_values
        cursor.close()
    
    def load_cities(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id_ciudad, ciudad, departamento FROM ciudades ORDER BY ciudad")
            cities = cursor.fetchall()
            
            city_values = [f"{city[0]} - {city[1]} ({city[2]})" for city in cities]
            
            self.displacement_city['values'] = city_values
            self.refuge_city['values'] = city_values
            
            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar ciudades: {e}")

    def load_shelters(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.*, c.ciudad as nombre_ciudad 
                FROM albergues a
                JOIN ciudades c ON a.id_ciudad = c.id_ciudad
                ORDER BY a.nombre
            """)
            shelters = cursor.fetchall()
            
            # Limpiar tabla
            for row in self.shelters_table.get_children():
                self.shelters_table.delete(row)
            
            # Agregar datos a la tabla
            for shelter in shelters:
                self.shelters_table.insert("", "end", values=(
                    shelter['id_albergue'],
                    shelter['nombre'],
                    shelter['nombre_ciudad'],
                    shelter['direccion_del_albergue'],
                    shelter['personas_albergadas'],
                    shelter['ciudad_de_procedencia']
                ))
            
            # Cargar combobox de albergues para voluntarios
            shelter_values = [f"{shelter['id_albergue']} - {shelter['nombre']}" for shelter in shelters]
            self.volunteer_shelter['values'] = shelter_values
            
            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar albergues: {e}")

    def load_cities_table(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ciudades ORDER BY ciudad")
            cities = cursor.fetchall()
            
            # Limpiar tabla
            for row in self.cities_table.get_children():
                self.cities_table.delete(row)
            
            # Agregar datos a la tabla
            for city in cities:
                self.cities_table.insert("", "end", values=(
                    city['id_ciudad'],
                    city['departamento'],
                    city['ciudad'],
                    city['localidad'],
                    city['cantidad_de_habitantes']
                ))
            
            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar ciudades: {e}")
    
    def load_refugees(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, 
                       c1.ciudad as ciudad_origen, c1.departamento as depto_origen,
                       c2.ciudad as ciudad_refugio, 
                       a.nombre as albergue
                FROM refugiados r
                JOIN ciudades c1 ON r.id_ciudad_del_despiazamiento = c1.id_ciudad
                JOIN ciudades c2 ON r.id_ciudad_a_refugiarse = c2.id_ciudad
                LEFT JOIN albergues a ON c2.id_ciudad = a.id_ciudad
                ORDER BY r.nombre
            """)
            refugees = cursor.fetchall()
            
            # Limpiar tabla
            for row in self.refugees_table.get_children():
                self.refugees_table.delete(row)
            
            # Agregar datos a la tabla
            for refugee in refugees:
                self.refugees_table.insert("", "end", values=(
                    refugee['id_refugiado'],
                    refugee['nombre'],
                    refugee['identificacion'],
                    refugee['numero_de_contacto'],
                    refugee['email'],
                    f"{refugee['ciudad_origen']} ({refugee['depto_origen']})",
                    refugee['motivo_despiazamiento'],
                    refugee['ciudad_refugio'],
                    refugee['albergue'] if refugee['albergue'] else "No asignado"
                ))
            
            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar refugiados: {e}")
    
    def on_refugee_select(self, event):
        selected_item = self.refugees_table.focus()
        if selected_item:
            refugee_data = self.refugees_table.item(selected_item)['values']
            
            self.refugee_name.delete(0, tk.END)
            self.refugee_name.insert(0, refugee_data[1])
            
            self.refugee_id.delete(0, tk.END)
            self.refugee_id.insert(0, refugee_data[2])
            
            self.refugee_contact.delete(0, tk.END)
            self.refugee_contact.insert(0, refugee_data[3])
            
            self.refugee_email.delete(0, tk.END)
            self.refugee_email.insert(0, refugee_data[4])
            
            # Buscar ciudad de desplazamiento
            displacement_text = refugee_data[5].split(" (")[0]
            for i, city in enumerate(self.displacement_city['values']):
                if displacement_text in city:
                    self.displacement_city.current(i)
                    break
            
            self.displacement_reason.set(refugee_data[6])
            
            # Buscar ciudad de refugio
            refuge_text = refugee_data[7]
            for i, city in enumerate(self.refuge_city['values']):
                if refuge_text in city:
                    self.refuge_city.current(i)
                    break

    def load_volunteers(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, c.ciudad as nombre_ciudad, a.nombre as nombre_albergue
                FROM voluntarios v
                LEFT JOIN ciudades c ON v.id_ciudad = c.id_ciudad
                LEFT JOIN albergues a ON v.id_albergue = a.id_albergue
                ORDER BY v.nombre
            """)
            volunteers = cursor.fetchall()
            
            # Limpiar tabla
            for row in self.volunteers_table.get_children():
                self.volunteers_table.delete(row)
            
            # Agregar datos a la tabla
            for volunteer in volunteers:
                self.volunteers_table.insert("", "end", values=(
                    volunteer['id_voluntario'],
                    volunteer['nombre'],
                    volunteer['identificacion'],
                    volunteer['nombre_ciudad'] if volunteer['nombre_ciudad'] else "",
                    volunteer['nombre_albergue'] if volunteer['nombre_albergue'] else "No asignado",
                    volunteer['profesion']
                ))
            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar voluntarios: {e}")
    def on_city_select(self, event):
        selected_item = self.cities_table.focus()
        if selected_item:
            city_data = self.cities_table.item(selected_item)['values']
            
            self.city_department.delete(0, tk.END)
            self.city_department.insert(0, city_data[1])
            
            self.city_name.delete(0, tk.END)
            self.city_name.insert(0, city_data[2])
            
            self.city_locality.delete(0, tk.END)
            self.city_locality.insert(0, city_data[3])
            
            self.city_population.delete(0, tk.END)
            self.city_population.insert(0, city_data[4])
    
    def on_volunteer_select(self, event):
        selected_item = self.volunteers_table.focus()
        if selected_item:
            volunteer_data = self.volunteers_table.item(selected_item)['values']
            
            self.volunteer_name.delete(0, tk.END)
            self.volunteer_name.insert(0, volunteer_data[1])
            
            self.volunteer_id.delete(0, tk.END)
            self.volunteer_id.insert(0, volunteer_data[2])
            
            # Buscar ciudad en el combobox
            if volunteer_data[3]:
                for i, city in enumerate(self.volunteer_city['values']):
                    if volunteer_data[3] in city:
                        self.volunteer_city.current(i)
                        break
            
            # Buscar albergue en el combobox
            if volunteer_data[4] and volunteer_data[4] != "No asignado":
                for i, shelter in enumerate(self.volunteer_shelter['values']):
                    if volunteer_data[4] in shelter:
                        self.volunteer_shelter.current(i)
                        break
            
            self.volunteer_profession.delete(0, tk.END)
            self.volunteer_profession.insert(0, volunteer_data[5])
    
    # Métodos CRUD para Refugiados
    
    
    def add_refugee(self):
        try:
            # Obtener valores del formulario
            name = self.refugee_name.get()
            identification = self.refugee_id.get()
            contact = self.refugee_contact.get()
            email = self.refugee_email.get()
            
            displacement_city_id = int(self.displacement_city.get().split(" - ")[0])
            reason = self.displacement_reason.get()
            refuge_city_id = int(self.refuge_city.get().split(" - ")[0])
            
            # Validar campos
            if not all([name, identification, contact, reason]):
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios excepto email")
                return
            
            # Crear DTO
            refugee = RefugiadoDTO(
                nombre=name,
                identificacion=identification,
                numero_de_contacto=contact,
                email=email,
                id_ciudad_desplazamiento=displacement_city_id,
                motivo_desplazamiento=reason,
                id_ciudad_refugio=refuge_city_id
            )
            
            # Insertar en la base de datos
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO refugiados (Nombre, identificacion, numero_de_contacto, Email, 
                                      id_ciudad_del_despiazamiento, motivo_despiazamiento, 
                                      id_ciudad_a_refugiarse)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                refugee.nombre, refugee.identificacion, refugee.numero_de_contacto, refugee.email,
                refugee.id_ciudad_despiazamiento, refugee.motivo_despiazamiento,
                refugee.id_ciudad_refugio
            ))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Refugiado agregado correctamente")
            self.load_refugees()
            self.clear_refugee_form()
        except Error as e:
            messagebox.showerror("Error", f"Error al agregar refugiado: {e}")
    
    def update_refugee(self):
        selected_item = self.refugees_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un refugiado para actualizar")
            return
        
        try:
            refugee_id = self.refugees_table.item(selected_item)['values'][0]
            
            # Obtener valores del formulario
            name = self.refugee_name.get()
            identification = self.refugee_id.get()
            contact = self.refugee_contact.get()
            email = self.refugee_email.get()
            
            displacement_city_id = int(self.displacement_city.get().split(" - ")[0])
            reason = self.displacement_reason.get()
            refuge_city_id = int(self.refuge_city.get().split(" - ")[0])
            
            # Validar campos
            if not all([name, identification, contact, reason]):
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios excepto email")
                return
            
            # Crear DTO
            refugee = RefugiadoDTO(
                id_refugiado=refugee_id,
                nombre=name,
                identificacion=identification,
                numero_de_contacto=contact,
                email=email,
                id_ciudad_despiazamiento=displacement_city_id,
                motivo_despiazamiento=reason,
                id_ciudad_refugio=refuge_city_id
            )
            
            # Actualizar en la base de datos
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE refugiados 
                SET Nombre = %s, identificacion = %s, numero_de_contacto = %s, Email = %s,
                    id_ciudad_del_despiazamiento = %s, motivo_despiazamiento = %s, 
                    id_ciudad_a_refugiarse = %s
                WHERE id_refugiado = %s
            """, (
                refugee.nombre, refugee.identificacion, refugee.numero_de_contacto, refugee.email,
                refugee.id_ciudad_despiazamiento, refugee.motivo_despiazamiento,
                refugee.id_ciudad_refugio, refugee.id_refugiado
            ))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Refugiado actualizado correctamente")
            self.load_refugees()
        except Error as e:
            messagebox.showerror("Error", f"Error al actualizar refugiado: {e}")
    
    def delete_refugee(self):
        selected_item = self.refugees_table.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un refugiado para eliminar")
            return
        
        confirmation = messagebox.askyesno("Confirmación", "¿Está seguro de eliminar este refugiado?")
        if not confirmation:
            return
        
        try:
            refugee_id = self.refugees_table.item(selected_item)['values'][0]
            
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM refugiados WHERE id_refugiado = %s", (refugee_id,))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", "Refugiado eliminado correctamente")
            self.load_refugees()
            self.clear_refugee_form()
        except Error as e:
            messagebox.showerror("Error", f"Error al eliminar refugiado: {e}")
    
    def clear_refugee_form(self):
        self.refugee_name.delete(0, tk.END)
        self.refugee_id.delete(0, tk.END)
        self.refugee_contact.delete(0, tk.END)
        self.refugee_email.delete(0, tk.END)
        self.displacement_city.set('')
        self.displacement_reason.set('')
        self.refuge_city.set('')
    
    def generate_refugee_distribution_report(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.ciudad, c.departamento, 
                       COUNT(r.id_refugiado) as cantidad_refugiados,
                       GROUP_CONCAT(DISTINCT cd.ciudad SEPARATOR ', ') as ciudades_origen
                FROM ciudades c
                LEFT JOIN refugiados r ON c.id_ciudad = r.id_ciudad_a_refugiarse
                LEFT JOIN ciudades cd ON r.id_ciudad_del_despiazamiento = cd.id_ciudad
                GROUP BY c.ciudad, c.departamento
                ORDER BY cantidad_refugiados DESC
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "DISTRIBUCIÓN DE REFUGIADOS POR CIUDAD\n\n")
            self.report_text.insert(tk.END, "Ciudad (Departamento)\t\tRefugiados\tCiudades de Origen\n")
            self.report_text.insert(tk.END, "="*80 + "\n")
            
            for row in results:
                self.report_text.insert(tk.END, 
                    f"{row['ciudad']} ({row['departamento']})\t\t{row['cantidad_refugiados']}\t\t{row['ciudades_origen']}\n")
        except Error as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def generate_volunteers_by_city_report(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.ciudad, c.departamento, 
                       COUNT(v.id_voluntario) as cantidad_voluntarios,
                       GROUP_CONCAT(DISTINCT v.profesion SEPARATOR ', ') as profesiones
                FROM ciudades c
                LEFT JOIN voluntarios v ON c.id_ciudad = v.id_ciudad
                GROUP BY c.ciudad, c.departamento
                ORDER BY cantidad_voluntarios DESC
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "VOLUNTARIOS POR CIUDAD\n\n")
            self.report_text.insert(tk.END, "Ciudad (Departamento)\t\tVoluntarios\tProfesiones\n")
            self.report_text.insert(tk.END, "="*80 + "\n")
            
            for row in results:
                self.report_text.insert(tk.END, 
                    f"{row['ciudad']} ({row['departamento']})\t\t{row['cantidad_voluntarios']}\t\t{row['profesiones']}\n")
        except Error as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")

    def execute_shelter_stats_procedure(self):
        try:
            cursor = self.db_connection.cursor()
            
            # Ejecutar el procedimiento almacenado
            cursor.callproc("ActualizarEstadisticasAlbergues")
            self.db_connection.commit()
            
            # Mostrar resultados actualizados
            cursor.execute("""
                SELECT a.nombre, c.ciudad, a.personas_albergadas, a.ciudad_de_procedencia
                FROM albergues a
                JOIN ciudades c ON a.id_ciudad = c.id_ciudad
                ORDER BY a.personas_albergadas DESC
            """)
            results = cursor.fetchall()
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "ESTADÍSTICAS ACTUALIZADAS DE ALBERGUES\n\n")
            self.report_text.insert(tk.END, "Albergue (Ciudad)\t\tPersonas\tCiudad de Procedencia\n")
            self.report_text.insert(tk.END, "="*80 + "\n")
            
            for row in results:
                self.report_text.insert(tk.END, f"{row[0]} ({row[1]})\t\t{row[2]}\t\t{row[3]}\n")
            
            cursor.close()
            messagebox.showinfo("Éxito", "Estadísticas de albergues actualizadas correctamente")
        except Error as e:
            messagebox.showerror("Error", f"Error al ejecutar procedimiento: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RefugeeManagementApp(root)
    root.mainloop()