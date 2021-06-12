from PySimpleGUI import *
from os import listdir, path
import pygame
import json
import sys
from random import randrange
import time
import threading
import winsound
from win10toast import ToastNotifier

theme('DarkAmber')
current = None
position = 0
c = False
pygame.init()
pygame.mixer.init()
music_ended = pygame.USEREVENT
m = pygame.mixer.music
m.set_endevent(music_ended)
close_win = False

def folder():
    global current
    try:
        with open('metadata.json', 'r+') as data:
            d = json.load(data)
            fol = d['path']
            current = d['last_played']
            position = d['pos']
    except FileNotFoundError:
        fol = popup_get_folder('Select the music folder', 'Music Folder', )
        if fol == '':
            popup('\nNo folder selected\n', title='Error', keep_on_top=True)
            return folder()
        elif fol is None:
            quit()
    return fol


def music_check(fol: str):
    music = []
    global current
    for song in listdir(fol):
        if song.endswith('.mp3'):
            music.append(song)
    if not current: 
        current = music[0]
    return music


def fade(music):
    if c is True:
        v = 1
        for i in range(10):
            time.sleep(0.025*i)
            v -= 0.1
            music.set_volume(v)    

'''
def care():
    global c
    music = m
    t1 = time.time()
    while True:
        time.sleep(1)
        t2 = time.time()
        print(t2-t1)
        if t2-t1 > 60*10 and c is True:
            window['-play-'].update(image_filename=r'images\rplay.png')
            fade(music)
            music.pause()
            t = ToastNotifier()
            t.show_toast(msg=f'You listening music more than {int((t2-t1)//60)}min !!!')
            t1 = time.time()
            c = False
        elif t2-t1 > 10 and c is False:
            t1 = t2
        if close_win:
            break
'''
fol = folder()
songs = music_check(fol)
while len(songs) < 1:
    popup(f'\nNo music files found !!!\n', title='Error')
current_song = current
layout = [
    [Frame('', layout=[[Button(image_filename=r'.\images\close.png', key='-stop-', border_width=0),
                        Text('Music Player', size=(500, 1), font=('Arial', 16, 'bold'), justification='center')]])],
    [InputText(size=(53, 5), font=('times', 11), pad=((170, 15), (10, 10)), key='-IN-'), Button(' Search ', key='-search-'), Button(' Play ', visible=True, key='play', pad=((0, 0), (10, 10)))],
    [Listbox(songs, enable_events=True, key='-song-', font=['arial', 13], size=(100, 28), default_values=[songs[0]])],
    [Frame('', [[Text(current_song, auto_size_text=True, border_width=0, key='-song_name-', font=('arial', 15), pad=((0, 0), (15, 15)), size=(500, 1), justification='center')],
                [Button(image_filename=r'.\images\rshuffle.png', key='-shuffle-', border_width=0, tooltip=' Shuffle ', pad=((10, 10), (0, 10))),
                 Button(image_filename=r'.\images\rforward.png', key='-previous-', border_width=0, tooltip=' Previous ', pad=((10, 10), (0, 10))),
                 Button(image_filename=r'.\images\rplay.png', key='-play-', border_width=0, tooltip=' Play ', pad=((10, 10), (0, 10))),
                 Button(image_filename=r'.\images\rnext.png', key='-next-', border_width=0, tooltip=' Next ', pad=((10, 10), (0, 10))),
                 Button(image_filename=r'.\images\repeat.png', key='-repeat-', border_width=0, tooltip=' Rewind ', pad=((10, 10), (0, 10)))]]
           , element_justification='center')
     ]]
window = Window('Music Player', layout, size=(700, 800), no_titlebar=True, grab_anywhere=True)
start = True
found = None
pre = None
m.load(path.join(fol, current_song))
#t1 = threading.Thread(target=care)
#t1.start()
while True:
    events, values = window.read(2000)
    pyevent = pygame.event.get()
    if pyevent:
        for i in pyevent:
            if i.type == music_ended:
                next_song = songs[songs.index(current_song)+1]
                current_song = next_song
                m.load(os.path.join(fol, current_song))
                m.play()
                window['-play-'].update(image_filename=r'.\images\rpause.png')
                c = True
    if events == '-stop-' or WIN_CLOSED:
        chck = popup_yes_no('\n Do you want to exit !!! \n', title=' Error ')
        if chck == 'Yes':
            data = {}
            with open('metadata.json', 'w+') as f:
                data['path'] = fol
                data['last_played'] = current_song
                data['pos'] = m.get_pos()
                json.dump(data, f)
            close_win = True
            fade(m)
            quit()

    elif events == '-play-':
        winsound.PlaySound(r".\sounds\ButtonClick.wav", 1)
        if c is True:
            window['-play-'].update(image_filename=r'.\images\rplay.png')
            fade(m)
            m.pause()
            c = False
        elif c is False and not start:
            m.set_volume(1)
            m.unpause()
            window['-play-'].update(image_filename=r'.\images\rpause.png')
            c = True
        elif c is False and start:
            m.play(start=position/100)
            start = False
            window['-play-'].update(image_filename=r'.\images\rpause.png')
            c = True
    elif events == '-shuffle-':
        winsound.PlaySound(".\sounds\ButtonClick.wav", 1)
        start = False
        current_song = songs[randrange(0, len(songs))]
        fade(m)
        m.load(path.join(fol, current_song))
        m.play()
        m.set_volume(1)
        window['-play-'].update(image_filename=r'.\images\rpause.png')
        c = True
    elif events == '-previous-':
        winsound.PlaySound(".\sounds\ButtonClick.wav", 1)
        if current_song != songs[0]:
            start = False
            current_song = songs[songs.index(current_song)-1]
            fade(m)
            m.load(path.join(fol, current_song))
            m.play()
            m.set_volume(1)
            c = True
    elif events == '-next-':
        winsound.PlaySound(".\sounds\ButtonClick.wav", 1)
        start = False
        if values['-song-']:
            next_song = songs[songs.index(current_song)+1]
            fade(m)
            m.load(path.join(fol, next_song))
            m.play()
            m.set_volume(1)
            c = True
            current_song = next_song
            window['-play-'].update(image_filename=r'.\images\rpause.png')
    elif events == '-repeat-':
        winsound.PlaySound(".\sounds\ButtonClick.wav", 1)
        start = False
        fade(m)
        m.rewind()
        m.set_volume(1)
        window['-play-'].update(image_filename=r'.\images\rpause.png')
        c = True
    elif events == '-song-':
        start = False
        current_song = values['-song-'][0]
        fade(m)
        m.load(path.join(fol, current_song))
        m.play()
        m.set_volume(1)
        c = True
        window['-play-'].update(image_filename=r'.\images\rpause.png')
    elif events == '-search-':
        if values['-IN-'] != '':
            if values['-IN-'] != found:
                query = values['-IN-']
                pre = query
                for i in songs:
                    if query.lower() in i.lower():
                        window['-IN-'].update(value=i, select=True)
                        found = i
                        break
                else:
                    popup_ok('\nNo songs matched \n', title='Error')
            else:
                for i in songs[songs.index(values['-IN-'])+1:]:
                    if pre.lower() in i.lower():
                        window['-IN-'].update(value=i, select=True)
                        found = i
                        break
                else:
                    popup_ok('\nNo more match found\n', title='Error')
        else:
            popup_error('\nEmpty query input\n', title='Error')

    elif events == 'play':
        winsound.PlaySound(".\sounds\ButtonClick.wav", 1)
        start = False
        current_song = values['-IN-']
        if current_song not in songs:
            popup('\nPlease search and play\n', title='Error')
        else:
            fade(m)
            m.load(path.join(fol, current_song))
            m.play()
            m.set_volume(1)
            c = True
            window['-play-'].update(image_filename=r'.\images\rpause.png')
    window['-song_name-'].update(value=current_song)
