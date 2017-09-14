package board

import (
    "fmt"
    "strings"
)

type board [9][9]int

func (b board) String() string {
    var bstring string
    var rowstr string
    for rowind, row := range b {
        rowstr = "|"
        for colind, num := range row {
            if (colind+1) % 3 == 0 {
                rowstr += fmt.Sprintf("%d|", num)
            }else{
                rowstr += fmt.Sprintf("%d", num)
            }
        }
        if (rowind) % 3 == 0 {
            bstring += strings.Repeat("-", 13) + "\n"
        }
        bstring += rowstr  + "\n"
    }
    bstring += strings.Repeat("-", 13) + "\n"
    return bstring
}

var Board board

// Zero out the board
func init() {
    for i := 0; i < 9; i++ {
        for j := 0; j < 9; j++ {
            Board[i][j] = 0
        }
    }
}

// {
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0},
//         [9]int{0,0,0,0,0,0,0,0,0}
//     }
