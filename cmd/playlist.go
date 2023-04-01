package cmd

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/zmb3/spotify/v2"
)

type PlaylistStruct struct {
	Id          string
	Name        string
	Tracks      []PlaylistItemStruct
	TotalTracks int
}

type PlaylistItemStruct struct {
	Name       string
	Artists    []string
	SpotifyUrl string
}

const (
	PlaylistCommandName string = "playlist"
	ListCommandName     string = "list"
	DownloadCommandName string = "download"
)

var (
	flag_playlist_id string
)

func GetPlaylistFlagSet() *flag.FlagSet {
	PlaylistFlagSet := flag.NewFlagSet(PlaylistCommandName, flag.ExitOnError)
	return PlaylistFlagSet
}

func GetListFlagSet() *flag.FlagSet {
	ListFlagSet := flag.NewFlagSet(ListCommandName, flag.ExitOnError)
	ListFlagSet.StringVar(&flag_playlist_id, "id", "", "ID of the playlist you want to list the contents of")
	return ListFlagSet
}

func GetDownloadFlagSet() *flag.FlagSet {
	DownloadFlagSet := flag.NewFlagSet(DownloadCommandName, flag.ExitOnError)
	DownloadFlagSet.StringVar(&flag_playlist_id, "id", "", "ID of the playlist you want to download the contents of")
	return DownloadFlagSet
}

func Playlist(args []string) {
	switch args[0] {
	case ListCommandName:
		List(args[1:])
	case DownloadCommandName:
		Download(args[1:])
	default:
		errorMsg := fmt.Sprintf("Expected '%s' or '%s' after the 'playlist' command.", ListCommandName, DownloadCommandName)
		log.Fatal(errorMsg)
		os.Exit(1)
	}
}

func List(args []string) {
	listCommand := GetListFlagSet()

	listCommand.Parse(args)

	if flag_playlist_id != "" {
		playlist_items := GetPlaylistTracks(flag_playlist_id)
		for _, playlist_item := range playlist_items {
			track := playlist_item.Track.Track

			fmt.Printf("%-30s %-20s %-20s\n", track.Name, track.Artists[0].Name, track.ExternalURLs["spotify"])
		}
	} else {
		playlists := GetAllPlayLists()
		for _, playlist := range playlists {
			fmt.Printf("%-20s\t %-40s\t %20d\n", playlist.ID, playlist.Name, playlist.Tracks.Total)
		}
	}
}

func Download(args []string) {
	downloadCommand := GetDownloadFlagSet()
	downloadCommand.Parse(args)

	if flag_playlist_id != "" {
		DownloadPlaylist(flag_playlist_id)
	} else {
		DownloadAllPlaylists()
	}
}

func GetPlaylist(id string) spotify.FullPlaylist {
	ctx := context.Background()
	spotify_client := GetSpotifyClient()

	playlist, err := spotify_client.GetPlaylist(ctx, spotify.ID(id))
	if err != nil {
		log.Fatal(err)
	}
	return *playlist
}

func GetPlaylistTracks(id string) []spotify.PlaylistItem {
	ctx := context.Background()
	spotify_client := GetSpotifyClient()

	playlist_items, err := spotify_client.GetPlaylistItems(ctx, spotify.ID(id))
	if err != nil {
		log.Fatal(err)
	}

	var return_list []spotify.PlaylistItem

	for page := 1; ; page++ {
		track_page, err3 := spotify_client.GetPlaylistItems(ctx, spotify.ID(id), spotify.Offset(page), spotify.Limit(len(playlist_items.Items)))
		if err3 != nil {
			log.Fatal(err3)
		}

		return_list = append(return_list, track_page.Items...)

		err2 := spotify_client.NextPage(ctx, track_page)
		if err2 == spotify.ErrNoMorePages {
			break
		}
		if err2 != nil {
			log.Fatal(err2)
		}
	}
	return return_list

}

func GetAllPlayLists() []spotify.SimplePlaylist {
	ctx := context.Background()
	spotify_client := GetSpotifyClient()

	playlists, err := spotify_client.CurrentUsersPlaylists(ctx)
	if err != nil {
		log.Fatal(err)
	}

	var return_list []spotify.SimplePlaylist

	for page := 1; ; page++ {
		playlist_page, err3 := spotify_client.CurrentUsersPlaylists(ctx, spotify.Offset(page), spotify.Limit(len(playlists.Playlists)))
		if err3 != nil {
			log.Fatal(err3)
		}

		return_list = append(return_list, playlist_page.Playlists...)

		err2 := spotify_client.NextPage(ctx, playlists)
		if err2 == spotify.ErrNoMorePages {
			break
		}
		if err2 != nil {
			log.Fatal(err2)
		}
	}
	return return_list
}

func DownloadPlaylist(id string) {
	ctx := context.Background()
	spotify_client := GetSpotifyClient()

	user, err := spotify_client.CurrentUser(ctx)
	if err != nil {
		log.Fatal(err)
	}

	current_directory, err2 := os.Getwd()
	if err2 != nil {
		log.Fatal(err2)
	}

	folder_path := filepath.Join(current_directory, user.ID)
	CreateDirectory(folder_path)

	playlist := GetPlaylist(id)
	log.Default().Println("Downloading playlist:", playlist.Name)
	playlist_tracks := GetPlaylistTracks(id)
	WriteToFile(folder_path, playlist, playlist_tracks)
}

func DownloadAllPlaylists() {
	playlists := GetAllPlayLists()
	log.Default().Println("Downloading all playlists")

	for _, playlist := range playlists {
		DownloadPlaylist(string(playlist.ID))
	}
}

func CreateDirectory(directory_path string) {
	if _, err := os.Stat(directory_path); errors.Is(err, os.ErrNotExist) {
		if err2 := os.Mkdir(directory_path, os.ModePerm); err2 != nil {
			log.Fatal(err2)
		}
	}
}

func WriteToFile(directoryPath string, playlist spotify.FullPlaylist, playlist_tracks []spotify.PlaylistItem) {
	tracks := make([]PlaylistItemStruct, len(playlist_tracks), len(playlist_tracks))
	for i, item := range playlist_tracks {
		track := item.Track.Track
		var artists []string

		for _, artist := range track.Artists {
			artists = append(artists, artist.Name)
		}

		pl_item_struct_instance := PlaylistItemStruct{
			Name:       track.Name,
			Artists:    artists,
			SpotifyUrl: track.ExternalURLs["spotify"],
		}
		tracks[i] = pl_item_struct_instance
	}

	playlist_struct_instance := PlaylistStruct{
		Id:          string(playlist.ID),
		Name:        playlist.Name,
		Tracks:      tracks,
		TotalTracks: playlist.Tracks.Total,
	}

	playlist_json, err := json.MarshalIndent(playlist_struct_instance, "", "		")
	if err != nil {
		log.Fatal(err)
	}
	filename := string(playlist.ID) + ".json"
	file, err2 := os.Create(filepath.Join(directoryPath, filename))
	if err2 != nil {
		log.Fatal(err2)
	}
	defer file.Close()

	file.WriteString(string(playlist_json))
}
