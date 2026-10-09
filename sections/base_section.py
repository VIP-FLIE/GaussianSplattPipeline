from abc import ABC, abstractmethod
import tkinter as tk
from typing import List
from gui.section_options import SectionOptions


class PipelineSection(SectionOptions, ABC):
    """Base class for executable pipeline sections."""
    @abstractmethod
    def render_options(self, parent: tk.Frame):
        """
        Draw the configuration widgets for this section into `parent`.
        Should verify if config keys exist, if not, set defaults.
        """
        pass

    def set_paths(self, input_path: str, output_path: str):
        """Called by PipelineManager to inject chained paths."""
        """TODO: Look into the above"""
        self.input_path = input_path
        self.output_path = output_path
        
        # We also update the config so the GUI (if open) reflects this, 
        # or at least so the build_command can find it.
        self.config.update_section_config(self.name, "input_dir", input_path)
        self.config.update_section_config(self.name, "output_dir", output_path)

    @abstractmethod
    def build_command(self, settings: dict) -> List[str]:
        """
        Constructs the strict command line arguments string list.
        e.g., ['python', 'script.py', '--input', '...']
        Requires reading from self.config (or self.widget_vars if they are synced).
        """
        pass

    def validate(self) -> bool:
        """
        Override this to check if necessary inputs exist (files, paths)
        before running.
        """
        return True
