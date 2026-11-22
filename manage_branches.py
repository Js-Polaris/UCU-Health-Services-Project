import tkinter as tk
from tkintrt import ttk
from services.branch_service import BranchService #this reads/writes branches in SQLite for us.
from templates.layouts import (form_selcetion, make_expandable, screen_title, table_section, ) 
from templates.widgets import (
    button_bar, clear_variables, data_table, labelled_entry, populate_table, show_error, show_info,

)

class ManageBranchesView(ttk,Frame):
    def __init__(self, parent, conn): 
        super().__init__(parent,padding = 4)
        self._service = BranchService(conn) #_service (private by convention) so other methods can use it.
        self.name_var = tk.StringVar() #StringVar is a tkinter variable that stays linked to a text box: we add _var because tkk.Frame already uses self._name internally
        self._build() #build all the widgets (title, form, buttons, table)
        self.refresh_table() #loading the branches from the database and show them in the table at start-up


    def _build(self):
        screen_title(self, "Manage Branches", row = 0) #heading
        form = form_selection(self, "New Branch", row=1) #creating titled box ("New branch") at row 1 to hold the input form. Form is the container that contains the form widgets 
        labelled_entry(form, "Branch Name", 0, variable=self._name_var) #to read what the user inputs
        button_far(form, [
              ("Add branch", self._on_add),
              ("Clear form", self._clear_form),
              ("Refresh list", self.refresh_table), #reloads the table from the database
        ] row = 1)
        table_frame = table_section(self, "Branches", row=2) #Building a table 
        self._table = data_table(table_frame[
            ("ID", "id", 80),
            ("Name", "name", 260),
        ])
        make_expandable(self, row=2)


    def _on_add(self):
        try:
            self._service.add(self._name_var.get()) #reading the text from the box (.get()) and ask the service to add the branch.
        except Exception as exc:
            show_error(str(exc)) #show the error text in pop-up exactly as received
            return 
        show_info("Branch added")#message if successfully
        clear_variables([self.name_var]) #clear/emoty the table for new entry of branch
        self.refresh_table()

#for a user ro clear form 
    def _clear_form(self):
        clear_variables([self.name_name_var])


    def refresh_table(self):
        populate_table(self._table, [
            (branch.branch_id, branch.name)
            for branch in self._service.list_all() #asking the service for every branch saved i SQLite, one branch at a time.
        ])

