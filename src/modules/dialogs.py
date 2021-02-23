import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import modules.db as db



class UserEntry(simpledialog.Dialog):
    def __init__(self, master,n_fields=2,labels=["label1","label2"],init=["init1","init2"],title="Enter Data",data_pad_char="@"):
        self.fields= n_fields
        self.labels = labels
        self.init = init
        self.data_pad = data_pad_char
        super().__init__(master, title=title)


    def body(self,master):
        for n in range(self.fields):
            frame = tk.Frame(self,name=str(n))
            frame.pack(side = "top")
            label = tk.Label(frame, text=self.labels[n])
            label.grid(row=n, column=0, padx=3)

            var = tk.StringVar(frame,value=self.init[n])

            entry = tk.Entry(frame,textvariable=var,name="entry{}".format(n))
            entry.grid(row=n,column=1, padx=3)

    def getresult(self):
        result = []
        for n in range(self.fields): 
            frame = self.nametowidget(str(n))
            entry = frame.nametowidget("entry{}".format(n))
            entry_val = entry.get()
            result.append(entry_val)
        return result

    def validate(self):
        result = self.getresult()

        for field in result:
            data_pad_char_check = field.find(self.data_pad)
            if data_pad_char_check != -1:
                messagebox.showwarning(title="Data padding character conflict.",message="Data padding character should not be used in any of the data entries. \n Please try again.",parent = self)
                return 0
        self.result = result
        return 1        

def get_user_entry(master,**kwarga):
    """
    Create dialog window and get user credentials
    Accepts arguments
    label1: Label for first entry
    label2: Label for second entry
    init1: initial text in first entry
    init2: Initial text in second entry
    title: Title of the pop-up

    returns (entry1, entry2)
    """
    d = UserEntry(master,**kwarga)
    return d.result




class UserCredentials(simpledialog.Dialog):
    def __init__(self, master):
        super().__init__(master, title="Input username and password")


    def body(self,master):
        self.frame = tk.Frame(self)
        self.frame.pack()

        self.label1 = tk.Label(self.frame, text="Username:")
        self.label1.grid(row=0, column=0, padx=3)

        self.label2 = tk.Label(self.frame, text= "Password:")
        self.label2.grid(row=1,column=0, padx=3)

        self.username_var = tk.StringVar(self,value="")
        self.password_var = tk.StringVar(self,value="")

        self.entry_username = tk.Entry(self.frame,textvariable=self.username_var)
        self.entry_username.grid(row=0,column=1, padx=3)

        self.entry_password = tk.Entry(self.frame,textvariable=self.password_var,show="*")
        self.entry_password.grid(row=1,column=1, padx=3)

        self.load_default = tk.IntVar()
        self.load_default.set(1)

        self.checkBox1 = tk.Checkbutton(self.frame, variable=self.load_default, onvalue=1, offvalue=0, text="Load default database:")
        self.checkBox1.grid(row=2,column=1, padx=3)


    def getresult(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        load = self.load_default.get()
        return (username,password,load)
  

    def validate(self):
        result = self.getresult()
        self.result = result
        return 1       


def user_credentials(master):
    """
    Create dialog window and get user credentials
    Returns:
        (username, password, load_default)
    """
    d = UserCredentials(master)
    return d.result


class AskNewPassword(simpledialog.Dialog):
    def __init__(self, master,curr_password,db):
        self.curr_password = curr_password
        self.data = db
        super().__init__(master, title="Change password")


    def body(self,master):
        self.frame = tk.Frame(self)
        self.frame.pack()

        self.label1 = tk.Label(self.frame, text="Old Password:")
        self.label1.grid(row=0, column=0, padx=3)

        self.label2 = tk.Label(self.frame, text="New Password:")
        self.label2.grid(row=1,column=0, padx=3)

        self.label3 = tk.Label(self.frame, text="Retype New Password:")
        self.label3.grid(row=2,column=0, padx=3)

        self.var1 = tk.StringVar(self, value="")
        self.var2 = tk.StringVar(self, value="")
        self.var3 = tk.StringVar(self, value="")

        self.entry1 = tk.Entry(self.frame,textvariable=self.var1,show="*")
        self.entry1.grid(row=0,column=1, padx=3)

        self.entry2 = tk.Entry(self.frame,textvariable=self.var2,show="*")
        self.entry2.grid(row=1,column=1, padx=3)

        self.entry3 = tk.Entry(self.frame,textvariable=self.var3,show="*")
        self.entry3.grid(row=2,column=1, padx=3)


    def getresult(self):
        old_pw = self.entry1.get()
        new_pw = self.entry2.get()
        renew_pw = self.entry3.get()
        return (old_pw,new_pw,renew_pw)

    def validate(self):
        result = self.getresult()
        old_pw,new_pw,renew_pw = result
        if self.curr_password != old_pw:
            messagebox.showwarning(title="Current password mismatch.", message = "Entered password does not match the one currently in use. \n Please try again.", parent = self)
            return 0

        if new_pw != renew_pw:
            messagebox.showwarning(title="New password mismatch.",message="New password and retyped new password do not match. \n Please try again.",parent = self)
            return 0

        password_byte = new_pw.encode(self.data.codec)
        if len(password_byte) > 16:
            messagebox.showwarning(title="Password is too long.",message="Password cannot exceed 16 byte charachters.\n Your password has byte character length of {} \n Please try again.".format(len(password_byte)),parent = self)
            return 0   

        self.result = result
        return 1  

def ask_change_password(master,curr_password,db):
    """
    Create dialog window and ask user to give password
    Returns:
        (username, password, load_default)
    """
    d = AskNewPassword(master,curr_password,db)
    return d.result



class DefineDatabase(simpledialog.Dialog):
    def __init__(self, master,curr_password,db,path="",redefine = False):
        self.curr_password = curr_password
        self.data = db
        self.path = path
        self.redefine = redefine

        super().__init__(master, title="Define Database")


    def body(self,master):
        self.frame = tk.Frame(self)
        self.frame.pack()

        # Database Password options
        if self.redefine == True:
            self.password_var = tk.StringVar(self, value = "")
        else:
            self.password_var = tk.StringVar(self, value = self.curr_password)

        self.new_password_var = tk.StringVar(self, value = "")
        self.renew_password_var = tk.StringVar(self, value = "")
        self.change_password_bool = tk.IntVar()
        self.change_password_bool.set(0)

        self.label1 = tk.Label(self.frame, text="Password:")
        self.label1.grid(row=0, column=0, padx=3)

        self.checkNewPassword = tk.Checkbutton(self.frame, variable=self.change_password_bool, onvalue=1, offvalue=0, text="Change Password",state="disabled")
        if self.redefine == True:
            self.checkNewPassword["state"] = "normal"
            self.checkNewPassword.bind("<Button-1>",self.check_new_password)
            self.checkNewPassword.grid(row=1,column=1, padx=3)
        

        self.label2 = tk.Label(self.frame, text="New Password")
        self.label2.grid(row=2,column=0, padx=3)

        self.label3 = tk.Label(self.frame, text="Retype New Password:")
        self.label3.grid(row=3,column=0, padx=3)


        self.entry1 = tk.Entry(self.frame,textvariable=self.password_var,show="*")
        self.entry1.grid(row=0,column=1, padx=3)

        self.entry2 = tk.Entry(self.frame,textvariable=self.new_password_var,show="*",state="disabled")
        self.entry2.grid(row=2,column=1, padx=3)

        self.entry3 = tk.Entry(self.frame,textvariable=self.renew_password_var,show="*",state="disabled")
        self.entry3.grid(row=3,column=1, padx=3)


        ## Database padding characters & Encryption mode:

        self.pass_pad_var = tk.StringVar(self, value= self.data.char1)
        self.data_pad_var = tk.StringVar(self, value= self.data.char2)
        current_mode = self.mode_int2str(self.data.mode)
        self.mode_var = tk.StringVar(self, value= current_mode)
        mode_options = {"No Encryption","Name & Key","All Fields"}

        self.label4 = tk.Label(self.frame, text="Password padding character:")
        self.label4.grid(row=0,column=2, padx=3)

        self.label5 = tk.Label(self.frame, text="Entry padding character:")
        self.label5.grid(row=1,column=2, padx=3)

        self.label6 = tk.Label(self.frame, text="Encryption Mode:")
        self.label6.grid(row=2,column=2, padx=3)

        self.entry4 = tk.Entry(self.frame,textvariable=self.pass_pad_var)
        self.entry4.grid(row=0,column=3, padx=3)

        self.entry5 = tk.Entry(self.frame,textvariable=self.data_pad_var)
        self.entry5.grid(row=1,column=3, padx=3)

        self.entry6 = tk.OptionMenu(self.frame,self.mode_var,*mode_options)
        self.entry6.grid(row=2,column=3, padx=3)

        # Database file location
        self.path_var = tk.StringVar(self, value=self.path)

        self.entry7 = tk.Entry(self.frame,textvariable=self.path_var,state="readonly")
        self.entry7.grid(row=4,column=0,columnspan=3, padx=3,pady=3,sticky="ew")

        self.dir_button = tk.Button(self.frame,text="Change location",command=self.change_loc)
        self.dir_button.grid(row=4,column=3,padx=3,pady=3)

    def change_loc(self):
        database_path = db.ask_save_path()
        if not database_path:
            return
        self.path_var.set(database_path)


    def mode_int2str(self,int_val):
        mode_dict_int = {0:"No Encryption",1:"Name & Key",2:"All Fields"}
        str_val = mode_dict_int[int_val]
        return str_val
 
    def mode_str2int(self,str_val):
        mode_dict_str = {"No Encryption":0,"Name & Key":1,"All Fields":2}
        int_val = mode_dict_str[str_val]
        return int_val

    def check_new_password(self,event):
        if self.change_password_bool.get() == 0:
            self.entry2["state"] = "normal"
            self.entry3["state"] = "normal"
        else:
            self.entry2["state"] = "disabled"
            self.entry3["state"] = "disabled"
            self.new_password_var.set("")
            self.renew_password_var.set("")

    def getresult(self):
        old_pw = self.entry1.get()

        new_pw = self.entry2.get()
        renew_pw = self.entry3.get()
        changed_password = self.change_password_bool.get()

        pass_pad = self.entry4.get()
        data_pad = self.entry5.get()

        mode_str = self.mode_var.get()
        mode_int = self.mode_str2int(mode_str)

        database_path = self.entry7.get()

        return (old_pw,new_pw,renew_pw,changed_password,pass_pad,data_pad,mode_int,database_path)

    def validate(self):
        result = self.getresult()
        old_pw,new_pw,renew_pw,changed_password,pass_pad,data_pad,mode_int,database_path = result

        ### Password checks:

        if self.curr_password != old_pw:
            messagebox.showwarning(title="Current password mismatch.", message = "Entered password does not match the one currently in use. \n Please try again.", parent = self)
            return 0

        if new_pw != renew_pw:
            messagebox.showwarning(title="New password mismatch.",message="New password and retyped new password do not match. \n Please try again.",parent = self)
            return 0

        pass_padding_byte = pass_pad.encode(self.data.codec)
        if len(pass_padding_byte) != 1:
            messagebox.showwarning(title="Bad password padding character.",message="Password padding character must be single byte charachter.\n {} has byte lenght of {} \n Please try again.".format(pass_pad,len(pass_padding_byte)),parent = self)
            return 0

        if self.change_password_bool.get() == 1:
            password_byte = new_pw.encode(self.data.codec)
        else:
            password_byte = old_pw.encode(self.data.codec)
        if len(password_byte) > 16:
            messagebox.showwarning(title="Password is too long.",message="Password cannot exceed 16 byte charachters.\n Your password has byte character length of {} \n Please try again.".format(len(password_byte)),parent = self)
            return 0        

        ### Data padding check

        data_padding_byte = data_pad.encode(self.data.codec)
        if len(data_padding_byte) != 1:
            messagebox.showwarning(title="Bad data padding character.",message="Data padding character must be single byte charachter.\n {} has byte lenght of {} \n Please try again.".format(data_pad,len(data_padding_byte)),parent = self)
            return 0

        for item in self.data.keys:
            for key in item:
                data_pad_char_check = item[key].find(data_pad)
                if data_pad_char_check != -1:
                    messagebox.showwarning(title="Data padding character conflict.",message="Data padding character should not be used in any of the data entries. \n Please try again.",parent = self)
                    return 0

        ### Database location

        if not database_path:
            messagebox.showwarning(title="No location for database",message="Database has no location. \n Use change location button to select location.",parent = self)
            return 0

        self.result = result
        return 1  

def ask_define_database(master,curr_password,db,path,redefine):
    """
    Create dialog window and ask user to give password
    Returns:
        (username, password, load_default)
    """
    d = DefineDatabase(master,curr_password,db,path,redefine)
    return d.result



if __name__ == "__main__":

    app = tk.Tk()
    result = user_credentials(app)
    print(result)

    app.mainloop()
