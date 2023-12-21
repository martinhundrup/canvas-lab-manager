import tkinter as tk
from tkinter import ttk
import configparser


class GuiWindow(tk.Tk):

    def __init__(self, window_size='960x1080', title='Canvas Lab Manager'):
        tk.Tk.__init__(self)
        self.title(title)
        self.geometry(window_size)
        self.progressbar = None
        return

    # Gets user entry based on number of prompts sent
    def get_user_credentials(self, prompts, default_values) -> list:
        entries = list()
        labels = list()

        # Create button
        button = tk.Button(self, text="Submit", command=self.quit)
        button.pack()

        # Create prompts and entries
        for ind, val in enumerate(prompts):
            labels.append(tk.Label(self, text=val))
            entries.append(tk.Entry(self, width=80))
            entries[-1].insert(tk.END, default_values[ind])
            labels[ind].pack()
            entries[ind].pack()

        # Run window
        self.mainloop()

        # Put user entries into a list to return
        response = list()
        for user_entry in entries:
            response.append(user_entry.get())

        # Clear out window
        self._clear_window()
        return response

    def get_course_selection(self, courses: dict) -> str:
        r_button = tk.StringVar()
        button = tk.Button(self, text="Submit", command=lambda: self.quit() if r_button.get() != '' else self.quit())
        button.pack()

        for key in courses.keys():
            r1 = tk.Radiobutton(self, text=key, variable=r_button, value=key)
            r1.pack()
            for val in courses[key]:
                label = tk.Label(self, text=val)
                label.pack()

        self.mainloop()
        selection = r_button.get()
        self._clear_window()
        return selection

    def get_action_selection(self) -> str:
        r_button = tk.StringVar()
        button = tk.Button(self, text="Submit", command=lambda: self.quit() if r_button.get() != '' else self.quit())
        button.pack()

        button_texts = ["Create Gradebook", "Download Submissions", "Run MOSS",
                        "Generate Cheating SpreadSheet",
                        "Generate Grading Status", "Generate Late Status", "Switch Course",
                        "Exit"]
        button_values = ["create_gradebook", "download_submissions", "run_moss",
                         "generate_cheating_spreadsheet",
                         "grading_status", "late_status", "switch_course",
                         "exit"]

        for ind in range(len(button_texts)):
            r = tk.Radiobutton(self, text=button_texts[ind], variable=r_button, value=button_values[ind])
            r.pack()

        self.mainloop()
        selection = r_button.get()
        self._clear_window()
        return selection

    def get_assignment_selection(self, assignment_list: list) -> list:
        button = tk.Button(self, text="Submit", command=self.quit)
        button.pack()

        check_buttons = list()
        variables = list()

        for assignment_name in assignment_list:
            variables.append(tk.StringVar())
            check_buttons.append(tk.Checkbutton(self,
                                                     text=assignment_name,
                                                     onvalue=True,
                                                     offvalue=False,
                                                     variable=variables[-1]))
            check_buttons[-1].deselect()
            check_buttons[-1].pack()

        self.mainloop()
        selection = list()
        for ind, val in enumerate(variables):
            if val.get() == '1':
                selection.append(assignment_list[ind])
        self._clear_window()
        return selection

    def set_progress_bar(self, step: float, reset: bool = False) -> None:
        if self.progressbar is None:
            self.progressbar = ttk.Progressbar(orient=tk.HORIZONTAL, length=420)
            self.progressbar.pack()
        if reset:
            self._clear_window()
            self.progressbar = None
        else:
            self.progressbar.step(step)
        self.update_idletasks()
        return

    # Used to clear out all elements of a window instead of destroying it
    def _clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
        return


class SelectAssignments(tk.Tk):

    def __init__(self, assignments: list):
        tk.Tk.__init__(self)



class BetterConfig:
    def __init__(self, config_name):
        self.config_name = config_name
        self.config = configparser.ConfigParser()
        self.config.read(config_name)
        return

    def get(self, key, default_value):
        if self.config.has_option('settings', key):
            param = self.config.get('settings', key)
        else:
            param = default_value

        return param

    def set(self, key, value):
        if not self.config.has_section('settings'):
            self.config.add_section('settings')
        self.config.set('settings', key, value)

        # Save to config
        with open(self.config_name, 'w') as configfile:
            self.config.write(configfile)
        return
