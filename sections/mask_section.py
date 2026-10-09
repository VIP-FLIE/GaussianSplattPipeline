import tkinter as tk

from gui.section_options import SectionOptions


class MaskSection(SectionOptions):
    """Collect mask options for the future masking backend."""

    def __init__(self, name, config):
        super().__init__(name, config)
        options = self.config.get_section_config(self.name)
        options.setdefault("single_mask", True)
        options.setdefault("masks_dir", "")
        options.setdefault("equirectangular", False)

    def render_options(self, parent: tk.Frame):
        self._add_dropdown(parent, "Mask mode:", "single_mask",
                           ["One mask for all photos", "Match photo names"], "One mask for all photos", width=23,
                           value_map={"One mask for all photos": True, "Match photo names": False})
        self._add_dropdown(parent, "Mask projection:", "equirectangular",
                           ["Equirectangular", "Flat"], "Flat", width=23,
                           value_map={"Equirectangular": True, "Flat": False})
        self._add_folder_selector(parent, "Select Masks Directory:", "masks_dir", dialog_title="Select Masks Directory")
