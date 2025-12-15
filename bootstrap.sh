#!/bin/bash

# --- 1. Cargar Variables del .env ---
echo "--- 1. Cargando configuración desde el archivo .env ---"
set -a
source /vagrant/.env 
set +a

PROJECT_DIR="/vagrant"
# El entorno virtual se crea en el directorio nativo de Linux
VENV_DIR="/home/vagrant/.venv"

# --- 2. Instalación de Dependencias del Sistema ---
echo "--- 2. Instalando MariaDB, Python y librerías necesarias ---"
sudo apt-get update
# Se añade libmysqlclient-dev que suele ser necesaria para compilar el driver de DB
sudo apt-get install -y mariadb-server python3-pip python3-venv git python3-dev libmysqlclient-dev

# Instalación de Firefox y geckodriver para tests de Selenium
echo "--- Instalando Firefox y geckodriver para Selenium ---"
sudo apt-get install -y firefox
# Descargar geckodriver
wget -q https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz
sudo tar -xzf geckodriver-v0.35.0-linux64.tar.gz -C /usr/local/bin/
sudo chmod +x /usr/local/bin/geckodriver
rm geckodriver-v0.35.0-linux64.tar.gz
echo "✅ Firefox y geckodriver instalados"

# --- 3. Configuración de MariaDB ---
echo "--- 3. Configurando MariaDB ---"
sudo systemctl enable mariadb
sudo systemctl start mariadb

# Esperamos a que la DB esté lista
while ! mysqladmin ping --silent; do
    sleep 1
done

sudo mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS $MARIADB_DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$MARIADB_USER'@'localhost' IDENTIFIED BY '$MARIADB_PASSWORD';
-- Aseguramos que la contraseña sea correcta (por si cambió en el .env)
ALTER USER '$MARIADB_USER'@'localhost' IDENTIFIED BY '$MARIADB_PASSWORD';
GRANT ALL PRIVILEGES ON $MARIADB_DATABASE.* TO '$MARIADB_USER'@'localhost';

CREATE DATABASE IF NOT EXISTS $MARIADB_TEST_DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON $MARIADB_TEST_DATABASE.* TO '$MARIADB_USER'@'localhost';

FLUSH PRIVILEGES;
EOF

echo "✅ MariaDB configurado."


echo "--- Configurando entorno Python y App como usuario 'vagrant' ---"

sudo -u vagrant bash <<EOF

    # Carga las variables nuevamente en el contexto de 'vagrant'
    set -a
    source /vagrant/.env 
    set +a
    
    PROJECT_DIR="/vagrant"
    VENV_DIR="/home/vagrant/.venv"
    # 4a. Crear entorno virtual en /home/vagrant
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        echo "✅ Entorno virtual creado en $VENV_DIR"
    fi

    # 4b. Activar entorno
    source "$VENV_DIR/bin/activate"

    # 4c. Instalar dependencias
    cd "$PROJECT_DIR"
    echo "--- Instalando dependencias (pip) ---"
    pip install -r requirements.txt
    
    echo "--- Instalando Rosemary en modo editable ---"
    pip install -e ./

    # 5. Migraciones
    echo "--- Ejecutando migraciones ---"
    export FLASK_APP=app:create_app

    if [ ! -d "migrations" ]; then
        flask db init
    fi

    # Intentar migrar (ignoramos error si no hay cambios)
    flask db migrate -m "Initial database migration" || echo "No hay cambios en migraciones"
    
    flask db upgrade

    # Seeds
    echo "--- Ejecutando Seeds ---"
    rosemary db:reset -y
    rosemary db:seed -y
    echo "✅ Base de datos inicializada."

    # 6. Lanzamiento
    echo "--- Iniciando Flask en segundo plano ---"
    
    # Matar procesos viejos
    pkill -f 'flask run' || true

    # Lanzar la app y guardar logs en /tmp
    nohup flask run --debug --host=0.0.0.0 > /tmp/flask_app.log 2>&1 &
EOF

echo "✅ Aprovisionamiento completado. Accede en http://localhost:5000"