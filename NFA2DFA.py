import customtkinter as ctk
from tkinter import messagebox
import string

class NFAtoDFAApp(ctk.CTk):
    def __init__(self):
        # Initialize the main window
        super().__init__()
        self.title("NFA to DFA Conversion Tool")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.number_of_symbols = 0
        self.transition_entries = []
        self.add_row_button = None
        self.submit_button = None
        
        # Initialize the DFA components page
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
        
        # try to convert the input to an integer if failed show an error message
        try:
            self.number_of_symbols = int(self.symbol_entry.get())
            if self.number_of_symbols < 1:
                raise ValueError
            # Adjust window size based on the number of symbols
            new_width = 600 + (self.number_of_symbols * 50)
            new_height = 400 + (self.number_of_symbols * 20)
            self.geometry(f"{new_width}x{new_height}")
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
        
        # Process each row of the transition table
        for row_entries in self.transition_entries:
            
            # Extract the data from the row
            row_data = []
            
            # Starting state is the first entry in the row
            starting_state = row_entries[0].get() if row_entries[0].get() != "" else "NULL"
            row_data.append(starting_state)
            
            # Process each input symbol transition in the row
            for i in range(1, len(row_entries)):
                input_symbol = string.ascii_lowercase[i - 1] if i <= self.number_of_symbols else "λ"
                transition_state = row_entries[i].get() if row_entries[i].get() != "" else "NULL"
                row_data.append((input_symbol, transition_state))
                
                # If the transition state is not NULL, add the input symbol to the set of NFA symbols
                if transition_state == "NULL":
                    nfa_symbols.add(input_symbol)
            transitions.append(row_data)

        # For now, we'll just display a confirmation message
        messagebox.showinfo("Transitions Submitted", "Transition table has been submitted.")
        # Call the backend NFA to DFA conversion here
        self.perform_nfa_to_dfa_conversion(transitions)
        self.show_dfa_table()

    # Function to calculate the lambda closure of a state in the NFA
    def lambda_closure(self, state, nfa_transitions, visited=None):
        if visited is None:
            visited = set()
        if state in visited:
            return set()

        # Add the current state to the visited set and the closure set
        visited.add(state)
        closure = set([state])
        
        # If the state has a lambda transition, add the lambda closure of the target states
        if state in nfa_transitions and "λ" in nfa_transitions[state]:
            for target in nfa_transitions[state]["λ"].split(","):
                closure.update(self.lambda_closure(target.strip(), nfa_transitions, visited))
        return closure

    def perform_nfa_to_dfa_conversion(self, transitions):
        # Define instance attributes for DFA states and transitions
        self.dfa_states = []
        self.dfa_transitions = {}
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
        self.dfa_states.append(initial_closure)
        unprocessed_states.append(initial_closure)

        # Process all unprocessed DFA states
        while unprocessed_states:
            current_dfa_state = unprocessed_states.pop(0)
            if current_dfa_state not in self.dfa_transitions:
                self.dfa_transitions[current_dfa_state] = {}

            # For each input symbol (except lambda)
            for symbol in nfa_symbols:
                if symbol == "λ":
                    continue

                # Calculate the set of NFA states reachable from the current DFA state using the symbol
                reachable_states = set()
                
                # For each NFA state in the current DFA state, find the target states for the symbol
                for nfa_state in current_dfa_state:
                    
                    # If the NFA state has a transition for the symbol, add the target states to the reachable set
                    if nfa_state in nfa_transitions and symbol in nfa_transitions[nfa_state]:
                        target_states = nfa_transitions[nfa_state][symbol].split(",")
                        for target in target_states:
                            
                            # Add the lambda closure of the target state to the reachable set
                            if target.strip() != 'NULL':
                                reachable_states.update(lambda_closures[target.strip()])

                # If there are reachable states, add the closure to the DFA transitions
                reachable_closure = frozenset(reachable_states)
                self.dfa_transitions[current_dfa_state][symbol] = reachable_closure

                # If this new state is not already in the DFA states, add it
                if reachable_closure not in self.dfa_states:
                    self.dfa_states.append(reachable_closure)
                    unprocessed_states.append(reachable_closure)

        # Print the DFA components for verification
        print("DFA States:", [f"{{{', '.join(state)}}}" if state else "{\u2205}" for state in self.dfa_states])
        print("DFA Transitions:")
        for state, transitions in self.dfa_transitions.items():
            state_str = f"{{{', '.join(state)}}}" if state else "{\u2205}"
            transitions_str = {symbol: (f"{{{', '.join(target_state)}}}" if target_state else "{\u2205}") for symbol, target_state in transitions.items()}
            print(f"  {state_str}: {transitions_str}")

    # Display the DFA transition table
    def show_dfa_table(self):
        # Clear current window
        for widget in self.winfo_children():
            widget.destroy()

        # Heading
        heading_label = ctk.CTkLabel(self, text="DFA Transition Table")
        heading_label.grid(row=0, column=0, columnspan=self.number_of_symbols + 2, pady=10)

        # Create the column headers for the DFA table
        ctk.CTkLabel(self, text="State").grid(row=1, column=0, padx=10, pady=5)
        for i, symbol in enumerate(sorted([sym for sym in self.dfa_transitions[next(iter(self.dfa_transitions))].keys() if sym != 'λ'])):
            ctk.CTkLabel(self, text=f"Input {symbol}").grid(row=1, column=i + 1, padx=10, pady=5)

        # Fill in the DFA table with states and transitions
        for row_index, (state, transitions) in enumerate(self.dfa_transitions.items(), start=2):
            state_str = f"{{{', '.join(state)}}}"
            ctk.CTkLabel(self, text=state_str).grid(row=row_index, column=0, padx=10, pady=5)
            for col_index, symbol in enumerate(sorted([sym for sym in transitions.keys() if sym != 'λ'])):
                target_state_str = f"{{{', '.join(transitions[symbol])}}}" if transitions[symbol] else "{\u2205}"
                ctk.CTkLabel(self, text=target_state_str).grid(row=row_index, column=col_index + 1, padx=10, pady=5)

        # Button to go back to the beginning
        restart_button = ctk.CTkButton(self, text="Restart", command=self.setup_symbol_entry_page)
        restart_button.grid(row=row_index + 1, column=0, columnspan=self.number_of_symbols + 2, pady=20)

if __name__ == "__main__":
    app = NFAtoDFAApp()
    app.mainloop()
