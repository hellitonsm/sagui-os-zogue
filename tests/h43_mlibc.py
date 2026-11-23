#!/usr/bin/env python3
"""Shim C/POSIX do SaguiOS: APIs suportadas e sysdeps no convidado."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qemu import Maquina, verificar, imagem_de_teste, RAIZ  # noqa: E402


def main():
    # O mlibc_nativo é um teste do shim POSIX completo, que exige funções
    # (stdio de FILE*, fcntl, time, mlibc_*) que o shim mínimo do build
    # padrão não oferece; ele é construído só com a toolchain do fork
    # (FORK_TOOLCHAIN=1). Sem o programa no /testes, o teste avisa e não
    # roda, como o H122 faz sem o vídeo de amostra.
    caminho = os.path.join(RAIZ, "build", "rootfs", "testes", "mlibc_nativo")
    if not os.path.exists(caminho):
        print("  AVISO: sem /testes/mlibc_nativo (shim POSIX completo do fork), o contrato POSIX NÃO foi testado")
        return 0
    with Maquina('h43-mlibc', 'ide', imagem=imagem_de_teste('/testes/mlibc_nativo')) as m:
        m.esperar_serial('[MLIBC] sysdeps validos', 120)
        m.esperar_serial('(mlibc_nativo) terminou com codigo 0', 60)
        verificar(True, 'shim POSIX do SaguiOS validada no convidado')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
