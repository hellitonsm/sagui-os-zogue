/* sudoku.c - Sudoku 9x9 no terminal do SaguiOS.
 *
 *   cc /exemplos/jogos/sudoku.c -o /tmp/sudoku
 *   /tmp/sudoku
 *
 * Comando: "linha coluna valor" (ex.: "3 5 7"); valor 0 apaga uma casa;
 * "q" sai. Linha e coluna de 1 a 9. */
#include <sagui.h>

static int tab[81] = {
    5,3,0,0,7,0,0,0,0,
    6,0,0,1,9,5,0,0,0,
    0,9,8,0,0,0,0,6,0,
    8,0,0,0,6,0,0,0,3,
    4,0,0,8,0,3,0,0,1,
    7,0,0,0,2,0,0,0,6,
    0,6,0,0,0,0,2,8,0,
    0,0,0,4,1,9,0,0,5,
    0,0,0,0,8,0,0,7,9
};
static int fixo[81];
static char linha[16];

static void preparar_fixos(void)
{
    int i;
    for (i = 0; i < 81; i++)
        fixo[i] = tab[i] != 0;
}

static int pode_por(int pos, int v)
{
    int i, j, l, c, bl, bc;
    l = pos / 9;
    c = pos % 9;
    for (i = 0; i < 9; i++) {
        if (tab[l * 9 + i] == v) return 0;
        if (tab[i * 9 + c] == v) return 0;
    }
    bl = (l / 3) * 3;
    bc = (c / 3) * 3;
    for (i = 0; i < 3; i++)
        for (j = 0; j < 3; j++)
            if (tab[(bl + i) * 9 + bc + j] == v) return 0;
    return 1;
}

static int completo(void)
{
    int i;
    for (i = 0; i < 81; i++)
        if (tab[i] == 0) return 0;
    return 1;
}

static void mostrar_tabuleiro(void)
{
    int i, j, v;
    limpar_tela();
    imprimir("    1 2 3   4 5 6   7 8 9\n");
    imprimir("  -----------------------\n");
    for (i = 0; i < 9; i++) {
        imprimir("%d | ", i + 1);
        for (j = 0; j < 9; j++) {
            v = tab[i * 9 + j];
            if (v == 0) imprimir(". ");
            else imprimir("%d ", v);
            if (j == 2 || j == 5) imprimir("| ");
        }
        imprimir("|\n");
        if (i == 2 || i == 5) imprimir("  -----------------------\n");
    }
}

static int ler_linha_cmd(void)
{
    int i, n;
    char c;
    i = 0;
    for (;;) {
        n = ler(ENTRADA, &c, 1);
        if (n <= 0) return -1;
        if (c == '\n' || c == '\r') break;
        if (i < 14) { linha[i] = c; i++; }
    }
    linha[i] = 0;
    return i;
}

/* Devolve o proximo numero da linha, -1 se acabou ou -2 se pediu para sair. */
static int proximo_int(int *pos)
{
    int n = -1;
    while (linha[*pos] != 0 && (linha[*pos] < '0' || linha[*pos] > '9')) {
        if (linha[*pos] == 'q' || linha[*pos] == 'Q') return -2;
        (*pos)++;
    }
    if (linha[*pos] == 0) return -1;
    while (linha[*pos] >= '0' && linha[*pos] <= '9') {
        if (n < 0) n = 0;
        n = n * 10 + (linha[*pos] - '0');
        (*pos)++;
    }
    return n;
}

int principal(int argc, char **argv)
{
    int l, c, v, cmd, pos, idx;
    (void)argc;
    (void)argv;
    preparar_fixos();
    for (;;) {
        mostrar_tabuleiro();
        if (completo()) {
            imprimir("Parabens, voce completou o sudoku!\n");
            return 0;
        }
        imprimir("linha coluna valor (ex.: 3 5 7), 0 apaga, q sai\n");
        if (ler_linha_cmd() < 0) { imprimir("Fim da entrada.\n"); return 0; }
        idx = 0;
        cmd = proximo_int(&idx);
        if (cmd == -2) { imprimir("Ate mais!\n"); return 0; }
        l = cmd;
        c = proximo_int(&idx);
        v = proximo_int(&idx);
        if (l < 1 || l > 9 || c < 1 || c > 9 || v < 0 || v > 9) {
            imprimir("Formato: linha coluna valor (ex.: 3 5 7)\n");
            continue;
        }
        pos = (l - 1) * 9 + (c - 1);
        if (fixo[pos]) { imprimir("Esse numero faz parte do puzzle.\n"); continue; }
        if (v != 0 && !pode_por(pos, v)) {
            imprimir("Jogada invalida: ja existe na linha, coluna ou bloco.\n");
            continue;
        }
        tab[pos] = v;
        if (v == 0) imprimir("Casa apagada.\n");
        else imprimir("Jogada aceita.\n");
    }
}
