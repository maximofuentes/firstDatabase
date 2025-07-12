
# --- Librerías estándar y de terceros ---
import sqlite3  # Para manejar la base de datos SQLite
import os  # Para operaciones con archivos y sistema
from datetime import datetime  # Para fechas y horas
import tkinter as tk  # Interfaz gráfica
from tkinter import messagebox  # Ventanas emergentes
from tkinter import ttk  # Widgets mejorados de Tkinter

# --- Conexión global a la base de datos ---
db_path = os.path.join(os.path.dirname(__file__), "programa.db")
conn = sqlite3.connect(db_path)
usuario_actual = None  # Usuario logueado actualmente
dinero_actual = 0  # Dinero del usuario actual

# --- Validación para campos numéricos en Tkinter ---
def solo_numeros(texto):
#    solo números en los campos de entrada
    return texto.isdigit() or texto == ""
#* FUNCIONES PRIMARIAS --------------------------------
def NuevoUsuario(nombre, password, password2):
    # Crea un nuevo usuario en la base de datos si los datos son válidos.
    if len(nombre) < 5:
        msg = "El nombre debe ser mayor a 5"
        return (False, msg)
    if password != password2:
        msg ="Las passwords no coinciden"
        return (False, msg)
    if len(password) < 5:
        msg = "La password debe ser mayor a 5"
        return (False, msg)

    try:
        with conn:  # Esto maneja automáticamente commit o rollback
            cursor = conn.cursor()

            # Buscar si ya existe
            cursor.execute("SELECT * FROM Users WHERE UserID= ?", (nombre,))
            if cursor.fetchone():
                msg = "El usuario ya existe."
                return (False, msg)

            # Insertar nuevo usuario
            cursor.execute("INSERT INTO Users (UserID, Password) VALUES (?, ?)", (nombre, password))
            msg = "Usuario creado con éxito."
            return (True, msg)

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
def IniciarSesion(nombre,password):
    """Verifica usuario y contraseña, inicia sesión si son correctos."""
    global usuario_actual
    if len(nombre) < 5:
        print("El nombre debe ser mayor a 5")
        msg = "El nombre debe ser mayor a 5"
        return (False,msg)
    if len(password) < 5:
        print("La password debe ser mayor a 5")
        msg = "La password debe ser mayor a 5"
        return (False,msg)
    try:
        with conn:  # Esto maneja automáticamente commit o rollback
            cursor = conn.cursor()

            # Buscar si existe
            cursor.execute("SELECT * FROM Users WHERE UserID = ? AND Password = ?", (nombre,password))
            if cursor.fetchone():
                if usuario_actual == nombre:
                    print("Ya has iniciado sesion.")
                    msg = "Ya has iniciado sesion."
                    return (False,msg)
                else:
                    if usuario_actual != None:
                        CerrarSesion()
                    print("Sesion Iniciada con Exito.")
                    msg = "Sesion Iniciada con Exito."
                    usuario_actual = nombre
                    GuardarUsuario(nombre)
                    Dinero()
                    return (True,msg)
            else:
                print("Nombre de usuario o password incorrectos.")
                msg = "Nombre de usuario o password incorrectos."
                return (False,msg)
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
def GuardarUsuario(nombre):
    """Guarda el usuario actual en un archivo para persistencia de sesión."""
    with open("usuario_actual.txt","w") as f:
        f.write(nombre)
def CargarUsuario():
    """Carga el usuario guardado en archivo, si existe."""
    try:
        with open("usuario_actual.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
def CerrarSesion():
    """Cierra la sesión del usuario actual y elimina el archivo de sesión."""
    global usuario_actual
    usuario_actual = None
    if os.path.exists("usuario_actual.txt"):
        os.remove("usuario_actual.txt")
    print("Sesión cerrada.")
def Transferencia(cantidad,destinatario):
    """Transfiere dinero a otro usuario, validando fondos y existencia."""
    if cantidad < 0:
        return
    global usuario_actual
    if destinatario == usuario_actual:
        print("No puedes mandarte dinero a ti mismo.")
        msg = "No puedes mandarte dinero a ti mismo."
        return (False,msg)
    try:
        with conn:  # Esto maneja automáticamente commit o rollback
            cursor = conn.cursor()

            # Buscar si existe
            cursor.execute("SELECT money FROM Users WHERE UserID = ?", (usuario_actual,))
            if cursor.fetchone()[0] < cantidad:
                print("No tienes dinero suficiente.")
                msg = "No tienes dinero suficiente."
                return (False,msg)
            cursor.execute("SELECT * FROM Users WHERE UserID = ?",(destinatario,))
            if cursor.fetchone() is None:
                print("El destinatario no existe.")
                msg = "El destinatario no existe."
                return (False,msg)
            ahora = datetime.now()
            fecha = ahora.strftime("%d/%m/%Y")
            cursor.execute("UPDATE Users SET money = money + ? WHERE UserID = ?",(cantidad,destinatario,))
            cursor.execute("UPDATE Users SET money = money - ? WHERE UserID = ?",(cantidad,usuario_actual))
            cursor.execute("INSERT INTO Transactions(SenderID,RecieverID,Amount,TransactionDate) VALUES (?,?,?,?)",(usuario_actual,destinatario,cantidad,fecha))
            transaction_id = cursor.lastrowid
            print(f'''
                Transferencia Exitosa \r
                Fecha: {fecha} \r
                ---------------------------- \r
                Usuario: {usuario_actual} \r
                Destinatario: {destinatario} \r
                Monto Enviado: ${cantidad} \r
                ID Transferencia: {transaction_id}''')
            msg = f'''
                Transferencia Exitosa \r
                Fecha: {fecha} \r
                ---------------------------- \r
                Usuario: {usuario_actual} \r
                Destinatario: {destinatario} \r
                Monto Enviado: ${cantidad} \r
                ID Transferencia: {transaction_id}'''
            return True, msg


                
               
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
def TransferenciaInterna(cursor, cantidad, destinatario):
    """Transfiere dinero entre usuarios dentro de una transacción SQL abierta."""
    global usuario_actual
    if cantidad < 0 or destinatario == usuario_actual:
        raise ValueError("Transferencia inválida.")

    cursor.execute("SELECT money FROM Users WHERE UserID = ?", (usuario_actual,))
    if cursor.fetchone()[0] < cantidad:
        raise ValueError("Fondos insuficientes.")
    
    cursor.execute("SELECT * FROM Users WHERE UserID = ?", (destinatario,))
    if cursor.fetchone() is None:
        raise ValueError("El destinatario no existe.")
    
    ahora = datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    
    cursor.execute("UPDATE Users SET money = money + ? WHERE UserID = ?", (cantidad, destinatario))
    cursor.execute("UPDATE Users SET money = money - ? WHERE UserID = ?", (cantidad, usuario_actual))
    cursor.execute("INSERT INTO Transactions(SenderID, RecieverID, Amount, TransactionDate) VALUES (?, ?, ?, ?)",
                   (usuario_actual, destinatario, cantidad, fecha))
    
    return cursor.lastrowid, fecha
def Vender(producto,cantidad,precio):
    """Pone a la venta un producto del inventario del usuario actual."""
    if producto < 0 or cantidad < 0 or precio < 0:
        return
    try:
        with conn:  
            cursor = conn.cursor()
            cursor.execute("SELECT Amount FROM Inventory WHERE UserID = ? AND ProductID = ?",(usuario_actual,producto,))
            
            result = cursor.fetchone()
            print(result)
            if result:
                
                amount = result[0]
                if amount < cantidad:
                    msg = "No posees la cantidad indicada."
                    return (False,msg)
                cursor.execute("INSERT INTO Sellings(UserID,ProductID,Amount,Price) VALUES (?,?,?,?)",(usuario_actual,producto,cantidad,precio,))
                if amount == cantidad:
                    cursor.execute("DELETE FROM Inventory WHERE ProductID = ?",(producto,))
                    
                else:
                    cursor.execute("UPDATE Inventory SET Amount = Amount - ? WHERE ProductID = ?",(cantidad, producto,))
                msg = "Producto puesto en venta con Exito."
                return (True,msg)
            else:
                msg = "No posees este Articulo."
                return (False,msg)     
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
def Comprar(sellingID,cantidad):
    """Permite comprar un producto en venta, actualizando inventario y fondos."""
    if sellingID < 0 or cantidad < 0:
        msg = "Error"
        return (False,msg)
    try:
        with conn:  
            cursor = conn.cursor()
            cursor.execute('''SELECT Amount,? * s.Price, s.ProductID, UserID, ProductName FROM Sellings s 
                           JOIN Products p ON s.ProductID = p.ProductID 
                           WHERE SellingID = ?''',(cantidad,sellingID))    
            result = cursor.fetchone()
            if result:
                max = result[0]
                if cantidad > max:
                    msg = "No hay tantas unidades a la venta."
                    return (False,msg)
                value = result[1]
                producto = result[2]
                vendedor = result[3]
                nombreProducto = result[4]
                cursor.execute("SELECT * FROM Inventory WHERE ProductID = ? AND UserID = ?",(producto,usuario_actual,))
                if cursor.fetchone():
                    cursor.execute("UPDATE Inventory SET Amount = Amount + ? WHERE ProductID = ?",(cantidad,producto))
                else:
                    cursor.execute("INSERT INTO Inventory(UserID,ProductID,Amount) VALUES (?,?,?)",(usuario_actual,producto,cantidad))
                transaction_id = TransferenciaInterna(cursor,value,vendedor)
                if cantidad < max:
                    cursor.execute("UPDATE Sellings SET Amount = Amount - ? WHERE SellingID = ?",(cantidad,sellingID))
                else:
                    cursor.execute("DELETE FROM Sellings WHERE SellingID = ?",(sellingID,))

                cursor.execute("INSERT INTO Purchases(TransactionID,ProductID,Amount) VALUES (?,?,?)",(transaction_id[0],producto,cantidad))
                id_compra = cursor.lastrowid
                msg = f'''Gracias por tu compra! \r
                    Fecha: {transaction_id[1]} \r
                    --------------------------- \r  
                    Vendedor: {vendedor} \r
                    Comprador: {usuario_actual} \r
                    Has comprado {cantidad} {nombreProducto} \r
                    Monto Debitado: {value} \r
                    ID Transaccion: {transaction_id[0]} \r
                    ID Compra: {id_compra}'''
                return (True,msg)
            else:
                msg = "No existe esta publicacion"
                return (False,msg)



    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
def Dinero():
    """Devuelve el dinero actual del usuario logueado."""
    global dinero_actual
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Money FROM Users WHERE UserID = ?",(usuario_actual,))
            dinero_actual = cursor.fetchone()[0]
            return dinero_actual
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
def Inventario():
    """Devuelve el inventario (nombres y IDs) del usuario actual."""
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT ProductName, i.ProductID From Inventory i 
                           JOIN Products p ON i.ProductID = p.ProductID
                           WHERE UserID = ?''',(usuario_actual,))
            inv = cursor.fetchall()
            lista = []
            ides = []
            for i in inv:
                lista.append(i[0])
                ides.append(i[1])
            
            return (lista,ides)
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
def Ventas():
    """Devuelve la lista de productos en venta (nombre, cantidad, precio, vendedor, ID)."""
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT ProductName, Amount, s.Price, s.UserID, SellingID From Sellings s
                           JOIN Products p ON s.ProductID = p.ProductID''')
            sell = cursor.fetchall()
            return sell
    except sqlite3.error as e:
        print(f"Error en la base de datos: {e}")
#! FUNCIONES TK ------------------------
def newUser(ventana_register,entrada_usuario,entrada_password,entrada_password2):
    """Lógica para registrar un nuevo usuario desde la ventana de registro."""
    nombre = entrada_usuario.get()
    password = entrada_password.get()
    password2 = entrada_password2.get()
    booler = NuevoUsuario(nombre,password,password2)
    if booler[0]:
        messagebox.showinfo("Exito",booler[1])
        toWindow(ventana_register,"login")
    else:
        messagebox.showerror("Error",booler[1])

def login(entrada_usuario,entrada_password,ventana_login):
    """Lógica para iniciar sesión desde la ventana de login."""

    nombre = entrada_usuario.get()
    password = entrada_password.get()
    booler = IniciarSesion(nombre,password)
    if booler[0]:
        messagebox.showinfo("Exito",booler[1])
        toWindow(ventana_login,"mainMenu")
    else:
        messagebox.showerror("Error",booler[1])
def logout(ventana):
    """Cierra sesión y vuelve a la ventana de login."""
    CerrarSesion()
    toWindow(ventana,"login")
def transfer(entrada_usuario,entrada_monto,ventana):
    """Lógica para transferir dinero desde la ventana de transferencias."""
    usuario = entrada_usuario.get()
    monto = int(entrada_monto.get())
    booler = Transferencia(monto,usuario)
    if booler[0]:
        messagebox.showinfo("Transferencia Exitosa",booler[1])
        toWindow(ventana, "mainMenu")
    else:
        messagebox.showerror("Error",booler[1])
def toWindow(ventana_actual,ventana_siguiente):
    """Cambia entre ventanas principales de la aplicación."""
    ventana_actual.destroy()
    if ventana_siguiente == "mainMenu":
        ventana_menu_principal()
    elif ventana_siguiente == "login":
        ventana_login()
    elif ventana_siguiente == "TransferMenu":
        ventana_transferir()
    elif ventana_siguiente == "SellingMenu":
        ventana_vender()
    elif ventana_siguiente == "BuyingMenu":
        ventana_comprar()
    elif ventana_siguiente == "register":
        ventana_register()
def sell(seleccion,cantidad,precio,ventana):
    """Lógica para poner un producto en venta desde la ventana de venta."""
    inv = Inventario()
    item = seleccion.get()
    indexItem = inv[0].index(item)
    print(inv)
    print(item)
    print(indexItem)
    producto = inv[1][indexItem]
    amount = int(cantidad.get())
    price = int(precio.get())
    booler = Vender(producto,amount,price)
    if booler[0]:
        messagebox.showinfo("Venta Exitosa",booler[1])
        toWindow(ventana,"mainMenu")
    else:
        messagebox.showerror("Venta Fallida",booler[1])
def buy(ventana,sellingID,cantidad):
    """Lógica para comprar un producto desde la ventana de compra."""
    booler = Comprar(sellingID, cantidad)
    if booler[0]:
        messagebox.showinfo("Compra Exitosa",booler[1])
        toWindow(ventana,"mainMenu")
    else:
        messagebox.showerror("Compra Fallida",booler[1])

#? VENTANASS TKINTER ----------------------------
def ventana_login():
    """Crea y muestra la ventana de inicio de sesión."""
    ventana_login = tk.Tk()
    ventana_login.title("Iniciar Sesión")
    ventana_login.geometry("350x200")

    frame = ttk.Frame(ventana_login, padding=20)
    frame.pack(expand=True)

    ttk.Label(frame, text="Usuario:").grid(row=0, column=0, sticky="e", pady=5)
    entrada_usuario = ttk.Entry(frame, width=25)
    entrada_usuario.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, sticky="e", pady=5)
    entrada_password = ttk.Entry(frame, show="*", width=25)
    entrada_password.grid(row=1, column=1, pady=5)

    ttk.Button(frame, text="Iniciar sesión", command=lambda: login(entrada_usuario, entrada_password, ventana_login)).grid(row=2, column=0, columnspan=2)
    ttk.Button(frame,text="Registrarse", command=lambda: toWindow(ventana_login, "register")).grid(row=3, column=0, columnspan=2, pady=5)

    ventana_login.mainloop()
def ventana_menu_principal():
    """Crea y muestra la ventana principal del menú de usuario."""
    ventana = tk.Tk()
    ventana.title("Menú Principal")
    ventana.geometry("350x250")

    frame = ttk.Frame(ventana, padding=20)
    frame.pack(expand=True)

    ttk.Label(frame, text=f"Usuario: {usuario_actual}", font=("Segoe UI", 11)).grid(row=0, column=0, columnspan=2, pady=5)
    ttk.Label(frame, text=f"Dinero: ${Dinero()}", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, columnspan=2, pady=5)

    botones = [
        ("Transferir", "TransferMenu"),
        ("Vender", "SellingMenu"),
        ("Comprar", "BuyingMenu"),
        ("Cerrar Sesión", "login")
    ]

    for i, (texto, destino) in enumerate(botones, start=2):
        cmd = lambda d=destino: logout(ventana) if d == "login" else toWindow(ventana, d)
        ttk.Button(frame, text=texto, width=25, command=cmd).grid(row=i, column=0, columnspan=2, pady=5)

    ventana.mainloop()
def ventana_transferir():
    """Crea y muestra la ventana para transferir dinero a otro usuario."""
    ventanaTr = tk.Tk()
    ventanaTr.title("Transferencia")
    ventanaTr.geometry("350x220")

    vcmd = ventanaTr.register(solo_numeros)

    frame = ttk.Frame(ventanaTr, padding=20)
    frame.pack(expand=True)

    ttk.Label(frame, text="Destinatario:").grid(row=0, column=0, sticky="e", pady=5)
    entrada_usuario = ttk.Entry(frame, width=25)
    entrada_usuario.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Monto:").grid(row=1, column=0, sticky="e", pady=5)
    entrada_monto = ttk.Entry(frame, validate="key", validatecommand=(vcmd, "%P"), width=25)
    entrada_monto.grid(row=1, column=1, pady=5)

    ttk.Button(frame, text="Confirmar", command=lambda: transfer(entrada_usuario, entrada_monto, ventanaTr)).grid(row=2, column=0, columnspan=2, pady=10)
    ttk.Button(frame, text="Atrás", command=lambda: toWindow(ventanaTr, "mainMenu")).grid(row=3, column=0, columnspan=2, pady=5)

    ventanaTr.mainloop()
def ventana_vender():
    """Crea y muestra la ventana para poner productos en venta."""
    ventanaV = tk.Tk()
    ventanaV.title("Poner Producto en Venta")
    ventanaV.geometry("400x250")

    vcmd = ventanaV.register(solo_numeros)

    frame = ttk.Frame(ventanaV, padding=20)
    frame.pack(expand=True, fill="both")

    # Título
    ttk.Label(frame, text="Vender Producto", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Selector de producto
    ttk.Label(frame, text="Producto:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
    opciones = Inventario()  # Debería devolver lista de nombres de productos
    seleccion = ttk.Combobox(frame, values=opciones[0], state="readonly", width=25)
    seleccion.grid(row=1, column=1, pady=5)

    # Cantidad
    ttk.Label(frame, text="Cantidad:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
    entrada_cantidad = ttk.Entry(frame, validate="key", validatecommand=(vcmd, "%P"), width=27)
    entrada_cantidad.grid(row=2, column=1, pady=5)
    ttk.Label(frame, text="Max: 10").grid(row=2, column=2, sticky="e", pady=5, padx=5)

    # Precio
    ttk.Label(frame, text="Precio por unidad:").grid(row=3, column=0, sticky="e", pady=5, padx=5)
    entrada_precio = ttk.Entry(frame, validate="key", validatecommand=(vcmd, "%P"), width=27)
    entrada_precio.grid(row=3, column=1, pady=5)
    ttk.Button(frame, text="Confirmar", command=lambda: sell(seleccion,entrada_cantidad,entrada_precio,ventanaV)).grid(row=4, column=0, columnspan=2, pady=15)
    ttk.Button(frame, text="Atrás", command=lambda: toWindow(ventanaV, "mainMenu")).grid(row=5, column=0, columnspan=2, pady=5)

    ventanaV.mainloop()
def ventana_comprar():
    """Crea y muestra la ventana para comprar productos en venta."""
    ventanaC = tk.Tk()
    ventanaC.title("Articulos")
    ventanaC.geometry("600x250")

    vcmd = ventanaC.register(solo_numeros)
    columnas = ("Producto","Cantidad","Precio", "Vendedor")
    tree = ttk.Treeview(ventanaC, columns=columnas,show="headings")

    for col in columnas:
        tree.heading(col,text=col)
        tree.column(col, anchor="center",width=120)
    
    datos = Ventas()
    for fila in datos:
        tree.insert("",tk.END, values=fila)
    cantidade = ttk.Entry(ventanaC, width=10, validatecommand=(vcmd, "%P"), validate="key")

    def obtener_seleccion():
        seleccion = tree.selection()
        if seleccion:
            fila = tree.item(seleccion[0])['values']
            producto = fila[0]
            cantidad = fila[1]
            precio = fila[2]
            vendedor = fila[3]
            sellingID = fila[4]
            try:
                amount = int(cantidade.get())
            except ValueError:
                messagebox.showerror("Error", "Ingresa una cantidad válida")
                return
            print("Seleccionado", f"Producto: {producto}\nCantidad: {cantidad}\nPrecio: {precio}\nVendedor: {vendedor}")
            if vendedor == usuario_actual:
                messagebox.showerror("Error","No puedes comprarte a ti mismo")
                return
            buy(ventanaC,sellingID, amount)
        else:
            messagebox.showwarning("Aviso", "No seleccionaste ningún producto.")
    
    tree.pack(expand=True, fill="both")
    ttk.Button(ventanaC, text="Atras", command=lambda:toWindow(ventanaC, "mainMenu")).pack(side="left")
    ttk.Button(ventanaC, text="Comprar", command=lambda:obtener_seleccion()).pack()
    cantidade.pack()
    ventanaC.mainloop()
def ventana_register():
    """Crea y muestra la ventana de registro de nuevos usuarios."""
    ventanaR = tk.Tk()
    ventanaR.title("Registrarse")
    ventanaR.geometry("350x250")

    frame = ttk.Frame(ventanaR, padding=20)
    frame.pack(expand=True)

    ttk.Label(frame, text="Usuario:").grid(row=0, column=0, sticky="e", pady=5)
    entrada_usuario = ttk.Entry(frame, width=25)
    entrada_usuario.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, sticky="e", pady=5)
    entrada_password = ttk.Entry(frame, show="*", width=25)
    entrada_password.grid(row=1, column=1, pady=5)

    ttk.Label(frame, text="Repetir Contraseña:").grid(row=2, column=0, sticky="e", pady=5)
    entrada_password2 = ttk.Entry(frame, show="*", width=25)
    entrada_password2.grid(row=2, column=1, pady=5)

    ttk.Button(frame, text="Registrarse", command=lambda:newUser(ventanaR,entrada_usuario,entrada_password,entrada_password2)).grid(row=3, column=0, columnspan=2, pady=15)
    ttk.Button(frame, text="Atrás", command=lambda: toWindow(ventanaR,"login")).grid(row=4, column=0, columnspan=2, pady=5)

    ventanaR.mainloop()

# --- Inicio de la aplicación ---
usuario_actual = CargarUsuario()  # Carga usuario si hay sesión previa
if usuario_actual == None:
    ventana_login()  # Si no hay usuario, muestra login
else:
    ventana_menu_principal()  # Si hay usuario, muestra menú principal




# --- Cierra la conexión a la base de datos al finalizar ---
conn.close()