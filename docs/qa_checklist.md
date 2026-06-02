# QA Checklist — Tacómetro MVP

Pruebas manuales antes de lanzar en producción. Probar en **móvil (Chrome Android + Safari iOS)** y **desktop Chrome**.

---

## Infraestructura y deployment

- [ ] La app carga sin errores 500 en el log de Railway
- [ ] `FLASK_ENV=production` está activo
- [ ] `SECRET_KEY` es único y seguro (no el default)
- [ ] `DATABASE_URL` apunta a PostgreSQL correcto
- [ ] Todas las migraciones aplicadas: no hay "head" pendiente en Alembic
- [ ] Gunicorn corre sin warnings críticos en logs
- [ ] Archivos estáticos sirven correctamente (logo, CSS)
- [ ] La app no expone traceback de Python al usuario (error 500 muestra página personalizada)

---

## Páginas públicas — Visitante sin cuenta

### Home `/`
- [ ] Carga en menos de 3 segundos en móvil
- [ ] Logo visible (o fallback de texto si no hay imagen)
- [ ] Contador de taquerías y reseñas correcto
- [ ] Ranking visible si hay taquerías con reseñas
- [ ] Botón "Calificar ahora" lleva a `/califica`
- [ ] Botones "Ver taquerías" y "Mapa taquero" funcionan
- [ ] Sin taquerías → mensaje de estado visible y CTA

### Navbar
- [ ] Logo clickeable lleva al home
- [ ] Links "Taquerías", "Mapa" visibles en desktop
- [ ] Búsqueda global aparece en desktop (no en mobile)
- [ ] Búsqueda global retorna resultados al escribir
- [ ] Búsqueda global se cierra al hacer click afuera o Escape
- [ ] Mobile hamburger abre y cierra menú
- [ ] Mobile menú tiene "Califica ahora" y "Sugerir taquería" visibles para todos

### Lista de taquerías `/places`
- [ ] Lista visible con nombre, score y número de reseñas
- [ ] Ordenar por "Mejor score", "Nombre", "Más reseñas" funciona
- [ ] Búsqueda por nombre filtra en tiempo real al enviar form
- [ ] Paginación funciona (si hay más de 24 lugares)
- [ ] Cards con imagen si existe, emoji si no
- [ ] Click en card lleva a detalle
- [ ] "Calificar" en cada card lleva al formulario de calificación

### Detalle de taquería `/places/<slug>`
- [ ] Nombre, dirección, teléfono (si existe) visibles
- [ ] Score promedio visible si hay reseñas
- [ ] Badge "Abierto/Cerrado ahora" si tiene horario configurado
- [ ] Categorías (tipos de taco) visibles como chips
- [ ] Foto de portada visible (o placeholder emoji)
- [ ] Mapa mini visible si tiene coordenadas
- [ ] Radar chart visible si hay reseñas
- [ ] Botón "Calificar" presente para visitante anónimo
- [ ] Lista de reseñas visible con score, nombre, fecha
- [ ] Reseñas con respuesta del dueño muestran la respuesta
- [ ] Taquerías similares al final (si hay misma categoría)
- [ ] Botón "Compartir" funciona (share API o clipboard)
- [ ] URL canónica en OG meta tag es la correcta
- [ ] Preview en WhatsApp: título + descripción + imagen visible al pegar URL

### Mapa `/mapa`
- [ ] Mapa carga correctamente (tiles de OpenStreetMap)
- [ ] Marcadores de taquerías con coordenadas aparecen
- [ ] Popup al hacer click en marcador muestra nombre y botón calificar
- [ ] Sidebar con lista de taquerías visible
- [ ] Botón "Mi ubicación" pide permiso y centra mapa
- [ ] Con ubicación activa: taquerías se ordenan por distancia
- [ ] Funciona en mobile (sin scroll horizontal indeseado)
- [ ] Sin taquerías geocodificadas → mensaje visible

### Calificar — flujo anónimo
- [ ] `/califica` — búsqueda de taquería por nombre funciona
- [ ] Resultados de búsqueda llevan a `/califica/rate/<id>`
- [ ] Sin login → puede ver el formulario de calificación
- [ ] Campo "Tu nombre o apodo" visible para anónimos
- [ ] Estrellas son táctiles en móvil (no solo hover)
- [ ] Score en vivo se actualiza al seleccionar estrellas
- [ ] Botón "Guardar" bloqueado hasta que todas las estrellas estén seleccionadas
- [ ] Al guardar sin login → confirmación `/califica/ok/<id>` visible con score
- [ ] Confirmación muestra score, criterios, nombre de la taquería
- [ ] Botón "Compartir reseña" funciona desde confirmación
- [ ] Botón "Calificar otra" regresa al inicio de califica

### Calificar — nueva taquería (requiere login)
- [ ] Desde `/califica`, escribir nombre que no existe → botón "Agregar taquería"
- [ ] `/califica/nueva` redirige a login si no está autenticado
- [ ] Con login: formulario de nueva taquería llena correctamente
- [ ] Al crear → redirect a calificar el nuevo lugar

### Sugerir taquería `/sugerir`
- [ ] Formulario accesible sin login
- [ ] Nombre obligatorio: error si está vacío
- [ ] Al enviar → flash de éxito y redirect
- [ ] La sugerencia aparece en `/admin/suggestions`

### Robots y sitemap
- [ ] `/robots.txt` retorna texto plano, desactiva `/admin/` y `/auth/`
- [ ] `/sitemap.xml` retorna XML válido con todas las taquerías activas
- [ ] Sitemap incluye home, `/places`, `/mapa`

### Páginas de error
- [ ] URL inexistente → 404 con emoji taco y link a home
- [ ] Superar rate limit → 429 con mensaje de espera
- [ ] Forzar 403 accediendo a `/admin` sin admin → página 403 visible
- [ ] Error 500 no expone traceback al usuario

---

## Autenticación y perfil

### Registro `/auth/register`
- [ ] Formulario visible y funciona
- [ ] Valida username (3-64 chars)
- [ ] Valida teléfono (exactamente 10 dígitos)
- [ ] Valida contraseña (mínimo 6 chars)
- [ ] Username o teléfono duplicado → error visible
- [ ] Registro exitoso → flash de éxito, redirect a login

### Login `/auth/login`
- [ ] Formulario funciona
- [ ] Teléfono + contraseña correctos → sesión iniciada, redirect a home
- [ ] Credenciales incorrectas → mensaje de error, sin revelar cuál campo falla
- [ ] Rate limit: 20 intentos / 5 minutos
- [ ] `?next=` param respetado y seguro (no permite redirect externo)

### Logout
- [ ] `/auth/logout` cierra sesión y redirige a home con flash

### Perfil `/perfil`
- [ ] Solo accesible con login
- [ ] Lista reseñas del usuario con links a editar/eliminar
- [ ] Lista de favoritos del usuario
- [ ] Solicitudes de reclamo pendientes visibles
- [ ] Formulario de cambio de contraseña funciona
- [ ] Error si contraseña actual incorrecta
- [ ] Error si nueva contraseña < 6 chars

---

## Reseñas (usuario registrado)

- [ ] Editar propia reseña → cambios guardados
- [ ] Editar reseña ajena → 403
- [ ] Eliminar propia reseña → confirmación y redirect
- [ ] Eliminar reseña ajena → 403
- [ ] Revisar que doble calificación (misma taquería) muestra mensaje de "ya calificaste" y no crea duplicado
- [ ] Favorito toggle funciona (AJAX, sin reload)

---

## Panel admin `/admin`

- [ ] Solo accessible con rol admin
- [ ] Sin login → redirect a login
- [ ] Con usuario normal → 403
- [ ] Dashboard muestra stats: taquerías, reseñas, usuarios, reseñas hoy
- [ ] Lista de taquerías con estado activo/inactivo
- [ ] Crear taquería → aparece en la lista
- [ ] Editar taquería → cambios guardados
- [ ] Desactivar taquería → desaparece de `/places` y del mapa
- [ ] Eliminar taquería → desaparece de todo, cascada elimina reseñas
- [ ] Gestión de categorías: crear, editar, eliminar
- [ ] Lista de usuarios: visible
- [ ] Reseñas: listar, ocultar, mostrar, eliminar
- [ ] Importar XLSX: sube archivo, crea taquerías, muestra conteo
- [ ] Geocodificar: inicia proceso background, muestra status
- [ ] Sugerencias: ver pendientes, aprobar (crea taquería borrador), rechazar
- [ ] Reclamos: ver pendientes, aprobar (asigna dueño), rechazar

---

## Panel de dueño `/mi-taqueria`

- [ ] Accesible solo si tiene taquería asignada (owner_id = user.id)
- [ ] Sin taquerías → pantalla vacía o redirect
- [ ] Dashboard muestra: score promedio, total reseñas, % volvería, gasto promedio
- [ ] Gráfica de tendencia por semana visible (8 semanas)
- [ ] Criterios descompuestos visibles
- [ ] Reseñas recientes con respuestas si las hay
- [ ] Formulario de respuesta a reseña funciona
- [ ] Editar información básica de taquería funciona
- [ ] No puede editar taquería de otro dueño → 403
- [ ] No puede acceder a `/admin` si no es admin

---

## Reclamo de taquería (flujo dueño)

- [ ] Botón "¿Eres el dueño?" visible en detalle de taquería sin dueño, solo para usuarios autenticados
- [ ] Click en botón → POST a `/mi-taqueria/reclamar/<id>`
- [ ] Solicitud creada → flash de éxito
- [ ] Segunda solicitud para el mismo lugar → flash de "ya tienes solicitud pendiente"
- [ ] Admin aprueba → usuario es asignado como owner, aparece en `/mi-taqueria`
- [ ] Botón "Panel de dueño" visible en detalle de taquería para el dueño aprobado

---

## Imágenes

- [ ] Subir imagen válida (JPG, PNG, WebP) → se guarda y aparece en detalle
- [ ] Subir archivo no imagen → se ignora sin crash
- [ ] Archivo > 5MB → rechazado por Flask (MAX_CONTENT_LENGTH)
- [ ] Imagen se redimensiona a máx 1200px de ancho antes de subir
- [ ] URL de imagen en HTTPS si es de R2 o Cloudinary
- [ ] Si no hay imagen: placeholder emoji visible en lista y detalle

---

## Responsive (mobile first)

Probar en **iPhone Safari** y **Android Chrome** con tamaño 390px de ancho:

- [ ] Home: CTA visible sin scroll horizontal
- [ ] Navbar: hamburger menú funciona
- [ ] Lista de taquerías: cards apiladas, legibles
- [ ] Detalle: info, score y botones visibles sin overflow
- [ ] Formulario de calificación: estrellas táctiles, fácil de llenar con pulgar
- [ ] Mapa: visible y funcional (sin bloquear scroll de página)
- [ ] Admin: usable (aunque no prioridad)

---

## Seguridad (smoke test)

- [ ] CSRF: enviar POST sin token → 400 CSRF validation failed
- [ ] `/admin/places/1/delete` sin sesión → redirect a login
- [ ] `/admin/places/1/delete` con usuario normal → 403
- [ ] `/mi-taqueria/taqueria-de-otro` con usuario sin ownership → 403
- [ ] URL `next` en login con dominio externo → ignorada, redirect a home
- [ ] Intentar XSS básico en nombre de taquería → se escapa correctamente en el HTML
- [ ] 10+ calificaciones desde misma IP en 5 min → 429

---

## Notas finales

- Probar siempre en modo incógnito para simular visitante nuevo
- Probar con WiFi lenta o 3G para detectar problemas de carga
- Probar el flujo completo de calificación en un celular físico, no en emulador
- Si algo falla en mobile pero no en desktop: revisar viewport, touch events, z-index
