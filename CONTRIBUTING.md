# **Prompter para AI – Notae (Python)**

Crie um **CLI diário/registro pessoal criptografado** para Linux, chamado `notae`, seguindo estas regras:

---

## **1. Funcionalidade**

* Offline, sem banco de dados, sem anexos.
* Cada nota em arquivo separado (`.note`) no diretório `~/notes/`.
* Criptografia: GPG/AES-256.
* Decifração apenas na leitura ou export.
* Logs detalhados em `~/.notae_logs/` (erros da aplicação e falhas de senha).
* Sessão de senha estilo `sudo` (5 min), 3 tentativas, bloqueio de 5 min em caso de falha.

---

## **2. Arquivos**

* Extensão: `.note`
* Nome: `YYYYMMDD-HHMMSS-titulo_sanitizado.note`

  * Minusculas
  * Espaços → `_`
  * Remover acentos e caracteres especiais
* Conteúdo decifrado dentro do arquivo:

```text
Title: título original (mantém maiúsculas, acentos, espaços)
Category: opcional
Tags: até 3, opcionais
Timestamp: YYYYMMDD-HHMMSS

Conteúdo da nota
```

---

## **3. Metadados**

* Timestamp automático
* Título sempre obrigatório
* Categoria: opcional, 1 por nota
* Tags: opcionais, até 3
* Export mantém metadados
* Listagem e pesquisa usam título, data, tags e categoria; **conteúdo não decifrado para performance**

---

## **4. Comandos CLI**

* `notae new [-t "titulo"] [-n "nota"] [-c "categoria"] [-g "tag1,tag2,tag3"]`

  * Cria nota; abre `$EDITOR` se faltar título ou conteúdo.
* `notae read <timestamp-titulo>` → mostra conteúdo decifrado
* `notae edit <timestamp-titulo>` → reabre no `$EDITOR`
* `notae delete <timestamp-titulo>` → remove nota
* `notae list [--sort date/title] [--order asc/desc] [--filter YYYY-MM]` → listagem rápida
* `notae export <arquivo_destino>` → merge de todas notas, inclui metadados
* `notae stats` → resumo (total, categorias, tags, últimas datas)
* `notae tag <tag>` → lista notas com tag
* `notae search <query>` → pesquisa rápida em título, tags, categoria

---

## **5. Regras de comportamento**

* Título e nota podem ser gerados automaticamente se fornecidos via CLI
* Categoria e tags são opcionais
* Sessão de senha mantém timer de 5 min
* Logs detalhados para depuração
* Nenhum backup automático

---

## **6. Outras observações**

* Toda a implementação em **Python 3**
* CLI deve ser avançada desde a primeira versão
* Sem abstrações C/C++ ou shell; adaptar exemplos conceituais para Python
* Export sempre merge único; separação de notas é trivial via arquivos `.note`
* Estrutura de projeto deve permitir fácil manutenção e extensão futura

---

Em uma linguagem menos tecnica:

Fechou, mano! 😎 Então agora o nome oficial do CLI vai ser **`notae`**.
Vou refazer **o documento completo em Markdown** pra tu copiar na moral, já com tudo que definimos, comandos, regras, criptografia, logs… nada de abstração, tudo detalhado.

---

# **Notae – CLI Diário/Notas Blindadas Linux**

**Objetivo:**
Criar um **diário/registro pessoal offline** para Linux, totalmente seguro, criptografado e baseado em arquivos `.note`, gerenciável via CLI, sem banco de dados, sem anexos, com logs detalhados, timer de sessão para senha e comandos avançados desde o início.

---

## **1. Estrutura de arquivos**

* Diretório padrão: `~/notes/`

* Extensão de arquivo: `.note`

* Nome de arquivo: `YYYYMMDD-HHMMSS-titulo_sanitizado.note`

  * Minusculas
  * Espaços → `_`
  * Remover acentos e caracteres especiais
  * Exemplo: `"Meu Diário do Dia!"` → `20260331-121000-meu_diario_do_dia.note`

* **Interno do arquivo (`.note`):**

```
Title: Meu Diário do Dia
Category: pessoal          # opcional
Tags: trabalho, estudo     # até 3, opcionais
Timestamp: 20260331-121000

Conteúdo da nota aqui...
```

* **Nota:** categoria e tags são opcionais.
* **Criptografia:** AES-256 via GPG; cada nota criptografada individualmente; decifração apenas em `read` e `export`.

---

## **2. CLI – Comandos principais**

* **`notae new [-t "titulo"] [-n "conteudo"] [-c "categoria"] [-g "tag1,tag2,tag3"]`**

  * Cria nova nota.
  * Se passar título e conteúdo, gera automaticamente.
  * Se faltar título ou conteúdo → abre `$EDITOR`.
  * Categoria e tags opcionais.

* **`notae read <timestamp-titulo>`**

  * Lê nota decifrada.

* **`notae list [--sort date/title] [--order asc/desc] [--filter YYYY-MM]`**

  * Lista notas com data formatada + título.
  * Ordenação: por data ou título, crescente/decrescente.
  * Filtro opcional: mês/ano (`--filter 2026-03`).

* **`notae export <arquivo_destino>`**

  * Merge de todas notas decifradas, metadados incluídos.

* **`notae edit <timestamp-titulo>`**

  * Reabre nota no `$EDITOR`.
  * Salva novamente criptografada.

* **`notae delete <timestamp-titulo>`**

  * Remove nota, pede confirmação antes.

* **`notae stats`**

  * Resumo de notas: total, distribuição por categoria/tag, últimas X datas.

* **`notae tag <tag>`**

  * Lista notas filtradas por tag.

* **`notae search <query>`**

  * Pesquisa rápida em **título, tags e categoria**, sem decifrar conteúdo.

---

## **3. Regras de senha e sessão**

* Timer estilo `sudo` (5 minutos).
* Três tentativas; se falhar → bloqueio 5 minutos.
* Timer reinicia a cada operação de autenticação.
* Sessão compartilhada durante execução da CLI; múltiplos terminais independentes pedem nova senha.

---

## **4. Logs**

* Diretório oculto: `~/notes/.notae_logs/`
* Arquivos de log:

  * `errors.log` → erros da aplicação
  * `auth.log` → falhas de senha, bloqueios
* Usuário vê mensagens simples, logs detalhados ficam apenas nos arquivos.

---

## **5. Metadados**

* **Category:** opcional, 1 por nota
* **Tags:** opcional, até 3
* **Timestamp:** automático no filename e nos metadados
* **Title:** pode ter acentos/espaços dentro do arquivo; filename sanitizado

---

## **6. Regras de criação de notas**

* Título e conteúdo opcionais → abre `$EDITOR` se faltar.
* Categoria e tags opcionais.
* Timestamp automático (`YYYYMMDD-HHMMSS`).
* Arquivo final criptografado via GPG/AES-256.

---

## **7. Pesquisa e listagem**

* Pesquisa rápida: título, tags, categoria.
* Ordenação/listagem: por data ou título, crescente/decrescente.
* Filtro opcional por mês/ano (`YYYY-MM`).
* Conteúdo **não decifrado na pesquisa/listagem** → performance.

---

## **8. Exportação**

* Comando: `notae export <arquivo_destino>`
* Merge de todas notas em **um único TXT decifrado**.
* Inclui metadados de cada nota.

---

## **9. Criptografia**

* GPG com **AES-256**
* Cada nota criptografada individualmente
* Decifração somente em `read` e `export`
* Senhas **não armazenadas em disco**

---

## **10. Fluxo geral**

1. Usuário abre CLI (`notae`)
2. Operação exige senha → pede se não houver sessão ativa
3. Operação executada (`new`, `read`, `list`, etc.)
4. Logs detalhados gravados em `.notae_logs`
5. Sessão de senha mantém timer estilo sudo
6. Saída limpa pro usuário

---

## **11. Comandos desde o início**

Todos já implementados na primeira versão:
`new`, `read`, `list`, `export`, `edit`, `delete`, `stats`, `tag`, `search`

---

## **12. Observações**

* Sem banco de dados
* Sem anexos
* Expansão futura possível respeitando criptografia e logs

---
