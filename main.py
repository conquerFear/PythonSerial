# main.py
import tkinter as tk
from GUI import SerialAppGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialAppGUI(root)
    root.mainloop()