git.props.mngr
==============

Software Properties Manager

# Purpose
* to report empty keys (SW-IDs),
    compare keys in source and destination files and report keys not in both files
    File: *.cmp, Format: <SW-ID> <SRC-GUI-TXT>, Tab delimited

* to extract key-GUItxt from source and destination files
    File: *.ext, Format: <SW-ID> <SRC-GUI-TXT>, Tab delimited

* to combine keys in source and destination files
    File: *.comb, Format: <Src Dir> <File> <Ratio> <SW ID> <English> <Russian>, Tab delimited

* to generate source or destination file with contex defined in wbm_ref file from source and destination files
    File: wbm_ref_wr.ext, Format: <Src Dir> <File> <Ratio> <SW ID> <English> <Russian>, Tab delimited

* to generate source or destination file with contex defined in wbm_ref file from source and destination files
    File: wbm_ref_wr.ext, Format: <Src Dir> <File> <Ratio> <SW ID> <English> <Russian>, Tab delimited
    File: *.ext, Format: <SW-ID> <SRC-GUI-TXT> <TypesSum>, Tab delimited

* to manage all files in directory of selected source or destination file
* to support codepage converstion from UTF8 before import into Excel (*.comb)
    Note: Used mostly in case of russification.
* to open source file directory to access files

Author:   Sašo Kunčič

Date:  Apr 2014

Used Tools:
* Python Portable (2.7.6)
* py2exe
* Inno Script Studio

# Usage
1.  Select Props type:

       * propertites: *.properties files

         Format: Key=<GUI string>. Example: m.Common.Calendar=Calendar
       * xml: *.xml files. Supported formats:

         Format 1: Section / Msg - parent Name, element Id , element Name + text

         Format 2: phrases / phrase - attribure key + text

         Note: No configurable solution (=general) available yet
2.  Select options:
       * Open output in editor: to open *.extr, *.cmp or *.comb files

         Note: Notepad text editor is used.

       * Extract to file: to generate *.extr file.
       * All files in folder: to manage all files in directory of selected source or destination file.
3.  Click "..." to select source file.

       Note: If All files in folder option is selected then all files with selected Props type
             are merged into single into single file, named "_all_files_"<Directory Name>
4.  Click Extract to import keys into source keys dictionary.
5.  Click "..." to select destination file.

       Note: If All files in folder option is selected then all files with selected Props type
             are merged into single into single file, named "_all_files_"<Directory Name>
6.  Click Extract to import keys into destination keys dictionary.
7.  Click Compare to report empty keys and report keys not in both files
8.  Click Combine to combine keys in source and destination files
9.  Click UTF-8 webConv to open juniconv page in browser.
10.  Paste text from file to Input field
11.  Select Java entities >> UTF-8 text direction and click Convert
12.  Select text in Output field, copy to clipboard and paste it into spreadsheet.

##   Appendix: wbm_ref items types description

> Element consist from three main groups of items:
>  ?E - 	items in Editor (View, Insert, Modify)
>  ?F - 	items in Finder (Spreadsheet)
>  ?A - 	other items - Attributes from database IGNORE
>  Note	"?" means any character.

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