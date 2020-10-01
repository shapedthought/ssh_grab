import paramiko
import xlsxwriter
import PySimpleGUI as sg
from pathlib import Path
import logging
import time

from paramiko import AuthenticationException

logging.basicConfig(filename='.\\issues.log', level=logging.DEBUG)

logger = logging.getLogger()
print(logger)

sg.theme('SystemDefaultForReal')


class Gui:
    """Creates the GUI"""

    def __init__(self):
        self.menu_def = [['Help', 'About...']]

        self.layout = [
            [sg.Menu(self.menu_def)],
            [sg.Text('Source IP Address file', size=(16, 1)), sg.Input(key='IPPATH'),
             sg.FileBrowse(file_types=(('Text Files', '.txt'),), )],
            [sg.Text('Disk Info Output folder', size=(16, 1)), sg.InputText(key='DISKPATH'), sg.FolderBrowse()],
            [sg.Checkbox('Use SSH Key', default=False, key='SSHCHECK', enable_events=True),
             sg.Checkbox('SSH Password', default=False, key='SSHPASS', enable_events=True, disabled=True)],
            [sg.Text('Username', size=(16, 1)), sg.InputText(key='USERNAME')],
            [sg.Text('Password', size=(16, 1)), sg.InputText(password_char='*', key='PASSWORD')],
            [sg.Text('SSH Key', size=(16, 1)), sg.InputText(key='SSHKEY', disabled=True), sg.FileBrowse(key='SSHKEYB',
                                                                                                        disabled=True)],
            [sg.Text('SSH Password', size=(16, 1)), sg.InputText(password_char='*', disabled=True, key='SSHPASSWORD')],
            [sg.Text("Log")],
            [sg.Output(size=(70, 10))],
            [sg.Submit('Submit', key='SUBMIT'), sg.Cancel('Cancel', key='CANCEL')]]

        self.window = sg.Window('SSH Grab', self.layout)


class Sshconnect:
    def __init__(self):
        # super().__init__()
        self.username = ""
        self.password = ""
        self.ipadd = []
        self.diskdata = []

    def connect(self, values):
        """Connects to each of the hosts in the hosts file"""
        try:
            path = Path(values['IPPATH'])  # change IP Address file location
        except FileNotFoundError as err:
            logger.error(err)
            raise

        with open(path, 'r') as f:
            print('Connecting to hosts')
            for ip in f:
                ip = ip.rstrip()
                ssh = paramiko.SSHClient()
                key = paramiko.RSAKey.from_private_key_file(values['SSHKEY']) if values['SSHCHECK'] else ""
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    print('Connecting to host ' + ip)
                    if values['SSHCHECK'] and values['SSHPASS']:
                        ssh.connect(hostname=ip, username=values['USERNAME'], password=values['PASSWORD'],
                                    pkey=key)
                    elif values['SSHCHECK']:
                        ssh.connect(hostname=ip, username=values['USERNAME'], pkey=key)
                    else:
                        ssh.connect(hostname=ip, username=values['USERNAME'], password=values['PASSWORD'])
                except AuthenticationException as err:
                    logger.error(err)
                    print(err)
                    return
                else:
                    print('Running disk command')
                    cmd = "df"
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    stdout = stdout.readlines()
                    for item in stdout:
                        self.ipadd.append(ip)
                        item = item.rstrip()
                        self.diskdata.append(item)
                    print('Data collected for ' + ip)
                    self.exceloutput(values)

    def exceloutput(self, values):
        """Exports the disk data out to excel file"""
        pathtoexecl = Path(values['DISKPATH'] + '/diskreport.xlsx')  # change output location
        if len(self.diskdata) > 0:
            print('Writing to excel')
            workbook = xlsxwriter.Workbook(pathtoexecl)
            worksheet = workbook.add_worksheet()
            for row_num, data in enumerate(self.ipadd):
                worksheet.write(row_num, 0, data)
            for row_num, data in enumerate(self.diskdata):
                worksheet.write(row_num, 1, data)
            workbook.close()
            print('Export finished')
        else:
            print(' Data was not collected')


def main():
    g = Gui()
    s = Sshconnect()
    check_ssh = False
    check_pass = False
    while True:
        event, values = g.window.Read()
        if event is None or event == 'CANCEL':
            break
        if event == 'SUBMIT':
            if check_ssh and not values['SSHKEY']:
                sg.popup_error('Missing SSH Key')
            elif check_pass and not values['SSHPASSWORD']:
                sg.popup_error('Missing SSH Password')
            elif not check_pass and not values['USERNAME'] or not values['PASSWORD'] or not values['IPPATH'] \
                    or not values['DISKPATH']:
                sg.popup_error('Info missing!')
                pass
            else:
                s.connect(values)
        if event == 'SSHCHECK':
            if not check_ssh:
                g.window['USERNAME'].update(disabled=True)
                g.window['PASSWORD'].update(disabled=True)
                g.window['SSHPASS'].update(disabled=False)
                g.window['SSHKEY'].update(disabled=False)
                g.window['SSHKEYB'].update(disabled=False)
                check_ssh = True
            else:
                g.window['USERNAME'].update(disabled=False)
                g.window['PASSWORD'].update(disabled=False)
                g.window['SSHPASS'].update(disabled=True)
                g.window['SSHKEY'].update(disabled=True)
                g.window['SSHKEYB'].update(disabled=True)
                check_ssh = False
        if event == 'SSHPASS':
            if not check_pass:
                g.window['SSHPASSWORD'].update(disabled=False)
                g.window['SSHCHECK'].update(disabled=True)
                check_pass = True
            else:
                g.window['SSHPASSWORD'].update(disabled=True)
                g.window['SSHCHECK'].update(disabled=False)
                check_pass = False
        if event == 'About...':
            sg.popup('This program makes it easy to grab disk information from Linux hosts.',
                     'https://github.com/shapedthought/ssh_grab')

main()
