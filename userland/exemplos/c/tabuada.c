/* Exemplo de C no SaguiOS 3.0: soma 1..n com laço.
 * Compile e rode dentro do SaguiOS:
 *
 *   cc /exemplos/c/tabuada.c -o /tmp/tabuada
 *   /tmp/tabuada
 */
#include <sagui.h>

static int soma(int n)
{
    int i = 1;
    int total = 0;

    while (i <= n) {
        total = total + i;
        i = i + 1;
    }
    return total;
}

int principal(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    if (soma(10) == 55) {
        imprimir("[C] soma 1..10 = 55, compilado dentro do SaguiOS\n");
        return 0;
    }
    imprimir("[C] falha no exemplo\n");
    return 1;
}
