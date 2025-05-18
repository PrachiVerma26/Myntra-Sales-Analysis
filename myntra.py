import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, Scrollbar, RIGHT, Y, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
from io import StringIO

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MyntraSalesApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Myntra Sales Analysis")
        self.geometry("1200x850")
        self.state("zoomed")
        self.resizable(True, True)

        self.data = None
        self.figure_canvas = None

        # Left Navigation Frame (fixed width, fill vertically)
        self.navigation_frame = ctk.CTkFrame(self, width=300)
        self.navigation_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.navigation_frame, text="Myntra Analysis", font=("Arial", 20, "bold")).pack(pady=(20, 30))

        # Navigation Buttons to switch frames
        self.home_button = ctk.CTkButton(self.navigation_frame, text="Home", command=self.show_home_frame)
        self.home_button.pack(pady=10, fill='x')

        self.analysis_button_nav = ctk.CTkButton(self.navigation_frame, text="Analysis", command=self.show_analysis_frame)
        self.analysis_button_nav.pack(pady=10, fill='x')

        # UI Scale Label & Dropdown
        self.ui_scale_label = ctk.CTkLabel(self.navigation_frame, text="UI Scale (%)", font=('Arial', 12))
        self.ui_scale_label.pack(pady=(40, 5))

        scale_options = ['80', '90', '100', '110']
        self.ui_scale = ctk.StringVar()
        self.ui_scale.set('100')
        self.ui_scale_dropdown = ctk.CTkOptionMenu(self.navigation_frame, variable=self.ui_scale, values=scale_options, command=self.adjust_ui_scale)
        self.ui_scale_dropdown.pack(pady=5, fill='x', padx=10)

        # Appearance Mode Label & Dropdown
        self.theme_label = ctk.CTkLabel(self.navigation_frame, text="Appearance", font=('Arial', 12))
        self.theme_label.pack(pady=5)

        theme_options = ['Light', 'Dark', 'System']
        self.theme_mode = ctk.StringVar()
        self.theme_mode.set('System')
        self.theme_dropdown = ctk.CTkOptionMenu(self.navigation_frame, variable=self.theme_mode, values=theme_options, command=self.set_theme)
        self.theme_dropdown.pack(pady=5, fill='x', padx=10)

        # Right Content Outer Frame (to hold canvas and scrollbar)
        self.content_outer_frame = ctk.CTkFrame(self)
        self.content_outer_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Canvas and vertical scrollbar for entire right content
        self.canvas = tk.Canvas(self.content_outer_frame)
        self.v_scrollbar = tk.Scrollbar(self.content_outer_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame inside canvas to hold all content frames
        self.content_frame = ctk.CTkFrame(self.canvas)
        self.canvas_window = self.canvas.create_window((0,0), window=self.content_frame, anchor='nw')

        # Bind to update scrollregion
        self.content_frame.bind("<Configure>", self.on_content_configure)
        # Bind canvas resize to update embedded frame width
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # HOME FRAME - instructions about app usage
        self.home_frame = ctk.CTkFrame(self.content_frame)
        self.home_frame.pack(fill="both", expand=True)
        self.create_home_content()

        # ANALYSIS FRAME - for options, uploading data, results
        self.analysis_frame = ctk.CTkFrame(self.content_frame)
        self.analysis_frame.pack_forget()
        self.create_analysis_content()

        # Initialize with default UI scale and theme
        self.adjust_ui_scale(self.ui_scale.get())
        self.set_theme(self.theme_mode.get())

        # Show home frame by default
        self.show_home_frame()

    def create_home_content(self):
        header = ctk.CTkLabel(self.home_frame, text="Welcome to Myntra Sales Analysis App", font=("Arial", 22, "bold"))
        header.pack(pady=20)

        instructions = (
            "How to Use This Application:\n\n"
            "- Use the 'Select File' button in the Analysis section to upload your CSV dataset.\n"
            "- Alternatively, enter a URL to a CSV file and click 'Load from URL'.\n"
            "- Select the analysis type and the visualization type from the dropdown menus.\n"
            "- Click 'Run Analysis' to perform the selected analysis and see the results.\n"
            "- The data preview will show the underlying data or results.\n"
            "- The graph area will visualize the analysis.\n\n"
            "UI Controls:\n"
            "- Adjust the UI scale and appearance (light/dark/system) from the left panel.\n\n"
            "Enjoy your data exploration!"
        )
        instructions_label = ctk.CTkLabel(self.home_frame, text=instructions, font=("Arial", 14), justify="left")
        instructions_label.pack(padx=20, pady=10, anchor="w")

    def create_analysis_content(self):
        # Top nav bar frame for all input options side-by-side
        self.navbar_frame = ctk.CTkFrame(self.analysis_frame)
        self.navbar_frame.pack(fill="x", padx=10, pady=(10,5))

        # File upload button
        self.upload_button = ctk.CTkButton(self.navbar_frame, text="Select File", command=self.upload_data)
        self.upload_button.grid(row=0, column=0, padx=5, pady=10, sticky='ew')

        # URL entry for CSV data and load button in same grid row
        self.url_entry = ctk.CTkEntry(self.navbar_frame)
        self.url_entry.grid(row=0, column=1, padx=5, pady=10, sticky='ew')
        self.url_fetch_button = ctk.CTkButton(self.navbar_frame, text="Load from URL", command=self.load_data_from_url)
        self.url_fetch_button.grid(row=0, column=2, padx=5, pady=10, sticky='ew')

        # Analysis type dropdown
        analysis_options = [
            "Count Sizes in Dataset",
            "Group by Size and Quantity",
            "Top 5 Most Popular Products",
            "Top Clothing Categories",
            "B2B Data Analysis",
            "Category by Size",
            "Top 10 States by Orders"
        ]
        self.analysis_type = ctk.StringVar()
        self.analysis_type.set(analysis_options[0])
        self.analysis_dropdown = ctk.CTkOptionMenu(self.navbar_frame, variable=self.analysis_type, values=analysis_options)
        self.analysis_dropdown.grid(row=0, column=3, padx=5, pady=10, sticky='ew')

        # Visualization type dropdown
        vis_options = ["Bar Graph", "Pie Chart", "Line Graph"]
        self.visualization_type = ctk.StringVar()
        self.visualization_type.set(vis_options[0])
        self.visualization_dropdown = ctk.CTkOptionMenu(self.navbar_frame, variable=self.visualization_type, values=vis_options)
        self.visualization_dropdown.grid(row=0, column=4, padx=5, pady=10, sticky='ew')

        # Run Analysis button
        self.run_analysis_button = ctk.CTkButton(self.navbar_frame, text="Run Analysis", command=self.run_analysis)
        self.run_analysis_button.grid(row=0, column=5, padx=5, pady=10, sticky='ew')

        # Configure grid columns weight for even spacing and responsiveness
        for i in range(6):
            self.navbar_frame.grid_columnconfigure(i, weight=1)

        # Data Preview Frame below navbar
        self.data_preview_frame = ctk.CTkFrame(self.analysis_frame)
        self.data_preview_frame.pack(fill="both", expand=True, pady=(10, 5), padx=10)

        self.display_textbox_label = ctk.CTkLabel(self.data_preview_frame, text='Data Preview', font=('Arial', 16, 'bold'))
        self.display_textbox_label.pack(anchor='w', padx=10, pady=(5,0))

        self.textbox_frame = ctk.CTkFrame(self.data_preview_frame)
        self.textbox_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.display_textbox = ctk.CTkTextbox(self.textbox_frame, wrap='word')
        self.display_textbox.pack(side="left", fill="both", expand=True)

        self.text_scrollbar = Scrollbar(self.textbox_frame, command=self.display_textbox.yview)
        self.text_scrollbar.pack(side=RIGHT, fill=Y)
        self.display_textbox.configure(yscrollcommand=self.text_scrollbar.set)

        # Graph Frame below data preview
        self.graph_frame = ctk.CTkFrame(self.analysis_frame, height=400)
        self.graph_frame.pack(fill="both", expand=True, pady=(5,10), padx=10)

        self.graph_label = ctk.CTkLabel(self.graph_frame, text='Data Visualization', font=('Arial', 16, 'bold'))
        self.graph_label.pack(anchor='w', padx=10, pady=(5, 0))

        self.graph_canvas_container = ctk.CTkFrame(self.graph_frame)
        self.graph_canvas_container.pack(fill="both", expand=True, padx=10, pady=10)

    def show_home_frame(self):
        self.analysis_frame.pack_forget()
        self.home_frame.pack(fill="both", expand=True)

    def show_analysis_frame(self):
        self.home_frame.pack_forget()
        self.analysis_frame.pack(fill="both", expand=True)

    def on_content_configure(self, event):
        # Update the scrollregion when the size of the content_frame changes
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Resize the embedded frame's width to match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def adjust_ui_scale(self, scale):
        try:
            scale_val = int(scale)
            ctk.set_widget_scaling(scale_val / 100)
        except Exception:
            pass

    def set_theme(self, theme):
        ctk.set_appearance_mode(theme)

    def upload_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.display_textbox.delete("1.0", "end")
                self.display_textbox.insert("1.0", "Data loaded successfully!\n" + self.data.head().to_string())
            except Exception as e:
                self.display_textbox.delete("1.0", "end")
                self.display_textbox.insert("1.0", f"Failed to load data: {e}\n")

    def load_data_from_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a valid URL.")
            return
        try:
            response = requests.get(url)
            response.raise_for_status()
            data_string = StringIO(response.text)
            self.data = pd.read_csv(data_string)
            self.display_textbox.delete("1.0", "end")
            self.display_textbox.insert("1.0", "Data loaded successfully from URL!\n" + self.data.head().to_string())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data from URL: {e}")

    def run_analysis(self):
        if self.data is None:
            self.display_textbox.delete("1.0", "end")
            self.display_textbox.insert("1.0", "Please upload data first.\n")
            return

        analysis_type = self.analysis_type.get()
        vis_type = self.visualization_type.get()

        # Clear previous graph
        if self.figure_canvas:
            self.figure_canvas.get_tk_widget().destroy()

        try:
            if analysis_type == "Count Sizes in Dataset":
                data = self.data['Size'].value_counts()
            elif analysis_type == "Group by Size and Quantity":
                data = self.data.groupby('Size')['Quantity'].sum()
            elif analysis_type == "Top Clothing Categories":
                data = self.data['Category'].value_counts()
            elif analysis_type == "Top 5 Most Popular Products":
                data = self.data['Category'].value_counts().head(5)
            elif analysis_type == "B2B Data Analysis":
                data = self.data['B2B'].value_counts()
            elif analysis_type == "Category by Size":
                data = self.data.groupby('Size')['Category'].count()
            elif analysis_type == "Top 10 States by Orders":
                data = self.data['Ship State'].value_counts().head(10)
            else:
                data = pd.Series()

            self.display_textbox.delete("1.0", "end")
            if data.empty:
                self.display_textbox.insert("1.0", "No data found for this analysis.\n")
                return

            # Prepare data for visualization
            df = data.reset_index()
            df.columns = ['Category', 'Value']  # Rename for uniform plotting

            self.display_textbox.insert("1.0", df.to_string(index=False))

            # Plotting
            fig, ax = plt.subplots(figsize=(8, 5))
            if vis_type == "Bar Graph":
                ax.bar(df['Category'].astype(str), df['Value'])
                plt.xticks(rotation=45, ha='right')
            elif vis_type == "Pie Chart":
                ax.pie(df['Value'], labels=df['Category'], autopct='%1.1f%%', startangle=140)
                ax.axis('equal')  # Equal aspect ratio ensures pie chart is circular.
            elif vis_type == "Line Graph":
                ax.plot(df['Category'].astype(str), df['Value'], marker='o')
                plt.xticks(rotation=45, ha='right')

            ax.set_title(f"{analysis_type} - {vis_type}")
            fig.tight_layout()

            self.figure_canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas_container)
            self.figure_canvas.draw()
            self.figure_canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            self.display_textbox.insert("1.0", f"Error during analysis: {e}\n")

if __name__ == "__main__":
    app = MyntraSalesApp()
    app.mainloop()
