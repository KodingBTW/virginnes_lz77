echo "Lz text inserter"
set romName="RoboCop versus The Terminator (USA) (Proto).nes"
set tblFile="encode.tbl"
:: Script1 config
set outFile1="script1.bin"
set scriptOffset1=0x5275
set scriptSize1=0x6f6
set pointerTable_1a=0x5DDE
set pointerTable_1b=0x5E40
set pointerTableSize1=0x4C
:: Script2 config
set outFile2="script2.bin"
set scriptOffset2=0x596b
set scriptSize2=0x2c4
set pointerTable_2a=0x5DD0
set pointerTable_2b=0x5e32
set pointerTableSize2=0x0E
:: Script3 config
set outFile3="script3.bin"
set scriptOffset3=0x5c2f
set scriptSize3=0x185
set pointerTable_3a=0x5DC9
set pointerTable_3b=0x5E2B
set pointerTableSize3=0x07
:loop
	pause
	Virgin_LZ77 -c %outFile1% %romName% %scriptOffset1% %scriptSize1% %pointerTable_1a% %pointerTable_1b% %pointerTableSize1% %tblFile%
	Virgin_LZ77 -c %outFile2% %romName% %scriptOffset2% %scriptSize2% %pointerTable_2a% %pointerTable_2b% %pointerTableSize2% %tblFile%
	Virgin_LZ77 -c %outFile3% %romName% %scriptOffset3% %scriptSize3% %pointerTable_3a% %pointerTable_3b% %pointerTableSize3% %tblFile%
goto :loop

