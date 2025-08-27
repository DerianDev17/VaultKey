from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
import os
import threading
from vault_core import load_or_create_vault, save_vault
from password_generator import generate_password, check_password_strength
from cloud_sync import LocalCloudSync

# Configurar tamaño de ventana para simular móvil
Window.size = (360, 640)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Título
        title = Label(text='🔐 Vault Móvil', font_size=dp(24), size_hint_y=None, height=dp(60))
        layout.add_widget(title)
        
        subtitle = Label(text='Gestor de Contraseñas Seguro', font_size=dp(16), 
                        size_hint_y=None, height=dp(40))
        layout.add_widget(subtitle)
        
        # Espaciador
        layout.add_widget(Label(size_hint_y=None, height=dp(20)))
        
        # Campo de contraseña
        self.password_input = TextInput(
            hint_text='Contraseña maestra',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16)
        )
        layout.add_widget(self.password_input)
        
        # Botones
        btn_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(100))
        
        login_btn = Button(text='🔓 Acceder', size_hint_y=None, height=dp(45), font_size=dp(16))
        login_btn.bind(on_press=self.login)
        btn_layout.add_widget(login_btn)
        
        sync_btn = Button(text='☁️ Sincronizar y Acceder', size_hint_y=None, height=dp(45), font_size=dp(16))
        sync_btn.bind(on_press=self.sync_and_login)
        btn_layout.add_widget(sync_btn)
        
        layout.add_widget(btn_layout)
        
        # Información
        info = Label(text='Si es tu primera vez, se creará\nuna nueva bóveda automáticamente', 
                    font_size=dp(12), size_hint_y=None, height=dp(60))
        layout.add_widget(info)
        
        self.add_widget(layout)
        
    def login(self, instance):
        password = self.password_input.text
        if not password:
            self.show_popup('Error', 'Por favor ingresa tu contraseña maestra')
            return
            
        try:
            app = App.get_running_app()
            app.vault_data, app.vault_key = load_or_create_vault(app.vault_file, password)
            app.master_password = password
            app.root.current = 'main'
            app.root.get_screen('main').refresh_entries()
        except Exception as e:
            self.show_popup('Error', f'Error al acceder: {str(e)}')
    
    def sync_and_login(self, instance):
        password = self.password_input.text
        if not password:
            self.show_popup('Error', 'Por favor ingresa tu contraseña maestra')
            return
        
        # Mostrar popup de sincronización
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_layout.add_widget(Label(text='Sincronizando con la nube...', font_size=dp(16)))
        
        popup = Popup(title='Sincronizando', content=popup_layout, size_hint=(0.8, 0.3))
        popup.open()
        
        def sync_thread():
            try:
                app = App.get_running_app()
                success = app.cloud_sync.sync_vault(app.vault_file)
                
                Clock.schedule_once(lambda dt: popup.dismiss())
                
                if success:
                    Clock.schedule_once(lambda dt: self.show_popup('Éxito', 'Sincronización completada'))
                else:
                    Clock.schedule_once(lambda dt: self.show_popup('Advertencia', 'No se pudo sincronizar'))
                
                app.vault_data, app.vault_key = load_or_create_vault(app.vault_file, password)
                app.master_password = password
                Clock.schedule_once(lambda dt: setattr(app.root, 'current', 'main'))
                Clock.schedule_once(lambda dt: app.root.get_screen('main').refresh_entries())
                
            except Exception as e:
                Clock.schedule_once(lambda dt: popup.dismiss())
                Clock.schedule_once(lambda dt: self.show_popup('Error', f'Error: {str(e)}'))
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_layout.add_widget(Label(text=message, font_size=dp(14)))
        
        close_btn = Button(text='Cerrar', size_hint_y=None, height=dp(40))
        popup_layout.add_widget(close_btn)
        
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(text='🔐 Mi Bóveda', font_size=dp(18), size_hint_x=0.7)
        header.add_widget(title)
        
        sync_btn = Button(text='☁️', size_hint_x=0.15, font_size=dp(16))
        sync_btn.bind(on_press=self.sync_vault)
        header.add_widget(sync_btn)
        
        logout_btn = Button(text='🚪', size_hint_x=0.15, font_size=dp(16))
        logout_btn.bind(on_press=self.logout)
        header.add_widget(logout_btn)
        
        layout.add_widget(header)
        
        # Botón agregar
        add_btn = Button(text='➕ Agregar Nueva Contraseña', size_hint_y=None, height=dp(45), font_size=dp(16))
        add_btn.bind(on_press=self.add_entry)
        layout.add_widget(add_btn)
        
        # Lista de entradas
        self.scroll = ScrollView()
        self.entries_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.entries_layout.bind(minimum_height=self.entries_layout.setter('height'))
        self.scroll.add_widget(self.entries_layout)
        layout.add_widget(self.scroll)
        
        self.add_widget(layout)
        
    def refresh_entries(self):
        self.entries_layout.clear_widgets()
        
        app = App.get_running_app()
        if not app.vault_data or not app.vault_data.get("entries"):
            empty_label = Label(text='No hay contraseñas guardadas.\n¡Agrega tu primera entrada!', 
                              font_size=dp(14), size_hint_y=None, height=dp(100))
            self.entries_layout.add_widget(empty_label)
            return
        
        for i, entry in enumerate(app.vault_data["entries"]):
            entry_widget = self.create_entry_widget(entry, i)
            self.entries_layout.add_widget(entry_widget)
    
    def create_entry_widget(self, entry, index):
        # Container principal
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=dp(5))
        
        # Fondo con borde
        from kivy.graphics import Color, Rectangle, Line
        with container.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Color de fondo
            container.rect = Rectangle(size=container.size, pos=container.pos)
            Color(0.5, 0.5, 0.5, 1)  # Color del borde
            container.line = Line(rectangle=(container.x, container.y, container.width, container.height))
        
        def update_graphics(instance, value):
            container.rect.size = instance.size
            container.rect.pos = instance.pos
            container.line.rectangle = (instance.x, instance.y, instance.width, instance.height)
        
        container.bind(size=update_graphics, pos=update_graphics)
        
        # Layout principal
        main_layout = BoxLayout(orientation='horizontal', padding=dp(10))
        
        # Información
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        title_label = Label(text=entry["title"], font_size=dp(16), halign='left', size_hint_y=0.6)
        title_label.bind(size=title_label.setter('text_size'))
        info_layout.add_widget(title_label)
        
        username_label = Label(text=f"Usuario: {entry['username']}", font_size=dp(12), 
                              halign='left', size_hint_y=0.4)
        username_label.bind(size=username_label.setter('text_size'))
        info_layout.add_widget(username_label)
        
        main_layout.add_widget(info_layout)
        
        # Botones
        btn_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(2))
        
        copy_btn = Button(text='📋', size_hint_y=0.5, font_size=dp(12))
        copy_btn.bind(on_press=lambda x: self.copy_password(index))
        btn_layout.add_widget(copy_btn)
        
        view_btn = Button(text='👁️', size_hint_y=0.5, font_size=dp(12))
        view_btn.bind(on_press=lambda x: self.view_entry(index))
        btn_layout.add_widget(view_btn)
        
        main_layout.add_widget(btn_layout)
        container.add_widget(main_layout)
        
        return container
    
    def add_entry(self, instance):
        app = App.get_running_app()
        app.root.current = 'entry_form'
        app.root.get_screen('entry_form').setup_form()
    
    def copy_password(self, index):
        app = App.get_running_app()
        password = app.vault_data["entries"][index]["password"]
        # En una app real, esto copiaría al portapapeles del sistema
        self.show_popup('Copiado', 'Contraseña copiada al portapapeles')
    
    def view_entry(self, index):
        app = App.get_running_app()
        entry = app.vault_data["entries"][index]
        strength = check_password_strength(entry["password"])
        
        message = f"Título: {entry['title']}\n"
        message += f"Usuario: {entry['username']}\n"
        message += f"Contraseña: {entry['password']}\n\n"
        message += f"Fortaleza: {strength['strength']} ({strength['score']}/8)"
        
        self.show_popup('Detalles', message)
    
    def sync_vault(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_layout.add_widget(Label(text='Sincronizando...', font_size=dp(16)))
        
        popup = Popup(title='Sincronizando', content=popup_layout, size_hint=(0.8, 0.3))
        popup.open()
        
        def sync_thread():
            try:
                app = App.get_running_app()
                success = app.cloud_sync.sync_vault(app.vault_file)
                
                Clock.schedule_once(lambda dt: popup.dismiss())
                
                if success:
                    app.vault_data, app.vault_key = load_or_create_vault(app.vault_file, app.master_password)
                    Clock.schedule_once(lambda dt: self.refresh_entries())
                    Clock.schedule_once(lambda dt: self.show_popup('Éxito', 'Sincronización completada'))
                else:
                    Clock.schedule_once(lambda dt: self.show_popup('Error', 'No se pudo sincronizar'))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: popup.dismiss())
                Clock.schedule_once(lambda dt: self.show_popup('Error', f'Error: {str(e)}'))
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def logout(self, instance):
        app = App.get_running_app()
        app.vault_data = None
        app.vault_key = None
        app.master_password = None
        app.root.current = 'login'
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_layout.add_widget(Label(text=message, font_size=dp(14)))
        
        close_btn = Button(text='Cerrar', size_hint_y=None, height=dp(40))
        popup_layout.add_widget(close_btn)
        
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.6))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class EntryFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'entry_form'
        self.edit_index = None
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        back_btn = Button(text='← Volver', size_hint_x=0.3, font_size=dp(14))
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        self.title_label = Label(text='Agregar Entrada', font_size=dp(18), size_hint_x=0.7)
        header.add_widget(self.title_label)
        
        layout.add_widget(header)
        
        # Formulario
        form_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        form_layout.add_widget(Label(text='Título:', font_size=dp(14), size_hint_y=None, height=dp(30)))
        self.title_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), font_size=dp(16))
        form_layout.add_widget(self.title_input)
        
        form_layout.add_widget(Label(text='Usuario/Email:', font_size=dp(14), size_hint_y=None, height=dp(30)))
        self.username_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), font_size=dp(16))
        form_layout.add_widget(self.username_input)
        
        form_layout.add_widget(Label(text='Contraseña:', font_size=dp(14), size_hint_y=None, height=dp(30)))
        
        password_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        self.password_input = TextInput(multiline=False, password=True, font_size=dp(16))
        password_layout.add_widget(self.password_input)
        
        generate_btn = Button(text='🎲', size_hint_x=None, width=dp(50), font_size=dp(16))
        generate_btn.bind(on_press=self.generate_password)
        password_layout.add_widget(generate_btn)
        
        form_layout.add_widget(password_layout)
        
        # Indicador de fortaleza
        self.strength_label = Label(text='', font_size=dp(12), size_hint_y=None, height=dp(30))
        form_layout.add_widget(self.strength_label)
        
        layout.add_widget(form_layout)
        
        # Botones de acción
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        save_btn = Button(text='💾 Guardar', font_size=dp(16))
        save_btn.bind(on_press=self.save_entry)
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='❌ Cancelar', font_size=dp(16))
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
        
        # Bind para actualizar fortaleza
        self.password_input.bind(text=self.update_strength)
        
    def setup_form(self, edit_index=None):
        self.edit_index = edit_index
        
        if edit_index is not None:
            app = App.get_running_app()
            entry = app.vault_data["entries"][edit_index]
            self.title_label.text = 'Editar Entrada'
            self.title_input.text = entry["title"]
            self.username_input.text = entry["username"]
            self.password_input.text = entry["password"]
        else:
            self.title_label.text = 'Agregar Entrada'
            self.title_input.text = ''
            self.username_input.text = ''
            self.password_input.text = ''
        
        self.update_strength()
    
    def generate_password(self, instance):
        new_password = generate_password(16, True, True, True, True)
        self.password_input.text = new_password
        self.update_strength()
    
    def update_strength(self, instance=None, value=None):
        password = self.password_input.text
        if password:
            strength = check_password_strength(password)
            self.strength_label.text = f"Fortaleza: {strength['strength']} ({strength['score']}/8)"
        else:
            self.strength_label.text = ''
    
    def save_entry(self, instance):
        title = self.title_input.text.strip()
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not title or not username or not password:
            self.show_popup('Error', 'Todos los campos son obligatorios')
            return
        
        app = App.get_running_app()
        entry_data = {
            "title": title,
            "username": username,
            "password": password
        }
        
        if self.edit_index is not None:
            app.vault_data["entries"][self.edit_index] = entry_data
        else:
            app.vault_data["entries"].append(entry_data)
        
        save_vault(app.vault_file, app.vault_data, app.vault_key)
        app.root.current = 'main'
        app.root.get_screen('main').refresh_entries()
    
    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_layout.add_widget(Label(text=message, font_size=dp(14)))
        
        close_btn = Button(text='Cerrar', size_hint_y=None, height=dp(40))
        popup_layout.add_widget(close_btn)
        
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class MobileVaultApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vault_data = None
        self.vault_key = None
        self.vault_file = "mobile_vault.json"
        self.master_password = None
        self.cloud_sync = LocalCloudSync("mobile_cloud")
    
    def build(self):
        sm = ScreenManager()
        
        sm.add_widget(LoginScreen())
        sm.add_widget(MainScreen())
        sm.add_widget(EntryFormScreen())
        
        return sm


if __name__ == '__main__':
    MobileVaultApp().run()