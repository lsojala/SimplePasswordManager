import struct


class XTEA:
    def __init__(self,key: bytes,n_rounds: int = 32, endian:str="!"):
        """
        Encryption/decryption class for eXtended Tiny Encryption Algorithm:  https://en.wikipedia.org/wiki/XTEA
        "Privacy" level of encryption. While generally regarded as safe, not necessarily suited for heavy duty secrecy.
        Arg:
            key: byte str       128 bit (byte length of 16 char) 
            n_rounds: int       Number of encryption passes, defaults to 32 (64 Feistel rounds)
            endian: str         Byte order, defaults to Big-endian/network ("!")

        c = XTEA(key)

        c.encrypt(block)
        Args:
            block: bytes         8 byte block
        Returns:                 Encrypted block
                       

        c.decrypt(block)
        Args:
            block: bytes        Encrypted 8 byte block 
        Returns:                Decrypted block

            Code based on https://code.activestate.com/recipes/496737-python-xtea-encryption/
        """
        self.rounds = n_rounds
        self.endian = endian

        self.key = key

        self.delta = 0x9e3779b9
        self.mask = 0xffffffff


    def encrypt(self,block: bytes):

        v0,v1 = struct.unpack(self.endian+"2L",block)
        k = struct.unpack(self.endian+"4L",self.key)
            
        sum = 0

        for round in range(self.rounds):
            v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & self.mask
            sum = (sum + self.delta) & self.mask
            v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & self.mask
        
        return struct.pack(self.endian+"2L",v0,v1)



    def decrypt(self,block: bytes):

        v0,v1 = struct.unpack(self.endian+"2L",block)
        k = struct.unpack(self.endian+"4L",self.key)
            
        sum = (self.delta * self.rounds) & self.mask

        for round in range(self.rounds):

            v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & self.mask
            sum = (sum - self.delta) & self.mask
            v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & self.mask

        return struct.pack(self.endian+"2L",v0,v1)




