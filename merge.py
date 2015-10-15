#
# run this code  only after all the chunks of image are downloaded.
# Make sure all the chunks of images are in the same folder as this.
# Also, all image folder extension is jpg


import glob

read_files = glob.glob("*.*.jpg") 

with open("result.jpg", "wb") as outfile:
    for f in read_files:
        with open(f, "rb") as infile:
            outfile.write(infile.read())