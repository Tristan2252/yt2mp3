import mutagen
from mutagen.flac import FLAC, Picture

def add_flac_cover(filename, albumart):

    #image = Picture()
#    p = Picture()
#    with open(albumart, "rb") as f: # Read bites
#        p.data = f.read()

    #ipic.type = id3.PictureType.COVER_FRONT
    #pic.mime = u"image/jpeg"
    #pic.width = 500
    #pic.height = 500
    #pic.depth = 16 # color depth
    p = open(albumart, 'rb').read()
    audio = MP3(filename)
    audio['APIC'] = APIC(3, 'image/jpeg', 3, 'Front cover', p)
    audio.save()
    
#    if albumart.endswith('png'):
#        mime = 'image/png'
#    else:
#        mime = 'image/jpeg'
#
#    p.desc = 'front cover'
#    #with open(albumart, 'rb') as f: # better than open(albumart, 'rb').read() ?
#    #    image.data = f.read()
#
#    audio.add_picture(p)
#    #mutagen.flac.FLAC.add_picture(p)
#    audio.save()
#    audio = MP3([filename], ID3=ID3)
#    audio.tags.delete([filename], delete_v1=True, delete_v2=True)
#    audio.tags.add(
#        APIC(
#            encoding=3,
#            mime='image/jpeg',
#            type=3,
#            desc=u'Cover',
#            data=open([albumart], 'rb').read()
#        )
#    )
#    audio.save([filename], v2_version=3, v1=2)

def main(): 
    song = "Test.mp3"
    art = "/Users/tristan/Documents/cool_cat.jpg"

    add_flac_cover(song, art)

if __name__ == "__main__":
    main()
