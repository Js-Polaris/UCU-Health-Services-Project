""" What this screen allows the user to do:
1. Select a branch
2. Select a medicine 
3. Enter the quantity received 
4. Click the receive stock button
5. See th updated stock for that branch"""

#tkinter is a python library used ot creat graphical user interfaces
#ttk provides themed widgets, e.g. styled buttons, and frames
import tkinter as tk
from tkinter import ttk

#importing classes 
from services.branch_service import BranchService
from services.medicine_service import MedicineService
from services.stock_service import StockService

#screen_title creates the heading of the screen
#form_section creates a section containing the form
#table_section creats a section containing the table
#make_expandable allows the screen to expand when the window is resized 
from templates.layouts import (
    form_section, make_expandable, screen_title, table_section,
)

#labelled_combobox creats a dropdown with label 
#labelled_entry creates a text input with a label
#button_bar creates buttons
#data_table creats a table
#populate_table inserts information into a table 
from templates.widgets import (
    button_bar, data_table, labelled_combobox, labelled_entry, populate_table, show_error, show_info
)

#_whole_number is intended for internal use only hence the leading underscore
def _whole_number(text, field_name):
    try:
        #the input is turned into an integer
        return int(str(text).strip())
    except (TypeError, ValueError):
        #from None is used to hide the original error traceback, it tells python to discard the context and show only the new exception
        raise ValueError(f"{field_name} must be a whole number") from None

class ReceiveStockView(ttk.Frame):
    #the constructor (a method that runs automatically when an object is created)
    def __init__(self, parent, conn):
        #parent tells tkinter where to place the fram, while padding  = 4 adds some internal spacing
        super().__init__(parent, padding = 4)
        self._service = StockService(conn)
        #help with retrieving the available branches and medicines
        branches = BranchService(conn)
        medicines = MedicineService(conn)

        self._branch_options = {
            #the display text
            #b.branch_id stores the actual ID as the dictionary value
            f"{b.branch_id} - {b.name}": b.branch_id
            #retrieving all branches and loops through them
            for b in branches.list_all()
        }

        self._medicine_options = {
            f"{m.code} - {m.name}": m.code
            for m in medicines.list_all()
        }

        #StringVar creates a tkinter variable that can store a string and communicate with GUI widgets
        #we are storing the selected branch, selected medicine, and quantity entered
        self._branch_var = tk.StringVar()
        self._medicine_var = tk.StringVar()
        self._quantity_var = tk.StringVar()

        self._build()
        #trace_add allows monitoring changes to a Tkinter variable
        #"write" is for detecting when the variable's value changes, if so the next section is executed
        # Refresh the table whenever a different branch is chosen.
        self._branch_var.trace_add("write", self._on_branch_changed)
        #checks if the dictionary is empty, creates an iterator over the keys, retrieve the first key, makes the branch the default selection
        if self._branch_options:
            self._branch_var.set(next(iter(self._branch_options)))
        if self._medicine_options:
            self._medicine_var.set(next(iter(self._medicine_options)))
        self.refresh_table()


    def _build(self):
        #row = 0 specifies its position in the grid layout
        screen_title(self, "Receive Stock", row = 0)

        form = form_section(self, "New Stock Receipt", row = 1)
        labelled_combobox(
            #the frame, label, row position
            form, "Branch", 0, list(self._branch_options),
            #connects the dropdown to the Tkinter variable
            variable = self._branch_var,
        )

        #displaying the available medicines
        labelled_combobox(
            form, "Medicine", 1, list(self._medicine_options),
            variable = self._medicine_var,
        )

        labelled_entry(
            form, "Quantity to add", 2, variable=self._quantity_var
        )

        #creating the buttons
        button_bar(form, [
            #self._on_receive as a callback because it only needs to execute when the user clicks the button
            ("Receive stock", self._on_receive),
            ("Clear quantity", self._clear_quantity),
        ], row = 3)

        table_frame = table_section(
            self, "Stock at the selected branch", row = 2
        )

        self._table = data_table(table_frame, [
            ("Medicine code", "code", 150),
            ("Quantity", "qty", 120),
        ])

        #allowing expansion when the window is resized
        make_expandable(self, row = 2)


    #having the stock table automatically updated whenever the user selects a different branch
    #*args allows a function to accept any number of positional arguments 
    def _on_branch_changed(self, *_args):
        self.refresh_table()

    def _on_receive(self):
        try:
            #branch_var is the tkinter variable connected to the branch dropdown, so get() retrieves whatever the user selected
            branch_id = self._branch_options.get(self._branch_var.get())
            medicine_code = self._medicine_options.get(self._medicine_var.get())

            #checking whether a branch was selected
            if branch_id is None:
                raise ValueError("Select a branch")

            if medicine_code is None:
                raise ValueError("Select a medicine")

            quantity = _whole_number(self._quantity_var.get(), "Quantity")
            self._service.receive(branch_id, medicine_code, quantity)

        except Exception as exc:
            #exc represents the exception that occured
            show_error(str(exc))
            #return stops the method from continuing 
            return

        #displaying a success message to the user if there are no errors
        show_info("Stock Received")
        #clears the quantity entry field
        self._clear_quantity()
        #refreshes the stock table so the updated quantities can be seen
        self.refresh_table()

    def _clear_quantity(self):
        self._quantity_var.set("")

    def refresh_table(self):
        branch_id = self._branch_options.get(self._branch_var.get())
        if branch_id is None:
            populate_table(self._table, [])
            #stops the method because there is no stock to retrieve from the branch
            return
        #retrieving stock records associated with the selected branch
        items = self._service.list_for_branch(branch_id)
        #looping through every stock item, and creating a list containing the medicine code and quantity
        populate_table(self._table, [
            (item.medicine_code, item.quantity) for item in items 
        ])