# ssh_grab

This is a GUI based SSH client to grab disk information from Linux hosts in an environment. The aim being to quickly gather this information.
All you need to do is put all the IP addresses for all the systems in a text file, one per-line and ssh_grab will loop through them and output
them to an excel file.

It is written in Python 3.8 and uses:

- paramiko
- xlsxwriter
- PySimpleGUI

![](images/ssh_grab.png)

Note that though there is a dedicated ssh key and ssh password checkbox they are only needed if your key is not in the 
usual .ssh directory. Paramiko is clever is that is will always check the keys listed there before using the username
and password. This also means that if you need to use multiple keys you can place them in the .ssh directory and it
will automatically check each of them.

Logging is enabled in ssh_grab so you will find a issues.log file in the root of the directory when you run it to see
what is going on. This is set to DEBUG mode (level=logging.DEBUG), if you want to reduce this log level just remove that
string and it will go back to the default WARNING level.

The app does work but there is still a lot to test and update.