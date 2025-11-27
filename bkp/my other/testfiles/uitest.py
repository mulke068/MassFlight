import customtkinter as ctk

def button_callback():
    print("button clicked")
def combobox_callback(choice):
    print("combobox dropdown clicked:", choice)
def radiobutton_event():
    print("radiobutton toggled, current value:", radio_var.get())
def segmented_button_callback(value):
    print("segmented button clicked:", value)
def slider_event(value):
    print(value)

app = ctk.CTk()
app.geometry("1000x500")

tabview = ctk.CTkTabview(master=app)

tabview.add("tab 1")  # add tab at the end
tabview.add("tab 2")  # add tab at the end
tabview.set("tab 2")  # set currently visible tab

button = ctk.CTkButton(text="my button", command=button_callback, master=tabview.tab("tab 1"))

combobox = ctk.CTkComboBox(app, values=["option 1", "option 2"], command=combobox_callback)
combobox.set("option 2")

entry = ctk.CTkEntry(app, placeholder_text="CTkEntry")

radio_var = ctk.IntVar(value=0)
radiobutton_1 = ctk.CTkRadioButton(app, text="CTkRadioButton 1",
                                             command=radiobutton_event, variable= radio_var, value=1)
radiobutton_2 = ctk.CTkRadioButton(app, text="CTkRadioButton 2",
                                             command=radiobutton_event, variable= radio_var, value=2)

segemented_button = ctk.CTkSegmentedButton(app, values=["Value 1", "Value 2", "Value 3"],
                                                     command=segmented_button_callback)
segemented_button.set("Value 1")

slider = ctk.CTkSlider(app, from_=0, to=100, command=slider_event)
progressbar = ctk.CTkProgressBar(app, orientation="horizontal", mode="determinate")


button.pack(padx=20, pady=20)
combobox.pack(padx=20, pady=20)
entry.pack(padx=20, pady=20)
progressbar.pack(padx=20, pady=20)
radiobutton_1.pack(padx=20, pady=10)
radiobutton_2.pack(padx=20, pady=10)
segemented_button.pack(padx=20, pady=20)
slider.pack(padx=20, pady=20)
tabview.pack(padx=20, pady=20)


progressbar.set(slider.get()/100)
app.mainloop()