import bz2

def decompress_until(bytesobj, halt_predicate):
    d = bz2.BZ2Decompressor()
    files = [d.decompress(bytesobj)]
    while not (d.unused_data == b'' or halt_predicate(files[-1])):
        files.append(d.decompress(d.unused_data))
    return files

