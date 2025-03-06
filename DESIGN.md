# Diseño del Generador de Proyectos Python

## Objetivo del Generador

Esta herramienta permite generar automáticamente la estructura completa de un nuevo proyecto Python en una ubicación externa especificada por el usuario. El generador crea una estructura estandarizada que sigue las mejores prácticas de desarrollo en Python.

## Estructura del Proyecto Generado

### Directorios Principales
```
proyecto/
├── src/               # Código fuente principal
├── config/           # Archivos de configuración
├── tests/            # Pruebas unitarias y de integración
└── docs/             # Documentación del proyecto
```

### Archivos Generados
- `README.md`: Documentación principal del proyecto
- `requirements.txt`: Dependencias del proyecto
- `environment.yml`: Configuración del entorno Conda
- `.gitignore`: Archivos a ignorar por Git
- `.env.example`: Plantilla de variables de entorno
- `setup.py`: Configuración de instalación del paquete
- `pyproject.toml`: Configuración de herramientas de desarrollo

## Flujo de Trabajo General

1. **Solicitud de Parámetros**
   - Nombre del proyecto (requerido)
   - Ubicación del proyecto (ruta externa)
   - Versión de Python (por defecto: 3.9)

2. **Validación**
   - Verificar nombre válido del proyecto
   - Confirmar existencia y permisos de la ruta
   - Validar versión de Python compatible
   - Comprobar que la ruta no sea dentro del generador

3. **Creación de Estructura**
   - Generar directorios principales
   - Crear archivos base
   - Inicializar repositorio Git
   - Configurar entorno virtual (opcional)

4. **Configuración de Herramientas**
   - Black para formateo de código
   - Flake8 para linting
   - isort para ordenar imports
   - pytest para testing
   - pre-commit hooks

## Herramientas y Configuración

### Herramientas de Calidad
- **Black**: Formateo automático de código
  ```toml
  [tool.black]
  line-length = 88
  target-version = ['py39']
  ```

- **Flake8**: Linting y estilo
  ```ini
  [flake8]
  max-line-length = 88
  extend-ignore = E203
  ```

- **isort**: Ordenamiento de imports
  ```toml
  [tool.isort]
  profile = "black"
  multi_line_output = 3
  ```

### Pre-commit Hooks
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## Requisitos Adicionales

1. **Manejo de Errores**
   - Captura y registro de excepciones
   - Mensajes de error claros para el usuario
   - Rollback en caso de fallos

2. **Sistema de Logging**
   - Registro de todas las operaciones
   - Archivo de log separado por proyecto
   - Niveles de log (INFO, ERROR, DEBUG)

3. **Opciones Adicionales**
   - Instalación automática de dependencias
   - Creación de entorno virtual
   - Inicialización de Git
   - Apertura en editor (VSCode/PyCharm)

## Notas de Implementación

- Usar `pathlib` para manejo de rutas
- Implementar validaciones robustas
- Mantener código modular y extensible
- Documentar cada función y módulo
- Incluir tests para cada funcionalidad
