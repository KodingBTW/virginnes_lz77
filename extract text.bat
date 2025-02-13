echo "Lz text extractor"
set romName="RoboCop versus The Terminator (USA) (Proto).nes"
set tblFile="decode.tbl"
set outFile1="script1.bin"
set outFile2="script2.bin"
set outFile3="script3.bin"
set startOffset1=0x5275
set startOffset2=0x596b
set startOffset3=0x5c2f
set size1=0x6f6
set size2=0x2c4
set size3=0x185
Virgin_LZ77.py -d %romName% %startOffset1% %size1% %outFile1% %tblFile%
Virgin_LZ77.py -d %romName% %startOffset2% %size2% %outFile2% %tblFile%
Virgin_LZ77.py -d %romName% %startOffset3% %size3% %outFile3% %tblFile%
pause