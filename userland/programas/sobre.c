/* sobre - versão e créditos do SaguiOS. */
#include "sagui.h"

int principal(int argc, char **argv)
{
    (void)argc; (void)argv;
    static info_processo_t v[64];
    int procs = info_sistema(INFO_PROCESSOS, v, 64);
    info_memoria_t m;
    info_sistema(INFO_MEMORIA, &m, sizeof m);
    info_versao_t iv;
    if (info_sistema(INFO_VERSAO, &iv, sizeof iv) < 0) copia_texto(iv.versao, "?", sizeof iv.versao);
    imprimir("Zogue OS %s: sistema operacional baseado no SaguiOS.\n", iv.versao);
    imprimir("Baseado no SaguiOS, criado por Eli Rigobeli com Claude (Anthropic),\n");
    imprimir("sem código de outros sistemas no núcleo. Zogue OS é um projeto separado\n");
    imprimir("que mantém créditos completos ao SaguiOS e seus contribuidores.\n");
    imprimir("Agora: %d processos, %u MB livres de memória.\n", procs, m.livre_kb / 1024);
    imprimir("Leia /sobre.txt e /historia/saguios.txt. O mascote está em /arte/sagui.txt.\n");
    return 0;
}
