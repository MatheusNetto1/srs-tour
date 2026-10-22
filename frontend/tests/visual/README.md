# Testes visuais de regressão

Specs Playwright em `tests/visual/`, com config própria (`playwright.visual.config.ts`). `tests/e2e/` cobre comportamento; aqui se compara imagem. Os testes são excluídos do Vitest e **rodam só localmente, fora do CI**: a fonte do sistema renderiza diferente entre Windows e Linux, e os snapshots são gerados no Windows da equipe.

## Rodar

```bash
cd frontend
npm run test:visual
```

Compara o app local (modo `path`; o Vite sobe sozinho na 5173) com os 12 snapshots de `tests/visual/__screenshots__/`: 4 rotas públicas (`/`, `/indicadores`, `/relatorios`, `/sobre`) × 3 viewports (1440x900, 768x1024, 390x844). A tolerância é `maxDiffPixelRatio: 0.001`.

## Regerar o baseline

O baseline vem **somente do protótipo** (branch `origin/gh-pages/prototype`), nunca do `develop`. O protótipo usa `createHashRouter` (URLs com `#`), por isso a regeração exige as variáveis abaixo. **Nunca rode `test:visual:update` sem elas**: sem `VISUAL_BASE_URL` você sobrescreveria o baseline com o app atual.

1. Obtenha o código do protótipo em uma pasta separada (por exemplo, uma worktree de `origin/gh-pages/prototype` fora da árvore do projeto) e rode `npm ci` em `frontend/`.
2. Suba o protótipo na porta 5199, com base `/` e `--strictPort`:
   - Git Bash: `MSYS_NO_PATHCONV=1 npx vite --base / --port 5199 --strictPort` (o prefixo evita que o Git Bash converta `/` em caminho do Windows).
   - PowerShell: `npx vite --base / --port 5199 --strictPort`.
3. Em outro terminal, em `frontend/` deste repositório:
   - Git Bash: `VISUAL_BASE_URL=http://localhost:5199 VISUAL_ROUTE_MODE=hash npm run test:visual:update`
   - PowerShell: `$env:VISUAL_BASE_URL="http://localhost:5199"; $env:VISUAL_ROUTE_MODE="hash"; npm run test:visual:update`

`--update-snapshots` (modo `changed`) só reescreve os snapshots que falham: um PNG ruim dentro da tolerância sobrevive à regeração. Para regerar o baseline inteiro:

```bash
VISUAL_BASE_URL=http://localhost:5199 VISUAL_ROUTE_MODE=hash npx playwright test --config playwright.visual.config.ts --update-snapshots=all
```
