import tkinter as tk
import numpy as np
from capyle.guicomponents import (_ConfigUIComponent, _Separator,
                                  _EditInitialGridWindow)

from ca_descriptions.fireutils.firefunctions import get_additional_funcs

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
        editframe = tk.Frame(optionsframe)
        # rdo_edit = tk.Radiobutton(editframe, text="Edit preset",
                                #   variable=self.selected, value=2)
        btn_edit = tk.Button(editframe, text="Set Default Initial!",
                             command=lambda: self.set_initial_initial())

        for (name, func) in get_additional_funcs():
            btn_add = tk.Button(editframe, text=name,
                             command=lambda f=func: f(self.ca_config))
            btn_add.pack()
            
        
        # rdo_edit.pack(side=tk.LEFT)
        btn_edit.pack(side=tk.LEFT)
        editframe.pack(fill=tk.BOTH)

        # Pack options
        optionsframe.pack()

        # Keep handles on the radio buttons for external use
        self.radiobuttons = [rdo_proportions, rdo_custom, rdo_centercell]
        self.set_default()

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
