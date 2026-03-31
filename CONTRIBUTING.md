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
Timestamp: YYYYMMDDHHMMSS

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
