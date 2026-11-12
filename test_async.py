"""Mini prueba asíncrona del pipeline contra el modelo configurado."""

import asyncio
import json
import logging

from chain import process_text


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    text = (
        "La API en FastAPI usa PostgreSQL y Redis. Un error provoca caída total "
        "del servicio."
    )
    result = await process_text(text)
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
