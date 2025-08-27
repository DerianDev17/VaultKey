import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import threading
import time
from vault_core import load_or_create_vault, save_vault
from password_generator import generate_password, check_password_strength
from cloud_sync import LocalCloudSync
from security_audit import SecurityAudit, SecureClipboard

# Configuración de tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PasswordVaultComplete:
    def __init__(self):
        self.vault_data = None
        self.vault_key = None
        self.vault_file = "password_vault_complete.json"
        self.master_password = None
        self.cloud_sync = LocalCloudSync("vault_cloud_complete")
        self.security_audit = SecurityAudit()
        self.secure_clipboard = SecureClipboard()
        
        # Variables de auto-bloqueo
        self.auto_lock_minutes = 15
        self.last_activity = time.time()
        self.lock_timer = None
        
        # Ventana principal
        self.root = ctk.CTk()
        self.root.title("Gestor de Contraseñas Profesional v3.0")
        self.root.geometry("1000x700")
        
        # Variables para la interfaz
        self.entries_frame = None
        self.selected_entry = None
        self.sync_status_label = None
        self.security_status_label = None
        
        # Bind eventos para detectar actividad
        self.root.bind('<Key>', self.update_activity)
        self.root.bind('<Button>', self.update_activity)
        
        self.setup_login_screen()
        self.start_auto_lock_timer()
        
    def update_activity(self, event=None):
        """Actualiza el tiempo de última actividad"""
        self.last_activity = time.time()
        
    def start_auto_lock_timer(self):
        """Inicia el temporizador de auto-bloqueo"""
        def check_auto_lock():
            while True:
                if self.vault_data is not None:  # Solo si hay sesión activa
                    time_since_activity = time.time() - self.last_activity
                    if time_since_activity > (self.auto_lock_minutes * 60):
                        # Auto-bloquear
                        self.root.after(0, self.auto_lock)
                        break
                time.sleep(30)  # Verificar cada 30 segundos
        
        self.lock_timer = threading.Thread(target=check_auto_lock, daemon=True)
        self.lock_timer.start()
        
    def auto_lock(self):
        """Bloquea automáticamente la aplicación"""
        if self.vault_data is not None:
            messagebox.showinfo("Auto-bloqueo", f"La aplicación se ha bloqueado automáticamente después de {self.auto_lock_minutes} minutos de inactividad.")
            self.logout()
        
    def setup_login_screen(self):
        """Configura la pantalla de inicio de sesión"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Frame principal de login
        login_frame = ctk.CTkFrame(self.root)
        login_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(login_frame, text="🔐 Gestor de Contraseñas Profesional v3.0", 
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=30)
        
        # Características
        features_frame = ctk.CTkFrame(login_frame)
        features_frame.pack(pady=20, padx=40, fill="x")
        
        features_title = ctk.CTkLabel(features_frame, text="✨ Características Profesionales", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        features_title.pack(pady=10)
        
        features_text = """
• 🔒 Cifrado AES-256 con derivación de clave PBKDF2
• ☁️ Sincronización automática en la nube
• 🛡️ Auditoría de seguridad con verificación de brechas
• 📋 Portapapeles seguro con auto-limpieza
• 🎲 Generador de contraseñas avanzado
• ⏰ Auto-bloqueo por inactividad
• 📱 Interfaz optimizada para móvil y escritorio
        """
        
        features_label = ctk.CTkLabel(features_frame, text=features_text, 
                                     font=ctk.CTkFont(size=12), justify="left")
        features_label.pack(pady=10)
        
        # Campo de contraseña
        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Contraseña maestra", 
                                          show="*", width=300, height=40)
        self.password_entry.pack(pady=20)
        
        # Botones de acceso
        button_frame = ctk.CTkFrame(login_frame)
        button_frame.pack(pady=10)
        
        login_button = ctk.CTkButton(button_frame, text="🔓 Acceder", command=self.login, 
                                     width=150, height=40)
        login_button.pack(side="left", padx=10)
        
        sync_login_button = ctk.CTkButton(button_frame, text="☁️ Sincronizar y Acceder", 
                                         command=self.sync_and_login, width=200, height=40)
        sync_login_button.pack(side="left", padx=10)
        
        # Configuración de auto-bloqueo
        config_frame = ctk.CTkFrame(login_frame)
        config_frame.pack(pady=20)
        
        ctk.CTkLabel(config_frame, text="Auto-bloqueo (minutos):", 
                    font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.auto_lock_var = ctk.StringVar(value=str(self.auto_lock_minutes))
        auto_lock_entry = ctk.CTkEntry(config_frame, textvariable=self.auto_lock_var, width=60)
        auto_lock_entry.pack(side="left", padx=5)
        
        def update_auto_lock():
            try:
                self.auto_lock_minutes = int(self.auto_lock_var.get())
            except:
                self.auto_lock_minutes = 15
        
        auto_lock_entry.bind('<FocusOut>', lambda e: update_auto_lock())
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda event: self.login())
        self.password_entry.focus()
        
    def login(self):
        """Maneja el proceso de inicio de sesión normal"""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Por favor ingresa tu contraseña maestra")
            return
            
        try:
            self.vault_data, self.vault_key = load_or_create_vault(self.vault_file, password)
            self.master_password = password
            self.update_activity()
            self.setup_main_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Error al acceder a la bóveda: {str(e)}")
    
    def sync_and_login(self):
        """Sincroniza con la nube antes de hacer login"""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Por favor ingresa tu contraseña maestra")
            return
        
        # Mostrar diálogo de progreso
        progress_dialog = ctk.CTkToplevel(self.root)
        progress_dialog.title("Sincronizando...")
        progress_dialog.geometry("300x150")
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
        
        progress_label = ctk.CTkLabel(progress_dialog, text="Sincronizando con la nube...", 
                                     font=ctk.CTkFont(size=14))
        progress_label.pack(pady=30)
        
        progress_bar = ctk.CTkProgressBar(progress_dialog, width=250)
        progress_bar.pack(pady=10)
        progress_bar.set(0.5)
        
        def sync_thread():
            try:
                success = self.cloud_sync.sync_vault(self.vault_file)
                progress_dialog.destroy()
                
                if success:
                    messagebox.showinfo("Éxito", "Sincronización completada")
                else:
                    messagebox.showwarning("Advertencia", "No se pudo sincronizar, usando versión local")
                
                self.vault_data, self.vault_key = load_or_create_vault(self.vault_file, password)
                self.master_password = password
                self.update_activity()
                self.setup_main_screen()
                
            except Exception as e:
                progress_dialog.destroy()
                messagebox.showerror("Error", f"Error durante la sincronización: {str(e)}")
        
        threading.Thread(target=sync_thread, daemon=True).start()
        
    def setup_main_screen(self):
        """Configura la pantalla principal del gestor"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header superior
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(header_frame, text="🔐 Mi Bóveda Profesional", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(side="left", padx=10, pady=10)
        
        # Estados de sincronización y seguridad
        status_frame = ctk.CTkFrame(header_frame)
        status_frame.pack(side="left", padx=20)
        
        self.sync_status_label = ctk.CTkLabel(status_frame, text="", font=ctk.CTkFont(size=12))
        self.sync_status_label.pack(pady=2)
        
        self.security_status_label = ctk.CTkLabel(status_frame, text="", font=ctk.CTkFont(size=12))
        self.security_status_label.pack(pady=2)
        
        # Botones de acción principales
        button_frame = ctk.CTkFrame(header_frame)
        button_frame.pack(side="right", padx=10, pady=10)
        
        add_button = ctk.CTkButton(button_frame, text="➕ Agregar", command=self.add_entry)
        add_button.pack(side="left", padx=5)
        
        audit_button = ctk.CTkButton(button_frame, text="🛡️ Auditoría", command=self.run_security_audit)
        audit_button.pack(side="left", padx=5)
        
        sync_button = ctk.CTkButton(button_frame, text="☁️ Sincronizar", command=self.manual_sync)
        sync_button.pack(side="left", padx=5)
        
        settings_button = ctk.CTkButton(button_frame, text="⚙️ Configuración", command=self.show_settings)
        settings_button.pack(side="left", padx=5)
        
        logout_button = ctk.CTkButton(button_frame, text="🚪 Salir", command=self.logout)
        logout_button.pack(side="left", padx=5)
        
        # Frame para la lista de entradas
        self.entries_frame = ctk.CTkScrollableFrame(main_frame)
        self.entries_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.refresh_entries_list()
        self.update_sync_status()
        self.update_security_status()
        
    def run_security_audit(self):
        """Ejecuta una auditoría de seguridad completa"""
        self.update_activity()
        
        # Mostrar diálogo de progreso
        progress_dialog = ctk.CTkToplevel(self.root)
        progress_dialog.title("Auditoría de Seguridad")
        progress_dialog.geometry("400x200")
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
        
        progress_label = ctk.CTkLabel(progress_dialog, text="Analizando seguridad de contraseñas...", 
                                     font=ctk.CTkFont(size=14))
        progress_label.pack(pady=30)
        
        progress_bar = ctk.CTkProgressBar(progress_dialog, width=350)
        progress_bar.pack(pady=10)
        progress_bar.set(0.3)
        
        def audit_thread():
            try:
                results = self.security_audit.audit_vault(self.vault_data)
                progress_dialog.destroy()
                self.show_audit_results(results)
                self.update_security_status()
                
            except Exception as e:
                progress_dialog.destroy()
                messagebox.showerror("Error", f"Error durante la auditoría: {str(e)}")
        
        threading.Thread(target=audit_thread, daemon=True).start()
    
    def show_audit_results(self, results):
        """Muestra los resultados de la auditoría en una ventana"""
        audit_window = ctk.CTkToplevel(self.root)
        audit_window.title("Resultados de Auditoría de Seguridad")
        audit_window.geometry("600x500")
        audit_window.transient(self.root)
        
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(audit_window)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(main_frame, text="🛡️ Reporte de Auditoría de Seguridad", 
                                   font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=10)
        
        # Resumen
        summary_frame = ctk.CTkFrame(main_frame)
        summary_frame.pack(fill="x", pady=10)
        
        summary_text = f"""
📊 RESUMEN:
• Total de entradas: {results['total_entries']}
• Contraseñas débiles: {len(results['weak_passwords'])}
• Contraseñas duplicadas: {len(results['duplicate_passwords'])}
• Contraseñas comprometidas: {len(results['breached_passwords'])}
        """
        
        summary_label = ctk.CTkLabel(summary_frame, text=summary_text, 
                                     font=ctk.CTkFont(size=12), justify="left")
        summary_label.pack(pady=10)
        
        # Recomendaciones
        if results['recommendations']:
            rec_frame = ctk.CTkFrame(main_frame)
            rec_frame.pack(fill="x", pady=10)
            
            rec_title = ctk.CTkLabel(rec_frame, text="💡 RECOMENDACIONES:", 
                                     font=ctk.CTkFont(size=14, weight="bold"))
            rec_title.pack(pady=5)
            
            for rec in results['recommendations']:
                rec_label = ctk.CTkLabel(rec_frame, text=f"• {rec}", 
                                         font=ctk.CTkFont(size=11), justify="left")
                rec_label.pack(anchor="w", padx=10)
        
        # Detalles de problemas
        if results['breached_passwords']:
            breach_frame = ctk.CTkFrame(main_frame)
            breach_frame.pack(fill="x", pady=10)
            
            breach_title = ctk.CTkLabel(breach_frame, text="🚨 CONTRASEÑAS COMPROMETIDAS:", 
                                        font=ctk.CTkFont(size=14, weight="bold"), text_color="red")
            breach_title.pack(pady=5)
            
            for breach in results['breached_passwords']:
                breach_label = ctk.CTkLabel(breach_frame, 
                                           text=f"• {breach['title']}: Encontrada {breach['breach_count']} veces", 
                                           font=ctk.CTkFont(size=11), text_color="red")
                breach_label.pack(anchor="w", padx=10)
        
        if results['weak_passwords']:
            weak_frame = ctk.CTkFrame(main_frame)
            weak_frame.pack(fill="x", pady=10)
            
            weak_title = ctk.CTkLabel(weak_frame, text="⚠️ CONTRASEÑAS DÉBILES:", 
                                      font=ctk.CTkFont(size=14, weight="bold"), text_color="orange")
            weak_title.pack(pady=5)
            
            for weak in results['weak_passwords']:
                weak_label = ctk.CTkLabel(weak_frame, 
                                          text=f"• {weak['title']}: {weak['strength']} ({weak['score']}/8)", 
                                          font=ctk.CTkFont(size=11), text_color="orange")
                weak_label.pack(anchor="w", padx=10)
        
        # Botón cerrar
        close_button = ctk.CTkButton(main_frame, text="Cerrar", command=audit_window.destroy)
        close_button.pack(pady=20)
    
    def show_settings(self):
        """Muestra la ventana de configuración"""
        self.update_activity()
        
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Configuración")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        
        # Auto-bloqueo
        auto_lock_frame = ctk.CTkFrame(settings_window)
        auto_lock_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(auto_lock_frame, text="⏰ Auto-bloqueo", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        lock_config_frame = ctk.CTkFrame(auto_lock_frame)
        lock_config_frame.pack(pady=10)
        
        ctk.CTkLabel(lock_config_frame, text="Minutos de inactividad:").pack(side="left", padx=10)
        
        lock_var = ctk.StringVar(value=str(self.auto_lock_minutes))
        lock_entry = ctk.CTkEntry(lock_config_frame, textvariable=lock_var, width=60)
        lock_entry.pack(side="left", padx=5)
        
        def save_settings():
            try:
                self.auto_lock_minutes = int(lock_var.get())
                messagebox.showinfo("Configuración", "Configuración guardada correctamente")
                settings_window.destroy()
            except:
                messagebox.showerror("Error", "Valor inválido para auto-bloqueo")
        
        save_button = ctk.CTkButton(settings_window, text="Guardar", command=save_settings)
        save_button.pack(pady=20)
    
    def update_security_status(self):
        """Actualiza el estado de seguridad basado en la última auditoría"""
        if not self.vault_data or not self.vault_data.get("entries"):
            self.security_status_label.configure(text="🛡️ Sin datos para auditar")
            return
        
        # Realizar auditoría rápida (sin verificación de brechas)
        weak_count = 0
        duplicate_passwords = set()
        passwords_seen = set()
        
        for entry in self.vault_data["entries"]:
            password = entry.get("password", "")
            strength = check_password_strength(password)
            
            if strength["score"] < 4:
                weak_count += 1
            
            if password in passwords_seen:
                duplicate_passwords.add(password)
            passwords_seen.add(password)
        
        if weak_count == 0 and len(duplicate_passwords) == 0:
            self.security_status_label.configure(text="🛡️ Seguridad: Excelente", text_color="green")
        elif weak_count > 0 or len(duplicate_passwords) > 0:
            issues = weak_count + len(duplicate_passwords)
            self.security_status_label.configure(text=f"⚠️ Seguridad: {issues} problemas", text_color="orange")
    
    def manual_sync(self):
        """Sincronización manual activada por el usuario"""
        self.update_activity()
        
        def sync_thread():
            try:
                self.sync_status_label.configure(text="🔄 Sincronizando...")
                self.root.update()
                
                self.save_vault()
                success = self.cloud_sync.sync_vault(self.vault_file)
                
                if success:
                    self.vault_data, self.vault_key = load_or_create_vault(self.vault_file, self.master_password)
                    self.refresh_entries_list()
                    self.sync_status_label.configure(text="✅ Sincronizado")
                    messagebox.showinfo("Éxito", "Sincronización completada")
                else:
                    self.sync_status_label.configure(text="❌ Error de sincronización")
                    messagebox.showerror("Error", "No se pudo sincronizar con la nube")
                    
            except Exception as e:
                self.sync_status_label.configure(text="❌ Error de sincronización")
                messagebox.showerror("Error", f"Error durante la sincronización: {str(e)}")
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def update_sync_status(self):
        """Actualiza el estado de sincronización"""
        # Construir la ruta de la copia en la nube
        cloud_path = os.path.join(self.cloud_sync.cloud_folder, self.cloud_sync.vault_filename or os.path.basename(self.vault_file))
        
        if os.path.exists(cloud_path) and os.path.exists(self.vault_file):
            cloud_time = os.path.getmtime(cloud_path)
            local_time = os.path.getmtime(self.vault_file)
            
            if abs(cloud_time - local_time) < 1:
                self.sync_status_label.configure(text="✅ Sincronizado")
            elif cloud_time > local_time:
                self.sync_status_label.configure(text="⬇️ Actualización disponible")
            else:
                self.sync_status_label.configure(text="⬆️ Cambios pendientes")
        elif os.path.exists(cloud_path):
            self.sync_status_label.configure(text="⬇️ Versión en nube disponible")
        else:
            self.sync_status_label.configure(text="☁️ No sincronizado")
    
    def refresh_entries_list(self):
        """Actualiza la lista de entradas en la interfaz"""
        # Limpiar frame
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
            
        if not self.vault_data["entries"]:
            empty_label = ctk.CTkLabel(self.entries_frame, 
                                      text="No hay contraseñas guardadas.\n¡Agrega tu primera entrada!", 
                                      font=ctk.CTkFont(size=16))
            empty_label.pack(pady=50)
            return
            
        # Crear entradas
        for i, entry in enumerate(self.vault_data["entries"]):
            entry_frame = ctk.CTkFrame(self.entries_frame)
            entry_frame.pack(fill="x", padx=5, pady=5)
            
            # Información de la entrada
            info_frame = ctk.CTkFrame(entry_frame)
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            title_label = ctk.CTkLabel(info_frame, text=entry["title"], 
                                       font=ctk.CTkFont(size=16, weight="bold"))
            title_label.pack(anchor="w")
            
            username_label = ctk.CTkLabel(info_frame, text=f"Usuario: {entry['username']}", 
                                           font=ctk.CTkFont(size=12))
            username_label.pack(anchor="w")
            
            # Mostrar fortaleza de la contraseña
            strength = check_password_strength(entry["password"])
            strength_color = {"Muy Fuerte": "green", "Fuerte": "blue", "Moderada": "orange", "Débil": "red"}
            strength_label = ctk.CTkLabel(info_frame, 
                                           text=f"Fortaleza: {strength['strength']} ({strength['score']}/8)", 
                                           font=ctk.CTkFont(size=10),
                                           text_color=strength_color.get(strength['strength'], "gray"))
            strength_label.pack(anchor="w")
            
            # Botones de acción
            action_frame = ctk.CTkFrame(entry_frame)
            action_frame.pack(side="right", padx=10, pady=10)
            
            copy_button = ctk.CTkButton(action_frame, text="📋 Copiar", width=80,
                                           command=lambda idx=i: self.copy_password_secure(idx))
            copy_button.pack(side="top", pady=2)
            
            view_button = ctk.CTkButton(action_frame, text="👁️ Ver", width=80,
                                           command=lambda idx=i: self.view_password(idx))
            view_button.pack(side="top", pady=2)
            
            edit_button = ctk.CTkButton(action_frame, text="✏️ Editar", width=80,
                                           command=lambda idx=i: self.edit_entry(idx))
            edit_button.pack(side="top", pady=2)
            
            delete_button = ctk.CTkButton(action_frame, text="🗑️ Eliminar", width=80,
                                             command=lambda idx=i: self.delete_entry(idx))
            delete_button.pack(side="top", pady=2)
    
    def copy_password_secure(self, index):
        """Copia la contraseña de forma segura con auto-limpieza"""
        self.update_activity()
        password = self.vault_data["entries"][index]["password"]
        
        # Intentar copia segura, si falla usar método básico
        if hasattr(self.secure_clipboard, 'copy'):
            try:
                self.secure_clipboard.copy(password)
                messagebox.showinfo("Copiado", "Contraseña copiada al portapapeles.\nSe limpiará automáticamente en 30 segundos.")
                return
            except Exception:
                pass
        # Fallback a método básico
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        messagebox.showinfo("Copiado", "Contraseña copiada al portapapeles")
    
    def add_entry(self):
        """Abre el diálogo para agregar una nueva entrada"""
        self.update_activity()
        self.entry_dialog()
        
    def edit_entry(self, index):
        """Edita la entrada especificada"""
        self.update_activity()
        self.entry_dialog(edit_index=index)
        
    def delete_entry(self, index):
        """Elimina la entrada especificada"""
        self.update_activity()
        entry = self.vault_data["entries"][index]
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar '{entry['title']}'?"):
            del self.vault_data["entries"][index]
            self.save_vault()
            self.refresh_entries_list()
            self.update_sync_status()
            self.update_security_status()
        
    def entry_dialog(self, edit_index=None):
        """Diálogo para agregar/editar entradas"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Agregar Entrada" if edit_index is None else "Editar Entrada")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Datos existentes si estamos editando
        existing_data = self.vault_data["entries"][edit_index] if edit_index is not None else {}
        
        # Campos del formulario
        ctk.CTkLabel(dialog, text="Título:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        title_entry = ctk.CTkEntry(dialog, width=400)
        title_entry.pack(pady=5)
        title_entry.insert(0, existing_data.get("title", ""))
        
        ctk.CTkLabel(dialog, text="Usuario/Email:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        username_entry = ctk.CTkEntry(dialog, width=400)
        username_entry.pack(pady=5)
        username_entry.insert(0, existing_data.get("username", ""))
        
        ctk.CTkLabel(dialog, text="Contraseña:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        password_frame = ctk.CTkFrame(dialog)
        password_frame.pack(pady=5)
        
        password_entry = ctk.CTkEntry(password_frame, width=300, show="*")
        password_entry.pack(side="left", padx=5)
        password_entry.insert(0, existing_data.get("password", ""))
        
        # Indicador de fortaleza
        strength_label = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=12))
        strength_label.pack(pady=5)
        
        def generate_and_update():
            new_password = generate_password(16, True, True, True, True)
            password_entry.delete(0, tk.END)
            password_entry.insert(0, new_password)
            update_strength()
        
        generate_button = ctk.CTkButton(password_frame, text="🎲 Generar", width=80,
                                           command=generate_and_update)
        generate_button.pack(side="left", padx=5)
        
        # Actualizar fortaleza cuando cambie la contraseña
        def update_strength(*args):
            pwd = password_entry.get()
            if pwd:
                st = check_password_strength(pwd)
                strength_color = {"Muy Fuerte": "green", "Fuerte": "blue", "Moderada": "orange", "Débil": "red"}
                strength_label.configure(text=f"Fortaleza: {st['strength']} ({st['score']}/8)",
                                         text_color=strength_color.get(st['strength'], "gray"))
            else:
                strength_label.configure(text="")
        
        password_entry.bind('<KeyRelease>', update_strength)
        update_strength()
        
        # Botones de acción
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        
        def save_entry_action():
            title = title_entry.get().strip()
            username = username_entry.get().strip()
            pwd = password_entry.get().strip()
            
            if not title or not username or not pwd:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
                
            entry_data = {
                "title": title,
                "username": username,
                "password": pwd
            }
            
            if edit_index is not None:
                self.vault_data["entries"][edit_index] = entry_data
            else:
                self.vault_data["entries"].append(entry_data)
            
            self.save_vault()
            self.refresh_entries_list()
            self.update_sync_status()
            self.update_security_status()
            dialog.destroy()
        
        save_button = ctk.CTkButton(button_frame, text="💾 Guardar", command=save_entry_action)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(button_frame, text="❌ Cancelar", command=dialog.destroy)
        cancel_button.pack(side="left", padx=10)
        
        title_entry.focus()
    
    def generate_password_for_entry(self, password_entry, strength_label):
        """Genera una contraseña y la coloca en el campo"""
        new_password = generate_password(16, True, True, True, True)
        password_entry.delete(0, tk.END)
        password_entry.insert(0, new_password)
        
        # Actualizar indicador de fortaleza
        strength = check_password_strength(new_password)
        strength_color = {"Muy Fuerte": "green", "Fuerte": "blue", "Moderada": "orange", "Débil": "red"}
        strength_label.configure(text=f"Fortaleza: {strength['strength']} ({strength['score']}/8)",
                                 text_color=strength_color.get(strength['strength'], "gray"))
    
    def save_entry(self, dialog, title_entry, username_entry, password_entry, edit_index):
        """Guarda la entrada en la bóveda"""
        title = title_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not title or not username or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
            
        entry_data = {
            "title": title,
            "username": username,
            "password": password
        }
        
        if edit_index is not None:
            self.vault_data["entries"][edit_index] = entry_data
        else:
            self.vault_data["entries"].append(entry_data)
            
        self.save_vault()
        self.refresh_entries_list()
        self.update_sync_status()
        self.update_security_status()
        dialog.destroy()
        
    def view_password(self, index):
        """Muestra la contraseña en un diálogo"""
        self.update_activity()
        entry = self.vault_data["entries"][index]
        strength = check_password_strength(entry["password"])
        
        message = f"Título: {entry['title']}\n"
        message += f"Usuario: {entry['username']}\n"
        message += f"Contraseña: {entry['password']}\n\n"
        message += f"Fortaleza: {strength['strength']} ({strength['score']}/8)"
        if strength['feedback']:
            message += f"\nRecomendaciones: {', '.join(strength['feedback'])}"
        
        messagebox.showinfo("Detalles de la Entrada", message)
        
    def save_vault(self):
        """Guarda la bóveda en el archivo"""
        try:
            save_vault(self.vault_file, self.vault_data, self.vault_key)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la bóveda: {str(e)}")
            
    def logout(self):
        """Cierra sesión y vuelve a la pantalla de login"""
        if self.vault_data is not None:
            if messagebox.askyesno("Sincronizar", "¿Deseas sincronizar tus cambios con la nube antes de salir?"):
                self.manual_sync()
        
        self.vault_data = None
        self.vault_key = None
        self.master_password = None
        self.selected_entry = None
        self.setup_login_screen()
        
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PasswordVaultComplete()
    app.run()