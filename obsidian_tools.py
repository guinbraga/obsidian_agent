from langchain_core.tools import tool
from pathlib import Path

VAULT_DIR = Path("./vault")


@tool
def read_obsidian_note(note_name: str) -> str:
    """
    Reads the content of a local Obsidian note by its name.
    Do not inlcude the .md extension in the note_name.
    """

    # Clean note name in case the LLM passes brackets or extensions:
    clean_name = note_name.replace("[[", "").replace("]]", "").replace(".md", "")
    file_path = VAULT_DIR / f"{clean_name}.md"

    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    else:
        return f"Error: Note '{clean_name}' not found in the vault."


@tool
def append_obsidian_note(note_name: str, content: str) -> str:
    """
    Appends content to a local Obsidian note by its name.
    If the note does not exist, it will be created.
    Do not include the .md extension in the note_name.
    To link to another note, use standard Obsidian wiki-link syntax in the content (e.g., [[Note Name]] or [[Note Name|Alias]]).
    """

    clean_name = note_name.replace("[[", "").replace("]]", "").replace(".md", "")
    file_path = VAULT_DIR / f"{clean_name}.md"

    with file_path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n{content}")

    return f"Successfully appended content to '{clean_name}'."


if __name__ == "__main__":
    # Ensure vault exists
    VAULT_DIR.mkdir(exist_ok=True)

    # Test reading a note
    print("Testing read tool:")
    print(read_obsidian_note.invoke("Agents"))

    # Test error handling
    print("\nTesting missing note:")
    print(read_obsidian_note.invoke("NonExistentNote"))
