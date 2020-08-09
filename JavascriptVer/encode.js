//Note that because of alpha premultiplication the RGB values of a 0 alpha pixel are lost
//But before we start a word from our sponsor, stackoverflow /s
function textToBin(text) //https://stackoverflow.com/a/23863941
{
  var length = text.length,
      output = [];
  for (var i = 0;i < length; i++) {
    var bin = text[i].charCodeAt().toString(2);
    output.push(Array(8-bin.length+1).join("0") + bin);
  } 
  return output.join("");
}

function toBytesInt32(num) //https://stackoverflow.com/a/24947000
{
arr = new ArrayBuffer(4); // an Int32 takes 4 bytes
view = new DataView(arr);
view.setUint32(0, num, false); // byteOffset = 0; litteEndian = false
return arr;
}

//Crc32 implementation START https://stackoverflow.com/a/18639999
var makeCRCTable = function()
{
var c;
var crcTable = [];
for(var n =0; n < 256; n++){
	c = n;
	for(var k =0; k < 8; k++){
		c = ((c&1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1));
	}
	crcTable[n] = c;
}
return crcTable;
}

var crc32 = function(str) 
{
	var crcTable = window.crcTable || (window.crcTable = makeCRCTable());
	var crc = 0 ^ (-1);

	for (var i = 0; i < str.length; i++ ) {
		crc = (crc >>> 8) ^ crcTable[(crc ^ str.charCodeAt(i)) & 0xFF];
	}

	return (crc ^ (-1)) >>> 0;
};
//Crc32 END

function encode() 
{
	//Create virtual canvas and draw uploaded image to it
	myImage = new Image()
	myImage.src = EncUploadedURL
	height = myImage.height
	width = myImage.width
	myImage.onload = function(ev)
	{
		//First get the image data and dimensions
		var c = document.createElement("canvas");
		c.width = width
		c.height = height
		var ctx = c.getContext("2d");
		ctx.drawImage(myImage, 0, 0, width, height);
		
		//Also get the payload as a binary string
		pixelData = new Uint8ClampedArray(ctx.getImageData(0, 0, width, height).data)
		var payload = document.getElementById("encInputTxt").value
		var binaryPayload = textToBin(payload)

		//Do the inverse of the first filter sub type to prepare for the payload
		//If that row's payload is a 1, otherwise leave it alone
		for (var i = ((height*width*4)-1); i >= 0; i-=4) 
		{
			var curX = i%(width*4)
			var curY = Math.floor(i/(width*4))

			if((binaryPayload[curY] == 1) && (curX > 4))
			{
				for (var j = 0; j < 4; j+=1) //Do for each R G B A component starting with A
				{
					curComponent = pixelData[i-j]
					pairComponent = pixelData[(i-j)-4]	//Pixel component to the left
					if(curComponent < pairComponent)
					{
						pixelData[i-j] = 256 + (curComponent - pairComponent)%256
					}
					else
					{
						pixelData[i-j] = (curComponent - pairComponent)%256
					}

				}
			}
			
		}

		//At this point the ImageData only has the inverse filters applied, not any payload filter bytes in it
		//Adding those bytes at the start of each row:
		PixelDataArray = Array.from(pixelData)
		for (var i = 0; i < height; i+=1) 
		{
			rowStartIndex = i*4*width
			if(i <= binaryPayload.length)
			{
				PixelDataArray.splice(rowStartIndex+i, 0, binaryPayload[i])
			}
			else
			{
				PixelDataArray.splice(rowStartIndex+i, 0, 0)
			}
		}

		//Construct the PNG chunks piece by piece
		var widthArray = toBytesInt32(width)
		var heightArray = toBytesInt32(height)
		var IHDR = [0,0,0,13,73,72,68,82].concat(Array.from(new Uint8Array(widthArray)), Array.from(new Uint8Array(heightArray)), [8,6,0,0,0])
		var IHDRCrc = toBytesInt32(crc32(String.fromCharCode.apply(null, IHDR.slice(4))))
		pixelBytes = new Uint8Array(PixelDataArray)
		
		var IDATCompressed = [73,68,65,84].concat(Array.from(pako.deflate(pixelBytes)))
		var IDATLength = toBytesInt32((IDATCompressed.length)-4)
		decoder = new TextDecoder('utf8')
		var IDATCrc = toBytesInt32(crc32(decoder.decode(new Uint8Array(IDATCompressed))))

		//Making the final PNG piecemeal from each section
		FinalDataRaw = [137,80,78,71,13,10,26,10].concat(IHDR,Array.from(new Uint8Array(IHDRCrc)), Array.from(new Uint8Array(IDATLength)), IDATCompressed, Array.from(new Uint8Array(IDATCrc)), [0,0,0,0,73,69,78,68,174,66,96,130])
		FinalData = new Uint8Array(FinalDataRaw)
		var blob=new Blob([FinalData]);// change resultByte to bytes
		var link=document.createElement('a');
		link.href=window.URL.createObjectURL(blob);
		link.download="EncodedOutput.png";
		link.click();
	}
}