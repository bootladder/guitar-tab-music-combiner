# Guitar Tab Overlayer

![alt text](https://user-images.githubusercontent.com/28636252/59810835-133d8900-92d5-11e9-913b-a6e3963d9699.png)
![alt text](https://user-images.githubusercontent.com/28636252/59811185-bb078680-92d6-11e9-9557-5b6f75508596.png)

# What does it do

* You select an image and a region containing music and tabs
* It scans the tabs and the music, and pastes the numbers over the note heads.
* It writes over the original image and you keep going
* When finished, you download the image with all the changes.

# Usage
`docker-compose up` should do the trick

## TODO ##

* Monophonic only, ie. no chords.  1 note at a time.
* Half Notes and Whole Notes don't work
* Double Digit numbers in tabs don't work
* Only works on fully cropped images ie. with no noise above and below the staff.
* Only works with completely horizontal staff lines
* Single digit tabs only.  ie. Frets 10 and above will not be recognized

# Convert pdf to image
**so you can rip pages out of pdfs to feed into this**

* pdftoppm page37.pdf outputname -png
* sudo apt install pdftk
* pdftk input.pdf cat 37 output page37.pdf

