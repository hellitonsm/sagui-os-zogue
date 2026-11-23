/* wget.c - cliente HTTP de texto, suporte inicial a http:// sem TLS (H49). */
#include "sagui.h"
#include "http.h"

typedef struct {
    int fd;          /* -1: mostra na saída; senão, grava no arquivo */
    bool gravar;
    bool ocupado;     /* ERRO_OCUPADO: a rede está com o servidor de arquivos */
} destino_t;

static int receber(void *ctx, const char *dados, unsigned n)
{
    destino_t *d = ctx;
    if (d->gravar)
        return escrever(d->fd, dados, n) == (int)n ? 0 : -1;
    return escrever_tudo(SAIDA, dados, n) >= 0 ? 0 : -1;
}

int principal(int argc, char **argv)
{
    if (argc < 2) { imprimir("Uso: wget http://host/caminho [arquivo]\n"); return 2; }
    destino_t d = { -1, false, false };
    if (argc >= 3) {
        d.fd = abrir(argv[2], ABRIR_ESCREVER | ABRIR_CRIAR | ABRIR_TRUNCAR);
        if (d.fd < 0) { imprimir("wget: nao abriu %s (%d)\n", argv[2], d.fd); return 1; }
        d.gravar = true;
    }
    http_resposta_t r;
    int ok = http_obter(argv[1], receber, &d, &r);
    if (d.fd >= 0) fechar(d.fd);
    if (ok < 0) {
        if (ok == ERRO_OCUPADO)
            imprimir("wget: a rede esta com o servidor de arquivos (%d); saia dele ou pare com kill.\n", ok);
        else
            imprimir("wget: falha de rede/HTTP (%s). Veja a placa com \"rede\"; so HTTP.\n",
                     r.erro[0] ? r.erro : nome_erro(ok));
        return 1;
    }
    if (r.situacao != 200) {
        imprimir("wget: o servidor respondeu %d\n", r.situacao);
        return 1;
    }
    if (d.gravar)
        imprimir("Salvo %d bytes em %s\n", r.recebidos, argv[2]);
    return 0;
}
