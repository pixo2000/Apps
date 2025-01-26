import customtkinter as ctk

# Initialize the main window
root = ctk.CTk()
root.title("CustomTkinter GUI")

# Create text fields
entry1 = ctk.CTkEntry(root, width=200)
entry2 = ctk.CTkEntry(root, width=200)
entry3 = ctk.CTkEntry(root, width=200)
entry4 = ctk.CTkEntry(root, width=200)
entry5 = ctk.CTkEntry(root, width=200)
entry6 = ctk.CTkEntry(root, width=200)

# Place text fields in a grid
entry1.grid(row=0, column=0, padx=10, pady=10)
entry2.grid(row=0, column=1, padx=10, pady=10)
entry3.grid(row=0, column=2, padx=10, pady=10)
entry4.grid(row=1, column=0, padx=10, pady=10)
entry5.grid(row=1, column=1, padx=10, pady=10)
entry6.grid(row=1, column=2, padx=10, pady=10)

# Function to set the content of a text field
def set_entry_content(entry, content):
    entry.delete(0, ctk.END)
    entry.insert(0, content)

# Function to get the content of a text field
def get_entry_content(entry):
    return entry.get()

# Example usage
set_entry_content(entry1, "Example 1")
set_entry_content(entry2, "Example 2")
set_entry_content(entry3, "Example 3")
set_entry_content(entry4, "Example 4")
set_entry_content(entry5, "Example 5")
set_entry_content(entry6, "Example 6")

def run_gui():
    # Run the main loop
    root.mainloop()