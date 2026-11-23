#!/usr/bin/env python3
"""H128 - o tema Zogue (a subespécie de sagui que batiza o sistema).

Critério: em Configurações > Aparência, o fundo **Zogue** existe e, ao ser
escolhido, a área de trabalho mostra a mata escura do `zogue.sgi` e o
mascote novo no canto inferior direito: corpo cinza-rosado, dorso
avermelhado e cauda preta (kernel/gui/arte.c).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qemu import Maquina, verificar, janela, cor_do_pixel, tamanho_png  # noqa: E402

POR_COLUNA = (768 - 40) // 92


def icone(i):
    return 20 + (i // POR_COLUNA) * 110 + 48, 40 + (i % POR_COLUNA) * 92 + 32


def regiao_tem(png, x0, y0, x1, y1, alvo, tol=28):
    """Procura a cor alvo (tol) numa região, varrendo de 4 em 4 px."""
    l, a = tamanho_png(png)
    x1 = min(x1, l - 1)
    y1 = min(y1, a - 1)
    for y in range(y0, y1, 4):
        for x in range(x0, x1, 4):
            c = cor_do_pixel(png, x, y)
            if all(abs(c[i] - alvo[i]) <= tol for i in range(3)):
                return True
    return False


def main():
    with Maquina("h128", "ide") as m:
        m.esperar_serial("area de trabalho no ar", 120)
        time.sleep(2)
        m.clique(*icone(7), duplo=True)          # Configurações (7º ícone)
        m.esperar_serial("configuracoes: aberto na aba Relógio", 30)
        j = janela(m.serial(), "Configurações")
        x0, y0 = j["x"], j["y"]
        time.sleep(0.5)
        m.clique(x0 + 10 + 65, y0 + 16 + 40 + 15)              # aba Aparência
        m.esperar_serial("configuracoes: aba Aparência", 10)
        time.sleep(0.4)
        # Zogue: 8º fundo -> linha 1, coluna 3 (X0=190; colunas de 100, linhas de 84)
        m.clique(x0 + 190 + 300 + 45, y0 + 76 + 84 + 48 + 12)
        m.esperar_serial("configuracoes: fundo zogue", 10)
        time.sleep(2)
        png = m.captura("H128-0-zogue")
        l, a = tamanho_png(png)
        verificar(regiao_tem(png, 40, 40, 500, 380, (35, 42, 25)),
                  "o fundo Zogue mostra a mata escura do zogue.sgi")
        verificar(regiao_tem(png, l - 200, a - 200, l - 10, a - 10, (201, 160, 139)),
                  "o mascote tem o corpo cinza-rosado do Zogue")
        verificar(regiao_tem(png, l - 200, a - 200, l - 10, a - 10, (158, 68, 38)),
                  "o mascote tem o dorso avermelhado")
        verificar(regiao_tem(png, l - 200, a - 200, l - 10, a - 10, (20, 18, 16)),
                  "o mascote tem a cauda preta")
    return 0


if __name__ == "__main__":
    sys.exit(main())
