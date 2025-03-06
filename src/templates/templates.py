def get_file_templates(project_name, python_version):
    return {
        'README.md': f"""# {project_name}

## Descripción
Descripción del proyecto aquí.

## Instalación
1. Clone el repositorio
2. Cree un entorno virtual
3. Instale las dependencias: `pip install -r requirements.txt`

## Uso
Instrucciones de uso aquí.
""",
        
        'requirements.txt': """black==22.3.0
flake8==4.0.1
pytest==7.1.1
pre-commit==2.19.0
""",
        
        'environment.yml': f"""name: {project_name}
channels:
  - defaults
  - conda-forge
dependencies:
  - python={python_version}
  - pip
  - black
  - flake8
  - pytest
""",
        
        '.gitignore': """__pycache__/
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
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.idea/
.vscode/
*.log
""",
        
        '.env.example': """# Variables de entorno del proyecto
DEBUG=True
API_KEY=your-api-key-here
""",
        
        'src/__init__.py': '',
        
        'src/main.py': """def main():
    print("¡Bienvenido al proyecto!")

if __name__ == '__main__':
    main()
""",
        
        'config/settings.py': """# Configuración global del proyecto
DEBUG = True
VERSION = '0.1.0'
""",
        
        'tests/__init__.py': '',
        
        'tests/test_integration.py': """def test_example():
    assert True
""",
        
        'docs/README.md': f"""# Documentación de {project_name}

## Estructura del Proyecto
- `src/`: Código fuente
- `config/`: Archivos de configuración
- `tests/`: Pruebas unitarias y de integración
- `docs/`: Documentación detallada

## Guías de Desarrollo
1. Instalar dependencias
2. Configurar pre-commit
3. Ejecutar pruebas
""",

        'documentation.txt': f"""Proyecto: {project_name}
Versión de Python: {python_version}

ESTRUCTURA DEL PROYECTO
---------------------
La estructura sigue las mejores prácticas de Python:
- src/: Código fuente principal
- config/: Configuraciones globales
- tests/: Pruebas automatizadas
- docs/: Documentación

CONFIGURACIÓN DEL ENTORNO
-----------------------
1. Crear entorno Conda:
   conda env create -f environment.yml
   
2. Activar entorno:
   conda activate {project_name}
   
3. Instalar herramientas de calidad:
   pip install -r requirements.txt
   
4. Configurar pre-commit:
   pre-commit install

INTEGRACIÓN CONTINUA
------------------
1. Ejecutar pruebas:
   python -m pytest tests/
   
2. Verificar estilo:
   black src/
   flake8 src/
"""
    }
