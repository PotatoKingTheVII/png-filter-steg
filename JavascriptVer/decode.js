function bin2String(array) //https://stackoverflow.com/a/3195961
{
  var result = "";
  for (var i = 0; i < array.length; i++) {
    result += String.fromCharCode(parseInt(array[i], 2));
  }
  return result;
}

function decode(binaryArray) 
{
	var width = (new Uint32Array(binaryArray.slice(16,20).reverse().buffer))[0]	//Reverse for big-endian 4 byte
	var height = (new Uint32Array(binaryArray.slice(20,24).reverse().buffer))[0]
	var colourMode = binaryArray[25] //2 RGB, 3 palette, 6 RGBA


	//Preparation for zlib decompression by collecting all IDAT chunks
	var arr_as_bin = [...new Uint8Array(binaryArray)].map(v => String.fromCharCode(v)).join('');	//Convert to str for easier search of IDAT 
	var arr_as_bin = arr_as_bin.slice(arr_as_bin.indexOf("IDAT")-8, (arr_as_bin.length)-12)	//Get IDAT chunks only
	while(arr_as_bin.indexOf("IDAT") != -1)
	{
		var location = arr_as_bin.indexOf("IDAT")
		IDATSection = arr_as_bin.slice(location-8,location+4)	//Remove prev crc, current length and IDAT
		var arr_as_bin = arr_as_bin.replace(IDATSection,"")
	}
	
	//Inflate all the collected IDAT chunks and recover the pixel elements from it in format RGBA (0), RGBA (1) array
	var pixels = pako.inflate(arr_as_bin)

	//Check how many elements per pixel from the colour mode
	if(colourMode == 2)	//RGB
	{
		var pixelElem = 3
	}
	else if(colourMode == 6)	//RGBA
	{
		var pixelElem = 4
	}
	else if(colourMode == 3)
	{
		var pixelElem = 1	//Palette
	}
	else	//Unsupported
	{
		console.log("Unsupported png")
	}
	
	//Actually read the filter bytes
	var i;
	var temp="";
	for (i = 0; i < pixels.length; i+=((width*pixelElem)+1)) 
	{

		temp += " " + pixels[i]
	}

	//Clean up and show the filter bytes
	document.getElementById('decOutputTxt').value = temp.slice(1,temp.length)	//Get rid of the leading space
	var inputraw = temp.replace(/ /g, "")
	inputArray = []
	for (var i = 0; i < (inputraw.length/8); i++)
	{
		var byteVal = [inputraw.slice(i*8,(i*8)+8)]
		if(byteVal == "00000000")
		{
			break
		}
		else
		{
			inputArray.push(byteVal)
		}
		
	}
	document.getElementById('decOutputTxtUTF').value = bin2String(inputArray)

}
