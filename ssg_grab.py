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
        self.layout = [
            [sg.Text('Username', size=(16, 1)), sg.InputText(key='USERNAME')],
            [sg.Text('Password', size=(16, 1)), sg.InputText(password_char='*', key='PASSWORD')],
            [sg.Text('Source IP Address file', size=(16, 1)), sg.Input(key='IPPATH'),
             sg.FileBrowse(file_types=(('Text Files', '.txt'),), )],
            [sg.Text('Disk Info Output folder', size=(16, 1)), sg.InputText(key='DISKPATH'), sg.FolderBrowse()],
            [sg.Checkbox('Use SSH Key', default=False, key='SSHCHECK'), sg.Checkbox('SSH Password', default=False,
                                                                                    key='SSHPASS')],
            [sg.Text('SSH Key', size=(16, 1)), sg.InputText(key='SSHKEY'), sg.FileBrowse()],
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
    while True:
        event, values = g.window.Read()
        if event is None or event == 'CANCEL':
            break
        if event == 'SUBMIT':
            if not values['USERNAME'] or not values['PASSWORD'] or not values['IPPATH'] or not values['DISKPATH']:
                sg.popup_error('Info missing!')
                pass
            elif values['SSHCHECK'] and not values['SSHKEY']:
                sg.popup_error('Key missing')
                pass
            else:
                s.connect(values)

main()
