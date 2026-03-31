# 📔 Notae - CLI de Notas Blindadas (AES-256)

**Notae** é um sistema de diário e registro pessoal offline para Linux, focado em **privacidade extrema** e segurança. Ele transforma seu terminal em um cofre seguro para seus pensamentos, ideias e registros diários.

---

## 🚀 Principais Recursos

*   🔐 **Criptografia AES-256**: Cada nota é um arquivo `.note` individual e blindado via GPG.
*   ⏳ **Sessão Inteligente**: Timer de 5 minutos estilo `sudo` (digite a senha uma vez e use livremente).
*   🛡️ **Bloqueio Automático**: Proteção contra força bruta (bloqueio de 5 min após 3 falhas).
*   ⚡ **Performance com Cache**: Buscas e listagens instantâneas sem decifrar arquivos.
*   📝 **Integração com $EDITOR**: Suporte nativo ao seu editor favorito (Vim, Nano, VS Code, etc).
*   📦 **Exportação Flexível**: Backup completo em texto claro com metadados organizados.

---

## 🛠️ Instalação Rápida

1.  **Pré-requisitos**: Certifique-se de ter o `python3` e o `gpg` instalados no seu Linux.
2.  **Instalar**:
    ```bash
    git clone https://github.com/marcelositr/notae.git
    cd notae
    pip install -e . --break-system-packages
    ```
3.  **Configurar**: Adicione `export EDITOR=seu_editor` ao seu shell se ainda não o tiver.

---

## 📟 Exemplos de Uso

```bash
# Criar uma nota rápida
notae new -t "Minha Ideia" -n "Conteúdo secreto da nota" -c "pessoal" -g "tag1,tag2"

# Ler uma nota existente (ID = timestamp)
notae read 20260331143000

# Listar notas de Março/2026 ordenadas por título
notae list --filter 2026-03 --sort title

# Pesquisa rápida em títulos, tags e categorias
notae search "trabalho"
```

---

## 📚 Documentação Completa (Wiki)

Para guias detalhados, regras de segurança e resoluções de problemas, acesse nossa **Wiki**:

*   🏠 [**Página Inicial**](wiki/Home.md) - Visão geral do projeto.
*   ⚙️ [**Instalação Detalhada**](wiki/Instalacao.md) - Guia passo a passo e requisitos.
*   ⌨️ [**Guia de Comandos**](wiki/Comandos.md) - Todos os comandos explicados com exemplos.
*   🔐 [**Segurança e Logs**](wiki/Seguranca.md) - Como protegemos seus dados.
*   ❓ [**FAQ**](wiki/FAQ.md) - Perguntas frequentes e dicas extras.

---

## 📜 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---
*Feito com foco em privacidade e simplicidade no terminal.*
