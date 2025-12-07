#!/bin/bash

# --- 1. Cargar Variables del .env ---
# Carga las credenciales de la DB y la aplicación desde el archivo unificado .env
echo "--- 1. Cargando configuración desde el archivo .env ---"
set -a
# Usamos el path /vagrant para acceder a los archivos del directorio compartido
source /vagrant/.env 
set +a

PROJECT_DIR="/vagrant"

# --- 2. Instalación de Dependencias del Sistema ---
echo "--- 2. Instalando MariaDB, Python (>=3.10) y utilidades ---"
sudo apt-get update
# python3-dev es necesario para compilar algunas dependencias
sudo apt-get install -y mariadb-server python3-pip python3-venv git python3-dev 

# --- 3. Configuración de MariaDB (Idempotente) ---
echo "--- 3. Configurando MariaDB y creando usuario '$MARIADB_USER' ---"
sudo systemctl enable mariadb
sudo systemctl start mariadb
sleep 5 

# Los comandos SQL deben usar la sintaxis más compatible para asegurar la creación del usuario.
sudo mysql -u root <<EOF
-- 3a. Crear la base de datos
CREATE DATABASE IF NOT EXISTS $MARIADB_DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3b. Crear/Modificar el usuario con la contraseña
-- Usamos la sintaxis estándar para compatibilidad.
CREATE USER IF NOT EXISTS '$MARIADB_USER'@'localhost' IDENTIFIED BY '$MARIADB_PASSWORD';

-- 3c. Asegurar que el plugin de autenticación sea compatible con PyMySQL (si la versión de MariaDB lo requiere)
-- Nota: Si usas una versión reciente de MariaDB, este paso es implícito o usa IDENTIFIED BY.
-- Lo mantenemos simple para evitar el ERROR 1064.

-- 3d. Otorgar permisos sobre la base de datos
GRANT ALL PRIVILEGES ON $MARIADB_DATABASE.* TO '$MARIADB_USER'@'localhost';

-- 3e. Aplicar los cambios
FLUSH PRIVILEGES;
EOF

echo "✅ MariaDB configurado."

# --- 4. Preparación del Entorno Python ---
echo "--- 4. Configurando entorno Python e instalando requirements.txt ---"
cd $PROJECT_DIR

# 4a. Crear y activar el entorno virtual
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# 4b. Instalar dependencias
pip install -r requirements.txt

# 4c. Instalar Rosemary ---
echo "--- Instalando la aplicación en modo editable (Rosemary) ---"
pip install -e ./

# --- 5. Migraciones y Creación de Tablas ---
echo "--- 5. Ejecutando migraciones de Flask (Alembic) ---"
export FLASK_APP=app:create_app
export WORKING_DIR="/vagrant"

# 5a. Inicializar el repositorio de migraciones (si no existe)
if [ ! -d "migrations" ]; then
    flask db init
fi

# 5b. Crear la migración inicial si es necesario
flask db migrate -m "Initial database migration"

# 5c. Aplicar las migraciones. Esto crea las tablas en la base de datos.
flask db upgrade

# Ejecutar el seeder usando el comando rosemary recién instalado
echo "Ejecutando Rosemary DB Seed..."

rosemary db:seed -y

echo "✅ Base de datos inicializada."

# --- 6. Lanzamiento de la Aplicación ---
echo "--- 6. Iniciando la aplicación Flask en segundo plano (Puerto 5000) ---"

# Detener cualquier instancia previa para idempotencia
pkill -f 'flask run --host=0.0.0.0'

# Iniciar la aplicación en segundo plano con nohup
# El .env se carga automáticamente por python-dotenv
nohup flask run --host=0.0.0.0 > /tmp/flask_app.log 2>&1 &

echo "✅ Aprovisionamiento y lanzamiento completados. Accede en http://localhost:5000"
deactivate