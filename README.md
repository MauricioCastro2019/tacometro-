# 🌮 Tacómetro

**El ranking callejero más honesto de las taquerías de León, Guanajuato.**

Tacómetro es una plataforma web que permite a los habitantes de León calificar, descubrir y rankear taquerías usando un sistema de puntuación ponderado que valora lo que realmente importa: el sabor, la salsa, el precio, el servicio y la higiene.

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 · Flask 3.1 |
| ORM | SQLAlchemy 2.0 · Flask-Migrate (Alembic) |
| Auth | Flask-Login · Werkzeug password hashing |
| Forms | Flask-WTF · WTForms · CSRF protection |
| DB | PostgreSQL (producción) · SQLite (desarrollo) |
| Imágenes | Cloudflare R2 → Cloudinary → local fallback |
| Frontend | Tailwind CSS (CDN) · Leaflet.js · Chart.js |
| Servidor | Gunicorn |
| Deploy | Railway |
| Procesamiento | Pillow (redimensionado) · openpyxl (importación XLSX) |

---

## Instalación local

### 1. Clonar y crear entorno

```bash
git clone <repo>
cd tacometro
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Variables de entorno

Copia `.env.example` a `.env` y configura los valores:

```bash
cp .env.example .env
```

Para desarrollo local, basta con:

```env
FLASK_ENV=development
SECRET_KEY=cualquier-clave-larga-para-dev
```

No necesitas `DATABASE_URL` en desarrollo: se crea `tacometro_dev.db` (SQLite) automáticamente.

### 3. Migraciones

```bash
flask db upgrade
```

### 4. Datos iniciales (opcional)

```bash
flask seed-categories   # Crea los 24 tipos de taco
flask seed              # Crea categorías + 3 taquerías de ejemplo
```

### 5. Ejecutar

```bash
flask run
# o
python run.py
```

La app corre en `http://localhost:5000`.

---

## Variables de entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `FLASK_ENV` | Sí | `development` o `production` |
| `SECRET_KEY` | Sí (producción) | Clave secreta para sesiones y CSRF. Mínimo 32 caracteres aleatorios. |
| `DATABASE_URL` | Sí (producción) | URL de PostgreSQL. Railway la provee automáticamente. |
| `ADMIN_USERNAME` | Recomendado | Username que se promueve a admin al arrancar. |
| `R2_ACCOUNT_ID` | Para imágenes | Account ID de Cloudflare R2. |
| `R2_ACCESS_KEY_ID` | Para imágenes | Access Key de Cloudflare R2. |
| `R2_SECRET_ACCESS_KEY` | Para imágenes | Secret Key de Cloudflare R2. |
| `R2_BUCKET_NAME` | Para imágenes | Nombre del bucket en R2. |
| `R2_PUBLIC_URL` | Para imágenes | URL pública del bucket R2. |
| `CLOUDINARY_URL` | Alternativo | Si no usas R2, usa Cloudinary. |

---

## Crear usuario administrador

### Opción A — Variable de entorno (recomendado para Railway)

1. Registra el usuario normalmente desde la app.
2. Establece `ADMIN_USERNAME=tuusuario` en las variables de entorno de Railway.
3. La próxima vez que arranque la app, ese usuario se promueve a admin automáticamente.

### Opción B — CLI

```bash
flask create-admin
# Sigue el prompt interactivo para username, teléfono y contraseña
```

### Opción C — Cambiar rol directamente

```bash
flask set-role <username> admin
```

---

## Comandos CLI

```bash
flask db upgrade          # Aplicar migraciones pendientes
flask seed-categories     # Crear 24 tipos de taco predefinidos
flask seed                # Seed completo (categorías + taquerías de ejemplo)
flask create-admin        # Crear o promover usuario a admin
flask set-role <user> <role>  # Asignar rol: user | admin | owner
```

---

## Despliegue en Railway

1. Conecta el repositorio a Railway.
2. Railway detecta el `Procfile` automáticamente:
   ```
   web: flask db upgrade && gunicorn run:app
   ```
3. Configura las variables de entorno en Railway Settings → Variables.
4. Asegúrate de configurar `SECRET_KEY`, `DATABASE_URL` ya existe por defecto al agregar el plugin PostgreSQL.
5. Railway ejecuta `flask db upgrade` antes de iniciar Gunicorn, aplicando todas las migraciones.

---

## Estructura del proyecto

```
tacometro/
├── app/
│   ├── __init__.py         # Factory de la app, registro de blueprints
│   ├── extensions.py       # db, migrate, login_manager, csrf
│   ├── commands.py         # CLI: seed, create-admin, set-role
│   ├── models/
│   │   ├── user.py         # User con roles: user | admin | owner
│   │   ├── place.py        # Place (taquería) con slug, coords, horario
│   │   ├── review.py       # Review con 5 criterios ponderados
│   │   ├── review_reply.py # Respuesta del dueño a una reseña
│   │   ├── category.py     # Tipo de taco (Al Pastor, Suadero, etc.)
│   │   ├── favorite.py     # Favoritos usuario-taquería
│   │   ├── suggestion.py   # Sugerencias de nuevas taquerías
│   │   └── claim.py        # Solicitudes de reclamo de taquería
│   ├── auth/               # Registro, login (por teléfono), logout
│   ├── main/               # Index, perfil, mapa, sugerir, sobre, robots, sitemap
│   ├── places/             # Lista, detalle, favoritos
│   ├── califica/           # Flujo calificar: buscar → crear → calificar → confirmación
│   ├── reviews/            # Crear, editar, eliminar reseñas
│   ├── admin/              # Panel admin completo (CRUD, importar, geocodificar, moderar)
│   ├── owner/              # Panel de dueño (dashboard, editar, responder reseñas)
│   ├── utils/
│   │   ├── decorators.py   # admin_required, rate_limit
│   │   ├── image_upload.py # Upload R2 → Cloudinary → local
│   │   ├── slugify.py      # Generador de slugs con soporte español
│   │   └── __init__.py     # esta_abierto() con zona horaria León
│   ├── templates/          # Jinja2 templates (Tailwind dark mode)
│   └── static/             # CSS, JS, imágenes
├── migrations/             # Migraciones Alembic
├── docs/                   # Documentación de operación
│   ├── lanzamiento_30_dias.md
│   ├── redes_30_dias.md
│   └── qa_checklist.md
├── config.py               # DevelopmentConfig, ProductionConfig
├── run.py                  # Entry point para desarrollo local
├── Procfile                # Comando de inicio para Railway
├── requirements.txt
└── .env.example
```

---

## Sistema de puntuación

El **Tacómetro** (overall_score) se calcula como promedio ponderado:

| Criterio | Peso | Razón |
|----------|------|-------|
| Sabor | 35% | Lo que define a un buen taco |
| Salsa | 25% | La salsa es parte del taco, no un accesorio |
| Precio/calidad | 15% | Accesibilidad importa en la cultura taquera |
| Servicio | 15% | El trato del taquero hace la diferencia |
| Higiene | 10% | Limpieza mínima indispensable |

Escala: 1.0 – 5.0 puntos.

---

## Roles de usuario

| Rol | Capacidades |
|-----|------------|
| `user` | Calificar, editar sus reseñas, favoritos, sugerir |
| `owner` | Todo lo de `user` + dashboard de su taquería + responder reseñas |
| `admin` | Todo lo anterior + CRUD de taquerías, moderar, importar, geocodificar, reclamos |

---

## Notas de producción

- El `SECRET_KEY` **debe** configurarse en las variables de entorno. Un valor inseguro genera un log CRITICAL al arrancar.
- Las migraciones se aplican automáticamente al arrancar vía `_run_migrations()` en `create_app()`. También se ejecutan en el `Procfile` antes de Gunicorn.
- El rate limiting es **in-memory** y se resetea en cada restart. Para producción con alta carga, considera implementar Redis-based rate limiting.
- La geocodificación usa Nominatim (OpenStreetMap) con un delay de 1.1s entre requests para respetar su ToS.
- Las imágenes se redimensionan a máximo 1200px de ancho antes de subir, en formato JPEG o WebP.

---

## Próximos pasos (post MVP)

- [ ] Buscar taquería desde el mapa directamente
- [ ] Filtro por categoría en lista y mapa
- [ ] Perfil público de taquería con URL compartible optimizada
- [ ] Notificaciones al dueño cuando recibe una reseña
- [ ] Analytics básicos de tráfico (Google Analytics / Plausible)
- [ ] Soporte para múltiples ciudades
- [ ] API pública documentada
- [ ] Tests automatizados con pytest
