# Pipeline de extracción de entidades técnicas

Pipeline asíncrono de extracción con Pydantic y LangChain LCEL. Recibe un
párrafo técnico y devuelve tecnologías, criticidad y un resumen validados.

## Requisitos y configuración

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configura `OPENAI_API_KEY` en el entorno o en un archivo `.env` en la raíz del
proyecto. El modelo predeterminado es `gpt-4o-mini`; puedes cambiarlo mediante
`OPENAI_MODEL`. No subas `.env` al repositorio.

## Archivos

- `schemas.py`: enum de criticidad y contrato Pydantic `ExtraccionTecnica`.
- `chain.py`: prompt modular, composición LCEL, salida estructurada y reintento.
  Expone `async process_text(text: str)`, que llama a la cadena con `.ainvoke()`.
- `test_async.py`: mini prueba asíncrona contra el modelo configurado.

## Ejecutar la prueba

```bash
python test_async.py
```

La prueba requiere una clave válida y conectividad con la API de OpenAI.
Imprime el objeto validado como JSON. Los logs INFO muestran el inicio y el
resultado de la validación; si se agotan los dos intentos, se registra el error.

## Ejemplo de salida

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "API con caché en Redis y persistencia en PostgreSQL; un error provoca la caída total del servicio."
}
```
