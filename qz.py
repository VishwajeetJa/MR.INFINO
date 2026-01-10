import tkinter as tk
from tkinter import messagebox
import wikipedia
import random
import re

# ---------- Theme Settings ----------
THEMES = {
    "Light 🌞": {
        "bg": "#ffffff", "fg": "#000000", "button": "#e3e3e3",
        "progress": "green", "correct": "green", "wrong": "red"
    },
    "Dark 🌙": {
        "bg": "#1f1f1f", "fg": "#ffffff", "button": "#333333",
        "progress": "#00ff99", "correct": "#00ff00", "wrong": "#ff5555"
    },
    "Pink Barbie 🌸": {
        "bg": "#ffe1ff", "fg": "#ff1493", "button": "#ffb8e8",
        "progress": "#ff1493", "correct": "#ff1493", "wrong": "#ff0088"
    },
    "Gaming Neon 🎮": {
        "bg": "#0d0221", "fg": "#00eaff", "button": "#10002b",
        "progress": "#00eaff", "correct": "#39ff14", "wrong": "#ff073a"
    }
}

class QuizApp:
    def __init__(self, root, topic, num_questions, theme):
        self.root = root
        self.root.title("🌈 AUTO QUIZ WITH THEMES 🌈")
        self.root.geometry("700x500")
        self.theme = THEMES[theme]

        self.root.configure(bg=self.theme["bg"])

        self.topic = topic
        self.num_questions = num_questions
        self.score = 0
        self.current = 0
        self.time_left = 15
        self.timer_id = None

        self.questions = self.load_questions()
        if not self.questions:
            messagebox.showerror("Error", "⚠ No questions found for this topic!")
            root.destroy()
            return

        # ------- UI -------
        self.question_label = tk.Label(root, text="", font=("Arial", 14),
                                       bg=self.theme["bg"], fg=self.theme["fg"], wraplength=650)
        self.question_label.pack(pady=20)

        self.hint_label = tk.Label(root, text="", font=("Arial", 12),
                                   bg=self.theme["bg"], fg=self.theme["correct"])
        self.hint_label.pack(pady=5)

        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(root, text="", font=("Arial", 12), width=30, bg=self.theme["button"], fg=self.theme["fg"],
                            command=lambda idx=i: self.check_answer(idx))
            btn.pack(pady=5)
            self.option_buttons.append(btn)

        self.skip_button = tk.Button(root, text="⏭️ Skip Question", font=("Arial", 12, "bold"),
                                     bg=self.theme["button"], fg=self.theme["fg"], command=self.skip_question)
        self.skip_button.pack(pady=10)

        self.progress_frame = tk.Frame(root, bg="lightgray", height=20, width=600)
        self.progress_frame.pack(pady=10)
        self.progress_bar = tk.Frame(self.progress_frame, bg=self.theme["progress"], height=20, width=0)
        self.progress_bar.pack(side="left")

        self.timer_label = tk.Label(root, text=f"⏰ Time left: {self.time_left}s", font=("Arial", 12),
                                    bg=self.theme["bg"], fg="red")
        self.timer_label.pack(pady=5)

        self.score_label = tk.Label(root, text=f"💖 Score: {self.score}/{self.num_questions}", font=("Arial", 12),
                                    bg=self.theme["bg"], fg=self.theme["correct"])
        self.score_label.pack(pady=5)

        self.show_question()

    def load_questions(self):
        try:
            content = wikipedia.summary(self.topic, sentences=15)
        except:
            return []

        words = re.findall(r'\b\w{6,}\b', content)
        keywords = list(set(words))
        random.shuffle(keywords)
        questions = []

        for i in range(min(self.num_questions, len(keywords))):
            answer = keywords[i]
            sentence = next((s for s in content.split('.') if answer in s), None)
            if sentence:
                question = sentence.replace(answer, "_______") + "?"
                distractors = random.sample([w for w in keywords if w != answer], k=3)
                options = distractors + [answer]
                random.shuffle(options)
                questions.append((question.strip(), options, answer))
        return questions

    def show_question(self):
        if self.current >= len(self.questions):
            self.show_end_screen()
            return

        self.time_left = 15
        self.update_timer()

        q = self.questions[self.current]
        self.question_label.config(text=f"🎯 Q{self.current+1}: {q[0]}")
        self.hint_label.config(text=f"💡 Hint: starts with '{q[2][0]}'")

        for i, opt in enumerate(q[1]):
            self.option_buttons[i].config(text=opt, state="normal")

        self.update_progress_bar()

    def check_answer(self, idx):
        q = self.questions[self.current]
        correct = q[1][idx].lower() == q[2].lower()

        if correct:
            self.score += 1
            messagebox.showinfo("Correct!", "🎉 Awesome!")
        else:
            messagebox.showinfo("Wrong", f"❌ Correct answer: {q[2]}")

        self.score_label.config(text=f"💖 Score: {self.score}/{self.num_questions}")
        self.current += 1

        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        self.show_question()

    def skip_question(self):
        messagebox.showinfo("Skipped ⏭️", "You skipped this question!")
        self.current += 1
        self.show_question()

    def update_timer(self):
        self.timer_label.config(text=f"⏰ Time left: {self.time_left}s")
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's Up!", f"⏰ Correct Answer: {self.questions[self.current][2]}")
            self.current += 1
            self.show_question()

    def update_progress_bar(self):
        progress = int((self.current / self.num_questions) * 600)
        self.progress_bar.config(width=progress)

    def show_end_screen(self):
        percent = int((self.score / self.num_questions) * 100)
        messagebox.showinfo("Quiz Completed 🎉",
                            f"✨ Score: {self.score}/{self.num_questions}\n📊 Percentage: {percent}%")
        self.root.destroy()


# -------- Theme Selection Window --------
def start_quiz():
    topic = topic_entry.get()
    num = num_entry.get()
    chosen_theme = theme_var.get()

    if not num.isdigit() or int(num) <= 0:
        messagebox.showerror("Error", "Enter a valid number of questions.")
        return

    start_window.destroy()
    root = tk.Tk()
    QuizApp(root, topic, int(num), chosen_theme)
    root.mainloop()

start_window = tk.Tk()
start_window.title("🎨 Select Theme")
start_window.geometry("400x350")
start_window.configure(bg="#ffe6ff")

tk.Label(start_window, text="Enter Topic:", bg="#ffe6ff", font=("Arial", 12)).pack(pady=5)
topic_entry = tk.Entry(start_window, font=("Arial", 12))
topic_entry.pack()

tk.Label(start_window, text="Number of Questions:", bg="#ffe6ff", font=("Arial", 12)).pack(pady=5)
num_entry = tk.Entry(start_window, font=("Arial", 12))
num_entry.pack()

tk.Label(start_window, text="Choose Theme:", bg="#ffe6ff", font=("Arial", 12, "bold")).pack(pady=10)

theme_var = tk.StringVar(value="Light 🌞")
for theme in THEMES.keys():
    tk.Radiobutton(start_window, text=theme, variable=theme_var, value=theme, bg="#ffe6ff",
                   font=("Arial", 10)).pack(anchor="w")

tk.Button(start_window, text="Start Quiz 🚀", bg="#ff59c7", fg="white", font=("Arial", 13, "bold"),
          command=start_quiz).pack(pady=15)

start_window.mainloop()
