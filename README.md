image_checker
========================

Multi-thread python app for validating images. Check if image can be opened and contains valid information.

Usage
=======================

    $python image_checker.py [-h] [-d | -inf INVALID_FOLDER] [-npil] folder

* folder - absolute path to the folder with images that you want to check
* -h - help message with useful information about arguments
* -d - if it is given, then all invalid images will be deleted
* -inf - absolute path to folder where invalid images should be moved. Folder will be created if it's not exist.
* -npil - don't use Pillow library. Warning: check quality may decline!

Examples
=======================

Find invalid images and print their paths:

    $ python image_checker.py /home/my_user_name/images

Delete all invalid images and don't use Pillow library:

    $ python image_checker.py /home/my_user_name/images -d -npil
    
Move all invalid images to folder "invalid_images":

    $ python image_checker.py /home/my_user_name/images -inf /home/my_user_name/images/invalid_images
    
Show help:

    $ python image_checker.py -h
    
Requirements
=======================

Pillow (PIL) library

    $pip install Pillow