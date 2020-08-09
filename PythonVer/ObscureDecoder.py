import zlib
from PIL import Image
import numpy
import binascii

#User inputs:
###################################
filename = "ObscureOutput.png"



#Get zlib
###################################
im = Image.open(filename)
width, height = im.size

with open(filename, 'rb') as fin:
    data=fin.read() 
    
DatLocation = data.find(bytes("IDAT","utf-8"))
CompressedZlibRaw = bytearray(data[DatLocation+4:len(data)])

while(CompressedZlibRaw.find(bytes("IDAT","utf-8")) != -1):
    DatLocationPlural = CompressedZlibRaw.find(bytes("IDAT","utf-8"))
    CurrentCRCChunk = CompressedZlibRaw[DatLocationPlural-4:DatLocationPlural]
    del CompressedZlibRaw[DatLocationPlural-8:DatLocationPlural+4]

CompressedZlib  = CompressedZlibRaw[0:len(CompressedZlibRaw)-4]
Decompressed = bytearray(zlib.decompress(CompressedZlib))



#Extract filter bytes
###################################
CodeString = ""

if(len(im.getbands()) == 3): #Then it's an RGB only image
    #print("RGB")
    for i in range(0,len(Decompressed), ((width*3)+1)):
        try:
            Decompressed[i] = 0
        except:
            pass
        
elif(len(im.getbands())==1): #Is Palette image
    #print("Plaette")
    for i in range(0,len(Decompressed), (width*1)+1):
        try:
            Decompressed[i] = 0
        except:
            pass
else: #Is RGBA image
    #print("RGBA")
    for i in range(0,len(Decompressed), (width*4)+1):
        try:
            Decompressed[i] = 0
        except:
            pass

EditCompressed = zlib.compress(Decompressed,9)

IENDChunk = bytearray(b"\00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82")
IDatChunkActualLength = hex(len(EditCompressed))
IDatChunkActualLengthSizeFix = IDatChunkActualLength[2:len(IDatChunkActualLength)].rjust(8,"0") #Make sure it's always a 4-byte value
FinalData = data[0:DatLocation-4] + bytes.fromhex(IDatChunkActualLengthSizeFix) + bytearray(b"\x49\x44\x41\x54") + EditCompressed
IDatCRC  = hex(binascii.crc32(FinalData[DatLocation:len(FinalData)]))
with open("OutputUnhidden.png", "wb") as fout:
    fout.write(FinalData + bytes.fromhex((IDatCRC[2:len(IDatCRC)]).rjust(8,"0")) + IENDChunk)

print("Finished")
