# 📁 Low-Level Design: In-Memory File System (Trie / Composite)

A classic object-oriented design and machine coding problem frequently asked at Google, Uber, and Microsoft (similar to LeetCode 588).

---

## 1. Requirements & Core API

* Support standard POSIX-like in-memory hierarchical directory and file manipulation:
  1. `ls(path: str) -> list[str]`:
     - If path is a directory, returns the list of directory and file names sorted lexicographically.
     - If path is a file, returns a list containing only that file's name.
  2. `mkdir(path: str) -> None`:
     - Recursively creates all intermediate directories in the path if they do not exist.
  3. `add_content_to_file(path: str, content: str) -> None`:
     - If file does not exist, creates it and appends `content`.
     - If file already exists, appends `content` to existing content.
  4. `read_content_from_file(path: str) -> str`:
     - Returns the full string content of the target file.

---

## 2. Trie / Composite Architecture

Every path is tokenized into path components (e.g. `"/a/b/c"` $\rightarrow$ `["a", "b", "c"]`). The file system behaves like a Trie where each node is either a `Directory` or a `File`.

```mermaid
flowchart TD
    Root["/ (Root Directory)"]
    Root --> Users["users/"]
    Root --> Etc["etc/"]
    Users --> Alice["alice/"]
    Alice --> Notes["notes.txt (File)"]
    Etc --> Config["config.yaml (File)"]
```

---

## 3. Python Implementation

```python
class FSNode:
    def __init__(self, name: str, is_dir: bool = True):
        self.name = name
        self.is_dir = is_dir
        # Only populated if is_dir is True
        self.children: dict[str, "FSNode"] = {}
        # Only populated if is_dir is False
        self.content: str = ""

class FileSystem:
    def __init__(self):
        self.root = FSNode("", is_dir=True)

    def _split_path(self, path: str) -> list[str]:
        # Filter out empty strings from "/a/b/c" -> ["a", "b", "c"]
        return [part for part in path.split("/") if part]

    def _traverse_to_parent(self, parts: list[str]) -> FSNode:
        curr = self.root
        for part in parts[:-1]:
            if part not in curr.children:
                curr.children[part] = FSNode(part, is_dir=True)
            curr = curr.children[part]
        return curr

    def ls(self, path: str) -> list[str]:
        parts = self._split_path(path)
        curr = self.root
        for part in parts:
            if part not in curr.children:
                return []
            curr = curr.children[part]

        # If it's a file, return its name only
        if not curr.is_dir:
            return [curr.name]
        
        # If it's a directory, return all children sorted
        return sorted(curr.children.keys())

    def mkdir(self, path: str) -> None:
        parts = self._split_path(path)
        curr = self.root
        for part in parts:
            if part not in curr.children:
                curr.children[part] = FSNode(part, is_dir=True)
            curr = curr.children[part]

    def add_content_to_file(self, file_path: str, content: str) -> None:
        parts = self._split_path(file_path)
        if not parts:
            return
        
        parent = self._traverse_to_parent(parts)
        filename = parts[-1]

        if filename not in parent.children:
            parent.children[filename] = FSNode(filename, is_dir=False)
        
        parent.children[filename].content += content

    def read_content_from_file(self, file_path: str) -> str:
        parts = self._split_path(file_path)
        curr = self.root
        for part in parts:
            if part not in curr.children:
                raise FileNotFoundError(f"Path '{file_path}' does not exist")
            curr = curr.children[part]

        if curr.is_dir:
            raise IsADirectoryError(f"Path '{file_path}' is a directory, not a file")
        
        return curr.content

# --- Verification ---
if __name__ == "__main__":
    fs = FileSystem()
    print("ls /:", fs.ls("/"))  # []
    fs.mkdir("/a/b/c")
    fs.add_content_to_file("/a/b/c/d.txt", "hello")
    print("ls /a/b/c:", fs.ls("/a/b/c"))  # ['d.txt']
    print("read /a/b/c/d.txt:", fs.read_content_from_file("/a/b/c/d.txt"))  # 'hello'
    fs.add_content_to_file("/a/b/c/d.txt", " world")
    print("read after append:", fs.read_content_from_file("/a/b/c/d.txt"))  # 'hello world'
```
