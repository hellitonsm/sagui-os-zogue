#!/usr/bin/env bash
# tinycc-sagui - TinyCC vendido e executado dentro do SaguiOS.
#
# O TinyCC (x86/i386) e compilado com o GCC do desenvolvimento (modo 32 bits)
# contra o libc nativo do SaguiOS e incluido na imagem em /bin/tinycc, com o
# sysroot (headers + libc.a + crt1.o) em /usr. Um programa em C pode ser
# compilado DENTRO do SaguiOS e executado ali mesmo:
#
#   tinycc -static -o /tmp/ola /tcc/hello.c
#   /tmp/ola
#
# Este script reimplementa o tools/tinycc-sagui/setup.ps1 em bash, para o
# build rodar no Linux (CI) sem a toolchain do Windows.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$AQUI/../.." && pwd)"

TINYCC_DIR="$REPO_ROOT/.local/tinycc"
TINYCC_COMMIT='70adbb129760b77e3bdfec447c1f986def763f2c'
TINYCC_URL='https://github.com/tinycc/tinycc.git'

if [ ! -f "$TINYCC_DIR/tcc.c" ]; then
    echo "== [setup] clonando tinycc em $TINYCC_DIR ..."
    rm -rf "$TINYCC_DIR"
    git clone "$TINYCC_URL" "$TINYCC_DIR"
    git -C "$TINYCC_DIR" checkout "$TINYCC_COMMIT"
else
    echo "== [setup] tinycc ja presente em $TINYCC_DIR"
fi

# O SaguiOS carrega programas em 0x40000000; o padrao do tinycc para Linux
# i386 e 0x08048000, que o carregador rejeita.
I386_LINK="$TINYCC_DIR/i386-link.c"
if ! grep -q '0x40000000' "$I386_LINK"; then
    sed -i 's/#define ELF_START_ADDR 0x08048000/#define ELF_START_ADDR 0x40000000/' "$I386_LINK"
    echo "== [setup] ELF_START_ADDR ajustado para 0x40000000"
fi

# Sem -o, o tinycc gravaria "a.out". No SaguiOS o executavel recebe o nome do
# fonte (sem extensao). O ajuste e feito no fonte vendorizado.
TCC_C="$TINYCC_DIR/tcc.c"
if ! grep -q 'SaguiOS: sem -o' "$TCC_C"; then
    python3 - "$TCC_C" <<'PY'
import sys
c = sys.argv[1]
t = open(c, encoding='utf-8', newline='').read()
antigo = (
    '    if ((s->just_deps || s->output_type == TCC_OUTPUT_OBJ) && !s->option_r && *ext)\n'
    '        strcpy(ext, ".o");\n'
    '    else\n'
    '        strcpy(buf, "a.out");\n'
)
novo = (
    '    if ((s->just_deps || s->output_type == TCC_OUTPUT_OBJ) && !s->option_r && *ext)\n'
    '        strcpy(ext, ".o");\n'
    '    else if (s->output_type == TCC_OUTPUT_EXE && first_file && strcmp(first_file, "-"))\n'
    '        *ext = 0;   /* SaguiOS: sem -o, o executavel tem o nome do fonte */\n'
    '    else\n'
    '        strcpy(buf, "a.out");\n'
)
if antigo in t:
    open(c, 'w', encoding='utf-8', newline='').write(t.replace(antigo, novo))
else:
    sys.exit("setup: tcc.c nao tem o trecho esperado para ajustar a saida")
PY
    echo "== [setup] saida padrao do tinycc ajustada (nome do fonte)"
fi

# config.h para o alvo Linux i386 (in-process; sem dlopen, sem backtrace).
cat > "$TINYCC_DIR/config.h" <<'EOF'
#define TARGETOS_Linux 1
#define CONFIG_TCCDIR "/usr/lib/tcc"
#define CONFIG_TCC_STATIC 1
#define CONFIG_TCC_BACKTRACE 0
#define CONFIG_TCC_PREDEFS 0
#define CONFIG_TCC_SEMLOCK 0
#define TCC_VERSION "0.9.28rc"
EOF
echo "== [setup] config.h pronto"
