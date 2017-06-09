from subprocess import call
basecmd = ["mplayer", "-ao", "alsa:device=bluetooth"]
myfile = "bath_1.mp3"
call(basecmd + [myfile])
