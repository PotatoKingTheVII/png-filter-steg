import zlib
from PIL import Image
import numpy
import binascii
import io
import math

#User inputs:
###################################
FileIn = "example.wav"       #Payload file
filename = "examplecover.png"     #Cover file



#Implementation of paeth (4 filter) algorithm from spec:
###################################
def paeth(left,top,topleft):
    finaldata = []
    for i in range(0,len(left)):
        a=left[i]
        b=top[i]
        c=topleft[i]
        array =[a,b,c]
         
        p=a+b-c
        pa=abs(p-a)
        pb=abs(p-b)
        pc=abs(p-c)

        arraydelta = [pa,pb,pc]
        
        finaldata.append((array[arraydelta.index(min(arraydelta))]))
    return(finaldata)



#Get payload
###################################
with open(FileIn, "rb") as fin:
    DataIn = fin.read()



#Preprocess image
###################################
with open(filename,"rb") as fin:
    img = Image.open(fin)
    pixels = img.load()
    pixelsPreFilter = img.load()

width, height = img.size
MaxLength = height
print("*Max payload size is " +str(MaxLength) + " bytes*")
if(len(DataIn)>MaxLength):
    print("Message too long, excess will be ignored")
print("\nPreprocessing image...")


for i in range(img.size[0]*img.size[1],-1,-1):   #Going from bottom right to top left
    x=i%img.size[0]
    y=(math.floor(i/img.size[0]))

    try:
        filterbyte = str(DataIn[y])
    except:
        filterbyte = 0

    if(filterbyte=="1"): #Sub
        if(x>0):
            pixels[x,y] = tuple(numpy.mod((numpy.subtract(pixelsPreFilter[x,y], pixelsPreFilter[x-1,y])),256))

    if(filterbyte=="2"): #Up
        if(y>0):
            pixels[x,y] = tuple(numpy.mod((numpy.subtract(pixelsPreFilter[x,y], pixelsPreFilter[x,y-1])),256))

    if(filterbyte=="3"): #Average
        if(y==0):
            if((x>0)):
                CorrectionTerm = (numpy.floor((numpy.divide((numpy.add(pixelsPreFilter[x-1,y],((0,) * len(img.getbands())))),2)))).astype("int")

            elif(x==0):
                CorrectionTerm = (numpy.floor((numpy.divide((numpy.add(((0,) * len(img.getbands())),((0,) * len(img.getbands())))),2)))).astype("int")

        else:
            if((x>0)):
                CorrectionTerm = (numpy.floor((numpy.divide((numpy.add(pixelsPreFilter[x-1,y],pixelsPreFilter[x,y-1])),2)))).astype("int")

            elif(x==0):
                CorrectionTerm = (numpy.floor((numpy.divide((numpy.add(((0,) * len(img.getbands())),pixelsPreFilter[x,y-1])),2)))).astype("int")
  
        pixels[x,y] = tuple(numpy.mod((numpy.subtract(pixelsPreFilter[x,y], CorrectionTerm)),256))
        
    if(filterbyte=="4"): #paeth
        if(y==0):
            if((x>0)):
                pixels[x,y] = tuple(numpy.mod((numpy.subtract(pixelsPreFilter[x,y],(  paeth((pixelsPreFilter[x-1,y]),(((0,) * len(img.getbands()))),(((0,) * len(img.getbands()))))    ))),256))
                
            elif(x==0):
                pixels[x,y] = tuple(numpy.mod((numpy.subtract(pixelsPreFilter[x,y],(  paeth((((0,) * len(img.getbands()))),(((0,) * len(img.getbands()))),(((0,) * len(img.getbands()))))    ))),256))

        else:
            if((x>0)):
                pixels[x,y] = tuple(numpy.mod((numpy.subtract(pixelsPreFilter[x,y],(  paeth((pixelsPreFilter[x-1,y]),(pixelsPreFilter[x,y-1]),(pixelsPreFilter[x-1,y-1]))    ))),256))
        
            elif(x==0):
                pixels[x,y] = tuple(numpy.mod((numpy.subtract(pixelsPreFilter[x,y],(  paeth((((0,) * len(img.getbands()))),(pixelsPreFilter[x,y-1]),(((0,) * len(img.getbands()))))    ))),256))  
        
            
ProcessedImageFile = io.BytesIO()
img.save(ProcessedImageFile,"png")



#Save processed image as 1 IDAT chunk and without any filters
###################################
ProcessedImageFile.seek(0)    #Why does this exist
fin = ProcessedImageFile
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
IHDR = IHDR + bytes.fromhex((IHDRCrc[2:len(IHDRCrc)]))

PixelArray = bytearray((numpy.array(img.getdata(),numpy.uint8).reshape(img.size[1], img.size[0], Bytes)).tobytes())
for i in range(0,height):
    PixelArray[((i*width*Bytes))+i:((i*width*Bytes))+i] = bytearray(b"\x00")

IDATCompressed = zlib.compress(PixelArray)
IDDATLength = len(IDATCompressed).to_bytes(4, 'big')
IDATCompressed = bytearray(b"\x49\x44\x41\x54")+IDATCompressed
IDATCrc =(hex(binascii.crc32(IDATCompressed)).rjust(8,"0"))

NoFiltersFile.write(PNGStart+IHDR+IDDATLength + IDATCompressed + bytes.fromhex(IDATCrc[2:len(IDATCrc)]) +bytearray(b"\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82"))
NoFiltersFile.seek(0)

im = Image.open(NoFiltersFile)
width, height = im.size



#Extract zlib chunk data
###################################
data=NoFiltersFile.getvalue()
NoFiltersFile.close()
print("\nWriting data...")

DatLocation = data.find(bytes("IDAT","utf-8"))
CompressedZlib = data[DatLocation+4:len(data)-8]
Decompressed = bytearray(zlib.decompress(CompressedZlib))



#Write input payload to filters
###################################
if(len(im.getbands())==3): #Is RGB image
    #print("RGB")
    for i in range(0,len(Decompressed), (width*3)+1):
        try:
            Decompressed[i] = int(DataIn[int(i/((width*3)+1))])
        except:
            pass
       
elif(len(im.getbands())==1): #Is palette image. I have no idea what will happen here if you try
    #print("Plaette")
    for i in range(0,len(Decompressed), (width*1)+1):
        try:
            Decompressed[i] = int(DataIn[int(i/((width*3)+1))])
        except:
            pass
else: #Is RGBA image
    #print("RGBA")
    for i in range(0,len(Decompressed), (width*4)+1):
        try:
            Decompressed[i] = int(DataIn[int(i/((width*4)+1))])
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
with open("Output.png", "wb") as fout:
    WriteData = FinalData + bytes.fromhex((IDatCRC[2:len(IDatCRC)]).rjust(8,"0")) + IENDChunk
    fout.write(WriteData)

ProcessedImageFile.close()
print("Finished")
