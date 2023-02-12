import requests
import os
import json
from Track import Track
from Artist import Artist
from Playlist import Playlist


# to get a list with recently played tracks 
def getRecentlyPlayedTracks(auth_token, limit=20):
    # getting response
    response = requests.get(
        url=f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )
    # creating list
    tracks = [Track(track["track"]["name"],track["track"]["id"],track["track"]["popularity"],track["track"]["artists"][0]["name"]) 
                for track in response.json()["items"]]
    return tracks


# to get a list with recently played artists 
def getRecentlyPlayedArtists(auth_token):
    # getting response
    response = requests.get(
        url="https://api.spotify.com/v1/me/player/recently-played?limit=20",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )
    # creating list
    artists = []
    for track in response.json()["items"]:
        artist = Artist(track["track"]["artists"][0]["name"],track["track"]["artists"][0]["id"])
        # to prevent duplicates
        if artist not in artists:
            artists.append(artist)
    return artists
   

# to get a list with top played tracks or artists
# type='artists' for top artists, type='tracks' for top tracks 
def getTopItems(auth_token, type):
    # getting response
    response = requests.get(
        url=f"https://api.spotify.com/v1/me/top/{type}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )
    # creating list
    if type == 'tracks':
        items = [Track(track["name"],track["id"],track["popularity"],track["artists"][0]["name"]) 
                for track in response.json()["items"]]
    else:
        items = [Artist(artist["name"],artist["id"]) for artist in response.json()["items"]]
    return items


# to get a list with recommended tracks based on seed tracks
# seedType='track' or seedType='artist'
def getRecommendedTracks(auth_token, seeds, limit, seedType):
    # getting seed url from seeds
    seed_url = ""
    for seed in seeds:
        seed_url += seed.id + ","
    # getting response
    response = requests.get(
        url=f"https://api.spotify.com/v1/recommendations?seed_{seedType}s={seed_url[:-1]}&limit={limit}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )
    # creating list
    tracks = [Track(track["name"],track["id"],track["popularity"],track["artists"][0]["name"]) 
                for track in response.json()["tracks"]]
    return tracks


# to get a list with current user's playlists 
def getUserPlaylists(auth_token):
    # getting response
    response = requests.get(
        url="https://api.spotify.com/v1/me/playlists", 
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )
    # creating list
    playlists = [Playlist(playlist["name"],playlist["id"]) 
                for playlist in response.json()["items"]]
    return playlists


# to get a list with tracks of a playlist
def getTracksOfAPlaylist(auth_token, playlistId):
    # getting response
    response = requests.get(
        url=f"https://api.spotify.com/v1/playlists/{playlistId}/tracks",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )
    # creating list
    tracks = [Track(track["track"]["name"],track["track"]["id"],track["track"]["popularity"],track["track"]["artists"][0]["name"]) 
                for track in response.json()["items"]]
    return tracks


# to create a playlist
def createPlaylistWithGivenTracks(auth_token, user_id, playlistName, tracks):
    # posting request to create playlist
    response = requests.post(
        url=f"https://api.spotify.com/v1/users/{user_id}/playlists",
        data=json.dumps({"name": playlistName, "public": False}),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )
    playlist = Playlist(playlistName, response.json()["id"])
    # adding tracks 
    addTracksToAPlaylist(auth_token,playlist.id,tracks)
    return playlist


# to add tracks to a playlist
def addTracksToAPlaylist(auth_token, playlistId, tracks):
    # creating track uris
    trackURIs = [f"spotify:track:{track.id}" for track in tracks]
    # posting request to add tracks
    response = requests.post(
        url=f"https://api.spotify.com/v1/playlists/{playlistId}/tracks",
        data=json.dumps(trackURIs),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    )


# takes inputs from the user and creates playlist
def getInputAndCreatePlaylist(auth_token, user_id, seeds, seedType):
    while(True):
        try:
            # getting input
            playlistLimit = input("Enter how many tracks do you want in your playlist: ")
            if playlistLimit == "EXIT": break # to break the loop if needed
            playlistName = input("Enter a name for the playlist: ")
            if playlistName == "EXIT": break # to break the loop if needed
            # getting recommended tracks
            recommendedTracks = getRecommendedTracks(auth_token,seeds,playlistLimit,seedType)
            # creaating playlist and adding tracks
            createPlaylistWithGivenTracks(auth_token,user_id,playlistName=playlistName,tracks=recommendedTracks)
            print("\nYour new playlist is created. You can access it from your library.\nPress enter to return to main menu.")
            input()
            inp = None
            break
        except:
            # if there are errors
            print("Invalid limit or name! Try again or type EXIT to exit.")
            inp = None



# to clear the terminal
def clear():
    os.system("cls" if os.name=="nt" else "clear")


# prints a menu with given items and message
# takes input from the user and checks it, returns valid input
# itemType is used for input message
def printMenuWithItemsAndGetInput(itemList, message, itemType):
    clear()
    print(f"-------------------------------- SPOTIFY PLAYLIST CREATOR --------------------------------\n\n{message}")
    # to list items
    i = 1
    for item in itemList:
        print(f"{i}. {item}")
        i+=1
    print(f"""{i}. Back
{i+1}. Exit
""")
    inp = input(f"Select {itemType}s up to 5 by entering numbers seperated by spaces: ")
    # to go back
    if inp == str(i):
        return None
    # to exit
    elif inp == str(i+1):
        quit()
    # to check if the input is valid 
    else:
        while(True):
            indexList = []
            invalid = False
            try:
                indexList = inp.split(" ")
                if len(indexList) > 5: invalid = True
                for num in indexList:
                    if int(num) < 1 or int(num) > i-1:
                        invalid = True
            except:
                invalid = True
            if invalid:
                inp = input(f"Invalid input!\nSelect {itemType}s up to 5 by entering numbers seperated by spaces: ")
            else:
                return indexList


def main():
    
    # initializing authotization token and user id from environment variables
    auth_token = os.getenv("SPOTIFY_AUTHORIZATION_TOKEN")
    user_id = os.getenv("SPOTIFY_USER_ID")


    inp = None
    while(inp not in ["1","2","3"]):
        # to print main menu
        clear()
        print("""-------------------------------- SPOTIFY PLAYLIST CREATOR --------------------------------\n
1. Create playlists with your recommendations based on the tracks or artists you selected.
2. Create extended versions of your playlists.
3. Exit
""")
        inp = input("Select by entering a number: ")

        # to print create playlists with recommendations options
        if inp == "1":
            inp = None
            while(inp not in ["1","2","3","4","5","6"]):
                clear()
                print("""------------------------------- SPOTIFY PLAYLIST CREATOR --------------------------------\n
Select from
1. Your Recently Played Tracks
2. Your Recently Played Artists
3. Your Top Tracks
4. Your Top Artists
5. Back
6. Exit
""")
                inp = input("Select by entering a number: ")

                # to print recently played tracks
                if inp == "1":
                    recentlyPlayedTracks = getRecentlyPlayedTracks(auth_token)
                    inp = printMenuWithItemsAndGetInput(itemList=recentlyPlayedTracks,message="Your Recently Played Tracks",itemType='track')
                    if inp == None: continue
                    seedTracks = [recentlyPlayedTracks[int(index)-1] for index in inp]
                    # getting inputs and creating playlist
                    getInputAndCreatePlaylist(auth_token,user_id,seeds=seedTracks,seedType='track')
                    

                # to print recently played artists
                elif inp == "2":
                    recentlyPlayedArtists = getRecentlyPlayedArtists(auth_token)
                    inp = printMenuWithItemsAndGetInput(itemList=recentlyPlayedArtists,message="Your Recently Played Artists",itemType='artist')
                    if inp == None: continue
                    seedArtists = [recentlyPlayedArtists[int(index)-1] for index in inp]
                    # getting inputs and creating playlist
                    getInputAndCreatePlaylist(auth_token,user_id,seeds=seedArtists,seedType='artist')
                    

                # to print top tracks
                elif inp == "3":
                    topTracks = getTopItems(auth_token,type='tracks')
                    inp = printMenuWithItemsAndGetInput(itemList=topTracks,message="Your Top Tracks",itemType='track')
                    if inp == None: continue
                    seedTracks = [topTracks[int(index)-1] for index in inp]
                    # getting inputs and creating playlist
                    getInputAndCreatePlaylist(auth_token,user_id,seeds=seedTracks,seedType='track')


                # to print top artists
                elif inp == "4":
                    topArtists = getTopItems(auth_token,type='artists')
                    inp = printMenuWithItemsAndGetInput(itemList=topArtists,message="Your Top Artists",itemType='artist')
                    if inp == None: continue
                    seedArtists = [topArtists[int(index)-1] for index in inp]
                    # getting inputs and creating playlist
                    getInputAndCreatePlaylist(auth_token,user_id,seeds=seedArtists,seedType='artist')

                # to go back 
                elif inp == "5":
                    pass

                # to exit
                elif inp == "6":
                    quit()
                
                
        # to print create new extended playlists options
        elif inp == "2":
            inp = None
            clear()
            print("""-------------------------------- SPOTIFY PLAYLIST CREATOR --------------------------------\n\nSelect one of your playlists""")
            
            # to get and list items
            playlistList = getUserPlaylists(auth_token)
            i = 1
            for item in playlistList:
                print(f"{i}. {item}")
                i+=1
            print(f"""{i}. Back
{i+1}. Exit
""")
            # getting input
            invalid = True
            while(invalid):
                inp = input("Select by entering a number: ")
                # to go back
                if inp == str(i):
                    break
                # to exit
                elif inp == str(i+1):
                    quit()
                # to check if the input is valid 
                else:
                    invalid = False
                    try:
                        index = int(inp)
                        if index < 1 or index > i-1:
                            invalid = True
                    except: invalid = True

                    # if input is valid
                    if not invalid:
                        # getting tracks from the selected playlist
                        playlistId = playlistList[index-1].id
                        tracksInPlaylist = getTracksOfAPlaylist(auth_token,playlistId)
                        while(True):
                            try:
                                playlistName = input("Enter a name for the playlist: ")
                                if playlistName == "EXIT": break # to break the loop if needed
                                playlist = createPlaylistWithGivenTracks(auth_token,user_id,playlistName,tracksInPlaylist)
                                tracksInPlaylistCut = tracksInPlaylist[:]
                                # getting recommendations based on first five track 
                                if len(tracksInPlaylist) > 5:
                                    tracksInPlaylistCut = tracksInPlaylistCut[:5]
                                recommendedTracks = getRecommendedTracks(auth_token,tracksInPlaylistCut,limit=5,seedType='track')
                                addTracksToAPlaylist(auth_token,playlist.id,recommendedTracks)

                                # adding recommended songs to the playlist
                                i = 1
                                while(i<10):
                                    tracksInPlaylist = getTracksOfAPlaylist(auth_token,playlist.id)
                                    tracksInPlaylistCut = tracksInPlaylist[5*i:5*i+5]
                                    recommendedTracks = getRecommendedTracks(auth_token,tracksInPlaylistCut,limit=5,seedType='track')
                                    addTracksToAPlaylist(auth_token,playlist.id,recommendedTracks)
                                    i+=1
                                
                                print("\nYour extended playlist is created with 50 new tracks. You can access it from your library.\nPress enter to return to main menu.")
                                input()
                                inp = None
                                break
                            except:
                                # if there are any errors
                                print("Something went wrong! Try again or type EXIT to exit.")
                                inp = None


if __name__ == "__main__":
    main()

