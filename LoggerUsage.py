#Create a program that iterates through all code files in a directory
#The code should locate any calls to Logger
#The code should check if the call is wrapped in compiler logic
#The code should return the FileName, LineNumber, and the call statement

#method to find all code files in the provided directory, recursively
#imports
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class LoggerUsage:
    def __init__(self, file_name, line_number, call):
        self.file_name = file_name
        self.line_number = line_number
        self.call = call

class LoggerGUI:
    def __init__(self, window):
        #define global variables
        self.window = window
        self.directory = ''
        self.code_files = []
        self.logger_calls = []

        self.window.title('Logger Finder')
        self.window.geometry('500x300')
        self.window.resizable(1,1)
        self.window.configure(background='#f0f0f0')
        #make the window a grid layout thats 2 rows and 3 columns
        #make the first row hold the buttons and the second row hold the rsults view
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=1)
        


        #Section to allow user to choose directory to search
        self.directory_label = tk.Label(self.window, text='Directory:')
        self.directory_label.grid(row=0, column=0, sticky='w')
        self.directory_entry = tk.Entry(self.window)
        self.directory_entry.grid(row=0, column=1, sticky='w')
        self.directory_button = tk.Button(self.window, text='Browse', command=self.browse_directory)
        self.directory_button.grid(row=0, column=2, sticky='w')

        #Section to allow user to save results to a file
        self.file_label = tk.Label(self.window, text='Save Results:')
        self.file_label.grid(row=1, column=0, sticky='w')
        self.file_entry = tk.Entry(self.window)
        self.file_entry.grid(row=1, column=1, sticky='w')
        self.file_button = tk.Button(self.window, text='Save', command=self.save_file)
        self.file_button.grid(row=1, column=2, sticky='w')
        
        #Section to allow user to clear table
        self.clear_button = tk.Button(self.window, text='Clear', command=self.clear_table)
        self.clear_button.grid(row=0, column=3, sticky='w')

        #Section to display results of find_logger_calls
        self.results_table = ttk.Treeview(self.window, columns=('File', 'Line', 'Call'), show='headings')
        self.results_table.grid(column=0, columnspan=4, sticky='ew')
        self.results_table.heading('File', text='File')
        self.results_table.heading('Line', text='Line')
        self.results_table.heading('Call', text='Call')
        self.results_table.column('File', width=100)
        self.results_table.column('Line', width=50)
        self.results_table.column('Call', width=200)
        self.results_table.bind('<Double-1>', self.select_row)
    
    def find_code_files(self):
        #Clear the table
        self.code_files = []
        for path in Path(self.directory).rglob('*.cs'):
            self.code_files.append(path)
        for path in Path(self.directory).rglob('*.vb'):
            self.code_files.append(path)

    def find_logger_lines(self, code_file):
        import re
        lines = []
        #try to open the file
        try:
             #open the file
            with open(code_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    #trim the line of any whitespace from the beginning and end
                    line = line.strip()
                    #if line starts with '_logger.' or 'Logger.'
                    if re.match(r'^_logger\.|^Logger\.', line):
                        #if line does not contain .Trace .Start .Stop .When
                        if not re.search(r'\.Trace|\.Start|\.Stop|\.When', line):
                            if i > 1:
                                #if previous 2 lines are not compiler directives #If
                                if not re.match(r'^#If|^#if', lines[i-2]):
                                    #extract the file name
                                    file_name = code_file.name
                                    self.logger_calls.append( LoggerUsage(file_name, i, line) )

        except:
            #if the file could not be opened, print an error message containing the file name
            print('Could not open file: ' + str(code_file))
            pass

    def find_logger_calls(self):
        self.logger_calls = []
        for code_file in self.code_files:
            self.find_logger_lines(code_file)

    def save_logger_calls(self, file_name):
        with open(file_name, 'w') as f:
            for call in self.logger_calls:
                f.write(str(call) + '\n')

    def exit_program(self):
        self.window.destroy()
        
    def browse_directory(self):
        self.directory = tk.filedialog.askdirectory()
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, self.directory)
        self.find_code_files()
        if self.code_files.__len__() > 0:
            self.find_logger_calls()
            self.display_results()
        else:
            self.logger_calls = []
            self.display_results()
            #display error message
            self.error_message = tk.Label(self.window, text='No code files found in directory')

    def save_file(self):
        if self.logger_calls:
            #pop up a file dialog to allow user to save the results
            file_name = filedialog.asksaveasfilename(initialdir = self.directory, title = 'Save Results', filetypes = (('Text File', '*.txt'), ('all files', '*.*')))
            #if the file name has no extension, add .txt check for contains .
            if not file_name.endswith('.txt'):
                file_name = file_name + '.txt'
            formatted_results = []
            for call in self.logger_calls:
                #seperate filename, line number, and call into a string with a tab delimiter
                formatted_results.append(call.file_name + '\t' + str(call.line_number) + '\t' + call.call)
            with open(file_name, 'w') as f:
                f.write('\n'.join(formatted_results))
        else:
            #display error message
            self.error_message = tk.Label(self.window, text='No results to save')

    def clear_table(self):
        self.results_table.delete(*self.results_table.get_children())
        self.window.update()

    def display_results(self):
        if self.logger_calls:
            self.results_table.delete(*self.results_table.get_children())
            for call in self.logger_calls:
                self.results_table.insert('', 'end', values=(call.file_name, call.line_number, call.call))
            self.window.update()
        else:
            tk.messagebox.showinfo('No Results', 'There are no logger calls')
    
    def select_row(self, event):
        #copy the selected row to the clipboard
        selected_row = self.results_table.selection()[0]
        selected_row_data = self.results_table.item(selected_row)['values']
        selected_row_data = '\n'.join(selected_row_data)
        self.clipboard_clear()
        self.clipboard_append(selected_row_data)
        tk.messagebox.showinfo('Copied', 'Copied to clipboard')



#Main method to run the program
if __name__ == '__main__':
    #Use the Tkinter library to create a window using the LoggerGUI class and tkinter.ttk to create a table
    root = tk.Tk()
    root.title('Logger Finder')
    root.geometry('500x500')
    app = LoggerGUI(root)
    root.mainloop()
    sys.exit()
    #End of program