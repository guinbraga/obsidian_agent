from note_models import NoteMetadata, VaultNote


def main():
    metadata_args = {
        "title": "sample_note",
        "tags": ["test", "code"],
        "created": "2026-07-20",
    }
    note_metadata = NoteMetadata(**metadata_args)
    valid_note = VaultNote(
        metadata=note_metadata, body="sample body for a note", word_count=0
    )

    print("valid note created!")

    print("attempting to create an invalid note:")
    try:
        invalid_metadata = NoteMetadata(
            title=None,
            tags=["test", "code"],
            created="2026-07-20",
        )
    except Exception as e:
        print(f"Unable to create note due to error {e}")

    print(f"Previous word count: {valid_note.word_count}")
    new_word_count = len(valid_note.body.split(" "))
    updated_note = valid_note.model_copy(update={"word_count": new_word_count})

    print(f"New word count: {updated_note.word_count}")


if __name__ == "__main__":
    main()
