#
# Author: Parker Kuivila
# Email: ptk3[at]duke.edu -or- Parker.Kuivila[at]gmail.com
# Web: http://Parker.Kuivi.la
#
# A multi-platform, Python implementation of Steve
# Lambert's SelfControl app.
#

import sys
import os
import time

# Importing only specific modules from Qt will save us about 150MB of space
from PyQt4.QtCore import Qt, QTimer, SIGNAL
from PyQt4.QtGui import QPushButton, QDialog, QApplication, QSlider, QLabel, QHBoxLayout, \
QVBoxLayout, QPlainTextEdit, QLCDNumber, QMessageBox
from threading import Timer


class MainForm(QDialog):

    def __init__(self, parent=None):
        # Create our main layout for picking duration and such
        super(MainForm, self).__init__(parent)
        self.setWindowTitle("SelfRestraint")
        # Create widgets such as buttons and slider
        self.editButton = QPushButton("Edit Blocklist")
        self.startButton = QPushButton("Start")
        self.timeSlider = QSlider(Qt.Horizontal)
        self.timeLabel = QLabel('Disabled')
        # Disable start button
        self.startButton.setEnabled(False)
        # Mess with the slider
        self.timeSlider.setTickPosition(QSlider.TicksBelow)
        self.timeSlider.setTickInterval(1)
        # Edit button widths
        self.startButton.setFixedWidth(90)
        self.editButton.setFixedWidth(120)
        self.setFixedSize(600, 150)
        # Create another layout to hold bottom contents
        bottomRow = QHBoxLayout()
        layout = QVBoxLayout()
        # Add to the layout
        layout.addWidget(self.startButton, 0, Qt.AlignHCenter)
        layout.addWidget(self.timeSlider)
        bottomRow.addWidget(self.timeLabel)
        bottomRow.addWidget(self.editButton, 0, Qt.AlignRight)
        layout.addLayout(bottomRow)
        # Set layout
        self.setLayout(layout)
        # Link functions to button and slider
        self.startButton.clicked.connect(backend.startBlock)
        self.timeSlider.valueChanged.connect(self.change)
        self.editButton.clicked.connect(self.openList)

    def openList(self):
        """Show the blocklist editor"""
        list.show()

    def change(self):
        """Displays the block time on the label"""
        if self.timeSlider.value() == 0:
            self.timeLabel.setText("Disabled")
            self.startButton.setEnabled(False)
            return
        self.startButton.setEnabled(True)
        loc = self.timeSlider.value() * 15
        if ((loc - loc % 60) / 60) == 1:
                hours = str((loc - loc % 60) / 60) + " hour, "
        elif ((loc - loc % 60) / 60) == 0:
                hours = ""
        else:
                hours = str((loc - loc % 60) / 60) + " hours, "

        self.timeLabel.setText(hours + str(loc % 60) + " minutes")


class ListEditor(QDialog):

    def __init__(self, parent=None):
        """Create layout for the blocked domains"""
        super(ListEditor, self).__init__(parent)
        self.setWindowTitle("Website Blocklist")
        # Create widgets
        self.tableView = QPlainTextEdit()

        if not os.path.isfile(os.path.join(config_dir, 'blocklist')):
            self.createBlockFile()
        self.loadBlockFile()

        layout = QVBoxLayout()
        layout.addWidget(self.tableView)
        self.saveButton = QPushButton("Done")
        self.saveButton.clicked.connect(self.closeList)
        layout.addWidget(self.saveButton, 0, Qt.AlignRight)

        self.setLayout(layout)

    def loadBlockFile(self):
        """If a site block file exists, load it"""
        file = open(config_dir + "blocklist")
        self.tableView.appendPlainText(file.read())
        file.close()

    def createBlockFile(self):
        """Create a new site block file"""
        file = open(config_dir + "blocklist", 'w')
        file.write("# Add one website per line #\nexample.com\n")
        file.close()

    def updateBlocks(self):
        """Write blocked sites to file"""
        file = open(config_dir + "blocklist", 'w+')
        file.write(list.tableView.toPlainText())

    def closeList(self):
        """Hide the list & save any changes"""
        self.updateBlocks()
        list.hide()


class Backend():
    """Backend class to deal with parsing the blocked lists
    and appending them to the system hosts file"""
    def __init__(self, parent=None):
        if sys.platform.startswith('linux'):
            self.initHosts()

        elif sys.platform.startswith('darwin'):
            self.HostsFile = "/etc/hosts"

        elif sys.platform.startswith('win'):
            self.HostsFile = "C:\Windows\System32\drivers\etc\hosts"

        else:
            sys.exit(1)  # let's try to avoid breaking things

    def initHosts(self):
        """Copy the system hosts file to our temp version

        For linux, we're going to modify a tmp version of the hosts file,
        then copy it over the top of /etc/hosts. This allows us to easily
        just request sudo for the final copy operation, not the whole script.

        """
        if sys.platform.startswith('linux'):
            self.realHostsFile = "/etc/hosts"
            self.tmpHostsFile = "/tmp/etc_hosts.tmp"
            os.system('cp {0} {1}'.format(self.realHostsFile, self.tmpHostsFile))
            self.HostsFile = self.tmpHostsFile

    def startBlock(self):
        """Append the blacklisted domains to the system hosts file"""
        form.hide()
        list.close()

        hostsFile = open(self.HostsFile, "a")

        hostsFile.write("\n# PySelfControl Blocklist. NO NOT EDIT OR MODIFY THE CONTENTS OF THIS\n")
        hostsFile.write("# PySelfControl will remove the block when the timer has ended\n")
        hostsFile.write('# Block the following sites:\n')

        blockedSites = list.tableView.toPlainText()
        # remove whitespace before and after
        blockedSites = [str(site).strip() for site in blockedSites.split("\n")]
        # filter out comments and empty rows
        blockedSites = [site for site in blockedSites if (not site.startswith('#')) and site != '']
        # write out
        for sites in blockedSites:
            hostsFile.write("0.0.0.0\t" + sites + "\n")
            if sites.startswith('www.'):
                temp = sites.split('www.')[1]
                hostsFile.write("0.0.0.0\t" + temp + "\n")
            else:
                hostsFile.write("0.0.0.0\t" + "www." + sites + "\n")

        hostsFile.write("# End Blocklist")
        hostsFile.close()

        if sys.platform.startswith('linux'):
            # attempt to copy the modified hosts file over the top of the system one.
            os.system('gksudo cp {0} {1}'.format(self.tmpHostsFile, self.realHostsFile))

        self.blockTime = form.timeSlider.value() * 60 * 15
        t = Timer(self.blockTime, self.endBlock)
        t.start()
        counter.display(time.strftime('%H:%M.%S', time.gmtime(self.blockTime)))
        counter.show()
        timer = QTimer(counter)
        counter.connect(timer, SIGNAL("timeout()"), self.countDown)
        timer.start(1000)

    def countDown(self):
        self.blockTime = self.blockTime - 1
        if self.blockTime > 1:
            timestring = time.strftime('%H:%M.%S', time.gmtime(self.blockTime))
            counter.display(timestring)
        else:
            # Got to the end, bail
            sys.exit(1)

    def endBlock(self):
        """Traverse host file and remove the site blocks"""
        restoreContents = []
        ignore = False
        # Do this again here, in case the tmp file went away during the countdown
        initHosts()
        f = open(self.HostsFile, "r")  # Open File

        for line in f:
            if line == "# PySelfControl Blocklist. NO NOT EDIT OR MODIFY THE CONTENTS OF THIS\n":
                ignore = True
            if ignore == False:
                restoreContents.append(line)
            elif line == "# End Blocklist":
                ignore = False

        f.close()

        # Restore contents
        if restoreContents[len(restoreContents) - 1] == "\n":
            restoreContents.pop()  # prevent adding newlines each time

        f = open(self.HostsFile, "w")
        for line in restoreContents:
            f.write(line)
        f.close()

        if sys.platform.startswith('linux'):
            # attempt to copy the modified hosts file over the top of the system one.
            os.system('gksudo cp {0} {1}'.format(self.tmpHostsFile, self.realHostsFile))

        form.show()
        counter.hide()


if __name__ == '__main__':
    # In OS X we need to run this as root in order to block sites
    if sys.platform.startswith('darwin'):
        if os.getuid() != 0:
            old_uid = os.getuid()
            # os.chdir('../MacOS')
            # os.system("""osascript -e 'do shell script "./SelfRestraint;"  with administrator privileges'""")
            # # If running via 'python SelfRestraint.py uncomment out below, and comment out above two lines
            # # os.system("""osascript -e 'do shell script "python SelfRestraint.py"  with administrator privileges'""")
            # sys.exit(1)
    elif sys.platform.startswith('linux'):
        from xdg.BaseDirectory import *
        config_dir = os.path.join(xdg_config_home, 'SelfRestraint/')
        # print config_dir
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)

    # Create the Qt Application

    app = QApplication(sys.argv)
    backend = Backend()

    # Create and show the forms
    if sys.platform.startswith('win'):
        # Make sure the program is running w/ administrative privileges.
        # import win32api
        from win32com.shell import shell, shellcon
        if not shell.IsUserAnAdmin():
            alertBox = QMessageBox()
            alertBox.setText("You may need to run this program as an Administrator. If it doesn't work please close this program, and run it by right clicking and choose 'Run As Administrator' ")
            alertBox.show()
        #get the MS AppData directory to store data in
        config_dir = "{}\\".format(shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0))
        if not os.path.isdir("{0}{1}".format(config_dir, "SelfRestraint")):
            os.mkdir("{0}{1}".format(config_dir, "SelfRestraint"))
        config_dir = config_dir + "\\SelfRestraint\\"

    form = MainForm()
    form.show()

    list = ListEditor()
    # Run the main Qt loop
    counter = QLCDNumber()
    counter.setSegmentStyle(QLCDNumber.Filled)
    counter.setNumDigits(8)
    counter.resize(150, 60)
    sys.exit(app.exec_())
