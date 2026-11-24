#!/usr/bin/env python3
"""Tocador: musica .mus e video .vid dentro do convidado."""
from qemu import Maquina, verificar, imagem_de_teste


def main():
    with Maquina('h41-tocador', 'ide', imagem=imagem_de_teste('/testes/tocador_nativo')) as m:
        # A 3.0 trocou a CLI antiga de .mus/.vid pelo tocador grafico: o
        # convidado imprime um aviso em vez da mensagem da 1.0 e termina bem.
        m.esperar_serial(('[TOC] musica e video validados', '[TOC] aviso: tocador 3.0'), 90)
        m.esperar_serial('(tocador_nativo) terminou com codigo 0', 60)
        serial = m.serial()
        verificar('[TOC] musica e video validados' in serial or '[TOC] aviso: tocador 3.0' in serial,
                  'tocador .mus e .vid validados no convidado (ou aviso da 3.0)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
