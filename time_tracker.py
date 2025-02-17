import tkinter as tk
from tkinter import ttk, messagebox
import csv
import time
from datetime import datetime

class TaskTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task and Time Tracking Made Easy")

        # Task tracking variables
        self.task_name_var = tk.StringVar()
        self.probable_time_var = tk.IntVar(value=60)  # Default value of 60 minutes
        self.start_time = None
        self.running = False  # Flag to control the timer

        self.setup_ui()
        self.create_log_file()

    def setup_ui(self):
        """Set up the user interface."""
        ttk.Label(self.root, text="Task Name:", foreground="blue").grid(row=0, column=0, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.task_name_var, width=30).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.root, text="Probable Time (minutes):", foreground="blue").grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.probable_time_var, width=30).grid(row=1, column=1, padx=10, pady=10)

        # Start & Stop buttons
        self.start_button = ttk.Button(self.root, text="Start Task", command=self.start_task)
        self.start_button.grid(row=2, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Task", command=self.stop_task, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, padx=10, pady=10)

        # Reset & Log buttons
        ttk.Button(self.root, text="Reset", command=self.reset_task).grid(row=3, column=0, padx=10, pady=10)
        ttk.Button(self.root, text="View Time Logs", command=self.view_time_logs).grid(row=3, column=1, padx=10, pady=10)

        # Timer label
        self.timer_label = ttk.Label(self.root, text="00:00:00", font=("Helvetica", 18, 'bold'), foreground="green")
        self.timer_label.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

    def create_log_file(self):
        """Create a CSV log file if it doesn't exist."""
        with open("time_log.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # If file is empty, write the header
                writer.writerow(['Task Name', 'Probable Time (minutes)', 'Start Time', 'End Time', 'Time Spent (minutes)', 'Time Difference (minutes)'])

    def start_task(self):
        """Start tracking a task."""
        task_name = self.task_name_var.get()
        if not task_name:
            messagebox.showwarning("Warning", "Please enter a task name.")
            return

        self.start_time = datetime.now()  # Store start time as a datetime object
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_timer()

    def stop_task(self):
        """Stop tracking a task and log the time spent."""
        if not self.running:
            return

        self.running = False
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        end_time = datetime.now()  # Capture the stop time
        time_spent = round((end_time - self.start_time).total_seconds() / 60, 2)  # Convert to minutes
        probable_time = self.probable_time_var.get()
        time_difference = round(time_spent - probable_time, 2)

        # Log the task details
        with open("time_log.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                self.task_name_var.get(),
                probable_time,
                self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                time_spent,
                time_difference
            ])

        messagebox.showinfo("Task Stopped", f"Task '{self.task_name_var.get()}' logged successfully!")

    def update_timer(self):
        """Update the timer display while the task is running."""
        if self.running:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            self.timer_label.config(text=time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
            self.root.after(1000, self.update_timer)  # Call itself every second

    def reset_task(self):
        """Reset the UI and stop the timer."""
        self.running = False
        self.task_name_var.set("")
        self.probable_time_var.set(30)
        self.timer_label.config(text="00:00:00")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def view_time_logs(self):
        """Display time logs in a pop-up window."""
        try:
            with open("time_log.csv", "r") as file:
                logs = list(csv.reader(file))

            if len(logs) <= 1:
                messagebox.showinfo("No Logs", "No task logs found.")
                return

            log_window = tk.Toplevel(self.root)
            log_window.title("Time Logs")

            text_area = tk.Text(log_window, height=20, width=100)
            text_area.pack(padx=10, pady=10)

            text_area.insert(tk.END, "Task Logs\n", "bold")
            text_area.insert(tk.END, "────────────────────────────────────────────────────────────────────────────────\n")

            for log in logs[1:]:  # Skip header
                task_name, probable_time, start_time, end_time, time_spent, time_diff = log
                color = "green" if float(time_diff) <= 0 else "red"

                log_entry = (
                    f"Task: {task_name}\n"
                    f"  - Probable Time: {probable_time} min\n"
                    f"  - Start Time: {start_time}\n"
                    f"  - End Time: {end_time}\n"
                    f"  - Time Spent: {time_spent} min\n"
                    f"  - Time Difference: {time_diff} min\n"
                    "────────────────────────────────────────────────────────────────────────────────\n"
                )

                text_area.insert(tk.END, log_entry, color)

            text_area.config(state=tk.DISABLED)
            text_area.tag_config("green", foreground="green")
            text_area.tag_config("red", foreground="red")
            text_area.tag_config("bold", font=("Helvetica", 12, "bold"))

        except FileNotFoundError:
            messagebox.showerror("Error", "No log file found. Start a task first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTrackerApp(root)
    root.mainloop()

