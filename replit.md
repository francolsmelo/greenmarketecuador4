# GreenMarket Ecuador

## Descripción del Proyecto

**GreenMarket Ecuador** es una plataforma de e-commerce especializada en productos automotrices ecológicos. La aplicación ofrece un catálogo de productos con un diseño temático verde que refleja el compromiso con la sostenibilidad y el medio ambiente.

## Tecnologías Utilizadas

### Backend
- **Flask** (Python 3.11): Framework web principal
- **PostgreSQL**: Base de datos relacional (Neon PostgreSQL via Replit)
- **Flask-SQLAlchemy**: ORM para gestión de base de datos
- **Pillow**: Procesamiento y optimización de imágenes
- **Werkzeug**: Seguridad y manejo de archivos

### Frontend
- **HTML5/CSS3**: Estructura y diseño
- **Jinja2**: Motor de plantillas integrado con Flask
- **Font Awesome**: Iconografía
- **CSS personalizado**: Diseño responsivo con paleta ecológica

## Estructura del Proyecto

```
GreenMarketEcuador/
├── main.py                 # Aplicación Flask principal con rutas
├── models.py               # Modelos de base de datos (Product, AdminUser, SiteConfig)
├── static/
│   ├── css/
│   │   └── style.css       # Estilos con tema ecológico
│   └── uploads/            # Imágenes de productos
├── templates/
│   ├── base.html           # Template base del frontend
│   ├── index.html          # Página principal con catálogo
│   ├── product_detail.html # Detalle de producto
│   ├── admin_base.html     # Template base del admin
│   ├── admin_login.html    # Login del administrador
│   ├── admin_dashboard.html# Panel principal del admin
│   ├── admin_add_product.html  # Formulario agregar producto
│   └── admin_edit_product.html # Formulario editar producto
└── replit.md              # Documentación del proyecto
```

## Características Implementadas

### Frontend (Cliente)
✅ **Catálogo de Productos**
- Visualización en grid responsivo
- Imágenes optimizadas
- Información de precio y stock
- Página de detalle completa para cada producto

✅ **Diseño Ecológico**
- Paleta de colores verde (#2d7a3e, #4caf50, #81c784)
- Iconografía relacionada con sostenibilidad
- Animaciones suaves y transiciones

✅ **Información de Contacto**
- Ing. Franklin Melo
- Dirección: Ambato - La Península
- Correo: klinfra@yahoo.com
- Visible en footer de todas las páginas

✅ **Redes Sociales**
- Enlaces a YouTube, Facebook y X (Twitter)
- Ubicados en header y footer
- Iconos con efectos hover

✅ **Acceso al Panel Admin**
- Icono de engranaje en el footer
- Redirige al login del administrador

### Panel de Administración
✅ **Autenticación**
- Usuario: `admin`
- Contraseña: `admin123`
- Sesiones protegidas

✅ **Gestión de Productos (CRUD Completo)**
- **Crear**: Formulario para agregar productos con:
  - Nombre
  - Descripción
  - Precio (USD)
  - Stock/Cantidad
  - Imagen (JPG, PNG, GIF, WEBP hasta 16MB)
  
- **Leer**: Dashboard con tabla de productos
  - Estadísticas (total, en stock, agotados)
  - Thumbnails de imágenes
  - Vista rápida de información

- **Actualizar**: Editar productos existentes
  - Modificar todos los campos
  - Cambiar o mantener imagen actual
  - Preview de nueva imagen

- **Eliminar**: Borrar productos
  - Confirmación antes de eliminar
  - Limpieza automática de imágenes

✅ **Procesamiento de Imágenes**
- Redimensionamiento automático (máx. 800x800px)
- Optimización de calidad (85%)
- Nombres únicos con timestamp
- Validación de formatos

### Base de Datos

**Tablas creadas:**

1. **products**
   - id (PK)
   - name
   - description
   - price
   - stock
   - image_filename
   - created_at
   - updated_at

2. **admin_users** (preparada para futuro)
   - id (PK)
   - username
   - password
   - created_at

3. **site_config** (preparada para futuro)
   - id (PK)
   - config_key
   - config_value

## Cómo Usar la Aplicación

### Para Visitantes
1. Abre la URL de la aplicación
2. Navega por el catálogo de productos
3. Haz clic en cualquier producto para ver detalles
4. Contacta via email para consultas

### Para Administradores
1. Haz clic en el icono de engranaje (⚙️) en el footer
2. Ingresa las credenciales:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. En el panel podrás:
   - Ver estadísticas de productos
   - Agregar nuevos productos
   - Editar productos existentes
   - Eliminar productos

## Despliegue

### Desarrollo (Actual)
La aplicación está configurada para ejecutarse automáticamente en Replit:
- El servidor Flask corre en el puerto 5000
- La base de datos PostgreSQL está conectada via variables de entorno
- Workflow: `python main.py`

### Producción (Futuro)
Para desplegar en producción:

1. **Replit Deployments (Recomendado)**
   - Usar el botón "Deploy" en Replit
   - La configuración ya está lista para deployment
   - Variables de entorno se copian automáticamente

2. **Heroku (Alternativa)**
   - Crear `Procfile`: `web: gunicorn main:app`
   - Configurar base de datos PostgreSQL en Heroku
   - Agregar buildpack de Python
   - Configurar variables de entorno

3. **Otros Servicios**
   - La app es compatible con cualquier hosting WSGI
   - Requiere PostgreSQL como base de datos
   - Configurar variables de entorno necesarias

## Variables de Entorno Requeridas

### Base de Datos y Sesión
```
DATABASE_URL=postgresql://...
SESSION_SECRET=your-secret-key-here
PGHOST=...
PGPORT=5432
PGUSER=...
PGPASSWORD=...
PGDATABASE=...
```

### Pagos
```
STRIPE_SECRET_KEY=sk_test_... (o sk_live_...)
PAYPAL_CLIENT_ID=tu-client-id
PAYPAL_CLIENT_SECRET=tu-client-secret
PAYPAL_MODE=sandbox (o 'live' para producción)
```

### Email (SMTP)
```
MAIL_SERVER=smtp.gmail.com (o smtp.mail.yahoo.com)
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicación
MAIL_DEFAULT_SENDER=noreply@greenmarket.com (opcional)
```

✅ Todas configuradas en Replit Secrets automáticamente.

## Fase 2 COMPLETADA - Mejoras Implementadas ✅

### Integraciones de Pago Completas
✅ **PayPal REST API**
  - Integración completa con paypalrestsdk
  - Procesamiento de pagos con redirección a PayPal
  - Reducción automática de stock después del pago
  - Configuración via variables de entorno (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE)
  
✅ **Stripe (PCI-DSS compliant)**
  - Procesamiento seguro de tarjetas vía Stripe Checkout
  - Configuración de claves desde variables de entorno
  - Redirección a páginas de éxito/cancelación
  
✅ **Sistema de Contacto por Email (SMTP)**
  - Formulario de contacto funcional que envía emails a klinfra@yahoo.com
  - Configuración SMTP con Flask-Mail
  - Soporte para Gmail, Yahoo y otros proveedores
  - Emails formateados en HTML y texto plano

✅ **Gestión de Métodos de Pago desde Admin**
  - Panel para habilitar/deshabilitar métodos de pago
  - Control del orden de visualización
  - Tres métodos configurados: Stripe, PayPal, Contacto Personal

### Personalización Visual desde Admin
✅ **Panel de Personalización**
  - Cambiar color primario, secundario y de fondo
  - Selectores de color con vista previa
  - Configuración almacenada en base de datos (tabla site_config)
  - Opción para restaurar colores predeterminados

### Sistema de Usuarios Completo
✅ **Registro de Usuarios**
  - Formulario de registro con validación
  - Campos: email, username, password, nombre completo, teléfono
  - Validación de unicidad de email y username
  - Contraseñas hasheadas con Werkzeug

✅ **Login de Clientes**
  - Inicio de sesión con username o email
  - Sesiones seguras con Flask
  - Redirección automática después del login

✅ **Perfiles de Usuario**
  - Actualización de información personal
  - Cambio de contraseña con verificación
  - Vista del historial de pedidos
  
✅ **Historial de Pedidos**
  - Registro de todas las compras del usuario
  - Información de producto, método de pago, monto y estado
  - Visualización ordenada por fecha

### Redes Sociales
✅ **Enlaces a Redes Sociales**
  - YouTube, Facebook, X (Twitter)
  - ✨ **NUEVO:** WhatsApp agregado (https://wa.me/593983043329)
  - Enlaces en header y footer
  - Iconos con efectos hover

## Próximas Fases (Roadmap)

### Fase 5: Carrito de Compras
- [ ] Agregar productos al carrito
- [ ] Modificar cantidades
- [ ] Proceso de checkout múltiple
- [ ] Cupones de descuento

### Fase 6: Inteligencia Artificial
- [ ] Recomendaciones de productos basadas en compras
- [ ] Chatbot de atención al cliente con IA
- [ ] Análisis predictivo de inventario
- [ ] Optimización de precios con ML

## Notas Técnicas

### Seguridad
✅ **Implementado:**
- Contraseñas hasheadas con Werkzeug (scrypt)
- Autenticación contra base de datos AdminUser
- Validación de inputs del lado del servidor
- Manejo de errores robusto con try/catch
- SESSION_SECRET obligatorio desde variables de entorno
- Validación de extensiones de archivos permitidas
- Procesamiento seguro de imágenes con manejo de excepciones

**Pendiente para producción:**
- Configurar HTTPS
- Implementar rate limiting para el login
- Agregar CAPTCHA para prevenir fuerza bruta
- Implementar CSRF tokens en formularios

### Optimizaciones
- Las imágenes se redimensionan automáticamente
- Cache-Control configurado para desarrollo
- Sesiones seguras con SECRET_KEY

### Base de Datos
- PostgreSQL (Neon) vía Replit
- Conexión mediante DATABASE_URL
- Pool de conexiones configurado (pool_recycle: 300s)
- Compatible con despliegue local, remoto y web

## Contacto del Proyecto

**Propietario:** Ing. Franklin Melo  
**Ubicación:** Ambato - La Península, Ecuador  
**Email:** klinfra@yahoo.com

---

**Fecha de Creación:** Octubre 2025  
**Última Actualización:** 23 de Octubre 2025  
**Versión:** 2.0.1 (Importado a Replit)  
**Estado:** Desarrollo - Configurado para Replit

## Configuración en Replit (Importación Completada) ✅

### Entorno de Desarrollo
- ✅ Python 3.11.13 instalado
- ✅ Todas las dependencias instaladas vía pip
- ✅ Base de datos PostgreSQL (Neon) conectada
- ✅ Variables de entorno configuradas (DATABASE_URL, SESSION_SECRET)
- ✅ Workflow configurado para ejecutar en puerto 5000
- ✅ Configuración de deployment lista (Gunicorn con autoscale)

### Credenciales de Administrador Iniciales
⚠️ **IMPORTANTE - SEGURIDAD:**
Por defecto, el sistema crea un usuario administrador con credenciales básicas:
- **Usuario:** admin
- **Contraseña:** admin123

🔒 **ACCIÓN REQUERIDA:** Después de iniciar sesión por primera vez, debes cambiar esta contraseña inmediatamente por seguridad. Este es un riesgo de seguridad si se deja sin cambiar.

### Siguiente Paso Recomendado
1. Acceder al panel de administración: `/admin/login`
2. Iniciar sesión con las credenciales por defecto
3. Cambiar la contraseña del administrador inmediatamente
4. Configurar las API keys opcionales para pagos y email si deseas usar esas funcionalidades:
   - STRIPE_SECRET_KEY (para pagos con tarjeta)
   - PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE (para PayPal)
   - MAIL_USERNAME, MAIL_PASSWORD (para envío de emails)

## Nuevas Características Implementadas (v2.0.0)

### Para Usuarios
- 🔐 Registro y login de usuarios
- 👤 Perfiles personalizables
- 🔑 Cambio de contraseña
- 📋 Historial de pedidos
- 💳 Pagos con PayPal y Stripe
- 📧 Formulario de contacto por email
- 📱 Enlace directo a WhatsApp

### Para Administradores
- 🎨 Personalización de colores del sitio
- 💰 Gestión de métodos de pago
- 📊 Mejor organización del panel admin
- ⚙️ Configuración centralizada

## Base de Datos Actualizada

### Nuevas Tablas (v2.0.0)

4. **users**
   - id (PK)
   - email (UNIQUE)
   - username (UNIQUE)
   - password (hashed)
   - full_name
   - phone
   - address
   - created_at

5. **orders**
   - id (PK)
   - user_id (FK → users)
   - product_id (FK → products)
   - payment_method
   - payment_id
   - amount
   - status
   - created_at

6. **payment_methods**
   - id (PK)
   - name
   - enabled
   - display_order
