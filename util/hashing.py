import pickle
import hashlib
import pathlib

from os.path import isfile, join, isdir


class SavedRuns:

    def __init__(self, file_name: str) -> None:
        self.runs_file = '.saved_runs.pkl'
        self.file_name = file_name
        self.saved_runs = None
        self.file_hash = None
        return

    # Returns True if hash is same as last computation, else return false
    def check_hash(self) -> bool:
        # Generate hash if not yet computed
        if self.file_hash is None:
            self.file_hash = self.get_md5()

        # Create empty dict if it failed to load
        if self.saved_runs is None:
            self.load_saved_runs()

        # Check for any saved runs
        if self.saved_runs is None:
            return False

        # Check for file_name in saved runs
        if self.file_name not in self.saved_runs:
            return False

        # Check hash is same as last
        if self.saved_runs[self.file_name] != self.file_hash:
            return False

        return True

    # Loads dictionary of saved runes from file
    def load_saved_runs(self) -> None:
        try:
            with open(self.runs_file, 'rb') as f:
                self.saved_runs = pickle.load(f)
        except FileNotFoundError as e:
            self.saved_runs = dict()
        return

    # Saves dictionary of saved runes from file
    def save_saved_runs(self) -> None:
        with open(self.runs_file, 'wb') as f:
            pickle.dump(self.saved_runs, f)
        return

    # Generates the MD5SUM of a file / dir
    def get_md5(self) -> str:
        # hash object
        hash_md5 = hashlib.md5()

        # When file name is a file
        if isfile(self.file_name):
            with open(self.file_name, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)

        # When file name is a directory, recurse through all files
        elif isdir(self.file_name):
            for path in pathlib.Path(self.file_name).rglob('*.'):
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)

        return hash_md5.hexdigest()

    # Save current file_name / hash pairing to file
    def save_hash(self) -> None:
        # Generate hash if not yet computed
        if self.file_hash is None:
            self.file_hash = self.get_md5()

        # Create empty dict if it failed to load
        if self.saved_runs is None:
            self.load_saved_runs()

        # Update hashed results
        self.saved_runs[self.file_name] = self.file_hash

        # Save to file
        self.save_saved_runs()

        return
