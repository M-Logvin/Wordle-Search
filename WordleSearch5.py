import tkinter as tk
from tkinter import ttk

# --- Load words ---
with open("words.txt", "r") as f:
    WORDS = sorted([w.strip().lower() for w in f if w.strip()])

# --- Filters storage ---
filters = {
    "Contains": set(),
    "Not Contains": set(),
    "At Position": {},      # position:int -> letter:str
    "Not Position": {}      
}

filter_history = []

# --- Filtering function ---
def apply_filters():
    filtered = WORDS[:]
    
    # Contains
    for letter in filters["Contains"]:
        filtered = [w for w in filtered if letter in w]
    
    # Not Contains
    for letter in filters["Not Contains"]:
        filtered = [w for w in filtered if letter not in w]
    
    # At Position
    for pos, letter in filters["At Position"].items():
        filtered = [w for w in filtered if pos < len(w) and w[pos] == letter]

    # Not Position
    for pos, letter in filters["Not Position"].items():
        filtered = [w for w in filtered if pos < len(w) and w[pos] != letter]
    
    update_results(filtered)

# --- GUI callbacks ---
import copy

def add_filter():
    ftype = filter_type.get()
    val = filter_value.get().lower().strip()
    
    if not val:
        return

    # Save current filters to history
    filter_history.append(copy.deepcopy(filters))

    if ftype in ["Contains", "Not Contains"]:
        filters[ftype].add(val)
    elif ftype in ["At Position", "Not Position"]:
        pos = position_value.get().strip()
        try:
            p = int(pos) - 1
            filters[ftype][p] = val
        except ValueError:
            return

    filter_value.delete(0, tk.END)
    position_value.delete(0, tk.END)

    update_filter_list()
    apply_filters()


def clear_filters():
    import copy
    filter_history.append(copy.deepcopy(filters))

    # Clear all filters
    filters["Contains"].clear()
    filters["Not Contains"].clear()
    filters["At Position"].clear()
    filters["Not Position"].clear()
    
    update_filter_list()
    update_results(WORDS)

def undo_filter():
    if filter_history:
        # Restore the last filter state
        last_state = filter_history.pop()
        global filters
        filters = last_state
        update_filter_list()
        apply_filters()

def update_filter_list():
    for i in filters_list.get_children():
        filters_list.delete(i)
    
    filters_list.insert("", "end", values=("Contains", ", ".join(sorted(filters["Contains"])), ""))
    filters_list.insert("", "end", values=("Not Contains", ", ".join(sorted(filters["Not Contains"])), ""))
    
    for pos, letter in sorted(filters["At Position"].items()):
        filters_list.insert("", "end", values=("At Position", letter, str(pos+1)))
    
    for pos, letter in sorted(filters["Not Position"].items()):
        filters_list.insert("", "end", values=("Not Position", letter, str(pos+1)))


def update_results(word_list):
    for row in results_tree.get_children():
        results_tree.delete(row)
    
    sorted_words = sorted(word_list)

    rows = [sorted_words[i:i+3] for i in range(0, len(sorted_words), 3)]
    
    for r in rows:
        # Pad row if shorter than 3
        while len(r) < 3:
            r.append("")
        results_tree.insert("", "end", values=r)
    word_count_label.config(text=f"Words: {len(word_list)}")

def validate_letter(new_value):
    # Allow empty string (so user can delete) or a single letter
    if new_value == "":
        return True
    if len(new_value) > 1:
        return False
    if not new_value.isalpha():
        return False
    return True

# --- GUI setup ---
root = tk.Tk()
root.title("Word Filter")

# Controls
frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="ew")

filter_type = ttk.Combobox(frame, values=["Contains", "Not Contains", "At Position", "Not Position"])
filter_type.set("Contains")
filter_type.grid(row=0, column=0)

vcmd = (root.register(validate_letter), "%P")
filter_value = ttk.Entry(frame, width=4, validate="key", validatecommand=vcmd)
filter_value.grid(row=0, column=1)

position_value = ttk.Entry(frame, width=4)
ttk.Label(frame, text="   Position: ").grid(row=0, column=2)
position_value.grid(row=0, column=3)

ttk.Button(frame, text="Add Filter", command=add_filter).grid(row=0, column=4)
ttk.Button(frame, text="Clear Filters", command=clear_filters).grid(row=0, column=5)
ttk.Button(frame, text="Undo", command=undo_filter).grid(row=0, column=6)

# --- Filter list with scrollbar ---
filters_frame = ttk.Frame(root)
filters_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

filters_list = ttk.Treeview(filters_frame, columns=("Type", "Value", "Pos"), show="headings", height=5)
filters_list.heading("Type", text="Type:")
filters_list.heading("Value", text="Letter:")
filters_list.heading("Pos", text="Position:")
filters_list.grid(row=0, column=0, sticky="nsew")

# Scrollbar
filters_scrollbar = ttk.Scrollbar(filters_frame, orient="vertical", command=filters_list.yview)
filters_list.configure(yscroll=filters_scrollbar.set)
filters_scrollbar.grid(row=0, column=1, sticky="ns")

# Allow the Treeview to expand
filters_frame.grid_rowconfigure(0, weight=1)
filters_frame.grid_columnconfigure(0, weight=1)

# Word Count Label
word_count_label = ttk.Label(root, text="Words: 0")
word_count_label.grid(row=3, column=0, sticky="w", padx=10)

# Results
results_frame = ttk.Frame(root)
results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
results_tree = ttk.Treeview(results_frame, columns=("Col1", "Col2", "Col3"), show="")

# Center text and set width
for col in ("Col1", "Col2", "Col3"):
    results_tree.column(col, width=100, anchor="center")
results_tree.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
results_tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

results_frame.grid_rowconfigure(0, weight=1)
results_frame.grid_columnconfigure(0, weight=1)

update_results(WORDS)
root.mainloop()
