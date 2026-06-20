import json
import requests


# CLASE 1: PRODUCTO
# Representa cada artículo individual dentro de la máquina expendedora

class Producto:
    def __init__(self, codigo, nombre, precio, stock):
        self._codigo = codigo  # Guarda la coordenada (ej: A1) o código de 5 letras
        self._nombre = nombre  # Nombre del producto
        self._precio = float(precio)  # Precio decimal del producto
        self._stock = int(stock)  # Unidades disponibles en la máquina

    # Métodos Getter para acceder a los atributos privados
    def get_codigo(self):
        return self._codigo

    def get_nombre(self):
        return self._nombre

    def get_precio(self):
        return self._precio

    def get_stock(self):
        return self._stock

    # Reduce en 1 el inventario cuando se realiza una venta exitosa
    def reducir_stock(self, cantidad):
        if self._stock >= cantidad:
            self._stock -= cantidad
            return True
        return False

    # Incrementa las unidades del producto (Módulo de Restock)
    def aumentar_stock(self, cantidad):
        self._stock += cantidad

    # Permite reemplazar por completo un producto en una coordenada
    def cambiar_producto(self, nuevo_nombre, nuevo_precio, nuevo_stock):
        self._nombre = nuevo_nombre
        self._precio = float(nuevo_precio)
        self._stock = int(nuevo_stock)


# CLASE 2: INVENTARIO
# Controla la colección de productos y la conexión con el servidor remoto

class Inventario:
    def __init__(self, url_github):
        self._lista_productos = {}  # Diccionario principal donde se guardan los objetos Producto
        self._url_github = url_github  # Enlace al archivo JSON remoto
        # Datos de respaldo local 
        self._datos_locales_respaldo = {
            "A1": {"nombre": "CocaC", "precio": 1.50, "stock": 5},
            "B1": {"nombre": "Pepsi", "precio": 1.50, "stock": 4},
            "C1": {"nombre": "Fanta", "precio": 1.25, "stock": 3},
            "D1": {"nombre": "Malta", "precio": 2.00, "stock": 6},
            "A2": {"nombre": "Chint", "precio": 1.80, "stock": 2}
        }

    # MÓDULO 1: Descarga y sincroniza los datos desde la URL de GitHub
    def cargar_desde_github(self):
        try:
            respuesta = requests.get(self._url_github)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                # Instanciamos cada producto del JSON en la clase Producto
                for cod, info in datos.items():
                    self._lista_productos[cod] = Producto(cod, info["nombre"], info["precio"], info["stock"])
                print("-> ¡Catálogo sincronizado desde GitHub!")
            else:
                self._cargar_respaldo_local()
        except Exception:
            self._cargar_respaldo_local()

    # Carga la base de datos simulada si no hay conexión
    def _cargar_respaldo_local(self):
        print("Cargando inventario local de respaldo.")
        for cod, info in self._datos_locales_respaldo.items():
            self._lista_productos[cod] = Producto(cod, info["nombre"], info["precio"], info["stock"])

    # Retorna el objeto Producto correspondiente a la coordenada ingresada
    def buscar_producto(self, codigo):
        return self._lista_productos.get(codigo, None)

    # Retorna todo el diccionario de mercancía
    def obtener_catalogo(self):
        return self._lista_productos

    # Maneja la inserción o actualización de productos desde el Restock
    def agregar_o_modificar_producto(self, codigo, nombre, precio, stock):
        if codigo in self._lista_productos:
            self._lista_productos[codigo].cambiar_producto(nombre, precio, stock)
        else:
            self._lista_productos[codigo] = Producto(codigo, nombre, precio, stock)

# CLASE 3: TRANSACCION
# Gestiona el pago seguro con tarjeta y el procesamiento de la compra

class Transaccion:
    # Base de datos segura 
    _tarjetas_validas = {
        "1234567890": 10.0,
        "9876543210": 20.0,
        "1223334444": 5.0,
        "4444333221": 50.0,
        "1010101010": 1.0
    }

    def __init__(self, id_transaccion, producto_seleccionado, numero_tarjeta):
        self._id_transaccion = id_transaccion  # Identificador secuencial de la operación
        self._producto_seleccionado = producto_seleccionado  # Objeto Producto que se desea adquirir
        self._numero_tarjeta = str(numero_tarjeta).strip()  # Cadena de la tarjeta ingresada

    # Valida la tarjeta usando la función hash()
    def verificar_pago(self):
        hash_ingresado = hash(self._numero_tarjeta)

        for tarjeta_real, saldo in Transaccion._tarjetas_validas.items():
            # Se compara el hash generado en lugar del número en texto plano 
            if hash(tarjeta_real) == hash_ingresado:
                if saldo >= self._producto_seleccionado.get_precio():
                    # Descuento real sobre el saldo almacenado en memoria de la tarjeta
                    Transaccion._tarjetas_validas[tarjeta_real] -= self._producto_seleccionado.get_precio()
                    return True, Transaccion._tarjetas_validas[tarjeta_real]
                else:
                    print("-> Tarjeta sin saldo suficiente.")
                    return False, 0
        
        print("-> Tarjeta no reconocida o inválida.")
        return False, 0

    # Orquestador del flujo de cobro y dispensación física del producto
    def procesar_operacion(self):
        if self._producto_seleccionado.get_stock() <= 0:
            print(f"El producto {self._producto_seleccionado.get_nombre()} se encuentra agotado.")
            return False
        
        es_valida, nuevo_saldo = self.verificar_pago()
        if not es_valida:
            return False

        # Modificación de estado: Reduce el inventario tras confirmar el pago financiero
        self._producto_seleccionado.reducir_stock(1)
        print(f"\n¡VENTA EXITOSA!")
        print(f"Dispensando producto: {self._producto_seleccionado.get_nombre()}")
        print(f"Saldo restante en tarjeta: ${nuevo_saldo:.2f}")
        print("¡Disfrute su producto!")
        return True


# CLASE 4: REPORTE
# Acumula el histórico de auditoría y genera el archivo plano solicitado

class Reporte:
    def __init__(self):
        self._ventas_historicas = []  # Listado de objetos Producto vendidos
        self._total_dinero_cobrado = 0.0  # Caja chica total acumulada
        self._usuarios_unicos = set()  # Set que guarda tarjetas únicas para evitar duplicados

    # Registra cada evento de compra exitosa en las métricas globales
    def registrar_venta(self, producto, tarjeta_usada):
        self._ventas_historicas.append(producto)
        self._total_dinero_cobrado += producto.get_precio()
        self._usuarios_unicos.add(tarjeta_usada)

    # Escribe el archivo de texto estructurado en el disco duro local
    def exportar_txt(self, inventario):
        try:
            with open("reporte_ventas.txt", "w", encoding="utf-8") as archivo:
                archivo.write("REPORTE DE AUDITORÍA MÁQUINA EXPENDEDORA\n\n")
                
                # Reporte del estado actual de existencias físicas
                archivo.write("Estado de Stock por Producto:\n")
                for cod, prod in inventario.obtener_catalogo().items():
                    archivo.write(f" - {prod.get_nombre()} ({cod}): Stock Restante = {prod.get_stock()}\n")
                
                # Métricas e indicadores cuantitativos solicitados en la pauta
                archivo.write(f"\nNúmero total de productos vendidos: {len(self._ventas_historicas)}\n")
                archivo.write(f"Cantidad total de dinero cobrado: ${self._total_dinero_cobrado:.2f}\n")
                archivo.write(f"Número total de usuarios atendidos: {len(self._usuarios_unicos)}\n")
            print(" ¡Reporte 'reporte_ventas.txt' generado con éxito en tu carpeta!")
        except IOError:
            print(" Error al guardar el reporte físico.")


# CLASE 5: MAQUINA EXPENDEDORA
# Controlador principal del sistema 

class MaquinaExpendedora:
    def __init__(self, url_raw_github):
        self._inventario = Inventario(url_raw_github)
        self._manejador_reportes = Reporte()
        self._contador_transacciones = 0

    # Lanza los procesos iniciales del hardware simulado
    def iniciar_sistema(self):
        print("Iniciando componentes del Sistema...")
        self._inventario.cargar_desde_github()
        self.desplegar_menu()

    # MÓDULO 1 VISUAL: Dibuja el catálogo estructurado en forma de matriz de ajedrez
    def _imprimir_matriz_catalogo(self):
        catalogo = self._inventario.obtener_catalogo()
        columnas = ["A", "B", "C", "D", "E"]
        
        print("    A         B         C         D         E")
        for fila in range(1, 6):
            linea_fila = f"{fila} "
            for col in columnas:
                coordenada = f"{col}{fila}"
                prod = catalogo.get(coordenada)
                
                # Si el producto existe y tiene existencias se imprime; si no, queda en blanco
                if prod and prod.get_stock() > 0:
                    linea_fila += f"{prod.get_nombre():<10}"
                else:
                    linea_fila += "          "
            print(linea_fila)
        print("")

    # Ciclo principal de control interactivo con el usuario (CLI)
    def desplegar_menu(self):
        while True:
            self._imprimir_matriz_catalogo()
            print("Comandos disponibles:")
            print(" - Ingrese la coordenada (ej: A1) para realizar una compra")
            print(" - Escriba 'RS' para ingresar al módulo de Restock")
            print(" - Escriba 'RP' para generar el reporte de auditoría")
            print(" - Escriba 'SALIR' para apagar la máquina")
            
            entrada = input("¿Qué desea hacer?: ").strip().upper()

            if entrada == "SALIR":
                print("Apagando sistema operativo... ¡Feliz tarde!")
                break
            elif entrada == "RS":
                self._ejecutar_modulo_restock()
            elif entrada == "RP":
                self._manejador_reportes.exportar_txt(self._inventario)
            else:
                self._ejecutar_modulo_ventas(entrada)

    # MÓDULO 2: Procesa y coordina los pasos de una venta mediante coordenadas
    def _ejecutar_modulo_ventas(self, coordenada):
        prod = self._inventario.buscar_producto(coordenada)
        if not prod:
            print(" Coordenada vacía o producto no asignado.")
            return

        print(f"El precio de {prod.get_nombre()} es ${prod.get_precio():.2f}")
        tarjeta = input("Introduzca su número de tarjeta: ").strip()
        
        if not tarjeta:
            print(" Operación cancelada. Regresando al catálogo.")
            return

        self._contador_transacciones += 1
        venta = Transaccion(str(self._contador_transacciones), prod, tarjeta)
        
        # Si la operación financiera pasa, registramos los datos para la auditoría
        if venta.procesar_operacion():
            self._manejador_reportes.registrar_venta(prod, tarjeta)

    # MÓDULO 3: Panel administrativo para añadir mercancía o reestructurar coordenadas
    def _ejecutar_modulo_restock(self):
        print("MÓDULO DE RESTOCK SELECCIONADO")
        print("1. Actualizar existencia de inventario")
        print("2. Cambiar producto en una coordenada")
        opcion = input("Seleccione una opción: ").strip()

        coordenada = input("Ingrese la coordenada a modificar (ej: E3): ").strip().upper()

        if opcion == "1":
            prod = self._inventario.buscar_producto(coordenada)
            if prod:
                try:
                    cantidad = int(input("Ingrese la cantidad de unidades a añadir: "))
                    prod.aumentar_stock(cantidad)
                    print(" Inventario actualizado.")
                except ValueError:
                    print(" Error: Cantidad inválida.")
            else:
                print(" No hay producto en esa coordenada para actualizar. Use la opción 2.")
                
        elif opcion == "2":
            nombre = input("Ingrese el nombre del nuevo producto: ").strip()
            try:
                precio = float(input("Ingrese el precio: $"))
                stock = int(input("Ingrese el stock inicial: "))
                self._inventario.agregar_o_modificar_producto(coordenada, nombre, precio, stock)
                print(f" Producto {nombre} asignado exitosamente a la coordenada {coordenada}.")
            except ValueError:
                print(" Error: Datos numéricos incorrectos.")



# Configuración de arranque del sistema 
if __name__ == "__main__":
    # URL RAW del archivo de datos JSON 
    URL_GITHUB = "https://raw.githubusercontent.com/lorenzocarmona/maquina-expendedora-unimet/main/inventario.json"
    
    # Encendido e inicialización de la máquina
    maquina = MaquinaExpendedora(URL_GITHUB)
    maquina.iniciar_sistema()
