-- DB: coral_tech
BEGIN TRANSACTION;

-- --------------------------------------------------------
CREATE TABLE provincia (
  id_provincia INTEGER PRIMARY KEY,
  nombre_provincia TEXT
);

INSERT INTO provincia (id_provincia, nombre_provincia) VALUES
(1, 'Buenos Aires'),
(2, 'Catamarca'),
(3, 'Chaco'),
(4, 'Chubut'),
(5, 'Córdoba'),
(6, 'Corrientes'),
(7, 'Entre Ríos'),
(8, 'Formosa'),
(9, 'Jujuy'),
(10, 'La Pampa'),
(11, 'La Rioja'),
(12, 'Mendoza'),
(13, 'Misiones'),
(14, 'Neuquén'),
(15, 'Río Negro'),
(16, 'Salta'),
(17, 'San Juan'),
(18, 'San Luis'),
(19, 'Santa Cruz'),
(20, 'Santa Fe'),
(21, 'Santiago del Estero'),
(22, 'Tierra del Fuego'),
(23, 'Tucumán'),
(24, 'Ciudad Autónoma de Buenos Aires');

-- --------------------------------------------------------
CREATE TABLE sucursal (
  id_sucursal INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre_sucursal TEXT
);

INSERT INTO sucursal (id_sucursal, nombre_sucursal) VALUES
(1, 'MiniMercado El Encuentro'),
(2, 'Super La Esquina'),
(3, 'Mercadito Don Pepe'),
(4, 'Almacén La Familia'),
(5, 'MiniMarket Buen Día'),
(6, 'Supermercado El Sol'),
(7, 'Mercado Express 24'),
(8, 'La Canasta de Barrio'),
(9, 'MiniMercado La Ruta'),
(10, 'Super El Trébol');

-- --------------------------------------------------------
CREATE TABLE cliente (
  id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  id_provincia INTEGER NOT NULL,
  domicilio TEXT NOT NULL,
  FOREIGN KEY (id_provincia) REFERENCES provincia(id_provincia)
);

-- --------------------------------------------------------
CREATE TABLE rubro (
  id_rubro INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre_rubro TEXT
);

-- --------------------------------------------------------
CREATE TABLE producto (
  id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL,
  precio REAL NOT NULL,
  id_rubro INTEGER NOT NULL,
  stock INTEGER NOT NULL,
  FOREIGN KEY (id_rubro) REFERENCES rubro(id_rubro)
);

-- --------------------------------------------------------
CREATE TABLE factura (
  id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT,
  id_sucursal INTEGER,
  id_cliente INTEGER,
  monto REAL,
  FOREIGN KEY (id_sucursal) REFERENCES sucursal(id_sucursal),
  FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
);

-- --------------------------------------------------------
CREATE TABLE detalle_factura (
  id_factura INTEGER,
  id_producto INTEGER,
  cantidad INTEGER NOT NULL,
  precio_unitario REAL NOT NULL,
  PRIMARY KEY (id_factura, id_producto),
  FOREIGN KEY (id_factura) REFERENCES factura(id_factura),
  FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);


COMMIT;
