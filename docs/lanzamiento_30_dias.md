# Lanzamiento y operación — 30 días de prueba

## 1. Checklist previo al lanzamiento

### Infraestructura
- [ ] Railway desplegado y corriendo sin errores
- [ ] `DATABASE_URL` configurado (PostgreSQL conectado)
- [ ] `SECRET_KEY` configurado con valor único y seguro (32+ chars)
- [ ] `ADMIN_USERNAME` configurado con tu usuario
- [ ] Migraciones aplicadas correctamente (`flask db upgrade` sin errores en logs)
- [ ] `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL` configurados (si usas imágenes)
- [ ] Dominio personalizado conectado (tacometro.app o similar)
- [ ] SSL activo (Railway lo hace automático con dominio custom)

### Contenido inicial
- [ ] Al menos 10 taquerías cargadas y activas
- [ ] Todas las taquerías tienen: nombre, dirección, categoría
- [ ] Al menos 5-6 taquerías tienen coordenadas (geocodificadas)
- [ ] Al menos 3 taquerías tienen foto de portada
- [ ] Las categorías de taco están creadas (`flask seed-categories`)
- [ ] Tu usuario admin está activo y puedes entrar al panel `/admin`

### Pruebas manuales mínimas
- [ ] Ver home desde móvil: ranking visible, CTA "Calificar ahora" funciona
- [ ] Calificar sin login: flujo completo hasta confirmación
- [ ] Registro de usuario nuevo con teléfono
- [ ] Login con usuario registrado
- [ ] Ver mapa: marcadores visibles, geolocalización funciona
- [ ] Buscar taquería desde navbar (desktop) y desde califica/paso1
- [ ] Detalle de taquería: foto, score, reseñas visibles
- [ ] Compartir desde confirmación: web share API o clipboard
- [ ] Admin: crear taquería, importar XLSX, ver sugerencias

### SEO / Distribución
- [ ] `/robots.txt` accesible y correcto
- [ ] `/sitemap.xml` genera URLs de todas las taquerías activas
- [ ] Open Graph funciona: pegar URL en WhatsApp muestra preview con imagen
- [ ] Favicon visible en pestaña del browser

---

## 2. Checklist de variables de entorno

| Variable | Valor esperado | Estado |
|----------|----------------|--------|
| `FLASK_ENV` | `production` | ☐ |
| `SECRET_KEY` | Cadena aleatoria 32+ chars | ☐ |
| `DATABASE_URL` | `postgresql://...` (Railway auto) | ☐ |
| `ADMIN_USERNAME` | Tu username registrado | ☐ |
| `R2_ACCOUNT_ID` | ID de Cloudflare | ☐ |
| `R2_ACCESS_KEY_ID` | Key de R2 | ☐ |
| `R2_SECRET_ACCESS_KEY` | Secret de R2 | ☐ |
| `R2_BUCKET_NAME` | Nombre del bucket | ☐ |
| `R2_PUBLIC_URL` | URL pública del bucket | ☐ |

**Generar SECRET_KEY seguro:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. Checklist de pruebas manuales antes de lanzar

### Flujo visitante (sin cuenta)
- [ ] Home carga correctamente en móvil Chrome/Safari
- [ ] Ranking visible en home
- [ ] Click en "Calificar ahora" → llega a `/califica`
- [ ] Buscar taquería → aparece en resultados
- [ ] Ir a detalle → información completa visible
- [ ] Calificar sin login: llena estrellas, guarda, ve confirmación con score
- [ ] Compartir desde confirmación: funciona WhatsApp/clipboard
- [ ] Sugerir taquería sin login: formulario funciona, flash de éxito
- [ ] Ver mapa: carga, marcadores visibles, botón "Mi ubicación" funciona
- [ ] Página `/sobre` carga y tiene contexto de la app
- [ ] `/robots.txt` retorna texto plano correcto
- [ ] `/sitemap.xml` retorna XML con taquerías

### Flujo usuario registrado
- [ ] Registro con teléfono: crear cuenta nueva
- [ ] Login: ingresar con teléfono + contraseña
- [ ] Calificar taquería ya registrada → acceso directo al formulario
- [ ] Editar propia reseña
- [ ] No puede editar reseña de otro (403)
- [ ] Agregar a favoritos (toggle AJAX)
- [ ] Ver perfil: reseñas y favoritos visibles
- [ ] Cambiar contraseña
- [ ] Cerrar sesión

### Flujo admin
- [ ] Login con usuario admin → enlace "Admin" visible en nav
- [ ] Panel admin `/admin` carga con stats
- [ ] Crear taquería nueva
- [ ] Editar taquería existente
- [ ] Activar/desactivar taquería
- [ ] Importar XLSX con taquerías
- [ ] Geocodificar taquerías pendientes (botón en admin)
- [ ] Ver lista de usuarios
- [ ] Moderar reseña (ocultar/mostrar)
- [ ] Eliminar reseña
- [ ] Ver sugerencias y aprobar una
- [ ] Ver reclamos (si los hay)

### Errores y edge cases
- [ ] URL inexistente → 404 con personalidad taquera
- [ ] Acceder a `/admin` sin login → redirect a login
- [ ] Acceder a `/admin` con usuario normal → 403
- [ ] Superar rate limit en calificación → 429 con mensaje claro
- [ ] Subir imagen muy grande → maneja sin crash (límite 5MB)
- [ ] Taquería sin reseñas → no aparece en ranking (correcto)
- [ ] Taquería inactiva → no aparece en lista ni mapa

---

## 4. Flujo para agregar taquerías iniciales

### Opción A — Importar desde XLSX (recomendado para muchas taquerías)

1. Prepara un archivo XLSX con columnas: `nombre`, `direccion`, `especialidad`, `zona/colonia`, `horario`
2. Ve a `/admin/import`
3. Sube el archivo
4. Revisa el conteo de importadas/omitidas/errores
5. Ve a `/admin` → botón "Geocodificar pendientes"
6. Espera a que el proceso termine (1-2 min por taquería)
7. Revisa las taquerías en el mapa para confirmar coordenadas

### Opción B — Agregar una a una desde admin

1. Ve a `/admin/places/new`
2. Llena nombre, dirección, ciudad (León), categorías
3. Sube foto si tienes
4. Activa el lugar
5. Guarda
6. Geocodifica si necesitas (desde admin dashboard)

### Orden recomendado para contenido inicial
1. Las 3-5 taquerías más conocidas o queridas de León
2. Distribuidas por zonas: Norte, Centro, Sur, Oriente, Poniente
3. Variedad de especialidades: pastor, suadero, birria, carnitas, cabeza
4. Al menos 1 que esté abierta 24 horas o madrugada
5. Al menos 1 de precio bajo y 1 de precio medio-alto

---

## 5. Flujo para moderar reseñas

1. Entra a `/admin/reviews`
2. Las reseñas están ordenadas por fecha (más recientes primero)
3. Lee el comentario y el score
4. Si algo viola las reglas básicas (lenguaje ofensivo, spam, irrelevante): haz click en "Ocultar"
5. La reseña sigue en BD pero `is_visible=False`, no aparece públicamente
6. Si es claramente inválida (bot, falsa): "Eliminar"
7. **Criterio sugerido para ocultar:**
   - Comentario con insultos directos a personas
   - Score 1 con comentario "1111" o spam evidente
   - Reseña de lugar equivocado
8. **No ocultes reseñas negativas genuinas** — la credibilidad del ranking depende de la honestidad

---

## 6. Flujo para revisar sugerencias

1. Entra a `/admin/suggestions`
2. Tienes sugerencias "Pendientes" y "Resueltas"
3. Para cada sugerencia pendiente:
   - ¿Ya existe en la app con otro nombre/slug? → Rechaza
   - ¿Parece legítima? → Aprueba → se crea en borrador para que la completes
4. Al aprobar, te redirige a editar la taquería recién creada
5. Completa la info (foto, categorías, horario, coords) antes de activarla
6. Una vez lista, marca `is_active = True` y guarda

---

## 7. Flujo para revisar reclamos (solicitudes de dueño)

1. Entra a `/admin/claims`
2. Tienes solicitudes pendientes y resueltas
3. Para cada pendiente, verifica:
   - ¿El mensaje da evidencia de que es el dueño?
   - ¿Tiene perfil creíble (username razonable)?
4. Si la apruebas: ese usuario se convierte en dueño de la taquería
   - Puede acceder a `/mi-taqueria/<slug>`
   - Puede editar información básica
   - Puede responder reseñas
5. Si la rechazas: el usuario puede volver a intentarlo (máx. 2 rechazos)
6. **Para quitar a un dueño:** va a `/admin/places/<id>/edit` → botón "Remover dueño"

---

## 8. Plan mínimo de mantenimiento semanal

Dedica **20-30 minutos a la semana**:

| Día | Acción |
|-----|--------|
| Lunes | Revisar sugerencias nuevas |
| Miércoles | Revisar reseñas en moderación |
| Viernes | Revisar reclamos nuevos, compartir en redes |
| Domingo | Ver stats del panel admin: total reseñas, nuevos usuarios |

**Una vez cada 2 semanas:**
- Geocodificar taquerías nuevas que no tengan coordenadas
- Agregar 2-3 taquerías nuevas desde sugerencias aprobadas
- Revisar si hay taquerías inactivas o cerradas que deban desactivarse

**Una vez al mes:**
- Exportar datos básicos para análisis (ver sección 9)
- Decidir si el proyecto continúa, pausa o pivota (ver sección 10)

---

## 9. Indicadores a revisar después de 7, 15 y 30 días

### A los 7 días
- [ ] ¿Cuántos usuarios se registraron?
- [ ] ¿Cuántas reseñas se publicaron?
- [ ] ¿Qué taquerías tienen más calificaciones?
- [ ] ¿Cuántas sugerencias llegaron?
- [ ] ¿Algún error 500 en logs?
- [ ] ¿La app cargó bien en mobile? (probar tú mismo en 3G)

**Umbral mínimo de señal:** 3+ usuarios y 10+ reseñas en los primeros 7 días.

### A los 15 días
- [ ] Total de usuarios activos (que han hecho al menos 1 reseña)
- [ ] ¿El ranking cambia semana a semana? (señal de actividad)
- [ ] ¿Llegan reclamos de dueños? (señal de que los establecimientos se enteran)
- [ ] ¿Hay reseñas con foto? (señal de compromiso real)
- [ ] ¿Se comparten en redes? (preguntar o revisar analytics si están)
- [ ] ¿Qué zonas/colonias tienen más cobertura? ¿Cuáles faltan?

**Umbral mínimo de señal:** 10+ usuarios, 30+ reseñas en las primeras 2 semanas.

### A los 30 días
- [ ] Total de usuarios registrados
- [ ] Total de reseñas publicadas
- [ ] Total de taquerías activas con al menos 1 reseña
- [ ] Porcentaje de taquerías con score >= 4.0
- [ ] ¿Algún dueño de taquería solicitó acceso? ¿Cuántos?
- [ ] ¿Cuál es el ratio de visitantes vs. usuarios registrados? (conversión)
- [ ] ¿El tráfico viene de dónde? (WhatsApp, Instagram, directo, Google?)
- [ ] ¿Alguna taquería generó conversación o se compartió mucho?

---

## 10. Decisión final después del mes

Analiza los datos y toma una de estas decisiones:

### Continuar 🟢
**Señales:** +30 usuarios, +100 reseñas, +5 taquerías con múltiples calificaciones, tráfico orgánico o por redes.
**Siguiente paso:** agregar más taquerías, abrir a otras ciudades o colonias, buscar patrocinadores locales.

### Pausar ⏸️
**Señales:** baja actividad pero hay interés de los dueños de taquerías. La app funciona pero no hay masa crítica de usuarios.
**Siguiente paso:** reactivar con una campaña focalizada, buscar un aliado local (restaurantero, blogger de comida, influencer taquero).

### Pivotar 🔄
**Señales:** los usuarios no califican tacos, pero sugieren muchas taquerías. O el ranking no les importa tanto como el mapa.
**Siguiente paso:** simplificar a un directorio/mapa. Quitar el flujo de calificación complejo. Hacer la UX más simple.

### Monetizar 💰
**Señales:** los dueños de taquerías quieren acceso, quieren responder reseñas, quieren aparecer primero.
**Modelo posible:** Plan básico gratis (solo ver stats), Plan Pro $200 MXN/mes (responder reseñas, foto mejorada, badge verificado).
**No monetices el ranking** — eso destruye la credibilidad del proyecto.

### Integrar 🔗
**Señales:** el proyecto funciona pero es difícil de mantener solo. Hay un negocio, blog o medio local que lo podría absorber y darle más alcance.
**Siguiente paso:** buscar alianza con un actor local de foodtech, turismo o gastronomía en León.
