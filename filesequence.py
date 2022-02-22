"""filesequence.py - in OS X, if you copy a file to a directory and a file
already exists by that name, then it appends -1, -2 and so on to the name. This
set of functions mimics that functionality in Python.
"""
import filecmp
import os
import shutil

def increment_filename(filename):
    """Given a filename, return the filename with a counter appended. It
    appends -1 if a counter is not already there, or increments an existing
    counter as appropriate.
    """
    basename, fileext = os.path.splitext(filename)

    # If there isn't a counter already, then append one and return
    if '-' not in basename:
        components = [basename, '-1', fileext]

    # If it looks like there might be a counter, then try to increment it and
    # return. If the string after the dash can't be coerced into an int, then
    # assume no counter already exists.
    else:
        base, counter = basename.rsplit('-', 1)
        try:
            new_count = int(counter) + 1
            components = [base, '-', str(new_count), fileext]
        except ValueError:
            components = [basename, '-1', fileext]

    next_filename = ''.join(components)
    return next_filename

def dest_filename(filepath, target_dir):
    """Given a filename and a target directory, return either:

    * the next name in sequence (myfile.jpg, myfile-1.jpg, myfile-2.jpg, ...)
      that is not being used, or
    * the name in the sequence that is both in use and also identical to the
      file in question
    """
    filename = os.path.basename(filepath)

    # If the file doesn't already exist, then we can just return the original
    # filename. This will always be trivially true if the target_dir doesn't
    # actually exists, but that's not a problem
    if not os.path.exists(os.path.join(target_dir, filename)):
        return filename

    # Now continue incrementing the filename until either:
    #
    # * we find a sequentially number file which is identical, or
    # * we find a file in the sequence that does not exist yet
    if os.path.exists(filepath):
        while (os.path.exists(os.path.join(target_dir, filename)) and \
               not filecmp.cmp(filepath, os.path.join(target_dir, filename))):
                   filename = increment_filename(filename)
    else:
        while os.path.exists(os.path.join(target_dir, filename)):
            filename = increment_filename(filename)

    return filename

def safe_file_copy(src, dst_dir):
    """Given a src and dst filepath, copy the src file to dst directory in such
    a way that no duplicates are produced, and nothing is overwritten. Returns
    the path of the file that is eventually written.
    """
    src = os.path.abspath(src)
    dst_dir = os.path.abspath(dst_dir)

    safe_dst = os.path.join(dst_dir, dest_filename(src, dst_dir))

    # If the dst_dir doesn't exist, then we need to create it before copying,
    # or we'll get an error
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # If there was duplication, then we don't need to copy the files again
    if not os.path.isfile(safe_dst):
        shutil.copy(src, safe_dst)

    return safe_dst
