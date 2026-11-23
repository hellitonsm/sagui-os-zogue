#!/usr/bin/env python3
"""H36 - desligar e reiniciar.

Critério: o kernel acha as tabelas ACPI e o objeto _S5_; o botão de energia
da barra de cima abre a janela Energia; Desligar faz o QEMU terminar sozinho
e grava antes o pendrive montado (arquivo presente e FAT32 íntegro);
Reiniciar volta ao boot.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qemu import Maquina, verificar, abrir_terminal, criar_pendrive, pendrive_qemu, mtype, janela  # noqa: E402

BOTAO_ENERGIA = (1024 - 21 * 8 - 10 - 30 + 10, 12)


def main():
    pen = criar_pendrive("h36-pen", rotulo="DADOS")
    with Maquina("h36", "ide", extras=["-device", "usb-ehci,id=ehci"] + pendrive_qemu(pen)) as m:
        m.esperar_serial("area de trabalho no ar", 120)
        abrir_terminal(m)   # o Terminal agora abre pelo ícone (D039)
        s = m.serial()
        verificar("[ACPI] PM1a" in s and "S5 ok" in s, "tabelas ACPI e o _S5_ encontrados")
        time.sleep(1)
        m.comando("montar")
        m.comando("echo guardado antes de desligar > /usb/energia.txt")
        m.clique(*BOTAO_ENERGIA)
        m.esperar_serial("energia: janela aberta", 15)
        verificar(True, "o botão de energia da barra abre a janela Energia")
        time.sleep(0.5)
        m.captura("H36-energia")
        j = janela(m.serial(), "Energia")
        m.clique(j["x"] + 20 + 50, j["y"] + 110 + 15)          # Desligar
        m.esperar_serial("[ZOGUE] desligando", 15)
        for _ in range(100):
            if m.proc.poll() is not None:
                break
            time.sleep(0.1)
        verificar(m.proc.poll() is not None, "o QEMU desligou sozinho (ACPI)")
        verificar("desligar pelo ACPI nao funcionou" not in m.serial(), "sem cair no aviso de desligar manual")
    verificar(mtype(pen, "/energia.txt").strip() == b"guardado antes de desligar", "o arquivo foi gravado no pendrive antes de desligar")
    # fsck.vfat não aceita deslocamento: confere a partição copiada para um arquivo à parte.
    part = pen + ".part"
    subprocess.run(["dd", f"if={pen}", f"of={part}", "bs=1M", "skip=1", "status=none"], check=True)
    r = subprocess.run(["fsck.vfat", "-n", part], capture_output=True, text=True)
    verificar(r.returncode == 0, "fsck.vfat: o FAT32 está íntegro depois de desligar")
    os.remove(part)

    with Maquina("h36r", "ide", reiniciar=True) as m:
        m.esperar_serial("area de trabalho no ar", 120)
        abrir_terminal(m)   # o Terminal agora abre pelo ícone (D039)
        time.sleep(1)
        m.digitar("reiniciar")
        m.tecla("ret")
        fim = time.time() + 120
        while time.time() < fim and "[ZOGUE] reiniciando" not in m.serial():
            time.sleep(0.2)
        verificar("[ZOGUE] reiniciando" in m.serial(), "o kernel registrou o reinício")
        abrir_terminal(m)   # segundo boot: o Terminal não abre sozinho (D039)
        s = m.serial()
        verificar("[ZOGUE] reiniciando" in s and s.count("sagui:/$") >= 2, "reiniciar volta ao boot e ao shell")
    return 0


if __name__ == "__main__":
    sys.exit(main())
