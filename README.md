# iMet-XQ2

Proyecto para trabajar con datos y comunicación del sistema **iMet-XQ2**.

## Requisitos

Antes de comenzar, asegúrate de tener instalado:

- Git
- Conda, mediante Anaconda o Miniconda
- Visual Studio Code
- Extensión de Python para Visual Studio Code

## Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/imet-xq2.git
```

Entrar a la carpeta del proyecto:

```bash
cd imet-xq2
```

## Crear el entorno Conda

El proyecto incluye un archivo `environment.yml` con las dependencias necesarias.

Para crear el entorno:

```bash
conda env create -f environment.yml
```

Luego activar el entorno:

```bash
conda activate imet-xq2
```

Puedes comprobar la versión de Python con:

```bash
python --version
```

## Configuración en Visual Studio Code

Abrir la carpeta del proyecto en VS Code:

```bash
code .
```

Luego seleccionar el entorno de Python:

1. Presionar `Ctrl + Shift + P`
2. Buscar `Python: Select Interpreter`
3. Seleccionar el entorno `imet-xq2`

La terminal debería mostrar algo similar a:

```text
(imet-xq2) PS C:\...\imet-xq2>
```

## Estructura del proyecto

```text
imet-xq2/
│
├── src/
│   └── main.py
│
├── docs/
│
├── tests/
│
├── .gitignore
├── environment.yml
└── README.md
```

- `src/`: código fuente del proyecto.
- `tests/`: pruebas del software.
- `docs/`: documentación adicional.
- `environment.yml`: dependencias del entorno Conda.

## Ejecutar el proyecto

Con el entorno activado:

```bash
python src/main.py
```

## Agregar nuevas dependencias

Si necesitas instalar una nueva librería, primero activa el entorno:

```bash
conda activate imet-xq2
```

Luego instala la dependencia. Por ejemplo:

```bash
conda install numpy
```

o:

```bash
pip install pyserial
```

Después de agregar nuevas dependencias, actualizar `environment.yml`:

```bash
conda env export --no-builds > environment.yml
```

El archivo actualizado debe ser incluido en el siguiente commit para que los demás miembros del equipo puedan actualizar su entorno.

## Actualizar un entorno existente

Si `environment.yml` fue modificado:

```bash
conda env update -f environment.yml --prune
```

## Flujo de trabajo con Git

Antes de comenzar a trabajar:

```bash
git pull
```

Después de realizar cambios:

```bash
git status
git add .
git commit -m "Descripción de los cambios"
git push
```

## Colaboración

Para evitar conflictos:

- Ejecutar `git pull` antes de comenzar a trabajar.
- Realizar commits pequeños y descriptivos.
- No subir archivos temporales ni entornos virtuales.
- Mantener actualizado `environment.yml` cuando se agreguen dependencias.
- Para cambios importantes, se recomienda trabajar utilizando ramas.

Ejemplo:

```bash
git checkout -b nombre-rama
```

Luego:

```bash
git add .
git commit -m "Descripción del cambio"
git push -u origin nombre-rama
```

## Autores

Proyecto desarrollado por el equipo de SPEL.

## Licencia

Agregar aquí la licencia del proyecto si corresponde.