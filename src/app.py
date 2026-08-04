import tkinter as tk

app = tk.Tk()
app.title("tcpad")
app.minsize(800, 600)
app.geometry("800x600")

left_frame = tk.Frame(app, bg="#dedede", width=260)
left_frame.pack_propagate(False)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

right_frame = tk.Frame(app, bg="#eaeaea")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

app.mainloop()
