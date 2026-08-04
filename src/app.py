import json
import pathlib
import tkinter as tk
from typing import Any


class App(tk.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title("tcpad")
        self.minsize(800, 600)
        self.geometry("800x600")

        self.left = tk.Frame(self, bg="#dedede", width=260)
        self.left.pack_propagate(False)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = tk.Frame(self, bg="#eaeaea")
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.config = Config()
        self.controller = Controller(self)

        self.ui()

    def ui(self) -> None:
        pass


class Config:
    def __init__(self) -> None:
        self.file = pathlib.Path("config.json")
        self.obj: dict[str, Any] = self.load()

    def load(self) -> dict[str, Any]:
        if not self.file.exists():
            self.file.write_text("{}")
            return {}

        content = self.file.read_text()
        return json.loads(content)

    def get(self, name: str) -> Any | None:
        return self.obj.get(name)

    def set(self, name: str, value: Any) -> None:
        self.obj[name] = value

        content = json.dumps(self.obj, ensure_ascii=False)
        self.file.write_text(content)


class Controller:
    def __init__(self, app: App) -> None:
        self.app = app


if __name__ == "__main__":
    app = App()
    app.mainloop()
