Text editor for nes virgin games, texts are compressed with LZ77 and this tool can handle that. Games mainly used:

- M.C Kids (USA)
- MCDonaldLand (Europe)
- RoboCop versus The Terminator (USA) (Proto).nes

Also the games listed used 2bytes pointers splitted, in one side LSB and other MSB, so the tool is configurated to used this format.

## Usage

Description:

```
Virgin_LZ77.py -d <romFile> <scriptStartOffset> <ScriptSize> <outFile> <tblFile>\n")
Virgin_LZ77.py -c <outFile> <romFile> <scriptOffset> <scriptSize> <pointerTable1> <pointerTable2> <pointerTableSize> <tblFile>\n")
Virgin_LZ77.py -h -? - Display help

```
pointerTable1 = staroffset LSB
pointerTable2 = staroffset MSB

You can use my GAME_NOTES.txt config

The program doesn't handle many exceptions, so try to provide the correct information to avoid issues. For more information, read the attached readme.txt.

### Instrutions

The attached files and instruccions are for RoboCop versus The Terminator (USA) (Proto).nes, but if you need for MC kids, you only need to debbug text and table offsets.

First copy all files in the same directory of the Rom, use "extract text.bat", it will create three files. Then, edit the text and the encode.tbl file. Once you're done, simply open "insert text.bat" and it will automatically insert the text.

## Frecuency Answer Questions

### Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me as contributor.

