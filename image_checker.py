__author__ = 'Antony Cherepanov'

import time
import argparse
import os
import shutil
import multiprocessing
import imghdr
from PIL import Image, ImageStat


def get_local_time_string():
    """ Get string with current date and local time
    @output: string with date and time
    """

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def parse_arguments():
    """ Parse arguments and start check process
    :return list of arguments
    """

    parser = argparse.ArgumentParser(description="Multi-thread python app for validating images")
    parser.add_argument("folder", help="absolute path to the folder with images to check")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--delete", action="store_true", help="delete invalid images")
    group.add_argument("-inf", "--invalid_folder", help="absolute path to the folder for invalid images")

    args = parser.parse_args()
    return [args.folder, args.delete, args.invalid_folder]


def check_arguments(t_folder, t_delete, t_inv_folder):
    """ Check arguments
    :param t_folder: string with absolute path to the folder with images to check
    :param t_delete: boolean value. If True, delete all invalid images
    :param t_inv_folder: string with absolute path to the folder for invalid images
    :return boolean value. True if arguments are OK.
    """

    if check_existing_folder(t_folder) is False:
        print("Error: Invalid path to folder " + t_folder)
        return False

    if t_delete is True and t_inv_folder is not None:
        print("Error: Conflicting options. We can't delete invalid image and move it to some folder")
        return False

    if t_delete is False and t_inv_folder is not None:
        if check_folder_path(t_inv_folder) is True:
            if not os.path.exists(t_inv_folder):
                os.makedirs(t_inv_folder)
        else:
            print("Error: Invalid path to folder for invalid images " + t_inv_folder)
            return False

    return True


def check_existing_folder(t_path):
    """ Check if folder really exist
    :param t_path: string with absolute path to presumably existing folder
    :return: boolean value. True if folder exist, False if it's not
    """

    if not os.path.isabs(t_path) or\
            not os.path.exists(t_path) or\
            not os.path.isdir(t_path):
        return False
    return True


def check_folder_path(t_path):
    """ Check if path to folder is valid
    :param t_path: string with absolute path to some folder
    :return: boolean value. True if path could be path for folder.
    """

    if os.path.isabs(t_path) is True:
        return True
    return False


def start_check(t_folder, t_delete, t_inv_folder):
    """ Check images
    :param t_folder: string with absolute path to the folder with images to check
    :param t_delete: boolean value. If True, delete all invalid images
    :param t_inv_folder: string with absolute path to the folder for invalid images
    """

    images = get_images_paths(t_folder)
    cores_num = multiprocessing.cpu_count()
    img_chunks = list_split(images, cores_num)

    function = print_invalid_img_path
    extra_args = None
    if t_delete is True:
        function = delete_invalid_image
    else:
        if t_inv_folder is not None:
            function = move_invalid_image
            extra_args = t_inv_folder

    jobs = list()
    for i in range(cores_num):
        thread = multiprocessing.Process(target=check_images, args=(next(img_chunks), function, extra_args))
        jobs.append(thread)
        thread.start()

    for thread in jobs:
        thread.join()


def list_split(t_list, t_size):
    """ Generator that split list of elements in n chunks
    :param t_list - list of elements
    :param t_size - size of chunk
    :return generator of lists of chunks
    """

    new_length = int(len(t_list) / t_size)
    for i in range(0, t_size - 1):
        yield t_list[i * new_length:i * new_length + new_length]
    yield t_list[t_size * new_length - new_length:]


def get_images_paths(t_folder):
    """ Check if folder contains images (on the first level) and return their paths
    :param t_folder: string with the absolute path to the folder
    :return: list with the absolute paths of the images in folder
    """

    if not os.path.isdir(t_folder):
        return list()

    image_extensions = ["jpg", "jpeg", "bmp", "png", "gif", "tiff"]
    images = list()
    entries = os.listdir(t_folder)
    for entry in entries:
        file_path = os.path.join(t_folder, entry)
        file_parts = str.split(file_path, '.')
        extension = file_parts[-1:][0]
        extension = extension.lower()
        if os.path.isfile(file_path) and extension in image_extensions:
            images.append(file_path)

    return images


def check_images(t_paths, t_func, t_extra_args):
    """ Check images if they are valid
    :param t_paths: list of path to the images
    :param t_func: function to call if image is not valid
    :param t_extra_args: arguments for t_func
    """

    for img_path in t_paths:
        try:
            image = Image.open(img_path)
            image.verify()
            image.close()

            if not imghdr.what(img_path):
                raise Exception

        except Exception as err:
            print(err)
            if t_extra_args is None:
                t_func(img_path)
            else:
                args = img_path, t_extra_args
                t_func(*args)


def print_invalid_img_path(t_path):
    """ Print path of invalid image
    :param t_path: string with path to the invalid image
    :return: boolean value True
    """

    print("Invalid image: " + t_path)
    return True


def delete_invalid_image(t_path):
    """ Delete invalid image
    :param t_path: string with path to the invalid image
    :return: boolean value. True if image was successfully deleted
    """

    if not os.path.isfile(t_path):
        print("Error: this is not a path to the file - " + t_path)
        return False

    try:
        os.remove(t_path)
    except Exception as err:
        print("Error: failed to remove file: {0}".format(err))
        return False

    print("Deleted: " + t_path)
    return True


def move_invalid_image(t_img_path, t_folder):
    """ Move image to the folder
    :param t_img_path: string with path to the invalid image
    :param t_folder: string with folder where invalid image should be moved
    :return: boolean value. True if image was successfully moved
    """

    if not os.path.isfile(t_img_path) or not os.path.isdir(t_folder):
        print("Error: invalid arguments - " + t_img_path + "; " + t_folder)
        return False

    try:
        shutil.copy(t_img_path, t_folder)
        os.remove(t_img_path)
    except Exception as err:
        print("Error: failed to move file: {0}".format(err))
        return False

    print("Moved: " + t_img_path)
    return True


if __name__ == '__main__':
    print(get_local_time_string() + " Start")
    arguments = parse_arguments()
    isOk = check_arguments(arguments[0], arguments[1], arguments[2])
    if isOk is True:
        start_check(arguments[0], arguments[1], arguments[2])
        print(get_local_time_string() + " Done")
    else:
        print(get_local_time_string() + " Invalid arguments. Try again!")