import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import modules.list_managers as listm
import modules.dialogs as dialogs
import modules.db as db
from modules.crypting import Crypting


class Manager(tk.Tk):
    """
    Simple password manager
    """
    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.option_add("*tearOff",value=False)
        self.geometry("620x520")

        self.unsaved = False
        ###
        # self.data = db.KeyDatabase()
        ###

        self.search_param = tk.StringVar(self,value="")
        self.search_param.trace_add(mode="write",callback=self.search_param_callback) 
        self.show_data = []
        self.unsaved_var = tk.StringVar(self,value=" "*18)
        self.db_path_var = tk.StringVar(self,value="No Database Loaded")
        self.username = ""
        self.user_var = tk.StringVar(self,value="Not logged in")
        self.password = ""
        self.data, self.path = db.create_data(self,self.password,placeholder=True)

        # Top level menus:
        menubar = tk.Menu()
        self.config(menu=menubar)

        login_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=login_menu,label="Login")

        data_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=data_menu,label="Database")

        help_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=help_menu,label="Help")


        #Menu commands:
        login_menu.add_command(label="Login / Change User",command=self.login)
        login_menu.add_command(label="Logout User",command=self.logout)
        login_menu.add_command(label="Quit",command=self.quit_app)

        data_menu.add_command(label="Create Database",command=self.create_data)
        data_menu.add_command(label="Load Database",command=self.load_data)
        data_menu.add_command(label="Save Database",command=self.save_data)
        data_menu.add_command(label="Backup Database",command=self.backup_data)
        data_menu.add_command(label="Change database password",command=self.change_password)
        data_menu.add_command(label="Redefine Database",command=self.redefine_database)

        help_menu.add_command(label="About",command=self.display_info)


        # Make toolbar/infobar:
        self.toolbar = tk.Frame(self,borderwidth="3",relief="ridge")
        self.toolbar.pack(side = "top",fill="x")

        self.login_button = tk.Button(self.toolbar,text="Login",command=self.login)
        self.login_button.grid(row = 0,column=0)

        self.add_button = tk.Button(self.toolbar,text="Add Entry",command=self.click_add)
        self.add_button.grid(row = 0,column=1)

        self.save_button = tk.Button(self.toolbar,text="Save Database",command=self.save_data)
        self.save_button.grid(row = 0,column=2)

        self.unsaved_info = tk.Label(self.toolbar,textvariable=self.unsaved_var,fg="red3")
        self.unsaved_info.grid(row = 0,column=3)


        #Search components
        self.search_field = tk.Entry(self.toolbar,textvariable=self.search_param)
        self.search_field.grid(row = 0,column=4)

        self.clear_search_button = tk.Button(self.toolbar,text="X",state="disabled",fg="red3",command=self.clear_search)
        self.clear_search_button.grid(row = 0,column=5)

        self.search_button = tk.Button(self.toolbar,text="Search",command=self.update_list)
        self.search_button.grid(row = 0,column=6)

        # Display curently active user
        self.user_active = tk.Label(self.toolbar,textvariable=self.user_var)
        self.user_active.grid(row = 0,column=7)


        # Create main dataframe
        self.mainframe = listm.ScrollableFrame(self)
        self.mainframe.pack(side="top",fill="both", expand=True,padx=10)


        # Bottom info bar
        self.bottombar = tk.Frame(self,borderwidth="3",relief="ridge")
        self.bottombar.pack(side="bottom",fill="x", expand=False)

        self.db_info = tk.Label(self.bottombar,textvariable=self.db_path_var,justify="left")
        self.db_info.pack(side="left")


    # Checks for user actions
    def check_login_ok(self):
        if not self.username:
            messagebox.showinfo(title="Not yet logged in",message="You must first log in.")
            return False
        else:
            return True

    def check_data_ok(self):
        if self.data.isplaceholder:
            messagebox.showinfo(title="No database found.",message="You must first load (Manage > Load Database) or create (Manage > Create Database) a database to be used.")
            return False
        else:
            return True

    def check_unsaved_ok(self):
        if self.unsaved:
            confirm = messagebox.askyesno(title="Confirm Close", 
                                                message="Current database contain unsaved changes:\nAre you sure you want to close it?\nUnsaved data will be lost.",
                                                icon = "question")
            return confirm
        else:
            return True

    # Create new database
    def create_data(self):
        if not self.check_login_ok() or not self.check_unsaved_ok():
            return

        result = db.create_data(self,self.password,placeholder=False)

        if not result:
            return
               
        self.data, self.path = result
        self.update_list()

    # Load database
    def load_data(self):
        if not self.check_login_ok() or not self.check_unsaved_ok():
            return

        result = db.load_data(self, self.password)

        if not result:
            return

        self.data, self.path = result

        self.unsaved = False
        self.update_list()

    # Save database
    def save_data(self):
        if not self.check_login_ok() or not self.check_data_ok():
            return

        if not self.path:
            database_path =  None
        else:
            database_path = self.path

        result = db.save_data(self.data,self.password,database_path)

        if not result:
            return
        self.data, self.path = result

        self.unsaved = False
        self.update_save_state()
        self.update_list()


    # Back-up database
    def backup_data(self):
        if not self.check_login_ok() or not self.check_data_ok():
            return
        db.backup_data(self.data,self.password)

    # Change database password
    def change_password(self):
        if not self.check_login_ok() or not self.check_data_ok():
            return

        result = dialogs.ask_change_password(self,self.password,self.data)

        if not result:
            return

        #Backup database, just in case
        backup_path = db.get_backup_filepath(self.path,self.username)
        db.backup_data(self.data,self.password,backup_path)

        # Get new values
        _,new_pw,_ = result

        self.password = new_pw

        self.save_data()

    # Define (or redefine) database parameters
    def redefine_database(self):
        if not self.check_login_ok() or not self.check_data_ok():
            return

        result = dialogs.ask_define_database(self,self.password,self.data,self.path,redefine=True)

        if not result:
            return

        #Backup database, just in case
        backup_path = db.get_backup_filepath(self.path,self.username)
        db.backup_data(self.data,self.password,backup_path)

        # Get new values
        _, new_pw, _, change_password, pass_pad, data_pad, mode_int, database_path = result

        if change_password == 1:
            self.password = new_pw
        self.data.char1 = pass_pad
        self.data.char2 = data_pad
        self.data.mode = mode_int
        self.path = database_path

        self.save_data()

    # Login user
    def login(self):
        if not self.check_unsaved_ok():
            return

        response = dialogs.user_credentials(self)

        if not response:
            return

        self.username, self.password,load = response

        if not self.username:
            return

        if load == 1:
            result = db.load_data(self,self.password,default=True,username=self.username)
            if not result:
                result = db.create_data(self,self.password,placeholder = True)
        else:
            result = db.create_data(self,self.password,placeholder = True)

        self.update_user()

        self.data, self.path = result
        self.unsaved = False
        self.update_list()

    # Logout user
    def logout(self):
        if not self.check_unsaved_ok():
            return

        self.username = ""
        self.password = ""
        self.update_user()

        result = db.create_data(self,self.password,placeholder = True)
        if not result:
            return
        self.data, self.path = result
        self.unsaved = False
        self.update_list()


    # Update functions for different user visible data
    def update_user(self):
        if not self.username:
            user = "Not logged in"
        else:
            user = self.username
        self.user_var.set("Logged in: {}".format(user))

    def update_db_info(self):
        if self.path:
            infotext = "Database: {}".format(self.path)
            self.db_path_var.set(infotext)
        else:    
            self.db_path_var.set("No Database Loaded")

    def update_save_state(self):
        if self.unsaved == False:
            self.unsaved_var.set(" "*18)
        else:
            self.unsaved_var.set("*unsaved changes*")

    def update_list(self):
        self.update_db_info()
        self.update_save_state()
        self.depopulate()
        self.populate()


    #Search functionality:
    def search_keys(self):
        text_to_search = self.search_param.get().lower()
        found_keys = []
        for item in self.data.keys:
            target_name = item["target"].lower()
            if listm.match_string(pattern= text_to_search,data=target_name):
                found_keys.append(item)
        return found_keys


    def search_param_callback(self, var, indx, mode): 
        if not self.search_param.get():
            self.clear_search_button["state"]="disabled"
        else:
            self.clear_search_button["state"]="normal"

    def clear_search(self):
        self.search_param.set("")
        self.clear_search_button["state"]="disabled"
        self.update_list()


    ### List item operations:

    # Add button clicked
    def click_add(self):
        if not self.check_login_ok():
            return
        if not self.check_data_ok():
            return

        added_entry = dialogs.get_user_entry(self,n_fields=3,labels=["Target: ","Name: ","Key: "],init=["","",""],title="Add new key",data_pad_char=self.data.char2)
        if not added_entry:
            return
        new_target_val, new_name_val, new_key_val = added_entry

        check = self.data.add_key(new_target_val, new_name_val, new_key_val)

        if check == True:
            self.unsaved = True
        self.update_list()

    # Item modify button clicked
    def click_modify(self,event):
        old_target_val, old_name_val, old_key_val = listm.get_item_values(event)
        
        modified_entry = dialogs.get_user_entry(self,n_fields=3,labels=["Target: ","Name: ","Key: "],init=[old_target_val,old_name_val,old_key_val],title="Modify stored key",data_pad_char=self.data.char2)
        
        if not modified_entry:
            return
        new_target_val, new_name_val, new_key_val = modified_entry
        if new_target_val == old_target_val and new_name_val == old_name_val and new_key_val == old_key_val:
            return
        
        check = self.data.modify_key(old_target_val,new_target_val,new_name_val,new_key_val)
        if check == True:
                    self.unsaved = True
        self.update_list()
        
    # Item delete button clicked
    def click_delete(self,event):
        target_val, name_val, key_val = listm.get_item_values(event)
        confirm_delete = messagebox.askyesno(title="Delete Key", 
                                            message="Do yo want to delete the following key:\n Target: {}, {}: {}".format(target_val,name_val,key_val),
                                            icon = "question")
        if confirm_delete:
            check = self.data.delete_key(target_val)
            if check == True:
                self.unsaved = True
            self.update_list()


    def click_copy(self,event):
        target_val, name_val, key_val = listm.get_item_values(event)
        caller = self.master
        self.clipboard_clear()
        self.clipboard_append(key_val)
        self.update()
      

    # Displayed List Management

    # Populate List
    def populate(self):
        if not self.search_param.get():
            data = self.data.keys
        else:
            data = self.search_keys()

        listm.make_headers(self.mainframe.scrollable_frame)

        for n,item in enumerate(data):
            frame = listm.ItemFrame(self.mainframe.scrollable_frame,name=str(n))
            target_entry = listm.ItemEntry(frame,text=item["target"],name="target{}".format(n))
            name_entry = listm.ItemEntry(frame,text=item["name"],name="name{}".format(n))
            key_entry = listm.ItemEntry(frame,text=item["key"],name="key{}".format(n))
            button_modify = listm.ItemButton(frame,function=self.click_modify,text="Modify", name="modify{}".format(n))
            button_delete = listm.ItemButton(frame,function=self.click_delete,text="Delete", name="delete{}".format(n))
            
    # Clear List
    def depopulate(self):
        for widget in self.mainframe.scrollable_frame.winfo_children():
            widget.destroy()


    # Display About Info
    def display_info(self):
        messagebox.showinfo(title="Password Manager Demo App",message="This is a demo app for\n a simple password manager.\nTest use only!\n\n\t\tLeo Ojala (2021)")

    # Finally
    def quit_app(self):
        self.destroy()






if __name__ == "__main__":

    app = Manager()
    app.mainloop()
