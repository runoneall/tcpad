from __future__ import annotations

import json
import pathlib
import socket
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any


class App(tk.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title("TCPad: TCP 客户端 & 服务器")
        self.minsize(800, 600)
        self.geometry("800x600")

        self.attributes("-topmost", True)
        self.focus_force()
        self.after(100, lambda: self.attributes("-topmost", False))

        left = tk.Frame(self, width=260)
        left.pack_propagate(False)
        left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = tk.Frame(self)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(left)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.quick_input_area = tk.Frame(left)
        self.quick_input_area.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))

        self.client_tab = tk.Frame(self.notebook)
        self.notebook.add(self.client_tab, text="客户端")

        self.server_tab = tk.Frame(self.notebook)
        self.notebook.add(self.server_tab, text="服务器")

        self.config = Config()
        self.controller = Controller(self)

        self.ui()

    def ui(self) -> None:
        last_tab_index = self.config.get("selected_tab_index")
        if last_tab_index:
            self.notebook.select(int(last_tab_index))

        def on_tab_changed(_: tk.Event[ttk.Notebook]) -> object:
            selected_index: int = self.notebook.index(self.notebook.select())
            self.config.set("selected_tab_index", selected_index)

        self.notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

        tk.Label(self.client_tab, text="对方 IP:").grid(row=0, column=0, padx=(10, 5), pady=8, sticky=tk.E)
        tk.Entry(self.client_tab, textvariable=self.controller.client_ip).grid(row=0, column=1, padx=(0, 10), pady=8, sticky=tk.W)

        tk.Label(self.client_tab, text="对方端口:").grid(row=1, column=0, padx=(10, 5), pady=8, sticky=tk.E)
        tk.Spinbox(self.client_tab, from_=1, to=65535, increment=1, textvariable=self.controller.client_port).grid(row=1, column=1, padx=(0, 10), pady=8, sticky=tk.W)

        client_button_frame = tk.Frame(self.client_tab)
        client_button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        tk.Button(client_button_frame, text="连接", width=8, command=self.controller.connect).pack(side=tk.LEFT, padx=5)
        tk.Button(client_button_frame, text="断开", width=8, command=self.controller.disconnect).pack(side=tk.LEFT, padx=5)

        tk.Label(self.server_tab, text="本地 IP:").grid(row=0, column=0, padx=(10, 5), pady=8, sticky=tk.E)
        tk.Entry(self.server_tab, textvariable=self.controller.server_ip).grid(row=0, column=1, padx=(0, 10), pady=8, sticky=tk.W)

        tk.Label(self.server_tab, text="本地端口:").grid(row=1, column=0, padx=(10, 5), pady=8, sticky=tk.E)
        tk.Spinbox(self.server_tab, from_=1, to=65535, increment=1, textvariable=self.controller.server_port).grid(row=1, column=1, padx=(0, 10), pady=8, sticky=tk.W)

        server_button_frame = tk.Frame(self.server_tab)
        server_button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        tk.Button(server_button_frame, text="启动", width=8, command=self.controller.start).pack(side=tk.LEFT, padx=5)
        tk.Button(server_button_frame, text="停止", width=8, command=self.controller.stop).pack(side=tk.LEFT, padx=5)

        for i in range(1, 11):
            row = tk.Frame(self.quick_input_area)
            row.pack(fill=tk.X, pady=2)

            var = tk.StringVar(value="")
            self.config.bind(f"quick_input_{i}", var)

            entry = tk.Entry(row, textvariable=var)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

            def submit(var: tk.StringVar = var) -> Any:
                data = var.get()
                if not data:
                    return

                self.controller.submit(data)

            button = tk.Button(row, text="发送", command=submit)
            button.pack(side=tk.RIGHT)

        textarea = tk.Text(self.right, font=("monospace", 11))
        textarea.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def on_input(event: tk.Event[tk.Text]) -> object:
            if event.keysym == "Return":
                data = textarea.get("insert linestart", "insert lineend").strip()
                textarea.insert(tk.END, "\n")
                self.controller.submit(data)
                return "break"

        def on_message(data: str) -> None:
            textarea.insert(tk.END, data.rstrip("\n") + "\n")

        textarea.bind("<Key>", on_input)
        self.controller.on_message = on_message


class Config:
    def __init__(self) -> None:
        self.file = pathlib.Path("config.json")
        self.obj: dict[str, Any] = self.load()

    def load(self) -> dict[str, Any]:
        if not self.file.exists():
            self.file.write_text("{}", encoding="utf-8")
            return {}

        content = self.file.read_text(encoding="utf-8")
        return json.loads(content)

    def get(self, name: str) -> Any | None:
        return self.obj.get(name)

    def set(self, name: str, value: Any) -> None:
        self.obj[name] = value

        content = json.dumps(self.obj, ensure_ascii=False)
        self.file.write_text(content, encoding="utf-8")

    def bind(self, name: str, var: tk.Variable):
        value = self.get(name)
        if value:
            var.set(value)

        def on_write(*_: Any) -> object:
            self.set(name, var.get())

        var.trace_add("write", on_write)


class Controller:
    def __init__(self, app: App) -> None:
        self.app = app

        self.client_ip = tk.StringVar(value="")
        self.app.config.bind("client_ip", self.client_ip)

        self.client_port = tk.IntVar(value=0)
        self.app.config.bind("client_port", self.client_port)

        self.server_ip = tk.StringVar(value="")
        self.app.config.bind("server_ip", self.server_ip)

        self.server_port = tk.IntVar(value=0)
        self.app.config.bind("server_port", self.server_port)

        self.sock: socket.socket | None = None
        self.listener: socket.socket | None = None

    def submit(self, data: str) -> None:
        if self.sock:
            try:
                self.sock.sendall((data + "\n").encode("utf-8"))

            except Exception as e:
                self.on_message(f"[系统] 发送数据失败: {e}")
                self.disconnect()

        else:
            self.on_message("[系统] 未建立连接")

    def on_message(self, data: str) -> None:
        pass

    def connect(self) -> None:
        if self.sock or self.listener:
            self.on_message("[系统] 当前已有活跃连接或服务")
            return

        ip = self.client_ip.get().strip()
        port = self.client_port.get()

        self.on_message(f"[系统] 正在尝试连接至 {ip}:{port} ...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            self.sock = sock
            self.on_message(f"[系统] 成功连接至 {ip}:{port}")

        except Exception as e:
            self.on_message(f"[系统] 连接失败: {e}")
            return

        def listen() -> None:
            while self.sock:
                try:
                    data = self.sock.recv(1024)
                    if not data:
                        self.app.after(0, self.on_message, "[系统] 远程主机已关闭连接")
                        break

                    text = data.decode("utf-8", errors="ignore")
                    self.app.after(0, self.on_message, text)

                except Exception:
                    break

            self.app.after(0, self.disconnect)

        threading.Thread(target=listen, daemon=True).start()

    def disconnect(self) -> None:
        sock = self.sock
        self.sock = None

        if sock:
            try:
                sock.close()
                self.on_message("[系统] 已断开连接")

            except Exception as e:
                self.on_message(f"[系统] 断开连接时出错: {e}")

    def start(self) -> None:
        if self.sock or self.listener:
            self.on_message("[系统] 当前已有活跃服务或连接")
            return

        ip = self.server_ip.get().strip()
        port = self.server_port.get()

        self.on_message(f"[系统] 正在启动服务器 {ip}:{port} ...")
        try:
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((ip, port))
            listener.listen(1)
            self.listener = listener
            self.on_message(f"[系统] 等待客户端连接...")

        except Exception as e:
            self.on_message(f"[系统] 服务器启动失败: {e}")
            return

        def accept_thread() -> None:
            try:
                client_sock, client_addr = listener.accept()
                listener.close()
                self.listener = None

                self.sock = client_sock
                self.app.after(0, self.on_message, f"[系统] 客户端 {client_addr[0]}:{client_addr[1]} 已连接")

                while self.sock:
                    data = self.sock.recv(1024)
                    if not data:
                        self.app.after(0, self.on_message, "[系统] 客户端已断开连接")
                        break

                    text = data.decode("utf-8", errors="ignore")
                    self.app.after(0, self.on_message, text)

            except Exception:
                pass

            finally:
                self.app.after(0, self.stop)

        threading.Thread(target=accept_thread, daemon=True).start()

    def stop(self) -> None:
        if self.listener:
            try:
                self.listener.close()

            except Exception:
                pass

            self.listener = None

        sock = self.sock
        self.sock = None

        if sock:
            try:
                sock.close()
                self.on_message("[系统] 服务器已停止")

            except Exception as e:
                self.on_message(f"[系统] 停止服务器时出错: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
