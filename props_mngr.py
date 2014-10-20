#-------------------------------------------------------------------------------
##  Name:     Properties_Manager
##  Purpose:  Localised properties files management application
##  = to check single properties file or directory for empty ids, substitute ; with ,
##  = to compare src and dest files and report entries not in both files or directories
##  = to expand text to import it into other applications (TEXTStat...)
##  = to combine src and dest files or directories with files into single with intersedted entries
##
##  Author:   S.Kuncic
##  Created:  02.02.2014
##   xml tested, ok, ru xml must be in utf8 (convert it before you use it)
##               error - tooltip contains more ';', see more columns in xlsx file
#-------------------------------------------------------------------------------
from Tkinter import *
import os, sys
import tkFileDialog, tkMessageBox
import webbrowser
from unicodedata import name
import os.path
from os import listdir
from os.path import isfile, join
import subprocess
import xml.etree.ElementTree as ET

dict_sort = False
const_editor = "D:\Usr\Install\Notepad2\Notepad2.exe "
##const_editor = "Notepad.exe "
##const_editor = "D:\Programs\Notepad2\Notepad2.exe " # IT
ext_extract = ".extr"
ext_delimiter = ";"
ext_terms = ".terms"
ext_cmp = ".cmp"
ext_comb = ".comb"
ext_props = ".properties"
props_delimiter = "."

extr_id_delimiter = "="
extr_comments_delimiter = "#"
extr_filename_delimiter = "*"
entry_empty = 'xxx'

# define options for opening a file
options = {}
options['defaultextension'] = '*.*'
options['filetypes'] = [('all file types', '.*'), ('properties files', '.properties'), ('asp', '.asp'), ('xml', '.xml') ]
options['initialdir'] = os.getcwd()
options['title'] = 'Select properties file (select Props type checkbuttons also)'

src_dict = {}
src_id_in_file = {}
dest_dict = {}
src_dir = ""
dest_dir = ""
src_extension = ""
wr_extr_file = ""

def main_gui(root):
    global rb_props_type
    global src_file
    global dest_file
    global wr_file
    global cb_rm_whitespaces
    global cb_open_txt
    global cb_extr_to_file
    global cb_in_file_folder

    f = Frame(root, width=600, height=400)

    rf = LabelFrame(f, relief=GROOVE, bd=2, text = "Props type")
    # Label(rf, text="Props type", width=18, height=2, anchor = W).pack(side=LEFT)
    rb_props_type = IntVar()
    for text, value in [('properties', 1), ('xml', 2), ('asp', 3)]:
        Radiobutton(rf, text=text, value=value, variable=rb_props_type).pack(side=LEFT, padx=10)
    rb_props_type.set(1)
    rf.pack(fill = BOTH, padx=10, pady=0)

    # Checkbuttons frame
    cf = LabelFrame(f, relief=GROOVE, bd=2, text = "Options")
    # Label Remove whitespaces, checkbox
##    cb_rm_whitespaces = IntVar()
##    Checkbutton(cf, text = "Remove whitespaces", variable = cb_rm_whitespaces, anchor = W, \
##                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)

    # Label Open txt editor, checkbox
    cb_open_txt = IntVar()
    cb_open_txt.set(0)
    Checkbutton(cf, text = "Open output in editor", variable = cb_open_txt, \
                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)

    # Label Save without ids, checkbox
    cb_extr_to_file = IntVar()
    cb_extr_to_file.set(0)
    Checkbutton(cf, text = "Extract to file", variable = cb_extr_to_file, \
                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)

    # Label All in File folder, checkbox
    cb_in_file_folder = IntVar()
    cb_in_file_folder.set(1)
    Checkbutton(cf, text = "All in files in folder", variable = cb_in_file_folder, \
                     onvalue = 1, offvalue = 0, height=1).pack(side=LEFT, padx=5)
    cf.pack(fill = BOTH, padx=10, pady=0)

    # Source file frame, src_file
    sf = LabelFrame(f, relief=SUNKEN, bd=2, text = "Source File")
    # Label(sf, text="File src", width=12, height=2).pack(side=LEFT, pady=5)
    src_file = StringVar()
    Entry(sf, bd = 2, fg = "blue", width =60, textvariable=src_file).pack(side=LEFT, padx=10)
##    src_file.set("Browse for source file!")
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

    # wbm_ref file frame, wr_file
    wf = LabelFrame(f, relief=SUNKEN, bd=2, text = "wbm_ref.txt File")
    # Label(wf, text="File dest", width=12, height=2).pack(side=LEFT, pady=5)
    wr_file = StringVar()
    Entry(wf, bd = 2, fg = "blue", width =60, textvariable=wr_file).pack(side=LEFT, padx=10)
    wr_file.set("")
    Button(wf, text="...", command=app_browse_wr).pack(side=LEFT, padx=5, pady=8)
    Button(wf, text="ExtrCtx", command=app_extract_wr).pack(side=RIGHT, padx=5, pady=8)
    wf.pack(fill = BOTH, padx=10, pady=0)

    cf = Frame(f, relief=GROOVE, borderwidth=0)
    Button(cf, text="  Close  ", command=app_close).pack(side=RIGHT, padx=10, pady=10)
    Button(cf, text="Combine", command=app_combine).pack(side=RIGHT, padx=5, pady=8)
    Button(cf, text="Compare", command=app_compare).pack(side=RIGHT, padx=5, pady=8)
##    Button(cf, text="OpenDir", command=app_open_files).pack(side=LEFT, padx=5, pady=8)
    Button(cf, text="UTF8webConv", command=app_open_web_utf8convertert).pack(side=LEFT, padx=5, pady=8)
    cf.pack(fill = BOTH, padx=0)

    f.pack()

def app_browse_src():
    # http://tkinter.unpythonic.net/wiki/tkFileDialog
    global root
    global src_file
    global src_dir
    global src_extension
    global options
    global rb_props_type
    global cb_in_file_folder
    global src_id_in_file

    sel_file = tkFileDialog.askopenfile(mode='r', **options)
    #print sel_file.name
    if not sel_file:
        # Cancel button selected
        return
    try:
        # set src file name
        src_file.set(sel_file.name)
        # set src dirname
        (filepath, filename) = os.path.split(sel_file.name)
        (shortname, src_extension) = os.path.splitext(filename)
        (parent_path, src_dir) = os.path.split(filepath)
        if rb_props_type.get() == 1 and cb_in_file_folder.get():
##            print 'properties, all files in directory'
            src_id_in_file.clear()
            # combine all files with the src_extension into single file
            fne = os.path.join(filepath, '_all_files' + src_dir + src_extension)
##            print 'app_browse_src(): file list name: ', fne
            if os.path.isfile(fne):
                os.remove(fne)
            textfiles = [ join(filepath,f) for f in listdir(filepath) if isfile(join(filepath,f)) and src_extension in  f]
            fned = open(fne, 'w')
            fned.write('######### Merged source files with %s extension #########\n' % src_extension)
            for textfile in textfiles:
                # Important: line starts with  '*' and contains '=' delimiter
                #            for extracting textfile from merged file in fun_extract()
                #            Only file in src folder contains this additional info
                fned.write('\n*********=%s=\n' % textfile)
                fdtextfile = open(textfile, 'r')
                for src_line in fdtextfile:
                    fned.write(src_line)
                fdtextfile.close()
##                print 'app_browse_src(): textfile: ', textfile
            # set file list as selected file
            fned.close()
            src_file.set(fne)

        elif rb_props_type.get() == 1 and cb_in_file_folder.get() == 0:
##            print 'properties, single file'
            fd = open(sel_file.name) # check selected file
            fd.close()

        elif rb_props_type.get() == 2:
            print 'xml, single file. cb_in_file_folder ignored'
            # create src/dest .properties file
            # update src_/dest_file, leave rb as is
            tree = ET.parse(sel_file.name) # xml_file_asp # xml_file_mp
            xmlroot = tree.getroot()
            if xmlroot.find('Section')!=None:
                # extr_xml_mp:  Section / Msg - parent Name, element Id , element Name + text
                fnnew = extr_xml_mp(xmlroot, sel_file.name)
            elif xmlroot.find('phrases')!=None:
                # extr_xml_aa: find phrases / phrase - attribure key + text
                fnnew = extr_xml_aa(xmlroot, sel_file.name)
            src_file.set(fnnew)

        elif rb_props_type.get() == 3:
            print 'asp, single file. cb_in_file_folder ignored'
            # create more language depandent .properties files *_en/_ru/_sl
            # update src_file *_en, change rb to 1, info to

        else:
            print 'tkMessageBox: Not supported src input combination!'
        options['initialdir'] = src_dir

##        print 'app_browse_src(): src file name: ', src_file.get()

    except Exception, e:
        raise
        tkMessageBox.showerror('Error Opening Src File',
                               'Unable to open file: %r' % sel_file.name)
'''
'''
def escape_html(data):
    data = data.replace("&amp;","&").replace("&quot;",'"').replace("&gt;",">").replace("&lt;","<").replace("\n","")
    data = data.replace('\\<','<').replace('\\>','>').replace('</','<')
    data = data.replace('</i>','').replace('<br/>','').replace("<i>",'').replace("<br>",'').replace('  ',' ')
    data2 = data.strip(' ').strip(':')
    return data2

def extr_xml_mp(root, filename):
    global ext_props
    global extr_id_delimiter
    global props_delimiter

    fne = os.path.splitext(filename)[0]+ext_props
    if os.path.isfile(fne):
        os.remove(fne)
    fned = open(fne, 'w')
    for parent in root.iterfind('Section'):
##        print 'SECTION', parent.attrib.get('Name').lower()
##        print 'SECTION - keys ', parent.keys()
        for elem in parent.iterfind('Msg'):
            elemstr = escape_html(elem.text)
            loc = elemstr.find('<Content>')
            # check for ToolTip, extract Content text to supplement elem.text
            if loc >= 0:
                loc2 = elemstr.find('</Content>')
                elemstr = elemstr[loc+len('<Content>'):loc2]
##            print '   MSG - keys ', elem.keys()
##            print '   ID:       ', parent.attrib.get('Name').lower(), '.' , elem.attrib.get('Id').lower(), '.', elem.attrib.get('Name').lower(), '\n   TEXT:     ', elemstr
            fned.write(parent.attrib.get('Name') + props_delimiter \
                        + elem.attrib.get('Id') + props_delimiter \
                        + elem.attrib.get('Name') + extr_id_delimiter + str(elemstr) + '\n')
    # Close the file.
    fned.close()
    return fne

def extr_xml_aa(root, filename):
    global ext_props
    global extr_id_delimiter
    global props_delimiter

    fne = os.path.splitext(filename)[0]+ext_props
    if os.path.isfile(fne):
        os.remove(fne)
    fned = open(fne, 'w')
    for parent in root.iterfind('phrases'):
        print parent.tag
        for elem in parent.iterfind('phrase'):
            for child in elem.getchildren():
##                print '   ID:       ', elem.attrib.get('key'), '\n   TEXT:     ', child.text
                fned.write(elem.attrib.get('key') + extr_id_delimiter \
                            + child.text + '\n')
    # Close the file.
    fned.close()
    return fne

def app_extract_src():
    global rb_props_type
    global src_file
    global src_dict
    global src_dir
    global cb_extr_to_file
    global cb_in_file_folder

    src_dict = {}
    # debug xxx
##    fname_small = "D:\Portable Python 2.7.5.1\__py_term_apps\messages_en_small.properties"
##    fname = 'D:/Portable Python 2.7.5.1/__py_term_apps/messages_en.properties'
##    src_file.set('D:\Portable Python 2.7.5.1\__py_term_apps\messages_en_small.properties')
##    src_dir = "__py_term_apps"
##        (filepath, filename) = os.path.split(sel_file.name)
##        (parent_path, dirname) = os.path.split(filepath)
##        dest_dir = dirname
    fn = src_file.get()
    src_dict = fun_extract(fn)
    if cb_extr_to_file.get():
        # save to .term and .extr file
        fun_save_extracted(fn, src_dict)

def fun_extract(filename):
    global extr_id_delimiter
    global extr_comments_delimiter
    global entry_empty
    global extr_filename_delimiter
    global src_id_in_file

    try:
        nmbs_commnets = 0
        nmbs_other = 0
        nmb = 0
        nmb_src_enties1w = 0
        nmb_src_enties2w = 0
        nmb_file_names = 0

        ext_dict = {}
        src_entry = []
        src_entry_file = 'xxxfff'
        fd = open(filename)
        for src_line in fd:
            nmb += 1
            src_line = src_line.rstrip('\n')
            if src_line.startswith(extr_comments_delimiter):
                nmbs_commnets += 1
            elif src_line.startswith(extr_filename_delimiter):
                src_entry=src_line.split(extr_id_delimiter) # split, 3 items
                (filepath, src_entry_file) = os.path.split(src_entry [1])
                nmb_file_names += 1
                print "fun_extract(): src_entry_file=%s!" % src_entry_file
            elif src_line.find("=") > 0:
                src_entry=src_line.split(extr_id_delimiter, 1) # split using only the first delimiter !
                if len(src_entry) == 2:
                    if src_entry[1] == '':
                        src_entry[1] = entry_empty
                        nmb_src_enties1w += 1
                    else:
                        nmb_src_enties2w += 1
                    ext_dict [src_entry[0]] = src_entry[1] # .encode('utf_8') # remove '\n'
                    if nmb_file_names:
                        # if merged src file is reading, build id to file mapping
                        src_id_in_file[src_entry[0]] = src_entry_file
                    # print "===       src_entry[0]: ", src_entry[0], "src_entry[1]: ", src_entry[1]
                elif len(src_entry) == 1:
                    ext_dict [src_entry[0]] = entry_empty # .encode('utf_8')
                    nmb_src_enties1w += 1
                else:
                    tkMessageBox.showwarning('Ectract: warning',
                               "Unexpected number of delimiters!" + str(len(src_entry)) + "src_line(" + str(nmb) + "):" + src_line)
##                if nmb_src_enties2w > 10000: # <= 5: # test print
##                    print "src_entry[0]", src_entry[0], "src_entry[1]", src_entry[1] # .encode('utf_8')
            else:
                nmbs_other += 1
        fd.close()
        tkMessageBox.showinfo('File extracting report',
            "Number of entries:\n\n one-word:" + str(nmb_src_enties1w) + "\n two-words:" + str(nmb_src_enties2w) + \
                    "\n comments: " + str(nmbs_commnets) + "\n undefined: " +  str(nmbs_other) + \
                    "\n files (in merged file):" + str(nmb_file_names))

    except IOError, NameError:
        tkMessageBox.showerror('Error Opening File',
                               'Unable to open file: %r' % filename)
    return ext_dict

# save dictionary into file
# generate .terms file with localized text onla to import it into TEXTStat
def fun_save_extracted(filename, ext_dict):
    global dict_sort
    global ext_extract
    global ext_delimiter
    global ext_terms
    global ext_cmp
    global ext_comb

    # print filename
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+ext_extract
    if os.path.isfile(fne):
            os.remove(fne)
    fnt = os.path.splitext(filename)[0]+ext_terms
    if os.path.isfile(fnt):
            os.remove(fnt)
    ldict = [x for x in ext_dict.iteritems()] # convert dictionary to the list
    if dict_sort:
        ldict.sort(key=lambda x: x[0]) # sort by key
    # write to files
    fned = open(fne, 'w')
    fntd = open(fnt, 'w')
    for list_element in ldict:
        fned.write(list_element[0] + ext_delimiter + list_element[1] + '\n')
        fntd.write(list_element[1] + '\n')
    # Close the file.
    fned.close()
    fntd.close()
    if cb_open_txt.get() == 1:
       os.system(const_editor + fne)

def app_browse_dest():
    # http://tkinter.unpythonic.net/wiki/tkFileDialog
    global root
    global dest_file
    global dest_dir
    global src_extension
    global rb_props_type
    global cb_in_file_folder
    global dest_extension

    sel_file = tkFileDialog.askopenfile(mode='r', **options)
    if not sel_file:
        # Cancel button selected
        return
    try:
        # set dest_file name
        dest_file.set(sel_file.name)
        # set dest dirname
        (filepath, filename) = os.path.split(sel_file.name)
        (shortname, dest_extension) = os.path.splitext(filename)
        (parent_path, dest_dir) = os.path.split(filepath)

        if rb_props_type.get() == 1 and cb_in_file_folder.get():
##          print 'properties, all files in directory'
            if src_extension != dest_extension and src_extension != '' and dest_extension != '':
                tkMessageBox.showinfo('Info Opening Dest File', \
                                   "Selected extensions of src (%s) and dest (%s) files are not the same! You could proceed or browse for new file!" % (src_extension, dest_extension))
##                dest_file.set('')
##                return
            if src_dir == dest_dir and dest_dir != '':
                tkMessageBox.showerror('Error Opening Dest File in Src Folder', \
                                   "Selected file is in the same directory (%s) as src file (%s)!" % (dest_dir, src_dir))
                dest_file.set('')
                return

            # combine all files with the dest_extension into single file
            fne = os.path.join(filepath, '_all_files' + dest_extension)
##            print 'app_browse_src(): file list name: ', fne
            if os.path.isfile(fne):
                os.remove(fne)
            textfiles = [ join(filepath,f) for f in listdir(filepath) if isfile(join(filepath,f)) and dest_extension in  f]
            fned = open(fne, 'w')
            fned.write('######### Merged files with %s extension #########\n' % dest_extension)
            for textfile in textfiles:
                # Important: line starts with  '*' and contains '=' delimiter
                #            for extracting textfile from merged src file in fun_extract()
                #               Merged dest file contains '#' instead of '*'
                #            Only file in src folder contains this additional info
                fned.write('\n######### File=%s=\n' % textfile)
                fdtextfile = open(textfile, 'r')
                for src_line in fdtextfile:
                    fned.write(src_line)
                fdtextfile.close()
##                print 'app_browse_src(): textfile: ', textfile
            # set file list as selected file
            fned.close()
            dest_file.set(fne)
        elif rb_props_type.get() == 1 and cb_in_file_folder.get() == 0:
##            print 'properties, single file'
            fd = open(dest_file.get()) # check selected file
            fd.close()

        elif rb_props_type.get() == 2:
            print 'xml, single file. cb_in_file_folder ignored'
            # create dest .properties file
            # update dest_file, leave rb as is
            tree = ET.parse(sel_file.name) # xml_file_asp # xml_file_mp
            xmlroot = tree.getroot()
            if xmlroot.find('Section')!=None:
                # extr_xml_mp - MP6012AX:  Section / Msg - parent Name, element Id , element Name + text
                fnnew = extr_xml_mp(xmlroot, sel_file.name)
            elif xmlroot.find('phrases')!=None:
                # extr_xml_aa - AA6191AX: find phrases / phrase - attribure key + text
                fnnew = extr_xml_aa(xmlroot, sel_file.name)
            dest_file.set(fnnew)

        elif rb_props_type.get() == 3:
            print 'asp, single file. cb_in_file_folder ignored'
            # create more language depandent .properties files *_en/_ru/_sl
            # update src_file *_en, change rb to 1, info to

        else:
            print 'tkMessageBox: Not supported src input combination!'
        print 'app_browse_dest(): dest file name: ', dest_file.get()
    except Exception, e:
        raise
        tkMessageBox.showerror('Error Opening Dest File',
                               'Unable to open file: %r' % sel_file.name)
    options['initialdir'] = dest_dir

def app_extract_dest():
    global rb_props_type
    global dest_file
    global dest_dict
    global dest_dir
    global cb_extr_to_file

    # debug xxx
##    fname_small = "D:\Portable Python 2.7.5.1\__py_term_apps\messages_ru_id-as-str_small.properties"
##    fname = 'D:/Portable Python 2.7.5.1/__py_term_apps/messages_ru_id-as-str.properties'
##    dest_file.set('D:/Portable Python 2.7.5.1/__py_term_apps/messages_ru_id-as-str_small.properties')
##    dest_dir = "__py_term_apps"
    fn = dest_file.get()
##    print "dest_file_name: ", fn
    dest_dict = {}
    dest_dict = fun_extract(fn)
# save to .term and .extr file
    if cb_extr_to_file.get():
        fun_save_extracted(fn, dest_dict)

def app_compare():
    global root
    global src_file
    global dest_file
    global src_dict
    global dest_dict

    non_intersection_src2dest = {}
    non_intersection_dest2src = {}
    non_intersection_src2dest = {}

    if len(src_dict) > 0 and len(dest_dict) > 0:
##        # keys in both dictionaries
##        intersection = dict([(item,src_dict[item]) for item in src_dict.keys() if dest_dict.has_key(item)])
##        print "Keys in both dictionaries:", intersection
        # keys in src_dict but not in dest_dict
        non_intersection_src2dest = dict([(item,src_dict[item]) for item in src_dict.keys() if not dest_dict.has_key(item)])
##        print "Keys in src_dict but not in dest_dict:", non_intersection_src2dest
        # keys in dest_dict but not in src_dict
        non_intersection_dest2src = dict([(item,dest_dict[item]) for item in dest_dict.keys() if not src_dict.has_key(item)])
##        print "Keys in dest_dict but not in src_dict:", non_intersection_dest2src
##        non_intersection_src2dest.update(non_intersection_dest2src )
##        print "Keys not in both dictionaries:", non_intersection_src2dest
        if len(non_intersection_src2dest)==0 and len(non_intersection_dest2src)==0:
            # open dialogbox
            print "Dictionaries are the same!"
        fun_save_cmpared(src_file.get(), non_intersection_src2dest, non_intersection_dest2src)
    elif len(src_dict) > 0:
        # allow basic src file checking only
        fun_save_cmpared(src_file.get(), non_intersection_src2dest, non_intersection_dest2src)

##    if len(src_dict) == 0:
##        # dialogbox
##        print "app_compare(): Empty src_dict! Run Extract!"
##
##    if len(dest_dict) == 0:
##        # dialogbox
##        print "app_compare(): Empty dest_dict! Run Extract!"

# save sorted dictionary into file
# generate .terms file with localized text onla to import it into TEXTStat
def fun_save_cmpared(filename, notin_dest, notin_src):
    global cb_open_txt
    global src_file
    global dest_file
    global src_dict
    global dest_dict
    global dict_sort
    global ext_delimiter
    global ext_cmp
    global entry_empty
    global cb_in_file_folder
    global src_id_in_file

    # print filename
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+ext_cmp
    if os.path.isfile(fne):
            os.remove(fne)

    fned = open(fne, 'w')
    filename1 = ''
    if len(notin_dest) > 0:
        ldict = [x for x in notin_dest.iteritems()] # convert dictionary to the list
        if dict_sort:
            ldict.sort(key=lambda x: x[0]) # sort by key
        # write header for notin_dest
        fned.write('######### Src File' + ext_delimiter + src_file.get() + '\n')
        fned.write('### Keys in src but not in dest' + ext_delimiter + str(len(notin_dest)) + '\n')

        for list_element in ldict:
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0])) + ext_delimiter
            fned.write(filename1 + list_element[0] + ext_delimiter + str(src_dict.get(list_element[0])) + '\n')

    if len(notin_src) > 0:
        ldict = [x for x in notin_src.iteritems()] # convert dictionary to the list
        if dict_sort:
            ldict.sort(key=lambda x: x[0]) # sort by key
        # write header for notin_src
        fned.write('######### Dest File' + ext_delimiter + dest_file.get() + '\n')
        fned.write('### Keys in dest but not in src' + ext_delimiter + str(len(notin_src)) + '\n')
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0])) + ext_delimiter
            fned.write(filename1 + list_element[0] + ext_delimiter + str(dest_dict.get(list_element[0])) + '\n')

    fned.write('######### Empty items report #########\n')
    # Empty items in src and dest_dict
    emptysrc = dict([(item,src_dict[item]) for item in src_dict.keys() if (src_dict.get(item)==entry_empty) and (dest_dict.get(item)==entry_empty)])
    if len(emptysrc) > 0:
        ldict = [x for x in emptysrc.iteritems()] # convert dictionary to the list
        if dict_sort:
            ldict.sort(key=lambda x: x[0]) # sort by key
        fned.write('### Empty items in src and dest file' + ext_delimiter + str(len(emptysrc)) + '\n')
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0])) + ext_delimiter
            fned.write(filename1 + list_element[0] + ext_delimiter + str(dest_dict.get(list_element[0])) + '\n')

    # Empty items in dest_dict only
    emptysrc = dict([(item,dest_dict[item]) for item in dest_dict.keys() if (src_dict.get(item)!=entry_empty) and (dest_dict.get(item)==entry_empty)])
    if len(emptysrc) > 0:
        ldict = [x for x in emptysrc.iteritems()] # convert dictionary to the list
        if dict_sort:
            ldict.sort(key=lambda x: x[0]) # sort by key
        fned.write('### Empty items in dest file only' + ext_delimiter + str(len(emptysrc)) + '\n')
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0])) + ext_delimiter
            fned.write(filename1 + list_element[0] + ext_delimiter + str(dest_dict.get(list_element[0])) + '\n')

    # Empty items in src_dict
    emptysrc = dict([(item,src_dict[item]) for item in src_dict.keys() if (src_dict.get(item)==entry_empty) and (dest_dict.get(item)!=entry_empty)])
    if len(emptysrc) > 0:
        ldict = [x for x in emptysrc.iteritems()] # convert dictionary to the list
        if dict_sort:
            ldict.sort(key=lambda x: x[0]) # sort by key
        fned.write('### Empty items in src file only' + ext_delimiter + str(len(emptysrc)) + '\n')
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0])) + ext_delimiter
            fned.write(filename1 + list_element[0] + ext_delimiter + str(dest_dict.get(list_element[0])) + '\n')

    semicolumns_src = dict([(item,src_dict[item]) for item in src_dict.keys() if (src_dict.get(item).find(ext_delimiter)!=-1)])
    semicolumns_dest = dict([(item,dest_dict[item]) for item in dest_dict.keys() if (dest_dict.get(item).find(ext_delimiter)!=-1)])

    if len(semicolumns_src) or len(semicolumns_dest):
        fned.write('######### Semicolumns found and replaced by comma <,> #########\n')

        fned.write('### Semicolumns in src file items: ' + ext_delimiter + str(len(semicolumns_src)) + '\n')
        ldict = [x for x in semicolumns_src.iteritems()] # convert dictionary to the list
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0])) + ext_delimiter
            fned.write(filename1 + list_element[0] + ext_delimiter + str(src_dict.get(list_element[0])) + '\n')
##            list_element[1] = src_dict.get(list_element[0]).replace(ext_delimiter, ',')
            src_dict[list_element[0]] = src_dict.get(list_element[0]).replace(ext_delimiter, ',')

        fned.write('### Semicolumns in dest file items: ' + ext_delimiter + str(len(semicolumns_dest)) + '\n')
        ldict = [x for x in semicolumns_dest.iteritems()] # convert dictionary to the list
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0])) + ext_delimiter
            fned.write(filename1 + list_element[0] + ext_delimiter + str(dest_dict.get(list_element[0])) + '\n')
            dest_dict[list_element[0]] = src_dict.get(list_element[0]).replace(ext_delimiter, ',')

    # Close the file.
    fned.close()
    if cb_open_txt.get() == 1:
       os.system(const_editor + fne)

def app_combine():
    global root
    global src_file
    global src_dict
    global dest_dict

    if len(src_dict) > 0 and len(dest_dict) > 0:
        # keys in both dictionaries
        intersection = dict([(item,src_dict[item]) for item in src_dict.keys() if dest_dict.has_key(item)])
##        print "Keys in both dictionaries:", intersection
        if len(intersection):
            # save to file
            fun_save_combined(src_file.get(), intersection)

    if len(src_dict) == 0:
        # dialogbox
        print "app_compare(): Empty src_dict! Run Extract!"

    if len(dest_dict) == 0:
        # dialogbox
        print "app_compare(): Empty dest_dict! Run Extract!"

# save sorted dictionary into file
# generate .terms file with localized text onla to import it into TEXTStat
def fun_save_combined(filename, intersection):
    global cb_open_txt
    global src_file
    global dest_file
    global src_dict
    global dest_dict
    global dict_sort
    global ext_delimiter
    global ext_comb
    global src_id_in_file
    global cb_in_file_folder
##    global src_dir
##    global dest_dir

    # print filename
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+ext_comb
    if os.path.isfile(fne):
        os.remove(fne)
    (filepath, filename1) = os.path.split(filename) # name of the original file
    (filepath, filename2) = os.path.split(fne)
    (filepath2, dirname) = os.path.split(filepath) # src file directory short name

    fned = open(fne, 'w')

    if len(intersection) > 0:
        ldict = [x for x in intersection.iteritems()] # convert dictionary to the list
        if dict_sort:
            ldict.sort(key=lambda x: x[0]) # sort by key
        # write header for intersection
        fned.write('Src Dir' + ext_delimiter + 'File' + ext_delimiter + 'Ratio' + ext_delimiter \
                    + 'SW ID' + ext_delimiter + 'English' + ext_delimiter + 'Russian'+ '\n')
##        src_len = ''
        i = 1
        for list_element in ldict:
##            if src_len == '':
##                # write Excel ratio formula in the second line,
##                # TBD use i for each line ....
##                src_len= '=(LEN(F2)-LEN(E2))/LEN(E2)'
##            else:
##                src_len = str(len(src_dict.get(list_element[0])))
##            dest_str = dest_dict.get(list_element[0]).decode('windows-1251')
##            dest_len = str(len(dest_str)) # potrebna je konverzija v utf-8
##            s_d_ratio = "{:.0%}".format((dest_len - src_len) / src_len * 100 )
            i +=1
            src_len = "=(LEN(F%(s)s)-LEN(E%(s)s))/LEN(E%(s)s)" % {'s': str(i)} ##  Excel ratio formula
            if cb_in_file_folder.get():
                filename1 = str(src_id_in_file.get(list_element[0]))
            fned.write(dirname + ext_delimiter + filename1 + ext_delimiter \
                            + src_len + ext_delimiter \
                            + str(list_element[0]) + ext_delimiter + str(src_dict.get(list_element[0])) \
                            + ext_delimiter + str(dest_dict.get(list_element[0])) + '\n')
    # Close the file.
    fned.close()


def app_browse_wr():
    global wr_file # src_file
    global wr_dir # src_dir
    global wr_extension # src_extension
    # not used globals yet
    global options
    global rb_props_type
    global cb_in_file_folder
    global src_id_in_file

    sel_file = tkFileDialog.askopenfile(mode='r', **options)
    #print sel_file.name
    if not sel_file:
        # Cancel button selected
        return
    try:
        # set src file name
        wr_file.set(sel_file.name)
        # set src dirname
        (filepath, filename) = os.path.split(sel_file.name)
        (shortname, wr_extension) = os.path.splitext(filename)
        (parent_path, wr_dir) = os.path.split(filepath)
##        print 'properties, single file'
        fd = open(sel_file.name) # check selected file
        fd.close()
        print 'app_browse_wr(): wbm_ref file name: ', wr_file.get()
    except Exception, e:
        raise
        tkMessageBox.showerror('Error Opening Src File',
                               'Unable to open file: %r' % sel_file.name)

''' wbm_ref
Element consist from three main groups of items:
?E - 	items in Editor (View, Insert, Modify)
?F - 	items in Finder (Spreadsheet)
?A - 	other items - Attributes from database IGNORE
Note	"?" means any character.
Each main group contains several items:
F? = 	Field in Editor/Finder/other Attribute
R? = 	Relation in Editor/Finder
D? = 	Domain Name in Editor/Finder/other Attribute - IGNORE
V? = 	Value in Editor/Finder/other Attribute - second field (IGNORE others)
I? = 	Interval in Editor/Finder/other Attribute - IGNORE
U? =    ???? - IGNORE
Editor represents a window which is opened when the View, Insert or Modify button is clicked.
Finder represents a Element's spreadsheet.
Other items in Editor:
TE = 	Tab
BE = 	Border Name (start)
bE = 	Border Name (end) - IGNORE
RE = 	Radio button (start)
rE = 	Radio button (end) - IGNORE
CE = 	Check box Name
or CE = 	Radio Button (for the CE items between "RE" and "rE" items) - CHECK GUI for RB
'''

def app_extract_wr():
    global wr_dict
    global wr_extr_file

    fname_wr = wr_file.get()
    fname_wr = "D:\Portable Python 2.7.5.1\__py_term_apps\wbm_ref.txt" # for testing

    if fname_wr != "":
        wr_dict = app_extract_wbm_ref(fname_wr)
    ##    wr_dict = app_extract_wbm_ref(wr_dict.name)

        if len(wr_dict) > 0 and src_file.get() == '':
            fun_save_wr_extracted(fname_wr, wr_dict)
            if cb_open_txt.get() == 1:
                os.system(const_editor + wr_extr_file)
        elif len(src_dict) > 0 and len(wr_dict) > 0:
            print "src_file.get() not empty - add context to _ctx.extr"
            fun_save_src_ctx_extracted(src_file.get(), src_dict)
        elif src_file.get() != '' and len(wr_dict) > 0:
            tkMessageBox.showinfo('Attach context to Source file', \
                    "Extract Source file and click ExtrCtx again!")

# multiple values for one key,
class mdict(dict):
    def __setitem__(self, key, value):
        """add the given value to the list of values for this key"""
        self.setdefault(key, []).append(value)


def app_extract_wbm_ref(filename):
    global wr_types_used
    wr_types_all = ['BE', 'DF', 'DE', 'DA', 'FA', 'FE', 'FF', 'FG', 'RE', 'RF', \
                    'TE', 'VA', 'E', 'VE', 'VF', 'EG', 'XA', 'XF', 'CE', 'XE', 'EX', \
                    'IA', 'IE', 'IF', 'bE', 'SW', 'UE', 'UF', 'UA'] # 29 types

    wr_types_all = ['BE', 'CE', 'E', 'EG', 'EX', 'FA', 'FE', 'FF', 'FG', 'IA', 'RE', 'RF', 'TE', 'UA', 'VA', 'VE', 'VF', 'XE', 'XF']
    wr_types_ignored = ['DE', 'DF', 'IF', 'IE', 'UE', 'UF', 'bE', 'rE ', 'rF', 'XA', 'SW']
    tmc_dict = {'FG':0, 'EG':1, 'E':2, 'TE':3, 'BE':4, \
                    'CE':5, 'RE':6, 'RF':7, 'FE':8, 'FF':9, 'FA':10, \
                    'VE':11, 'VF':12, 'DA':13, 'DF':14, 'DE': 15 }
    tmc = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # counters for used types in src_file
    ext_delimiter = ";"

    fdline = 0
    src_entry = []
    nmbs_ignored = 0
    nmbs_ignored_integers = 0
    wr_entry_stat = [0, 0, 0, 0, 0, 0, 0, 0] # statistic numb of elem in entry
    wr_types = []       # init used types
    wr_types_cntrs = [] # init types statistic counters
    wr_types_stat = {}
    wr_types_used = []
    ext_dict = mdict() # extracted dictionary: gui string: list of types
    try:
        fd = open(filename)
        for src_line in fd:
            fdline += 1
            src_line = src_line.rstrip('\n')
            src_entry=src_line.split(ext_delimiter) # split line into entries
            wr_entry_stat[len(src_entry)] += 1 # update statistic numb of elem in entry
            if len(src_entry) > 1:
                # types statistic
                if src_entry[0] not in wr_types:
                    wr_types.append(src_entry[0])   # new type found, extend the list of used types
                    wr_types_cntrs.append(0)        # open new counter
                wr_types_cntrs[wr_types.index(src_entry[0])] += 1   # update types statistic
                #
                if src_entry[0].endswith == 'A' or src_entry[0] in wr_types_ignored:
                    nmbs_ignored += 1
                elif src_entry[1].startswith('m.'):
                    tmc[tmc_dict[src_entry[0]]] +=1
                elif len(src_entry) >= 3 and src_entry[2].startswith('m.'):
                    tmc[tmc_dict[src_entry[0]]] +=1
                elif src_entry[1].startswith('c.'):
                    tmc[tmc_dict[src_entry[0]]] +=1
                elif len(src_entry) >= 3 and src_entry[0] == 'VE' or src_entry[0] == 'VF':
                    if src_entry[2].isdigit():
                        nmbs_ignored_integers += 1
                    else:
                        ext_dict[src_entry[2]] = src_entry[0]
                        if src_entry[0] not in wr_types_used:
                            wr_types_used.append(src_entry[0])
                else:
                    if src_entry[1].isdigit():
                        nmbs_ignored_integers += 1
                    else:
                        ext_dict[src_entry[1]] = src_entry[0]
                        if src_entry[0] not in wr_types_used:
                            wr_types_used.append(src_entry[0])
##                if fdline <= 5: # test print > 100000: #
##                    print fdline, ":  src_entry[0]", src_entry[0], "src_entry[1]", src_entry[1] # .encode('utf_8')
        fd.close()
        print 'wr ignored empty lines and numeric values: ', nmbs_ignored, nmbs_ignored_integers
        print 'wr_entry_stat: ', wr_entry_stat
        wr_types_stat = {k: v for k, v in zip(wr_types, wr_types_cntrs)}
        print 'wr_types_stat: ', wr_types_stat
        wr_types_used.sort()
        print 'wr_types_used: ', wr_types_used

        print 'Number of m.*/c.* entries: ', tmc
        print 'm.*/c.* entries types:     ', tmc_dict.keys()
##        print "Types overview:\n ignored:", nmbs_ignored, "\n lines in file:", fdline
##                    "\n comments: ", nmbs_commnets, "\n undefined: ", nmbs_other

    except IOError, NameError:
        tkMessageBox.showerror('Error Opening File',
                               'Unable to open file: %r' % filename)
    return ext_dict


def fun_save_wr_extracted(filename, ext_dict):
    from collections import Counter
    global ext_extract
    global ext_delimiter
    global wr_extr_file
    global wr_types_used
    wr_types_in_line = []
    wr_types_in_line2 = []
    wr_types_in_line = ['0' for x in range(len(wr_types_used))]
    print wr_types_used
    print wr_types_in_line
    ext_extract = '_wr.extr'
    ext_delimiter = ';'
    list_elem1 = ''
    # print filename
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+ext_extract
    if os.path.isfile(fne):
            os.remove(fne)
    ldict = [x for x in ext_dict.iteritems()] # convert dictionary to the list
    wr_extr_file = fne
    # write to files
    fned = open(fne, 'w')
    fned.write('SW-ID' + ext_delimiter + 'TypesSum' + ext_delimiter + ext_delimiter.join(wr_types_used) + '\n')
##    excel_c_str = ['=SUM(C3:C20000)' for x in range(len(wr_types_used))]
##    fned.write(' ' + ext_delimiter + ' ' + ext_delimiter + ext_delimiter.join(excel_c_str) + '\n') # fill all columns
    # output with types' array - 3 lines
    fned.write(' ' + ext_delimiter + ' ' + ext_delimiter + '=SUM(C3:C20000)' + '\n') # fill first column only
    ln = 2
    for list_element in ldict:
        # count, sort, remove multiplicated values
        wr_types_in_line2 = list(wr_types_in_line)
        ln += 1
        excel_str = ext_delimiter + '=SUM(C' + str(ln) + ':AH' + str(ln) + ')' + ext_delimiter # not used in simple type
        c=Counter(list_element[1])
        # output simple - 1line
##        list_elem1 = ' '.join(c.keys())
        # output with types' array - 4 lines
        type_list = set(c.keys())
        for elm in type_list:
            i = wr_types_used.index(elm)
            wr_types_in_line2[i] = '1'
        if list_element[0]== '':
            # output with types' array - 1 line
            fned.write('xxx' + excel_str + ext_delimiter.join(wr_types_in_line2) + '\n')
            # output simple - 1line
##            fned.write('xxx' + ext_delimiter + list_elem1 + '\n')
        else:
            # output with types array - 1 line
            fned.write(list_element[0] + excel_str + ext_delimiter.join(wr_types_in_line2) + '\n')
            # output simple - 1line
##            fned.write(list_element[0] + ext_delimiter + list_elem1 + '\n')
    # Close the file.
    fned.close()


# save dictionary into file
# generate .terms file with localized text onla to import it into TEXTStat
def fun_save_src_ctx_extracted(filename, ext_dict):
    global dict_sort
    global ext_delimiter
    ext_extract_with_ctx = '_with_ctx.extr'

    # print filename
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+ext_extract_with_ctx
    if os.path.isfile(fne):
            os.remove(fne)
    ldict = [x for x in ext_dict.iteritems()] # convert dictionary to the list
    if dict_sort:
        ldict.sort(key=lambda x: x[0]) # sort by key
    # write to files
    fned = open(fne, 'w')
    for list_element in ldict:
        # check for the ctx
        list_element_ctx = ext_delimiter + '-1'
        fned.write(list_element[0] + ext_delimiter + list_element[1] + list_element_ctx + '\n')
    # Close the file.
    fned.close()
    if cb_open_txt.get() == 1:
       os.system(const_editor + fne)

def app_open_files():
    global src_file
    global ext_comb
    global ext_cmp
    global rb_props_type
    global cb_in_file_folder

    filename = src_file.get()

##    if os.path.isfile(filename):
##        (filepath, filename) = os.path.split(filename)
##        print 'filepath ', filepath
##        subprocess.Popen('explorer /select, "' + filepath + "'" )
##    else:
##        tkMessageBox.showerror('Error Opening File',
##                               'Unable to open file: %r. Browse for file again!' % filename)
##    fne = os.path.splitext(filename)[0]+ext_cmp
##    if os.path.isfile(fne):
##        os.system(const_editor + fne)
##
##    fne = os.path.splitext(filename)[0]+ext_comb
##    if os.path.isfile(fne):
##        os.system(const_editor + fne)

def app_open_web_utf8convertert():
    url = 'http://itpro.cz/juniconv/'
##    http://2cyr.com/decode/?lang=en
    webbrowser.open_new_tab(url)

def app_close():
    global root
##    print "app_close()"
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
