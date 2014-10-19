#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      skuncic
#
# Created:     03.01.2014
# Licence:      [] {} @ | \
'''
Universal Cyrillic decoder http://2cyr.com/decode/?lang=en
jUniConv Unicode Characters to Java Entities Converter http://itpro.cz/juniconv/
Windows 1251 CYRILLIC
'''
#-------------------------------------------------------------------------------
from Tkinter import *
import os, sys
import tkFileDialog, tkMessageBox

def main_gui(root):
    global props_type
    global src_file
    global dest_file
    global cb_rm_whitespaces
    global cb_open_txt

    f = Frame(root, width=600, height=400)

    rf = LabelFrame(f, relief=GROOVE, bd=2, text = "Props type")
    # Label(rf, text="Props type", width=18, height=2, anchor = W).pack(side=LEFT)
    props_type = IntVar()
    for text, value in [('id', 1), ('asp', 2), ('txt', 3), ('file+id', 4), ('xml', 5)]:
        Radiobutton(rf, text=text, value=value, variable=props_type).pack(side=LEFT, padx=10)
    props_type.set(1)
    rf.pack(fill = BOTH, padx=10, pady=0)

    # Checkbuttons frame
    cf = LabelFrame(f, relief=GROOVE, bd=2, text = "Options")
    # Label Remove whitespaces, checkbox
    cb_rm_whitespaces = IntVar()
    Checkbutton(cf, text = "Remove whitespaces", variable = cb_rm_whitespaces, anchor = W, \
                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)

    # Label Open txt editor, checkbox
    cb_open_txt = IntVar()
    cb_open_txt.set(0)
    Checkbutton(cf, text = "Open output in editor", variable = cb_open_txt, \
                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)
    # cf.pack(fill = BOTH, padx=5, pady=0)

    # Label Save without ids, checkbox
    cb_save_wo_ids = IntVar()
    cb_save_wo_ids.set(0)
    Checkbutton(cf, text = "Extract without ids", variable = cb_save_wo_ids, \
                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)
    # cf.pack(fill = BOTH, padx=10, pady=0)

    # Label Save without ids, checkbox
    cb_dest_in_unicode = IntVar()
    cb_dest_in_unicode.set(1)
    Checkbutton(cf, text = "Terms in unicode", variable = cb_dest_in_unicode, \
                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)
    cf.pack(fill = BOTH, padx=10, pady=0)

    # Source file frame, src_file
    sf = LabelFrame(f, relief=SUNKEN, bd=2, text = "Source File")
    # Label(sf, text="File src", width=12, height=2).pack(side=LEFT, pady=5)
    src_file = StringVar()
    Entry(sf, bd = 2, fg = "blue", width =60, textvariable=src_file).pack(side=LEFT, padx=10)
    src_file.set("Browse for source file!")
    Button(sf, text="...", command=app_browse_src).pack(side=LEFT, padx=5, pady=8)
    Button(sf, text="Extract", command=app_extract_src).pack(side=RIGHT, padx=5, pady=8)
    sf.pack(fill = BOTH, padx=10, pady=0)

    # Destination file frame, dest_file
    df = LabelFrame(f, relief=SUNKEN, bd=2, text = "Destination File")
    # Label(df, text="File dest", width=12, height=2).pack(side=LEFT, pady=5)
    dest_file = StringVar()
    Entry(df, bd = 2, fg = "blue", width =60, textvariable=dest_file).pack(side=LEFT, padx=10)
    dest_file.set("")
    Button(df, text="...", command=app_browse_dest).pack(side=LEFT, padx=5, pady=8)
    Button(df, text="Extract", command=app_extract_dest).pack(side=RIGHT, padx=5, pady=8)
    df.pack(fill = BOTH, padx=10, pady=0)

    cf = Frame(f, relief=GROOVE, borderwidth=0)
    Button(cf, text="Close", command=app_close).pack(side=RIGHT, padx=10, pady=10)
    Button(cf, text="Combine", command=app_combine).pack(side=RIGHT, padx=5, pady=8)
    Button(cf, text="Compare", command=app_compare).pack(side=RIGHT, padx=5, pady=8)

    cf.pack(fill = BOTH, padx=0)

    f.pack()

def app_browse_src():
    # http://tkinter.unpythonic.net/wiki/tkFileDialog
    global root
    global src_file

    # define options for opening a file
    options = {}
    options['defaultextension'] = '.*'
    options['filetypes'] = [('all files', '.*'), ('properties files', '.properties'), ('asp files', '.asp'), ('text files', '.txt')]
    options['initialdir'] = os.getcwd()
    options['title'] = 'Select properties source file'

    sel_file = tkFileDialog.askopenfile(mode='r', **options)
    #print sel_file.name
    if not sel_file:
        # Cancel button selected
        return
    try:
        src_file.set(sel_file.name)
        fd = open(sel_file.name)
        fd.close()
    except Exception, e:
        raise
        tkMessageBox.showerror('Error Opening Src File',
                               'Unable to open file: %r' % sel_file.name)

def app_extract_src():
    global root
    global props_type
    global cb_rm_whitespaces
    global cb_open_txt
    global src_file
    global src_dict
    '''
    '''
    try:
        fd = open(src_file.get())
        nmbs_commnets = 0
        nmbs_other = 0
        nmb = 0
        src_entry = []
        nmb_src_enties = 0
        src_dict = {}
        for src_line in fd:
            nmb += 1
            if src_line.startswith("#"):
                nmbs_commnets += 1
            elif src_line.find("=") > 1:
                src_entry=src_line.split("=")
                src_dict [src_entry[0]] = src_entry[1].rstrip('\n') # remove '\n'
                nmb_src_enties += 1
                if nmb_src_enties <= 10:
                    # encode ne dela !!!!!!!!!!!!!!
                    print "src_entry[0]", src_entry[0], "src_entry[1]", src_entry[1].encode('ascii')
            else:
                nmbs_other += 1
        fd.close()
        print "nmb_src_enties:", nmb_src_enties
        print "sys.getdefaultencoding()", sys.getdefaultencoding()
        if cb_open_txt.get() == 1:
            print "app_extract_src() - src_file.get(): ", src_file.get()
            os.system("D:\Usr\Install\Notepad2\Notepad2.exe " + src_file.get())
    except IOError, NameError:
        tkMessageBox.showerror('Error Opening Src File',
                               'Unable to open file: %r' % src_file.get())

def app_browse_dest():
    global root
    global dest_file
    print "src_file:", dest_file.get()

def app_extract_dest():
    global root
    global props_type
    global cb_rm_whitespaces
    global cb_open_txt
    global dest_file
    print "props_type:", props_type.get()
    print "cb_rm_whitespaces:", cb_rm_whitespaces.get()
    print "cb_open_txt:", cb_open_txt.get()
    print "dest_file:", dest_file.get()

def app_compare():
    global root
    print "app_compare()"

def app_combine():
    global root
    print "app_combine()"

def app_close():
    global root
    print "app_close()"
    root.destroy()

def main():
    global root
    root = Tk()
    # root.option_readfile('optionDB')
    root.title('Toplevel')
    main_gui(root)
    root.mainloop()

if __name__ == '__main__':

    main()
