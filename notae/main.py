import sys
import os
import argparse
import tempfile
import subprocess
import json
from datetime import datetime
from notae.core.constants import NOTES_DIR, LOGS_DIR, SESSION_TIMEOUT, NOTE_EXTENSION, AUTH_LOG, ERRORS_LOG, DATE_FORMAT
from notae.core.utils import setup_directories, setup_logging_lazy, get_now, log_error, log_auth
from notae.core.encryption import encrypt_data, decrypt_data
from notae.core.session import authenticate, save_session, get_session, reset_failures, record_failure, clear_session
from notae.core.note import Note, list_notes

METADATA_CACHE = os.path.join(LOGS_DIR, ".metadata.cache")

def get_editor():
    return os.environ.get('EDITOR', 'vim')

def open_editor(initial_content=""):
    with tempfile.NamedTemporaryFile(suffix=".tmp", mode='w+', delete=False) as tf:
        tf.write(initial_content)
        temp_path = tf.name
    
    try:
        subprocess.call([get_editor(), temp_path])
        with open(temp_path, 'r') as tf:
            return tf.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def update_metadata_cache(filename, note_obj):
    cache = get_metadata_cache()
    cache[filename] = {
        'title': note_obj.title,
        'category': note_obj.category,
        'tags': note_obj.tags,
        'timestamp': note_obj._raw_timestamp
    }
    with open(METADATA_CACHE, 'w') as f:
        json.dump(cache, f)

def get_metadata_cache():
    if not os.path.exists(METADATA_CACHE):
        return {}
    try:
        with open(METADATA_CACHE, 'r') as f:
            return json.load(f)
    except:
        return {}

def cmd_new(args):
    setup_directories()
    passphrase = authenticate()
    if not passphrase: return

    title = args.title
    content = args.content
    category = args.category
    tags = [t.strip() for t in args.tags.split(',')] if args.tags else []

    # Se faltar título ou conteúdo, abre editor com modelo
    if not title or not content:
        now_raw = datetime.now().strftime(DATE_FORMAT)
        human_ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        initial = "============================================================\n"
        initial += f"Title: {title or ''}\n"
        initial += f"Category: {category or ''}\n"
        initial += f"Tags: {', '.join(tags) if tags else ''}\n"
        initial += f"Timestamp: {human_ts}\n"
        initial += "\n"
        initial += content or "conteúdo da nota"
        initial += "\n============================================================"
        
        edited = open_editor(initial)
        # Parse edited content
        try:
            note = Note.from_text(edited)
            # Re-check mandatory fields from editor
            if not note.title:
                print("\x1b[31mErro: O título é obrigatório dentro do editor.\x1b[0m")
                return
            if not note.content or note.content.strip() == "conteúdo da nota":
                 print("\x1b[31mErro: O conteúdo da nota é obrigatório.\x1b[0m")
                 return
        except Exception as e:
            print(f"\x1b[31mErro ao processar dados do editor: {e}\x1b[0m")
            return
    else:
        note = Note(title, content, category, tags)

    try:
        encrypted = encrypt_data(note.to_text(), passphrase)
        with open(note.full_path, 'wb') as f:
            f.write(encrypted)
        
        update_metadata_cache(note.filename, note)
        save_session(passphrase)
        reset_failures()
        print(f"\x1b[32m[OK] Nota salva: {note.filename}\x1b[0m")
    except Exception as e:
        log_error(f"Erro no salvamento: {e}")
        print(f"\x1b[31mErro fatal ao salvar nota. Logs em {ERRORS_LOG}\x1b[0m")

def cmd_read(args):
    setup_directories()
    target = args.id
    found_file = None
    for f in os.listdir(NOTES_DIR):
        if f.startswith(target) and f.endswith(NOTE_EXTENSION):
            found_file = os.path.join(NOTES_DIR, f)
            break
    
    if not found_file:
        print(f"\x1b[31mErro: Nota '{target}' não encontrada.\x1b[0m")
        return

    for i in range(3):
        passphrase = authenticate()
        if not passphrase: return
        try:
            with open(found_file, 'rb') as f:
                encrypted = f.read()
            decrypted = decrypt_data(encrypted, passphrase)
            print("\n" + decrypted + "\n") # to_text() already includes boundaries
            save_session(passphrase)
            reset_failures()
            update_metadata_cache(os.path.basename(found_file), Note.from_text(decrypted))
            return
        except Exception as e:
            clear_session()
            record_failure()
            print(f"\x1b[33mSenha Inválida! Tentativa {i+1} de 3.\x1b[0m")
    print("\x1b[31mBloqueio: Muitas tentativas falhas. Aguarde 5 minutos.\x1b[0m")

def cmd_list(args):
    notes = list_notes()
    if not notes:
        print("\x1b[33mInfo: Nenhuma nota encontrada no diretório ~/notes/\x1b[0m")
        return

    if args.filter:
        f_val = args.filter.replace('-', '')
        notes = [n for n in notes if n['timestamp'].startswith(f_val)]
    
    reverse = (args.order == 'desc')
    if args.sort == 'title':
        notes.sort(key=lambda x: x['sanitized_title'].lower(), reverse=reverse)
    else:
        notes.sort(key=lambda x: x['timestamp'], reverse=reverse)
    
    print(f"\n\x1b[1m{'ID (TIMESTAMP)':<18} | {'TÍTULO (SANITIZADO)'}\x1b[0m")
    print("-" * 60)
    for n in notes:
        print(f"{n['timestamp']:<18} | {n['sanitized_title']}")
    print("-" * 60 + f"\nTotal: {len(notes)} notas\n")

def cmd_delete(args):
    setup_directories()
    target = args.id
    found_file = None
    fname = None
    for f in os.listdir(NOTES_DIR):
        if f.startswith(target) and f.endswith(NOTE_EXTENSION):
            found_file = os.path.join(NOTES_DIR, f)
            fname = f
            break
    
    if not found_file:
        print(f"\x1b[31mErro: ID '{target}' não corresponde a nenhuma nota.\x1b[0m")
        return

    confirm = input(f"\x1b[33mAVISO: Deseja apagar '{fname}' permanentemente? (y/N): \x1b[0m")
    if confirm.lower() == 'y':
        try:
            os.remove(found_file)
            cache = get_metadata_cache()
            if fname in cache:
                del cache[fname]
                with open(METADATA_CACHE, 'w') as f:
                    json.dump(cache, f)
            print("\x1b[32m[OK] Nota excluída com sucesso.\x1b[0m")
        except Exception as e:
            print(f"\x1b[31mErro: Falha ao deletar arquivo: {e}\x1b[0m")
    else:
        print("Operação cancelada.")

def cmd_edit(args):
    setup_directories()
    target = args.id
    found_file = None
    old_filename = None
    for f in os.listdir(NOTES_DIR):
        if f.startswith(target) and f.endswith(NOTE_EXTENSION):
            found_file = os.path.join(NOTES_DIR, f)
            old_filename = f
            break
    
    if not found_file:
        print(f"\x1b[31mErro: Nota '{target}' não encontrada para edição.\x1b[0m")
        return

    for i in range(3):
        passphrase = authenticate()
        if not passphrase: return
        try:
            with open(found_file, 'rb') as f:
                encrypted = f.read()
            decrypted = decrypt_data(encrypted, passphrase)
            
            edited = open_editor(decrypted)
            if not edited.strip():
                print("\x1b[33mEdição abortada pelo usuário.\x1b[0m")
                return
            
            if edited == decrypted:
                print("Nenhuma alteração detectada. O arquivo não foi reescrito.")
                return
            
            note = Note.from_text(edited)
            new_encrypted = encrypt_data(note.to_text(), passphrase)
            new_path = note.full_path
            
            if new_path != found_file:
                os.remove(found_file)
                cache = get_metadata_cache()
                if old_filename in cache: del cache[old_filename]
                with open(METADATA_CACHE, 'w') as f: json.dump(cache, f)
            
            with open(new_path, 'wb') as f:
                f.write(new_encrypted)
            
            update_metadata_cache(note.filename, note)
            save_session(passphrase)
            reset_failures()
            print(f"\x1b[32m[OK] Nota editada e recriptografada: {note.filename}\x1b[0m")
            return
        except Exception as e:
            clear_session()
            record_failure()
            print(f"\x1b[33mSenha Incorreta! Tentativa {i+1} de 3.\x1b[0m")
    print("\x1b[31mBloqueio de segurança ativado.\x1b[0m")

def cmd_export(args):
    setup_directories()
    for i in range(3):
        passphrase = authenticate()
        if not passphrase: return
        try:
            notes_files = [f for f in os.listdir(NOTES_DIR) if f.endswith(NOTE_EXTENSION)]
            notes_files.sort()
            all_content = []
            for f in notes_files:
                with open(os.path.join(NOTES_DIR, f), 'rb') as nf:
                    decrypted = decrypt_data(nf.read(), passphrase)
                    all_content.append(decrypted)
                    all_content.append("\n")
            
            with open(args.dest, 'w') as f:
                f.write("\n".join(all_content))
            
            save_session(passphrase)
            reset_failures()
            print(f"\x1b[32m[OK] Exportação (Merge + Metadados) salva em: {args.dest}\x1b[0m")
            return
        except Exception as e:
            clear_session()
            record_failure()
            print(f"\x1b[33mFalha na exportação: Senha inválida (Tentativa {i+1}/3)\x1b[0m")
    print("\x1b[31mErro: Não foi possível exportar os dados.\x1b[0m")

def cmd_stats(args):
    cache = get_metadata_cache()
    if not cache:
        print("\x1b[33mDica: Use 'notae list' ou crie uma nota para gerar dados estatísticos.\x1b[0m")
        return
        
    total = len(cache)
    categories = {}
    tags_count = {}
    dates = []
    
    for f, meta in cache.items():
        cat = meta.get('category') or "Sem Categoria"
        categories[cat] = categories.get(cat, 0) + 1
        for t in meta.get('tags', []):
            tags_count[t] = tags_count.get(t, 0) + 1
        dates.append(meta.get('timestamp'))
    
    dates.sort(reverse=True)
    
    print("\n\x1b[1m=== NOTAE ESTATÍSTICAS ===\x1b[0m")
    print(f"Total de Notas: {total}")
    print("\n\x1b[4mDistribuição por Categoria\x1b[0m")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:<20}: {count} notas")
    
    print("\n\x1b[4mTags mais Frequentes\x1b[0m")
    for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  #{tag:<19}: {count} vezes")
    
    print("\n\x1b[4mHistórico Recente\x1b[0m")
    for d in dates[:3]:
        print(f"  Última atividade em: {d}")
    print("\nLogs em ~/.notae_logs/\n")

def cmd_tag(args):
    cache = get_metadata_cache()
    target_tag = args.tag
    found = []
    for f, meta in cache.items():
        if target_tag in meta.get('tags', []):
            found.append(f"{meta['timestamp']} | {meta['title']}")
    
    if found:
        print(f"\nNotas com a tag \x1b[1m#{target_tag}\x1b[0m:")
        for item in sorted(found):
            print(f"  - {item}")
        print()
    else:
        print(f"\x1b[33mInfo: Nenhuma nota marcada com a tag '#{target_tag}'.\x1b[0m")

def cmd_search(args):
    cache = get_metadata_cache()
    query = args.query.lower()
    found = []
    for f, meta in cache.items():
        in_title = query in meta.get('title', '').lower()
        in_cat = query in meta.get('category', '').lower()
        in_tags = any(query in t.lower() for t in meta.get('tags', []))
        
        if in_title or in_cat or in_tags:
            found.append(f"{meta['timestamp']} | {meta['title']}")
    
    if found:
        print(f"\nBusca por '\x1b[1m{query}\x1b[0m': {len(found)} resultado(s)")
        for item in sorted(found):
            print(f"  -> {item}")
        print()
    else:
        print(f"\x1b[33mNenhum resultado para o termo '{query}'.\x1b[0m")

def show_main_help():
    help_text = """NOTAE - Sistema de Notas Criptografadas AES-256
Segurança total para seus registros pessoais no Linux

USO GERAL:
  notae <comando> [opções] [argumentos]

COMANDOS:

  new       Cria uma nova nota
            -t, --title "Título"       Define o título
            -n, --content "Conteúdo"   Define o conteúdo
            -c, --category "Categoria" Categoria única (opcional)
            -g, --tags "tag1,tag2,tag3" Até 3 tags separadas por vírgula (opcional)
            Exemplo: notae new -t "Reuniao" -n "Discutir projeto X" -c "trabalho" -g "urgente,py"
            Se passar título e conteúdo, salva direto. Senão abre editor.

  read      Lê uma nota existente
            Uso: notae read <id_da_nota>
            Exemplo: notae read 20260331-121000-minha_nota

  edit      Edita uma nota existente no editor definido ($EDITOR)
            Uso: notae edit <id_da_nota>

  delete    Remove uma nota permanentemente
            Uso: notae delete <id_da_nota>
            Pede confirmação antes de apagar

  list      Lista notas cadastradas
            --sort [date|title]   Ordena por data ou título (default: date)
            --order [asc|desc]    Ordem crescente ou decrescente
            --filter "YYYY-MM"    Filtra notas por mês
            Exemplo: notae list --sort title --order desc --filter 2026-03

  search    Pesquisa por termo em título, categoria e tags
            Uso: notae search <termo>
            Exemplo: notae search "trabalho"

  tag       Lista notas por tag
            Uso: notae tag <nome_da_tag>
            Exemplo: notae tag "estudo"

  export    Exporta todas as notas decifradas em um arquivo
            Uso: notae export <arquivo_destino>
            Exemplo: notae export backup_diario.txt

  stats     Mostra estatísticas do diário
            Uso: notae stats

OPÇÕES GLOBAIS:
  -h, --help   Mostra esta ajuda

DICAS:
  * ID da nota: <timestamp>-<titulo_sanitizado>
  * Todos os arquivos .note são criptografados AES-256
  * Título minúsculo, sem acentos ou caracteres especiais"""
    print(help_text)

def main():
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        show_main_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(prog='notae', add_help=False)
    subparsers = parser.add_subparsers(dest='command')

    # --- NEW ---
    p_new = subparsers.add_parser('new', add_help=True)
    p_new.add_argument('-t', '--title', metavar='TITULO')
    p_new.add_argument('-n', '--content', metavar='TEXTO')
    p_new.add_argument('-c', '--category', metavar='CAT')
    p_new.add_argument('-g', '--tags', metavar='T1,T2')

    # --- READ ---
    p_read = subparsers.add_parser('read', add_help=True)
    p_read.add_argument('id', metavar='ID')

    # --- LIST ---
    p_list = subparsers.add_parser('list', add_help=True)
    p_list.add_argument('--sort', choices=['date', 'title'], default='date')
    p_list.add_argument('--order', choices=['asc', 'desc'], default='asc')
    p_list.add_argument('--filter', metavar='YYYY-MM')

    # --- DELETE ---
    p_delete = subparsers.add_parser('delete', add_help=True)
    p_delete.add_argument('id', metavar='ID')

    # --- EDIT ---
    p_edit = subparsers.add_parser('edit', add_help=True)
    p_edit.add_argument('id', metavar='ID')

    # --- EXPORT ---
    p_export = subparsers.add_parser('export', add_help=True)
    p_export.add_argument('dest', metavar='ARQUIVO')

    # --- STATS ---
    subparsers.add_parser('stats', add_help=True)

    # --- TAG ---
    p_tag = subparsers.add_parser('tag', add_help=True)
    p_tag.add_argument('tag', metavar='TAG')

    # --- SEARCH ---
    p_search = subparsers.add_parser('search', add_help=True)
    p_search.add_argument('query', metavar='TERMO')
    
    args = parser.parse_args()
    
    if args.command == 'new': cmd_new(args)
    elif args.command == 'read': cmd_read(args)
    elif args.command == 'list': cmd_list(args)
    elif args.command == 'delete': cmd_delete(args)
    elif args.command == 'edit': cmd_edit(args)
    elif args.command == 'export': cmd_export(args)
    elif args.command == 'stats': cmd_stats(args)
    elif args.command == 'tag': cmd_tag(args)
    elif args.command == 'search': cmd_search(args)

if __name__ == "__main__":
    main()
