import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

class MatriculasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matriculas 2016-2024")
        self.root.geometry("1000x600")

        # DataFrame para almacenar los datos
        self.df = None  
        
        # Restablecer
        self.original_df = None

        # Crear Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Crear Frame para los botones 
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Crear botones
        self.open_button = ttk.Button(self.button_frame, text="Abrir archivo", command=self.file_open)
        self.open_button.pack(side=tk.TOP, padx=5, pady=5)

        self.plot_bar_button = ttk.Button(self.button_frame, text="Graficar barras", command=self.graficar_barras)
        self.plot_bar_button.pack(side=tk.TOP, padx=5, pady=5)

        # Menú desplegable para seleccionar la columna para el gráfico de barras
        self.column_selection = tk.StringVar()
        self.column_selection.set("Seleccione una columna")

        self.column_menu = ttk.OptionMenu(self.button_frame, self.column_selection, "Seleccione una columna", 
                                          "COLEGIO_DEPA", "COLEGIO0_PROV", "COLEGIO_DIST", "ANIO", 
                                          "PERIODO", "TIPO_MATRICULA", "DOMICILIO_DEPA", "DOMICILIO_PROV", 
                                          "DOMICILIO_DIST", "ANIO_NACIMIENTO", "NACIMIENTO_PAIS", 
                                          "NACIMIENTO_DEPA", "NACIMIENTO_PROV", "NACIMIENTO_DIST", 
                                          "SEXO", "MODALIDAD", "METODOLOGIA", "FACULTAD", "ESPECIALIDAD", 
                                          "CICLO_RELATIVO")
        self.column_menu.pack(side=tk.TOP, padx=5, pady=5)
        
        # Seguir con los botones
        self.plot_heatmap_button = ttk.Button(self.button_frame, text="Graficar mapa de calor", command=self.graficar_heatmap)
        self.plot_heatmap_button.pack(side=tk.TOP, padx=5, pady=5)
        
        self.search_button = ttk.Button(self.button_frame, text="Buscar por IDHASH", command=self.buscar_por_idhash)
        self.search_button.pack(side=tk.TOP, padx=5, pady=5)
        
        # Campo de entrada para búsqueda por IDHASH
        self.idhash_entry = ttk.Entry(self.button_frame)
        self.idhash_entry.pack(side=tk.TOP, padx=5, pady=5)
        
        # Botones
        self.filter_faculty_button = ttk.Button(self.button_frame, text="Filtrar por Facultad", command=self.filtrar_por_facultad)
        self.filter_faculty_button.pack(side=tk.TOP, padx=5, pady=5)

        self.filter_specialty_button = ttk.Button(self.button_frame, text="Filtrar por Especialidad", command=self.filtrar_por_especialidad)
        self.filter_specialty_button.pack(side=tk.TOP, padx=5, pady=5)

        self.filter_nacimiento_depa_button = ttk.Button(self.button_frame, text="Filtrar por departamento de Nacimiento", command=self.filtrar_por_nacimiento_depa)
        self.filter_nacimiento_depa_button.pack(side=tk.TOP, padx=5, pady=5)

        self.filter_colegio_dist_button = ttk.Button(self.button_frame, text="Filtrar por Colegio Distrital", command=self.filtrar_por_colegio_dist)
        self.filter_colegio_dist_button.pack(side=tk.TOP, padx=5, pady=5)

        self.filter_by_year_button = ttk.Button(self.button_frame, text="Filtrar por Año", command=self.filtrar_por_anio)
        self.filter_by_year_button.pack(side=tk.TOP, padx=5, pady=5)

        self.filter_by_birth_year_button = ttk.Button(self.button_frame, text="Filtrar por Año de Nacimiento", command=self.filtrar_por_anio_nacimiento)
        self.filter_by_birth_year_button.pack(side=tk.TOP, padx=5, pady=5)

        self.matricula_stats_button = ttk.Button(self.button_frame, text="Estadísticas de Matrículas", command=self.matricula_stats)
        self.matricula_stats_button.pack(side=tk.TOP, padx=5, pady=5)
        
        self.reset_button = ttk.Button(self.button_frame, text="Restablecer Base de Datos", command=self.restablecer_base_datos)
        self.reset_button.pack(side=tk.TOP, padx=5, pady=5)
        
        self.save_pdf_button = ttk.Button(self.button_frame, text="Guardar como PDF", command=self.guardar_como_pdf)
        self.save_pdf_button.pack(side=tk.TOP, padx=5, pady=5)

        self.export_button = ttk.Button(self.button_frame, text="Exportar datos", command=self.exportar_datos)
        self.export_button.pack(side=tk.TOP, padx=5, pady=5)
        
        self.exit_button = ttk.Button(self.button_frame, text="Salir", command=self.salir)
        self.exit_button.pack(side=tk.TOP, pady=10)
        
        # Crear Frame para datos con barras de desplazamiento
        self.data_frame = ttk.Frame(self.main_frame)
        self.data_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear barras de desplazamiento
        self.scroll_y = ttk.Scrollbar(self.data_frame, orient="vertical")
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scroll_x = ttk.Scrollbar(self.data_frame, orient="horizontal")
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Crear Treeview para mostrar los datos
        self.tree = ttk.Treeview(self.data_frame, columns=("IDHASH", "anio", "anio_nacimiento", "ciclo", "facultad", "especialidad", "sexo", "modalidad", "domicilio_depa", "colegio_dist"), show='headings', yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.tree.heading("IDHASH", text="Codigo")
        self.tree.heading("anio", text="Año")
        self.tree.heading("anio_nacimiento", text="Año de Nacimiento")
        self.tree.heading("ciclo", text="Ciclo")
        self.tree.heading("facultad", text="Facultad")
        self.tree.heading("especialidad", text="Especialidad")
        self.tree.heading("sexo", text="Sexo")
        self.tree.heading("modalidad", text="Modalidad")
        self.tree.heading("domicilio_depa", text="Departamento")
        self.tree.heading("colegio_dist", text="Colegio Distrital")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar el comportamiento de las barras de desplazamiento
        self.scroll_y.config(command=self.tree.yview)
        self.scroll_x.config(command=self.tree.xview)

    def file_open(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.original_df = self.df.copy()
                self.display_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                    
    def display_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, row in self.df.iterrows():
            self.tree.insert("", "end", text=index, values=(row["IDHASH"], row["ANIO"], row["ANIO_NACIMIENTO"], row["CICLO_RELATIVO"], row["FACULTAD"], row["ESPECIALIDAD"], row["SEXO"], row["MODALIDAD"], row["DOMICILIO_DEPA"], row["COLEGIO_DIST"]))

    def graficar_barras(self):
        if self.df is not None:
            column = self.column_selection.get()
            if column != "Seleccione una columna":
                try:
                    self.df[column].value_counts().plot(kind='bar')
                    plt.title(f"Distribución de {column}")
                    plt.xlabel(column)
                    plt.ylabel("Frecuencia")
                    plt.show()
                except KeyError:
                    messagebox.showerror("Error", f"La columna '{column}' no se encuentra en el DataFrame.")
            else:
                messagebox.showinfo("Información", "Por favor seleccione una columna para graficar.")

    def graficar_heatmap(self):
        if self.df is not None:
            numeric_columns = ['ANIO', 'ANIO_NACIMIENTO']  # Añadir otras columnas numéricas según sea necesario
            correlation_matrix = self.df[numeric_columns].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
            plt.title("Mapa de Calor de Correlaciones")
            plt.show()


    def filtrar_por_facultad(self):
        if self.df is not None:
            facultad = simpledialog.askstring("Entrada", "Ingrese la Facultad:")
            if facultad:
                filtered_df = self.df[self.df["FACULTAD"].str.contains(facultad, na=False, case=False)]
                self.show_stats(filtered_df)
                self.df = filtered_df
                self.display_data()
            else:
                messagebox.showinfo("Información", "No se encontraron registros para la facultad proporcionada.")

    def filtrar_por_especialidad(self):
        if self.df is not None:
            especialidad = simpledialog.askstring("Entrada", "Ingrese la Especialidad:")
            if especialidad:
                filtered_df = self.df[self.df["ESPECIALIDAD"].str.contains(especialidad, na=False, case=False)]
                self.show_stats(filtered_df)
                self.df = filtered_df
                self.display_data()
            else:
                messagebox.showinfo("Información", "No se encontraron registros para la especialidad proporcionada.")

    def filtrar_por_nacimiento_depa(self):
        if self.df is not None:
            nacimiento_depa = simpledialog.askstring("Entrada", "Ingrese el Departamento de Nacimiento:")
            if nacimiento_depa:
                filtered_df = self.df[self.df["NACIMIENTO_DEPA"].str.contains(nacimiento_depa, na=False, case=False)]
                self.show_stats(filtered_df)
                self.df = filtered_df
                self.display_data()
            else:
                messagebox.showinfo("Información", "No se encontraron registros para el departamento de nacimiento proporcionado.")

    def filtrar_por_colegio_dist(self):
        if self.df is not None:
            colegio_dist = simpledialog.askstring("Entrada", "Ingrese el Colegio Distrital:")
            if colegio_dist:
                filtered_df = self.df[self.df["COLEGIO_DIST"].str.contains(colegio_dist, na=False, case=False)]
                self.show_stats(filtered_df)
                self.df = filtered_df
                self.display_data()
            else:
                messagebox.showinfo("Información", "No se encontraron registros para el colegio distrital proporcionado.")
                
    def filtrar_por_anio(self):
        if self.df is not None:
            anio = simpledialog.askinteger("Entrada", "Ingrese el Año:")
            if anio:
                filtered_df = self.df[self.df["ANIO"] == anio]
                self.show_stats(filtered_df)
                self.df = filtered_df
                self.display_data()
            else:
                messagebox.showinfo("Información", "No se encontraron registros para el año proporcionado.")
                
    def filtrar_por_anio_nacimiento(self):
        if self.df is not None:
            anio_nacimiento = simpledialog.askinteger("Entrada", "Ingrese el Año de Nacimiento:")
            if anio_nacimiento:
                filtered_df = self.df[self.df["ANIO_NACIMIENTO"] == anio_nacimiento]
                self.show_stats(filtered_df)
                self.df = filtered_df
                self.display_data()
            else:
                messagebox.showinfo("Información", "No se encontraron registros para el año de nacimiento proporcionado.")

    def buscar_por_idhash(self):
        if self.df is not None:
            idhash = self.idhash_entry.get()
            if idhash:
                result = self.df[self.df["IDHASH"].astype(str).str.contains(idhash, na=False)]
                self.df = result
                self.display_data()
                self.show_stats(result)
            else:
                messagebox.showinfo("Información", "Por favor ingrese un IDHASH.")

    def matricula_stats(self):
        if self.df is not None:
            # Crear la primera ventana con las estadísticas de tipo de matrícula
            tipo_matricula_window = tk.Toplevel(self.root)
            tipo_matricula_window.title("Estadísticas de Tipo de Matrícula")
            stats_tipo_matricula = self.df['TIPO_MATRICULA'].value_counts().to_string()
            tk.Label(tipo_matricula_window, text=stats_tipo_matricula).pack()

            # Crear la segunda ventana con las estadísticas por año, facultad, ciclo y especialidad
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Estadísticas Detalladas")

            # Crear un Frame dentro de la ventana de estadísticas
            stats_frame = tk.Frame(stats_window)
            stats_frame.pack(fill=tk.BOTH, expand=True)

            # Crear la barra de desplazamiento
            scrollbar = tk.Scrollbar(stats_frame, orient="vertical")
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Crear el widget Text para mostrar las estadísticas
            stats_text_widget = tk.Text(stats_frame, wrap=tk.WORD, height=30, width=80, yscrollcommand=scrollbar.set)
            stats_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=stats_text_widget.yview)

            # Crear el contenido de la ventana
            stats_text = ""
            for year in sorted(self.df["ANIO"].unique()):
                df_year = self.df[self.df["ANIO"] == year]
                stats_text += f"Año {year}:\n"
                for facultad in df_year["FACULTAD"].unique():
                    df_facultad = df_year[df_year["FACULTAD"] == facultad]
                    total = len(df_facultad)
                    stats_text += f"  {facultad}: {total} estudiantes\n"
                    for especialidad in df_facultad["ESPECIALIDAD"].unique():
                        df_especialidad = df_facultad[df_facultad["ESPECIALIDAD"] == especialidad]
                        stats_text += f"    Especialidad {especialidad}: {len(df_especialidad)} estudiantes\n"
                        for ciclo in df_especialidad["CICLO_RELATIVO"].unique():
                            df_ciclo = df_especialidad[df_especialidad["CICLO_RELATIVO"] == ciclo]
                            stats_text += f"      Ciclo {ciclo}: {len(df_ciclo)} estudiantes\n"

            # Insertar el contenido en el widget Text
            stats_text_widget.insert(tk.END, stats_text)
            stats_text_widget.config(state=tk.DISABLED)


    def show_stats(self, df):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas de Filtrado")
        total = len(df)
        stats_text = f"Total de estudiantes: {total}\n"
        carreras = df["ESPECIALIDAD"].value_counts()
        for carrera, count in carreras.items():
            porcentaje = (count / total) * 100
            stats_text += f"{carrera}: {count} estudiantes ({porcentaje:.2f}%)\n"
        tk.Label(stats_window, text=stats_text).pack()

    def restablecer_base_datos(self):
        self.df = self.original_df.copy()
        self.display_data()

    def guardar_como_pdf(self):
        if self.df is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file_path:
                with PdfPages(file_path) as pdf:
                    for column in self.df.columns:
                        plt.figure()
                        self.df[column].value_counts().plot(kind='bar')
                        plt.title(f"Distribución de {column}")
                        plt.xlabel(column)
                        plt.ylabel("Frecuencia")
                        pdf.savefig()
                        plt.close()
                messagebox.showinfo("Información", "Archivo PDF guardado exitosamente.")
                
    def exportar_datos(self):
        if self.df is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                self.df.to_csv(file_path, index=False)
                messagebox.showinfo("Información", "Datos exportados exitosamente.")

    def salir(self):
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MatriculasApp(root)
    root.mainloop()
