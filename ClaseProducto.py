#  Contiene: Producto, Carrito, Venta
class Producto:
    def __init__(self, id, nombre, precio, categoria, stock, codigo_barras=None):
        self.id = id
        self.nombre = nombre
        self.precio = float(precio)
        self.categoria = categoria
        self.stock = int(stock)
        self.codigo_barras = codigo_barras

    def hay_stock(self):
        """Devuelve True si hay al menos 1 unidad disponible."""
        return self.stock > 0

    def reducir_stock(self, cantidad=1):
        """Descuenta del stock cuando se vende."""
        if cantidad > self.stock:
            raise ValueError(f"Stock insuficiente para '{self.nombre}'")
        self.stock -= cantidad

    def __str__(self):
        """Representación legible del producto."""
        return f"{self.nombre} — ${self.precio:.2f} (stock: {self.stock})"


class ItemCarrito:
    def __init__(self, producto: Producto, cantidad: int = 1):
        self.producto = producto
        self.cantidad = cantidad

    def subtotal(self):
        """Precio del producto × cantidad."""
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} — ${self.subtotal():.2f}"


class Carrito:
    def __init__(self):
        self.items = []  

    def agregar(self, producto: Producto, cantidad: int = 1):
        """
        Agrega un producto al carrito.
        Si ya existe, suma la cantidad en lugar de duplicar.
        """
        for item in self.items:
            if item.producto.id == producto.id:
                item.cantidad += cantidad
                return
        self.items.append(ItemCarrito(producto, cantidad))

    def quitar(self, producto_id: int):
        """Elimina completamente un producto del carrito por su ID."""
        self.items = [i for i in self.items if i.producto.id != producto_id]

    def total(self):
        """Suma todos los subtotales del carrito."""
        return sum(item.subtotal() for item in self.items)

    def cantidad_items(self):
        """Cantidad total de unidades en el carrito."""
        return sum(item.cantidad for item in self.items)

    def vaciar(self):
        """Limpia el carrito (se usa después de confirmar la venta)."""
        self.items = []

    def esta_vacio(self):
        return len(self.items) == 0

    def __str__(self):
        if self.esta_vacio():
            return "El carrito está vacío."
        lineas = [str(item) for item in self.items]
        lineas.append(f"TOTAL: ${self.total():.2f}")
        return "\n".join(lineas)


class Venta:
    def __init__(self, items: list, total: float, pago: float):
        self.items = items            # Copia de los ítems vendidos
        self.total = total            # Total cobrado
        self.pago = pago              # Dinero entregado por el cliente
        self.vuelto = pago - total    # Cambio a devolver

    def es_valida(self):
        """Una venta es válida si el pago cubre el total."""
        return self.pago >= self.total

    def ticket(self):
        """Genera el texto del ticket de compra."""
        lineas = ["=" * 30, "      TICKET DE COMPRA", "=" * 30]
        for item in self.items:
            lineas.append(str(item))
        lineas.append("-" * 30)
        lineas.append(f"TOTAL:   ${self.total:.2f}")
        lineas.append(f"PAGÓ:    ${self.pago:.2f}")
        lineas.append(f"VUELTO:  ${self.vuelto:.2f}")
        lineas.append("=" * 30)
        return "\n".join(lineas)