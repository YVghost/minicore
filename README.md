# UDLA Notas — Calculadora de Notas Universitarias

Aplicativo web MVC construido con **Django 4.2** para gestionar y predecir notas de la Universidad de las Américas (UDLA). Permite organizar materias por carrera y semestre, registrar notas de cada progreso y calcular automáticamente qué nota se necesita para alcanzar la meta deseada.

Desplegado en **Render** con base de datos **PostgreSQL**. Funciona tanto en entorno local como en producción sin cambiar código, solo variables de entorno.

---

## Tabla de Contenidos

1. [Requisitos](#requisitos)
2. [Instalación local](#instalación-local)
3. [Variables de entorno](#variables-de-entorno)
4. [Despliegue en Render](#despliegue-en-render)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Modelos](#modelos)
7. [Vistas](#vistas)
8. [URLs](#urls)
9. [Templates](#templates)
10. [Lógica de predicción de notas](#lógica-de-predicción-de-notas)
11. [Flujo de uso](#flujo-de-uso)

---

## Requisitos

- Python 3.10+
- Las siguientes dependencias se instalan con `pip install -r requirements.txt`:

| Paquete               | Uso                                              |
|-----------------------|--------------------------------------------------|
| `Django>=4.2`         | Framework principal                              |
| `psycopg2-binary`     | Conector PostgreSQL                              |
| `dj-database-url`     | Parsea la variable `DATABASE_URL` a config Django|
| `python-decouple`     | Lee variables desde `.env` o el entorno del SO   |
| `gunicorn`            | Servidor WSGI para producción (Render)           |
| `whitenoise`          | Sirve archivos estáticos sin servidor externo    |
| `pillow`              | Manejo de imágenes (Django)                      |

---

## Instalación local

```bash
# 1. Situarse en el directorio del proyecto
cd minicore

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/Scripts/activate   # Windows
source venv/bin/activate       # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar el archivo de entorno y configurarlo
cp .env.example .env
# Editar .env con tus valores (ver sección Variables de entorno)

# 5. Aplicar migraciones
python manage.py migrate

# 6. (Opcional) Crear superusuario para el panel admin
python manage.py createsuperuser

# 7. Levantar el servidor
python manage.py runserver
```

Acceder en el navegador: `http://127.0.0.1:8000`

Panel de administración: `http://127.0.0.1:8000/admin`

---

## Variables de entorno

El proyecto usa `python-decouple` para leer la configuración. En local se lee desde el archivo `.env` (ignorado por git). En Render se leen desde las *Environment Variables* del servicio.

### Archivo `.env` (desarrollo local)

Copia `.env.example` como `.env` y completa los valores:

```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-larga-y-aleatoria

# URL externa de la BD de Render (para conectarte desde local)
DATABASE_URL=postgresql://usuario:password@host.render.com/nombre_bd

# Hosts permitidos en local
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Variables requeridas en producción (Render Dashboard)

| Variable         | Valor en Render                                               |
|------------------|---------------------------------------------------------------|
| `DEBUG`          | `False`                                                       |
| `SECRET_KEY`     | Clave secreta larga y aleatoria (generar una nueva)           |
| `DATABASE_URL`   | URL **interna** de la BD PostgreSQL de Render                 |
| `ALLOWED_HOSTS`  | `tu-app.onrender.com`                                         |

> **Por qué dos URLs de base de datos:**
> - **URL interna** (`dpg-...a/minicore_base`) — solo funciona dentro de la red de Render. Úsala en producción para latencia mínima y sin costo de ancho de banda.
> - **URL externa** (`dpg-...ohio-postgres.render.com/minicore_base`) — accesible desde internet. Úsala en local para conectarte a la misma BD de Render durante el desarrollo.

### Comportamiento según entorno

| Situación                    | Base de datos usada       |
|------------------------------|---------------------------|
| Sin `.env` y sin `DATABASE_URL` | SQLite local (fallback) |
| Con `DATABASE_URL` en `.env`    | PostgreSQL (Render)     |
| En Render con var de entorno    | PostgreSQL (Render)     |

---

## Despliegue en Render

### 1. Preparar el repositorio

Asegúrate de que estos archivos estén commiteados:

```
build.sh          ← script de build
requirements.txt  ← dependencias
.env.example      ← plantilla de variables (sin credenciales reales)
```

El archivo `.env` **nunca** debe commitearse (está en `.gitignore`).

### 2. Crear el servicio en Render

1. Ir a [render.com](https://render.com) → **New** → **Web Service**
2. Conectar el repositorio de GitHub/GitLab
3. Configurar el servicio:

| Campo           | Valor                                      |
|-----------------|--------------------------------------------|
| **Runtime**     | Python                                     |
| **Build Command** | `chmod +x build.sh && ./build.sh`        |
| **Start Command** | `gunicorn grade_calculator.wsgi:application` |
| **Plan**        | Free                                       |

### 3. Configurar las variables de entorno en Render

En la sección **Environment** del servicio, agregar:

| Key              | Value                                                                                   |
|------------------|-----------------------------------------------------------------------------------------|
| `DEBUG`          | `False`                                                                                 |
| `SECRET_KEY`     | *(generar con `python -c "import secrets; print(secrets.token_urlsafe(50))"` )*        |
| `DATABASE_URL`   | URL **interna** de tu BD PostgreSQL de Render                                           |
| `ALLOWED_HOSTS`  | `tu-app.onrender.com`                                                                   |

### 4. Lo que hace `build.sh` en cada deploy

```bash
pip install -r requirements.txt      # instala dependencias
python manage.py collectstatic --no-input  # compila archivos estáticos con WhiteNoise
python manage.py migrate             # aplica migraciones pendientes
```

### Archivos estáticos en producción

WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`) sirve los archivos estáticos directamente desde Django sin necesitar un servidor de archivos externo (S3, Nginx, etc.). El `collectstatic` del `build.sh` copia todo a `staticfiles/` con compresión y nombres con hash para caché óptima.

---

## Estructura del proyecto

```
minicore/
│
├── manage.py                        # Punto de entrada de comandos Django
├── requirements.txt                 # Dependencias del proyecto
├── build.sh                         # Script de build para Render
├── .env                             # Variables locales (NO se commitea)
├── .env.example                     # Plantilla de variables (sí se commitea)
├── .gitignore                       # Excluye venv, .env, __pycache__, etc.
├── db.sqlite3                       # BD SQLite — solo si no hay DATABASE_URL
│
├── grade_calculator/                # Paquete de configuración principal
│   ├── settings.py                  # Configuración unificada local/producción
│   ├── urls.py                      # Enrutador raíz del proyecto
│   ├── wsgi.py                      # Punto de entrada WSGI (gunicorn)
│   └── asgi.py                      # Punto de entrada ASGI
│
├── accounts/                        # App de autenticación de usuarios
│   ├── forms.py                     # RegisterForm, LoginForm
│   ├── views.py                     # Login, registro, logout
│   └── urls.py                      # Rutas /cuenta/...
│
├── grades/                          # App principal de notas
│   ├── models.py                    # Career, Semester, Subject + lógica de predicción
│   ├── forms.py                     # CareerForm, SemesterForm, SubjectForm, GradeUpdateForm
│   ├── views.py                     # CRUD de carreras, semestres, materias
│   ├── urls.py                      # Rutas /app/...
│   ├── admin.py                     # Registro de modelos en el panel admin
│   └── migrations/
│       └── 0001_initial.py          # Migración inicial de los tres modelos
│
├── templates/                       # Templates HTML globales
│   ├── base.html                    # Layout base con navbar y sidebar
│   ├── accounts/
│   │   ├── login.html               # Formulario de inicio de sesión
│   │   └── register.html            # Formulario de registro
│   └── grades/
│       ├── dashboard.html           # Vista resumen con todas las carreras
│       ├── career_list.html         # Listado de carreras del usuario
│       ├── career_form.html         # Formulario crear / editar carrera
│       ├── career_confirm_delete.html
│       ├── semester_list.html       # Semestres de una carrera
│       ├── semester_form.html       # Formulario crear / editar semestre
│       ├── semester_confirm_delete.html
│       ├── subject_list.html        # Materias de un semestre
│       ├── subject_form.html        # Formulario crear / editar materia
│       ├── subject_detail.html      # Ingreso de notas + predicción
│       └── subject_confirm_delete.html
│
├── static/                          # Archivos estáticos fuente (CSS, JS, imágenes)
└── staticfiles/                     # Generado por collectstatic — NO se commitea
```

---

## Modelos

Ubicación: [`grades/models.py`](grades/models.py)

Los tres modelos forman una jerarquía: **Career → Semester → Subject**.
Cada modelo pertenece al usuario a través de la cadena de llaves foráneas.

---

### `Career` — Carrera

Representa una carrera universitaria que sigue el usuario.
Un usuario puede tener múltiples carreras (ej. dos carreras simultáneas).

| Campo        | Tipo                  | Descripción                              |
|--------------|-----------------------|------------------------------------------|
| `user`       | ForeignKey → User     | Propietario del registro                 |
| `name`       | CharField(200)        | Nombre de la carrera                     |
| `created_at` | DateTimeField         | Fecha de creación (automática)           |

**Método útil:**
- `get_overall_average()` — promedio de todas las notas finales de las materias de la carrera.

---

### `Semester` — Semestre

Agrupa materias dentro de una carrera. Puede representar un semestre, ciclo o período académico.

| Campo        | Tipo                  | Descripción                              |
|--------------|-----------------------|------------------------------------------|
| `career`     | ForeignKey → Career   | Carrera a la que pertenece               |
| `name`       | CharField(100)        | Nombre del semestre (ej. "Semestre 3")   |
| `created_at` | DateTimeField         | Fecha de creación (automática)           |

**Métodos útiles:**
- `get_average()` — promedio de las notas finales del semestre.
- `get_status()` — devuelve `'empty'`, `'not_started'`, `'in_progress'` o `'complete'`.

---

### `Subject` — Materia

Es el modelo central. Almacena las tres notas de progreso y contiene toda la lógica de cálculo y predicción.

| Campo           | Tipo                      | Descripción                                        |
|-----------------|---------------------------|----------------------------------------------------|
| `semester`      | ForeignKey → Semester     | Semestre al que pertenece                          |
| `name`          | CharField(200)            | Nombre de la materia                               |
| `desired_grade` | DecimalField(0–10)        | Nota que el estudiante desea obtener               |
| `progress1`     | DecimalField(0–10, null)  | Nota del primer progreso  (25%)                    |
| `progress2`     | DecimalField(0–10, null)  | Nota del segundo progreso (35%)                    |
| `progress3`     | DecimalField(0–10, null)  | Nota del tercer progreso  (40%)                    |

Los campos de progreso son **opcionales** (null/blank) para permitir ingresarlos gradualmente.

**Constantes de peso:**

```python
WEIGHT_P1 = Decimal('0.25')   # 25%
WEIGHT_P2 = Decimal('0.35')   # 35%
WEIGHT_P3 = Decimal('0.40')   # 40%
PASSING_GRADE = Decimal('7.00')
```

**Propiedades calculadas (no se guardan en BD):**

| Propiedad            | Retorna                                                        |
|----------------------|----------------------------------------------------------------|
| `current_grade`      | Suma ponderada de los progresos ingresados hasta el momento    |
| `final_grade`        | Nota final si los 3 progresos están ingresados, `None` si no  |
| `is_passing`         | `True/False` si hay nota final, `None` si aún no está completa|
| `progresses_entered` | Número de progresos ingresados (0–3)                          |
| `prediction`         | Diccionario con la predicción de nota (ver sección dedicada)   |

---

## Vistas

Ubicación: [`grades/views.py`](grades/views.py) y [`accounts/views.py`](accounts/views.py)

Todas las vistas de `grades` están decoradas con `@login_required`.
Las consultas filtran siempre por `user=request.user` para aislar los datos entre usuarios.

---

### Vistas de autenticación (`accounts/views.py`)

| Vista               | Tipo         | Descripción                                          |
|---------------------|--------------|------------------------------------------------------|
| `CustomLoginView`   | Class-Based  | Extiende `LoginView` de Django con formulario propio |
| `register_view`     | Function     | Crea el usuario y lo autentica automáticamente       |
| `logout_view`       | Function     | Cierra sesión y redirige al login                    |

---

### Vistas de la app (`grades/views.py`)

#### Dashboard

| Vista       | Método | Descripción                                                                     |
|-------------|--------|---------------------------------------------------------------------------------|
| `dashboard` | GET    | Resumen de todas las carreras, totales de materias aprobadas/reprobadas         |

#### Carreras

| Vista           | Método    | Descripción                              |
|-----------------|-----------|------------------------------------------|
| `career_list`   | GET       | Lista todas las carreras del usuario     |
| `career_create` | GET/POST  | Crea una nueva carrera                   |
| `career_update` | GET/POST  | Edita el nombre de una carrera           |
| `career_delete` | GET/POST  | Confirma y elimina una carrera (cascada) |

#### Semestres

| Vista             | Método    | Descripción                                     |
|-------------------|-----------|-------------------------------------------------|
| `semester_list`   | GET       | Lista semestres de una carrera                  |
| `semester_create` | GET/POST  | Crea un semestre dentro de una carrera          |
| `semester_update` | GET/POST  | Edita el nombre de un semestre                  |
| `semester_delete` | GET/POST  | Confirma y elimina un semestre (cascada)        |

#### Materias

| Vista            | Método    | Descripción                                              |
|------------------|-----------|----------------------------------------------------------|
| `subject_list`   | GET       | Lista materias de un semestre                            |
| `subject_create` | GET/POST  | Crea una materia con nombre y nota deseada               |
| `subject_update` | GET/POST  | Edita nombre y nota deseada de la materia                |
| `subject_delete` | GET/POST  | Confirma y elimina una materia                           |
| `subject_detail` | GET/POST  | Vista principal: ingresa/actualiza notas y muestra predicción |

La vista `subject_detail` maneja dos responsabilidades en una sola URL:
- **GET** → muestra el formulario con las notas actuales y la predicción calculada.
- **POST** → guarda las notas y redirige a la misma vista actualizada.

---

## URLs

### Raíz (`grade_calculator/urls.py`)

| Ruta        | App       | Descripción                     |
|-------------|-----------|---------------------------------|
| `/`         | —         | Redirige a `/app/` (dashboard)  |
| `/admin/`   | Django    | Panel de administración         |
| `/cuenta/`  | accounts  | Rutas de autenticación          |
| `/app/`     | grades    | Rutas principales de la app     |

### Autenticación (`accounts/urls.py`) — prefijo `/cuenta/`

| URL                  | Nombre               | Vista           |
|----------------------|----------------------|-----------------|
| `/cuenta/login/`     | `accounts:login`     | CustomLoginView |
| `/cuenta/registro/`  | `accounts:register`  | register_view   |
| `/cuenta/salir/`     | `accounts:logout`    | logout_view     |

### App principal (`grades/urls.py`) — prefijo `/app/`

| URL                                            | Nombre                   | Vista           |
|------------------------------------------------|--------------------------|-----------------|
| `/app/`                                        | `grades:dashboard`       | dashboard       |
| `/app/carreras/`                               | `grades:career_list`     | career_list     |
| `/app/carreras/nueva/`                         | `grades:career_create`   | career_create   |
| `/app/carreras/<pk>/editar/`                   | `grades:career_update`   | career_update   |
| `/app/carreras/<pk>/eliminar/`                 | `grades:career_delete`   | career_delete   |
| `/app/carreras/<career_pk>/semestres/`         | `grades:semester_list`   | semester_list   |
| `/app/carreras/<career_pk>/semestres/nuevo/`   | `grades:semester_create` | semester_create |
| `/app/semestres/<pk>/editar/`                  | `grades:semester_update` | semester_update |
| `/app/semestres/<pk>/eliminar/`                | `grades:semester_delete` | semester_delete |
| `/app/semestres/<semester_pk>/materias/`       | `grades:subject_list`    | subject_list    |
| `/app/semestres/<semester_pk>/materias/nueva/` | `grades:subject_create`  | subject_create  |
| `/app/materias/<pk>/`                          | `grades:subject_detail`  | subject_detail  |
| `/app/materias/<pk>/editar/`                   | `grades:subject_update`  | subject_update  |
| `/app/materias/<pk>/eliminar/`                 | `grades:subject_delete`  | subject_delete  |

---

## Templates

Todos los templates heredan de [`templates/base.html`](templates/base.html).

### `base.html` — Layout principal

Define la estructura visual completa:
- **Navbar** superior con logo "UDLA Notas", nombre del usuario y botón de cerrar sesión.
- **Sidebar** lateral (visible en pantallas medianas+) con navegación a dashboard y carreras.
- **Área de contenido** principal donde cada template hijo renderiza su bloque `{% block content %}`.
- Para páginas de autenticación usa `{% block auth_content %}` con fondo oscuro degradado, sin sidebar.
- Integra **Bootstrap 5.3** y **Bootstrap Icons 1.11** vía CDN.
- Variables CSS personalizadas: `--udla-dark` (azul oscuro), `--udla-gold` (dorado).

---

### Templates de autenticación

#### `accounts/login.html`
Pantalla centrada sobre fondo azul oscuro. Formulario de usuario y contraseña con enlace al registro.

#### `accounts/register.html`
Mismo fondo. Formulario en dos columnas (nombres/apellidos), con email, usuario y contraseñas. Al registrarse, el usuario queda autenticado automáticamente.

---

### Templates de la app

#### `grades/dashboard.html`
Vista principal post-login. Muestra:
- **4 tarjetas de estadísticas:** total de carreras, materias, aprobadas y reprobadas.
- **Una tarjeta por carrera** con sus semestres, y dentro de cada semestre una lista de materias con su nota o progreso actual.
- Estado vacío con botón para crear la primera carrera.

#### `grades/career_list.html`
Grilla de tarjetas, una por carrera. Cada tarjeta muestra nombre, número de semestres, promedio general (si hay notas finales) y botones de editar/eliminar/ver semestres.

#### `grades/career_form.html`
Formulario simple con breadcrumb. Reutilizado para crear y editar con el parámetro `action` en el contexto.

#### `grades/career_confirm_delete.html`
Pantalla de confirmación con advertencia de eliminación en cascada.

#### `grades/semester_list.html`
Similar a `career_list` pero a nivel de semestre. Cada tarjeta muestra las materias del semestre con sus notas en una lista compacta.

#### `grades/semester_form.html` / `semester_confirm_delete.html`
Análogos a los de carrera.

#### `grades/subject_list.html`
Grilla de materias. Cada tarjeta muestra las tres notas de progreso con sus porcentajes (`25%`, `35%`, `40%`) y la nota final si está completa.

#### `grades/subject_form.html`
Formulario para crear o editar materia (nombre + nota deseada).

#### `grades/subject_confirm_delete.html`
Confirmación de eliminación de materia.

#### `grades/subject_detail.html` — Vista más importante

Dividida en dos columnas:

**Columna izquierda — Ingreso de notas:**
- Tres secciones (una por progreso) con etiqueta de porcentaje, campo de entrada y texto explicativo de cuánto aporta cada progreso.
- Botón "Guardar notas" que hace POST a la misma URL.

**Columna derecha — Resumen y predicción:**
- **Tarjeta "Nota acumulada":** círculo visual con la nota acumulada actual, coloreado verde (aprobado), rojo (reprobado) o gris/amarillo (pendiente).
- **Tarjeta "Predicción de Notas":** muestra el resultado del motor de predicción en un recuadro con borde de color según si la meta es alcanzable o no.

---

## Lógica de predicción de notas

Implementada como propiedad `prediction` en el modelo `Subject` ([`grades/models.py`](grades/models.py)).

La nota final se calcula como:

```
Nota final = P1 × 0.25 + P2 × 0.35 + P3 × 0.40
```

La predicción varía según cuántos progresos se han ingresado:

---

### Caso 1: Ningún progreso ingresado

```python
{'status': 'no_data', 'message': 'Ingresa tus notas para ver la predicción'}
```

Se muestra un recuadro gris informativo.

---

### Caso 2: Solo P1 ingresado

Se calcula el **promedio necesario igual en P2 y P3** para alcanzar la nota deseada:

```
peso_restante = 0.35 + 0.40 = 0.75
necesario = (deseada - P1 × 0.25) / 0.75
```

```python
{'status': 'need_p2_p3', 'current': ..., 'needed': ..., 'achievable': 0 <= needed <= 10}
```

- Si `needed > 10` → la meta ya no es alcanzable con ninguna nota posible.
- Si `needed < 0` → la meta ya está asegurada sin importar lo que saque.

---

### Caso 3: P1 y P2 ingresados

Se calcula **exactamente qué nota se necesita en P3**:

```
necesario_p3 = (deseada - P1 × 0.25 - P2 × 0.35) / 0.40
```

```python
{'status': 'need_p3', 'current': ..., 'needed': ..., 'achievable': 0 <= needed <= 10}
```

---

### Caso 4: Los 3 progresos ingresados

Se muestra la nota final calculada y si se alcanzó la meta:

```python
{'status': 'complete', 'final_grade': ..., 'achieved': final >= deseada}
```

---

### Nota mínima para aprobar en UDLA

La constante `PASSING_GRADE = Decimal('7.00')` determina si una materia está aprobada o reprobada. La escala de notas es de **0 a 10**.

---

## Flujo de uso

```
1. Registro / Login
        │
        ▼
2. Crear Carrera  (ej: "Ingeniería en Sistemas")
        │
        ▼
3. Crear Semestre  (ej: "Semestre 3 — 2024")
        │
        ▼
4. Agregar Materias  (ej: "Cálculo II", nota deseada: 8.00)
        │
        ▼
5. Ingresar notas conforme avanza el ciclo:
   - Después del 1er progreso → ingresa P1
   - Después del 2do progreso → ingresa P2
   - Después del 3er progreso → ingresa P3
        │
        ▼
6. Ver predicción en tiempo real:
   - Con P1:      "Necesitas 7.87 promedio en P2 y P3"
   - Con P1+P2:   "Necesitas 6.50 en el tercer progreso"
   - Con P1+P2+P3: "Nota final: 7.45 — Aprobado"
```

---

## Panel de administración

Accesible en `/admin/` con un superusuario. Permite gestionar directamente `Career`, `Semester` y `Subject` con inlines para navegar la jerarquía desde una sola pantalla.
