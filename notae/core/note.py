import os
import re
from datetime import datetime
from notae.core.constants import DATE_FORMAT, NOTE_EXTENSION, NOTES_DIR, MAX_TAGS
from notae.core.utils import sanitize_filename

class Note:
    def __init__(self, title, content, category=None, tags=None, timestamp=None):
        self.title = title
        self.content = content
        self.category = category or ""
        self.tags = tags or []
        self.timestamp = timestamp or datetime.now().strftime(DATE_FORMAT)
    
    @property
    def filename(self):
        sanitized = sanitize_filename(self.title)
        return f"{self.timestamp}-{sanitized}{NOTE_EXTENSION}"
    
    @property
    def full_path(self):
        return os.path.join(NOTES_DIR, self.filename)

    def to_text(self):
        tags_str = ", ".join(self.tags[:MAX_TAGS])
        lines = [
            f"Title: {self.title}",
            f"Category: {self.category}",
            f"Tags: {tags_str}",
            f"Timestamp: {self.timestamp}",
            "",
            self.content
        ]
        return "\n".join(lines)

    @classmethod
    def from_text(cls, text):
        lines = text.splitlines()
        title = ""
        category = ""
        tags = []
        timestamp = ""
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
                timestamp = line[11:].strip()
            elif line == "":
                content_start = i + 1
                break
        
        content = "\n".join(lines[content_start:])
        return cls(title, content, category, tags, timestamp)

def list_notes():
    notes = []
    if not os.path.exists(NOTES_DIR):
        return notes
        
    for f in os.listdir(NOTES_DIR):
        if f.endswith(NOTE_EXTENSION):
            # Try to extract timestamp and title from filename for fast listing
            match = re.match(r'^(\d{8}-\d{6})-(.*)\.note$', f)
            if match:
                notes.append({
                    'filename': f,
                    'timestamp': match.group(1),
                    'sanitized_title': match.group(2)
                })
    return notes
