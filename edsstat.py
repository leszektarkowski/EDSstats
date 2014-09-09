#!/usr/bin/env python
# -*- coding: utf-8 -*-
#ver 1.1

import sys, os
try:
    from PySide import QtGui, QtCore
    qtver = 'PySide'
except ImportError:
    import sip
    sip.setapi("QFileDialog", 2)
    sip.setapi('QString', 2)
    from PyQt4 import QtGui, QtCore
    qtver = 'PyQt4'


import eds

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        mainl = QtGui.QHBoxLayout()

        file_open_btn = QtGui.QPushButton("Open File")
        files_open_btn = QtGui.QPushButton("Open Files")
        dir_open_btn = QtGui.QPushButton("Open Folder")
        self.save_btn = QtGui.QPushButton("Save Results")

        bl = QtGui.QVBoxLayout()
        bl.addWidget(file_open_btn)
        bl.addWidget(files_open_btn)
        #bl.addWidget(dir_open_btn)
        bl.addItem(QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        bl.addWidget(self.save_btn)

        self.save_btn.hide()

        rl = QtGui.QVBoxLayout()
        self.table = QtGui.QTableWidget()
        self.res_tab = QtGui.QTableWidget()
        sizepolicy1 = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizepolicy1.setVerticalStretch(False)
        self.res_tab.setSizePolicy(sizepolicy1)
        sizepolicy2 = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizepolicy2.setVerticalStretch(True)
        self.table.setSizePolicy(sizepolicy2)
        rl.addWidget(QtGui.QLabel("Files:"))
        rl.addWidget(self.table)
        rl.addWidget(QtGui.QLabel("Statistics:"))
        rl.addWidget(self.res_tab)

        mainl.addLayout(bl)
        mainl.addLayout(rl)
        self.setLayout(mainl)
        self.resize(650, 450)
        self.setWindowTitle('EDS statistics 0.9')

        self.connect(file_open_btn,QtCore.SIGNAL('clicked()'), self.open_file)
        self.connect(files_open_btn,QtCore.SIGNAL('clicked()'), self.open_files)
        self.connect(dir_open_btn,QtCore.SIGNAL('clicked()'), self.open_dir)
        self.connect(self.save_btn,QtCore.SIGNAL('clicked()'), self.save_raport)

    def open_file(self):
        if qtver == 'PySide':
            csvfile, fil = QtGui.QFileDialog.getOpenFileName(self,
                                                      caption="Open ESD file",
                                                      filter="EDS files (*.csv)")
        else:
            csvfile = QtGui.QFileDialog.getOpenFileName(self,
                                                      caption="Open ESD file",
                                                      filter="EDS files (*.csv)")
        if csvfile:
            self.process_multiple_files([csvfile])


    def open_files(self):
        if qtver == 'PySide':
            filelist, fil = QtGui.QFileDialog.getOpenFileNames(self,
                                                      caption="Open ESD file(s)",
                                                      filter="EDS files (*.csv)")
        else:
            filelist = QtGui.QFileDialog.getOpenFileNames(self,
                                                      caption="Open ESD file(s)",
                                                      filter="EDS files (*.csv)")
        self.process_multiple_files(filelist)


    def open_dir(self):
        dir_name = QtGui.QFileDialog.getExistingDirectory(self,
                                                      caption="Select directory",
                                                      )
        if dir_name:
            files = os.listdir(dir_name)
            valid_files = [file for file in files if file[-3:] == "csv"]
            valid_files.sort()
            self.process_multiple_files(valid_files)

    def process_multiple_files(self, filelist):
        self.wt_total = {}
        number_of_samples = 0
        for csvfile in filelist:
            wt = eds.loadEDSdata(csvfile)
            if (wt.has_key('Al') & wt.has_key('O')):
                wt = eds.calcAl2O3(wt)
                self.wt_total[csvfile] = wt
                number_of_samples = number_of_samples + 1
            elif (wt.has_key('Zr') & wt.has_key('O')):
                wt = eds.calcZrO2(wt)
                self.wt_total[csvfile] = wt
                number_of_samples = number_of_samples + 1
            else:
                self.wt_total[csvfile] = wt
                number_of_samples = number_of_samples + 1
        if number_of_samples > 0:
            self.fill_table(self.wt_total)
        if number_of_samples > 2:
            self.fill_raport(self.wt_total)
        else:
            self.res_tab.setRowCount(0)


    def fill_raport(self,samples):
        self.res_tab.setColumnCount(len(self.elements.keys())*2)
        self.res_tab.setRowCount(3)
        self.res_tab.setVerticalHeaderLabels(["wt","at","vol"])
        header_keys = []
        for el in self.elements.keys():
            header_keys.append(el)
            header_keys.append("std")
        self.res_tab.setHorizontalHeaderLabels(header_keys)
        self.res_tab.resizeColumnsToContents()
        self.res_tab.resizeRowsToContents()
        self.res_tab.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.stats = eds.calcStatistics(samples)
        i = 0
        for element in self.elements.keys():
            self.res_tab.setItem(0,i*2,
                    QtGui.QTableWidgetItem("{0:.2f}".format(self.stats[element]["wt"]["mean"].nominal_value)))
            self.res_tab.setItem(0,(i*2)+1,
                    QtGui.QTableWidgetItem("{0:.2f}".format(self.stats[element]["wt"]["std"].nominal_value)))

            self.res_tab.setItem(1,i*2,
                    QtGui.QTableWidgetItem("{0:.2f}".format(self.stats[element]["at"]["mean"].nominal_value)))
            self.res_tab.setItem(1,(i*2)+1,
                    QtGui.QTableWidgetItem("{0:.2f}".format(self.stats[element]["at"]["std"].nominal_value)))

            self.res_tab.setItem(2,i*2,
                    QtGui.QTableWidgetItem("{0:.2f}".format(self.stats[element]["vol"]["mean"].nominal_value)))
            self.res_tab.setItem(2,(i*2)+1,
                    QtGui.QTableWidgetItem("{0:.2f}".format(self.stats[element]["vol"]["std"].nominal_value)))


            i += 1
        self.save_btn.show()

    def fill_table(self,wt):
        self.elements = {}
        for filename in wt:
            for wts in wt[filename]:
                if self.elements.has_key(wts):
                    pass
                else:
                    self.elements[wts] = []

        self.table.setColumnCount(len(self.elements.keys()))
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(self.elements.keys())
        filenames = []

        rc = 0
        for filename in wt:
            self.table.insertRow(self.table.rowCount())
            i = 0
            for ele in self.elements:
                if wt[filename].has_key(ele):
                    v = wt[filename][ele]
                    self.table.setItem(rc,i,
                    QtGui.QTableWidgetItem("wt: {0:.2f} +- {1:.2f}\nat: {2:.2f} +- {3:.2f}\nvol: {4:.2f} +- {5:.2f}".
                                                      format(v["wt"].nominal_value,
                                                             v["wt"].std_dev(),
                                                             v["at"].nominal_value,
                                                             v["at"].std_dev(),
                                                             v["vol"].nominal_value,
                                                             v["vol"].std_dev())))
                    i += 1
                else:
                    self.table.setItem(rc,i,
                               QtGui.QTableWidgetItem("--"))
                    i += 1
            rc += 1
            filenames.append(os.path.basename(filename))
        self.table.setVerticalHeaderLabels(filenames)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        #self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #self.table.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Interactive)

    def save_raport(self):
        foutname = QtGui.QFileDialog.getSaveFileName(self,
                                                      caption="Save results",
                                                      filter="txt files (*.dat)")
        fout = open(foutname,'w')
        quantity_type = ["wt","at","vol"]
        #print elements table: elements, then wt, at, vol percentages
        #header
        fout.write(" "*17)
        fout.write("wt     at     vol\n")
        fout.write(" "*17)
        for t in quantity_type:
            for ele in self.elements:
                fout.write("{0:>8}        u".format(ele))
        fout.write("\n")
        for filename in self.wt_total:
            fout.write("{0:15}: ".format(os.path.basename(filename)))
            for t in quantity_type:
                for ele in self.elements:
                    if self.wt_total[filename].has_key(ele):
                        v = self.wt_total[filename][ele]
                        fout.write("{0:8.2f} {1:8.2f}".
                                                          format(v[t].nominal_value,
                                                                 v[t].std_dev()))
                    else:
                        fout.write("      --       --")
            fout.write("\n")
        #statistics
        fout.write("\n\n----\nStatistics:\n")
        fout.write(" "*3)
        for ele in self.elements:
            fout.write("{0:>20}".format(ele))
        fout.write("\n")
        for t in quantity_type:
            fout.write("{0:>5}: ".format(t))
            for ele in self.elements:
                fout.write("{0:8.2f} +- {1:<8.2f}".
                                           format(self.stats[ele][t]["mean"].nominal_value,
                                                  self.stats[ele][t]["std"].nominal_value))
            fout.write("\n")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())