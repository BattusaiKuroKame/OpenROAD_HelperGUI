import sys
import os
import shutil
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt

class PDKManagerApp(QWidget):

    def is_ubuntu(self):
        try:
            with open("/etc/os-release") as f:
                return any("ubuntu" in line.lower() for line in f)
        except FileNotFoundError:
            return False

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenROAD GUI")
        self.setGeometry(100, 100, 600, 500)
        self.initUI()
        self.current_file = None
        self.imported_design = None  # Store the last imported design name
    
    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Create a splitter for dynamic resizing
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Console Output (Left Side, takes most space)
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        splitter.addWidget(self.console_output)
        
        # Buttons Layout (Right Side, Snapped to Top)
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Select PDK (Same row as dropdown)
        pdk_layout = QHBoxLayout()
        self.pdk_label = QLabel("Select PDK:")
        self.pdk_dropdown = QComboBox()
        self.populate_pdk_dropdown()
        self.pdk_dropdown.currentTextChanged.connect(self.pdk_changed)
        pdk_layout.addWidget(self.pdk_label)
        pdk_layout.addWidget(self.pdk_dropdown)
        buttons_layout.addLayout(pdk_layout)

        # Source .env
        self.sourceEnv_label = QPushButton("Source Env")
        self.sourceEnv_label.clicked.connect(self.source_env)
        buttons_layout.addWidget(self.sourceEnv_label)
        
        # Imported Design Label
        self.imported_design_label = QLabel("Imported Design: None")
        buttons_layout.addWidget(self.imported_design_label)
        
        # Import Design
        self.import_design_button = QPushButton("Import Design")
        self.import_design_button.clicked.connect(self.import_design)
        buttons_layout.addWidget(self.import_design_button)
        
        # Edit config.mk & Reset config.mk (Same Row)
        config_layout = QHBoxLayout()
        self.edit_config_button = QPushButton("Edit config.mk")
        self.edit_config_button.clicked.connect(lambda: self.edit_file("config.mk"))
        config_layout.addWidget(self.edit_config_button)
        
        self.reset_config_button = QPushButton("Reset config.mk")
        self.reset_config_button.clicked.connect(self.reset_config)
        config_layout.addWidget(self.reset_config_button)
        buttons_layout.addLayout(config_layout)
        
        # Edit constraints.sdc & Reset constraints.sdc (Same Row)
        constraints_layout = QHBoxLayout()
        self.edit_constraints_button = QPushButton("Edit constraints.sdc")
        self.edit_constraints_button.clicked.connect(lambda: self.edit_file("constraints.sdc"))
        constraints_layout.addWidget(self.edit_constraints_button)
        
        self.reset_constraints_button = QPushButton("Reset constraints.sdc")
        self.reset_constraints_button.clicked.connect(self.reset_constraints)
        constraints_layout.addWidget(self.reset_constraints_button)
        buttons_layout.addLayout(constraints_layout)
        
        # Set Makefile & Run Make Layout
        make_layout = QVBoxLayout()
        self.set_makefile_button = QPushButton("Set Makefile")
        self.set_makefile_button.clicked.connect(self.set_makefile)
        make_layout.addWidget(self.set_makefile_button)
        
        self.run_make_button = QPushButton("Run Make")
        self.run_make_button.clicked.connect(self.run_make)
        make_layout.addWidget(self.run_make_button)
        buttons_layout.addLayout(make_layout)
        
        # Edit File Area
        self.text_edit = QTextEdit()
        self.text_edit.setVisible(False)
        buttons_layout.addWidget(self.text_edit)
        
        self.save_button = QPushButton("Save File")
        self.save_button.setVisible(False)
        self.save_button.clicked.connect(self.save_file)
        buttons_layout.addWidget(self.save_button)
        
        # Add button layout to the right side
        splitter.addWidget(buttons_widget)
        
        # Allow resizing
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def log(self, message):
        self.console_output.append(message)
    
    def source_env(self):
        #Windows
        # os.system("source .env")
        # self.log("Sourced .env file")

        #Ubuntu
        # Run the 'source .env' command in a new bash process and execute additional commands if necessary

        if self.is_ubuntu():

            result = subprocess.run(["bash", "-i", "-c", "cd .. && source ./env.sh && cd flow && echo 'Env sourced'"],capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Sourced .env file successfully: {result.stdout}")
            else:
                self.log(f"Failed to source .env file: {result.stderr}")
        else:
            self.log("NOT UBUNTU")
    
    def populate_pdk_dropdown(self):
        pdk_path = "designs"
        if os.path.exists(pdk_path):
            items = [item for item in os.listdir(pdk_path) if item != 'src']
            self.pdk_dropdown.addItems(items)
            # self.pdk_dropdown.addItems(os.listdir(pdk_path))
    
    def pdk_changed(self, text):
        self.log(f"Selected PDK: {text}")
    
    def import_design(self):
        design_folder = QFileDialog.getExistingDirectory(self, "Select Design Folder")
        if design_folder:
            self.imported_design = os.path.basename(design_folder)
            self.imported_design_label.setText(f"Imported Design: {self.imported_design}")
            selected_pdk = self.pdk_dropdown.currentText()
            dest_src = f"designs/src/{self.imported_design}"
            dest_pdk = f"designs/{selected_pdk}/{self.imported_design}"
            
            shutil.copytree(design_folder, dest_src, dirs_exist_ok=True)
            shutil.copytree(design_folder, dest_pdk, dirs_exist_ok=True)
            
            self.reset_config()
            self.reset_constraints()

            # shutil.copy("defaultConstraints.txt", f"{dest_pdk}/constraints.sdc")
            # shutil.copy("defaultConfig.txt", f"{dest_pdk}/config.mk")
            self.log(f"Imported {self.imported_design} into {dest_pdk} and {dest_src}")

            # self.source_env()
    
    def edit_file(self, file_name):
        selected_pdk = self.pdk_dropdown.currentText()
        file_path = f"designs/{selected_pdk}/{self.imported_design}/{file_name}"
        if os.path.exists(file_path):
            self.current_file = file_path
            
            with open(file_path, "r") as file:
                self.text_edit.setText(file.read())
            self.text_edit.setVisible(True)
            self.save_button.setVisible(True)
    
    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_edit.toPlainText())
            self.text_edit.setVisible(False)
            self.save_button.setVisible(False)
            self.log(f"Saved {self.current_file}")
    
    def reset_config(self):
        selected_pdk = self.pdk_dropdown.currentText()
        # shutil.copy("defaultConfig.txt", f"designs/{selected_pdk}/{self.imported_design}/config.mk")

        with open("defaultConfig.txt", "r") as file:
                makefile_data = (file.read().replace("gcd",self.imported_design)).replace("sky130hd",selected_pdk)
                with open(f"designs/{selected_pdk}/{self.imported_design}/config.mk", "w") as file:
                    file.write(makefile_data)

        if self.current_file == f"designs/{selected_pdk}/{self.imported_design}/config.mk":
            self.edit_file("config.mk")
        self.log("Reset config.mk")
    
    def reset_constraints(self):
        selected_pdk = self.pdk_dropdown.currentText()
        # shutil.copy("defaultConstraints.txt", f"designs/{selected_pdk}/{self.imported_design}/constraints.sdc")

        with open("defaultConstraints.txt", "r") as file:
                makefile_data = file.read().replace("gcd",self.imported_design)
                with open(f"designs/{selected_pdk}/{self.imported_design}/constraints.sdc", "w") as file:
                    file.write(makefile_data)

        if self.current_file == f"designs/{selected_pdk}/{self.imported_design}/constraints.sdc":
            self.edit_file("constraints.sdc")
        self.log("Reset constraints.sdc")
    
    def set_makefile(self):
        if self.imported_design:
            with open("defaultMakefile.txt", "r") as file:
                makefile_data = file.read().replace("DESIGN_CONFIG ?= ./designs/nangate45/gcd/config.mk", "DESIGN_CONFIG ?= ./designs/"+self.pdk_dropdown.currentText()+"/"+self.imported_design+"/config.mk")
            with open("Makefile", "w") as file:
                file.write(makefile_data)
            self.log("Makefile updated")
        else:
            self.log("No design has been imported yet.")
    
    def run_make(self):
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", "make; exec bash"])
        self.log("Running make...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Dark Mode Style
    dark_stylesheet = """
    QWidget {
        background-color: #2e2e2e;
        color: white;
    }
    QPushButton {
        background-color: #444444;
        color: white;
        border: 1px solid #888888;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    """
    app.setStyleSheet(dark_stylesheet)
    window = PDKManagerApp()
    window.show()
    sys.exit(app.exec())
