import os
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class ProjectGenerator:
    def __init__(self, project_name: str, python_version: str):
        """
        Inicializa el generador solo con nombre y versión.
        La ruta se solicitará durante la ejecución.
        """
        self.project_name = project_name
        self.python_version = python_version
        self.project_path = None
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Configuración mejorada del sistema de logging"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{self.project_name}_generation.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_file)),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(self.project_name)

    def solicitar_ruta_proyecto(self) -> Tuple[bool, str]:
        """
        Solicita y valida la ruta de destino para el nuevo proyecto.
        Retorna un tuple (True, ruta_validada) si la validación es exitosa,
        o (False, mensaje_error) en caso de fallo.
        """
        try:
            while True:
                self.logger.info("Solicitando ruta del proyecto al usuario")
                ruta = input("\n¿En qué carpeta desea crear el nuevo proyecto?: ").strip()
                
                if not ruta:
                    self.logger.warning("Usuario proporcionó ruta vacía")
                    print("Error: Debe especificar una ruta.")
                    continue

                # Expandir y resolver ruta
                ruta = os.path.expanduser(os.path.expandvars(ruta))
                ruta_path = Path(ruta).resolve()
                self.logger.debug(f"Ruta expandida y resuelta: {ruta_path}")
                
                # Validar que no sea subdirectorio del generador
                generator_path = Path(__file__).parent.parent.resolve()
                if generator_path in ruta_path.parents or ruta_path == generator_path:
                    self.logger.warning(f"Intento de crear proyecto en directorio del generador: {ruta_path}")
                    print("Error: No se puede crear el proyecto dentro del directorio del generador.")
                    continue

                # Verificar/crear directorio
                if not ruta_path.exists():
                    self.logger.info(f"Directorio no existente: {ruta_path}")
                    crear = input(f"La carpeta {ruta} no existe. ¿Desea crearla? (s/N): ").lower()
                    if crear == 's':
                        try:
                            os.makedirs(ruta_path, exist_ok=True)
                            self.logger.info(f"Directorio creado exitosamente: {ruta_path}")
                        except Exception as e:
                            self.logger.error(f"Error al crear directorio: {e}")
                            print(f"Error: No se pudo crear el directorio: {e}")
                            continue
                    else:
                        self.logger.info("Usuario decidió no crear el directorio")
                        continue

                # Verificar permisos
                if not os.access(ruta_path, os.W_OK):
                    self.logger.error(f"Sin permisos de escritura en: {ruta_path}")
                    print(f"Error: No tiene permisos de escritura en {ruta}")
                    continue

                self.logger.info(f"Ruta validada exitosamente: {ruta_path}")
                return True, str(ruta_path)

        except Exception as e:
            self.logger.error(f"Error inesperado al procesar la ruta: {e}")
            return False, f"Error inesperado: {e}"

    def validate_parameters(self) -> bool:
        """
        Valida todos los parámetros del proyecto y configura las rutas necesarias.
        """
        try:
            self.logger.info("Iniciando validación de parámetros")
            
            # Validar nombre del proyecto
            if not self.project_name.isidentifier():
                error_msg = f"Nombre de proyecto inválido: {self.project_name}"
                self.logger.error(error_msg)
                print(f"Error: {error_msg}")
                return False
            self.logger.info(f"Nombre de proyecto validado: {self.project_name}")
            
            # Validar versión de Python
            if not self._is_valid_python_version(self.python_version):
                error_msg = f"Versión de Python no soportada: {self.python_version}"
                self.logger.error(error_msg)
                print(f"Error: {error_msg}")
                return False
            self.logger.info(f"Versión de Python validada: {self.python_version}")
            
            # Solicitar y validar ruta del proyecto
            success, ruta = self.solicitar_ruta_proyecto()
            if not success:
                self.logger.error(f"Error en la validación de ruta: {ruta}")
                print(f"Error: {ruta}")
                return False
            
            # Establecer y validar ruta completa del proyecto
            self.project_path = Path(ruta) / self.project_name
            self.logger.info(f"Ruta completa del proyecto: {self.project_path}")
            
            if self.project_path.exists():
                if any(self.project_path.iterdir()):
                    self.logger.warning(f"Directorio existente y no vacío: {self.project_path}")
                    sobrescribir = input(
                        f"\nEl directorio {self.project_path} ya existe y no está vacío.\n"
                        "¿Desea sobrescribirlo? (s/N): "
                    ).lower()
                    if sobrescribir != 's':
                        self.logger.info("Usuario canceló la sobrescritura del directorio")
                        return False
                    self.logger.info("Usuario confirmó sobrescribir directorio existente")
            
            self.logger.info("Todos los parámetros validados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inesperado durante la validación: {e}")
            print(f"Error inesperado: {e}")
            return False

    def _is_valid_python_version(self, version: str) -> bool:
        """Validación de versión de Python"""
        try:
            major, minor = map(int, version.split('.'))
            return major == 3 and 6 <= minor <= 12
        except ValueError:
            return False

    def create_project_structure(self) -> bool:
        """Creación de la estructura del proyecto con manejo de errores mejorado"""
        try:
            # Mostrar resumen antes de comenzar
            print("\nSe creará el proyecto con la siguiente configuración:")
            print(f"Nombre: {self.project_name}")
            print(f"Ubicación: {self.project_path}")
            print(f"Versión Python: {self.python_version}")
            
            confirmar = input("\n¿Desea continuar? (S/n): ").lower()
            if confirmar == 'n':
                self.logger.info("Operación cancelada por el usuario")
                return False

            # Limpiar directorio si existe y se confirmó sobrescribir
            if self.project_path.exists() and any(self.project_path.iterdir()):
                self.logger.info("Limpiando directorio existente")
                for item in self.project_path.glob('*'):
                    if item.is_file():
                        item.unlink()
                    else:
                        import shutil
                        shutil.rmtree(item)

            # Crear directorios base
            directories = [
                self.project_path,
                self.project_path / 'src',
                self.project_path / 'config',
                self.project_path / 'tests',
                self.project_path / 'docs'
            ]
            
            for directory in directories:
                self._create_directory(directory)

            self._create_project_files()
            self._create_versioning_files()
            self._init_git()
            
            # Generar documentación y mostrar resumen
            if not self.generate_documentation():
                self.logger.warning("No se pudo generar la documentación completa")
            
            # Ejecutar post-proceso
            if not self.post_process():
                self.logger.warning("No se completó el post-proceso correctamente")
            
            self._show_final_summary()
            
            print("\nEstructura del proyecto creada exitosamente.")
            print(f"Ubicación: {self.project_path}")
            
            self.logger.info(f"Proyecto {self.project_name} creado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error durante la creación del proyecto: {e}")
            print(f"\nError: No se pudo crear el proyecto: {e}")
            return False

    def generate_documentation(self) -> bool:
        """Genera documentación detallada del proyecto."""
        try:
            from datetime import datetime
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            content = f"""DOCUMENTACIÓN DEL PROYECTO
Generado: {fecha}

1. INFORMACIÓN GENERAL
----------------------
Nombre del proyecto: {self.project_name}
Ubicación: {self.project_path}
Versión de Python: {self.python_version}

2. ESTRUCTURA DEL PROYECTO
--------------------------
{self.project_name}/
├── src/         - Código fuente principal
├── config/      - Configuraciones globales
├── tests/       - Pruebas unitarias e integración
└── docs/        - Documentación del proyecto

3. CONFIGURACIÓN DEL ENTORNO
----------------------------
1. Crear y activar el entorno Conda:
   conda env create -f environment.yml
   conda activate {self.project_name}

2. Instalar dependencias adicionales:
   pip install -r requirements.txt

3. Configurar herramientas de desarrollo:
   pre-commit install

4. CONTROL DE VERSIONES
-----------------------
- Repositorio Git inicializado
- Archivo .gitignore configurado
- Hooks de pre-commit instalados para:
  * Black (formateo de código)
  * Flake8 (análisis estático)
  * isort (ordenamiento de imports)

5. HERRAMIENTAS DE CALIDAD
--------------------------
- Black: Formateo automático de código
  * Configurado en pyproject.toml
  * Longitud máxima de línea: 88 caracteres

- Flake8: Análisis estático de código
  * Configurado en .flake8
  * Integrado con docstring checks

- pytest: Framework de pruebas
  * Directorio de pruebas: ./tests
  * Configuración en pyproject.toml

6. SIGUIENTES PASOS
-------------------
1. Revise la documentación en docs/
2. Configure su editor (VSCode/PyCharm)
3. Active el entorno virtual
4. Instale las dependencias
5. Ejecute las pruebas iniciales
"""
            # Crear archivo de documentación
            doc_path = self.project_path / "documentation.txt"
            self._create_file(doc_path, content)
            self.logger.info("Documentación generada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al generar la documentación: {e}")
            return False

    def post_process(self) -> bool:
        """Ejecuta pasos posteriores a la creación del proyecto con feedback en tiempo real."""
        try:
            # Definir las rutas completas
            vscode_path = r"C:\Users\pepec\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"
            self.logger.info(f"Usando VS Code desde: {vscode_path}")
            
            print("\n=== Configuración del Entorno ===")
            
            instalar = input("\n¿Desea instalar automáticamente las dependencias del entorno? (s/N): ").strip().lower()
            if instalar == 's':
                try:
                    # Verificar si conda está disponible
                    try:
                        conda_version = subprocess.run(
                            ['conda', '--version'], 
                            capture_output=True, 
                            text=True, 
                            check=True
                        )
                        print(f"\nConda detectado: {conda_version.stdout.strip()}")
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("\nError: Conda no está disponible. Asegúrese de que está instalado y en el PATH.")
                        return False

                    print("\nActualizando entorno Conda...")
                    self.logger.info("Iniciando actualización del entorno Conda")
                    
                    # Mostrar proceso de creación del entorno
                    process = subprocess.Popen(
                        ["conda", "env", "create", "-f", "environment.yml"],
                        cwd=self.project_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )

                    # Mostrar salida en tiempo real
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(output.strip())
                    
                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(process.returncode, process.args)

                    print("\nInstalando dependencias con pip...")
                    self.logger.info("Instalando dependencias con pip")
                    
                    # Mostrar proceso de instalación de dependencias
                    process = subprocess.Popen(
                        ["pip", "install", "-r", "requirements.txt"],
                        cwd=self.project_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )

                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(output.strip())

                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(process.returncode, process.args)

                    # Verificar y configurar pre-commit con feedback
                    print("\nVerificando pre-commit...")
                    try:
                        subprocess.run(["pre-commit", "--version"], check=True, capture_output=True)
                        print("Configurando pre-commit hooks...")
                        result = subprocess.run(
                            ["pre-commit", "install"],
                            cwd=self.project_path,
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        print(result.stdout)
                        self.logger.info("pre-commit hooks instalados exitosamente")
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("Nota: pre-commit no está instalado. Se omitirá su configuración.")
                        self.logger.warning("pre-commit no disponible, configuración omitida")

                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Error durante la instalación: {e}")
                    print(f"\nError en el proceso: {e}")
                    if self._should_rollback():
                        self.rollback_changes()
                    return False

            # Preguntar por apertura en VS Code
            abrir_vscode = input("\n¿Desea abrir el proyecto en VS Code? (s/N): ").strip().lower()
            if abrir_vscode == 's':
                try:
                    print("\nConfigurando VS Code para usar Conda en PowerShell...")
                    
                    # Crear configuración para VS Code con PowerShell
                    vscode_settings_dir = self.project_path / ".vscode"
                    vscode_settings_dir.mkdir(exist_ok=True)
                    
                    settings = {
                        "terminal.integrated.defaultProfile.windows": "PowerShell",
                        "terminal.integrated.profiles.windows": {
                            "PowerShell": {
                                "source": "PowerShell",
                                "args": [
                                    "-NoExit",
                                    "-Command",
                                    f"conda activate {self.project_name}"
                                ]
                            }
                        }
                    }
                    
                    # Guardar configuración
                    with open(vscode_settings_dir / "settings.json", 'w') as f:
                        import json
                        json.dump(settings, f, indent=4)
                    
                    if os.path.exists(vscode_path):
                        # Abrir VS Code en una nueva ventana sin cerrar la actual
                        subprocess.run([
                            vscode_path,
                            "--new-window",  # Forzar nueva ventana
                            str(self.project_path),  # Abrir carpeta del proyecto
                        ], check=True)
                        
                        # Esperar un momento y luego abrir documentation.txt
                        import time
                        time.sleep(2)
                        doc_path = self.project_path / "documentation.txt"
                        subprocess.run([
                            vscode_path,
                            "--reuse-window",
                            str(doc_path)
                        ], check=True)
                        
                        self.logger.info("VS Code abierto con terminal PowerShell y Conda")
                    else:
                        print(f"\nNota: VS Code no encontrado en {vscode_path}")
                        print("Intentando con el comando 'code' del PATH...")
                        subprocess.run(['code', "--new-window", str(self.project_path)], check=True)
                        time.sleep(2)
                        subprocess.run(['code', "--reuse-window", str(doc_path)], check=True)
                        self.logger.info("VS Code abierto usando PATH")

                except Exception as e:
                    print(f"\nError al abrir VS Code: {e}")
                    self.logger.error(f"Error al abrir VS Code: {e}")

            self.logger.info("Post-proceso completado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error durante el post-proceso: {e}")
            print(f"\nError durante el post-proceso: {e}")
            if self._should_rollback():
                self.rollback_changes()
            return False

    def _should_rollback(self) -> bool:
        """Pregunta al usuario si desea realizar rollback en caso de error."""
        response = input("\n¿Desea revertir los cambios realizados? (s/N): ").strip().lower()
        return response == 's'

    def rollback_changes(self):
        """Revierte los cambios realizados en caso de error."""
        try:
            print("\nRevirtiendo cambios...")
            self.logger.info("Iniciando rollback de cambios")
            
            if self.project_path.exists():
                import shutil
                shutil.rmtree(self.project_path)
                self.logger.info(f"Directorio del proyecto eliminado: {self.project_path}")
            
            print("Cambios revertidos exitosamente.")
            self.logger.info("Rollback completado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error durante el rollback: {e}")
            print(f"\nError: No se pudieron revertir todos los cambios: {e}")

    def _show_final_summary(self):
        """Muestra un resumen final con instrucciones útiles."""
        summary = f"""
¡Proyecto {self.project_name} creado exitosamente!

📁 Ubicación: {self.project_path}

El entorno Conda se está configurando en una nueva ventana.
Si no se abrió automáticamente, siga estos pasos:

1. Abra Anaconda Prompt y navegue al proyecto:
   cd {self.project_path}

2. Cree y active el entorno:
   conda env create -f environment.yml
   conda activate {self.project_name}

3. Instale dependencias adicionales:
   pip install -r requirements.txt

4. Configure Git y pre-commit:
   git init
   pre-commit install

5. Revise la documentación:
   documentation.txt - Para una guía detallada
   README.md - Para instrucciones básicas
   docs/ - Para documentación adicional

Para comenzar a desarrollar:
1. Active el entorno: conda activate {self.project_name}
2. Ejecute las pruebas: pytest
3. Comience a codificar en src/main.py
"""
        print(summary)
        self.logger.info("Resumen final mostrado al usuario")

    def _create_directory(self, path: Path):
        try:
            os.makedirs(path, exist_ok=True)
            self.logger.info(f"Creado directorio: {path}")
        except Exception as e:
            self.logger.error(f"Error al crear directorio {path}: {e}")

    def _create_file(self, path: Path, content: str):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Creado archivo: {path}")
        except Exception as e:
            self.logger.error(f"Error al crear archivo {path}: {e}")

    def _create_versioning_files(self):
        """Crea archivos de configuración para versionado y herramientas de calidad"""
        try:
            self.logger.info("Creando archivos de configuración para versionado y calidad")
            
            versioning_files = {
                '.gitignore': """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/

# Coverage
.coverage
coverage.xml
htmlcov/

# Environments
.env
.env.*
.venv/
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.hypothesis/

# Logs
*.log
logs/
""",
                '.env.example': """# Configuración del proyecto
PROJECT_NAME={self.project_name}
PYTHON_VERSION={self.python_version}

# Configuración de la base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/db_name

# Configuración de la aplicación
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=app.log
""",
                'pyproject.toml': f"""[tool.black]
line-length = 88
target-version = ['py{self.python_version.replace(".", "")}']
include = '\\.pyi?$'
extend-exclude = '''
# Carpetas a excluir
/(
    \\.git
    | \\.mypy_cache
    | \\.venv
    | build
    | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88
skip = [".git", ".venv"]

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --cov=src"
testpaths = ["tests"]
""",
                '.flake8': """[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    .venv,
    .eggs
per-file-ignores =
    __init__.py:F401,F403
    tests/*:S101,S105,S404,S603
max-complexity = 10
""",
                '.pre-commit-config.yaml': """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: check-yaml
    -   id: check-json
    -   id: check-added-large-files
    -   id: end-of-file-fixer
    -   id: trailing-whitespace
    -   id: check-merge-conflict
    -   id: debug-statements

-   repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
    -   id: black
        language_version: python3

-   repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
    -   id: flake8
        additional_dependencies: [
            'flake8-docstrings',
            'flake8-bugbear',
            'flake8-comprehensions',
            'flake8-simplify'
        ]
"""
            }
            
            for filename, content in versioning_files.items():
                self._create_file(self.project_path / filename, content)
                
            self.logger.info("Archivos de configuración creados exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al crear archivos de configuración: {e}")
            raise

    def _init_git(self):
        """Inicializa el repositorio Git y configura pre-commit"""
        try:
            # Inicializar Git
            subprocess.run(['git', 'init'], cwd=self.project_path, check=True)
            self.logger.info("Repositorio Git inicializado")

            # Configurar pre-commit si está disponible
            try:
                subprocess.run(['pre-commit', '--version'], check=True)
                subprocess.run(['pre-commit', 'install'], cwd=self.project_path, check=True)
                self.logger.info("pre-commit hooks instalados")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.warning("pre-commit no está instalado, saltando configuración de hooks")
                
        except Exception as e:
            self.logger.error(f"Error al inicializar Git: {e}")
            raise

    def _create_project_files(self):
        files_content = self._get_file_templates()
        for file_path, content in files_content.items():
            self._create_file(self.project_path / file_path, content)

    def _get_file_templates(self) -> Dict[str, str]:
        """Retorna las plantillas de archivos para el proyecto."""
        import datetime
        
        return {
            'README.md': f"""# {self.project_name}

## Descripción
Descripción detallada del proyecto aquí.

## Instalación
1. Clone el repositorio
2. Cree un entorno virtual:
   ```bash
   conda env create -f environment.yml
   conda activate {self.project_name}
   ```
3. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
Instrucciones de uso aquí.
""",
            'requirements.txt': """black==22.3.0
flake8==4.0.1
pytest==7.1.1
pre-commit==2.19.0
python-dotenv==0.20.0
""",
            'environment.yml': f"""name: {self.project_name}
channels:
  - defaults
  - conda-forge
dependencies:
  - python={self.python_version}
  - pip
  - black
  - flake8
  - pytest
  - pre-commit
""",
            '.gitignore': """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environments
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log
""",
            'src/__init__.py': '',
            'src/main.py': f'''#!/usr/bin/env python3
"""
{self.project_name} - Descripción corta aquí

Author: Tu Nombre
Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
"""

def main():
    """Punto de entrada principal de la aplicación."""
    print("¡Bienvenido a {self.project_name}!")

if __name__ == '__main__':
    main()
''',
            'tests/__init__.py': '',
            'tests/test_main.py': """import pytest

def test_example():
    \"\"\"Test de ejemplo.\"\"\"
    assert True
""",
            'docs/README.md': f"""# Documentación de {self.project_name}

## Estructura del Proyecto
- `src/`: Código fuente
- `config/`: Archivos de configuración
- `tests/`: Pruebas unitarias y de integración
- `docs/`: Documentación detallada

## Configuración del Entorno
1. Crear entorno virtual
2. Instalar dependencias
3. Configurar pre-commit

## Guías de Desarrollo
[Incluir guías específicas del proyecto aquí]
""",
            '.env.example': """# Variables de entorno del proyecto
DEBUG=True
API_KEY=your-api-key-here
"""
        }

def solicitar_nombre_proyecto() -> str:
    """Solicita y valida el nombre del proyecto"""
    while True:
        nombre = input("\nIngrese el nombre del proyecto: ").strip()
        if not nombre:
            print("Error: El nombre no puede estar vacío.")
            continue
        if not nombre.isidentifier():
            print("Error: El nombre debe ser un identificador válido de Python (solo letras, números y guiones bajos).")
            continue
        return nombre

def solicitar_version_python() -> str:
    """Solicita y valida la versión de Python"""
    while True:
        version = input("\nIngrese la versión de Python (Enter para usar 3.9): ").strip()
        if not version:
            return "3.9"
        try:
            major, minor = map(int, version.split('.'))
            if major == 3 and 6 <= minor <= 12:
                return version
            print("Error: Versión no soportada. Use una versión entre 3.6 y 3.12")
        except ValueError:
            print("Error: Formato inválido. Use el formato X.Y (ejemplo: 3.9)")

def main():
    print("\n=== Generador de Proyectos Python ===\n")
    
    # Solicitar parámetros
    project_name = solicitar_nombre_proyecto()
    python_version = solicitar_version_python()
    
    # Crear generador y procesar
    generator = ProjectGenerator(project_name, python_version)
    
    if not generator.validate_parameters():
        return 1
        
    if not generator.create_project_structure():
        return 1
        
    return 0

if __name__ == '__main__':
    exit(main())
