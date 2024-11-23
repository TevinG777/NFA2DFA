import customtkinter as ctk
from tkinter import messagebox
import string

class NFAtoDFAApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NFA to DFA Conversion Tool")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.geometry("600x400")
        self.number_of_symbols = 0
        self.transition_entries = []
        self.add_row_button = None
        self.submit_button = None
        self.setup_symbol_entry_page()

    def setup_symbol_entry_page(self):
        # Clear current window
        for widget in self.winfo_children():
            widget.destroy()

        # Label to prompt the user
        prompt_label = ctk.CTkLabel(self, text="Enter the number of input symbols:")
        prompt_label.pack(pady=20)

        # Entry to input the number of columns/symbols
        self.symbol_entry = ctk.CTkEntry(self)
        self.symbol_entry.pack(pady=10)

        # Button to proceed
        submit_button = ctk.CTkButton(self, text="Submit", command=self.get_number_of_symbols)
        submit_button.pack(pady=20)

    def get_number_of_symbols(self):
        try:
            self.number_of_symbols = int(self.symbol_entry.get())
            if self.number_of_symbols < 1:
                raise ValueError
            self.setup_transition_table_page()  # Move to the next page to input transitions
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive integer.")

    def setup_transition_table_page(self):
        # Clear current window
        for widget in self.winfo_children():
            widget.destroy()

        # Heading
        heading_label = ctk.CTkLabel(self, text="Input Transition Table")
        heading_label.grid(row=0, column=0, columnspan=self.number_of_symbols + 3, pady=10)

        # Create the column headers
        ctk.CTkLabel(self, text="Starting State").grid(row=1, column=0, padx=10, pady=5)
        for i in range(self.number_of_symbols):
            input_symbol = string.ascii_lowercase[i]
            ctk.CTkLabel(self, text=f"Input {input_symbol}").grid(row=1, column=i + 1, padx=10, pady=5)
        ctk.CTkLabel(self, text="Input λ").grid(row=1, column=self.number_of_symbols + 1, padx=10, pady=5)

        # Button to add rows dynamically
        self.add_row_button = ctk.CTkButton(self, text="Add Row", command=self.add_transition_row)
        self.add_row_button.grid(row=2, column=0, pady=10, sticky="w", columnspan=1)

        # Submit button
        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_transitions)
        self.submit_button.grid(row=2, column=self.number_of_symbols + 1, pady=10, sticky="e")

    def add_transition_row(self):
        row_number = len(self.transition_entries) + 3
        row_entries = []

        # Add entries for starting state and all input symbols including lambda
        starting_state_entry = ctk.CTkEntry(self)
        starting_state_entry.grid(row=row_number, column=0, padx=10, pady=5)
        row_entries.append(starting_state_entry)

        for i in range(self.number_of_symbols + 1):  # Including lambda column
            entry = ctk.CTkEntry(self)
            entry.grid(row=row_number, column=i + 1, padx=10, pady=5)
            row_entries.append(entry)

        self.transition_entries.append(row_entries)

        # Move the Add Row and Submit buttons down
        self.add_row_button.grid(row=row_number + 1, column=0, pady=10, sticky="w", columnspan=1)
        self.submit_button.grid(row=row_number + 1, column=self.number_of_symbols + 1, pady=10, sticky="e")

    def submit_transitions(self):
        nfa_symbols = set()  # Ensure nfa_symbols is defined
        transitions = []
        for row_entries in self.transition_entries:
            row_data = []
            starting_state = row_entries[0].get() if row_entries[0].get() != "" else "NULL"
            row_data.append(starting_state)
            for i in range(1, len(row_entries)):
                input_symbol = string.ascii_lowercase[i - 1] if i <= self.number_of_symbols else "λ"
                transition_state = row_entries[i].get() if row_entries[i].get() != "" else "NULL"
                row_data.append((input_symbol, transition_state))
                if transition_state == "NULL":
                    nfa_symbols.add(input_symbol)
            transitions.append(row_data)

        # Here, you can add the logic to handle the transitions and convert the NFA to DFA
        # For now, we'll just display a confirmation message
        messagebox.showinfo("Transitions Submitted", "Transition table has been submitted.")
        # Call the backend NFA to DFA conversion here
        self.perform_nfa_to_dfa_conversion(transitions)

    def lambda_closure(self, state, nfa_transitions, visited=None):
        if visited is None:
            visited = set()
        if state in visited:
            return set()

        visited.add(state)
        closure = set([state])
        if state in nfa_transitions and "λ" in nfa_transitions[state]:
            for target in nfa_transitions[state]["λ"].split(","):
                closure.update(self.lambda_closure(target.strip(), nfa_transitions, visited))
        return closure

    def perform_nfa_to_dfa_conversion(self, transitions):
        # Pull out the transitions from the input
        nfa_states = set()
        nfa_symbols = set()
        nfa_transitions = {}  # Initialize nfa_transitions with default NULL values

        # Grab each row from the transitions
        for row in transitions:
            starting_state = row[0]
            nfa_states.add(starting_state)

            # Initialize transition dictionary with NULL for all symbols
            if starting_state not in nfa_transitions:
                nfa_transitions[starting_state] = {symbol: 'NULL' for symbol in string.ascii_lowercase[:self.number_of_symbols] + 'λ'}

            # Process each symbol transition in the row
            for input_symbol, transition_state in row[1:]:
                nfa_symbols.add(input_symbol)
                if transition_state != "NULL":
                    nfa_transitions[starting_state][input_symbol] = transition_state

        # Lambda closures for each state
        lambda_closures = {state: self.lambda_closure(state, nfa_transitions, visited=set()) for state in nfa_states}

        # Start constructing DFA
        dfa_states = []
        dfa_transitions = {}
        unprocessed_states = []

        # Start with the lambda closure of the initial state
        initial_closure = frozenset(lambda_closures['q0'])
        dfa_states.append(initial_closure)
        unprocessed_states.append(initial_closure)

        # Process all unprocessed DFA states
        while unprocessed_states:
            current_dfa_state = unprocessed_states.pop(0)
            dfa_transitions[current_dfa_state] = {}

            # For each input symbol (except lambda)
            for symbol in nfa_symbols:
                if symbol == "λ":
                    continue

                # Calculate the set of NFA states reachable from the current DFA state using the symbol
                reachable_states = set()
                for nfa_state in current_dfa_state:
                    if nfa_state in nfa_transitions and symbol in nfa_transitions[nfa_state]:
                        target_states = nfa_transitions[nfa_state][symbol].split(",")
                        for target in target_states:
                            reachable_states.update(lambda_closures[target.strip()])

                reachable_closure = frozenset(reachable_states)
                dfa_transitions[current_dfa_state][symbol] = reachable_closure

                # If this new state is not already in the DFA states, add it
                if reachable_closure not in dfa_states:
                    dfa_states.append(reachable_closure)
                    unprocessed_states.append(reachable_closure)

        # Print the DFA components for verification
        print("DFA States:", dfa_states)
        print("DFA Transitions:")
        for state, transitions in dfa_transitions.items():
            print(f"  {state}: {transitions}")

    def show_dfa_table(self):
        # Placeholder for displaying DFA table after conversion
        self.setup_symbol_entry_page()  # For now, restart by going back to the first page

if __name__ == "__main__":
    app = NFAtoDFAApp()
    app.mainloop()
