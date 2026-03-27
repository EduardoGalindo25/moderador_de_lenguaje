# Moderador de Chat Inteligente con IA (DeepSeek)

Este proyecto es una aplicación web de chat interactivo que utiliza Inteligencia Artificial para moderar las conversaciones en tiempo real. Está diseñado para evaluar el comportamiento del usuario durante una interacción de 10 mensajes y generar un reporte detallado al finalizar.

## 🚀 Características
- **Moderación en Tiempo Real:** El sistema detecta lenguaje ofensivo o tóxico y cambia su tono para advertir al usuario.
- **Retroalimentación Positiva:** Reconoce y agradece los comentarios constructivos y amables.
- **Límite de Conversación:** Las sesiones están limitadas a 10 mensajes para un análisis conciso.
- **Reporte Final IA:** Al décimo mensaje, el sistema utiliza la API de DeepSeek para generar un análisis JSON sobre:
  - Calificación de redacción (ortografía, gramática, claridad).
  - Estadísticas de vocabulario (palabras más usadas, sentimiento).
  - Calificación final del usuario (puntaje y clasificación).

## 🛠️ Tecnologías Utilizadas
- **Framework Web:** [Django 5.x](https://www.djangoproject.com/)
- **Lenguaje:** Python 3.10+
- **IA/ML:** API de [DeepSeek](https://www.deepseek.com/) (compatible con la librería de OpenAI)
- **CSS:** [TailwindCSS](https://tailwindcss.com/)
- **Base de Datos:** SQLite (desarrollo)
- **Variables de Entorno:** python-dotenv

## 📋 Requisitos Previos
1. Tener instalado **Python 3.x**.
2. Una **API Key** de DeepSeek. Puedes obtenerla en [platform.deepseek.com](https://platform.deepseek.com/).

## 🔧 Configuración e Instalación

### 1. Clonar el repositorio (si aplica) o situarse en la carpeta
```bash
cd moderador_chat
```

### 2. Crear y activar un entorno virtual
Es altamente recomendado usar un entorno virtual para mantener las dependencias aisladas.

**En Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo llamado `.env` en la raíz del proyecto basándote en el archivo de ejemplo:
```bash
cp .env.example .env
```
Edita el archivo `.env` y añade tu clave de API:
```env
DEEPSEEK_API_KEY=tu_clave_aqui
```

### 5. Preparar la base de datos
Ejecuta las migraciones iniciales de Django:
```bash
python manage.py migrate
```

### 6. Iniciar el servidor
```bash
python manage.py runserver
```
La aplicación estará disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📁 Estructura del Proyecto
- `chat_app/`: Contiene la lógica del chat, las vistas de la API y el procesamiento de mensajes con DeepSeek.
- `moderator_project/`: Configuración global del proyecto Django.
- `templates/`: Archivos HTML del frontend.
- `static/`: Archivos CSS (Tailwind) y JavaScript.

## 📝 Notas Adicionales
- La lógica de evaluación requiere que una palabra se repita al menos **3 veces** para ser considerada en las estadísticas de "palabras más usadas".
- El sistema utiliza el modelo `deepseek-chat`.
