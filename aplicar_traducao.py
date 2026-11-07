# -*- coding: utf-8 -*-
"""Troca o pakchunk0-ps5.pak de um dump PPSA35999 pelo texto em português."""
import hashlib
import os
import sys

PAK_REL = os.path.join("tresgame", "content", "paks", "pakchunk0-ps5.pak")
PAK_MAGIC = 0x5A6F12E1
BUF = 8 * 1024 * 1024
TITLE_ID = "PPSA35999"

if getattr(sys, "frozen", False):
    HERE = os.path.dirname(sys.executable)
else:
    HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "pakchunk0-ps5.pak")


def sha1_file(path, state=None):
    digest = hashlib.sha1()
    total = os.path.getsize(path)
    done = 0
    last = -1
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(BUF)
            if not chunk:
                break
            digest.update(chunk)
            done += len(chunk)
            if state is None:
                continue
            pct = 100 if total <= 0 else min(100, done * 100 // total)
            if pct == last:
                continue
            last = pct
            width = 40
            filled = pct * width // 100
            bar = "#" * filled + "." * (width - filled)
            print("\r%s [%s] %3d%%" % (state, bar, pct), end="", flush=True)
    if state is not None:
        print(flush=True)
    return digest.digest()


def pak_magic_ok(path):
    size = os.path.getsize(path)
    if size < 44:
        return False
    with open(path, "rb") as handle:
        handle.seek(size - 44)
        magic = int.from_bytes(handle.read(4), "little")
    return magic == PAK_MAGIC


def title_ok(app0):
    param = os.path.join(app0, "sce_sys", "param.json")
    if not os.path.isfile(param):
        return True
    with open(param, "r", encoding="utf-8", errors="replace") as handle:
        return TITLE_ID in handle.read()


def apply(app0):
    app0 = os.path.abspath(app0)
    target = os.path.join(app0, PAK_REL)
    if not os.path.isfile(PAYLOAD):
        raise SystemExit("nao achei o pak traduzido ao lado do instalador: " + PAYLOAD)
    if not os.path.isfile(target):
        raise SystemExit("nao achei " + target)
    if not pak_magic_ok(PAYLOAD) or not pak_magic_ok(target):
        raise SystemExit("o pak nao tem o rodape do Kingdom Hearts III")
    if not title_ok(app0):
        raise SystemExit("esta pasta nao e o PPSA35999")

    print("Atualizando os textos.", flush=True)
    print("A janela fica aberta e a barra anda ate terminar.", flush=True)
    print("alvo", target, flush=True)

    payload_size = os.path.getsize(PAYLOAD)
    if os.path.getsize(target) == payload_size:
        print("Conferindo se a traducao ja esta instalada...", flush=True)
        if sha1_file(PAYLOAD) == sha1_file(target):
            print("ja aplicado, nada a fazer")
            return

    print("Lendo a traducao.", flush=True)
    payload_hash = sha1_file(PAYLOAD, "Preparando")
    backup = os.path.join(os.path.dirname(app0), "pakchunk0-ps5.pak.before-pt.bak")
    temp = target + ".pt-apply"
    if os.path.exists(temp):
        os.remove(temp)

    print("Copiando o pak. Pode demorar alguns minutos.", flush=True)
    state = {"done": 0, "total": payload_size, "last": -1}

    def show():
        pct = 100 if state["total"] <= 0 else min(100, state["done"] * 100 // state["total"])
        if pct == state["last"]:
            return
        state["last"] = pct
        width = 40
        filled = pct * width // 100
        bar = "#" * filled + "." * (width - filled)
        print("\rAtualizando [%s] %3d%%" % (bar, pct), end="", flush=True)

    with open(PAYLOAD, "rb") as src, open(temp, "wb") as dst:
        while True:
            chunk = src.read(BUF)
            if not chunk:
                break
            dst.write(chunk)
            state["done"] += len(chunk)
            show()
    print(flush=True)
    print("Conferindo o arquivo...", flush=True)
    if os.path.getsize(temp) != payload_size or sha1_file(temp) != payload_hash:
        os.remove(temp)
        raise SystemExit("a copia saiu diferente da traducao")

    if os.path.exists(backup):
        print("backup ja existe, mantido:", backup)
        os.remove(target)
    else:
        os.replace(target, backup)
        print("backup", backup)
    os.replace(temp, target)
    print("Pronto.", os.path.getsize(target))
    print("No jogo, em Configuracoes, Idiomas, Texto, escolha Portugues.")


def resolve_app0(path):
    path = os.path.abspath(path.strip().strip('"'))
    candidates = []
    current = path
    for _ in range(6):
        candidates.append(current)
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    if os.path.isdir(path):
        try:
            names = os.listdir(path)
        except OSError:
            names = []
        for name in names:
            candidates.append(os.path.join(path, name))
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if os.path.isfile(os.path.join(candidate, PAK_REL)):
            return candidate
    raise SystemExit("nao achei a pasta do jogo (pakchunk0-ps5.pak) em: " + path)


def pause():
    if os.environ.get("KH3_FROM_BAT"):
        return
    try:
        input("\nPressione Enter para sair...")
    except EOFError:
        pass


def pick_app0():
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        return sys.argv[1]
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askdirectory(title="Selecione a pasta do Kingdom Hearts III (app0)")
        root.destroy()
        return path
    except Exception:
        print("Cole o caminho da pasta do jogo.")
        try:
            return input("Pasta app0: ").strip().strip('"')
        except EOFError:
            return ""


if __name__ == "__main__":
    code = 0
    try:
        path = pick_app0()
        if not path:
            print("Nenhuma pasta informada.")
            code = 1
        else:
            apply(resolve_app0(path))
    except SystemExit as exc:
        if exc.code not in (0, None):
            if isinstance(exc.code, int):
                code = exc.code
            else:
                print(exc.code)
                code = 1
    except Exception as exc:
        print("ERRO:", exc)
        code = 1
    pause()
    sys.exit(code)
