### Codex noticed this:
read_application_note recursively scans every markdown file and reads each file body until it finds a matching key, which makes a single lookup O(total application files × file size). As the vault grows, this will noticeably degrade response time for each lookup; storing or deriving a direct path/index by application_key would avoid repeated full-directory rescans.

### After a talk with codex it here is a summary
We concluded that the keys are meant to be stable identifiers, not just filenames.

`company_key` is currently useful because company notes are effectively resolved by key through the tracker: the service looks up the tracker entry, gets `company_note_path`, and reads that file directly. That is already close to O(1) lookup.

`application_key` is conceptually the same kind of stable ID, but the current implementation does not give it the same benefit yet. Application reads still scan all application markdown files and search file contents for the matching key, so that path is O(n).

Your main point was that if the system knows the company or maintains direct links to notes, it should resolve the markdown file directly rather than scanning. That is correct. A helper that resolves note paths from structured metadata would be cleaner and faster.

The likely better design is to unify both company and application lookup behind the same pattern:

- keep stable keys
- maintain a reliable `key -> note path` mapping
- resolve the file path first, then read the file directly

For companies, the repo already has most of that via the tracker. For applications, it would need an equivalent index or stored link/path before the same approach can be applied cleanly.


### Goal

Propose a fix and implement the change to the mcp code base, then fix the tests
