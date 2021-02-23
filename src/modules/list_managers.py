import tkinter as tk
from tkinter import ttk, simpledialog


class ScrollableFrame(ttk.Frame):
    """
    Scrollable frame. 
    Data is stored in cls.scrollable_frame
    Ref: https://blog.tecladocode.com/tkinter-scrollable-frames/
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        scroll_area = tk.Canvas(self,highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=scroll_area.yview)
        self.scrollable_frame = tk.Frame(scroll_area)

        scroll_area.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: scroll_area.configure(
                scrollregion=scroll_area.bbox("all")
                )
            )

        scroll_area["yscrollcommand"] = scrollbar.set

        scroll_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")





class ItemFrame(tk.Frame):
    def __init__(self,master,name):
        super().__init__(master,name=name)          
        place_widget(self,side = "top")

class ItemLabel(tk.Label):
    def __init__(self,master,text,name):
        super().__init__(master,text=text,font="bold",name=name,anchor="w",justify="left")
        place_widget(self)

class ItemEntry(tk.Entry):
    def __init__(self,master,text,name,**kwargs):
        self.var = tk.StringVar(master,value=text,name="{}_var".format(name))
        super().__init__(master,textvariable=self.var,name=name,justify="left",state="readonly",**kwargs)
        place_widget(self)

class ItemButton(tk.Label):
    def __init__(self,master,function,text,name):
        super().__init__(master,text=text,relief="raised",name=name,justify="center")
        self.bind("<Button-1>",function)
        place_widget(self,ipadx=3)


# Consturctors for list item elements:
def make_headers(master):
    frame = ItemFrame(master,name="headers")
    header1 = ItemEntry(frame, text="Target",name="header1",relief="flat")
    header2 = ItemEntry(frame, text="Name",name="header2",relief="flat")
    header3 = ItemEntry(frame, text="Key",name="header3",relief="flat")


def place_widget(widget,side="left",**kwargs):
    widget.pack(side=side,expand=True)


# Item operations functions
def get_name(widget):
    return str(widget).split(".")[-1]


def get_item_values(event):
    item = event.widget.master
    id = get_name(item)         # Get name of the item frame the widget belogs to
    target = item.nametowidget("target{}".format(id))
    target_val = target.get()
    name = item.nametowidget("name{}".format(id))
    name_val = name.get()
    key = item.nametowidget("key{}".format(id))
    key_val = key.get()
    return (target_val,name_val,key_val)

def match_string(pattern:str,data:str):
    if data.find(pattern) != -1:
        return True
    else:
        return False


if __name__ == "__main__":

    app = tk.Tk()
    frame = ScrollableFrame(app)
    frame.pack()

    app.mainloop()