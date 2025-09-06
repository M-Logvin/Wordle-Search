import tkinter as tk
from tkinter import ttk

# --- Load words ---
with open("words.txt", "r") as f:
    WORDS = sorted([w.strip().lower() for w in f if w.strip()])

# --- Filters storage ---
filters = {
    "Not Contains": set(), #grey tile
    "At Position": {},     #green tile 
    "Not Position": {}     #yellow tile 
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
    filtered = WORDS[:]
    
    # Contains
    #for letter in filters["Contains"]:
    #    filtered = [w for w in filtered if letter in w]
    
    # Not Contains
    for letter in filters["Not Contains"]:
        filtered = [w for w in filtered if letter not in w]
    
    # At Position
    for pos, letter in filters["At Position"].items():
        filtered = [w for w in filtered if pos < len(w) and w[pos] == letter]

    # Not Position
    for pos, letter in filters["Not Position"].items():
        filtered = [w for w in filtered if letter in w and (pos >= len(w) or w[pos] != letter)]
    
    # Update results
    update_results(filtered)

# --- GUI callbacks ---
import copy

def add_filter():
    gui_choice = filter_type.get()
    ftype = FILTER_MAP.get(gui_choice, gui_choice)
    val = filter_value.get().lower().strip()
    
    if not val:
        return

    # Save current filters to history
    filter_history.append(copy.deepcopy(filters))

    if ftype == "Not Contains":
        filters[ftype].add(val)
    elif ftype in ["At Position", "Not Position"]:
        pos = position_value.get().strip()
        try:
            p = int(pos) - 1
            filters[ftype][p] = val
        except ValueError:
            return

    # Clear inputs
    filter_value.delete(0, tk.END)
    position_value.delete(0, tk.END)

    update_filter_list()
    apply_filters()


def clear_filters():
    import copy
    filter_history.append(copy.deepcopy(filters))

    # Clear all filters
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
    # Clear old entries
    for i in filters_list.get_children():
        filters_list.delete(i)

    # Not Contains (Exclude Letter)
    if filters["Not Contains"]:
        filters_list.insert(
            "",
            "end",
            values=(
                REVERSE_FILTER_MAP["Not Contains"],
                ", ".join(sorted(filters["Not Contains"])),
                ""
            )
        )

    # At Position (Letter at Position)
    for pos, letter in sorted(filters["At Position"].items()):
        filters_list.insert(
            "",
            "end",
            values=(
                REVERSE_FILTER_MAP["At Position"],
                letter,
                str(pos + 1)
            )
        )

    # Not Position (Letter not at Position)
    for pos, letter in sorted(filters["Not Position"].items()):
        filters_list.insert(
            "",
            "end",
            values=(
                REVERSE_FILTER_MAP["Not Position"],
                letter,
                str(pos + 1)
            )
        )



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

# --- Controls (replace your existing controls section with this) ---
inputs_frame = ttk.Frame(root, padding=(20, 0, 10, 20))
inputs_frame.grid(row=0, column=0, sticky="ew", pady=(5, 0))

# columns:
# 0: filter_type
# 1: filter_value
# 2: position_frame (hidden initially)
# 3: length label
# 4: length combobox
# 5: spacer (expands)
# 6: buttons (right aligned)
inputs_frame.grid_columnconfigure(5, weight=1)  # spacer expands to push buttons right

# --- Filter type combobox (create before binding) ---
filter_type = ttk.Combobox(
    inputs_frame,
    values=["Gray Tile:", "Green Tile:", "Yellow Tile:"]
)
filter_type.set("Gray Tile:")
filter_type.grid(row=0, column=0, padx=2, sticky="w")

# --- Single-letter entry (validate function should already exist) ---
vcmd = (root.register(validate_letter), "%P")  # reuse your validate_letter
filter_value = ttk.Entry(inputs_frame, width=4, validate="key", validatecommand=vcmd)
filter_value.grid(row=0, column=1, padx=(0, 2), sticky="w")

# --- Position frame (create but DO NOT grid its contents at startup) ---
position_frame = ttk.Frame(inputs_frame)   # this frame will be shown/hidden as a whole
position_label = ttk.Label(position_frame, text="Position:")
position_value = ttk.Entry(position_frame, width=4)
# place the label & entry inside the position_frame (they are NOT gridded into inputs_frame)
position_label.grid(row=0, column=0, padx=(0,4))
position_value.grid(row=0, column=1)

# --- Function to show/hide the position_frame ---
def update_position_visibility(event=None):
    choice = filter_type.get()
    if choice in ["Green Tile:", "Yellow Tile:"]:
        if not position_frame.winfo_ismapped():
            position_frame.grid(row=0, column=2, padx=2, sticky="w")
    else:
        position_frame.grid_remove()


# Bind AFTER combobox is created
filter_type.bind("<<ComboboxSelected>>", update_position_visibility)

# Ensure initial state is hidden (call once)
update_position_visibility()



# --- Buttons (right aligned) ---
buttons_frame = ttk.Frame(inputs_frame)
buttons_frame.grid(row=0, column=6, sticky="e")  # stays right because column 5 expands

ttk.Button(buttons_frame, text="Add Filter", command=add_filter).grid(row=0, column=0, padx=2)
ttk.Button(buttons_frame, text="Clear Filters", command=clear_filters).grid(row=0, column=1, padx=2)
ttk.Button(buttons_frame, text="Undo", command=undo_filter).grid(row=0, column=6, padx=(2, 15))





# --- Filter list with scrollbar ---
filters_frame = ttk.Frame(root)
filters_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 5))

filters_list = ttk.Treeview(filters_frame, columns=("Type", "Value", "Pos"), show="headings", height=5)
filters_list.heading("Type", text="Type")
filters_list.heading("Value", text="Letter")
filters_list.heading("Pos", text="Position")
filters_list.grid(row=0, column=0, sticky="nsew")

filters_scrollbar = ttk.Scrollbar(filters_frame, orient="vertical", command=filters_list.yview)
filters_list.configure(yscroll=filters_scrollbar.set)
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
    results_tree.column(col, width=0, anchor="center", stretch=True)
results_tree.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
results_tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

results_frame.grid_rowconfigure(0, weight=1)
results_frame.grid_columnconfigure(0, weight=1)

# --- Initial update ---
update_results(WORDS)
# --- Make window dynamically expandable ---
root.grid_rowconfigure(1, weight=1)   # filters_frame row
root.grid_rowconfigure(2, weight=3)   # results_frame row
root.grid_columnconfigure(0, weight=1)

results_frame.grid_rowconfigure(0, weight=1)
results_frame.grid_columnconfigure(0, weight=1)

root.mainloop()

