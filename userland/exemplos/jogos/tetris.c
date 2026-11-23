/* tetris.c - Tetris no terminal do SaguiOS.
 *
 *   cc /exemplos/jogos/tetris.c -o /tmp/tetris
 *   /tmp/tetris
 *
 * A/D movem, W gira, S desce rapido, Q sai. */
#include <sagui.h>

static int pozo[180];
static int base[28] = { 4,5,6,7,  1,2,5,6,  1,4,5,6,  1,2,4,5,  0,1,5,6,  0,4,5,6,  2,4,5,6 };
static int cel[4];
static int peca, rot, px, py, pontos, linhas, gravidade, proxima, perdeu;

static int aleatorio(int n) { return n > 0 ? (int)(tempo_ms() % (unsigned)n) : 0; }

static void recalcular(void)
{
    int k, ddy, ddx, r, t;
    for (k = 0; k < 4; k++) {
        ddy = base[peca * 4 + k] / 4;
        ddx = base[peca * 4 + k] % 4;
        r = rot;
        while (r > 0) { t = ddy; ddy = ddx; ddx = 3 - t; r--; }
        cel[k] = ddy * 4 + ddx;
    }
}

static int cabe(void)
{
    int k, ax, ay;
    for (k = 0; k < 4; k++) {
        ax = px + cel[k] % 4;
        ay = py + cel[k] / 4;
        if (ax < 0 || ax >= 10) return 0;
        if (ay >= 18) return 0;
        if (ay >= 0 && pozo[ay * 10 + ax] != 0) return 0;
    }
    return 1;
}

static void nova_peca(void)
{
    peca = proxima;
    rot = 0;
    px = 3;
    py = 0;
    proxima = aleatorio(7);
    recalcular();
    if (!cabe()) perdeu = 1;
}

static void travar(void)
{
    int k, ax, ay;
    for (k = 0; k < 4; k++) {
        ax = px + cel[k] % 4;
        ay = py + cel[k] / 4;
        if (ay >= 0 && ay < 18 && ax >= 0 && ax < 10)
            pozo[ay * 10 + ax] = 1;
    }
}

static void limpar_linhas_cheias(void)
{
    int y, x, yy, xx, cheia;
    for (y = 17; y >= 0; y--) {
        cheia = 1;
        for (x = 0; x < 10; x++)
            if (pozo[y * 10 + x] == 0) cheia = 0;
        if (cheia) {
            for (yy = y; yy > 0; yy--)
                for (xx = 0; xx < 10; xx++)
                    pozo[yy * 10 + xx] = pozo[(yy - 1) * 10 + xx];
            for (xx = 0; xx < 10; xx++) pozo[xx] = 0;
            linhas++;
            pontos += 250;
            y++;
        }
    }
}

static void gerar_peca_inicial(void)
{
    int i;
    for (i = 0; i < 180; i++) pozo[i] = 0;
    pontos = 0; linhas = 0; gravidade = 0; perdeu = 0;
    proxima = aleatorio(7);
    nova_peca();
}

static void desenhar(void)
{
    int row, col, k, marcado, eh_peca, ax, ay;
    limpar_tela();
    imprimir("  TETRIS   pontos %d   linhas %d\n", pontos, linhas);
    for (col = 0; col < 12; col++) imprimir("-");
    imprimir("\n");
    for (row = 0; row < 18; row++) {
        imprimir("|");
        for (col = 0; col < 10; col++) {
            marcado = pozo[row * 10 + col];
            eh_peca = 0;
            for (k = 0; k < 4; k++) {
                ax = px + cel[k] % 4;
                ay = py + cel[k] / 4;
                if (col == ax && row == ay) eh_peca = 1;
            }
            if (eh_peca) imprimir("O");
            else if (marcado) imprimir("#");
            else imprimir(" ");
        }
        imprimir("|\n");
    }
    for (col = 0; col < 12; col++) imprimir("-");
    imprimir("\nA/D movem, W gira, S desce, Q sai\n");
}

int principal(int argc, char **argv)
{
    int c;
    (void)argc; (void)argv;
    gerar_peca_inicial();
    modo_terminal(TERM_BRUTO);
    for (;;) {
        dormir(50);
        c = tecla_tentada();
        while (c >= 0) {
            if (c == 'q' || c == 'Q') { modo_terminal(TERM_LINHA); imprimir("Ate mais!\n"); return 0; }
            if (c == 'a' || c == 'A') { px--; if (!cabe()) px++; }
            if (c == 'd' || c == 'D') { px++; if (!cabe()) px--; }
            if (c == 's' || c == 'S') { py++; if (!cabe()) py--; }
            if (c == 'w' || c == 'W') {
                rot = (rot + 1) % 4; recalcular();
                if (!cabe()) { rot = (rot + 3) % 4; recalcular(); }
            }
            c = tecla_tentada();
        }
        gravidade++;
        if (gravidade >= 3) {
            gravidade = 0;
            py++;
            if (!cabe()) {
                py--;
                travar();
                pontos += 10;
                limpar_linhas_cheias();
                nova_peca();
                if (perdeu) {
                    modo_terminal(TERM_LINHA);
                    desenhar();
                    imprimir("Fim de jogo! Pontos: %d\n", pontos);
                    return 0;
                }
            }
        }
        desenhar();
    }
}
