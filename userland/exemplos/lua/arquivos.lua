-- Leitura e escrita de arquivos, e dofile.

local f = assert(io.open("/exemplos/lua/saida.txt", "w"))
f:write("linha 1\n", "linha 2\n")
f:close()

local g = assert(io.open("/exemplos/lua/saida.txt", "r"))
local a = g:read("l")
local b = g:read("l")
g:close()
print("arquivo:", a, b)

for l in io.lines("/exemplos/lua/saida.txt") do
    print("linha:", l)
end

dofile("/exemplos/lua/dofile.lua")
