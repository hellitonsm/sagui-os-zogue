/* Testa a loja de apps no proprio SaguiOS. Uma feature por caso. */
#include "sagui.h"

static int rodar(char *const args[], char *buf, unsigned cap)
{
    /* A saída do filho vai para um arquivo (não para um pipe): o filho
     * termina e o conteúdo é lido depois, sem a interação pipe+espera. */
    int codigo = -1;
    int fd = abrir("/tmp/loja-saida.txt", ABRIR_ESCREVER | ABRIR_CRIAR | ABRIR_TRUNCAR);
    if (fd < 0) return -1;
    int a = duplicar(SAIDA, 14), b = duplicar(ERROS, 15);
    if (a < 0 || b < 0) {
        if (a >= 0) fechar(a);
        if (b >= 0) fechar(b);
        fechar(fd); return -1;
    }
    duplicar(fd, SAIDA); duplicar(fd, ERROS); fechar(fd);
    int pid = executar(args[0], args);
    duplicar(a, SAIDA); duplicar(b, ERROS); fechar(a); fechar(b);
    if (pid < 0) return -1;
    if (esperar(pid, &codigo) < 0) return -1;
    fd = abrir("/tmp/loja-saida.txt", ABRIR_LER);
    if (fd < 0) return -1;
    int n = ler(fd, buf, cap - 1); fechar(fd);
    apagar("/tmp/loja-saida.txt");
    if (n < 0) return -1;
    buf[n] = 0;
    return codigo;
}

int principal(int argc, char **argv)
{
    (void)argc; (void)argv;
    char b[4096];
    /* 1. listar fonte local */
    char *listar[] = {"/bin/loja", "listar", NULL};
    if (rodar(listar, b, sizeof b) != 0) return 1;
    if (!acha_char(b, 'o') || !acha_char(b, 'a')) return 2;
    /* 2. instalar app Go local (/exemplos/go/ola.go -> /store/ola.loj compilado+empacotado) */
    char *inst_go[] = {"/bin/loja", "instalar", "ola", NULL};
    if (rodar(inst_go, b, sizeof b) != 0) return 3;
    if (!acha_char(b, 'i')) return 4;
    /* 3. informar o pacote .loj */
    char *info[] = {"/bin/loja", "informar", "/store/ola.loj", NULL};
    if (rodar(info, b, sizeof b) != 0) return 11;
    if (!acha_char(b, 'S') || !acha_char(b, 'o')) return 12;
    /* 3b. executar o .loj (extrai o ELF e roda) */
    char *exec[] = {"/bin/loja", "executar", "ola", NULL};
    if (rodar(exec, b, sizeof b) != 0) return 13;
    if (!acha_char(b, 'G') || !acha_char(b, 'S')) return 14;
    /* 4. configurar link da loja e reler */
    char *conf[] = {"/bin/loja", "configurar", "http://loja.exemplo/", NULL};
    if (rodar(conf, b, sizeof b) != 0) return 6;
    char *link[] = {"/bin/loja", "link", NULL};
    if (rodar(link, b, sizeof b) != 0) return 7;
    if (compara_texto(b, "loja: http://loja.exemplo/\n")) return 8;
    /* 5. instalar app Lua local (/exemplos/lua/recursos.lua -> /store/recursos.lua) */
    char *inst_lua[] = {"/bin/loja", "instalar", "recursos", NULL};
    if (rodar(inst_lua, b, sizeof b) != 0) return 9;
    {
        info_arquivo_t inf;
        if (info_arquivo("/store/recursos.lua", &inf) < 0) return 10;
        apagar("/store/recursos.lua");
    }
    registrar("[LOJA] fonte local, instalacao Go e link validados\n");
    return 0;
}
