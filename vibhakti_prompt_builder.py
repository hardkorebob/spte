#!/usr/bin/env python3
"""
Vibhakti Prompt Builder
=======================
A guided wizard for building precise AI prompts based on
Sanskrit's 8-case grammar system (Panini's Ashtadhyayi).

Usage:  python3 vibhakti_prompt_builder.py
Requires: Python 3.x with tkinter (included in standard installs)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# DATA: Section definitions
# ──────────────────────────────────────────────────────────────────────────────

SECTIONS = [
    {
        "number": "1",
        "title": "Addressee / Role Assignment",
        
        "guidance": (
            "Who is the AI acting as?\n"
            "Define expertise, seniority, and domain.\n"
            "Be specific — 'senior backend engineer with 10 years\n"
            "of TypeScript experience' is better than 'developer'."
        ),
        "fields": [
            ("Role", "single", "e.g. Senior full-stack engineer"),
            ("Expertise", "single", "e.g. React, Node.js, PostgreSQL, AWS"),
            ("Tone", "single", "e.g. Production-grade code, concise comments"),
        ],
    },
    {
        "number": "2",
        "title": "Agent / Subject",
        
        "guidance": (
            "Who or what performs the primary action?\n"
            "A user type, a system process, a cron job,\n"
            "an API consumer, an admin, etc."
        ),
        "fields": [
            ("Primary Agent", "single", "e.g. Authenticated admin user"),
            ("Agent Description", "multi", "Describe the agent's context and behavior"),
            ("Agent Permissions", "single", "e.g. Read/write to orders table, no delete"),
        ],
    },
    {
        "number": "3",
        "title": "Action / Verb",
        
        "guidance": (
            "What is the core action? Use one precise verb.\n"
            "If there are multiple actions, list them in\n"
            "execution order in the secondary actions field."
        ),
        "fields": [
            ("Primary Action", "single", "e.g. Validate and submit a registration form"),
            ("Secondary Action A", "single", "e.g. Sanitize all text inputs"),
            ("Secondary Action B", "single", "e.g. Check email uniqueness via API"),
            ("Secondary Action C", "single", "e.g. Display success or error feedback"),
        ],
    },
    {
        "number": "4",
        "title": "Object / Target",
        
        "guidance": (
            "What is being created, modified, fetched, deleted,\n"
            "or transformed? Be specific about data shape,\n"
            "UI element, file, or system artifact."
        ),
        "fields": [
            ("Primary Object", "single", "e.g. A user registration form component"),
            ("Object Details", "multi", "Describe structure, fields, data shape"),
            ("Object Format or Shape", "single", "e.g. Single .tsx file, exports default component"),
        ],
    },
    {
        "number": "5",
        "title": "Instrument / Means",
        
        "guidance": (
            "What tools, languages, frameworks, libraries,\n"
            "patterns, or methods must be used?\n"
            "Also state what must NOT be used."
        ),
        "fields": [
            ("Required Stack", "multi", "Languages, frameworks, libraries, versions"),
            ("Required Patterns", "single", "e.g. Repository pattern, dependency injection"),
            ("Forbidden Tools or Patterns", "multi", "What must NOT be used and why"),
        ],
    },
    {
        "number": "6",
        "title": "Source / Origin",
        
        "guidance": (
            "Where does the input data or existing code come from?\n"
            "Database, API, file upload, user input, another\n"
            "microservice, a CSV, a third-party webhook, etc."
        ),
        "fields": [
            ("Data Source", "single", "e.g. REST API at /api/v2/users"),
            ("Input Format", "single", "e.g. JSON with fields: name, email, role"),
            ("Authentication to Source", "single", "e.g. Bearer token from env AUTH_TOKEN"),
        ],
    },
    {
        "number": "7",
        "title": "Purpose / Beneficiary",
        
        "guidance": (
            "For whom is this built and why?\n"
            "What is the measurable outcome or acceptance criteria?\n"
            "List concrete, testable criteria."
        ),
        "fields": [
            ("Beneficiary", "single", "e.g. Non-technical marketing team members"),
            ("Goal", "single", "e.g. Self-serve dashboard creation without engineering help"),
            ("Acceptance Criterion A", "single", "e.g. Form validates all fields before submit"),
            ("Acceptance Criterion B", "single", "e.g. Error messages appear inline per field"),
            ("Acceptance Criterion C", "single", "e.g. Submits in under 200ms on 3G"),
        ],
    },
    {
        "number": "8",
        "title": "Ownership / Relation",
        
        "guidance": (
            "What larger system, project, module, or domain does\n"
            "this belong to? What naming conventions or architectural\n"
            "rules does that parent system enforce?"
        ),
        "fields": [
            ("Parent Project", "single", "e.g. Acme SaaS Platform monorepo"),
            ("Module or Domain", "single", "e.g. packages/auth/src/components/"),
            ("Naming Conventions", "single", "e.g. camelCase vars, PascalCase components"),
            ("Architectural Rules", "multi", "e.g. No direct DB imports in components"),
        ],
    },
    {
        "number": "9",
        "title": "Context / Locus",
        
        "guidance": (
            "Where and when does this execute?\n"
            "Environment, page, route, trigger event,\n"
            "runtime constraints, deployment target."
        ),
        "fields": [
            ("Environment", "single", "e.g. Node.js 20, Browser ES2022+"),
            ("Route or Location", "single", "e.g. /settings/profile page, right sidebar"),
            ("Trigger Event", "single", "e.g. User clicks 'Save Profile' button"),
            ("Runtime Constraints", "single", "e.g. Must render in under 100ms, max 512MB RAM"),
            ("Deployment Target", "single", "e.g. Vercel Edge, Docker on AWS EKS"),
        ],
    },
    {
        "number": "10",
        "title": "Constraints / Qualifiers",
        
        "guidance": (
            "Non-functional requirements: performance, security,\n"
            "accessibility, file size, token limits, error handling,\n"
            "and edge cases that must be addressed."
        ),
        "fields": [
            ("Performance", "single", "e.g. Page load under 1.5s, Lighthouse > 90"),
            ("Security", "single", "e.g. Sanitize all inputs, no eval(), CSP compliant"),
            ("Accessibility", "single", "e.g. WCAG 2.1 AA, keyboard navigable"),
            ("Error Handling", "single", "e.g. Result type pattern, no uncaught exceptions"),
            ("Edge Case A", "single", "e.g. Empty form submission"),
            ("Edge Case B", "single", "e.g. Network timeout mid-submission"),
            ("Edge Case C", "single", "e.g. Concurrent edits by two users"),
        ],
    },
    {
        "number": "11",
        "title": "Examples / References",
        
        "guidance": (
            "Provide concrete input/output examples, reference\n"
            "implementations, or links the AI should study\n"
            "before generating code."
        ),
        "fields": [
            ("Example Input", "multi", "Paste a sample input payload or describe it"),
            ("Expected Output", "multi", "Paste the expected result or describe it"),
            ("Reference Implementation or Link", "multi", "File path, URL, or code snippet to follow"),
        ],
    },
    {
        "number": "12",
        "title": "Anti-Requirements / What This Is NOT",
        
        "guidance": (
            "State what the AI must avoid generating.\n"
            "Wrong interpretations you want to prevent.\n"
            "Common mistakes for this type of task."
        ),
        "fields": [
            ("This is NOT", "multi", "e.g. This is NOT a REST endpoint. No HTTP responses."),
            ("Do NOT", "multi", "e.g. Do NOT query the DB; all data is in the event payload."),
            ("Common Mistakes to Avoid", "multi", "e.g. Don't use try/catch for flow control."),
        ],
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# COLORS & STYLE
# ──────────────────────────────────────────────────────────────────────────────

BG           = "#1a1a2e"
BG_CARD      = "#16213e"
BG_INPUT     = "#0f3460"
FG           = "#e0e0e0"
FG_DIM       = "#8888aa"
FG_TITLE     = "#e94560"
FG_SANSKRIT  = "#f5a623"
ACCENT       = "#e94560"
ACCENT_HOVER = "#ff6b81"
BTN_BG       = "#e94560"
BTN_FG       = "#ffffff"
BTN_NAV_BG   = "#0f3460"
BORDER       = "#533483"
FONT_TITLE   = ("Segoe UI", 18, "bold")
FONT_SECTION = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_INPUT   = ("Consolas", 10)
FONT_MONO    = ("Consolas", 9)


# ──────────────────────────────────────────────────────────────────────────────
# APPLICATION
# ──────────────────────────────────────────────────────────────────────────────

class VibhaktiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vibhakti Prompt Builder")
        self.root.geometry("820x700")
        self.root.minsize(780, 600)
        self.root.configure(bg=BG)

        self.current_step = 0
        self.field_widgets = {}   # step_index -> { field_label: widget }

        self._build_ui()
        self._show_step(0)

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar: title + progress
        top = tk.Frame(self.root, bg=BG, pady=10, padx=20)
        top.pack(fill="x")

        tk.Label(
            top, text="VIBHAKTI PROMPT BUILDER", font=FONT_TITLE,
            bg=BG, fg=FG_TITLE, anchor="w"
        ).pack(side="left")

        self.progress_label = tk.Label(
            top, text="", font=FONT_SMALL, bg=BG, fg=FG_DIM, anchor="e"
        )
        self.progress_label.pack(side="right")

        # Progress bar
        bar_frame = tk.Frame(self.root, bg=BG, padx=20)
        bar_frame.pack(fill="x")
        self.progress_canvas = tk.Canvas(
            bar_frame, height=6, bg=BG, highlightthickness=0
        )
        self.progress_canvas.pack(fill="x")

        # Scrollable content area
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Make canvas window resize with canvas
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.canvas.bind_all("<Button-4>",
            lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>",
            lambda e: self.canvas.yview_scroll(1, "units"))

        # Bottom navigation
        nav = tk.Frame(self.root, bg=BG, pady=12, padx=20)
        nav.pack(fill="x", side="bottom")

        self.btn_prev = tk.Button(
            nav, text="<  PREVIOUS", font=FONT_SECTION,
            bg=BTN_NAV_BG, fg=FG, activebackground=BORDER, activeforeground=FG,
            relief="flat", padx=18, pady=8, cursor="hand2",
            command=self._prev_step
        )
        self.btn_prev.pack(side="left")

        self.btn_next = tk.Button(
            nav, text="NEXT  >", font=FONT_SECTION,
            bg=BTN_BG, fg=BTN_FG, activebackground=ACCENT_HOVER,
            activeforeground=BTN_FG, relief="flat", padx=18, pady=8,
            cursor="hand2", command=self._next_step
        )
        self.btn_next.pack(side="right")

        # Center buttons: Clear + Jump
        center_nav = tk.Frame(nav, bg=BG)
        center_nav.pack(side="right", padx=20)

        self.btn_clear = tk.Button(
            center_nav, text="CLEAR SECTION", font=FONT_SMALL,
            bg=BG, fg=FG_DIM, activebackground=BG, activeforeground=FG,
            relief="flat", padx=10, pady=4, cursor="hand2",
            command=self._clear_current
        )
        self.btn_clear.pack(side="left", padx=(0, 8))

        # Jump-to dropdown
        tk.Label(center_nav, text="Jump to:", font=FONT_SMALL,
                 bg=BG, fg=FG_DIM).pack(side="left", padx=(8, 4))

        self.jump_var = tk.StringVar()
        jump_values = [f"{s['number']}. {s['title']}" for s in SECTIONS]
        jump_values.append(">> GENERATE PROMPT")
        self.jump_combo = ttk.Combobox(
            center_nav, textvariable=self.jump_var,
            values=jump_values, state="readonly", width=28
        )
        self.jump_combo.pack(side="left")
        self.jump_combo.bind("<<ComboboxSelected>>", self._on_jump)

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # ── Step rendering ────────────────────────────────────────────────────

    def _show_step(self, index):
        self.current_step = index

        # Clear scroll area
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        # Update progress
        total = len(SECTIONS) + 1  # +1 for generate step
        self.progress_label.config(
            text=f"Step {index + 1} of {total}"
        )
        self._draw_progress(index, total)

        # Update nav buttons
        self.btn_prev.config(state="normal" if index > 0 else "disabled")
        if index < len(SECTIONS):
            self.btn_next.config(text="NEXT  >", bg=BTN_BG)
        else:
            self.btn_next.config(text="", bg=BG, state="normal")

        if index < len(SECTIONS):
            self._render_section(index)
        else:
            self._render_generate_page()

        self.canvas.yview_moveto(0)

    def _draw_progress(self, current, total):
        self.progress_canvas.delete("all")
        self.root.update_idletasks()
        w = self.progress_canvas.winfo_width()
        if w < 10:
            w = 760
        # Background bar
        self.progress_canvas.create_rectangle(
            0, 0, w, 6, fill=BG_INPUT, outline=""
        )
        # Filled portion
        fill_w = int(w * (current + 1) / total)
        self.progress_canvas.create_rectangle(
            0, 0, fill_w, 6, fill=ACCENT, outline=""
        )

    def _render_section(self, index):
        section = SECTIONS[index]
        frame = self.scroll_frame

        # Section header
        header = tk.Frame(frame, bg=BG)
        header.pack(fill="x", pady=5)

        tk.Label(
            header,
            text=f"  {section['number']}  ",
            font=("Segoe UI", 22, "bold"), bg=ACCENT, fg=BTN_FG,
        ).pack(side="left", padx=(0, 12))

        title_block = tk.Frame(header, bg=BG)
        title_block.pack(side="left", fill="x")
        tk.Label(
            title_block, text=section["title"], font=FONT_TITLE,
            bg=BG, fg=FG, anchor="w"
        ).pack(anchor="w")

        # Guidance box
        guide_frame = tk.Frame(frame, bg=BG_CARD, padx=14, pady=10)
        guide_frame.pack(fill="x", pady=10)
        tk.Label(
            guide_frame, text=section["guidance"], font=FONT_BODY,
            bg=BG_CARD, fg=FG_DIM, justify="left", anchor="w", wraplength=700
        ).pack(anchor="w")

        # Fields
        if index not in self.field_widgets:
            self.field_widgets[index] = {}

        for label, field_type, placeholder in section["fields"]:
            self._make_field(frame, index, label, field_type, placeholder)

    def _make_field(self, parent, step_index, label, field_type, placeholder):
        tk.Label(
            parent, text=label.upper(), font=FONT_SECTION,
            bg=BG, fg=FG, anchor="w", pady=8
        ).pack(fill="x")

        tk.Label(
            parent, text=placeholder, font=FONT_SMALL,
            bg=BG, fg=FG_DIM, anchor="w"
        ).pack(fill="x")

        if field_type == "single":
            widget = tk.Entry(
                parent, font=FONT_INPUT, bg=BG_INPUT, fg=FG,
                insertbackground=FG, relief="flat", borderwidth=0,
                highlightthickness=1, highlightcolor=ACCENT,
                highlightbackground=BORDER
            )
            widget.pack(fill="x", ipady=8, pady=10)

            # Restore saved value
            if label in self.field_widgets.get(step_index, {}):
                saved = self.field_widgets[step_index][label]
                if isinstance(saved, str):
                    widget.insert(0, saved)
        else:
            widget = tk.Text(
                parent, font=FONT_INPUT, bg=BG_INPUT, fg=FG,
                insertbackground=FG, relief="flat", borderwidth=0,
                highlightthickness=1, highlightcolor=ACCENT,
                highlightbackground=BORDER, height=4, wrap="word"
            )
            widget.pack(fill="x", pady=10)

            if label in self.field_widgets.get(step_index, {}):
                saved = self.field_widgets[step_index][label]
                if isinstance(saved, str):
                    widget.insert("1.0", saved)

        self.field_widgets[step_index][label] = widget

    # ── Navigation ────────────────────────────────────────────────────────

    def _save_current_fields(self):
        """Save widget contents to strings so we can restore after re-render."""
        idx = self.current_step
        if idx >= len(SECTIONS):
            return
        saved = {}
        for label, widget in self.field_widgets.get(idx, {}).items():
            if isinstance(widget, tk.Entry):
                saved[label] = widget.get()
            elif isinstance(widget, tk.Text):
                saved[label] = widget.get("1.0", "end-1c")
            elif isinstance(widget, str):
                saved[label] = widget
        self.field_widgets[idx] = saved

    def _next_step(self):
        self._save_current_fields()
        if self.current_step < len(SECTIONS):
            self._show_step(self.current_step + 1)

    def _prev_step(self):
        self._save_current_fields()
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _on_jump(self, event):
        self._save_current_fields()
        sel = self.jump_combo.current()
        if sel >= 0:
            self._show_step(sel)
        self.jump_var.set("")

    def _clear_current(self):
        idx = self.current_step
        if idx >= len(SECTIONS):
            return
        for label, widget in self.field_widgets.get(idx, {}).items():
            if isinstance(widget, tk.Entry):
                widget.delete(0, "end")
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
        self.field_widgets[idx] = {}
        self._show_step(idx)

    # ── Generate page ─────────────────────────────────────────────────────

    def _render_generate_page(self):
        frame = self.scroll_frame

        tk.Label(
            frame, text="GENERATE PROMPT", font=FONT_TITLE,
            bg=BG, fg=FG_TITLE, anchor="w"
        ).pack(fill="x", pady=4)

        tk.Label(
            frame,
            text="Review your prompt below. Copy to clipboard or save as a text file.",
            font=FONT_BODY, bg=BG, fg=FG_DIM, anchor="w"
        ).pack(fill="x", pady=12)

        # Button row
        btn_row = tk.Frame(frame, bg=BG)
        btn_row.pack(fill="x", pady=10)

        tk.Button(
            btn_row, text="COPY TO CLIPBOARD", font=FONT_SECTION,
            bg=BTN_BG, fg=BTN_FG, activebackground=ACCENT_HOVER,
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=self._copy_to_clipboard
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_row, text="SAVE AS .TXT", font=FONT_SECTION,
            bg=BTN_NAV_BG, fg=FG, activebackground=BORDER,
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=self._save_to_file
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_row, text="START OVER", font=FONT_SECTION,
            bg=BG, fg=FG_DIM, activebackground=BG,
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=self._start_over
        ).pack(side="right")

        # Output preview
        self.output_text = tk.Text(
            frame, font=FONT_MONO, bg=BG_INPUT, fg=FG,
            insertbackground=FG, relief="flat", borderwidth=0,
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=BORDER, wrap="word", height=28
        )
        self.output_text.pack(fill="both", expand=True, pady=10)

        prompt = self._build_prompt_text()
        self.output_text.insert("1.0", prompt)

    def _build_prompt_text(self):
        lines = []
        divider = "=" * 72

        lines.append(divider)
        lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(divider)
        lines.append("")

        for i, section in enumerate(SECTIONS):
            section_head = (
                f"----- {section['number']}. {section['title']} "
            )
            section_head += "-" * max(0, 72 - len(section_head))
            lines.append(section_head)
            lines.append("")

            data = self.field_widgets.get(i, {})
            for label, field_type, _ in section["fields"]:
                value = data.get(label, "")
                if isinstance(value, (tk.Entry, tk.Text)):
                    # Widget still live (shouldn't happen but safety)
                    if isinstance(value, tk.Entry):
                        value = value.get()
                    else:
                        value = value.get("1.0", "end-1c")
                value = value.strip() if value else ""

                if not value:
                    value = "(not specified)"

                # Indent multi-line values
                if "\n" in value:
                    formatted = f"  {label}:\n"
                    for vline in value.split("\n"):
                        formatted += f"    {vline}\n"
                    lines.append(formatted.rstrip())
                else:
                    lines.append(f"  {label}: {value}")

            lines.append("")

        lines.append(divider)
        lines.append("  END OF PROMPT")
        lines.append(divider)
        return "\n".join(lines)

    # ── Actions ───────────────────────────────────────────────────────────

    def _copy_to_clipboard(self):
        text = self.output_text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Prompt copied to clipboard.")

    def _save_to_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"vibhakti_prompt_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
        if path:
            text = self.output_text.get("1.0", "end-1c")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Prompt saved to:\n{path}")

    def _start_over(self):
        if messagebox.askyesno("Start Over", "Clear all fields and start from step 1?"):
            self.field_widgets = {}
            self._show_step(0)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = VibhaktiApp(root)
    root.mainloop()
