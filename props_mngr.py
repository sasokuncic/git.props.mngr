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

# define options for opening a file
options = {}
options['defaultextension'] = '.*'
options['filetypes'] = [('all files', '.*'), ('properties files', '.properties'), ('asp files', '.asp'), ('text files', '.txt')]
options['initialdir'] = os.getcwd()
options['title'] = 'Select properties source file'


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
    global options

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
    global props_type
    global src_file
    global src_dict

    src_dict = {}
    src_dict = fun_extract(src_file.get())
    fun_save_extracted(src_file.get(), src_dict)

def fun_extract(filename):
    extr_id_delimiter = "="
    extr_comments_delimiter = "#"
    try:
        nmbs_commnets = 0
        nmbs_other = 0
        nmb = 0
        nmb_src_enties1w = 0
        nmb_src_enties2w = 0

        ext_dict = {}
        src_entry = []
        fd = open(filename)
        for src_line in fd:
            nmb += 1
            src_line = src_line.rstrip('\n')
            if src_line.startswith(extr_comments_delimiter):
                nmbs_commnets += 1
            elif src_line.find("=") > 0:
                src_entry=src_line.split(extr_id_delimiter)
                if len(src_entry) == 2:
                    if src_entry[1] == '':
                        src_entry[1] = "None"
                        nmb_src_enties1w += 1
                    else:
                        nmb_src_enties2w += 1
                    ext_dict [src_entry[0]] = src_entry[1] # .encode('utf_8') # remove '\n'
                    # print "===       src_entry[0]: ", src_entry[0], "src_entry[1]: ", src_entry[1]
                elif len(src_entry) == 1:
                    ext_dict [src_entry[0]] = "None" # .encode('utf_8')
                    nmb_src_enties1w += 1
                else:
                    print "fun_extract(): Unexpected number of delimiters!", len(src_entry), "src_line(", nmb, "):", src_line
                if nmb_src_enties2w > 10000: # <= 5: # test print
                    print "src_entry[0]", src_entry[0], "src_entry[1]", src_entry[1] # .encode('utf_8')
            else:
                nmbs_other += 1
        fd.close()
        print "Number of entries:\n one-word:", nmb_src_enties1w, "\n two-words:", nmb_src_enties2w, \
                    "\n comments: ", nmbs_commnets, "\n undefined: ", nmbs_other

    except IOError, NameError:
        tkMessageBox.showerror('Error Opening File',
                               'Unable to open file: %r' % filename)
    return ext_dict

# save sorted dictionary into file
# generate .terms file with localized text onla to import it into TEXTStat
def fun_save_extracted(filename, ext_dict):
    ext_extract = ".extr"
    ext_delimiter = ":"
    ext_terms = ".terms"
    ext_cmp = ".cmp"
    ext_comb = ".comb"
    # print filename
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+ext_extract
    if os.path.isfile(fne):
            os.remove(fne)
    fnt = os.path.splitext(filename)[0]+ext_terms
    if os.path.isfile(fnt):
            os.remove(fnt)
    ldict = [x for x in ext_dict.iteritems()] # convert dictionary to the list
    if False:
        ldict.sort(key=lambda x: x[0]) # sort by key
    # write to files
    fned = open(fne, 'w')
    fntd = open(fnt, 'w')
    # Get the amount of sales for each day and write # it to the file.
    for list_element in ldict:
        fned.write(list_element[0] + ext_delimiter + list_element[1] + '\n')
        fntd.write(list_element[1] + '\n')
    # Close the file.
    fned.close()
    fntd.close()
    if cb_open_txt.get() == 1:
       os.system("D:\Usr\Install\Notepad2\Notepad2.exe " + fne)

def app_browse_dest():
    # http://tkinter.unpythonic.net/wiki/tkFileDialog
    global root
    global dest_file
    global options

    sel_file = tkFileDialog.askopenfile(mode='r', **options)
    #print sel_file.name
    if not sel_file:
        # Cancel button selected
        return
    try:
        dest_file.set(sel_file.name)
        fd = open(sel_file.name)
        fd.close()
    except Exception, e:
        raise
        tkMessageBox.showerror('Error Opening Src File',
                               'Unable to open file: %r' % sel_file.name)

def app_extract_dest():
    global props_type
    global dest_file
    global dest_dict

    dest_dict = {}
    dest_dict = fun_extract(dest_file.get())
    fun_save_extracted(dest_file.get(), dest_dict)

def app_compare():
    global root
    global src_file
    global dest_file
    global src_dict
    global dest_dict
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
