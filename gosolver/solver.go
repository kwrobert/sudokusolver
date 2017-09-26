package main

import (
    "fmt"
    "board"
    "os"
    "bufio"
)

func main() {
    filename := os.Args[1]
    fmt.Println("This is the go solver")
    // board.Board[0][3] = 4
    // fmt.Println(board.Board)
    fmt.Println(filename)
    fmt.Println(board.Board)
    board.Board.ReadFromFile(filename)
    fmt.Println(board.Board)
    // for _, row := range board.Board {
    //     for _, sq := range row {
    //         fmt.Println(sq)
    //     }
    // }
    fmt.Println(board.Board.GetCol(3))
    fmt.Println(board.Board.GetSection(0, 0))
    fmt.Println(board.Board[1][0])
    fmt.Println(board.Board)
    // board.Board.GetOpts()
    // solved := board.Board.SetVals()
    // fmt.Println(board.Board)
    // fmt.Println(solved)
    solved := false
    for !solved {
        board.Board.GetOpts()
        board.Board.EliminateOpts()
        solved = board.Board.SetVals()
        fmt.Println(board.Board)
        reader := bufio.NewReader(os.Stdin)
        fmt.Print("Enter text: ")
        _, _ = reader.ReadString('\n')
    }

}
