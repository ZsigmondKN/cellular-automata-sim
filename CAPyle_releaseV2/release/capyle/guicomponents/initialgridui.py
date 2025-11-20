import tkinter as tk
from tkinter import ttk
import numpy as np
from capyle.guicomponents import (_ConfigUIComponent, _Separator,
                                  _EditInitialGridWindow)

from ca_descriptions.fireutils.firefunctions import get_additional_ember_set, get_additional_funcs, get_additional_wind_dir

class _InitialGridUI(tk.Frame, _ConfigUIComponent):

    def __init__(self, parent, ca_config):
        """UI element to customise the initial grid"""
        # superclasses
        tk.Frame.__init__(self, parent)
        _ConfigUIComponent.__init__(self)

        self.parent = parent
        self.ca_config = ca_config

        labelframe = tk.Frame(self)
        label = tk.Label(labelframe, text="Initial grid:")
        label.pack(side=tk.LEFT)
        labelframe.pack(fill=tk.BOTH)

        self.selected = tk.IntVar()
        optionsframe = tk.Frame(self)

        # --- Center cell option (for 1D CA)
        rdo_centercell = None
        if self.ca_config.dimensions == 1:
            centerframe = tk.Frame(optionsframe)
            rdo_centercell = tk.Radiobutton(centerframe, text="Center cell",
                                            variable=self.selected, value=3,
                                            command=self.set_centercell)
            rdo_centercell.pack(side=tk.LEFT)
            centerframe.pack(fill=tk.BOTH)

        # --- Proportions option
        propframe = tk.Frame(optionsframe)
        rdo_proportions = tk.Radiobutton(propframe, text="% Initialised",
                                         variable=self.selected, value=0)
        btn_proportions = tk.Button(propframe, text="Edit",
                                    command=lambda: self.editinitgrid(proportions=True))
        rdo_proportions.pack(side=tk.LEFT)
        btn_proportions.pack(side=tk.LEFT)
        propframe.pack(fill=tk.BOTH)

        # --- Custom option
        customframe = tk.Frame(optionsframe)
        rdo_custom = tk.Radiobutton(customframe, text="Custom",
                                    variable=self.selected, value=1)
        btn_custom = tk.Button(customframe, text="Edit",
                               command=lambda: self.editinitgrid(custom=True))
        rdo_custom.pack(side=tk.LEFT)
        btn_custom.pack(side=tk.LEFT)
        customframe.pack(fill=tk.BOTH)

        # --- Edit preset button
        _Separator(optionsframe).pack(fill=tk.X, pady=5)
        labelframe = tk.Frame(optionsframe)
        label = tk.Label(labelframe, text="Grid Setup Options:")
        label.pack(side=tk.LEFT)
        labelframe.pack(fill=tk.BOTH)


        editframe = tk.Frame(optionsframe)
        self.grid_selected = tk.StringVar(value="")  # no default selection
        style = ttk.Style()
        style.configure("Grid.TButton", relief="raised")
        style.map("Grid.TButton", relief=[("selected", "sunken")])
        
        for name, func in get_additional_funcs():
            rb = ttk.Radiobutton(editframe, text=name, value=name, variable=self.grid_selected, style="Grid.TButton",
                command=lambda f=func: (self.set_initial_initial(), f(self.ca_config)))
            rb.pack(side=tk.LEFT, padx=2)

        editframe.pack(fill=tk.BOTH)

        # Pack options
        optionsframe.pack()

        windoptionsframe = tk.Frame(self)
        _Separator(windoptionsframe).pack(fill=tk.X, pady=5)

        labelframe = tk.Frame(windoptionsframe)
        label = tk.Label(labelframe, text="Wind Direction Options:")
        label.pack(side=tk.LEFT)
        labelframe.pack(fill=tk.BOTH)

        editWind = tk.Frame(windoptionsframe)

        buttons = list(get_additional_wind_dir(self.ca_config))
        half = (len(buttons) + 1) // 2

        self.wind_selected = tk.StringVar(value="N to S") # Default selection

        style = ttk.Style()
        style.configure("Wind.TButton", relief="raised")
        style.map("Wind.TButton",
                relief=[("selected", "sunken")])

        # Row 1
        row1 = tk.Frame(editWind)
        for name, func in buttons[:half]:
            rb = ttk.Radiobutton(row1, text=name, value=name, variable=self.wind_selected, style="Wind.TButton",
                command=lambda f=func: f(self.ca_config))
            rb.pack(side=tk.LEFT, padx=3, pady=2)
        row1.pack(anchor="w")

        # Row 2
        row2 = tk.Frame(editWind)
        for name, func in buttons[half:]:
            rb = ttk.Radiobutton(row2, text=name, value=name, variable=self.wind_selected, style="Wind.TButton",
                command=lambda f=func: f(self.ca_config))
            rb.pack(side=tk.LEFT, padx=3, pady=2)
        row2.pack(anchor="w")

        editWind.pack(fill=tk.BOTH)
        windoptionsframe.pack()

        emberOptionsframe = tk.Frame(self)
        _Separator(emberOptionsframe).pack(fill=tk.X, pady=5)
        labelframe = tk.Frame(emberOptionsframe)
        label = tk.Label(labelframe, text="Enable Embers:")
        label.pack(side=tk.LEFT)
        labelframe.pack(fill=tk.BOTH)

        editember = tk.Frame(emberOptionsframe)
        self.ember_selected = tk.StringVar(value="Disable Embers") # Default selection
        style = ttk.Style()
        style.configure("Ember.TButton", relief="raised")
        style.map("Ember.TButton", relief=[("selected", "sunken")])
        for name, func in get_additional_ember_set(self.ca_config):
            rb = ttk.Radiobutton(editember, text=name, value=name, variable=self.ember_selected, style="Ember.TButton",
                command=lambda f=func: f(self.ca_config))
            rb.pack(side=tk.LEFT, padx=2)
        editember.pack(fill=tk.BOTH)

        emberOptionsframe.pack()

        # Keep handles on the radio buttons for external use
        self.radiobuttons = [rdo_proportions, rdo_custom, rdo_centercell]
        self.set_default()

    def apply_button_changes(self):
        # Apply wind direction
        wind_choice = self.wind_selected.get()
        for name, func in get_additional_wind_dir(self.ca_config):
            if name == wind_choice:
                func(self.ca_config)
                break

        # Apply ember setting
        ember_choice = self.ember_selected.get()
        for name, func in get_additional_ember_set(self.ca_config):
            if name == ember_choice:
                func(self.ca_config)
                break

    def update_config(self, ca_config):
        """Update configuration reference"""
        self.ca_config = ca_config

    def get_value(self):
        """Return selected mode index"""
        return int(self.selected.get())

    def set_default(self):
        """Set default mode depending on dimensions"""
        if self.ca_config.dimensions == 2:
            # Default: proportions for 2D
            self.set(0)
        else:
            # Default: center cell for 1D
            self.set(3)
            self.set_centercell()

    def set(self, index):
        """Select given mode"""
        self.selected.set(index)

    def set_centercell(self):
        """Set a 1D grid with center cell active"""
        new_row = np.zeros((1, self.ca_config.grid_dims[1]))
        center = int(self.ca_config.grid_dims[1] / 2)
        new_row[0, center] = 1
        self.ca_config.set_initial_grid(new_row)

    def set_initial_initial(self):
        self.ca_config.initial_grid = self.ca_config.initial_initial_grid

    def editinitgrid(self, proportions=False, custom=False, edit=False):
        """Open the grid editing window in the selected mode"""
        # Prepare grid dimensions
        if self.ca_config.dimensions == 2:
            self.ca_config.set_grid_dims(
                dims=self.parent.griddims_entry.get_value())
        else:
            self.ca_config.set_grid_dims(
                num_generations=self.parent.generations_entry.get_value())

        # Select the correct radio option
        if proportions:
            self.selected.set(0)
        elif custom:
            self.selected.set(1)
        elif edit:
            self.selected.set(2)

        # Open the grid editor window
        editwindow = _EditInitialGridWindow(
            self.ca_config,
            proportions=proportions,
            custom=custom,
            edit=edit
        )
