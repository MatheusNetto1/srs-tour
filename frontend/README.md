# SRS Tour --- Frontend

Frontend da aplicação SRS Tour desenvolvido com React e TypeScript.

## Tecnologias

-   Node.js 24
-   TypeScript
-   React
-   Vite
-   Tailwind CSS
-   Biome
-   Vitest
-   Testing Library
-   Playwright

## Pré-requisitos

Para execução local:

-   Node.js 24+
-   npm

Alternativamente, o frontend pode ser executado utilizando Docker a
partir da raiz do projeto.

## Instalação

A partir da raiz:

``` bash
make install-front
```

Ou diretamente:

``` bash
cd frontend
npm ci
```

## Executando localmente

A partir da raiz:

``` bash
make front-dev
```

Ou diretamente:

``` bash
cd frontend
npm run dev
```

A aplicação ficará disponível em `http://localhost:5173`.

## Executando com Docker

A partir da raiz:

``` bash
make up
```

Ou:

``` bash
docker compose up
```

No container, o Vite usa polling (`DEV_USE_POLLING=true` no `compose.yml`):
sem isso, no Windows, uma edição em `src/` não chega ao navegador até
reiniciar o serviço. No host (`make front-dev`) o polling fica desligado. A
porta do host é `FRONTEND_HOST_PORT` (padrão 5173); o serviço tem
`healthcheck` e só sobe depois do backend ficar `healthy`. Exemplo das
variáveis em [`.env.example`](../.env.example) (raiz).

## Acesso à API

O Vite encaminha `/api` para o backend (`server.proxy`), então o navegador fala
só com a origem do frontend e não há CORS. O destino é `API_PROXY_TARGET`
(padrão `http://localhost:8000`; no container, `http://backend:8000`, definido
no `compose.yml`). Exemplo de variáveis em [`.env.example`](.env.example).

Em `src/api/`:

-   `client.ts`: `request<T>(path, { method, query, body, signal })`, o **único**
    ponto de `fetch`. Base `VITE_API_BASE_URL` (padrão `/api/v1`), envia JSON,
    anexa `Authorization: Bearer` quando há token e trata `204`.
-   `errors.ts`: `ApiError` (`status`, `code`, `detail`, `errors`). Normaliza o
    envelope de erro novo (`detail` + `code` + `errors`) e o formato antigo
    (`detail` string, ou `detail` lista no 422). Falha de rede vira `status: 0`,
    `code: "network_error"`; resposta que não é JSON vira `internal_error`.
-   `token.ts`: token em `sessionStorage` (`srs-tour.token`), tolerante a storage
    indisponível.
-   `useApiQuery.ts`: `useApiQuery(fetcher, deps)` devolve `status`
    (`loading | error | empty | success`), `data`, `error` e `refetch()`; cancela
    ao desmontar e ignora resposta atrasada.

`LoadingState`, `ErrorState` e `EmptyState` (`src/components/ui/`) mostram cada
estado; ainda não são usados pelas páginas.

### Tipos do OpenAPI

Com o backend no ar (`make up`):

``` bash
make front-api-types
```

Gera `src/api/schema.d.ts` a partir de `${API_PROXY_TARGET}/openapi.json`. O
arquivo está no `.gitignore` e nada o importa por enquanto (assim `tsc -b` e o
CI não dependem do backend).

### Override do TypeScript no `package.json`

O `openapi-typescript` (7.13.0, fixado) declara `peer typescript@^5.x`, mas o
projeto usa TypeScript 6. Sem ajuste, o `npm install` falha com `ERESOLVE`. O
`package.json` tem um `overrides` restrito a esse pacote
(`"openapi-typescript": { "typescript": "$typescript" }`), que o faz usar o
TypeScript do projeto. A geração de tipos foi validada com o TS 6.

**Remover o `overrides`** quando o `openapi-typescript` declarar suporte ao
TypeScript 6 no `peerDependencies` (confira com `npm view openapi-typescript
peerDependencies`) e confirmar que `npm ci` segue passando.

## Build

Para gerar o build de produção:

``` bash
make front-build
```

Ou:

``` bash
cd frontend
npm run build
```

Os arquivos gerados serão armazenados em `dist/`.

## Qualidade de código

O projeto utiliza Biome para lint e formatação.

### Lint

``` bash
make front-lint    # só regras de lint
make front-check   # lint + formato + imports (o que o CI roda)
```

Ou:

``` bash
cd frontend
npx biome lint .
npm run lint       # biome check .
```

### Formatação

``` bash
make front-format
```

Ou:

``` bash
cd frontend
npm run format
```

### Correções automáticas

``` bash
make front-lint-fix
```

Ou:

``` bash
cd frontend
npm run lint:fix
```

## Testes

### Vitest

Os testes unitários e de componentes utilizam Vitest e Testing Library.

``` bash
make front-test
```

Ou:

``` bash
cd frontend
npm run test:run
```

Para executar o Vitest em modo watch:

``` bash
cd frontend
npm run test
```

### Playwright

Os testes end-to-end utilizam Playwright. Instale os browsers uma vez (o
`make setup` já faz isso):

``` bash
make front-install-browsers
make front-e2e
```

Ou:

``` bash
cd frontend
npm run test:e2e
```

Os testes E2E estão localizados em `tests/e2e/` e só precisam do Vite. No CI
rodam no job `Frontend E2E`, com `make front-install-browsers
PLAYWRIGHT_INSTALL_ARGS=--with-deps` (dependências de sistema do Linux); o
relatório e os traces são publicados como artifact quando falham.

Se `make front-e2e` falhar com o frontend do Docker rodando (porta 5173), rode
`make rebuild` para renovar o `node_modules` do container.

### Regressão visual

Os testes visuais (`make front-visual`, ou `npm run test:visual`) rodam só
localmente e não fazem parte do `make test-all`. Para regerar o baseline,
`make front-visual-update` exige `VISUAL_BASE_URL` e `VISUAL_ROUTE_MODE`. Veja
[`tests/visual/README.md`](tests/visual/README.md), inclusive como regerar
os snapshots.

O Playwright inicia automaticamente o servidor Vite durante a execução
dos testes.

## Scripts

  Script               Descrição
  -------------------- ----------------------------------------
  `npm run dev`        Inicia o servidor Vite
  `npm run build`      Gera o build de produção
  `npm run lint`       Executa as verificações do Biome
  `npm run lint:fix`   Aplica correções do Biome
  `npm run format`     Formata o código
  `npm run test`       Executa Vitest em modo watch
  `npm run test:run`   Executa os testes uma vez
  `npm run test:e2e`   Executa os testes Playwright
  `npm run preview`    Executa localmente o build de produção
