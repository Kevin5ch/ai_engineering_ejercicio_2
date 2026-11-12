"""Pipeline LCEL asíncrono para extraer entidades técnicas."""

from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from schemas import ExtraccionTecnica

logger = logging.getLogger(__name__)

INSTRUCCIONES_FORMATO = """Extrae la información técnica sin inventar datos.
Si no se identifica una tecnología, usa [\"No especificada\"].
Clasifica la criticidad únicamente como baja, media o alta. Si el texto es
ambiguo, explica la incertidumbre en el resumen y usa criticidad media,
salvo que haya evidencia clara de un impacto distinto."""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un analista de sistemas. Devuelve una extracción precisa y "
            "conservadora que cumpla el esquema.\n{instrucciones_formato}",
        ),
        ("human", "Analiza este texto técnico:\n\n{texto}"),
    ]
)


def build_chain(model: Any | None = None):
    """Construye Prompt | salida estructurada | reintento LCEL.

    `.with_retry()` vuelve a ejecutar la cadena si falla el proveedor o la
    validación de la salida. `model` permite inyectar un modelo compatible en
    pruebas.
    """
    if model is None:
        load_dotenv()
        model = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            max_retries=0,
        )

    # Composición LCEL solicitada: prompt -> LLM con salida Pydantic estructurada.
    chain = prompt | model.with_structured_output(ExtraccionTecnica)
    # Si el parser devuelve None o campos incompletos, Pydantic lanza un error
    # para que `.with_retry()` ejecute otra vez la cadena completa.
    async def validate_result(result: Any) -> ExtraccionTecnica:
        return ExtraccionTecnica.model_validate(result)

    chain = chain | RunnableLambda(validate_result)
    return chain.with_retry(
        retry_if_exception_type=(Exception,),
        wait_exponential_jitter=False,
        stop_after_attempt=2,
    )


async def process_text(text: str) -> ExtraccionTecnica:
    """Procesa texto mediante `.ainvoke()` y devuelve el modelo Pydantic."""
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("El texto de entrada no puede estar vacío.")

    logger.info("Iniciando extracción técnica (%d caracteres).", len(cleaned_text))
    try:
        result = await build_chain().ainvoke(
            {"texto": cleaned_text, "instrucciones_formato": INSTRUCCIONES_FORMATO}
        )
    except Exception:
        logger.exception(
            "Falló la extracción o la validación; la cadena agotó los intentos configurados."
        )
        raise
    logger.info("Extracción validada correctamente con Pydantic.")
    return result
