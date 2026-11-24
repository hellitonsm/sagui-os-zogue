#!/usr/bin/env python3
"""H99 - laço (issue #25, parte 3) de seleção translúcido na área de trabalho.

Ideia e primeira versão: commit 0b3c462, do Robson (ramo area-lixeira, do
código da 1.0), refeito para o código atual.

Critérios:
  - arrastar no vazio desenha um retângulo translúcido: durante o arraste, um
    pixel dentro do laço muda de cor, mas o fundo continua aparecendo (não é
    uma cor sólida);
  - ao soltar, os ícones tocados ficam marcados (o kernel conta quantos);
  - um clique num ícone marca só ele;
  - clicar no vazio desmarca;
  - capturas para a revisão a olho.
"""
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qemu import Maquina, FalhaTeste, verificar, abrir_terminal, cor_do_pixel  # noqa: E402


def marcados(m, desde):
    r = re.findall(r"\[GUI\] laco: .* (\d+) icones marcados", m.serial()[desde:])
    if not r:
        raise FalhaTeste("o laço não terminou")
    return int(r[-1])


def esperar(m, texto, tempo=10, desde=0):
    fim = time.time() + tempo
    while time.time() < fim:
        if texto in m.serial()[desde:]:
            return
        time.sleep(0.2)
    raise FalhaTeste(f"tempo esgotado esperando {texto!r}")


def main():
    with Maquina("h99", "ide", memoria="768M") as m:
        m.esperar_serial("area de trabalho no ar", 120)
        abrir_terminal(m)   # o Terminal agora abre pelo ícone (D039)
        time.sleep(1)
        # O duplo clique no ícone deixa o Terminal marcado (D039). Limpamos a
        # seleção antes da foto de referência: assim o pixel do Terminal na
        # foto é o do fundo, e da para conferir que o clique num ícone o
        # desmarca de volta.
        m.clique(150, 600)
        time.sleep(0.3)
        # O Terminal abre por cima do meio da tela. Os ícones ficam em duas
        # colunas (x de 20 a 116 e de 130 a 226; cada linha desce 92 pixels a
        # partir de y = 40); na segunda há o "Sobre" e, embaixo dele, a
        # Lixeira (H103). O laço vai de (127, 300) a (10, 140), só na primeira
        # coluna: toca Terminal e Editor.
        antes_png = m.captura("H99-0-antes")
        ponto = (122, 250)                      # vazio, dentro do laço (entre as colunas)
        fundo = cor_do_pixel(antes_png, *ponto)

        n = len(m.serial())
        m.mouse_para(127, 300)
        m.monitor("mouse_button 1")             # segura o botão (mouse_mover só move)
        time.sleep(0.2)
        m.mouse_mover(10, 140)
        time.sleep(0.6)
        durante = m.captura("H99-1-laco")
        cor = cor_do_pixel(durante, *ponto)
        dif = sum(abs(a - b) for a, b in zip(cor, fundo))
        verificar(8 < dif < 200, f"o laço é translúcido (fundo {fundo}, com o laço {cor})")
        m.monitor("mouse_button 0")
        esperar(m, "[GUI] laco:", 10, n)
        k = marcados(m, n)
        verificar(k == 2, f"o laço marcou os 2 ícones que tocou ({k})")
        time.sleep(0.6)
        m.captura("H99-2-marcados")

        # Clique num ícone: marca só ele (a Calculadora, índice 4, y de 408 a 504). O
        # destaque pinta o canto vazio da célula; o do Terminal, desmarcado,
        # volta ao fundo. O kernel so registra "[GUI] laco:" quando ha arraste;
        # num clique simples a conferencia e pela cor do destaque.
        sem = cor_do_pixel(antes_png, 24, 422)
        m.clique(68, 440)
        time.sleep(0.8)
        png = m.captura("H99-3-um-icone")
        com = cor_do_pixel(png, 24, 422)
        verificar(sum(abs(a - b) for a, b in zip(com, sem)) > 8, f"o clique marca a Calculadora ({sem} -> {com})")
        verificar(cor_do_pixel(png, 24, 146) == cor_do_pixel(antes_png, 24, 146), "e desmarca o Terminal")

        # Clique no vazio desmarca. Um clique simples na area de trabalho nao
        # gera o log do laço (ele so e escrito quando ha arraste), entao a
        # conferencia e pela cor: os tres icones voltam ao fundo da foto.
        m.clique(150, 600)
        time.sleep(0.8)
        limpo_png = m.captura("H99-4-sem-selecao")
        for x, y in ((24, 146), (24, 238), (24, 422)):
            verificar(cor_do_pixel(limpo_png, x, y) == cor_do_pixel(antes_png, x, y),
                      f"clicar no vazio desmarca tudo (pixel {x},{y})")


if __name__ == "__main__":
    main()
