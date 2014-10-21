git.props.mngr
==============

Software Properties Manager

#### Purpose
```
    * to report empty keys (SW-IDs)and compare keys in source and destination files
      and report keys not in both files
      * File: *.cmp, Format: <SW-ID> <GUI-TXT>, Tab delimited
    * to extract key-GUItxt from source and destination files
      * File: *.ext, Format: <SW-ID> <GUI-TXT>, Tab delimited
    * to combine keys in source and destination files
      * File: *.comb, Format: <Src Dir> <File> <Ratio> <SW ID> <SRC> <DEST>, Tab delimited
      Note: If the source and destination GUI-TXTS are the same, then Ratio is 0.
            The source and destination files are the same if this is true for all keys.
    * to manage all files in directory of selected source or destination file
    * to support codepage converstion from UTF8 before import into Excel (*.comb)
      Note: Used mostly in case of russification.
    * to open source file directory to access files

    * to generate source or destination file with contex defined in wbm_ref file
      from source and destination files
      * File: *.ext, Format: <SW-ID> <GUI-TXT> <TypesSum>, <Item types>, Tab delimited
    * to generate extended wbm_ref file with contex
      * File: wbm_ref_wr.ext, Format: <Src Dir> <File> <Ratio> <SW ID> <English> <Russian>, Tab delimited

    Note: Context supported features related to wbm_ref are excluded from public setup.
```
