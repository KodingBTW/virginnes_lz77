## Virgin games decompressor LZ77
## Source code by koda v0.1
## Used bitstring 4.1 and python 3.7.|


import sys
import bitstring
import re
  
def read_tbl(tblFile):
    """
    Reads a .tbl file to create a character mapping table.
    
    Parameters:
        tblFile (str): The path to the .tbl file.
    
    Returns:
        dict: A dictionary with byte values (int), and strings (characters or sequences).
    """
    charTable = {}   
    with open(tblFile, "r", encoding="UTF-8") as f:
        for line in f:
            if line.startswith(";") or line.startswith("/"):
                continue  
            if "=" in line:
                hexValue, chars = line.split("=",1)
                if "~" in chars:
                    continue
                try:
                    hexValue = int(hexValue, 16)
                    chars = chars.rstrip("\n")
                    charTable[hexValue] = chars 
                except ValueError:
                    continue
    return charTable

def decompress(romFile, startOffset):
    """
    Decompresses the data from the ROM file starting at a specific offset.
    
    Parameters:
        romFile (str): The path to the ROM file.
        startOffset (int): The starting offset in the ROM to begin decompressing.
    
    Returns:
        tuple: Contains:
            - List of decompressed data (list of integers).
            - The size of the compressed data.
            - The size of the decompressed data.
    """
    BIT_PASTCOPY = 0
    BIT_LITERAL = 1

    romStream = bitstring.ConstBitStream(filename=romFile)
    romStream.bytepos += startOffset

    decomp = []

    copySourceSize = romStream.read('uint:4')
    copyLengthSize = romStream.read('uint:4')

    while True:
        nextCommand = romStream.read('bool')

        if nextCommand == BIT_PASTCOPY:
            copySource = romStream.read(copySourceSize).uint
            copyLength = romStream.read(copyLengthSize).uint
            copyLength += 3

            if copySource == 0:
                break

            for i in range(copyLength):
                decomp.append(decomp[-copySource])

        elif nextCommand == BIT_LITERAL:
            literalByte = romStream.read('uint:8')
            decomp.append(literalByte)

    romStream.bytealign()
    endOffset = romStream.bytepos
    compress_size = endOffset - startOffset
    decompress_size = len(decomp)

    return decomp, compress_size, decompress_size

def get_decode_text(byte_value):
    """
    Returns the decoded text for a given byte value using the character table.
    
    Parameters:
        byte_value (int): The byte value to decode.
    
    Returns:
        str: The decoded string or a placeholder for unrecognized byte values.
    """
    char_table = read_tbl(tbl_file)
    if byte_value in char_table:
        return char_table[byte_value]
    else:
        return f"~{byte_value:02X}~"

def format_text(data, line_breaker):
    """
    Formats a list of decoded text bytes into a list of strings, with line breaks at the specified breaker.
    
    Parameters:
        data (list): The list of decoded byte values.
        line_breaker (int): The byte value that indicates the end of a line.
    
    Returns:
        list: A list of formatted strings with line breaks.
    """
    decode_text = [get_decode_text(byte) for byte in data]
    
    line_breaker = get_decode_text(line_breaker) 
    
    script = []
    line = []
    i = 0
    while i < len(decode_text):
        char = decode_text[i]
        if char == line_breaker:
            line.append(line_breaker)            
            script.append(''.join(line))
            line = []  
        else:
            line.append(char)
        i += 1
        
    return script

def write_out_file(file, scriptText):
    """
    Writes formatted script text to a file, adding line numbers and specific markers for each line.
    
    Parameters:
        file (str): The path to the output file.
        scriptText (list): A list of strings representing the script content to write to the file.
    """
    with open(file, "w", encoding='UTF-8') as f:
        i = 0
        for line in scriptText:
            f.write(f"@{i+1}\n")
            f.write(f";{line}\n")
            f.write(f"{line}\n")
            f.write("|\n")
            i += 1

##compress
def readScriptFile(file):
    """
    Reads a script file and returns a list of non-commented lines of text.
    
    Parameters:
        file (str): The path to the script file.
    
    Returns:
        list: A list of strings representing the lines of text from the script.
    """
    with open(file, "r", encoding='utf-8') as f:
        script = []
        for line in f.readlines():
            line = line.rstrip("\n")  
            if line.startswith(";") or line.startswith("@") or line.startswith("|"):
                continue
            script.append(line)
    return script

def encode_chars(script, tbl_file):
    """
    Converts a list of text into hexadecimal values using the tbl dictionary,
    and also creates a frequency histogram of the characters.
    
    Parameters:
        script (list): List of strings (the script to be compressed).
        tbl_file (str): .tbl file containing the character table.
    
    Returns:
        tuple: 
            - A list (int) of hexadecimal values.
    """
    char_table = read_tbl(tbl_file)
    encoded_script = []
    hex_format = r'~([0-9A-Fa-f]{2})~'
    
    for line in script:
        byte_values = []
        matches = re.findall(hex_format, line)     
        for match in matches:
            hex_value = int(match, 16)
            line = line.replace(f"~{match}~", chr(hex_value))

        for char in line:
            if char in char_table.values():
                hex_value = [k for k, v in char_table.items() if v == char][0]
                byte_values.append(hex_value)
            else:
                byte_value = ord(char)
                byte_values.append(byte_value)

        encoded_script.append(byte_values)
        
    return encoded_script

def calculate_ptr_table(decompressed_text, base):
    """
    Calculates a pointer table for the decompressed script.
    
    Parameters:
        decompressed_text (list): A list of byte values representing the decompressed script.
        line_breaker (int): The byte value indicating the end of a line.
        base (int): The base address used to calculate the pointers.
    
    Returns:
        tuple: 
            - A bytearray with the LSB (Least Significant Byte) values of the pointers.
            - A bytearray with the MSB (Most Significant Byte) values of the pointers.
            - The number of pointers calculated.
    """
    cumulative_length = [0]
    total_length = 0 
    
    for line in decompressed_text:
        total_length += len(line)
        cumulative_length.append(total_length)

    cumulative_length.pop()

    little_endian_lsb = bytearray() 
    little_endian_msb = bytearray() 
    
    for length in cumulative_length:
        pointer = length + base 
        lsb = pointer & 0xFF
        msb = (pointer >> 8) & 0xFF 
        little_endian_lsb.append(lsb)  
        little_endian_msb.append(msb) 

    return little_endian_lsb, little_endian_msb, len(cumulative_length)

def compress(data):
    """
    Compresses a list of byte values using a modified LZ77 compression algorithm.
    
    Parameters:
        data (list): The list of bytes to compress.
    
    Returns:
        tuple:
            - A bytearray containing the compressed data.
            - The size of the compressed data.
    """
    # Format in one list.
    data = [byte for line in data for byte in line]
    decompressed_len = len(data)
    
    # Define some useful constants.
    BIT_PASTCOPY = 0
    BIT_LITERAL = 1

    # Initialize variables to store the best compressed data and its size
    best_compressed_data = None
    best_compressed_size = float('inf')
    best_sourceArgSize = 0
    best_lengthArgSize = 0

    for sourceArgSize in range(10, 12):  
        for lengthArgSize in range(3, 6): 
            currentIndex = 0
            endIndex = len(data)
            output = bitstring.BitArray()
            output.append(bitstring.pack('uint:4', sourceArgSize))
            output.append(bitstring.pack('uint:4', lengthArgSize))

            # Start compressing the input data
            while currentIndex < endIndex:
                bestSource = 0
                bestLength = 0

                # Limit the search for matching patterns based on the current source argument size
                searchLimit = min(currentIndex, (1 << sourceArgSize) - 1)

                # Search for the best match in the data
                for i in range(1, searchLimit + 1):
                    #Limit the length of the match based on the current length argument size
                    lookaheadLimit = min((1 << lengthArgSize) - 1 + 3, endIndex - currentIndex)
                    currentLength = 0
                    for j in range(lookaheadLimit):
                        if data[currentIndex - i + j] == data[currentIndex + j]:
                            currentLength += 1
                        else:
                            break

                    # Update the best match if the current match is longer
                    if currentLength > bestLength:
                        bestSource = i
                        bestLength = currentLength

                # If a match of at least 3 bytes is found, encode it as a past copy reference
                if bestLength >= 3:
                    output.append(bitstring.pack('uint:1', BIT_PASTCOPY))
                    output.append(bitstring.pack('uint:n=v', n=sourceArgSize, v=bestSource))
                    output.append(bitstring.pack('uint:n=v', n=lengthArgSize, v=bestLength - 3))
                    currentIndex += bestLength
                else:
                    output.append(bitstring.pack('uint:1', BIT_LITERAL))
                    output.append(bitstring.pack('uint:8', data[currentIndex]))
                    currentIndex += 1

            # End the compressed data with an additional past copy instruction (terminating)
            output.append(bitstring.pack('uint:1', BIT_PASTCOPY))
            output.append(bitstring.pack('uint:n=v', n=sourceArgSize, v=0))
            output.append(bitstring.pack('uint:n=v', n=lengthArgSize, v=0))

            # Pad the output to make it byte-aligned if necessary
            if len(output) % 8 != 0:
                output.append('0b' + '0' * (8 - len(output) % 8))
            

            # If the current compressed data is smaller than the best found so far, update the best data
            if len(output.bytes) < best_compressed_size:
                best_compressed_data = output
                best_compressed_size = len(output.bytes)
                best_sourceArgSize = sourceArgSize
                best_lengthArgSize = lengthArgSize

    return bytearray(best_compressed_data.bytes), len(bytearray(best_compressed_data.bytes)), decompressed_len

def writeROM(romFile, startOffset, originalSize, data):
    """
    Writes data to the ROM at the specified offset.

    Parameters:
        romFile (str): The path to the ROM file.
        startOffset (int): The offset in the ROM file where data should be written.
        originalSize (int): The original size of the data to ensure there is enough space for the write operation.
        data (bytes or bytearray): The data to write to the ROM.
    
    Returns:
        int: The amount of free space left after writing the data.
    """
    # Check free space
    freeSpace = int(originalSize) - len(data)

    # Fill free space
    filledData = data + b'\x00' * freeSpace
        
    with open(romFile, "r+b") as f: 
        f.seek(startOffset)
        f.write(filledData)
    return freeSpace
        
            
if __name__ == "__main__":
    if len(sys.argv) < 7:
        sys.stdout.write("Usage: -d <romFile> <scriptStartOffset> <ScriptSize> <outFile> <tblFile>\n")
        sys.stdout.write("       -c <outFile> <romFile> <scriptOffset> <scriptSize> <pointerTable1> <pointerTable2> <pointerTableSize> <tblFile>\n")
        sys.stdout.write("       -v show version.\n")
        sys.exit(1)
    
    # Option
    option = sys.argv[1]
    
    # Decompress
    if option == '-d' and len(sys.argv) == 7:
        rom_file = sys.argv[2]
        script_addr = int(sys.argv[3],16)
        script_addr_size = int(sys.argv[4],16)
        out_file = sys.argv[5]
        tbl_file = sys.argv[6]

        # Decompress script from rom.
        decompress_script, compress_script_size, decompress_script_size = decompress(rom_file, script_addr)

        # Decode script with .tbl
        decode_script = format_text(decompress_script, 0x00)

        # Extract text to bin file
        ratio = 1 + ((decompress_script_size - compress_script_size) / compress_script_size)
        export_script = write_out_file(out_file, decode_script)
        print(f"Decompressed text: {decompress_script_size} bytes, ratio: {ratio}")
        print(f"Text extracted to {out_file}")
        print("Decoding complete.\n")
        
    # Compress
    elif option == '-c' and len(sys.argv) == 10:
        script_file = sys.argv[2]
        rom_file = sys.argv[3]
        script_addr = int(sys.argv[4],16)
        script_size = int(sys.argv[5],16)
        ptr_table_offset_1 = int(sys.argv[6],16)
        ptr_table_offset_2 = int(sys.argv[7],16)
        ptr_table_size = int(sys.argv[8],16)  
        tbl_file = sys.argv[9]
        base = 0x6900
        
        # Read decompressed script
        script = readScriptFile(script_file)

        # Encode Script with .tbl
        encode_script = encode_chars(script, tbl_file)

        # Create pointers table
        lsb, msb , pointers_size = calculate_ptr_table(encode_script, base)

        # Compress script
        compress_script, compress_script_size, decompressed_size = compress(encode_script)
    
        # Write data to ROM if pass len checks
        if compress_script_size > script_size:
            print(f"ERROR: script size has exceeded its maximum size. Remove {compress_script_size - script_size} bytes.")
            exit()
        if pointers_size > ptr_table_size:
            print(f"ERROR: table pointer size has exceeded its maximum size. Remove {pointers_size - ptr_table_size} lines.")
            exit()
        ratio = 1 - abs((compress_script_size - decompressed_size) / decompressed_size)
        script_freespace = writeROM(rom_file, script_addr, script_size, compress_script)
        print(f"Script text write to address {hex(script_addr)}, ratio: {ratio}, {script_freespace} bytes free.")
        ptr_table_freespace_lsb = writeROM(rom_file, ptr_table_offset_1, ptr_table_size, lsb)
        ptr_table_freespace_msb = writeROM(rom_file, ptr_table_offset_2, ptr_table_size, msb)
        print(f"Pointer table write to address {hex(ptr_table_offset_1)} and {hex(ptr_table_offset_2)}, {ptr_table_freespace_lsb} bytes free.")
        print("Encoding complete.\n")
        
    elif option == '-v' or option == '?':
        print("LZ77 Text Decompressor/Compressor by koda v0.1")
        sys.exit(1)
        
    else:
        sys.stdout.write("Usage: -d <romFile> <scriptStartOffset> <ScriptSize> <outFile> <tblFile>\n")
        sys.stdout.write("       -c <outFile> <romFile> <scriptOffset> <scriptSize> <pointerTable1> <pointerTable2> <pointerTableSize> <tblFile>\n")
        sys.stdout.write("       -v show version.\n")
        sys.exit(1)
 


