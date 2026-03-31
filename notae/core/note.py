import os
import re
import unicodedata
from datetime import datetime
from notae.core.constants import DATE_FORMAT, NOTE_EXTENSION, NOTES_DIR, MAX_TAGS

def sanitize_filename(title):
    if not title: return ""
    # Remove acentos
    nfkd_form = unicodedata.normalize('NFKD', title)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    # Minúsculas e espaços -> _
    sanitized = only_ascii.lower().replace(' ', '_')
    # Remove caracteres especiais (mantém letras, números e _)
    sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)
    return re.sub(r'_+', '_', sanitized).strip('_')

class Note:
    def __init__(self, title, content, category=None, tags=None, timestamp=None):
        self.title = title
        self.content = content
        self.category = category or ""
        self.tags = tags or []
        # Timestamp bruto para o nome do arquivo
        self._raw_timestamp = timestamp or datetime.now().strftime(DATE_FORMAT)
    
    @property
    def filename(self):
        sanit_title = sanitize_filename(self.title)
        return f"{self._raw_timestamp}-{sanit_title}{NOTE_EXTENSION}"
    
    @property
    def full_path(self):
        return os.path.join(NOTES_DIR, self.filename)

    def to_text(self):
        # Formato humano dentro da nota: 31/03/2026 14:33:47
        try:
            dt = datetime.strptime(self._raw_timestamp, DATE_FORMAT)
            human_ts = dt.strftime("%d/%m/%Y %H:%M:%S")
        except:
            human_ts = self._raw_timestamp

        tags_str = ", ".join(self.tags[:MAX_TAGS])
        lines = [
            "============================================================",
            f"Title: {self.title}",
            f"Category: {self.category}",
            f"Tags: {tags_str}",
            f"Timestamp: {human_ts}",
            "",
            self.content,
            "============================================================"
        ]
        return "\n".join(lines)

    @classmethod
    def from_text(cls, text):
        lines = text.splitlines()
        # Remove as bordas ==== se existirem
        if lines and lines[0].startswith("==="): lines = lines[1:]
        if lines and lines[-1].startswith("==="): lines = lines[:-1]

        title = ""
        category = ""
        tags = []
        timestamp_human = ""
        content_start = 0
        
        for i, line in enumerate(lines):
            if line.startswith("Title: "):
                title = line[7:].strip()
            elif line.startswith("Category: "):
                category = line[10:].strip()
            elif line.startswith("Tags: "):
                tag_str = line[6:].strip()
                tags = [t.strip() for t in tag_str.split(",") if t.strip()]
            elif line.startswith("Timestamp: "):
                timestamp_human = line[11:].strip()
            elif line == "":
                content_start = i + 1
                break
        
        content = "\n".join(lines[content_start:])
        
        # Converte timestamp humano de volta para bruto se possível
        raw_ts = None
        if timestamp_human:
            try:
                dt = datetime.strptime(timestamp_human, "%d/%m/%Y %H:%M:%S")
                raw_ts = dt.strftime(DATE_FORMAT)
            except:
                pass
                
        return cls(title, content, category, tags, raw_ts)

def list_notes():
    notes = []
    if not os.path.exists(NOTES_DIR):
        return notes
        
    for f in os.listdir(NOTES_DIR):
        if f.endswith(NOTE_EXTENSION):
            # Formato: 20260331143347-titulo_sanitizado.note
            match = re.match(r'^(\d{14})-(.*)\.note$', f)
            if match:
                notes.append({
                    'filename': f,
                    'timestamp': match.group(1),
                    'sanitized_title': match.group(2)
                })
    return notes
