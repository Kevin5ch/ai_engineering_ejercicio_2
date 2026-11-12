"""Esquemas validados para la extracción de información técnica."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class NivelCriticidad(StrEnum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class ExtraccionTecnica(BaseModel):
    """Contrato de salida del pipeline."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    tecnologias: list[str] = Field(
        min_length=1,
        description="Tecnologías, lenguajes, servicios o herramientas mencionados.",
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Criticidad del problema: baja, media o alta."
    )
    resumen_tecnico: str = Field(
        min_length=1,
        description="Resumen técnico breve y fiel al texto proporcionado.",
    )
