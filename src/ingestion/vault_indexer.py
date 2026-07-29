from pathlib import Path
import os
import json

from src.ingestion import create_embeddings, load_embedder
from src.ingestion.chunker import MarkdownChunker
from src.ingestion.knowledge_base import KnowledgeBase


class VaultIndexer:
    def __init__(self, vault_dir: Path, state_file: Path = Path(".index_state.json")):
        self.vault_dir = vault_dir.resolve()
        self.state_file = (vault_dir / state_file).resolve()

    def _create_index_state_file(self):
        index_state = {}
        for abs_note_path in self.vault_dir.rglob("*.md"):
            note_file = str(abs_note_path.relative_to(self.vault_dir))
            mtime = os.path.getmtime(abs_note_path)
            index_state[note_file] = mtime
        with open(self.state_file, "w", encoding="utf-8") as index_state_file:
            json.dump(index_state, index_state_file)
        return index_state

    def _load_index_state_file(self):
        if self.state_file.is_file():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception as e:
                raise Exception(f"Failed to load index_state.json: {e}")
        else:
            return self._create_index_state_file()

    def index(self):
        index_state = self._load_index_state_file()
        md_chunker = MarkdownChunker()
        knowledge_base = KnowledgeBase()
        embedder = None
        for abs_note_path in self.vault_dir.rglob("*.md"):
            note_file = str(abs_note_path.relative_to(self.vault_dir))
            mtime = os.path.getmtime(abs_note_path)
            if index_state.get(note_file, -1) != mtime:
                if not embedder:
                    embedder = load_embedder()

                # Delete old chunks from this file
                # TODO: Create KnowledgeBase method that deletes and inserts in the same commit
                knowledge_base.delete_by_source(note_file, source_type="vault_note")

                with open(abs_note_path, "r", encoding="utf-8") as note:
                    metadata = {"source": note_file}
                    chunks = md_chunker.split(note.read(), metadata)
                    note_embed = create_embeddings(chunks, embedder=embedder)
                    knowledge_base.insert(chunks, note_embed, source_type="vault_note")

                # Update index_state
                index_state[note_file] = mtime

        indexed_files = set(index_state.keys())
        current_files = {
            str(f.relative_to(self.vault_dir)) for f in self.vault_dir.rglob("*.md")
        }
        removed = indexed_files - current_files

        for removed_file in removed:
            knowledge_base.delete_by_source(removed_file, source_type="vault_note")
            del index_state[removed_file]

        with open(self.state_file, "w", encoding="utf-8") as index_state_file:
            json.dump(index_state, index_state_file)


if __name__ == "__main__":
    vi = VaultIndexer(Path("../../Documents/Obsidian Vault"))
    vi.index()
