import json
import os
from tkinter import messagebox, filedialog
from datetime import datetime

import modules.dialogs as dialogs
from modules.crypting import Crypting


DEFAULT_DATABASE = [("JSON File", "*.json"),("Back-up File", "*.bak")]

class KeyDatabase:
    def __init__(self,passphrase:str,codec:str="",pass_pad:str="",data_pad:str="",mode:int=2,from_file:bool=False,path:str="",placeholder=False):
        """
        args:
            codec : str         Name of the coded used in human-readable strings, e.g. 'utf-8'.
            pass_pad : str      Character used to pad the passphrase to rquired length.
            data_pad : str      Character used to pad the encoded field to required length.
            mode : str          Encryption mode:
                                0   No encryption.
                                1   Encrypt username and password.
                                2   Encrypt pasword target, username and password.
            from_file : bool    Read database from a file
            path : str          Valid path for reading and saving the data.
        """

        if from_file:
            if not path or not os.path.exists(path):
                raise Exception("KeyDatabase initialized with non-existing path.")
            self.passphrase = passphrase
            self.read_db(path)
        else:
            self.passphrase = passphrase
            self.codec = codec
            self.char1 = pass_pad
            self.char2 = data_pad
            self.mode =  mode
            self.keys = []
            self.crypt = Crypting(passphrase,pass_pad,data_pad,codec)

            if mode != 0 and mode != 1 and mode != 2:
                raise ValueError("Invalid encryption mode. Encryption mode must be '0','1' or '2'")
        self.isplaceholder = placeholder


    def update_crypting(self):
        self.crypt = Crypting(passphrase = self.passphrase, 
                              pass_padding=self.char1, 
                              data_padding=self.char2, 
                              encoding=self.codec)

    def add_key(self,new_target,new_name,new_key):
        existing_key = False
        existing_key_loc = 0
        for n,item in enumerate(self.keys):
            if new_target == item["target"]:
                existing_key = True
                existing_key_loc = n

        if existing_key:
            confirm_add = messagebox.askyesno(title="Key already exists", 
                                             message="""Key for {} already exists in the database.\nDatabase can't hold multible keys for the same target.\nExisting key will be overwritten by this one.\nDo you want to continue.""".format(new_target),
                                             icon = "question")
            if not confirm_add:
                # Call dialogbox with previous values
                return

            #overwrite previous key
            self.keys.pop(existing_key_loc)

        self.keys.append({"target":new_target,"name":new_name,"key":new_key})
        
        return True

 
    def modify_key(self,old_target,new_target,new_name,new_key):
        existing_keys = []
        for item in self.keys:
            existing_keys.append(item["target"])

        if new_target != old_target and new_target in existing_keys:
            confirm_modify = messagebox.askyesno(title="Key already exists", 
                                             message="""Key for {} already exists in the database.\nDatabase can't hold multible keys for the same target.\nExisting key will be overwritten by this one.\nDo you want to continue.""".format(new_target),
                                             icon = "question")
            if not confirm_modify:
                return

        # new_data = self.prime_database(self.data["codec"],self.data["char1"],self.data["char2"],mode=self.data["mode"])
        new_keys = []

        for item in self.keys:
            if item["target"] == old_target:
                new_keys.append({"target":new_target,"name":new_name,"key":new_key})
                continue
            if item["target"] != new_target:
                new_keys.append(item)

        self.keys = new_keys
        return True


    def delete_key(self,target):
        existing_key = False
        existing_key_loc = 0
        for n,item in enumerate(self.keys):
            if target == item["target"]:
                existing_key = True
                existing_key_loc = n
        if existing_key:
            self.keys.pop(existing_key_loc)
            return True

    def _process_keys(self,keys,processor):
        """
        Processor must be either
        self.crypt.encrypt 
        or
        self.crypt.decrypt
        """
        if self.mode == 0:
            return keys
        elif self.mode == 1 or self.mode == 2:
            ret_keys = []
            for key in keys:
                entry = dict()
                if self.mode == 1:
                    entry["target"] = key["target"]
                else:
                    entry["target"] = processor(key["target"])
                entry["name"] = processor(key["name"])
                entry["key"] = processor(key["key"])
                ret_keys.append(entry)
            return ret_keys
        else:
            raise Exception("Prosessing of keys finished unsatisfactorily")

    # dict to data transform
    def read_dict(self,data_dict):
        self.codec = data_dict["codec"]
        self.char1 = data_dict["char1"]
        self.char2 = data_dict["char2"]
        self.mode =  data_dict["mode"]
        self.update_crypting()

        self.keys = self._process_keys(keys = data_dict["keys"], processor = self.crypt.decrypt)


    # data to dict transform
    def write_dict(self):

        keys = self._process_keys(keys = self.keys, processor = self.crypt.encrypt)

        data_dict = {"codec": self.codec,
                "char1": self.char1,
                "char2": self.char2,
                "mode" : self.mode,
                "keys" : keys
                }
        return data_dict

    # File handlers
    def read_db(self,path):
        with open(path,"r") as file:
            dict = json.load(file)
        self.read_dict(dict)

    def write_db(self,path):
        dict = self.write_dict()
        with open(path,"w") as file:
            json.dump(dict,file)


    def make_test(self):
        test_data = {"codec": self.codec,
                     "char1": self.char1,
                     "char2": self.char2,
                     "mode" : self.mode,
                     "keys" : [{"target":"House","name":"Owner","key":"Key"},
                               {"target":"Stables","name":"Animal","key":"Horse"},
                               {"target":"Monkey","name":"Together","key":"Strong"},
                               {"target":"Teletubby","name":"Wants","key":"DIE!"},
                               {"target":"YouTube","name":"Mr.","key":"Streamer"},
                               {"target":"Coffee","name":"Shop","key":"Creamer"},
                               {"target":"waste","name":"Cthulhu","key":"Default"},
                               {"target":"Russian","name":"Likes","key":"Boogie"},
                               {"target":"Doctor","name":"TV","key":"House"},
                               {"target":"Doctor2","name":"Brithish","key":"Who"},
                               {"target":"House2","name":"Owner","key":"Key"},
                               {"target":"Stables2","name":"Animal","key":"Horse"},
                               {"target":"Monkey2","name":"Together","key":"Strong"},
                               {"target":"Teletubby2","name":"Wants","key":"DIE!"},
                               {"target":"YouTube2","name":"Mr.","key":"Streamer"},
                               {"target":"Coffee2","name":"Shop","key":"Creamer"},
                               {"target":"waste2","name":"Cthulhu","key":"Default"},
                               {"target":"Russian2","name":"Likes","key":"Boogie"},
                               {"target":"Doctor2","name":"TV","key":"House"},
                               {"target":"Doctor22","name":"Brithish","key":"Who"},
                              ]
                     }
        self.read_dict(test_data)


# Datbase management functions
def load(path):
    with open(path,"r") as file:
        data = json.load(file)
    return data

def save(data,path):
    with open(path,"w") as file:
        json.dump(data,file)


def ask_save_path():
    database_path =  filedialog.asksaveasfilename(filetypes = DEFAULT_DATABASE, defaultextension = DEFAULT_DATABASE)
    return database_path

def ask_open_path():
    database_path =  filedialog.askopenfilename(filetypes = DEFAULT_DATABASE, defaultextension = DEFAULT_DATABASE)
    return database_path


def create_data(master, password,database_path = "",placeholder=False):

    db = KeyDatabase(passphrase = password, codec="utf-8",pass_pad="@",data_pad="{",mode=1,placeholder=True)
    
    if placeholder == True:
        return (db,database_path)

    # query options or make database parameters editable
    result = dialogs.ask_define_database(master,curr_password = password,db = db, path = database_path, redefine=False)
    
    if not result:
        return

    old_pw,_,_,_,pass_pad,data_pad,mode_int,database_path = result
    
    db = KeyDatabase(passphrase = old_pw, codec="utf-8",pass_pad=pass_pad,data_pad=data_pad,mode=mode_int)

    folder = os.path.dirname(database_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    db.write_db(database_path)

    return (db,database_path)



def load_data(master,password, default=False,username=""):

    if default and username:
        file_extension = DEFAULT_DATABASE[0][1][1:]
        working_dir = os.getcwd()
        relative_path = "./Users/{}/{}{}".format(username,username,file_extension)
        database_path = os.path.realpath(relative_path)
        if not os.path.exists(database_path):
            confirm_create = messagebox.askyesno(title="Create Database?", 
                                            message="""Default database for user {} was not found:\nDo you want to create database at {}?""".format(username,database_path),
                                            icon = "question")
            if confirm_create:
                result = create_data(master, password, database_path)
                if not result:
                    return
                database_path = result[1]
            else:
                return
    elif default and not username:
        raise ValueError("Username cannot be empty")
    else:
        database_path = ask_open_path()
        
    if not database_path:
        return

    db = KeyDatabase(passphrase = password, from_file = True,path = database_path)

    return (db,database_path)


def save_data(db,password,savepath = None):
    if savepath == None:
        database_path = ask_save_path()

        if not database_path:
            return
    else:
        database_path = savepath
    
    db.passphrase = password
    db.update_crypting()

    db.write_db(database_path)

    return (db,database_path)


def get_backup_filepath(db_path,username):
    """
    Generate unused name for database backup.
    """
    base_dir = os.path.dirname(db_path)
    backup_date = datetime.today().strftime('%Y_%m_%d')
    backup_filename_date = "_".join(("Backup",username,backup_date))
    backup_extension = DEFAULT_DATABASE[1][1][1:]
    backup_name_base = "\\".join((base_dir,backup_filename_date))
    test_filepath = "".join((backup_name_base,backup_extension))

    while os.path.exists(test_filepath):
        backup_name_base = "".join((backup_name_base,"_(Copy)"))
        test_filepath = "".join((backup_name_base,backup_extension))

    return test_filepath



def backup_data(db,password,backup_path = None):
    if backup_path == None:
        backup_path =  filedialog.asksaveasfilename(filetypes = [DEFAULT_DATABASE[1]], defaultextension = [DEFAULT_DATABASE[1]])
        if not backup_path:
            return

    save_data(db,password,savepath=backup_path)