pyra
=========
**http://www.jaiverma.com/blog/pyra**

pyra stands for **Python Remote Access**.

pyra has a multithreaded Command and Control Server or **C2** to which multiple clients can connect and can be controlled from the C2.

The client can run on any system which supports Python which include **Windows**, **Linux**, **macOS**, **iPhone**.

>**Some supported features are:**
>- Run shell commands
>- Upload or download files
>- Screenshot
>- Brute force SSH logins from the client
>- Download iOS keychain hashes, bookmarks, calendar, SMS

---------------
>**Client Requirements:**
>- Paramiko (for SSH brute force on client)
>- pyscreenshot (for screen shots)

>**Server Requirements:**
>- texttable

------------
Usage
-----------
Run **main.py** from **server** directory to start the server. The server listens on port 9999.

Run **main.py** from **client** directory to start the client. (Make sure you edit the server address to match the IP address of your server computer)

Have a look at my blog http://www.jaiverma.com/blog/pyra to see detailed usage instructions and all features.