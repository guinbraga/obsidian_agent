from pydantic import BaseModel


class NoteMetadata(BaseModel):
    title: str
    tags: list[str] = []
    created: str


class VaultNote(BaseModel):
    metadata: NoteMetadata
    body: str
    word_count: int = 0
