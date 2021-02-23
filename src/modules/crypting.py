from modules.xtea import XTEA
from math import ceil


class Crypting:
    def __init__(self,passphrase: str,pass_padding:str,data_padding:str = None, encoding:str = "utf-8"):
        """
        Encryption/decryption class for arbitary string
        "Privacy" level of encryption. While generally regarded as safe, not necessarily suited for heavy duty secrecy.
        Arg:
            passphrase: str     key used to encrypt / decrypt data = 128 bit (byte length of 16 char or less) 
            pass_padding: str   Single byte charachter
            data_padding: str   Single byte charachter, defaults to pass_padding
            n_rounds: int       Number of encryption passes, defaults to 32 (64 Feistel rounds)
            encoding: str       Encoding of human-readable strings, defaults to "utf-8"
            endian: str         Byte order, defaults to Big-endian/network ("!")

        c = XTEA(*args)

        c.encrypt(string)
        Args:
            string: str           Data in a string with encoding corresponding to 'encoding' arg.
        Returns:                Encrypted data in hex string
                       

        c.decrypt(string)
        Args:
            string: str         Encrypted hex string 
        Returns:                Decrypted human-readable string

        """

        self.encoding = encoding
        self.pass_padding = pass_padding.encode(self.encoding)
        self.key = self._encode_key(passphrase)
        self.engine = XTEA(self.key)

        if data_padding == None:
            self.data_padding = self.pass_padding
        else:
            self.data_padding = data_padding.encode(self.encoding)

        if len(self.pass_padding) != 1:
            raise ValueError("Bad padding character. Padding character must have byte string length of 1. {} has byte string length of {} in {}.".format(self.pass_padding.decode(self.encoding),len(self.pass_padding),self.encoding))
        elif len(self.data_padding) != 1:
            raise ValueError("Bad padding character. Padding character must have byte string length of 1. {} has byte string length of {} in {}.".format(self.data_padding.decode(self.encoding),len(self.data_padding),self.encoding))




    def _encode_key(self,passphrase:str):
        key = passphrase.encode(self.encoding)
        if len(key) > 16:
            raise ValueError("Passphrase maximum length exceeded. Maximum byte string length is 16. {} has length of {} with {}.".format(key.decode(self.encoding),len(key),self.encoding))
        elif len(key) < 16:
            key = key.ljust(16,self.pass_padding)
        return key


    def _generate_block(self,data:bytes):
        # Calc number of blocks
        block_len = 8
        n_blocks_float = len(data)/block_len
        n_blocks = ceil(n_blocks_float)

        # Pad data to block divisable length
        pad_len = block_len * n_blocks
        data = data.ljust(pad_len,self.data_padding)

        for n in range(n_blocks):
            block = data[n*block_len : (n + 1)*block_len]
            yield block


    def _sanitize_output(self,output):
        output = output.strip(self.data_padding)
        return output


    def encrypt(self,data: str):
        data = data.encode(self.encoding)
        return_seq = bytearray()

        for block in self._generate_block(data):
                    
            return_seq += self.engine.encrypt(block)

        return_seq = return_seq.hex()

        return return_seq


    def decrypt(self,data: str):
        data = bytearray.fromhex(data)
        return_seq = bytearray()

        for block in self._generate_block(data):
            
            return_seq += self.engine.decrypt(block)

        return_seq = self._sanitize_output(return_seq)
        try:
            return_seq = return_seq.decode(self.encoding)
        except UnicodeError:
            return_seq = return_seq.hex()

        return return_seq

    def __repr__(self):
        passph = self.key.decode(self.encoding)
        pass_pad = self.pass_padding.decode(self.encoding)
        data_pad = self.data_padding.decode(self.encoding)
        return "<Crypting Obj - Passphrase: {}, Passphrase padding: {}, Data padding: {}, Encoding: {}>".format(passph,pass_pad,data_pad,self.encoding)



if __name__ == "__main__":
    """
    Test the reversibility of encrypting:
    """
    import string
    import random


    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ascii_letters = ascii_lowercase + ascii_uppercase
    scandinavian = 'ëüåäöËÜÅÄÖ'
    digits = '0123456789'
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    more_characters = "§½£€¤¨"
    one_byte = digits + ascii_letters + punctuation
    characters = digits + ascii_letters + scandinavian + punctuation + more_characters

     
    def str_gen(size=6, chars=characters):
        return ''.join(random.choice(chars) for _ in range(size))

    test_counter = 0
    error_counter = 0
    for n in range(32):
        pass_pad = str_gen(1, one_byte)
        data_pad = str_gen(1, one_byte)

        gen_password_length = int(n/2)+1
        password = str_gen(gen_password_length, characters)

        while len(password.encode("utf-8"))>16:
            password = password[:-1]

        valid_data_chars = ""
        for char in characters:
            if char == data_pad:
                continue
            valid_data_chars = "".join((valid_data_chars,char))


        c = Crypting(password,pass_pad,data_pad)
        print(c)

        for i in range(50):
            data = str_gen(random.randint(5,20), valid_data_chars)
            
            encrypted = c.encrypt(data)
            decrypted = c.decrypt(encrypted)

            if data != decrypted:
                print("Error Encrypting / decrypting data: {}".format(data))
                print("    Start and end point do not match.")
                error_counter += 1
            if encrypted == data:
                print("Error Encrypting / decrypting data: {}".format(data))
                print("    No encryption achieved.")
                error_counter += 1
            test_counter += 1
        print()
    print()
    print("Test completed:")
    print("{} errors during {} test encryptions.".format(error_counter,test_counter))