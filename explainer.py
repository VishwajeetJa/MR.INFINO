import tkinter as tk
from tkinter import scrolledtext, ttk

def explain_line(line, lang):
    line = line.strip()

    if lang == "Python":
        if "input(" in line:
            return "Takes input from the user."
        if "=" in line and "==" not in line:
            return "Assigns value to a variable."
        if line.startswith("print"):
            return "Displays output."
    else:
        if "=" in line:
            return "Variable assignment or operation."
        if "printf" in line or "cout" in line:
            return "Displays output."
        if "scanf" in line or "cin" in line:
            return "Takes input from the user."
        if "if" in line:
            return "Checks a condition."
        if "for" in line or "while" in line:
            return "Loop statement."
        if "(" in line and ")" in line and "{" in line:
            return "Function definition."

    return "General statement or logic."

def run_tutor():
    output.delete("1.0", tk.END)
    code = code_area.get("1.0", tk.END)
    lang = language.get()

    lines = code.split("\n")

    output.insert(tk.END, f"📘 Language Selected: {lang}\n\n")

    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        explanation = explain_line(line, lang)
        output.insert(tk.END, f"🔹 Line {i}: {line}\n")
        output.insert(tk.END, f"👉 Explanation: {explanation}\n")
        output.insert(tk.END, "-" * 50 + "\n")

    output.insert(tk.END, "\n✅ Code Explanation Completed")

# -------- GUI --------
root = tk.Tk()
root.title("UniTutor – Universal Code Tutor")
root.geometry("900x600")

tk.Label(root, text="Select Language:", font=("Arial", 11, "bold")).pack()

language = tk.StringVar(value="Python")
lang_menu = ttk.Combobox(root, textvariable=language,
                         values=["Python", "C", "C++", "Java", "JavaScript"],
                         state="readonly")
lang_menu.pack(pady=5)

tk.Label(root, text="Enter Code:", font=("Arial", 11, "bold")).pack()

code_area = scrolledtext.ScrolledText(root, height=12)
code_area.pack(fill=tk.BOTH, padx=10)

tk.Button(root, text="▶ Explain Code",
          bg="#2196F3", fg="white",
          font=("Arial", 11),
          command=run_tutor).pack(pady=8)

tk.Label(root, text="Explanation Output:", font=("Arial", 11, "bold")).pack()

output = scrolledtext.ScrolledText(root, height=15)
output.pack(fill=tk.BOTH, padx=10)

root.mainloop()
