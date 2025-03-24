# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, filedialog
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
import sys
import os

class BecasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Extractor de Másteres")
        self.root.geometry("400x200")

        self.frame = tk.Frame(root)
        self.frame.pack(pady=20)

        self.start_button = tk.Button(self.frame, text="Extraer Datos", command=self.scrape_data, font=("Arial", 14))
        self.start_button.pack(pady=10)

        self.status_label = tk.Label(self.frame, text="Haz clic para comenzar", font=("Arial", 10))
        self.status_label.pack()

    def scrape_data(self):
        try:
            # Configuración para ejecutable compilado
            if getattr(sys, 'frozen', False):
                chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
            else:
                chromedriver_path = "chromedriver.exe"

            # Opciones de Chrome
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")  # Sin ventana del navegador
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")  # Ocultar warnings

            # Inicializar driver
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)

            # Cargar página
            driver.get("https://www.educacion.gob.es/simuladorbecas/formularioSimulacionVariable?idCurso=2023&secuenc=1")
            time.sleep(3)

            # Seleccionar nivel educativo
            nivel_educativo = Select(driver.find_element(By.ID, "nivelEducativo"))
            nivel_educativo.select_by_visible_text("Másteres")
            time.sleep(2)

            # Obtener universidades
            universidades_dropdown = Select(driver.find_element(By.ID, "universidades"))
            universidades = [opt.text for opt in universidades_dropdown.options if opt.text != "Seleccione"]

            data = []
            for idx, uni in enumerate(universidades):
                # Actualizar estado en la interfaz
                self.status_label.config(text=f"Procesando: {uni} ({idx+1}/{len(universidades)})")
                self.root.update_idletasks()

                # Seleccionar universidad
                universidades_dropdown.select_by_visible_text(uni)
                time.sleep(2)

                # Obtener estudios
                estudios_dropdown = Select(driver.find_element(By.ID, "estudios"))
                estudios = [opt.text for opt in estudios_dropdown.options if opt.text != "Seleccione"]
                data.append({
                    "Universidad": uni,
                    "Estudios": ", ".join(estudios)
                })

            # Guardar archivo
            if data:
                df = pd.DataFrame(data)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx")],
                    initialfile="maestrias_universidades.xlsx"
                )
                if file_path:
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Éxito", f"Archivo guardado en:\n{file_path}")

            driver.quit()
            self.status_label.config(text="Proceso completado")

        except Exception as e:
            messagebox.showerror("Error", f"Ha ocurrido un error:\n{str(e)}")
            if 'driver' in locals():
                driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BecasApp(root)
    root.mainloop()