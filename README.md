# Make Jumbo Poster from Small Photos Assembled Together

Printing a poster-sized photo is expensive. Printing standard photos (4x6) is cheap.

This Python 3 script takes any photo and breaks it out into small pieces that can be printed as standard 4x6 prints. Those 4x6 prints can then be glued or taped together to create a large poster.

The script handles image scaling and checks for minimum DPI needed for printing. The output images each include a small address tag in the top corner, like "(1,1)", to make it easy to later know where each 4x6 photo needs to fit back into the poster.

NOTE: many print services automatically apply colour corrections to the prints. Given that each photo here is really just a small piece of a larger photo, colour correcting can give some "funny" results and make the final assembled poster look bad. It is best make any photo corrections on the original photos (before splitting it here), and then disable colour corrections from the print service.

## Start with some photo
![Original Image](images/original_photo.jpg)


## 2. The script splits it up into a series of standard photo-size images
![Standard-Sized Photos](images/individual_standard_photos.jpg)


## 3. Tape the collection of photos onto some backing board and enjoy your large poster!
