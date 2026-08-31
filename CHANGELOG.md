# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.2.1] - 2026-08-31
### Adicionado
- `__all__` explícito em `quantilica.catalog.dims` (re-exports), configuração `[tool.ruff]` padrão do ecossistema e workflows de CI (test + publish GitHub Releases/índice).
### Corrigido
- Quitação de dívida de lint (E501, I001); `UP042` suprimido em `enums.py` com nota (migrar para `StrEnum` muda `str()` dos membros — fica para um major deliberado).

## [0.1.0] - 2026-06-04

Primeira entrada em formato Keep a Changelog; documenta o estado do pacote nesta
versão.

### Adicionado

- Catálogo de dados unificado e modelo canônico de observação para o ecossistema
  Quantilica.
