import random
import zlib
from PIL import Image
import numpy
import binascii
import io

#User inputs:
###################################
filename = "example.png"
LowFilter = 1
HighFilter = 4
#Filters 1-4 are defined and have effects, 0 is no effect

#Convert text to binary
###################################
im = Image.open(filename)
width, height = im.size
TextList = ""
for i in range(0,height):
    Temp = str(random.randint(LowFilter,HighFilter))
    TextList += Temp

fin = open(filename, 'rb')



#Save processed image as 1 IDAT chunk and without any filters
###################################
NoFiltersFile = io.BytesIO()
img = Image.open(fin)
width, height = img.size
PNGStart = bytearray(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A")

if(len(img.getbands())==3): #Is RGB only image
    ColourType = 2
    Bytes = 3
elif(len(img.getbands())==4): #Is RGBA image
    ColourType = 6
    Bytes = 4

IHDR = bytearray(b"\x00\x00\x00\x0D\x49\x48\x44\x52") + width.to_bytes(4, 'big') + height.to_bytes(4, 'big') + bytearray(b"\x08") + bytearray(bytes([ColourType])) + bytearray(b"\x00\x00\x00")
IHDRCrc = (hex(binascii.crc32(IHDR[4:len(IHDR)])).rjust(8,"0"))
IHDR = IHDR + bytes.fromhex((IHDRCrc[2:len(IHDRCrc)].rjust(8,"0")))

PixelArray = bytearray((numpy.array(img.getdata(),numpy.uint8).reshape(img.size[1], img.size[0], Bytes)).tobytes())
for i in range(0,height):
    PixelArray[((i*width*Bytes))+i:((i*width*Bytes))+i] = bytearray(b"\x00")

IDATCompressed = zlib.compress(PixelArray)
IDDATLength = len(IDATCompressed).to_bytes(4, 'big')
IDATCompressed = bytearray(b"\x49\x44\x41\x54")+IDATCompressed
IDATCrc =(hex(binascii.crc32(IDATCompressed)).rjust(8,"0"))

NoFiltersFile.write(PNGStart+IHDR+IDDATLength + IDATCompressed + bytes.fromhex(IDATCrc[2:len(IDATCrc)]) +bytearray(b"\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82"))
NoFiltersFile.seek(0)



#Get zlib
###################################
data=NoFiltersFile.getvalue()
DatLocation = data.find(bytes("IDAT","utf-8"))
CompressedZlibRaw = bytearray(data[DatLocation+4:len(data)])

while(CompressedZlibRaw.find(bytes("IDAT","utf-8")) != -1):
    DatLocationPlural = CompressedZlibRaw.find(bytes("IDAT","utf-8"))
    CurrentCRCChunk = CompressedZlibRaw[DatLocationPlural-4:DatLocationPlural]
    del CompressedZlibRaw[DatLocationPlural-8:DatLocationPlural+4]

CompressedZlib  = CompressedZlibRaw[0:len(CompressedZlibRaw)-4]
Decompressed = bytearray(zlib.decompress(CompressedZlib))



#Edit filter bytes
###################################
if(len(im.getbands())==3): #Then it's an RGB only image
    #print("RGB")
    for i in range(0,len(Decompressed), (width*3)+1):
        try:
            Decompressed[i] = int(TextList[int(i/((width*3)+1))])
        except:

            pass
       
elif(len(im.getbands())==1): #Is Palette image
    #print("Plaette")
    for i in range(0,len(Decompressed), (width*1)+1):
        try:
            Decompressed[i] = int(TextList[int(i/((width*1)+1))])
        except:

            pass
else: #Is RGBA image
    #print("RGBA")
    for i in range(0,len(Decompressed), (width*4)+1):
        try:
            Decompressed[i] = int(TextList[int(i/((width*4)+1))])
        except:

            pass



#Calculate new length and CRC of edited chunks and combine them
###################################
IENDChunk = bytearray(b"\00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82")
EditCompressed = zlib.compress(Decompressed)
FinalData = bytearray(data[0:DatLocation+4] + EditCompressed)
IDatChunkActualLength = hex(len(EditCompressed))
IDatChunkActualLengthSizeFix = IDatChunkActualLength[2:len(IDatChunkActualLength)].rjust(8,"0") #Make sure it's always a 4-byte value

FinalData[(DatLocation - 4):DatLocation] = bytes.fromhex(IDatChunkActualLengthSizeFix)
DatLocation = FinalData.find(bytes("IDAT","utf-8"))
IDatCRC  = hex(binascii.crc32(FinalData[DatLocation:len(FinalData)]))



#Save final png to file
###################################
with open("ObscureOutput.png", "wb") as fout:
    WriteData = FinalData + bytes.fromhex((IDatCRC[2:len(IDatCRC)]).rjust(8,"0")) + IENDChunk
    fout.write(WriteData)

print("Finished")
