#!/usr/bin/env python3
"""
mkzogue.py - desenha o papel de parede "Zogue" (1024x768) e o converte
para o formato .sgi do SaguiOS com o tools/mkfundo.py.

A cena imita o clima da Mata Atlântica (a do mata-atlantica.sgi): luz
quente de sol passando pela copa, verdes profundos e névoa. Na frente, um
galho com o Zogue, a subespécie de sagui que batiza o sistema: corpo
cinza-rosado, dorso avermelhado, rosto claro com tufos brancos e a cauda
longa toda preta.

Uso: python3 tools/mkzogue.py [saida.sgi]   (padrão: rootfs/arte/zogue.sgi)
Precisa do Pillow (ferramenta de build, não roda no sistema).
"""
import math
import os
import struct
import sys

from PIL import Image, ImageDraw

W, H = 1024, 768
SS = 2                      # supersampling: desenha em 2x e reduz (anti-serrilhado)

# ---------------------------------------------------------------- cores

CORU = (252, 238, 200)       # céu no alto, quente
CORH = (214, 226, 198)       # céu junto ao horizonte
COR_SOL = (255, 240, 190)
VERDE_LONGE = (89, 107, 66)
VERDE_MEIO = (59, 88, 73)
VERDE_PERTO = (35, 42, 25)
VERDE_TOPO = (111, 144, 119)
NÉVOA = (232, 216, 170)
GALHO = (74, 52, 36)
GALHO_CLARO = (110, 78, 52)
CORPO = (201, 160, 139)      # cinza-rosado do Zogue
DORSO = (158, 68, 38)        # avermelhado
CABECA = (60, 45, 35)
ROSTO = (235, 222, 205)
BOCA = (150, 96, 80)
TUFOS = (245, 245, 240)
CAUDA = (20, 18, 16)
OLHO = (20, 18, 16)

# ---------------------------------------------------------------- utilitários

def mistura(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def parallax_camadas(w2, h2, escala=1.0):
    """Vetor de alturas de uma 'serra' de mata, com o mesmo sabor das ondas
    do kernel (senoides somadas), para o desenho da copa."""
    base = h2 * (0.42 + 0.10 * escala)
    amp = h2 * (0.05 + 0.04 * escala)
    n = 140
    xs = [int(i * w2 / (n - 1)) for i in range(n)]
    ys = []
    for i, x in enumerate(xs):
        y = base + amp * (0.6 * math.sin(x / 190.0 + escala * 4.2)
                          + 0.4 * math.sin(x / 97.0 + escala * 9.1))
        ys.append(int(y))
    return xs, ys

def serra(draw, cor, cor_topo, w2, h2, escala=1.0, limite=0.0):
    xs, ys = parallax_camadas(w2, h2, escala)
    pts = list(zip(xs, ys)) + [(w2, h2), (0, h2)]
    draw.polygon(pts, fill=cor)
    # brilho no topo da copa (a luz batendo nas folhas)
    for i in range(len(xs) - 1):
        draw.line([(xs[i], ys[i]), (xs[i + 1], ys[i + 1])],
                  fill=cor_topo, width=3)

def raios_de_sol(base, cx, cy, w2, h2):
    """Raios translúcidos saindo do sol. Devolve uma camada RGBA."""
    tam = (w2, h2)
    camada = Image.new("RGBA", tam, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    n = 9
    for i in range(n):
        ang = math.radians(-46 + i * 12.5)
        # cateto do raio: 1.6x a diagonal (sai da tela)
        comp = int(math.hypot(w2, h2) * 1.6)
        dx, dy = math.cos(ang), math.sin(ang)
        esq = (cx + dx * comp * 0.45, cy + dy * comp * 0.45)
        lar = 26 + (i % 3) * 14
        d.polygon([(cx, cy),
                   (esq[0] - dy * lar, esq[1] + dx * lar),
                   (esq[0] + dy * lar, esq[1] - dx * lar)],
                  fill=(255, 244, 200, 46))
    return camada

def zogue(draw, x, y, esc):
    """O Zogue sentado num galho, olhando para a esquerda. (x, y) é o ponto
    de apoio (o traseiro); esc escala o bicho. A cauda cai e volta para
    cima, com a curva clássica do sagui."""
    def elipse(cx, cy, rx, ry, cor):
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=cor)

    # --- cauda (desenhada primeiro, atrás do corpo) ---
    cx, cy = x + 58 * esc, y - 8 * esc
    n = 60
    for i in range(n):
        t = i / (n - 1)
        # caminho: cai, vira para a esquerda embaixo e sobe de novo
        px = cx + math.sin(t * math.pi * 1.9) * 105 * esc * (0.35 + 0.65 * t)
        py = cy + t * 150 * esc + math.sin(t * math.pi) * 26 * esc
        raio = (9 - 5.5 * t) * esc
        elipse(px, py, raio, raio, CAUDA)

    # --- corpo: dorso avermelhado por cima, cinza-rosado por baixo ---
    elipse(x, y - 26 * esc, 30 * esc, 34 * esc, DORSO)
    elipse(x + 6 * esc, y - 14 * esc, 24 * esc, 26 * esc, CORPO)

    # --- cabeça ---
    elipse(x - 26 * esc, y - 62 * esc, 17 * esc, 17 * esc, CABECA)
    elipse(x - 30 * esc, y - 58 * esc, 8 * esc, 8 * esc, TUFOS)   # orelha
    elipse(x - 18 * esc, y - 72 * esc, 7 * esc, 7 * esc, TUFOS)   # tufo
    elipse(x - 8 * esc, y - 74 * esc, 5 * esc, 5 * esc, TUFOS)
    elipse(x - 33 * esc, y - 62 * esc, 6 * esc, 6 * esc, ROSTO)   # rosto
    elipse(x - 27 * esc, y - 64 * esc, 3.4 * esc, 3.4 * esc, BOCA)
    elipse(x - 39 * esc, y - 67 * esc, 1.6 * esc, 1.6 * esc, OLHO)

    # --- braço e pernas apoiando no galho ---
    elipse(x - 6 * esc, y - 6 * esc, 4 * esc, 6 * esc, CORPO)     # mão
    elipse(x + 24 * esc, y - 2 * esc, 5 * esc, 4 * esc, CABECA)   # pé
    elipse(x + 44 * esc, y - 6 * esc, 5 * esc, 4 * esc, CABECA)

    # --- luz na cabeça (contra o sol) ---
    elipse(x - 31 * esc, y - 66 * esc, 11 * esc, 10 * esc, (130, 96, 72))

def galho(draw, w2, h2):
    """Um galho entrando pela direita, com musgo e folhas."""
    camada = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    # corpo do galho: uma curva grossa
    pts = []
    for i in range(60):
        t = i / 59.0
        x = w2 * (0.30 + 0.72 * t)
        y = h2 * (0.56 + 0.115 * t + 0.05 * math.sin(t * 4.6))
        pts.append((x, y))
    d.line(pts, fill=GALHO, width=int(26 * SS))
    # face de cima iluminada
    d.line([(p[0], p[1] - 6 * SS) for p in pts[2:]], fill=GALHO_CLARO,
           width=5 * SS)
    # musgo e folhas
    for i in range(0, len(pts), 7):
        x, y = pts[i]
        d.ellipse([x - 10 * SS, y - 16 * SS, x + 10 * SS, y + 2 * SS],
                  fill=(62, 92, 66))
    return camada

def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else "rootfs/arte/zogue.sgi"
    w2, h2 = W * SS, H * SS

    # céu: degradê vertical
    base = Image.new("RGB", (w2, h2))
    d = ImageDraw.Draw(base)
    for y in range(h2):
        t = y / h2
        d.line([(0, y), (w2, y)], fill=mistura(CORU, CORH, t))

    # brilho do sol (círculos concêntricos, quase invisíveis)
    brilho = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    db = ImageDraw.Draw(brilho)
    solx, soly = int(w2 * 0.42), int(h2 * 0.22)
    for r in range(560, 0, -14):
        alfa = max(0, 26 - r // 24)
        db.ellipse([solx - r, soly - r, solx + r, soly + r],
                   fill=(255, 244, 200, alfa))
    base = Image.alpha_composite(base.convert("RGBA"), brilho).convert("RGB")

    # camadas de mata, de trás para a frente
    d = ImageDraw.Draw(base)
    serra(d, mistura(VERDE_LONGE, NÉVOA, 0.55), mistura(VERDE_TOPO, NÉVOA, 0.5),
          w2, h2, escala=1.0)
    serra(d, mistura(VERDE_MEIO, NÉVOA, 0.30), mistura(VERDE_TOPO, NÉVOA, 0.25),
          w2, h2, escala=1.6)
    serra(d, VERDE_PERTO, mistura(VERDE_TOPO, VERDE_PERTO, 0.5),
          w2, h2, escala=2.2)

    # névoa baixa
    nevoeiro = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nevoeiro)
    for i in range(9):
        cx = (i * 137) % w2
        cy = int(h2 * (0.58 + 0.05 * ((i % 3) - 1)))
        dn.ellipse([cx - 320 * SS, cy - 30 * SS, cx + 320 * SS, cy + 30 * SS],
                   fill=NÉVOA + (60,))
    base = Image.alpha_composite(base.convert("RGBA"), nevoeiro).convert("RGB")

    # raios de sol
    raios = raios_de_sol(base, solx, soly, w2, h2)
    base = Image.alpha_composite(base.convert("RGBA"), raios).convert("RGB")

    # galho da frente
    base = Image.alpha_composite(base.convert("RGBA"), galho(d, w2, h2)).convert("RGB")

    # o Zogue
    dz = ImageDraw.Draw(base)
    zogue(dz, int(w2 * 0.36), int(h2 * 0.60), esc=4.6 * SS)

    # vinheta suave (escurece os cantos)
    vinheta = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    dv = ImageDraw.Draw(vinheta)
    dv.ellipse([-w2 * 0.25, -h2 * 0.25, w2 * 1.25, h2 * 1.25],
                fill=(0, 0, 0, 0))
    # grade radial simples: escurece as bordas aos poucos
    for r in range(int(min(w2, h2) * 0.95), int(min(w2, h2) * 0.55), -18):
        dv.ellipse([w2 // 2 - r, h2 // 2 - r, w2 // 2 + r, h2 // 2 + r],
                   outline=(0, 0, 0, 20), width=18)
    base = Image.alpha_composite(base.convert("RGBA"), vinheta).convert("RGB")

    # reduz para o tamanho final e converte para .sgi
    final = base.resize((W, H), Image.LANCZOS)
    png = "/tmp/opencode/zogue-wall.png"
    final.save(png)

    # reusa a conversão do mkfundo: paleta de 256 cores + RLE
    from mkfundo import rle
    q = final.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = (q.getpalette() + [0] * 768)[:768]
    dados = rle(q.tobytes())
    with open(saida, "wb") as f:
        f.write(b"SGI1" + struct.pack("<HH", *q.size) + bytes(pal) + dados)
    print(f"mkzogue: {saida} {q.size[0]}x{q.size[1]}, {776 + len(dados)} bytes")


if __name__ == "__main__":
    main()
