/* Exemplo de C no SaguiOS 3.0, compilado pelo cc oficial. */
#include <sagui.h>

static int soma(int esquerda, int direita)
{
    return esquerda + direita;
}

int principal(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    int i = 0;
    int total = 0;

    while (i < 4) {
        total = total + i;
        i = i + 1;
    }

    if (soma(total, 1) == 7) {
        imprimir("[C] compilado dentro do SaguiOS\n");
        return 0;
    }
    imprimir("[C] falha no exemplo\n");
    return 1;
}
