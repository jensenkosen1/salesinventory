import tkinter as tk
from tkinter import filedialog

def select_file():
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("All Files", "*.*"), ("Text Files", "*.txt"), ("Python Files", "*.py")])
    if file_path:
        label.config(text=f"Selected File:\n{file_path}")

# Create main window
root = tk.Tk()
root.title("File Selector")
root.geometry("400x200")

# Create button to select file
button = tk.Button(root, text="Browse Files", command=select_file, padx=10, pady=5)
button.pack(pady=20)

# Label to show selected file
label = tk.Label(root, text="No file selected", wraplength=350, justify="left")
label.pack()

# Run Tkinter event loop
root.mainloop()

