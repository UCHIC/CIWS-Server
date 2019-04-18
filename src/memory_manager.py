import os

def check_mem(partition):
    return sorted(
        (os.path.join(dirname, filename)
         for dirname, dirnames, filenames in os.walk(partition)
         for filename in filenames),
        key=lambda fn: os.stat(fn).st_mtime), reversed == True


def delete_oldest(free_bytes_required, partition):
    file_list = check_mem(partition)
    while file_list:
        statv = os.statvfs(partition)
        if statv.f_bfree * statv.f_bsize >= free_bytes_required:
            break
        os.remove(file_list.pop())

delete_oldest()