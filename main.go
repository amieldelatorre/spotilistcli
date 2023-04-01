package main

import (
	"fmt"
	"log"
	"os"

	"github.com/amieldelatorre/spotilistcli/cmd"
)

func main() {

	if len(os.Args) < 2 {
		fmt.Println("Expected 'login' or 'playlist' command")
		os.Exit(1)
	}

	switch os.Args[1] {
	case cmd.LoginCommandName:
		cmd.Login()
	case cmd.PlaylistCommandName:
		cmd.Playlist(os.Args[2:])
	default:
		log.Fatal("Expected 'login' or 'playlist' command")
		os.Exit(1)
	}

}
