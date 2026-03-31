import sys
import os
import argparse
import tempfile
import subprocess
import json
from datetime import datetime
from notae.core.constants import NOTES_DIR, LOGS_DIR, SESSION_TIMEOUT, NOTE_EXTENSION
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
    cache = {}
    if os.path.exists(METADATA_CACHE):
        try:
            with open(METADATA_CACHE, 'r') as f:
                cache = json.load(f)
        except:
            cache = {}
    
    cache[filename] = {
        'title': note_obj.title,
        'category': note_obj.category,
        'tags': note_obj.tags,
        'timestamp': note_obj.timestamp
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
    if not passphrase:
        return

    title = args.title
    content = args.content
    category = args.category
    tags = [t.strip() for t in args.tags.split(',')] if args.tags else []

    if not title or not content:
        initial = ""
        if title: initial += f"Title: {title}\n"
        if category: initial += f"Category: {category}\n"
        if tags: initial += f"Tags: {', '.join(tags)}\n"
        initial += "\n"
        if content: initial += content
        
        edited = open_editor(initial)
        if not edited.strip():
            print("Aborted.")
            return
        
        try:
            note = Note.from_text(edited)
        except:
            print("Error parsing note from editor.")
            return
    else:
        note = Note(title, content, category, tags)

    if not note.title:
        print("Error: Title is required.")
        return

    encrypted = encrypt_data(note.to_text(), passphrase)
    
    with open(note.full_path, 'wb') as f:
        f.write(encrypted)
    
    update_metadata_cache(note.filename, note)
    save_session(passphrase)
    reset_failures()
    print(f"Note saved: {note.filename}")
def cmd_read(args):
    setup_directories()
    target = args.id
    found_file = None
    for f in os.listdir(NOTES_DIR):
        if f.startswith(target) and f.endswith(NOTE_EXTENSION):
            found_file = os.path.join(NOTES_DIR, f)
            break
    
    if not found_file:
        print(f"Note not found: {target}")
        return

    for i in range(3):
        passphrase = authenticate()
        if not passphrase: return
        try:
            with open(found_file, 'rb') as f:
                encrypted = f.read()
            decrypted = decrypt_data(encrypted, passphrase)
            print(decrypted)
            save_session(passphrase)
            reset_failures()
            update_metadata_cache(os.path.basename(found_file), Note.from_text(decrypted))
            return
        except Exception as e:
            clear_session()
            record_failure()
            print(f"Decryption failed (Attempt {i+1}/3).")
    print("Locked if 3 consecutive failures reached.")


def cmd_list(args):
    notes = list_notes()
    if args.filter:
        notes = [n for n in notes if n['timestamp'].startswith(args.filter.replace('-', ''))]
    
    reverse = (args.order == 'desc')
    if args.sort == 'title':
        notes.sort(key=lambda x: x['sanitized_title'], reverse=reverse)
    else:
        notes.sort(key=lambda x: x['timestamp'], reverse=reverse)
    
    for n in notes:
        print(f"{n['timestamp']} - {n['sanitized_title']}")

def cmd_delete(args):
    setup_directories()
    target = args.id
    found_file = None
    for f in os.listdir(NOTES_DIR):
        if f.startswith(target) and f.endswith(NOTE_EXTENSION):
            found_file = os.path.join(NOTES_DIR, f)
            fname = f
            break
    
    if not found_file:
        print(f"Note not found: {target}")
        return

    confirm = input(f"Are you sure you want to delete '{target}'? (y/N): ")
    if confirm.lower() == 'y':
        os.remove(found_file)
        # Remove from cache
        cache = get_metadata_cache()
        if fname in cache:
            del cache[fname]
            with open(METADATA_CACHE, 'w') as f:
                json.dump(cache, f)
        print("Deleted.")
    else:
        print("Aborted.")

def cmd_edit(args):
    setup_directories()
    target = args.id
    found_file = None
    for f in os.listdir(NOTES_DIR):
        if f.startswith(target) and f.endswith(NOTE_EXTENSION):
            found_file = os.path.join(NOTES_DIR, f)
            old_filename = f
            break
    
    if not found_file:
        print(f"Note not found: {target}")
        return

    for i in range(3):
        passphrase = authenticate()
        if not passphrase: return
        try:
            with open(found_file, 'rb') as f:
                encrypted = f.read()
            decrypted = decrypt_data(encrypted, passphrase)
            edited = open_editor(decrypted)
            if not edited.strip() or edited == decrypted:
                print("No changes or aborted.")
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
            print(f"Note updated: {note.filename}")
            return
        except Exception as e:
            clear_session()
            record_failure()
            print(f"Error/Decryption failed (Attempt {i+1}/3).")
    print("Locked if 3 consecutive failures reached.")

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
                    all_content.append("\n" + "="*40 + "\n")
            
            with open(args.dest, 'w') as f:
                f.write("\n".join(all_content))
            
            save_session(passphrase)
            reset_failures()
            print(f"Exported all notes to {args.dest}")
            return
        except Exception as e:
            clear_session()
            record_failure()
            print(f"Export failed/Decryption failed (Attempt {i+1}/3).")
    print("Locked if 3 consecutive failures reached.")

def cmd_stats(args):
    cache = get_metadata_cache()
    total = len(cache)
    categories = {}
    tags_count = {}
    dates = []
    
    for f, meta in cache.items():
        cat = meta.get('category') or "None"
        categories[cat] = categories.get(cat, 0) + 1
        for t in meta.get('tags', []):
            tags_count[t] = tags_count.get(t, 0) + 1
        dates.append(meta.get('timestamp'))
    
    dates.sort(reverse=True)
    
    print(f"Total notes: {total}")
    print("\nCategories:")
    for cat, count in categories.items():
        print(f"  - {cat}: {count}")
    print("\nTop Tags:")
    for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {tag}: {count}")
    print("\nLatest dates:")
    for d in dates[:5]:
        print(f"  - {d}")

def cmd_tag(args):
    cache = get_metadata_cache()
    target_tag = args.tag
    found = []
    for f, meta in cache.items():
        if target_tag in meta.get('tags', []):
            found.append(f"{meta['timestamp']} - {meta['title']}")
    
    if found:
        for item in sorted(found):
            print(item)
    else:
        print(f"No notes with tag: {target_tag}")

def cmd_search(args):
    cache = get_metadata_cache()
    query = args.query.lower()
    found = []
    for f, meta in cache.items():
        in_title = query in meta.get('title', '').lower()
        in_cat = query in meta.get('category', '').lower()
        in_tags = any(query in t.lower() for t in meta.get('tags', []))
        
        if in_title or in_cat or in_tags:
            found.append(f"{meta['timestamp']} - {meta['title']}")
    
    if found:
        for item in sorted(found):
            print(item)
    else:
        print(f"No results for: {query}")

def main():
    parser = argparse.ArgumentParser(description="Notae - Encrypted CLI Notes")
    subparsers = parser.add_subparsers(dest='command')

    # New
    p_new = subparsers.add_parser('new')
    p_new.add_argument('-t', '--title')
    p_new.add_argument('-n', '--content')
    p_new.add_argument('-c', '--category')
    p_new.add_argument('-g', '--tags')

    # Read
    p_read = subparsers.add_parser('read')
    p_read.add_argument('id')

    # List
    p_list = subparsers.add_parser('list')
    p_list.add_argument('--sort', choices=['date', 'title'], default='date')
    p_list.add_argument('--order', choices=['asc', 'desc'], default='asc')
    p_list.add_argument('--filter')

    # Delete
    p_delete = subparsers.add_parser('delete')
    p_delete.add_argument('id')

    # Edit
    p_edit = subparsers.add_parser('edit')
    p_edit.add_argument('id')

    # Export
    p_export = subparsers.add_parser('export')
    p_export.add_argument('dest')

    # Stats
    p_stats = subparsers.add_parser('stats')

    # Tag
    p_tag = subparsers.add_parser('tag')
    p_tag.add_argument('tag')

    # Search
    p_search = subparsers.add_parser('search')
    p_search.add_argument('query')
    
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
    else: parser.print_help()

if __name__ == "__main__":
    main()
