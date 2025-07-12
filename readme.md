# Sistema Bancario en Python (Tkinter + SQLite)

Este es un sistema bancario con interfaz gráfica desarrollado en **Python** usando **Tkinter** para la interfaz de usuario y **SQLite** como base de datos.  
Permite a los usuarios registrarse, iniciar sesión, transferir dinero, comprar y vender productos.

## 🚀 Funcionalidades principales

- Registro de usuarios.
- Inicio y cierre de sesión con persistencia local.
- Transferencias de dinero entre usuarios.
- Sistema de ventas y compras de productos.
- Inventario personal.
- Interfaz gráfica amigable con **Tkinter**.

## 📋 Requisitos

- Python 3.x
- Librerías incluidas en Python estándar:
  - `sqlite3`
  - `os`
  - `datetime`
  - `tkinter`

## 📂 Estructura del proyecto
sql.py # Archivo principal de la aplicación
programa.db # Base de datos SQLite (se genera automáticamente)
usuario_actual.txt # Archivo para recordar sesión (se genera al iniciar sesión)

## 🏃 Cómo ejecutar

1. Asegúrate de tener Python instalado.
2. Abre una terminal en la carpeta donde esté el archivo `sql.py`.
3. Ejecuta:
```bash
python sql.py
