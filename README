# Siembra+
> **Sistema de Monitoreo Agrícola y Gestión de Cultivos Modular**

![Python](https://img.shields.io/badge/python-3.12-2d5a27)
![Flask](https://img.shields.io/badge/flask-3.0-4caf50)
![AWS](https://img.shields.io/badge/AWS-Cognito%20%26%20S3-orange)
![Docker](https://img.shields.io/badge/docker-ready-blue)


---

## Características Principales

* **Arquitectura Modular:** Implementación de **Blueprints** para separar la lógica de Autenticación de la lógica de Negocio.
* **Autenticación Segura:** Integración con **AWS Cognito** para el manejo de sesiones y registro de usuarios.
* **Gestión de Almacenamiento:** Subida de imágenes optimizada directamente a **AWS S3** con nombres sanitizados.
* **UX/UI Dinámica:** * Zona de *Drag & Drop* para archivos.
    * Barra de progreso en tiempo real mediante **AJAX (XMLHttpRequest)**.
    * Diseño responsivo con variables CSS modernas.
* **Procesamiento de Datos:** Optimización de imágenes (formato JPEG, 85% calidad) mediante la librería **Pillow**.

---

## Stack Tecnológico

| Componente | Tecnología |
| :--- | :--- |
| **Backend** | Python 3.12 / Flask |
| **Frontend** | HTML5 / CSS3 / JS Vanilla |
| **Cloud Storage** | AWS S3 |
| **Identity Provider** | AWS Cognito |
| **Contenerización** | Docker / Docker Compose |

---

## Estructura del Proyecto



```text
siembra-plus/
├── app.py              # Ensamblaje de la aplicación y configuración global
├── auth.py             # Lógica de Autenticación y Decoradores
├── main.py             # Lógica de Dashboard, Procesamiento y S3
├── static/             # Archivos CSS, JS e Imágenes
├── templates/          # Vistas Jinja2 (welcome, login, index, success)
├── Dockerfile          # Definición del contenedor
└── docker-compose.yml  # Orquestación local
```

---
## Instalación y Configuración

1. Requisitos Previos
Docker y Docker Compose instalados.

Cuenta de AWS con User Pool en Cognito y un Bucket en S3.

2. Variables de Entorno
Crea un archivo .env en la raíz.

3. Ejecución
Para levantar el proyecto en un entorno local aislado:

```bash
# Construir y levantar los contenedores
docker-compose up --build
```

## Seguridad Implementada
Protección de Rutas: Uso del decorador personalizado @login_required para validar sesiones activas.

Validación de Archivos: Filtro estricto por extensiones (.png, .jpg, .jpeg, .gif).

Sanitización: Uso de secure_filename para prevenir ataques de inyección de rutas.

Optimización: Conversión forzada a espacio de color RGB para evitar errores de metadatos corruptos.