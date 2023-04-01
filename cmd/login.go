package cmd

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/joho/godotenv"
	"github.com/zmb3/spotify/v2"
	spotifyauth "github.com/zmb3/spotify/v2/auth"
	"golang.org/x/oauth2"
)

const (
	LoginCommandName string = "login"
	cache_filename          = ".cache"
)

var (
	ch    = make(chan *spotify.Client)
	state = GenerateRandomString(64)
	auth  *spotifyauth.Authenticator
)

func GetLoginFlagSet() *flag.FlagSet {
	LoginFlagSet := flag.NewFlagSet(LoginCommandName, flag.ExitOnError)
	return LoginFlagSet
}

func Login() {
	godotenv.Load(".env")
	port := os.Getenv("http_port")
	redirect_uri := os.Getenv("spotify_redirect_uri")
	client_id := os.Getenv("spotify_client_id")
	client_secret := os.Getenv("spotify_client_secret")
	auth = spotifyauth.New(
		spotifyauth.WithClientID(client_id),
		spotifyauth.WithClientSecret(client_secret),
		spotifyauth.WithRedirectURL(redirect_uri),
		spotifyauth.WithScopes(spotifyauth.ScopePlaylistReadPrivate, spotifyauth.ScopeUserLibraryRead, spotifyauth.ScopePlaylistReadCollaborative),
	)

	http.HandleFunc("/callback", completeAuth)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		log.Default().Println("Received unexpected request for:", r.URL.String())
	})

	go func() {
		err := http.ListenAndServe(fmt.Sprintf(":%s", port), nil)
		if err != nil {
			log.Fatal(err)
		}
	}()

	auth_url := auth.AuthURL(state)
	fmt.Println("If your browser doesn't open, please log in to Spotify by visiting the following link in your browser:", auth_url)

	client := <-ch
	user, err := client.CurrentUser(context.Background())
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Now logged in as %s (%s).", user.DisplayName, user.ID)
}

func GenerateRandomString(length int) string {
	var possibleValues []rune = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
	var randomString strings.Builder
	rand.Seed(time.Now().UnixMicro())

	for i := 0; i < length; i++ {
		index := rand.Intn(len(possibleValues))
		randomString.WriteRune(possibleValues[index])
	}

	return randomString.String()
}

func completeAuth(w http.ResponseWriter, r *http.Request) {
	token, err := auth.Token(r.Context(), state, r)
	if err != nil {
		http.Error(w, "Couldn't get token", http.StatusForbidden)
		log.Fatal(err)
	}

	if received_state := r.FormValue("state"); received_state != state {
		http.NotFound(w, r)
		log.Fatal(fmt.Sprintf("State mismatch %s != %s", received_state, state))
	}

	client := spotify.New(auth.Client(r.Context(), token))
	fmt.Fprintf(w, "Login Completed!\nYou may now close this window.")

	json_token, err2 := json.Marshal(token)
	if err2 != nil {
		log.Fatal(err2)
	}

	file, err3 := os.Create(cache_filename)
	if err3 != nil {
		log.Fatal(err3)
	}

	defer file.Close()
	file.WriteString(string(json_token))

	ch <- client
}

func CacheFileExists() bool {
	current_directory, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}

	cache_file_path := filepath.Join(current_directory, cache_filename)

	if _, err2 := os.Stat(cache_file_path); errors.Is(err2, os.ErrNotExist) {
		return false
	}

	return true
}

func GetAuthToken() oauth2.Token {
	if !CacheFileExists() {
		log.Fatal("There are no credentials stored! Please run `spotilistcli login` to generate new credentials.")
	}

	token_file, err := os.Open(".cache")
	if err != nil {
		log.Fatal(err)
	}

	defer token_file.Close()

	raw_token, err2 := ioutil.ReadAll(token_file)
	if err2 != nil {
		log.Fatal(err2)
	}

	var oauth2_token *oauth2.Token
	json.Unmarshal(raw_token, &oauth2_token)
	return *oauth2_token
}

func GetSpotifyClient() *spotify.Client {
	auth_token := GetAuthToken()

	ctx := context.Background()

	auth_client := spotifyauth.New().Client(ctx, &auth_token)
	spotify_client := spotify.New(auth_client)
	return spotify_client
}
