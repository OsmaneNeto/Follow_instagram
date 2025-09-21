# -*- coding: utf-8 -*-
import json
import csv
from pathlib import Path

# Ajuste os nomes/caminhos se necessÃ¡rio
FOLLOWERS_FILE = "followers_1.json"   # quem te segue
FOLLOWING_FILE = "following.json"     # quem vocÃª segue

# SaÃ­das
OUT_TXT = "nao_te_seguem.txt"
OUT_CSV = "nao_te_seguem.csv"

def load_json(path: str):
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Arquivo nÃ£o encontrado: {path_obj.resolve()}")
    with open(path_obj, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_usernames_generic(data):
    """
    Extrai usernames de diferentes formatos comuns dos dumps do Instagram.
    Retorna um set de strings (minÃºsculas, sem @).
    """
    # Descobrir onde estÃ£o os itens
    items = None
    if isinstance(data, dict):
        for key in (
            "relationships_followers",
            "relationships_following",
            "followers",
            "following",
            "users",
            "accounts",
        ):
            if key in data and isinstance(data[key], list):
                items = data[key]
                break
        # Alguns dumps vÃªm como {"string_list_data": [...]}
        if items is None and isinstance(data.get("string_list_data"), list):
            items = data["string_list_data"]

    if items is None:
        items = data if isinstance(data, list) else []

    users = set()
    for item in items:
        if not isinstance(item, dict):
            continue

        # 1) Campo direto
        username = item.get("username")
        if username:
            users.add(str(username).strip().lstrip("@").lower())
            continue

        # 2) Estrutura com string_list_data
        sld = item.get("string_list_data")
        if isinstance(sld, list) and sld:
            entry = sld[0]
            val = entry.get("value") or entry.get("href") or entry.get("title")
            if val:
                val = str(val).strip()
                if val.startswith("http"):
                    # extrai handle do final da URL
                    val = val.rstrip("/").split("/")[-1]
                users.add(val.lstrip("@").lower())
                continue

        # 3) Alguns formatos tÃªm "name" como @handle
        name = item.get("name")
        if name:
            users.add(str(name).strip().lstrip("@").lower())
            continue

    # Filtra vazios
    return {u for u in users if u}

def main():
    followers_data = load_json(FOLLOWERS_FILE)   # quem te segue
    following_data = load_json(FOLLOWING_FILE)   # quem vocÃª segue

    followers = extract_usernames_generic(followers_data)
    following = extract_usernames_generic(following_data)

    nao_te_seguem = sorted(following - followers)

    # Salvar TXT (um @ por linha)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        for u in nao_te_seguem:
            f.write(f"@{u}\n")

    # Salvar CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username"])
        for u in nao_te_seguem:
            writer.writerow([f"@{u}"])

    print(f"Total que vocÃª segue: {len(following)}")
    print(f"Total que te seguem: {len(followers)}")
    print(f"NÃ£o te seguem de volta: {len(nao_te_seguem)}")
    print(f"Arquivos gerados: {OUT_TXT}, {OUT_CSV}")

if __name__ == "__main__":
    main()
