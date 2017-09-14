package main

import (
    "fmt"
    "board"
)

func main() {
    fmt.Println("This is the go solver")
    fmt.Println(board.Board)
    board.Board[0][3] = 4
    fmt.Println(board.Board)
}
