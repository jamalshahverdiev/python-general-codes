#!/usr/bin/env python
import smtplib
import os
import paramiko

codepath = os.getcwd()
outputdir = codepath+'/outdir/'

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("company.notificator@gmail.com", "CompanyEmailPASS")
# Function to get static MAC template list:
#def get_staticmacs(ip, vlanID):
#    os.system('cat outdir/'+ip+' | grep -v -i ALL | grep '+vlanID+' | awk \'{print $2 }\'')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def createMessage(mac):
    global message
    message =  """From: Company Notificator <company.notificator@gmail.com>
To: Email To <email.to@gmail.com>
Subject: Switch Port MAC address is Changed
{0} MAC address is not founded in "StaticMacs" file""".format(mac)

def macget(vlanID, ip):
    stdin, stdout, stderr = ssh.exec_command('show mac address-table vlan '+vlanID+'')
    output = stdout.readlines()

    with open(outputdir+''+ip+'', 'wb') as switchout:
        switchout.write(''.join(output))

def filterMAC(ip, vlanID):
    os.system('cat '+outputdir+'/'+ip+' | grep -v -i ALL | grep '+vlanID+' | awk \'{print $2 }\' >> '+outputdir+'/MAC.result')

iplist = open('iplist', 'r')
for ip in iplist.readlines():
    ssh.connect(''.join(ip.split()), port=22, username='switchuser', password='switchpass', look_for_keys=False, allow_agent=False)
    macget('823', ''.join(ip.split()))
    filterMAC(''.join(ip.split()), '823')


with open(outputdir+'/MAC.result', 'r') as macresult:
    for line in macresult.readlines():
        if line in open(codepath+'/StaticMacs'):
            pass
        else:
            createMessage(line.replace('\n', ''))
            server.sendmail("company.notificator@gmail.com", "email.to@gmail.com", message)
            server.quit()
            os.system('rm -rf '+outputdir+'/*')

iplist.close()
ssh.close()
