# Testes visuais de regressão

Specs Playwright em `tests/visual/`, com config própria (`playwright.visual.config.ts`). `tests/e2e/` cobre comportamento; aqui se compara imagem. Os testes são excluídos do Vitest e **rodam só localmente, fora do CI**: a fonte do sistema renderiza diferente entre Windows e Linux, e os snapshots são gerados no Windows da equipe.

## Rodar

```bash
cd frontend
npm run test:visual
```

Compara o app local (modo `path`; o Vite sobe sozinho na 5173) com os 12 snapshots de `tests/visual/__screenshots__/`: 4 rotas públicas (`/`, `/indicadores`, `/relatorios`, `/sobre`) × 3 viewports (1440x900, 768x1024, 390x844). A tolerância é `maxDiffPixelRatio: 0.001`.

## Regerar o baseline

Regra: **o baseline vem do protótipo** (branch `origin/gh-pages/prototype`), **exceto páginas com conteúdo novo**, que não existe no protótipo. Essas páginas têm baseline gerado a partir do app atual.

| Rota | Origem do baseline |
| --- | --- |
| `/`, `/indicadores`, `/relatorios` | protótipo |
| `/sobre` | app atual (desde a seção Cadastur e FNRH Digital e os logotipos dos três níveis) |

**Nunca rode `test:visual:update` sem `VISUAL_BASE_URL` e `VISUAL_ROUTE_MODE`**: sem elas você sobrescreveria o baseline sem escolher a origem. O `make front-visual-update` recusa rodar sem as duas.

### Páginas do protótipo

O protótipo usa `createHashRouter` (URLs com `#`), por isso a regeração usa `VISUAL_ROUTE_MODE=hash`. **Exclua as páginas que têm baseline do app** (hoje, `sobre`) com `--grep-invert`; sem isso o snapshot delas seria trocado pela versão do protótipo, sem o conteúdo novo.

1. Obtenha o código do protótipo em uma pasta separada (por exemplo, uma worktree de `origin/gh-pages/prototype` fora da árvore do projeto) e rode `npm ci` em `frontend/`.
2. Suba o protótipo na porta 5199, com base `/` e `--strictPort`:
   - Git Bash: `MSYS_NO_PATHCONV=1 npx vite --base / --port 5199 --strictPort` (o prefixo evita que o Git Bash converta `/` em caminho do Windows).
   - PowerShell: `npx vite --base / --port 5199 --strictPort`.
3. Em outro terminal, em `frontend/` deste repositório:
   - Git Bash: `VISUAL_BASE_URL=http://localhost:5199 VISUAL_ROUTE_MODE=hash npm run test:visual:update -- --grep-invert sobre`
   - PowerShell: `$env:VISUAL_BASE_URL="http://localhost:5199"; $env:VISUAL_ROUTE_MODE="hash"; npm run test:visual:update -- --grep-invert sobre`

`--update-snapshots` (modo `changed`) só reescreve os snapshots que falham: um PNG ruim dentro da tolerância sobrevive à regeração. Para regerar inteiro o baseline das páginas do protótipo:

```bash
VISUAL_BASE_URL=http://localhost:5199 VISUAL_ROUTE_MODE=hash npx playwright test --config playwright.visual.config.ts --update-snapshots=all --grep-invert sobre
```

### Páginas com conteúdo novo (baseline do app)

Regere **só os snapshots afetados**, a partir do app atual, filtrando a rota com `-g`. Com o Vite no ar (`make front-dev`), em `frontend/`:

- Git Bash: `VISUAL_BASE_URL=http://localhost:5173 VISUAL_ROUTE_MODE=path npx playwright test --config playwright.visual.config.ts -g sobre --update-snapshots`
- PowerShell: `$env:VISUAL_BASE_URL="http://localhost:5173"; $env:VISUAL_ROUTE_MODE="path"; npx playwright test --config playwright.visual.config.ts -g sobre --update-snapshots`

Depois rode `make front-visual` completo: os 12 devem passar. O PR deve listar quais snapshots mudaram e por quê. Se uma nova página passar a ter conteúdo que não existe no protótipo, acrescente-a à tabela acima e ao `--grep-invert` dos comandos do protótipo (por exemplo, `--grep-invert "sobre|outra"`).
