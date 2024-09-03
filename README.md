# Guía para Levantar el Proyecto en Local - FastAPI
Este proyecto utiliza FastAPI, un marco web moderno y rápido para la creación de APIs con Python. Sigue los siguientes pasos para levantar el proyecto en tu entorno local:

## Requisitos Previos
* Python 3.7 o superior instalado en tu sistema.
* Editor de código (por ejemplo, VSCode, PyCharm) para la edición y visualización del código.
## Configuración del Entorno Virtual (opcional pero recomendado)
* Abre una terminal y navega hasta el directorio del proyecto.
* Crea un nuevo entorno virtual ejecutando el siguiente comando:
```bash
python3 -m venv env
```
* Activa el entorno virtual:
En Windows:
```bash
env\Scripts\activate
```
En macOS y Linux:
```bash
source env/bin/activate
```
## Instalación de Dependencias
Asegúrate de que estás en el directorio del proyecto y el entorno virtual está activado.
Instala las dependencias del proyecto ejecutando el siguiente comando:
```bash
pip install -r requirements.txt
```
## Configuración de Variables de Entorno
Crea un archivo .env en el directorio raíz del proyecto.
Define las variables de entorno necesarias en el archivo .env. Asi::
```Python
# PostgreSQL example:

DB_URL = "postgresql://user:password@localhost/products_app"
```
Define las credenciales para la generación y decodificación de JWT tokens:
```Python
# JSON web token credentials

JWT_SECRET_KEY="tuClaveSegura"
ALGORITHM="HS256" # Se recomienda dejar éste mismo.
ACCESS_TOKEN_EXPIRE_SEC= 1200 # Duración en segundos del token.
```
Crea un servicio SMPT con alguna plataforma de email como gmail ó outlook.
*Ejemplo de cómo crearla en el siguiente enlace:* https://www.youtube.com/watch?v=ExqdE1IzpZ0
Desde este correo se enviarán los mails de confirmación de registro en la API:
```Python
# Gmail SMPT service:

EMAIL="ejemplo@gmail.com"
EMAIL_PASSWORD="password_given_by_google"
CHANGE_PASSWORD_ENDPIONT="http://localhost:5173/api/v1/users/reset_password_form"
```
Ingresa las credenciales del usuario con rol de admin de la API; éste usuario podrá ingresar a las rutas protegidas de usuario con las cuales podrá realizar operaciones CRUD de los demás usuarios registrados:
```Python
# Web Master Credentials:

WEB_MASTER_EMAIL="mariotriana1978@gmail.com"

# Admin User Credentials: 
NAME="test_name"
ADMIN_EMAIL="mariotriana1978@gmail.com"
PASSWORD="securepassword"
```

URL del servicio de alojamiento de imágenes y de imágenes por defecto del carrusel y las targetas de los productos:
```Python
# Images

IMAGES_SERVICE='url con credencial del servicio de almacanamiento de imágenes (Recomendado: Claudinary)'

STORE_IMAGE='https://res-console.cloudinary.com/dgovs6wlm/thumbnails/v1/image/upload/v1716693885/ZGFsYW5hX2tpZHMvaXhvdmt2Yml5b2x6MnJwb3RwdDI=/preview' 

CART_IMAGE='URL de la imagen que se pondrá por defecto en las tarjetas de los productos'

CAROUSEL_IMAGE='URL de la imagen que se pondrá por defecto en el carrusel principal de la página'
```

## Allowed Origins
Ingresa las URL de las APPs del Frontend que van a consumir la API:
```Python
# React app dev URL for example:

ALLOWED_ORIGINS="http://127.0.0.1:5173/"
```
## Creación de las tablas en la base de datos
* Crea la tabla "products_app" en un gestor de bases de datos relacionales; MySQL ó Postgres, por ejemplo:
```SQL
CREATE DATABASE "products_app"
```

* Luego ingresa a la carpeta "src/db_config" en el fichero "db_tables.py"  
![alt text](static\images\image-3.png)
* Una vez estando allí, deberás borrar los encabezados "src." de la rutas de importación de la conección a la base de datos y del enum de validación "UsrRole" las cuales deben quedar asi:![alt text](static\images\image-4.png)*(ésto se hace para que el ORM reconozca la ruta de ejecución del script y cree las tablas automáticamente en la base de datos)*.
* Luego ejecuta el script ya sea desde la consola ó dando click al botón de ejecución del editor de código. De ésta menera se crearán las tablas en la base de datos y se insertarán los datos del usuario administrador y de las tablas lookup con unformación de los roles de los usuarios.
* Por último vuelve a poner los encabezados "src." de las rutas de importación anteriormente modificadas; deben quedar nuevamente asi:![alt text](static\images\image-5.png) *(ésto se hace con el fin de que ahora sea en framework FastAPI el que reconozca las rutas de los modelos y esquemase de validación usados en la API)*
## Ejecución del Proyecto
Con el entorno virtual activado y las dependencias instaladas, ejecuta el siguiente comando para iniciar el servidor:
```bash
uvicorn main:app --reload
```
* Abre tu navegador web y navega a la dirección http://localhost:8000 para interactuar con la API.
## Documentación de la API
FastAPI genera automáticamente una documentación interactiva de la API que puedes consultar en http://localhost:8000/docs. Al dirigirte a esta URL se verá la documentación del proyecto con el emulador de peticiones SWAGER.![alt text](static\images\image.png)

## Login con Oauthdir2
Una vez hayas ingresado a la documentación, deberás ingresar dando click al item Authorize e ingresando las credenciales con rol de administrador que proporcionaste anteriormente en las variables de entorno.  
![alt text](static\images\image-1.png)  
![alt text](static\images\image-2.png)

# Probar los endpoints de la API
Una vez autenticado podrás probar las rutas protegidas que aparecen con un candado en la parte derecha.
# Diagrama de tablas de la Base de Datos  
![alt text](static\images\db_diagrams.png)