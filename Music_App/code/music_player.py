import pandas as pd  # Vor Ausführung noch pandas und tqdm installieren
from tqdm import tqdm
import time


def load_data():  # CSV-Speicherort noch anpassen
    try:
        return pd.read_csv(
            "C:/Users/johan/OneDrive/Desktop/Projekte/Music_App/data/spotify_dataframe_cleaned.csv")
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame()


favorite_songs = []
playlists = {}


def search_music(data, query):
    while True:
        print("\nSuchalgorithmus Auswahl:")
        print("1 - Binary Search")
        print("2 - Linear Search")
        print("0 - Zurück")
        choice = input("Wähle einen Suchalgorithmus: ")

        if choice == '1':
            binary_search(data, query)
            break
        elif choice == '2':
            linear_search(data, query)
            break
        elif choice == '0':
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


def binary_search(data, query):  # Binary Search
    query = query.lower()  # für Kleinbuchstaben
    left, right = 0, len(data) - 1
    results = []
    start_time = time.time()  # Startzeit

    # Sortiert Daten basierend auf den Titeln
    data = data.sort_values('track_name', kind='mergesort').reset_index(drop=True)

    # Fortschrittsbalken
    pbar = tqdm(total=len(data), desc="Binary Search läuft", unit="Einträge", leave=True)

    while left <= right:
        mid = (left + right) // 2
        mid_value = data.iloc[mid]['track_name'].lower() if isinstance(data.iloc[mid]['track_name'], str) else ""

        # Aktualisierung des Fortschrittsbalken
        pbar.update(abs(left - right) // 2)

        # Überprüfe, ob der Titel mit der Suchanfrage beginnt
        if mid_value.startswith(query):
            l, r = mid, mid
            while l >= 0 and isinstance(data.iloc[l]['track_name'], str) and data.iloc[l][
                'track_name'].lower().startswith(query):
                results.append(data.iloc[l])
                l -= 1
                pbar.update(1)
            while r < len(data) and isinstance(data.iloc[r]['track_name'], str) and data.iloc[r][
                'track_name'].lower().startswith(query):
                if r != mid:
                    results.append(data.iloc[r])
                r += 1
                pbar.update(1)
            break
        elif mid_value < query:
            left = mid + 1
        else:
            right = mid - 1

    pbar.close()
    end_time = time.time()  # Endzeit
    print(f"\nBinary Search abgeschlossen in {end_time - start_time:.2f} Sekunden.")

    if not results:
        print("Keine Ergebnisse gefunden.")
    else:
        handle_search_results(pd.DataFrame(results), data)


def linear_search(data, query):  # Linear Search
    query = query.lower()
    results = []

    start_time = time.time()

    with tqdm(total=len(data), desc="Linear Search läuft", unit="Einträge", leave=True) as pbar:
        for index, row in data.iterrows():
            track_name = row['track_name']
            if isinstance(track_name, str) and track_name.lower().startswith(query):
                results.append(row)
            pbar.update(1)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nLinear Search abgeschlossen in {elapsed_time:.2f} Sekunden.")

    # Suchergebnisse anzeigen
    if not results:
        print("Keine Ergebnisse gefunden.")
    else:
        handle_search_results(pd.DataFrame(results), data)


def display_song_list_with_options(songs, list_title, handle_song_selection):
    while True:
        print(f"\n{list_title}:")
        songs_list = songs.reset_index(drop=True)
        for index, row in songs_list.iterrows():
            album = row['album_name'] if pd.notna(row['album_name']) else 'Unbekannt'
            print(
                f"{index + 1}. Titel: {row['track_name']}, Album: {album}, Künstler: {row['artists']}, Genre: {row['track_genre']}")

        print("\nOptionen:")
        print("1 - Titel anhören")
        print("0 - Zurück")
        choice = input("Wähle eine Option: ")

        if choice == '1':
            try:
                song_choice = int(input("Wähle die Nummer des Titels zum Anhören: ")) - 1
                if 0 <= song_choice < len(songs_list):
                    chosen_song = songs_list.iloc[song_choice]
                    handle_song_selection(chosen_song)
                else:
                    print("Ungültige Nummer, bitte erneut versuchen.")
            except ValueError:
                print("Bitte gib eine gültige Nummer ein.")
        elif choice == '0':
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


def handle_search_results(results, data):
    display_song_list_with_options(results, "Gefundene Ergebnisse", lambda song: listen_to_title(song, results, data))


# Titel anhören und Untermenü
def listen_to_title(title, results, original_data):
    is_paused = False
    display_now_playing(title)

    while True:
        print("\nOptionen:")
        if title_in_favorites(title):
            print("1 - Pause / Play")
            print("2 - Titel aus Lieblingssongs entfernen")
            print("3 - Titel zu Playlist hinzufügen")
        else:
            print("1 - Pause / Play")
            print("2 - Titel zu Lieblingssongs hinzufügen")
            print("3 - Titel zu Playlist hinzufügen")

        print("0 - Zurück")
        choice = input("Wähle eine Option: ")

        if choice == '1':
            if is_paused:
                print(f"\n🔊 Titel '{title['track_name']}' wird fortgesetzt. 🔊")
                is_paused = False
            else:
                print(f"\nTitel '{title['track_name']}' pausiert.")
                is_paused = True
        elif choice == '2':
            if title_in_favorites(title):
                remove_from_favorites(title)
            else:
                add_to_favorites(title)
            display_now_playing(title)
        elif choice == '3':
            handle_playlist_options(title)
            display_now_playing(title)
        elif choice == '0':
            return
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


def display_now_playing(title):
    album = title['album_name'] if pd.notna(title['album_name']) else 'Unbekannt'
    print(f"\n🔊 Es läuft {title['track_name']} von {title['artists']} (Album: {album}) 🔊")


# Playlist-Optionen
def handle_playlist_options(title):
    while True:
        print("\nPlaylist-Optionen:")
        print("1 - Neue Playlist erstellen")

        # Überprüfung ob Playlists existiert
        if playlists:
            print("2 - Bestehende Playlists")
            has_playlists = True
        else:
            has_playlists = False

        print("0 - Zurück")
        choice = input("Wähle eine Option: ")

        if choice == '1':
            create_new_playlist(title)
            break
        elif choice == '2' and has_playlists:
            choose_existing_playlist(title)
            break
        elif choice == '0':
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


def create_new_playlist(title):
    playlist_name = input("\nGib einen Namen für die neue Playlist ein: ").strip()
    if not playlist_name:
        print("Ungültiger Name. Bitte versuche es erneut.")
    elif playlist_name in playlists:
        print(f"Eine Playlist mit dem Namen '{playlist_name}' existiert bereits.")
    else:
        playlists[playlist_name] = [title]
        print(f"Playlist '{playlist_name}' erstellt und Titel '{title['track_name']}' hinzugefügt.")


def choose_existing_playlist(title):
    while True:
        print("\nBestehende Playlists:")
        playlist_names = list(playlists.keys())
        for index, name in enumerate(playlist_names, 1):
            print(f"{index} - {name}")

        try:
            choice = int(
                input("Bitte wähle eine Playlist, um den Titel hinzuzufügen, oder wähle 0, um zurückzugehen: "))
            if choice == 0:
                break
            elif 1 <= choice <= len(playlist_names):
                playlist_name = playlist_names[choice - 1]
                playlists[playlist_name].append(title)
                print(f"'{title['track_name']}' wurde zur Playlist '{playlist_name}' hinzugefügt.")
                break
            else:
                print("Ungültige Nummer, bitte erneut versuchen.")
        except ValueError:
            print("Bitte gib eine gültige Nummer ein.")


def title_in_favorites(title):
    return title['track_name'] in [song['track_name'] for song in favorite_songs]


def add_to_favorites(title):
    if not title_in_favorites(title):
        favorite_songs.append(title)
        print(f"\nTitel '{title['track_name']}' zu Lieblingssongs hinzugefügt.")
    else:
        print(f"\nTitel '{title['track_name']}' ist bereits in den Lieblingssongs.")


def remove_from_favorites(title):
    global favorite_songs
    favorite_songs = [song for song in favorite_songs if song['track_name'] != title['track_name']]
    print(f"\nTitel '{title['track_name']}' aus Lieblingssongs entfernt.")


def display_favorite_songs():
    if not favorite_songs:
        print("Du hast keine gespeicherten Lieblingssongs.")
    else:
        display_song_list_with_options(pd.DataFrame(favorite_songs), "Meine Lieblingssongs", lambda song: listen_to_title(song, favorite_songs, favorite_songs))



def display_favorite_artists():
    if not favorite_songs:
        print("Du hast keine gespeicherten Künstler.")
    else:
        while True:
            favorite_artists = list({song['artists'] for song in favorite_songs})
            print("\nMeine Künstler:")
            for index, artist in enumerate(favorite_artists, 1):
                print(f"{index}. {artist}")

            sub_choice = input(
                "\nWähle die Nummer eines Künstlers, um seine Songs anzuzeigen, oder 0, um zurückzugehen: ")
            if sub_choice == '0':
                break
            else:
                try:
                    artist_index = int(sub_choice) - 1
                    if 0 <= artist_index < len(favorite_artists):
                        chosen_artist = favorite_artists[artist_index]
                        display_artist_songs(chosen_artist)
                    else:
                        print("Ungültige Nummer, bitte erneut versuchen.")
                except ValueError:
                    print("Bitte gib eine gültige Nummer ein.")


def handle_favorite_songs():
    while True:
        sub_choice = input("\nWähle die Nummer eines Titels, um ihn abzuspielen, oder 0, um zurückzugehen: ")
        if sub_choice == '0':
            break  # Zurück zum Favoriten-Menü
        else:
            try:
                song_index = int(sub_choice) - 1
                if 0 <= song_index < len(favorite_songs):
                    chosen_song = favorite_songs[song_index]
                    listen_to_title(chosen_song, pd.DataFrame(favorite_songs))
                else:
                    print("Ungültige Nummer, bitte erneut versuchen.")
            except ValueError:
                print("Bitte gib eine gültige Nummer ein.")


def display_artist_songs(artist):
    artist_songs = [song for song in favorite_songs if song['artists'] == artist]
    display_song_list_with_options(pd.DataFrame(artist_songs), f"Gespeicherte Songs von {artist}", lambda song: listen_to_title(song, artist_songs, artist_songs))


def display_favorite_genres():
    if not favorite_songs:
        print("Du hast noch keine gespeicherten Genres.")
    else:
        while True:
            favorite_genres = list({song['track_genre'] for song in favorite_songs})
            print("\nMeine Genres:")
            for index, genre in enumerate(favorite_genres, 1):
                print(f"{index}. {genre}")

            sub_choice = input("\nWähle die Nummer eines Genres, um die Songs anzuzeigen, oder 0, um zurückzugehen: ")
            if sub_choice == '0':
                break
            else:
                try:
                    genre_index = int(sub_choice) - 1
                    if 0 <= genre_index < len(favorite_genres):
                        chosen_genre = favorite_genres[genre_index]
                        display_genre_songs(chosen_genre)
                    else:
                        print("Ungültige Nummer, bitte erneut versuchen.")
                except ValueError:
                    print("Bitte gib eine gültige Nummer ein.")



def display_genre_songs(genre):
    genre_songs = [song for song in favorite_songs if song['track_genre'] == genre]
    display_song_list_with_options(pd.DataFrame(genre_songs), f"Gespeicherte Songs im Genre {genre}", lambda song: listen_to_title(song, genre_songs, genre_songs))


# Favoriten-Menü
def favorites_menu():
    while True:
        print("\nFavoriten:")
        print("1 - Meine Lieblingssongs")
        print("2 - Meine Künstler")
        print("3 - Meine Genres")
        print("0 - Zurück")
        choice = input("Wähle eine Option: ")

        if choice == '1':
            display_favorite_songs()
        elif choice == '2':
            display_favorite_artists()
        elif choice == '3':
            display_favorite_genres()
        elif choice == '0':
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


# Playlists verwalten
def manage_playlists():
    while True:
        print("\nPlaylists verwalten:")
        print("1 - Neue Playlist erstellen")
        print("2 - Bestehende Playlists")
        print("3 - Playlist bearbeiten")
        print("4 - Playlist löschen")
        print("0 - Zurück")
        choice = input("Wähle eine Option: ")

        if choice == '1':
            playlist_name = input("\nGib einen Namen für die neue Playlist ein: ").strip()
            if not playlist_name:
                print("Ungültiger Name. Bitte versuche es erneut.")
            elif playlist_name in playlists:
                print(f"Eine Playlist mit dem Namen '{playlist_name}' existiert bereits.")
            else:
                playlists[playlist_name] = []
                print(f"Playlist '{playlist_name}' erstellt.")
        elif choice == '2':
            view_playlists()
        elif choice == '3':
            edit_playlist()
        elif choice == '4':
            delete_playlist()
        elif choice == '0':
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")

def view_playlists():
    if not playlists:
        print("Du hast noch keine Playlists.")
    else:
        while True:
            print("\nBestehende Playlists:")
            playlist_names = list(playlists.keys())
            for index, name in enumerate(playlist_names, 1):
                print(f"{index}. {name}")

            sub_choice = input("\nWähle die Nummer einer Playlist, um sie anzuzeigen, oder 0, um zurückzugehen: ")
            if sub_choice == '0':
                break
            else:
                try:
                    playlist_index = int(sub_choice) - 1
                    if 0 <= playlist_index < len(playlist_names):
                        chosen_playlist = playlist_names[playlist_index]
                        manage_playlist(chosen_playlist)
                    else:
                        print("Ungültige Nummer, bitte erneut versuchen.")
                except ValueError:
                    print("Bitte gib eine gültige Nummer ein.")


def manage_playlist(playlist_name):
    while True:
        playlist_songs = playlists[playlist_name]
        print(f"\nSongs in der Playlist '{playlist_name}':")
        for index, song in enumerate(playlist_songs, 1):
            album = song['album_name'] if pd.notna(song['album_name']) else 'Unbekannt'
            print(f"{index}. Titel: {song['track_name']}, Album: {album}, Künstler: {song['artists']}")

        sub_choice = input("\nWähle die Nummer eines Titels, um ihn abzuspielen, oder 0, um zurückzugehen: ")
        if sub_choice == '0':
            break
        else:
            try:
                song_index = int(sub_choice) - 1
                if 0 <= song_index < len(playlist_songs):
                    chosen_song = playlist_songs[song_index]
                    listen_to_title(chosen_song, pd.DataFrame(playlist_songs))
                else:
                    print("Ungültige Nummer, bitte erneut versuchen.")
            except ValueError:
                print("Bitte gib eine gültige Nummer ein.")


# Playlist bearbeiten
def edit_playlist():
    if not playlists:
        print("Du hast noch keine Playlists.")
    else:
        while True:
            print("\nWähle eine Playlist zum Bearbeiten:")
            playlist_names = list(playlists.keys())
            for index, name in enumerate(playlist_names, 1):
                print(f"{index}. {name}")

            sub_choice = input("\nWähle die Nummer einer Playlist, um Songs zu entfernen, oder 0, um zurückzugehen: ")
            if sub_choice == '0':
                break
            else:
                try:
                    playlist_index = int(sub_choice) - 1
                    if 0 <= playlist_index < len(playlist_names):
                        chosen_playlist = playlist_names[playlist_index]
                        remove_song_from_playlist(chosen_playlist)
                    else:
                        print("Ungültige Nummer, bitte erneut versuchen.")
                except ValueError:
                    print("Bitte gib eine gültige Nummer ein.")


# Song aus Playlist entfernen
def remove_song_from_playlist(playlist_name):
    while True:
        playlist_songs = playlists[playlist_name]
        print(f"\nSongs in der Playlist '{playlist_name}':")
        for index, song in enumerate(playlist_songs, 1):
            album = song['album_name'] if pd.notna(song['album_name']) else 'Unbekannt'
            print(f"{index}. Titel: {song['track_name']}, Album: {album}, Künstler: {song['artists']}")

        sub_choice = input("\nWähle die Nummer eines Titels, um ihn zu entfernen, oder 0, um zurückzugehen: ")
        if sub_choice == '0':
            break
        else:
            try:
                song_index = int(sub_choice) - 1
                if 0 <= song_index < len(playlist_songs):
                    removed_song = playlist_songs.pop(song_index)
                    print(f"'{removed_song['track_name']}' wurde aus der Playlist '{playlist_name}' entfernt.")
                    if not playlist_songs:  # Lösche Playlist, wenn sie leer ist
                        del playlists[playlist_name]
                        print(f"Playlist '{playlist_name}' wurde gelöscht, da sie leer ist.")
                        break
                else:
                    print("Ungültige Nummer, bitte erneut versuchen.")
            except ValueError:
                print("Bitte gib eine gültige Nummer ein.")


def delete_playlist():
    if not playlists:
        print("Du hast noch keine Playlists.")
    else:
        while True:
            print("\nWähle eine Playlist zum Löschen:")
            playlist_names = list(playlists.keys())
            for index, name in enumerate(playlist_names, 1):
                print(f"{index}. {name}")

            sub_choice = input("\nWähle die Nummer einer Playlist zum Löschen, oder 0, um zurückzugehen: ")
            if sub_choice == '0':
                break
            else:
                try:
                    playlist_index = int(sub_choice) - 1
                    if 0 <= playlist_index < len(playlist_names):
                        chosen_playlist = playlist_names[playlist_index]
                        confirm = input(
                            f"Bist du sicher, dass du die Playlist '{chosen_playlist}' löschen möchtest? (j/n): ").lower()
                        if confirm == 'j':
                            del playlists[chosen_playlist]
                            print(f"Playlist '{chosen_playlist}' wurde gelöscht.")
                            break
                        else:
                            print("Löschvorgang abgebrochen.")
                    else:
                        print("Ungültige Nummer, bitte erneut versuchen.")
                except ValueError:
                    print("Bitte gib eine gültige Nummer ein.")


# Hauptmenü
def main_menu():
    data = load_data()
    if data.empty:
        return

    while True:
        print("\nHauptmenü:")
        print("1 - Durchsuchen und sortieren")
        print("2 - Favoriten")
        print("3 - Playlists verwalten")
        print("4 - Entdecken")
        print("0 - Beenden")
        choice = input("Wähle eine Option: ")

        if choice == '1':
            sort_or_search_menu(data)
        elif choice == '2':
            favorites_menu()
        elif choice == '3':
            manage_playlists()
        elif choice == '4':
            explore_genres(data)
        elif choice == '0':
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


def sort_or_search_menu(data):
    while True:
        print("\nDurchsuchen und sortieren:")
        print("1 - Suche nach einem Titel")
        print("2 - Sortieren A-Z nach Titel")
        print("3 - Sortieren Z-A nach Titel")
        print("0 - Zurück")
        choice = input("Wähle eine Option: ")

        if choice == '1':
            query = input("Gib einen Suchbegriff ein (Titel): ")
            search_music(data, query)
        elif choice == '2':
            sort_data(data, ascending=True)
        elif choice == '3':
            sort_data(data, ascending=False)
        elif choice == '0':
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


def sort_data(songs, ascending=True):
    while True:
        print("\nWähle einen Sortieralgorithmus:")
        print("1 - Quick Sort")
        print("2 - Bubble Sort")
        print("0 - Zurück")
        choice = input("Wähle einen Sortieralgorithmus: ")

        if choice == '1':
            songs = songs.to_dict('records') if isinstance(songs, pd.DataFrame) else songs
            sorted_songs = quick_sort(songs, ascending=ascending)
            sorted_songs_df = pd.DataFrame(sorted_songs)
            handle_search_results(sorted_songs_df, sorted_songs_df)
            break
        elif choice == '2':
            songs = songs.to_dict('records') if isinstance(songs, pd.DataFrame) else songs
            sorted_songs = bubble_sort(songs, ascending=ascending)
            sorted_songs_df = pd.DataFrame(sorted_songs)
            handle_search_results(sorted_songs_df, sorted_songs_df)
            break
        elif choice == '0':
            break
        else:
            print("Ungültige Eingabe, bitte erneut versuchen.")


def bubble_sort(data, ascending=True):
    start_time = time.time()
    n = len(data)

    pbar = tqdm(range(n), desc="Bubble Sort läuft", unit="Durchläufe")

    for i in pbar:
        swapped = False
        for j in range(0, n - i - 1):
            if isinstance(data[j]['track_name'], str) and isinstance(data[j + 1]['track_name'], str):
                if (ascending and data[j]['track_name'].lower() > data[j + 1]['track_name'].lower()) or \
                        (not ascending and data[j]['track_name'].lower() < data[j + 1]['track_name'].lower()):
                    data[j], data[j + 1] = data[j + 1], data[j]
                    swapped = True
        if not swapped:
            break

    pbar.close()
    end_time = time.time()
    print(f"Bubble Sort abgeschlossen in {end_time - start_time:.2f} Sekunden.")

    return data


def quick_sort(data, ascending=True):
    start_time = time.time()

    pbar = tqdm(total=len(data), desc="Quick Sort läuft", unit="Einträge")

    data = data if isinstance(data, list) else data.to_dict('records')

    def quicksort_helper(data):
        if len(data) <= 1:
            pbar.update(len(data))
            return data
        else:
            pivot = data[len(data) // 2]

            left = [x for x in data if
                    isinstance(x['track_name'], str) and x['track_name'].lower() < pivot['track_name'].lower()]
            middle = [x for x in data if
                      isinstance(x['track_name'], str) and x['track_name'].lower() == pivot['track_name'].lower()]
            right = [x for x in data if
                     isinstance(x['track_name'], str) and x['track_name'].lower() > pivot['track_name'].lower()]

            sorted_left = quicksort_helper(left)
            sorted_right = quicksort_helper(right)
            pbar.update(len(left) + len(right))
            return sorted_left + middle + sorted_right

    sorted_data = quicksort_helper(data)
    pbar.close()

    end_time = time.time()
    print(f"\nQuick Sort abgeschlossen in {end_time - start_time:.2f} Sekunden.")
    return sorted_data if ascending else sorted_data[::-1]


def display_sorted_songs(sorted_data):
    print("\nSortierte Songs:")
    for index, song in enumerate(sorted_data, 1):
        album = song['album_name'] if pd.notna(song['album_name']) else 'Unbekannt'
        print(
            f"{index}. Titel: {song['track_name']}, Album: {album}, Künstler: {song['artists']}, Genre: {song['track_genre']}")


# Genres in der gesamten Datenbank anzeigen
def explore_genres(data):
    genres = list({row['track_genre'] for _, row in data.iterrows()})
    if not genres:
        print("Es gibt keine Genres in der Datenbank.")
    else:
        while True:
            print("\nEntdecke neue Musikrichtungen und Genres:")
            for index, genre in enumerate(genres, 1):
                print(f"{index}. {genre}")

            sub_choice = input("\nWähle die Nummer eines Genres, um die Songs anzuzeigen, oder 0, um zurückzugehen: ")
            if sub_choice == '0':
                break
            else:
                try:
                    genre_index = int(sub_choice) - 1
                    if 0 <= genre_index < len(genres):
                        chosen_genre = genres[genre_index]
                        display_genre_songs_from_data(chosen_genre, data)
                    else:
                        print("Ungültige Nummer, bitte erneut versuchen.")
                except ValueError:
                    print("Bitte gib eine gültige Nummer ein.")


def display_genre_songs_from_data(genre, data):
    genre_songs = data[data['track_genre'] == genre].reset_index(drop=True)
    display_song_list_with_options(genre_songs, f"Songs im Genre '{genre}'", lambda song: listen_to_title(song, genre_songs, data))


if __name__ == "__main__":
    main_menu()
