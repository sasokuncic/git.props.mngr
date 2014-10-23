#-------------------------------------------------------------------------------
'''
##  Name:     Properties_Manager
##  Purpose:
    * to report empty keys (SW-IDs) and to compare keys in source and destination files
      and report keys not in both files
      * File: *.cmp,
      * Format: <SW-ID> <GUI-TXT>, Tab delimited
    * to extract key-GUItxt from source and destination files
      * File: *.ext, Format: <SW-ID> <GUI-TXT>, Tab delimited
    * to combine keys in source and destination files
      * File: *.comb,
      * Format: <Src Dir> <File> <Ratio> <SW ID> <SRC> <DEST>, Tab delimited
      Note: If the source and destination GUI-TXT is the same, then the Ratio is 0.
            The source and destination files are the same if this is true for all keys.
    * to manage all files in directory of selected source or destination file
    * to support codepage converstion from UTF8 before importing into Excel (*.comb)
      Note: Used mostly in case of russification.
    * to open source file directory to access files
    INTERNAL FEATURES:
    * to generate source or destination file with contex defined in wbm_ref file
      from source and destination files
      * File: *.ext,
      * Format: <SW-ID> <GUI-TXT> <TypesSum>, <Item types>, Tab delimited
    * to generate extended wbm_ref file with contex
      * File: wbm_ref_wr.ext,
      * Format: <Src Dir> <File> <Ratio> <SW ID> <English> <Russian>, Tab delimited

    Note: Context supported features related to wbm_ref are excluded from public setup.
    Note: xml_ru must be in utf8 - convert it before you use it!

##  Author:  S.Kuncic
##  Release: 3.4, 10.04.2014
##  Details:
    Additional procedure: browse for wbm_ref and click Cancel to clear wr_dict dictionary
##  Used tools:
    Python 2.7.6
    PyScripter
    py2exe: python setup.py py2exe
    Inno Script Studio
##  TBD:
##  = xml properties files general solution
##  = asp properties files support
##  = tooltip contains more ';', see more columns in xlsx file
'''
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
#-------------------------------------------------------------------------------
# application main window title
APPL_TITLE =  "Properties Manager 3.4"
## package build - True = internal, False = public
IT_PCKG = False
# used text editor
USED_EDITOR = "Notepad.exe "

## Generated files extensions
PREF_FLS_FLDR = "_all_files_" # prefix of file with all files in folder
SUFF_EXT_EXTRACT = ".extr"    # extracted keys
SUFF_EXT_TERMS = ".terms"     # not implemented (SUFF_EXT_EXTRACT used instead)
SUFF_EXT_CMP = ".cmp"         # src-dest comparision
SUFF_EXT_COMB = ".comb"       # src+dest combination
SUFF_EXT_EXTRACT_WITH_CTX = '_wr.extr' # src+ctx

PROPS_SUB_DLMTR = "."     # XML delimiter
PROPS_ID_DLMTR = "="      # delimiter between SW-ID and GUI-TXT
PROPS_COMM_1ST_CHR = "#"  # comment first char in line
PROPS_FLNM_1ST_CHR = "*"  # filename first char in line

PRP_TYP_PROPERTIES = 1
PRP_TYP_XML = 2
PRP_TYP_ASP = 3

OTFL_DLMTR = "\t"         # output files delimiter
WRFL_DLMTR = ";"          # delimiter used in wbm_ref file
OTFL_DLMTR_RPLC = "   "   # ','
EMPTY_ENTRY = "xxx"       # empty

# general parameters
SORT_DICT = False         # dictionary sort flag
SUFF_EXT_PROPS = ".properties"
SRC_LBL = 'English'       # .comb file header, source label
DST_LBL = 'Russian'       # .comb file header, destination label
#-------------------------------------------------------------------------------
# options for opening file
options = {}
options['defaultextension'] = '*.*'
## options['filetypes'] = [('properties files', '.properties'), ('asp', '.asp'), ('xml', '.xml'), ('all file types', '.*')]
options['filetypes'] = [('properties files', '.properties'), ('xml', '.xml'), ('all file types', '.*')]
options['initialdir'] = os.getcwd()
options['title'] = 'Select file with properties (select Props type checkbuttons also)'
# source definitions
src_dict = {}
src_id_in_file = {}
src_extension = ""
src_dir = ""
# destination definitions
dest_dict = {}
dest_dir = ""
# wbm_ref (context) definitions
wr_dict = {}
wr_extr_file = ""
wr_types_used = []

#-------------------------------------------------------------------------------
# Application GUI
#
def main_gui(root):
    global rb_props_type
    global src_file
    global dest_file
    global wr_file
    global cb_open_txt
    global cb_extr_to_file
    global cb_in_file_folder

    f = Frame(root, width=600, height=400)
    root.title(APPL_TITLE)

    rf = LabelFrame(f, relief=GROOVE, bd=2, text = "Props type")
    # Label(rf, text="Props type", width=18, height=2, anchor = W).pack(side=LEFT)
    rb_props_type = IntVar()
    for text, value in [('properties', PRP_TYP_PROPERTIES), ('xml', PRP_TYP_XML)]:  #, ('asp', PRP_TYP_ASP)]:
        Radiobutton(rf, text=text, value=value, variable=rb_props_type).pack(side=LEFT, padx=10)
    rb_props_type.set(PRP_TYP_PROPERTIES)
    rf.pack(fill = BOTH, padx=10, pady=0)

    # Checkbuttons frame
    cf = LabelFrame(f, relief=GROOVE, bd=2, text = "Options")

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
    cb_in_file_folder.set(0)
    Checkbutton(cf, text = "All files in folder", variable = cb_in_file_folder, \
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
    if IT_PCKG:
        wf = LabelFrame(f, relief=SUNKEN, bd=2, text = "wbm_ref.txt File")
        wr_file = StringVar()
        Entry(wf, bd = 2, fg = "blue", width =60, textvariable=wr_file).pack(side=LEFT, padx=10)
        wr_file.set("")
        Button(wf, text="...", command=app_browse_wr).pack(side=LEFT, padx=5, pady=8)
        Button(wf, text="ExtrCtx", command=app_extract_wr).pack(side=RIGHT, padx=5, pady=8)
        wf.pack(fill = BOTH, padx=10, pady=0)
    else:
        wr_file = StringVar()
        wr_file.set("")

    cf = Frame(f, relief=GROOVE, borderwidth=0)
    Button(cf, text="  Close  ", command=app_close).pack(side=RIGHT, padx=10, pady=10)
    Button(cf, text="Combine", command=app_combine).pack(side=RIGHT, padx=5, pady=8)
    Button(cf, text="Compare", command=app_compare).pack(side=RIGHT, padx=5, pady=8)
    Button(cf, text="Open Source Dir", command=app_open_srcdir).pack(side=LEFT, padx=5, pady=8)
    Button(cf, text="UTF8webConv", command=app_open_web_utf8convertert).pack(side=LEFT, padx=5, pady=8)
    cf.pack(fill = BOTH, padx=0)
    f.pack()

#-------------------------------------------------------------------------------
# Browse for source file
#    or if cb_in_file_folder selected for all files in the current directory
#                                     with the same suffix as selected file
def app_browse_src():
    global root
    global src_file
    global src_dir
    global src_extension
    global options
    global rb_props_type
    global cb_in_file_folder
    global src_id_in_file0
    global PREF_FLS_FLDR

    # For details see http://tkinter.unpythonic.net/wiki/tkFileDialog
    sel_file = tkFileDialog.askopenfile(mode='r', **options)
    if not sel_file:
        # Cancel button selected
        src_file.set('')
        return
    try:
        src_file.set(sel_file.name)
        (filepath, filename) = os.path.split(sel_file.name)
        (shortname, src_extension) = os.path.splitext(filename)
        (parent_path, src_dir) = os.path.split(filepath)
        if rb_props_type.get() == PRP_TYP_PROPERTIES and cb_in_file_folder.get():
##            print 'properties, all files in directory'
            src_id_in_file.clear()
            # combine all files with the src_extension into single file
            fne = os.path.join(filepath, PREF_FLS_FLDR + src_dir + src_extension)
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

        elif rb_props_type.get() == PRP_TYP_PROPERTIES and cb_in_file_folder.get() == 0:
##            print 'properties, single file'
            fd = open(sel_file.name) # check selected file
            fd.close()

        elif rb_props_type.get() == PRP_TYP_XML:
            print 'xml, single file. cb_in_file_folder ignored'
            # create src/dest .properties file
            # update src_/dest_file, leave rb as is
            tree = ET.parse(sel_file.name) # xml_file_asp # xml_file_mp
            xmlroot = tree.getroot()
            if xmlroot.find('Section')!=None:
                # extr_xml_mp (PQMS product):  Section / Msg - parent Name, element Id , element Name + text
                fnnew = extr_xml_mp(xmlroot, sel_file.name)
            elif xmlroot.find('phrases')!=None:
                # extr_xml_aa (AA6191AX - DSR product): find phrases / phrase - attribure key + text
                fnnew = extr_xml_aa(xmlroot, sel_file.name)
            src_file.set(fnnew)

        elif rb_props_type.get() == PRP_TYP_ASP:
            print 'asp, single file. cb_in_file_folder ignored'
            # create more language depandent .properties files *_en/_ru/_sl
            # update src_file *_en, change rb to 1
            # TBD

        else:
            print 'tkMessageBox: Not supported src input combination!'
        options['initialdir'] = src_dir

##        print 'app_browse_src(): src file name: ', src_file.get()

    except Exception, e:
        raise
        tkMessageBox.showerror('Error Opening Src File',
                               'Unable to open file: %r' % sel_file.name)

#-------------------------------------------------------------------------------
#  Replace content in xml files that cannot be translated
#
def escape_html(data):
    data = data.replace("&amp;","&").replace("&quot;",'"').replace("&gt;",">").replace("&lt;","<").replace("\n","")
    data = data.replace('\\<','<').replace('\\>','>').replace('</','<')
    data = data.replace('</i>','').replace('<br/>','').replace("<i>",'').replace("<br>",'').replace('  ',' ')
    data2 = data.strip(' ').strip(':')
    return data2

#-------------------------------------------------------------------------------
# PQMS product specific XML:
#   Section / Msg - parent Name, element Id , element Name + text
#
def extr_xml_mp(root, filename):
    global SUFF_EXT_PROPS
    global PROPS_ID_DLMTR
    global PROPS_SUB_DLMTR

    fne = os.path.splitext(filename)[0]+SUFF_EXT_PROPS
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
            fned.write(parent.attrib.get('Name') + PROPS_SUB_DLMTR \
                        + elem.attrib.get('Id') + PROPS_SUB_DLMTR \
                        + elem.attrib.get('Name') + PROPS_ID_DLMTR + str(elemstr) + '\n')
    fned.close()
    return fne

#-------------------------------------------------------------------------------
# AA6191AX - DSR product specific XML
#   find phrases / phrase - attribure key + text
def extr_xml_aa(root, filename):
    global SUFF_EXT_PROPS
    global PROPS_ID_DLMTR
    global PROPS_SUB_DLMTR

    fne = os.path.splitext(filename)[0]+SUFF_EXT_PROPS
    if os.path.isfile(fne):
        os.remove(fne)
    fned = open(fne, 'w')
    for parent in root.iterfind('phrases'):
        print parent.tag
        for elem in parent.iterfind('phrase'):
            for child in elem.getchildren():
##                print '   ID:       ', elem.attrib.get('key'), '\n   TEXT:     ', child.text
                fned.write(elem.attrib.get('key') + PROPS_ID_DLMTR \
                            + child.text + '\n')
    fned.close()
    return fne

#-------------------------------------------------------------------------------
# Open source file to extract keys
#
def app_extract_src():
    global rb_props_type
    global src_file
    global src_dict
    global src_dir
    global wr_dict
    global cb_extr_to_file
    global cb_in_file_folder

    src_dict = {}
    fn = src_file.get()
    src_dict = fun_extract(fn)
    if cb_extr_to_file.get():
        # save to .extr file
        fun_save_extracted(fn, src_dict)

#-------------------------------------------------------------------------------
# Extract properties
#
def fun_extract(filename):
    global PROPS_ID_DLMTR
    global PROPS_COMM_1ST_CHR
    global EMPTY_ENTRY
    global PROPS_FLNM_1ST_CHR
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
            if src_line.startswith(PROPS_COMM_1ST_CHR):
                nmbs_commnets += 1
            elif src_line.startswith(PROPS_FLNM_1ST_CHR):
                src_entry=src_line.split(PROPS_ID_DLMTR) # split, 3 items
                (filepath, src_entry_file) = os.path.split(src_entry [1])
                nmb_file_names += 1
                print "fun_extract(): src_entry_file=%s!" % src_entry_file
            elif src_line.find("=") > 0:
                src_entry=src_line.split(PROPS_ID_DLMTR, 1) # split using only the first delimiter !
                if len(src_entry) == 2:
                    if src_entry[1] == '':
                        src_entry[1] = EMPTY_ENTRY
                        nmb_src_enties1w += 1
                    else:
                        nmb_src_enties2w += 1
                    ext_dict [src_entry[0]] = src_entry[1] # .encode('utf_8') # remove '\n'
                    if nmb_file_names:
                        # if merged src file is reading, build id to file mapping
                        src_id_in_file[src_entry[0]] = src_entry_file
                    # print "===       src_entry[0]: ", src_entry[0], "src_entry[1]: ", src_entry[1]
                elif len(src_entry) == 1:
                    ext_dict [src_entry[0]] = EMPTY_ENTRY # .encode('utf_8')
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

#-------------------------------------------------------------------------------
# Save dictionary into SUFF_EXT_EXTRACT file
#
def fun_save_extracted(filename, pext_dict):
    global SORT_DICT
    global SUFF_EXT_EXTRACT
    global OTFL_DLMTR
    global SUFF_EXT_TERMS
    global SUFF_EXT_CMP
    global SUFF_EXT_COMB
    global USED_EDITOR
    global cb_open_txt
    global wr_types_used
    global wr_dict
    global src_id_in_file ## include id to file mapping
    NOT_FOUND = 'xxx'

    # print filename
    # print pext_dict.keys()
    fne = os.path.splitext(filename)[0]+SUFF_EXT_EXTRACT
    if os.path.isfile(fne):
            os.remove(fne)
    fnt = os.path.splitext(filename)[0]+SUFF_EXT_TERMS
    if os.path.isfile(fnt):
            os.remove(fnt)
    wr_dict_len = len(wr_dict)
    if wr_dict_len:
        wr_types_in_line = []
        wr_types_in_line2 = []
        wr_types_in_line = ['0' for x in range(len(wr_types_used))]

    ldict = [x for x in pext_dict.iteritems()] # convert dictionary to the list
    if SORT_DICT:
        ldict.sort(key=lambda x: x[0]) # sort by key
    # write to files
    fned = open(fne, 'w')

    otfl_hdr = 'SW-ID' + OTFL_DLMTR + 'GUI-TXT'
    if cb_in_file_folder.get():
        otfl_hdr = 'File' + OTFL_DLMTR + otfl_hdr
    if wr_dict_len:
        otfl_hdr = otfl_hdr + OTFL_DLMTR + 'TypesSum' + OTFL_DLMTR + OTFL_DLMTR.join(wr_types_used)
##        fned.write('SW-ID' + OTFL_DLMTR + 'GUI-TXT' + OTFL_DLMTR + 'TypesSum' \
##                    + OTFL_DLMTR + OTFL_DLMTR + OTFL_DLMTR.join(wr_types_used) + '\n')
    fned.write(otfl_hdr + '\n')

    ln = 1
##    fntd = open(fnt, 'w')
    for list_element in ldict:
        list_element_ctx = ''
        id_flnm =  ''
        if cb_in_file_folder.get():
            id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            excel_str_summ_strt = '=SUM(E'
        else:
            excel_str_summ_strt = '=SUM(D'
        if wr_dict_len:
            el_ctx = wr_dict.get(list_element[1], NOT_FOUND)
            ln += 1
            excel_str = OTFL_DLMTR + excel_str_summ_strt + str(ln) + ':AH' + str(ln) + ')' + OTFL_DLMTR
            if el_ctx == NOT_FOUND:
                list_element_ctx = excel_str + '-1'
            else:
                wr_types_in_line2 = list(wr_types_in_line)
                for elm in el_ctx:
                    i = wr_types_used.index(elm)
                    wr_types_in_line2[i] = '1'
                # simple txt extension for simple review in txt editor
##                list_element_ctx = OTFL_DLMTR + OTFL_DLMTR.join(el_ctx)
                # for filtering in Excel
                list_element_ctx = excel_str + OTFL_DLMTR.join(wr_types_in_line2)
        # because Excel import replace OTFL_DLMTR with OTFL_DLMTR_RPLC
        fned.write(id_flnm + list_element[0] + OTFL_DLMTR \
                    + list_element[1].replace(OTFL_DLMTR, OTFL_DLMTR_RPLC) \
                    + list_element_ctx + '\n')
##        fntd.write(list_element[1] + '\n')
    fned.close()
##    fntd.close()
    if cb_open_txt.get() == 1:
       os.system(USED_EDITOR + fne)

#-------------------------------------------------------------------------------
# Browse for destination file
# or if cb_in_file_folder selected for all files in the current directory
#                                  with the same suffix as selected file
def app_browse_dest():
    global root
    global dest_file
    global dest_dir
    global src_extension
    global rb_props_type
    global cb_in_file_folder
    global dest_extension
    global PREF_FLS_FLDR

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

        if rb_props_type.get() == PRP_TYP_PROPERTIES and cb_in_file_folder.get():
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
            fne = os.path.join(filepath, PREF_FLS_FLDR + dest_dir + dest_extension)
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
        elif rb_props_type.get() == PRP_TYP_PROPERTIES and cb_in_file_folder.get() == 0:
##            print 'properties, single file'
            fd = open(dest_file.get()) # check selected file
            fd.close()

        elif rb_props_type.get() == PRP_TYP_XML:
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

        elif rb_props_type.get() == PRP_TYP_ASP:
            print 'asp, single file. cb_in_file_folder ignored'
            # TBD
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

#-------------------------------------------------------------------------------
# Extract keys from destination file
#
def app_extract_dest():
    global rb_props_type
    global dest_file
    global dest_dict
    global dest_dir
    global cb_extr_to_file
    global wr_dict

    fn = dest_file.get()
##    print "dest_file_name: ", fn
    dest_dict = {}
    dest_dict = fun_extract(fn)
# save to .extr file
    if cb_extr_to_file.get():
        fun_save_extracted(fn, dest_dict)

#-------------------------------------------------------------------------------
# Compare source and destination keys and report differences
#
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

#-------------------------------------------------------------------------------
# Save comparision results
#
def fun_save_cmpared(filename, notin_dest, notin_src):
    global cb_open_txt
    global src_file
    global dest_file
    global src_dict
    global dest_dict
    global SORT_DICT
    global OTFL_DLMTR
    global SUFF_EXT_CMP
    global EMPTY_ENTRY
    global USED_EDITOR
    global cb_in_file_folder
    global src_id_in_file

    # print filename
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+SUFF_EXT_CMP
    if os.path.isfile(fne):
            os.remove(fne)

    fned = open(fne, 'w')
    id_flnm = ''
    if len(notin_dest) > 0:
        ldict = [x for x in notin_dest.iteritems()] # convert dictionary to the list
        if SORT_DICT:
            ldict.sort(key=lambda x: x[0]) # sort by key
        # write header for notin_dest
        fned.write('######### Src File' + OTFL_DLMTR + src_file.get() + '\n')
        fned.write('### Keys in src but not in dest' + OTFL_DLMTR + str(len(notin_dest)) + '\n')

        for list_element in ldict:
            if cb_in_file_folder.get():
                id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            fned.write(id_flnm + list_element[0] + OTFL_DLMTR + str(src_dict.get(list_element[0])) + '\n')

    if len(notin_src) > 0:
        ldict = [x for x in notin_src.iteritems()] # convert dictionary to the list
        if SORT_DICT:
            ldict.sort(key=lambda x: x[0]) # sort by key
        # write header for notin_src
        fned.write('######### Dest File' + OTFL_DLMTR + dest_file.get() + '\n')
        fned.write('### Keys in dest but not in src' + OTFL_DLMTR + str(len(notin_src)) + '\n')
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            fned.write(id_flnm + list_element[0] + OTFL_DLMTR + str(dest_dict.get(list_element[0])) + '\n')

    fned.write('######### Empty items report #########\n')

    # Empty items in src_dict
    emptysrc = dict([(item,src_dict[item]) for item in src_dict.keys() if (src_dict.get(item)==EMPTY_ENTRY) and (dest_dict.get(item)!=EMPTY_ENTRY)])
    if len(emptysrc) > 0:
        ldict = [x for x in emptysrc.iteritems()] # convert dictionary to the list
        if SORT_DICT:
            ldict.sort(key=lambda x: x[0]) # sort by key
        fned.write('### Empty items in src file only' + OTFL_DLMTR + str(len(emptysrc)) + '\n')
        ## xxx
        for list_element in ldict:
            if cb_in_file_folder.get():
                id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            fned.write(id_flnm + list_element[0] + OTFL_DLMTR + str(dest_dict.get(list_element[0])) + '\n')

    # Empty items in dest_dict only
    emptysrc = dict([(item,dest_dict[item]) for item in dest_dict.keys() if (src_dict.get(item)!=EMPTY_ENTRY) and (dest_dict.get(item)==EMPTY_ENTRY)])
    if len(emptysrc) > 0:
        ldict = [x for x in emptysrc.iteritems()] # convert dictionary to the list
        if SORT_DICT:
            ldict.sort(key=lambda x: x[0]) # sort by key
        fned.write('### Empty items in dest file only' + OTFL_DLMTR + str(len(emptysrc)) + '\n')

        for list_element in ldict:
            if cb_in_file_folder.get():
                id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            fned.write(id_flnm + list_element[0] + OTFL_DLMTR + str(dest_dict.get(list_element[0])) + '\n')

    # Empty items in src and dest_dict
    emptysrc = dict([(item,src_dict[item]) for item in src_dict.keys() if (src_dict.get(item)==EMPTY_ENTRY) and (dest_dict.get(item)==EMPTY_ENTRY)])
    if len(emptysrc) > 0:
        ldict = [x for x in emptysrc.iteritems()] # convert dictionary to the list
        if SORT_DICT:
            ldict.sort(key=lambda x: x[0]) # sort by key
        fned.write('### Empty items in src and dest file' + OTFL_DLMTR + str(len(emptysrc)) + '\n')

        for list_element in ldict:
            if cb_in_file_folder.get():
                id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            fned.write(id_flnm + list_element[0] + OTFL_DLMTR + str(dest_dict.get(list_element[0])) + '\n')

    semicolumns_src = dict([(item,src_dict[item]) for item in src_dict.keys() if (src_dict.get(item).find(OTFL_DLMTR)!=-1)])
    semicolumns_dest = dict([(item,dest_dict[item]) for item in dest_dict.keys() if (dest_dict.get(item).find(OTFL_DLMTR)!=-1)])

    if len(semicolumns_src) or len(semicolumns_dest):
        fned.write('######### Semicolumns (OTFL_DLMTR) found and replaced by comma (OTFL_DLMTR_RPLC) #########\n')

        fned.write('### Semicolumns in src file items: ' + OTFL_DLMTR + str(len(semicolumns_src)) + '\n')
        ldict = [x for x in semicolumns_src.iteritems()] # convert dictionary to the list
        for list_element in ldict:
            if cb_in_file_folder.get():
                id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            fned.write(id_flnm + list_element[0] + OTFL_DLMTR + str(src_dict.get(list_element[0])) + '\n')
##            list_element[1] = src_dict.get(list_element[0]).replace(OTFL_DLMTR, OTFL_DLMTR_RPLC)
            src_dict[list_element[0]] = src_dict.get(list_element[0]).replace(OTFL_DLMTR, OTFL_DLMTR_RPLC)

        fned.write('### Semicolumns in dest file items: ' + OTFL_DLMTR + str(len(semicolumns_dest)) + '\n')
        ldict = [x for x in semicolumns_dest.iteritems()] # convert dictionary to the list
        for list_element in ldict:
            if cb_in_file_folder.get():
                id_flnm = str(src_id_in_file.get(list_element[0])) + OTFL_DLMTR
            fned.write(id_flnm + list_element[0] + OTFL_DLMTR + str(dest_dict.get(list_element[0])) + '\n')
            dest_dict[list_element[0]] = src_dict.get(list_element[0]).replace(OTFL_DLMTR, OTFL_DLMTR_RPLC)
    fned.close()
    if cb_open_txt.get() == 1:
       os.system(USED_EDITOR + fne)

#-------------------------------------------------------------------------------
# Combine source and destination file
#
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

#-------------------------------------------------------------------------------
# Save sorted dictionary into file
#
def fun_save_combined(filename, intersection):
    global cb_open_txt
    global src_file
    global dest_file
    global src_dict
    global dest_dict
    global SORT_DICT
    global OTFL_DLMTR
    global SUFF_EXT_COMB
    global src_id_in_file
    global cb_in_file_folder
    global SRC_LBL
    global DST_LBL

    if not IT_PCKG:
        SRC_LBL = 'SRC'  # .comb file header, source label
        DST_LBL = 'DEST'  # .comb file header, destination label

    fne = os.path.splitext(filename)[0]+SUFF_EXT_COMB
    if os.path.isfile(fne):
        os.remove(fne)
    (filepath, filename1) = os.path.split(filename) # name of the original file
    (filepath, filename2) = os.path.split(fne)
    (filepath2, dirname) = os.path.split(filepath) # src file directory short name

    fned = open(fne, 'w')

    if len(intersection) > 0:
        ldict = [x for x in intersection.iteritems()] # convert dictionary to the list
        if SORT_DICT:
            ldict.sort(key=lambda x: x[0]) # sort by key
        # write header for intersection
        fned.write('Src Dir' + OTFL_DLMTR + 'File' + OTFL_DLMTR + 'Ratio' + OTFL_DLMTR \
                    + 'SW ID' + OTFL_DLMTR + SRC_LBL + OTFL_DLMTR + DST_LBL + '\n')
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
            fned.write(dirname + OTFL_DLMTR + filename1 + OTFL_DLMTR \
                            + src_len + OTFL_DLMTR \
                            + str(list_element[0]) + OTFL_DLMTR + str(src_dict.get(list_element[0])) \
                            + OTFL_DLMTR + str(dest_dict.get(list_element[0])) + '\n')
    fned.close()
    if cb_open_txt.get() == 1:
       os.system(USED_EDITOR + fne)

#-------------------------------------------------------------------------------
# Browse for wbm_ref file
#
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
        # TBD
        wr_dict.clear()
        wr_file.set("")
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
        # print 'app_browse_wr(): wbm_ref file name: ', wr_file.get()
    except Exception, e:
        raise
        tkMessageBox.showerror('Error Opening Src File',
                               'Unable to open file: %r' % sel_file.name)

#-------------------------------------------------------------------------------
# Extract context from wbm_ref file
#
def app_extract_wr():
    global wr_dict
    global wr_extr_file

    fname_wr = wr_file.get()
    if fname_wr != "":
        wr_dict = app_extract_wbm_ref(fname_wr)
        if len(wr_dict) > 0:
            fun_save_wr_extracted(fname_wr, wr_dict)
            if cb_open_txt.get() == 1:
                os.system(USED_EDITOR + wr_extr_file)
    else:
        tkMessageBox.showinfo('Extract context from wbm_ref.txt ', \
                "Select wbm_ref.txt file and click ExtrCtx again!")

# multiple values for one key,
class mdict(dict):
    def __setitem__(self, key, value):
        """add the given value to the list of values for this key"""
        self.setdefault(key, []).append(value)

#-------------------------------------------------------------------------------
# Extract wbm gui strings and context types from wbm_ref file
'''
    Element consists from three main groups of items:
     ?E - 	items in Editor (View, Insert, Modify)
     ?F - 	items in Finder (Spreadsheet)
     ?A - 	other items - Attributes from database IGNORE
     Note: "?" means any character.

    Each main group contains several items:
     F? = 	Field in Editor/Finder/other Attribute
     R? = 	Relation in Editor/Finder
     D? = 	Domain Name in Editor/Finder/other Attribute - IGNORE
     V? = 	Value in Editor/Finder/other Attribute - second field (IGNORE others)
     I? = 	Interval in Editor/Finder/other Attribute - IGNORE
     U? =    ???? - IGNORE

    Other items in Editor:
     TE = 	Tab
     BE = 	Border Name (start)
     bE = 	Border Name (end) - IGNORE
     RE = 	Radio button (start)
     rE = 	Radio button (end) - IGNORE
     CE = 	Check box Name
     or CE = 	Radio Button (for the CE items between "RE" and "rE" items) - CHECK GUI for RB

Note: Editor represents a window which is opened when the View, Insert or Modify is clicked.
      Finder represents a Element's spreadsheet.
      Most Iskratel's software applications are capable of generating wbm_ref file.
'''
def app_extract_wbm_ref(filename):
    global wr_types_used
    global WRFL_DLMTR

    wr_types_all = ['BE', 'DF', 'DE', 'DA', 'FA', 'FE', 'FF', 'FG', 'RE', 'RF', \
                    'TE', 'VA', 'E', 'VE', 'VF', 'EG', 'XA', 'XF', 'CE', 'XE',  \
                    'EX', 'IA', 'IE', 'IF', 'bE', 'SW', 'UE', 'UF', 'UA'
                   ]  # 29 types
    wr_types_all = ['BE', 'CE', 'E', 'EG', 'EX', 'FA', 'FE', 'FF', 'FG', 'IA',  \
                     'RE', 'RF', 'TE', 'UA', 'VA', 'VE', 'VF', 'XE', 'XF'
                   ]
    wr_types_ignored = ['DE', 'DF', 'IF', 'IE', 'UE', 'UF', 'bE', 'rE ', 'rF',  \
                         'XA', 'SW'
                       ]
    tmc_dict = {'FG':0, 'EG':1, 'E':2, 'TE':3, 'BE':4, \
                    'CE':5, 'RE':6, 'RF':7, 'FE':8, 'FF':9, 'FA':10, \
                    'VE':11, 'VF':12, 'DA':13, 'DF':14, 'DE': 15
               }
    # counters for used types in src_file
    tmc = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
            src_entry=src_line.split(WRFL_DLMTR) # split line into entries
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
##        print 'wr ignored empty lines and numeric values: ', nmbs_ignored, nmbs_ignored_integers
##        print 'wr_entry_stat: ', wr_entry_stat
##        wr_types_stat = {k: v for k, v in zip(wr_types, wr_types_cntrs)}
##        print 'wr_types_stat: ', wr_types_stat
        wr_types_used.sort()
##        print 'wr_types_used: ', wr_types_used
##        print 'Number of m.*/c.* entries: ', tmc
##        print 'm.*/c.* entries types:     ', tmc_dict.keys()
##        print "Types overview:\n ignored:", nmbs_ignored, "\n lines in file:", fdline
##                    "\n comments: ", nmbs_commnets, "\n undefined: ", nmbs_other
    except IOError, NameError:
        tkMessageBox.showerror('Error Opening File',
                               'Unable to open file: %r' % filename)
    return ext_dict

#-------------------------------------------------------------------------------
# Generate file from src or dest with context info from wbm_ref file
#
def fun_save_wr_extracted(filename, ext_dict):
    from collections import Counter

    global SUFF_EXT_EXTRACT_WITH_CTX # SUFF_EXT_EXTRACT
    global OTFL_DLMTR
    global wr_extr_file
    global wr_types_used
##    OTFL_DLMTR = ';'
    wr_types_in_line = []
    wr_types_in_line2 = []
    wr_types_in_line = ['0' for x in range(len(wr_types_used))]
##    print wr_types_used
##    print wr_types_in_line
    list_elem1 = ''
    # print ext_dict.keys()
    fne = os.path.splitext(filename)[0]+SUFF_EXT_EXTRACT_WITH_CTX
    if os.path.isfile(fne):
            os.remove(fne)
    ldict = [x for x in ext_dict.iteritems()] # convert dictionary to the list
    wr_extr_file = fne
    # write to files
    fned = open(fne, 'w')
    fned.write('SW-ID' + OTFL_DLMTR + 'TypesSum' + OTFL_DLMTR + OTFL_DLMTR.join(wr_types_used) + '\n')
##    excel_c_str = ['=SUM(C3:C20000)' for x in range(len(wr_types_used))]
##    fned.write(' ' + OTFL_DLMTR + ' ' + OTFL_DLMTR + OTFL_DLMTR.join(excel_c_str) + '\n') # fill all columns
    # output with types' array - 3 lines
    fned.write(' ' + OTFL_DLMTR + ' ' + OTFL_DLMTR + '=SUM(C3:C20000)' + '\n') # fill first column only
    ln = 2
    for list_element in ldict:
        # count, sort, remove multiplicated values
        wr_types_in_line2 = list(wr_types_in_line)
        ln += 1
        excel_str = OTFL_DLMTR + '=SUM(C' + str(ln) + ':AH' + str(ln) + ')' + OTFL_DLMTR # not used in simple type
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
            fned.write('xxx' + excel_str + OTFL_DLMTR.join(wr_types_in_line2) + '\n')
            # output simple - 1line
##            fned.write('xxx' + OTFL_DLMTR + list_elem1 + '\n')
        else:
            # output with types array - 1 line
            fned.write(list_element[0] + excel_str + OTFL_DLMTR.join(wr_types_in_line2) + '\n')
            # output simple - 1line
##            fned.write(list_element[0] + OTFL_DLMTR + list_elem1 + '\n')
    # Close the file.
    fned.close()

#-------------------------------------------------------------------------------
# Open src folder
#
def app_open_srcdir():
    global src_file
    global SUFF_EXT_COMB
    global SUFF_EXT_CMP
    global rb_props_type
    global cb_in_file_folder

    filename = src_file.get()
    if filename == "":
        tkMessageBox.showerror('Error Opening Src Directory',
                               'Source file not selected. Browse for file and click again!')
    elif os.path.isfile(filename):
        (filepath, filename) = os.path.split(filename)
        os.startfile(filepath)
    else:
        tkMessageBox.showerror('Error Opening Src Directory',
                               'Source file: %r. Browse for file again!' % filename)
##    fne = os.path.splitext(filename)[0]+SUFF_EXT_CMP
##    if os.path.isfile(fne):
##        os.system(USED_EDITOR + fne)
##
##    fne = os.path.splitext(filename)[0]+SUFF_EXT_COMB
##    if os.path.isfile(fne):
##        os.system(USED_EDITOR + fne)

#-------------------------------------------------------------------------------
# Open web page to convert content from UTF8 to suitable codepage to paste it into Excel
#
def app_open_web_utf8convertert():
    url = 'http://itpro.cz/juniconv/'
    url2 = 'http://2cyr.com/decode/?lang=en' # additonal useful
    webbrowser.open_new_tab(url)
    tkMessageBox.showinfo('Hint',
                       'Copy-Paste content to Input field, select Direction "Java entities >> UTF-8 text" and click Convert!')

#-------------------------------------------------------------------------------
def app_close():
    global root
    root.destroy()

#-------------------------------------------------------------------------------
def main():
    global root
    root = Tk()
    # root.option_readfile('optionDB')
    root.title('Toplevel')
    main_gui(root)
    root.mainloop()

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()