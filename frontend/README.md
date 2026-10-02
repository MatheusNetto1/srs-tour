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
make front-lint
```

Ou:

``` bash
cd frontend
npm run lint
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
make front-fix
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

Os testes end-to-end utilizam Playwright:

``` bash
make front-e2e
```

Ou:

``` bash
cd frontend
npm run test:e2e
```

Os testes E2E estão localizados em `tests/e2e/`.

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
