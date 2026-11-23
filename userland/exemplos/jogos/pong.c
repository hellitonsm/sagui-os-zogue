/* pong.c - Pong contra o CPU no terminal do SaguiOS.
 *
 *   cc /exemplos/jogos/pong.c -o /tmp/pong
 *   /tmp/pong
 *
 * W/S movem a raquete da esquerda; Q sai. Primeiro a 5 pontos vence. */
#include <sagui.h>

static int py_jog, py_cpu, bx, by, bvx, bvy, pontos_jog, pontos_cpu, tick, cpucont;

static int aleatorio(int n)
{
    return n > 0 ? (int)(tempo_ms() % (unsigned)n) : 0;
}

static void reiniciar_bola(void)
{
    bx = 20;
    by = 3 + aleatorio(8);
    bvx = (aleatorio(2) == 0) ? -1 : 1;
    bvy = (aleatorio(2) == 0) ? -1 : 1;
}

static void desenhar(void)
{
    int row, col;
    limpar_tela();
    imprimir("  PONG   jogador %d x %d cpu\n", pontos_jog, pontos_cpu);
    for (row = 0; row < 14; row++) {
        for (col = 0; col < 40; col++) {
            if (row == 0 || row == 13) { imprimir("#"); continue; }
            if (col == 1 && row >= py_jog && row <= py_jog + 2) { imprimir("|"); continue; }
            if (col == 38 && row >= py_cpu && row <= py_cpu + 2) { imprimir("|"); continue; }
            if (col == bx && row == by) { imprimir("o"); continue; }
            imprimir(" ");
        }
        imprimir("\n");
    }
    imprimir("W/S movem a raquete, Q sai\n");
}

int principal(int argc, char **argv)
{
    int c;
    (void)argc;
    (void)argv;
    pontos_jog = 0;
    pontos_cpu = 0;
    tick = 0;
    cpucont = 0;
    py_jog = 5;
    py_cpu = 5;
    reiniciar_bola();
    modo_terminal(TERM_BRUTO);
    for (;;) {
        dormir(60);
        c = tecla_tentada();
        while (c >= 0) {
            if (c == 'q' || c == 'Q') {
                modo_terminal(TERM_LINHA);
                imprimir("Ate mais!\n");
                return 0;
            }
            if (c == 'w' || c == 'W') py_jog--;
            if (c == 's' || c == 'S') py_jog++;
            c = tecla_tentada();
        }
        if (py_jog < 1) py_jog = 1;
        if (py_jog > 10) py_jog = 10;
        cpucont++;
        if (cpucont >= 3) {
            cpucont = 0;
            if (by < py_cpu) py_cpu--;
            if (by > py_cpu + 2) py_cpu++;
        }
        if (py_cpu < 1) py_cpu = 1;
        if (py_cpu > 10) py_cpu = 10;
        tick++;
        if (tick >= 2) {
            tick = 0;
            bx += bvx;
            by += bvy;
            if (by <= 1) { by = 1; bvy = -bvy; }
            if (by >= 12) { by = 12; bvy = -bvy; }
            if (bx == 2 && bvx < 0 && by >= py_jog && by <= py_jog + 2) { bvx = -bvx; bx = 3; }
            if (bx == 37 && bvx > 0 && by >= py_cpu && by <= py_cpu + 2) { bvx = -bvx; bx = 36; }
            if (bx <= 0) { pontos_cpu++; reiniciar_bola(); }
            if (bx >= 39) { pontos_jog++; reiniciar_bola(); }
        }
        desenhar();
        if (pontos_jog >= 5 || pontos_cpu >= 5) {
            modo_terminal(TERM_LINHA);
            limpar_tela();
            if (pontos_jog >= 5) imprimir("Voce venceu!\n");
            else imprimir("O CPU venceu!\n");
            return 0;
        }
    }
}
