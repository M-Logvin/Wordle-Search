import tkinter as tk
from tkinter import ttk
import copy

# --- Load words ---
with open("words.txt", "r") as f:
    WORDS = sorted({w.strip().lower() for w in f if w.strip()})

# --- Filters storage ---
filters = {
    "Not Contains": set(),   # gray tile
    "At Position": {},       # green tile
    "Not Position": {}       # yellow tile
}

FILTER_MAP = {
    "Gray Tile:": "Not Contains",
    "Green Tile:": "At Position",
    "Yellow Tile:": "Not Position"
}
REVERSE_FILTER_MAP = {v: k for k, v in FILTER_MAP.items()}

filter_history = []

# --- Filtering function ---
def apply_filters():
    filtered = WORDS
    for letter in filters["Not Contains"]:
        filtered = [w for w in filtered if letter not in w]
    for pos, letter in filters["At Position"].items():
        filtered = [w for w in filtered if pos < len(w) and w[pos] == letter]
    for pos, letter in filters["Not Position"].items():
        filtered = [w for w in filtered if letter in w and (pos >= len(w) or w[pos] != letter)]
    update_results(filtered)

# --- GUI callbacks ---
def add_filter():
    ftype = FILTER_MAP.get(filter_type.get())
    val = filter_value.get().lower().strip()
    if not val:
        return

    filter_history.append(copy.deepcopy(filters))

    if ftype == "Not Contains":
        filters[ftype].add(val)
    else:
        try:
            p = int(position_value.get().strip()) - 1
            filters[ftype][p] = val
        except ValueError:
            return

    filter_value.delete(0, tk.END)
    position_value.delete(0, tk.END)
    update_filter_list()
    apply_filters()

def clear_filters():
    filter_history.append(copy.deepcopy(filters))
    for f in filters.values():
        f.clear()
    update_filter_list()
    update_results(WORDS)

def undo_filter():
    if filter_history:
        global filters
        filters = filter_history.pop()
        update_filter_list()
        apply_filters()

def update_filter_list():
    filters_list.delete(*filters_list.get_children())
    if filters["Not Contains"]:
        filters_list.insert("", "end", values=(
            REVERSE_FILTER_MAP["Not Contains"],
            ", ".join(sorted(filters["Not Contains"])), ""
        ))
    for pos, letter in sorted(filters["At Position"].items()):
        filters_list.insert("", "end", values=(
            REVERSE_FILTER_MAP["At Position"], letter, str(pos + 1)
        ))
    for pos, letter in sorted(filters["Not Position"].items()):
        filters_list.insert("", "end", values=(
            REVERSE_FILTER_MAP["Not Position"], letter, str(pos + 1)
        ))

def update_results(word_list):
    results_tree.delete(*results_tree.get_children())
    rows = [word_list[i:i+3] for i in range(0, len(word_list), 3)]
    for r in rows:
        results_tree.insert("", "end", values=r + [""] * (3 - len(r)))
    word_count_label.config(text=f"Words: {len(word_list)}")

def validate_letter(new_value):
    return new_value == "" or (len(new_value) == 1 and new_value.isalpha())

# --- GUI setup ---
root = tk.Tk()
root.title("Word Filter")

# --- Controls ---
inputs_frame = ttk.Frame(root, padding=(20, 0, 10, 20))
inputs_frame.grid(row=0, column=0, sticky="ew", pady=(5, 0))
inputs_frame.grid_columnconfigure(5, weight=1)

filter_type = ttk.Combobox(inputs_frame, values=list(FILTER_MAP.keys()))
filter_type.set("Gray Tile:")
filter_type.grid(row=0, column=0, padx=2, sticky="w")

vcmd = (root.register(validate_letter), "%P")
filter_value = ttk.Entry(inputs_frame, width=4, validate="key", validatecommand=vcmd)
filter_value.grid(row=0, column=1, padx=(0, 2), sticky="w")

position_frame = ttk.Frame(inputs_frame)
ttk.Label(position_frame, text="Position:").grid(row=0, column=0, padx=(0, 4))
position_value = ttk.Entry(position_frame, width=4)
position_value.grid(row=0, column=1)

def update_position_visibility(event=None):
    if filter_type.get() in ["Green Tile:", "Yellow Tile:"]:
        if not position_frame.winfo_ismapped():
            position_frame.grid(row=0, column=2, padx=2, sticky="w")
    else:
        position_frame.grid_remove()

filter_type.bind("<<ComboboxSelected>>", update_position_visibility)
update_position_visibility()

buttons_frame = ttk.Frame(inputs_frame)
buttons_frame.grid(row=0, column=6, sticky="e")
ttk.Button(buttons_frame, text="Add Filter", command=add_filter).grid(row=0, column=0, padx=2)
ttk.Button(buttons_frame, text="Clear Filters", command=clear_filters).grid(row=0, column=1, padx=2)
ttk.Button(buttons_frame, text="Undo", command=undo_filter).grid(row=0, column=2, padx=(2, 15))

# --- Filter list ---
filters_frame = ttk.Frame(root)
filters_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 5))

filters_list = ttk.Treeview(filters_frame, columns=("Type", "Value", "Pos"), show="headings", height=5)
for col in ("Type", "Value", "Pos"):
    filters_list.heading(col, text=col)
filters_list.grid(row=0, column=0, sticky="nsew")

filters_scrollbar = ttk.Scrollbar(filters_frame, orient="vertical", command=filters_list.yview)
filters_list.configure(yscrollcommand=filters_scrollbar.set)
filters_scrollbar.grid(row=0, column=1, sticky="ns")

filters_frame.grid_rowconfigure(0, weight=1)
filters_frame.grid_columnconfigure(0, weight=1)

# --- Word count ---
word_count_label = ttk.Label(root, text="Words: 0")
word_count_label.grid(row=3, column=0, sticky="w", padx=20, pady=5)

# --- Results ---
results_frame = ttk.Frame(root)
results_frame.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=(10, 0))

results_tree = ttk.Treeview(results_frame, columns=("Col1", "Col2", "Col3"), show="", height=15)
for col in ("Col1", "Col2", "Col3"):
    results_tree.column(col, anchor="center", stretch=True)
results_tree.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
results_tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

results_frame.grid_rowconfigure(0, weight=1)
results_frame.grid_columnconfigure(0, weight=1)

# --- Initial update ---
update_results(WORDS)

# --- Expandable layout ---
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=3)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
