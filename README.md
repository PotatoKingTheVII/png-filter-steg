## File usage
| File | Usage |
|--|--|
| 1) FilterEncoder | Hide text in the filter bytes of the input image as binary |
| 2) FilterDecoder | Extract filter bytes from an image |
| 3) ObscureEncoder | Randomize filters to obscure the image |
| 4) ObscureDecoder | Zeroes all filters and returns the normal image  |

User inputs can be found at the top of each file, FilterDecoder prints the raw filter byte value to be more generalised, to extract any text from the Encoder decode the result in binary.

*Compatiable with RGB and RGBA PNGs*

## Brief technical overview
PNGs utilise filters before compressing the raw pixel data with zlib to try and reduce the file size. If we manually change these filters beforehand to hide our payload then the pixels can be edited such that when the filters are applied by an image decoder it gives back the original picture seemingly unchanged. The basic flow for encoding is:

 1. Save image with no filters and normal visual pixel data. This is done by gathering all IDAT chunks to one zlib stream, decompressing it and looping through all filter bytes then saving the new data to a replacement IDAT chunk and changing any CRCs and chunk length values
 2. Edit scanlines which are changed by the text to be encoded such that when the filter is applied the normal image will result
 3. Edit filters to hide input text data and save

Decoding can be done by loading the zlib data, looping through all filter bytes and displaying them.

A much higher data density can be achieved by using more filter states (Would require extra pre-processing for each state) or the whole FF range of the filter bytes. However, by limiting to just the defined 0-4 states it's more spec compliant

Obscuring can be done in a similar way but ignoring step 2 and in 3 random filter bytes are applied with no pre-processing so when filters are applied the image will be a mess, some interesting effects can be seen by changing the random bytes used.


## Dependancies

 - numpy
 - pillow
