import os
import sys
import argparse
from mutagen.id3 import ID3
from mutagen.id3 import ID3NoHeaderError

extension = '.mp3'
args = None    # Define this globally so it can be used without passing it as a parameter

def dir_list(dir_name):
    """Generates a list of all files in a directory (including sub
    directories if recursive) and returns it"""
    outputList = []
    if args.recursiveclean:
        for root, dirs, files in os.walk(dir_name):
            outputList.append(root)
            for d in dirs:
                outputList.append('/'.join([root, d]))
            for f1 in files:
                outputList.append('/'.join([root, f1]))
        return outputList
    else:
        for f in os.listdir(dir_name):
            outputList.append(os.path.join(dir_name, f))
        return outputList

def move():
    """Moves every song in a directory (recursivly) to another directory"""
    if not args.verbose:
        print('Moving...')
    for song in dir_list(args.fromdir):
        if song[-4:] == extension:
            newsong = os.path.split(song)[1]
            songdir = os.path.split(song)[0]

            os.rename(os.path.join(songdir, newsong), os.path.join(args.todir, newsong))
            if args.verbose:
                print('Moved ' + song)
    if not args.verbose:
        print('Done')

def buildnums():
    """Generates a list of numbers (as strings) 00..99 to use when
    removing track numbers from file names"""
    nums = []
    for i in range(100):
        if i < 10:
            nums.append('0'+str(i))
        else:
            nums.append(str(i))
    return nums

def smartclean(basedir, song):
    """Performs cleaning actions such as removing extra spaces, the
    artist, and track numbers from the filename. Also tries to capitolize
    the first letter of every word."""
    begin_nums = buildnums()

    #Get the song's artist for removal later
    artist = ''
    try:
        audio = ID3(os.path.join(basedir, song))
        artist = audio['TPE1'].text[0]
    except KeyError:
        print(song+' has no artist info')
    except ID3NoHeaderError:
        print(song + ' has no ID3 header')

    newname = song

    #Remove the artist name if in the file name
    if artist in newname:
        if   artist.lower()+'-' in newname.lower():
            newname = newname.lower().replace(artist.lower()+'-', '')
        elif artist+' - ' in newname:
            newname = newname.lower().replace(artist.lower()+' - ', '')
        else:
            newname = newname.lower().replace(artist.lower(), '')
            
    parts = newname.split()

    # Remove track numbers from the beginning of filenames
    if parts[0] in begin_nums:
        parts.remove(parts[0])

    # Remove non alphabetic characters at the beginning of filenames
    if not parts[0][0].lower() in 'abcdefghijklmnopqrstuvwxyz':
        parts.remove(parts[0])

    # Capitolize each word
    for part in parts:
        parts[parts.index(part)] = part[0].upper() + part[1:]

    # Rejoin the parts (also gets rid of extra spaces)
    newname = ''
    for part in parts:
        newname += part
        if not part == parts[-1]:
            newname += ' '

    return newname

def clean():
    """Cleans filenames of strange formatting such as having the artist or
    track number in the file name. Also capitolizes each word. Can be used
    to remove an arbitrary number of characters from the beginning or end
    of a file name."""

    if not args.verbose:
        print('Cleaning...')
    songlist = []

    for song in dir_list(args.fromdir):
        if extension in song:
            basedir = os.path.split(song)[0]
            song = os.path.split(song)[1]
            
            # Try to set the filename to the song's ID3 Title
            try:
                audio = ID3(os.path.join(basedir, song))
                newname = (audio['TIT2'].text[0] + extension).encode('ascii', 'ignore')
                if '/' in newname or '\\' in newname or '"' in newname or ':' in newname or '*' in newname or '?' in newname or '<' in newname or '>' in newname or '|' in newname:
                    raise KeyError
            # If that doesn't work try some smart cleaning features
            except KeyError:
                newname = smartclean(basedir, song)
            except ID3NoHeaderError:
                newname = smartclean(basedir, song)

            # If the name changed from the origional then rename it
            if newname != song and not newname == '':
                if args.verbose:
                    print(song + ' ==> ' + newname)
                os.rename(os.path.join(basedir, song), os.path.join(basedir, newname))

    if not args.verbose:
        print('Done')

def main():
    """Parses arguments and call the rest of the program"""
    parser = argparse.ArgumentParser()
    parser.add_argument('fromdir', help='Specify the directory to read from.')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity.',
                        action='store_true')
    parser.add_argument('-r', '--recursiveclean', help='Allow cleaning to search directories recursivly for files.',
                        action='store_true')
    parser.add_argument('-t', '--todir', help='Specify the directory to move music to. If none names will only be cleaned.')

    args = parser.parse_args()

    clean()
    if not args.todir == None: #Move music
        move()

if __name__ == '__main__':
    main()
