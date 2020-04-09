import os
import math

from PIL import Image
from PIL import ImageStat
from PIL import ImageDraw
from PIL import ImageFont


def resize(size, hwRatio):
    """
    Return the minimum size of image that is at least "size" but
    maintains the provided aspect ratio
    """
    if size[0] * hwRatio > size[1]:
        return (size[0], int(math.ceil(size[0]*hwRatio)))
    else:
        return (int(math.ceil(1.0*size[1] / hwRatio)), size[1])


def crop_image(size, hwRatioCropped):
    """
    Return the size of image that crops image to hwRatioCropped
    while minimizing cropping required.
    Crops evenly from both sides (keeps middle of image).
    """
    if size[0] * hwRatioCropped > size[1]:
        trim = size[0] - size[1]/hwRatioCropped
        #print size[0], size[1], trim
        #print int(math.ceil(trim/2)), 0, int(math.ceil(size[0] - 1.0*trim/2)), size[1]
        return (int(math.ceil(trim/2)), 0, int(math.ceil(size[0] - 1.0*trim/2)), size[1])
    else:
        trim = size[1] - size[0]*hwRatioCropped
        #print size[0], size[1], trim
        #print 0, int(math.ceil(trim/2)), int(math.ceil(size[1] - 1.0*trim/2)), size[0]
        return (0, int(math.ceil(trim/2)), size[0], int(math.ceil(size[1] - 1.0*trim/2)))


def brightness( im_file ):
    # http://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
    # mode L = 8-bit pixels, black and white
    # 8 bit range = 2^8 = 255 (black = 0; white = 255)
    im = im_file.convert('L')
    stat = ImageStat.Stat(im)
    return stat.mean[0]


def print_photo_number(curr_img, print_txt):
    """
    prints the photo location / position
    references:
    1) http://python-catalin.blogspot.ca/2010/06/add-text-on-image-with-pil-module.html
    2) http://stackoverflow.com/questions/8110342/python-any-tutorial-to-overlay-text-on-a-picture
    3) http://openfontlibrary.org
    """
    font_fname = r'fonts/Hanken-Light.ttf'
    font_size = 10
    font = ImageFont.truetype(font_fname, font_size)

    w,h = curr_img.size
    corner_pct = 0.1 # look at 10% of pixels in top-left
    top_left = curr_img.crop( (0, 0, int(corner_pct*w), int(corner_pct*h)) )

    draw = ImageDraw.Draw(curr_img)

    if brightness( top_left ) > 125:
        # corner is light
        text_color = (0,0,0) # black text
    else:
        # corner is dark
        text_color = (255,255,255) # white text

    draw.text((0, 0),print_txt,text_color,font=font) #black

    return curr_img


def stitch_image_processor(input_dir, fname, w_h_inch, save_dir, prefix='stitch'):
    src = Image.open( os.path.join(input_dir, fname) )
    w_pic, h_pic = src.size

    desired_image_w_inch, desired_image_h_inch = w_h_inch

    MM_PER_INCH = 25.4
    desired_image_w_mm = desired_image_w_inch * MM_PER_INCH
    desired_image_h_mm = desired_image_h_inch * MM_PER_INCH

    #paper dims not exactly 4x6 (102mm x 152mm)
    h_paper_mm = 102
    w_paper_mm = 152
    hw_paper_ratio = h_paper_mm / w_paper_mm

    # find number of whole frames that will fit (use round first, b/c "int" rounds down)
#     stitch_count_w = int(desired_image_w_mm / w_paper_mm)
#     stitch_count_h = int(desired_image_h_mm / h_paper_mm)
    stitch_count_w = int(round(desired_image_w_mm / w_paper_mm,0))
    stitch_count_h = int(round(desired_image_h_mm / h_paper_mm,0))
    stitch_count_tot = stitch_count_w * stitch_count_h
    #print stitch_count_w, stitch_count_h

    # calculate actual final dimensions (based on even # frames)
    final_image_w_mm = stitch_count_w * w_paper_mm
    final_image_h_mm = stitch_count_h * h_paper_mm
    final_image_w_inch = final_image_w_mm / MM_PER_INCH
    final_image_h_inch = final_image_h_mm / MM_PER_INCH

    # (original image, stitched sub-images)
    hw_ratio = final_image_h_mm / final_image_w_mm
    #print hw_ratio

    # crop the starting image to correct aspect ratio
    src = src.crop(crop_image((w_pic, h_pic), hw_ratio))
    w_pic, h_pic = src.size
    #print crop_image((w_pic, h_pic), hw_ratio)
    #print src.size

    w_stitch_px = int(w_pic / stitch_count_w)
    h_stitch_px = int(h_pic / stitch_count_h)
    hw_stitch_ratio = h_stitch_px / w_stitch_px
    #print w_stitch_px, h_stitch_px

    # calculate stitch images
    for h in range(stitch_count_h):
        for w in range(stitch_count_w):
            # pull sub-image, and save it
            dest = src.crop( (w*w_stitch_px,h*h_stitch_px,(w+1)*w_stitch_px,(h+1)*h_stitch_px) )
            prefix_stitch = prefix + '_%i_%i_' % (h+1,w+1)
            print_label = '(%i,%i)' % (h+1,w+1)
            dest = print_photo_number(dest,print_label)
            dest.save( os.path.join(save_dir, prefix_stitch+fname), 'JPEG', quality=100)

    print('stitches produced for %s: %i (%ix%i)' % (fname, stitch_count_tot, stitch_count_w, stitch_count_h))
    print('final image size (inch): %.1fx%.1f' % (final_image_h_inch, final_image_w_inch))

    #print 'percent diff AR: %.2f' % abs(hw_stitch_ratio/hw_paper_ratio-1)
    if abs(hw_stitch_ratio/hw_paper_ratio-1) > 0.01:
        # percent diff > X%
        print('ERROR: bad frame ratio | desired = %.4f | actual = %.4f' % (hw_paper_ratio, hw_stitch_ratio))

    min_res = min(w_pic/final_image_w_inch, h_pic/final_image_h_inch)
    print('min resolution: %i dpi' % (min_res))


if __name__ == "__main__":

    input_dir = ''
    w_h_inch = (36,36)                      # dimensions of the finished poster (when small photos are stitched back)
    fname = 'test_image_to_split.jpg'       # the input file
    save_dir = 'image_stitch_output'        # the output directory

    stitch_image_processor(input_dir,fname,w_h_inch,save_dir,'stitch')

    print('done')

