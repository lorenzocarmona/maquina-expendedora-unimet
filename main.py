import json
import requests

class Producto:
    def __init__(self, codigo, nombre, precio, stock):
        self._codigo = codigo  # Coordenada o código de 5 letras
        self._nombre = nombre
        self._precio = float(precio)
        self._stock = int(stock)

    def get_codigo(self):
        return self._codigo

    def get_nombre(self):
        return self._nombre

    def get_precio(self):
        return self._precio

    def get_stock(self):
        return self._stock

    def reducir_stock(self, cantidad):
        if self._stock >= cantidad:
            self._stock -= cantidad
            return True
        return False

    def aumentar_stock(self, cantidad):
        self._stock += cantidad

    def cambiar_producto(self, nuevo_nombre, nuevo_precio, nuevo_stock):
        self._nombre = nuevo_nombre
        self._precio = float(nuevo_precio)
        self._stock = int(nuevo_stock)


class Inventario:
    def __init__(self, url_github):
        self._lista_productos = {}
        self._url_github = url_github
        # Diccionario local simulado por si falla la conexión a internet
        self._datos_locales_respaldo = {
            "A1": {"nombre": "CocaC", "precio": 1.50, "stock": 5},
            "B1": {"nombre": "Pepsi", "precio": 1.50, "stock": 4},
            "C1": {"nombre": "Fanta", "precio": 1.25, "stock": 3},
            "D1": {"nombre": "Malta", "precio": 2.00, "stock": 6},
            "A2": {"nombre": "Chint", "precio": 1.80, "stock": 2}
        }

    def cargar_desde_github(self):
        try:
            respuesta = requests.get(self._url_github)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                for cod, info in datos.items():
                    self._lista_productos[cod] = Producto(cod, info["nombre"], info["precio"], info["stock"])
                print("-> ¡Catálogo sincronizado desde GitHub!")
            else:
                self._cargar_respaldo_local()
        except Exception:
            self._cargar_respaldo_local()

    def _cargar_respaldo_local(self):
        print(" No se pudo conectar a GitHub. Cargando inventario local de respaldo.")
        for cod, info in self._datos_locales_respaldo.items():
            self._lista_productos[cod] = Producto(cod, info["nombre"], info["precio"], info["stock"])

    def buscar_producto(self, codigo):
        return self._lista_productos.get(codigo, None)

    def obtener_catalogo(self):
        return self._lista_productos

    def agregar_o_modificar_producto(self, codigo, nombre, precio, stock):
        if codigo in self._lista_productos:
            self._lista_productos[codigo].cambiar_producto(nombre, precio, stock)
        else:
            self._lista_productos[codigo] = Producto(codigo, nombre, precio, stock)


class Transaccion:
    def __init__(self, id_transaccion, producto_seleccionado, numero_tarjeta):
        self._id_transaccion = id_transaccion
        self._producto_seleccionado = producto_seleccionado
        self._numero_tarjeta = str(numero_tarjeta)
        
        # Base de datos segura 
        self._tarjetas_validas = {
            "1234567890": 10.0,
            "9876543210": 20.0,
            "1223334444": 5.0,
            "4444333221": 50.0,
            "1010101010": 1.0
        }

    def verificar_pago(self):
        #Usa el built-in function hash de Python para validar la seguridad de la tarjeta.
        tarjeta_ingresada = self._numero_tarjeta.strip()
        hash_ingresado = hash(tarjeta_ingresada)

        for tarjeta_real, saldo in self._tarjetas_validas.items():
            if hash(tarjeta_real) == hash_ingresado:
                if saldo >= self._producto_seleccionado.get_precio():
                    # Descontamos el saldo almacenado en la tarjeta
                    self._tarjetas_validas[tarjeta_real] -= self._producto_seleccionado.get_precio()
                    return True, saldo
                else:
                    print("Tarjeta sin saldo suficiente.")
                    return False, 0
        
        print("Tarjeta no reconocida o inválida.")
        return False, 0

    def procesar_operacion(self):
        if self._producto_seleccionado.get_stock() <= 0:
            print(f"El producto {self._producto_seleccionado.get_nombre()} se encuentra agotado.")
            return False
        
        es_valida, saldo_antiguo = self.verificar_pago()
        if not es_valida:
            return False

        self._producto_seleccionado.reducir_stock(1)
        print(f"Dispensando producto: {self._producto_seleccionado.get_nombre()}")
        print("¡Disfrute su producto!")
        return True


class Reporte:
    def __init__(self):
        self._ventas_historicas = []
        self._total_dinero_cobrado = 0.0
        self._usuarios_unicos = set()

    def registrar_venta(self, producto, tarjeta_usada):
        self._ventas_historicas.append(producto)
        self._total_dinero_cobrado += producto.get_precio()
        self._usuarios_unicos.add(tarjeta_usada)

    def exportar_txt(self, inventario):
        try:
            with open("reporte_ventas.txt", "w", encoding="utf-8") as archivo:
                archivo.write("REPORTE DE AUDITORÍA MÁQUINA EXPENDEDORA\n\n")
                
                archivo.write("Estado de Stock por Producto:\n")
                for cod, prod in inventario.obtener_catalogo().items():
                    archivo.write(f" - {prod.get_nombre()} ({cod}): Stock Restante = {prod.get_stock()}\n")
                
                archivo.write(f"\nNúmero total de productos vendidos: {len(self._ventas_historicas)}\n")
                archivo.write(f"Cantidad total de dinero cobrado: ${self._total_dinero_cobrado:.2f}\n")
                archivo.write(f"Número total de usuarios atendidos: {len(self._usuarios_unicos)}\n")
            print(" Reporte 'reporte_ventas.txt' generado con éxito.")
        except IOError:
            print(" Error al guardar el reporte físico.")


class MaquinaExpendedora:
    def __init__(self, url_raw_github):
        self._inventario = Inventario(url_raw_github)
        self._manejador_reportes = Reporte()
        self._contador_transacciones = 0

    def iniciar_sistema(self):
        print("Iniciando componentes del Sistema...")
        self._inventario.cargar_desde_github()
        self.desplegar_menu()

    def _imprimir_matriz_catalogo(self):
        #MÓDULO 1: Imprime el catálogo en formato de matriz de ajedrez (Filas 1-5, Columnas A-D/E)
        catalogo = self._inventario.obtener_catalogo()
        columnas = ["A", "B", "C", "D", "E"]
        
        print("    A         B         C         D         E")
        for fila in range(1, 6):
            linea_fila = f"{fila} "
            for col in columnas:
                coordenada = f"{col}{fila}"
                prod = catalogo.get(coordenada)
                
                if prod and prod.get_stock() > 0:
                    linea_fila += f"{prod.get_nombre():<10}"
                else:
                    linea_fila += "          "  # Si está agotado o no existe, se imprime en blanco
            print(linea_fila)
        print("")

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

    def _ejecutar_modulo_ventas(self, coordenada):
        #MÓDULO 2: Procesa la venta validando la existencia de la coordenada.
        prod = self._inventario.buscar_producto(coordenada)
        if not prod:
            print("-> Coordenada vacía o producto no asignado.")
            return

        print(f"El precio de {prod.get_nombre()} es ${prod.get_precio():.2f}")
        tarjeta = input("Introduzca su número de tarjeta: ").strip()
        
        if not tarjeta:
            print("-> Operación cancelada. Regresando al catálogo.")
            return

        self._contador_transacciones += 1
        venta = Transaccion(str(self._contador_transacciones), prod, tarjeta)
        
        if venta.procesar_operacion():
            self._manejador_reportes.registrar_venta(prod, tarjeta)

    def _ejecutar_modulo_restock(self):
        #MÓDULO 3: Restock - Permite actualizar existencias o cambiar un producto entero.
        print("Módulo de Restock seleccionado")
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
                    print("-> Inventario actualizado.")
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
                print("Error: Datos numéricos incorrectos.")


if __name__ == "__main__":
    URL_GITHUB = "https://raw.githubusercontent.com/lorenzocarmona/maquina-expendedora-unimet/refs/heads/main/inventario.json"
    
    maquina = MaquinaExpendedora(URL_GITHUB)
    maquina.iniciar_sistema()
