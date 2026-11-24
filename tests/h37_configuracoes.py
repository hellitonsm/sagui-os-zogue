#!/usr/bin/env python3
"""H37 - configurações guardadas.

Critério: sem pendrive montado, mudar uma configuração avisa que só vale até
desligar; com pendrive, ela vai para /usb/.saguios/configuracoes.txt; depois
de reiniciar com o mesmo pendrive, ele é montado sozinho (tem configurações
do SaguiOS) e a configuração continua igual.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qemu import Maquina, verificar, abrir_terminal, criar_pendrive, pendrive_qemu, mtype  # noqa: E402


def main():
    pen = criar_pendrive("h37-pen", rotulo="DADOS")
    with Maquina("h37", "ide", reiniciar=True, extras=["-device", "usb-ehci,id=ehci"] + pendrive_qemu(pen)) as m:
        m.esperar_serial("area de trabalho no ar", 120)
        abrir_terminal(m)   # o Terminal agora abre pelo ícone (D039)
        time.sleep(1)
        verificar("montado sozinho" not in m.serial(), "um pendrive sem configurações não é montado sozinho")
        out = m.comando("config teste.sem_pendrive sim")
        verificar("vale até desligar" in out, "sem pendrive montado: avisa que só vale até desligar")
        m.comando("montar")
        out = m.comando("config aparencia.fundo azul")
        verificar("aparencia.fundo = azul" in out and "até desligar" not in out, "com pendrive: a configuração é guardada")
        out = m.comando("config sistema.persistente")
        verificar("= sim" in out, "config diz que há onde guardar")
        m.captura("H37-config")
        m.digitar("reiniciar")
        m.tecla("ret")
        # O QEMU reinicia no mesmo processo e a serial guarda o prompt antigo.
        # Esperamos o aviso do kernel e so depois o boot novo (D039).
        fim = time.time() + 180
        while time.time() < fim and "[ZOGUE] reiniciando" not in m.serial():
            time.sleep(0.2)
        verificar("[ZOGUE] reiniciando" in m.serial(), "o kernel registrou o reinício")
        n = len(m.serial())
        m.esperar_serial("area de trabalho no ar", 120, n)
        m.esperar_serial("montado sozinho", 30, n)
        verificar(True, "depois de reiniciar, o pendrive com configurações é montado sozinho")
        abrir_terminal(m, n)   # o Terminal nao abre sozinho no boot novo (D039)
        time.sleep(1)
        out = m.comando("config aparencia.fundo")
        verificar("aparencia.fundo = azul" in out, "a configuração continua igual depois de reiniciar")
        out = m.comando("config teste.sem_pendrive")
        verificar("= sim" in out, "o que foi mudado antes de montar foi guardado junto na gravação seguinte")
        m.comando("desmontar")
    texto = mtype(pen, "/.saguios/configuracoes.txt").decode("latin-1")
    verificar("aparencia.fundo = azul" in texto, "mtools: o arquivo de configurações está no pendrive")
    return 0


if __name__ == "__main__":
    sys.exit(main())
