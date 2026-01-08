import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTextEdit, QLabel
)
from PyQt6.QtGui import QFont

class M_IDE(QMainWindow):
    def __init__(self):
        super().__init__()
        # English titles for the UI
        self.setWindowTitle("📝 M-IDE (M Language) Version 0.3")
        self.setGeometry(100, 100, 1000, 700)
        
        font = QFont("Consolas", 10)
        QApplication.setFont(font)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_editor_area()
        self.create_output_area()
        
    def create_editor_area(self):
        top_layout = QHBoxLayout()
        editor_label = QLabel("M Code Editor:")
        top_layout.addWidget(editor_label)
        
        # Action button in English
        run_btn = QPushButton("▶ RUN / Compile M")
        run_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        run_btn.clicked.connect(self.run_code)
        
        top_layout.addWidget(run_btn)
        self.main_layout.addLayout(top_layout)
        
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("Write your M Language code here...")
        self.main_layout.addWidget(self.code_editor)

    def create_output_area(self):
        output_label = QLabel("M Console (Output/Compilation Errors):")
        self.main_layout.addWidget(output_label)
        
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setStyleSheet("background-color: #1e1e1e; color: #00FF00; font-family: 'Consolas';")
        self.main_layout.addWidget(self.output_console)
        
        self.main_layout.setStretch(1, 3)
        self.main_layout.setStretch(3, 1)

    def run_code(self):
        code = self.code_editor.toPlainText()
        self.output_console.clear()
        
        self.variables = {} 
        self.output_console.append("--- M-Compiler: Analysis & Execution Started ---")
        
        if not code.strip():
            self.output_console.append("ERROR: No code detected in editor.")
            return

        lines = code.split('\n')
        self.execution_state = 0 
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            if not stripped_line or stripped_line.startswith('#'):
                continue 

            is_indented = len(line) > len(line.lstrip(' '))
            if self.execution_state != 0 and not is_indented:
                self.execution_state = 0 

            try:
                # --- IF / ELSE BLOCKS ---
                if stripped_line.startswith('IF ') and stripped_line.endswith(':'):
                    condition = stripped_line[3:-1].strip()
                    try:
                        res = eval(condition, {}, self.variables)
                    except:
                        res = False
                    self.execution_state = 1 if bool(res) else 2
                    self.output_console.append(f"[L{line_num}]: IF: Condition is {bool(res)}.")
                    continue

                elif stripped_line == 'ELSE:':
                    self.execution_state = 1 if self.execution_state == 2 else 2
                    continue

                # --- COMMAND EXECUTION ---
                if self.execution_state in [0, 1]:
                    
                    # 1. NEW COMMAND: $add (Library Integration)
                    if stripped_line.startswith('$add '):
                        lib = stripped_line[5:].strip()
                        self.output_console.append(f"[L{line_num}]: SUCCESS: Module '{lib}' linked.")

                    # 2. NEW COMMAND: import() (Output/Print)
                    elif stripped_line.startswith('import(') and stripped_line.endswith(')'):
                        content = stripped_line[7:-1].strip()
                        parts = content.split(',')
                        results = []
                        for p in parts:
                            p = p.strip()
                            if p.startswith('"') and p.endswith('"'):
                                results.append(p.strip('"'))
                            else:
                                try:
                                    results.append(str(eval(p, {}, self.variables)))
                                except:
                                    results.append(f"<undefined:{p}>")
                        self.output_console.append(f"[L{line_num}]: OUTPUT: {''.join(results)}")

                    # 3. VAR DECLARATION
                    elif stripped_line.startswith('VAR '):
                        # ... Logic for VAR as requested ...
                        definition = stripped_line[4:].strip()
                        if '=' not in definition: raise SyntaxError("Incomplete VAR statement.")
                        var_def, val_str = definition.split('=', 1)
                        name = var_def.strip()
                        self.variables[name] = eval(val_str.strip(), {}, self.variables)
                        self.output_console.append(f"[L{line_num}]: STORED: '{name}' = {self.variables[name]}")
                    
                    # 4. VARIABLE UPDATE (Assignment)
                    elif '=' in stripped_line:
                        name, expr = stripped_line.split('=', 1)
                        name = name.strip()
                        if name in self.variables:
                            self.variables[name] = eval(expr.strip(), {}, self.variables)
                            self.output_console.append(f"[L{line_num}]: UPDATED: '{name}' to {self.variables[name]}")
                        else:
                            raise NameError(f"Variable '{name}' was not initialized.")
                    
                    else:
                        self.output_console.append(f"[L{line_num}]: SYNTAX ERROR: Unknown command: {stripped_line}")

            except Exception as e:
                self.output_console.append(f"--- FATAL ERROR at Line {line_num} ---")
                self.output_console.append(f"[{type(e).__name__}]: {str(e)}")
                return 

        self.output_console.append("\n--- M-Memory: Execution Finished ---")
        self.output_console.append(str(self.variables))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = M_IDE()
    ide.show()
    sys.exit(app.exec())