from __future__ import annotations

import json
import pathlib
import tkinter as tk
from tkinter import ttk
from typing import Any


class App(tk.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title("TCPad: TCP 客户端 & 服务器")
        self.minsize(800, 600)
        self.geometry("800x600")

        left = tk.Frame(self, width=260)
        left.pack_propagate(False)
        left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = tk.Frame(self)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(left)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.client_tab = tk.Frame(notebook)
        notebook.add(self.client_tab, text="客户端")

        self.server_tab = tk.Frame(notebook)
        notebook.add(self.server_tab, text="服务器")

        self.config = Config()
        self.controller = Controller(self)

        self.ui()

    def ui(self) -> None:
        textarea = tk.Text(self.right, font=("monospace", 11))
        textarea.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def on_input(event: tk.Event[tk.Text]) -> object:
            if event.keysym == "Return":
                self.controller.submit()
                return "break"

            elif event.char and event.char.isprintable():
                old = self.controller.input.get()
                self.controller.input.set(old + event.char)

        def on_message(data: str) -> None:
            textarea.insert(tk.END, "\n" + data + "\n")

        textarea.bind("<Key>", on_input)
        self.controller.on_message = on_message


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
        self.input = tk.StringVar(value="")

    def submit(self) -> None:
        self.on_message(self.input.get())
        self.input.set("")

    def on_message(self, data: str) -> None:
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
