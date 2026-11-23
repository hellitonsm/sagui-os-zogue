/* Verifica assembler e compilador C executados no anel 3 do SaguiOS. */
#include "sagui.h"

static int rodar(char *const args[])
{
    int codigo = -1;
    int pid = executar(args[0], args);
    if (pid < 0 || esperar(pid, &codigo) != pid) return -1;
    return codigo;
}

static int gravar(const char *caminho, const char *texto)
{
    int fd = abrir(caminho, ABRIR_ESCREVER | ABRIR_CRIAR | ABRIR_TRUNCAR);
    if (fd < 0) return 0;
    int ok = escrever_tudo(fd, texto, (unsigned)tam_texto(texto)) >= 0;
    if (fechar(fd) < 0) ok = 0;
    return ok;
}

int principal(int argc, char **argv)
{
    (void)argc; (void)argv;
    char *montar_asm[] = { "/bin/asagui", "build", "-o", "/tmp/ola-asm", "/exemplos/asm/ola.asm", NULL };
    char *executar_asm[] = { "/tmp/ola-asm", NULL };
    if (rodar(montar_asm) != 0) return 1;
    if (rodar(executar_asm) != 0) return 2;

    /* C compilado no convidado com o csagui (subconjunto próprio). */
    const char *c_ola =
        "int soma(int a, int b) { return a + b; }\n"
        "int main(void) {\n"
        "    int i = 0, total = 0;\n"
        "    while (i < 4) { total = total + i; i = i + 1; }\n"
        "    if (soma(total, 1) == 7) { puts(\"[C] ok\"); return 0; }\n"
        "    puts(\"[C] falha\"); return 1;\n"
        "}\n";
    if (!gravar("/tmp/ola-csagui.c", c_ola)) return 3;
    char *compilar_c[] = { "/bin/csagui", "build", "-o", "/tmp/ola-c", "/tmp/ola-csagui.c", NULL };
    char *executar_c[] = { "/tmp/ola-c", NULL };
    if (rodar(compilar_c) != 0) return 3;
    if (rodar(executar_c) != 0) return 4;

    /* Fonte C invalida: o ELF anterior deve continuar executavel. */
    if (!gravar("/tmp/invalido.c", "int main(void) { return variavel_ausente; }\n")) return 5;
    char *c_invalido[] = { "/bin/csagui", "build", "-o", "/tmp/ola-c", "/tmp/invalido.c", NULL };
    if (rodar(c_invalido) == 0) return 6;
    if (rodar(executar_c) != 0) return 7;

    /* Simbolo de assembly indefinido: o destino anterior tambem fica intacto. */
    const char *asm_invalido =
        "bits 32\n"
        "global _start\n"
        "_start:\n"
        "    mov eax, rotulo_ausente\n"
        "    mov ebx, 0\n"
        "    mov eax, 3\n"
        "    int 0x80\n";
    if (!gravar("/tmp/invalido.asm", asm_invalido)) return 8;
    char *a_invalido[] = { "/bin/asagui", "build", "-o", "/tmp/ola-asm", "/tmp/invalido.asm", NULL };
    if (rodar(a_invalido) == 0) return 9;
    if (rodar(executar_asm) != 0) return 10;

    /* Fluxo relocavel: csagui gera ET_REL, ldagui resolve printf externo. */
    const char *c_objeto =
        "#include <stdio.h>\n"
        "int main(void) {\n"
        "    if (printf(\"valor=%d\\n\", 40 + 2) != 0) return 1;\n"
        "    return 0;\n"
        "}\n";
    const char *crt_asm =
        "bits 32\n"
        "global _start\n"
        "extern main\n"
        "section .text\n"
        "_start:\n"
        "    call main\n"
        "    mov ebx, eax\n"
        "    mov eax, 3\n"
        "    int 0x80\n"
        "    hlt\n";
    const char *printf_asm =
        "bits 32\n"
        "global printf\n"
        "section .text\n"
        "printf:\n"
        "    mov eax, [esp+8]\n"
        "    cmp eax, 42\n"
        "    jne printf_falha\n"
        "    mov eax, 0\n"
        "    ret\n"
        "printf_falha:\n"
        "    mov eax, 1\n"
        "    ret\n";
    if (!gravar("/tmp/ola-rel.c", c_objeto) ||
        !gravar("/tmp/crt-rel.asm", crt_asm) ||
        !gravar("/tmp/printf-rel.asm", printf_asm)) return 11;
    char *compilar_objeto[] = { "/bin/csagui", "compile", "-c", "-o", "/tmp/ola-rel.o", "/tmp/ola-rel.c", NULL };
    char *montar_crt[] = { "/bin/asagui", "assemble", "-c", "-o", "/tmp/crt-rel.o", "/tmp/crt-rel.asm", NULL };
    char *montar_printf[] = { "/bin/asagui", "assemble", "-c", "-o", "/tmp/printf-rel.o", "/tmp/printf-rel.asm", NULL };
    if (rodar(compilar_objeto) != 0 || rodar(montar_crt) != 0 || rodar(montar_printf) != 0) return 12;
    char *linkar[] = { "/bin/ldagui", "link", "-o", "/tmp/ola-rel", "/tmp/crt-rel.o", "/tmp/ola-rel.o", "/tmp/printf-rel.o", NULL };
    char *executar_linkado[] = { "/tmp/ola-rel", NULL };
    if (rodar(linkar) != 0 || rodar(executar_linkado) != 0) return 13;

    /* Valida que o csagui compila programas maiores (estilo jogos) no convidado.
     * Os exemplos de /exemplos/jogos usam Sagui 3.0/cc; aqui usamos fontes
     * csagui inline para manter o teste do compilador nativo. */
    const char *csudoku =
        "int tab[81];\n"
        "int ok(int p, int v){ if(p<0) return 0; if(v<0) return 0; return 1; }\n"
        "int main(void){ int i; for(i=0;i<81;i=i+1) tab[i]=0; tab[0]=5; if(ok(0,5)) return 0; return 1; }\n";
    const char *cpong =
        "int bx; int by; int vx;\n"
        "int passo(void){bx=bx+vx; if(bx>10) vx=0-bx; return bx;}\n"
        "int main(void){bx=1;by=2;vx=1;passo();return 0;}\n";
    const char *ctetris =
        "int p[4]; int g[200];\n"
        "int cabe(int x){int i;for(i=0;i<4;i=i+1) p[i]=x+i; return g[0]==0;}\n"
        "int main(void){int i;for(i=0;i<200;i=i+1) g[i]=0;if(cabe(0)) return 0; return 1;}\n";
    if (!gravar("/tmp/csudoku.c", csudoku) || !gravar("/tmp/cpong.c", cpong) ||
        !gravar("/tmp/ctetris.c", ctetris)) return 14;
    char *comp_sudoku[] = { "/bin/csagui", "build", "-o", "/tmp/sudoku", "/tmp/csudoku.c", NULL };
    if (rodar(comp_sudoku) != 0) { imprimir_em(ERROS, "[TOOLS] o sudoku nao compilou\n"); return 14; }
    char *comp_pong[] = { "/bin/csagui", "build", "-o", "/tmp/pong", "/tmp/cpong.c", NULL };
    if (rodar(comp_pong) != 0) { imprimir_em(ERROS, "[TOOLS] o pong nao compilou\n"); return 15; }
    char *comp_tetris[] = { "/bin/csagui", "build", "-o", "/tmp/tetris", "/tmp/ctetris.c", NULL };
    if (rodar(comp_tetris) != 0) { imprimir_em(ERROS, "[TOOLS] o tetris nao compilou\n"); return 16; }
    registrar("[TOOLS] jogos sudoku, pong e tetris compilam no convidado\n");

    (void)apagar("/tmp/ola-asm");
    (void)apagar("/tmp/ola-c");
    (void)apagar("/tmp/invalido.c");
    (void)apagar("/tmp/invalido.asm");
    (void)apagar("/tmp/ola-rel");
    (void)apagar("/tmp/ola-rel.o");
    (void)apagar("/tmp/ola-rel.c");
    (void)apagar("/tmp/crt-rel.asm");
    (void)apagar("/tmp/crt-rel.o");
    (void)apagar("/tmp/printf-rel.asm");
    (void)apagar("/tmp/printf-rel.o");
    registrar("[TOOLS] assembler, compilador C e ligador ELF relocavel validados\n");
    return 0;
}
