import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

PASTA = Path(__file__).resolve().parent
PROFISSIONAIS = {
    "Clínico geral": "Laura Teixeira",
    "Ginecologista": "Marina Farias",
    "Ortopedista": "André Seixas",
    "Endocrinologista": "Renata Monteiro",
}


def main():
    load_dotenv(PASTA / ".env")
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("Preencha MONGODB_URI no arquivo .env do projeto.")

    pacientes = json.loads((PASTA / "pacientes.json").read_text(encoding="utf-8-sig"))
    with MongoClient(uri, serverSelectionTimeoutMS=10000) as cliente:
        banco = cliente["telemedicina"]
        banco.pacientes.create_index("paciente_id", unique=True)
        resultado = banco.pacientes.bulk_write([
            UpdateOne(
                {"paciente_id": paciente["paciente_id"]},
                {"$setOnInsert": paciente},
                upsert=True,
            )
            for paciente in pacientes
        ])
        for especialidade, nome in PROFISSIONAIS.items():
            banco.especialidades.update_one(
                {"_id": especialidade}, {"$setOnInsert": {"nome": especialidade}}, upsert=True
            )
            banco.profissionais.update_one(
                {"_id": especialidade},
                {"$setOnInsert": {"nome": nome, "especialidade": especialidade}},
                upsert=True,
            )

    print(f"Pacientes conferidos: {len(pacientes)}. Novos cadastros: {resultado.upserted_count}.")
    print("Carga de especialidades e profissionais concluída.")


if __name__ == "__main__":
    main()
