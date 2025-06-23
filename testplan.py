import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
from docx import Document
from fpdf import FPDF

OPENROUTER_API_KEY = "u api "
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class TestPlanBuilderAI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Interactive Test Plan Builder with Risk Analysis & Strategy")
        self.root.geometry("800x750")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Select Project Type:").pack(anchor='w', padx=10, pady=(10,2))
        self.project_type = ttk.Combobox(self.root, values=[
            "Web Application", "Mobile Application", "API", "Desktop Application", "Embedded System"
        ], state="readonly")
        self.project_type.current(0)
        self.project_type.pack(fill='x', padx=10)

        ttk.Label(self.root, text="Enter Project Description:").pack(anchor='w', padx=10, pady=(10,2))
        self.desc_entry = tk.Text(self.root, height=6)
        self.desc_entry.pack(fill='both', padx=10, pady=(0,10))

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Generate Test Plan", command=self.generate_test_plan).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Generate Test Strategy", command=self.generate_test_strategy).grid(row=0, column=1, padx=5)

        ttk.Label(self.root, text="Generated Output:").pack(anchor='w', padx=10)
        self.output_area = scrolledtext.ScrolledText(self.root, height=25)
        self.output_area.pack(fill='both', padx=10, pady=5, expand=True)

        export_frame = ttk.Frame(self.root)
        export_frame.pack(pady=10)
        ttk.Button(export_frame, text="Export as PDF", command=self.export_pdf).grid(row=0, column=0, padx=10)
        ttk.Button(export_frame, text="Export as Word", command=self.export_word).grid(row=0, column=1, padx=10)

    def generate_test_plan(self):
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, "⏳ Generating Test Plan and Risk Analysis...\n")
        self.root.update()

        desc = self.desc_entry.get("1.0", tk.END).strip()
        if not desc:
            messagebox.showwarning("Warning", "Please enter the project description.")
            return

        try:
            project_type = self.project_type.get()
            plan_prompt = (
                f"Create a full test plan for a {project_type} based on the description below:\n"
                f"{desc}\n\n"
                "Include: Introduction, Scope, Objectives, Test Types, Tools, Environment, Schedule, Resources, Deliverables. "
                "Do not include risk analysis."
            )
            plan = self.call_openrouter_api(plan_prompt)

            risk_prompt = (
                f"Generate a Risk Analysis section for a {project_type} project based on the following:\n{desc}"
            )
            risk = self.call_openrouter_api(risk_prompt)

            final_output = plan.strip() + "\n\n=== Risk Analysis ===\n" + risk.strip()
            self.output_area.delete("1.0", tk.END)
            self.output_area.insert(tk.END, final_output)
        except Exception as e:
            self.output_area.insert(tk.END, f"\n❌ Error: {e}")

    def generate_test_strategy(self):
        self.output_area.insert(tk.END, "\n\n⏳ Generating Test Strategy...\n")
        self.root.update()

        desc = self.desc_entry.get("1.0", tk.END).strip()
        if not desc:
            messagebox.showwarning("Warning", "Please enter the project description.")
            return

        try:
            project_type = self.project_type.get()
            strategy_prompt = (
                f"Create a detailed Test Strategy document for a {project_type} project.\n"
                f"Description:\n{desc}\n"
                "Include: Testing approach, Test levels, Tools, Entry & Exit Criteria, Metrics, Risk mitigation, Communication strategy."
            )
            strategy = self.call_openrouter_api(strategy_prompt)
            self.output_area.insert(tk.END, "\n\n=== Test Strategy ===\n" + strategy.strip())
        except Exception as e:
            self.output_area.insert(tk.END, f"\n❌ Error: {e}")

    def call_openrouter_api(self, prompt):
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1800,
            "temperature": 0.7,
        }
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def export_pdf(self):
        content = self.output_area.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Nothing to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            for line in content.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf.output(file_path)
            messagebox.showinfo("Success", "Exported as PDF successfully!")

    def export_word(self):
        content = self.output_area.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Nothing to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word files", "*.docx")])
        if file_path:
            doc = Document()
            for line in content.split('\n'):
                doc.add_paragraph(line)
            doc.save(file_path)
            messagebox.showinfo("Success", "Exported as Word successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestPlanBuilderAI(root)
    root.mainloop()
