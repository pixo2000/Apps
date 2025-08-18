import customtkinter as ctk

# Initialize the main window
root = ctk.CTk()
root.title("CustomTkinter GUI")

# Create labels for headings
overworld_label = ctk.CTkLabel(root, text="Overworld")
nether_label = ctk.CTkLabel(root, text="Nether")

# Create text fields with placeholders
overworld_x = ctk.CTkEntry(root, width=50, placeholder_text="X")
overworld_y = ctk.CTkEntry(root, width=50, placeholder_text="Y")
overworld_z = ctk.CTkEntry(root, width=50, placeholder_text="Z")
nether_x = ctk.CTkEntry(root, width=50, placeholder_text="X")
nether_y = ctk.CTkEntry(root, width=50, placeholder_text="Y")
nether_z = ctk.CTkEntry(root, width=50, placeholder_text="Z")

# Place labels and text fields in a grid
overworld_label.grid(row=0, column=0, padx=10, pady=10, columnspan=3)
overworld_x.grid(row=1, column=0, padx=10, pady=10)
overworld_y.grid(row=1, column=1, padx=10, pady=10)
overworld_z.grid(row=1, column=2, padx=10, pady=10)
nether_label.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
nether_x.grid(row=3, column=0, padx=10, pady=10)
nether_y.grid(row=3, column=1, padx=10, pady=10)
nether_z.grid(row=3, column=2, padx=10, pady=10)

def run_gui():
    # Run the main loop
    root.mainloop()


if __name__ == '__main__':
    run_gui()