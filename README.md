## Versions
This Python version came first and has a few more features while the javascript version was just a port of the normal enc/dec versions for a first web project and can be found https://pngfiltersteg.neocities.org/ or used locally, it's entirely clientside


## File usage
| File | Usage |
|--|--|
| 1) FilterEncoder | Hide text in the filter bytes of the input image as binary |
| 2) FilterDecoder | Extract filter bytes from an image |
| 3) FilterHDEncoder | Uses full byte range to hide files in image  |
| 4) FilterHDDecoder | Extract high density files from above  |
| 5) ObscureEncoder | Randomize filters to obscure the image |
|6) ObscureDecoder | Zeroes all filters and returns the normal image  |


User inputs can be found at the top of each file, FilterDecoder writes the raw filter byte value to be more generalised and view the filter bytes normally (Decode result as binary for text) while FilterHDDecoder outputs the actual binary data to a file.

*Compatiable with RGB and RGBA PNGs*

## Brief technical overview
PNGs utilise filters before compressing the raw pixel data with zlib to try and reduce the file size. If we manually change these filters beforehand to hide our payload then the pixels can be edited such that when the filters are applied by an image decoder it gives back the original picture seemingly unchanged. The basic flow for encoding is:

 1. Preprocess the image by getting the visible pixel data from the image and editing it such that each scanline pixel's are altered so when the payload filters are applied the normal image will result, usually doing the inverse of the filter algorithm
 2. Zero all the filter bytes from this preprocessed pixel array then add in the payload data where necessary on each scanline row
 3. Create a new PNG with this pixel data array from scratch chunk by chunk to ensure our edited filter payload is kept

Decoding can be done by gathering all the IDAT chunks for the zlib stream, loading that data, gathering all filter bytes and writing them.

The normal version only uses the 0 and 1 filters to be more spec compliant thus limiting the payload size to 1/8 of the cover's height. The HD versions use all 0-255 filters and apply the above step 2 to each 1-4 defined filters allowing the payload's size to directly be the cover's height

Obscuring can be done in a similar way but ignoring step 2 and in 3 random filter bytes are applied with no pre-processing so when filters are applied the image will be a mess, some interesting effects can be seen by changing the random bytes used. Since the image was re-written with known all 0 filter bytes in step 1 the new random bytes can be zeroed to get back the un-obscured image.


## Dependancies

 - numpy
 - pillow
