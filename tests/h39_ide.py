#!/usr/bin/env python3
"""IDE: executar exemplos Go e Lua na máquina convidada."""
import re
import time
from qemu import Maquina, verificar, abrir_terminal, FalhaTeste


def main():
    with Maquina('h39-ide', 'ide') as m:
        m.esperar_serial('area de trabalho no ar', 120)
        abrir_terminal(m)   # o Terminal agora abre pelo ícone (D039)
        m.comando('ide /exemplos/go/ola.go')
        m.esperar_serial('ide: pronto', 30)
        match = re.findall(r'criada por \d+: "IDE - sem nome" (\d+)x(\d+) em \((\d+),(\d+)\)', m.serial())[-1]
        x, y = int(match[2]), int(match[3])
        # Conteúdo da janela começa depois da borda e da barra de título.
        m.clique(x + 2 + 290, y + 24 + 52)
        m.esperar_serial('Go no SaguiOS!', 60)
        m.esperar_serial('programa da aba ide-5-0 terminou (codigo 0)', 60)
        verificar('Compilado. Abrindo no Terminal...' in m.serial(), 'Go compilado e executado')
        m.clique(x + int(match[0]) + 4 - 2 - 20 + 8, y + 12)
        m.esperar_serial('ide: fechado', 20)
        m.esperar_serial('sagui:/$', 15)
        time.sleep(1)
        # A notificação do fim do processo da IDE às vezes sai depois do prompt,
        # engolindo a primeira letra do comando: tenta de novo se não abrir.
        aberto = False
        for _ in range(3):
            m.digitar('ide /exemplos/lua/ola.lua\n', 0.03)
            try:
                m.esperar_serial('ide: aberto /exemplos/lua/ola.lua', 15)
                aberto = True
                break
            except FalhaTeste:
                m.esperar_serial('sagui:/$', 10)
        verificar(aberto, 'a IDE abriu o arquivo Lua')
        match = re.findall(r'criada por \d+: "IDE - sem nome" (\d+)x(\d+) em \((\d+),(\d+)\)', m.serial())[-1]
        x, y = int(match[2]), int(match[3])
        m.clique(x + 2 + 290, y + 24 + 52)
        m.esperar_serial('soma', 60)
        verificar('[GUI] janela' in m.serial() and '"Terminal"' in m.serial(), 'Lua interpretado no Terminal')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
