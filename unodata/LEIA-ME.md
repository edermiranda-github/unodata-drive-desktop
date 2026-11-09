# UNODATA Nuvem (app de sincronização para Windows)

App de desktop da Nextcloud com a marca da UNODATA, para os clientes da nuvem operada pela UNODATA.
Código oficial em https://github.com/nextcloud/desktop (GPL-2.0), versão de base indicada no commit.
Mudanças: só marca (nome, ícones, cores, identificadores próprios no Windows), sem mudança de comportamento.

- `unodata/aplicar-marca.py`: aplica a marca sobre uma tag do código oficial (idempotente).
- `.github/workflows/unodata-windows.yml`: compila e gera o instalador (artefato do run).

Versão nova da Nextcloud: checkout da tag nova, rodar `aplicar-marca.py`, conferir o diff, commit, rodar o workflow.
