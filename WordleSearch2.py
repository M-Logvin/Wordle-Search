import tkinter as tk
from tkinter import ttk

# --- Load words ---
with open("words.txt", "r") as f:
    WORDS = [w.strip().lower() for w in f if w.strip()]

# --- Filters storage ---
filters = {
    "Contains": set(),
    "Not Contains": set(),
    "At Position": {}  # position:int -> letter:str
}

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
    
    update_results(filtered)

# --- GUI callbacks ---
def add_filter():
    ftype = filter_type.get()
    val = filter_value.get().lower().strip()
    
    # Ignore empty values
    if not val:
        return

    if ftype in ["Contains", "Not Contains"]:
        # Just add the letter/substring to the set
        filters[ftype].add(val)
    elif ftype == "At Position":
        # Only use the position field for At Position
        pos = position_value.get().strip()
        try:
            p = int(pos) - 1  # convert to 0-based index
            filters[ftype][p] = val
        except ValueError:
            # Invalid position entered, ignore
            return

    # Clear input fields for convenience
    filter_value.delete(0, tk.END)
    position_value.delete(0, tk.END)

    # Update filter list and results
    update_filter_list()
    apply_filters()


def clear_filters():
    filters["Contains"].clear()
    filters["Not Contains"].clear()
    filters["At Position"].clear()
    update_filter_list()
    update_results(WORDS)

def update_filter_list():
    for i in filters_list.get_children():
        filters_list.delete(i)
    
    # Combine Contains and Not Contains letters into one string
    filters_list.insert("", "end", values=("Contains", ", ".join(sorted(filters["Contains"])), ""))
    filters_list.insert("", "end", values=("Not Contains", ", ".join(sorted(filters["Not Contains"])), ""))
    
    # At Position: one row per position
    for pos, letter in sorted(filters["At Position"].items()):
        filters_list.insert("", "end", values=("At Position", letter, str(pos+1)))

def update_results(word_list):
    results.delete("1.0", tk.END)
    for w in word_list:
        results.insert(tk.END, w + "\n")

# --- GUI setup ---
root = tk.Tk()
root.title("Word Filter")

# Controls
frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="ew")

filter_type = ttk.Combobox(frame, values=["Contains", "Not Contains", "At Position"])
filter_type.set("Contains")
filter_type.grid(row=0, column=0)

filter_value = ttk.Entry(frame, width=10)
filter_value.grid(row=0, column=1)

position_value = ttk.Entry(frame, width=5)
position_value.grid(row=0, column=2)
ttk.Label(frame, text="(Position for 'At Position')").grid(row=0, column=3)

ttk.Button(frame, text="Add Filter", command=add_filter).grid(row=0, column=4)
ttk.Button(frame, text="Clear Filters", command=clear_filters).grid(row=0, column=5)

# Filter list
filters_list = ttk.Treeview(root, columns=("Type", "Value", "Pos"), show="headings", height=5)
filters_list.heading("Type", text="Type")
filters_list.heading("Value", text="Value")
filters_list.heading("Pos", text="Pos")
filters_list.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

# Results
results = tk.Text(root, height=15, width=40)
results.grid(row=2, column=0, padx=10, pady=10)

update_results(WORDS)
root.mainloop()
