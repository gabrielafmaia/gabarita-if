# Limpeza segura do projeto

## Arquivos apagados

- `.ruff_cache/.gitignore`
- `.ruff_cache/0.14.5/11842326130491800655`
- `.ruff_cache/0.14.5/13939928730335262512`
- `.ruff_cache/0.14.5/4125318321376859654`
- `.ruff_cache/0.14.5/4637685775129727979`
- `.ruff_cache/0.14.5/775140176502232638`
- `.ruff_cache/0.14.5/804642550038377322`
- `.ruff_cache/CACHEDIR.TAG`
- `auditar_imagens_matematica.py`
- `auditar_recuperacao.py`
- `auditoria_contextos.txt`
- `auditoria_imagens_contextos.txt`
- `auditoria_imagens_matematica.json`
- `auditoria_recuperacao.json`
- `auditoria_visual_matematica/pagina_1.jpg`
- `auditoria_visual_matematica/pagina_2.jpg`
- `auditoria_visual_matematica/pagina_3.jpg`
- `auditoria_visual_matematica/pagina_4.jpg`
- `auditoria_visual_matematica/pagina_5.jpg`
- `backup_antes_imagens_matematica_20261105_164318.sqlite3`
- `backup_antes_recuperacao_20261105_161440.sqlite3`
- `contextos_docx_matematica.json`
- `inserir_textos.py`
- `inventario_imagens_matematica.csv`
- `previa_imagens_matematica.json`
- `previa_imagens_matematica.md`
- `previa_recuperacao.json`
- `recuperar_imagens_matematica.py`
- `recuperar_textos_auditados.py`
- `relatorio_imagens_matematica.json`
- `relatorio_imagens_matematica.md`
- `relatorio_recuperacao.json`
- `relatorio_recuperacao.md`

## Arquivos com comentários removidos

- `config/settings.py`
- `dashboard/admin.py`
- `dashboard/models.py`
- `dashboard/tests.py`
- `dashboard/views/questao.py`
- `gabarita_if/tests.py`
- `gabarita_if/views/caderno.py`
- `gabarita_if/views/questao.py`
- `usuarios/models.py`
- `usuarios/tests.py`
- `usuarios/urls.py`
- `website/admin.py`
- `website/models.py`
- `website/tests.py`

## Arquivos com imports limpos ou exports explicitados

- `dashboard/admin.py`
- `dashboard/models.py`
- `dashboard/tests.py`
- `dashboard/views/avaliacao.py`
- `dashboard/views/main.py`
- `dashboard/views/questao.py`
- `dashboard/views/texto.py`
- `dashboard/views/usuario.py`
- `gabarita_if/tests.py`
- `gabarita_if/urls.py`
- `gabarita_if/views/__init__.py`
- `gabarita_if/views/caderno.py`
- `usuarios/tests.py`
- `usuarios/urls.py`
- `usuarios/views.py`
- `website/admin.py`
- `website/models.py`
- `website/tests.py`
- `website/views.py`

## Dependências

- requirements.txt contém todas as dependências de produção, sem duplicatas e em UTF-8 (antes estava em UTF-16).
- python-docx==1.2.0 incluído: usado pelos comandos de importação.
- requirements.prod.txt contém apenas -r requirements.txt, mantendo compatibilidade com Docker.

## Verificação estrutural

- A etapa de limpeza de Python comparou as ASTs antes/depois e confirmou equivalência, desconsiderando apenas imports.
- Banco ativo, mídia, documentos originais, templates e arquivos de execução preservados byte a byte.
- Imports públicos utilizados pelas rotas foram preservados.
- Comentários explicativos de regras e configurações importantes preservados.
- Nenhum commit realizado.

## Estrutura final da raiz

Validações finais: `manage.py check` sem problemas; Ruff F401/F841 aprovado;
sintaxe de 65 arquivos Python válida; 65 dependências sem duplicatas;
`git diff --check` sem erros de whitespace.

```text
.git/
.github/
arquivos_originais/
config/
dashboard/
docs/
gabarita_if/
media/
nginx/
static/
staticfiles/
templates/
usuarios/
venv/
website/
.dockerignore
.gitignore
db.sqlite3
docker-compose.yml
Dockerfile
entrypoint.sh
LICENSE
manage.py
README.md
requirements.prod.txt
requirements.txt
```
