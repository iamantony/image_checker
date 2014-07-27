image_checker
========================

Multi-thread python app for validating images.

Usage
=======================

    $ image_checker PATH_TO_FOLDER FOLDER_FOR_INVALID_IMAGES

* PATH_TO_FOLDER - absolute path to the folder with images that you want to check
* FOLDER_FOR_INVALID_IMAGES - absolute path to folder where invalid images should be moved.
Folder will be created if it's not exist.

Examples
=======================

    $ python image_checker.py /home/my_user_name/images /home/my_user_name/images/invalid_images
    
Requirements
=======================

Pillow (PIL) library

    $pip install Pillow