# SimplePasswordManager
Simple Password Manager (Demo)

Allows user to store passwords in a local json database.
Database is encrypted with XTEA (eXtended Tiny Encryption Algorhitm: https://en.wikipedia.org/wiki/XTEA)
While simple XTEA should provide a reasonable privacy.

The program doesn't store any information about the users. The password supplied by the user is used to decrypt the accessed database.
If the supplied password and the password used to encrypt the data are a match, the correct information is displayd. If they do not match,
user only sees falsely decrypted output:


| ![Screenshot1](/screenshots/Emmy_example.jpg) | ![Screenshot2](/screenshots/quest.jpg)                |
|---------------------------------------------- | ----------------------------------------------------- |
|Example user with correct password             | User without the correct password                     |  

The encryption program only provides security against the data being viewed by other parties. Unauthorized users can tamper with the data,
even use the program to re-encrypt it, making it unaccessible to all parties. As the databases are stored locally, it is assumed that the other parties, who have access to the filesystem, would have this capability anyway eg. by deleting the database file from the hard drive. 

If the user forgets their password, there is no way to retrieve it, short of cracking the XTEA encryption.

Requirements:
Python 3.x

### Demonstration use only is adviced.



