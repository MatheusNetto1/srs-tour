# Guia de contribuição

Este guia descreve o **processo**: do primeiro dia até o merge. As regras técnicas
(arquitetura, testes, listas de áreas e tipos, comandos) ficam só no
[`AGENTS.md`](AGENTS.md), que também é lido pelos agentes de código. Aqui só
linkamos para ele, para não ter duas versões da mesma regra.

## Sumário

- [Primeiro dia](#primeiro-dia)
- [VS Code](#vs-code)
- [Fluxo de trabalho](#fluxo-de-trabalho)
- [CI e checks obrigatórios](#ci-e-checks-obrigatórios)
- [Revisão](#revisão)
- [Squash merge](#squash-merge)
- [PRs empilhados](#prs-empilhados)
- [Versões de Python, Node e Poetry](#versões-de-python-node-e-poetry)
- [Agentes de código](#agentes-de-código)

## Primeiro dia

Todo o time usa Windows com **Git Bash** e GNU Make (veja os pré-requisitos no
[`README.md`](README.md#pré-requisitos)). Na raiz do repositório:

```bash
make setup   # valida versões, cria backend/.env, instala dependências e browsers do Playwright
make up      # sobe banco, backend e frontend; as migrations rodam sozinhas
```

Para rodar os testes do backend, o banco de teste precisa estar migrado:
`make back-test-migrate`. A lista completa de comandos está em `make help` e na
seção [Comandos](AGENTS.md#comandos) do `AGENTS.md`.

O backend roda de dois jeitos: **Poetry no host** (`make back-test`, `make seed`,
`make back-migration`, exigem `make install-back`) ou **tudo em container**
(`make docker-back-test`, `make docker-seed`, `make docker-back-migration m="..."`,
exigem apenas `make up`). Para dois clones ou branches ao mesmo tempo, mude
`COMPOSE_PROJECT_NAME` e as portas `*_HOST_PORT` (veja `.env.example`).

## VS Code

O repositório versiona uma configuração mínima em `.vscode/` (`extensions.json`,
`settings.json` e `launch.json`). Ao abrir a pasta, o VS Code sugere as extensões
recomendadas (Biome, Ruff, Python, Playwright, Vitest, EditorConfig, Tailwind CSS
IntelliSense e Docker). Instale-as: o formatador padrão e o *format on save* dependem
de Biome (TypeScript, JSON e CSS) e Ruff (Python).

> **Atenção: backup do `.vscode/settings.json` local.**
> Esse arquivo antes era ignorado pelo Git. Se você já tem um `.vscode/settings.json`
> (ou `extensions.json`/`launch.json`) na sua cópia, o `git pull`/`git switch` que
> traz a versão versionada **falha** com *"The following untracked working tree files
> would be overwritten"*. Antes de atualizar a branch:
>
> ```bash
> mv .vscode/settings.json .vscode/settings.json.bak   # repita para extensions.json e launch.json, se existirem
> ```
>
> Depois do checkout, leve o que for preferência pessoal (tema, fonte etc.) para as
> *User settings* do VS Code. O arquivo do projeto só tem configuração de projeto.

### Venv do backend (`backend/.venv`)

O `backend/poetry.toml` manda o Poetry criar o ambiente em `backend/.venv`, um caminho
fixo dentro do projeto que a extensão Python Environments do VS Code encontra pelo
gerenciador configurado no `settings.json`. Em um clone novo, o `make setup` já cria o
`.venv` e não há nada a migrar.

Quem já tem um ambiente criado pelo Poetry **fora** da pasta (no cache do Poetry)
continua usando esse ambiente antigo até removê-lo. Faça a migração **junto com o
backup do `settings.json`**, e também se for testar uma branch com essas mudanças antes
do merge. No Git Bash:

1. Se o terminal abrir com algum venv ativado, rode `deactivate`.
2. `cd backend && poetry env list` para ver o nome do ambiente antigo.
3. `poetry env remove <nome>`. Não use `--all`: com `in-project` ativo, ele não enxerga
   o ambiente do cache.
4. `poetry install`.
5. `poetry env info --path` deve terminar em `backend\.venv`.

No VS Code:

1. `Developer: Reload Window`.
2. Em `Python: Select Interpreter`, escolha
   `poetry (3.12.10) .\backend\.venv\Scripts\python.exe` (marcado como *Workspace*).
   **Não** escolha as entradas `venv` em `AppData\Roaming\pypoetry`: são o ambiente
   interno do Poetry, não o do projeto.

> Depois da migração, o VS Code pode continuar mostrando *"Um interpretador Python
> inválido foi selecionado"*. Se a barra de status mostrar `poetry (3.12.10)` e os
> imports resolverem, ignore o aviso: é uma referência antiga da extensão Python
> Environments ao venv do cache.

O terminal do VS Code **não ativa o venv automaticamente** (o `settings.json` desliga a
ativação). O fluxo continua sendo `make` (da raiz) e `poetry run` (em `backend/`). A
ativação automática chegou a ativar o ambiente interno do Poetry, onde um
`poetry install` instalaria as dependências do projeto no lugar errado.

O `.editorconfig` evita diffs de indentação e de fim de linha em editores sem
plugin, mas **os formatadores são a autoridade**: Biome no frontend e Ruff no backend.

## Fluxo de trabalho

1. **Atualize e crie a branch** a partir de `develop`:
   `git switch develop && git pull && git switch -c <iniciais>/<tipo>/<descricao-em-kebab-case>`.
   Tipos e formato: [Git, PRs e CI](AGENTS.md#git-prs-e-ci). O workflow `PR Conventions`
   reprova nome fora do padrão (e o nome de um PR aberto não muda: seria preciso abrir outro).
2. **Faça alterações pequenas e focadas.** Uma mudança por PR; nada fora do escopo.
   Veja [Regras para alterações](AGENTS.md#regras-para-alterações).
3. **Commite** em Conventional Commits em PT-BR, com escopo opcional, assunto de até
   72 caracteres: `feat(tourism): adiciona CRUD de estabelecimentos`. **Nunca** inclua
   linha de atribuição a IA (`Co-Authored-By`, "Generated with…").
4. **Rode as verificações antes de abrir o PR:** `make check-all` e `make test`
   (`make test-all` se o fluxo tem E2E). Mudou model? Gere a migration com
   `make back-migration` (ou `make docker-back-migration`) e revise o arquivo.
   O CI reprova mais de uma head de migrations (`make back-migration-single-head`):
   se acusar, ajuste o `down_revision` da sua migration.
5. **Abra o PR** para `develop` (ou para a branch base, se for [empilhado](#prs-empilhados)).
   O template já traz o checklist. O título segue `[Área] [Tipo] Título` (listas em
   [Git, PRs e CI](AGENTS.md#git-prs-e-ci)) e **vira o commit em `develop`**, então
   escreva-o como mensagem de commit.
6. **Peça revisão** a alguém do time e acompanhe o CI.

## CI e checks obrigatórios

Todo PR (qualquer base, inclusive empilhado), push em `main`/`develop` e disparo manual
rodam os workflows. Eles chamam os mesmos alvos `make` do uso local, então o que passa
no `make check-all` e no `make test-all` passa no CI. Checks exigidos para o merge em
`develop` e `main`:

| Check | O que valida |
|---|---|
| `Backend` | Ruff, versões em sincronia, migrations no banco de teste, `alembic check` e pytest |
| `Backend Docker Build` | build da imagem do backend |
| `Frontend` | Biome, Vitest e build (`tsc -b` + Vite) |
| `Frontend E2E` | Playwright (só precisa do Vite) |
| `PR Conventions` | título `[Área] [Tipo] Título` e nome da branch |

O teste visual do frontend roda só localmente (veja
[`frontend/tests/visual/README.md`](frontend/tests/visual/README.md)).

Para rodar um workflow manualmente numa branch já enviada ao remoto:

```bash
gh workflow run "Backend CI" --ref <branch>
gh workflow run "Frontend CI" --ref <branch>
gh run list --branch <branch>
```

## Revisão

Critérios gerais, extraídos das revisões anteriores. Valem para quem abre o PR (confira
antes de pedir revisão) e para quem revisa.

**Escopo e histórico**

- O PR contém só o que foi pedido. Fora de escopo e arquivos que não são do projeto
  (`.dev/`, `dist/`, `node_modules/`) não entram; **lockfile** só muda quando a
  dependência muda (um `package-lock.json` apagado quebra `npm ci`, Docker e CI).
- A branch está atualizada com a base e **o CI rodou no PR**. Sem CI não há aprovação.
  Branch atrasada que carrega commits já mergeados por squash polui o diff: atualize
  (ou veja [PRs empilhados](#prs-empilhados)).
- Commits em Conventional Commits PT-BR, assunto com até 72 caracteres, sem atribuição
  a IA; branch no padrão.

**Descrição verdadeira e verificável**

- Tudo o que a descrição afirma precisa ser conferível: link do run do CI, contagem de
  testes, arquivos e linhas. Não marque no checklist o que não foi feito.
- Mudança visual: capturas lado a lado nos viewports relevantes (ou a evidência da
  comparação automática). Mudança de CI: link do run verde **e** a prova de que o CI
  falha quando deve.
- Diga o que **não** foi validado. Dependências novas precisam de justificativa.

**Fidelidade e testes**

- A implementação segue a especificação ou o protótipo; divergência é intencional e
  está descrita.
- Os testes cobrem o sucesso e os principais erros, e **falhariam se o comportamento
  quebrasse**: confira o caso negativo (ex.: o link inativo *não* tem a classe de
  ativo), não só o positivo.
- Desconfie de verde vazio: um teste que passa sem exercer o que o título diz (por
  exemplo, `test.use({ viewport })` dentro de um laço, que faz todos os testes rodarem
  no mesmo viewport). Não silencie nem remova teste para a suíte passar.
- Além de lint e testes, rode o **build** (`make front-build` roda `tsc -b` e pega
  erros que o Vitest não pega).
- Mudou comportamento, comando ou convenção: testes e `AGENTS.md`/`README.md`
  atualizados, e o texto não diz o que o código não faz.

**Como o revisor classifica os achados**

| Nível | Significado |
|---|---|
| Bloqueante | impede o merge: defeito, quebra de CI, descumprimento de requisito |
| Importante | deve ser resolvido antes do merge (ex.: CI não rodou, evidência ausente) |
| Menor | melhoria sem risco, pode ir em PR posterior |
| Sugestão | informativo |

Para cada achado, indique a evidência (arquivo, linha, comando) e a correção. Reproduza
localmente quando possível, de preferência num `git worktree` separado, para não
alterar a sua árvore de trabalho.

## Squash merge

O merge em `develop` é **squash**: o título do PR vira o commit, e os commits da branch
somem do histórico. Por isso o título precisa estar no padrão, e commits intermediários
ruins não importam para o histórico (mas importam para a revisão). Depois do merge,
apague a branch.

## PRs empilhados

Use quando um PR **depende de outro ainda não mergeado** (por exemplo, o PR 2 usa o que
o PR 1 introduz), ou para fatiar uma mudança grande em PRs revisáveis.

- A **base** do PR é a branch do PR anterior, não `develop`. O diff mostra só o que é
  novo. O CI roda normalmente, mas o `PR Conventions` só valida PRs com base em
  `develop`/`main`.
- Mergeie **de baixo para cima**: primeiro o PR 1 em `develop`, depois o PR 2, e assim
  por diante.
- Como o merge é squash, o commit do PR 1 em `develop` tem outro hash. O PR 2 ainda
  carrega os commits antigos do PR 1 e precisa ser reposicionado.

Depois do squash merge da base (aqui, `A` é a branch do PR 1 e `B` a do PR 2). Anote o
último commit de `A` **antes** de apagá-la (`git rev-parse origin/A`) ou ache-o com
`git log --oneline` na sua `B`:

```bash
git fetch origin
git rebase --onto origin/develop <ultimo-commit-de-A> B
git push --force-with-lease
```

`--onto` leva para `develop` apenas os commits que estão depois de `<ultimo-commit-de-A>`,
descartando os do PR 1. Em seguida, no GitHub, mude a base do PR 2 para `develop` (o
GitHub faz isso sozinho ao apagar a branch `A` no merge). Ao mudar a base para
`develop`, o `PR Conventions` passa a validar o título e a branch.

Com **mais de dois PRs** (`A` ← `B` ← `C`), `--update-refs` reposiciona as branches
intermediárias junto (Git 2.38+):

```bash
git rebase --update-refs --onto origin/develop <ultimo-commit-de-A> C
git push --force-with-lease origin B C
```

Conflitos no rebase: resolva, `git add` e `git rebase --continue`. Se der errado,
`git rebase --abort` volta ao estado anterior. Antes de reescrever, confirme com
`git log --oneline origin/develop..B` quais commits restam.

## Versões de Python, Node e Poetry

A fonte única é o par `.python-version` e `.nvmrc` na raiz. Os workflows
(`python-version-file`, `node-version-file`) e o `make check` leem deles; o Poetry tem
a versão mínima em `requires-poetry` (`backend/pyproject.toml`). Para trocar uma
versão, altere o arquivo de pin e rode `make check-pins`: ele acusa os Dockerfiles,
`engines` e `requires-python` que ficaram para trás (o CI roda a mesma checagem).
O nvm para Windows não lê `.nvmrc` sozinho: use `nvm use 24` com a versão do arquivo.

## Agentes de código

O [`AGENTS.md`](AGENTS.md) da raiz é a **fonte única** de instruções para agentes de
código (Claude Code, Codex CLI e Gemini CLI). Edite só ele.

- Não crie `CLAUDE.md`, `GEMINI.md` nem `CLAUDE.local.md`. O Claude Code só lê o
  `AGENTS.md` quando não existe nenhum `CLAUDE.md` (nem `CLAUDE.local.md`) no
  diretório de trabalho ou acima dele. **No menu `/memory` do Claude Code, não
  selecione a opção que cria o `CLAUDE.md`.**
- **Claude Code**: versão mínima v2.1.277. Confirme com `/memory` (ou pela linha
  `no CLAUDE.md found; AGENTS.md loaded: ...` no início da sessão).
- **Codex CLI**: lê o `AGENTS.md` nativamente. Confirme com
  `codex --ask-for-approval never "Show which instruction files are active."`.
- **Gemini CLI**: o `.gemini/settings.json` do repositório aponta `context.fileName`
  para o `AGENTS.md`. Confirme pelo contador de arquivos de contexto no rodapé ou com
  `/memory show`.
  - Se o recurso de pastas confiáveis estiver ativo (`security.folderTrust.enabled`,
    desligado por padrão), o Gemini ignora o `.gemini/settings.json` de pastas não
    confiáveis. Confie na pasta do projeto com `/permissions` (ou em
    `~/.gemini/trustedFolders.json`).
- Regra do time: nenhuma linha de atribuição a IA em commits e PRs. Está no
  `AGENTS.md` e, no Claude Code, em `.claude/settings.json`.
