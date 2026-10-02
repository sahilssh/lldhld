import unittest

class FSNode:
    def __init__(self, name: str, is_dir: bool = True):
        self.name = name
        self.is_dir = is_dir
        self.children: dict[str, "FSNode"] = {}
        self.content: str = ""

class FileSystem:
    def __init__(self):
        self.root = FSNode("", is_dir=True)

    def _split_path(self, path: str) -> list[str]:
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

        if not curr.is_dir:
            return [curr.name]
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
            curr = curr.children[part]
        return curr.content

class TestFileSystem(unittest.TestCase):
    def test_file_system_operations(self):
        fs = FileSystem()
        self.assertEqual(fs.ls("/"), [])
        fs.mkdir("/a/b/c")
        self.assertEqual(fs.ls("/a/b"), ["c"])
        fs.add_content_to_file("/a/b/c/doc.txt", "hello")
        self.assertEqual(fs.read_content_from_file("/a/b/c/doc.txt"), "hello")
        fs.add_content_to_file("/a/b/c/doc.txt", " world")
        self.assertEqual(fs.read_content_from_file("/a/b/c/doc.txt"), "hello world")
        self.assertEqual(fs.ls("/a/b/c"), ["doc.txt"])
        self.assertEqual(fs.ls("/a/b/c/doc.txt"), ["doc.txt"])

if __name__ == "__main__":
    unittest.main()
