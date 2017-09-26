package board

import (
    "fmt"
    "strings"
    "os"
    "encoding/csv"
    "log"
    "strconv"
    "sort"
)
type Square struct {
    val int
    opts []int
    row int
    col int
    srow int
    scol int
}

type board [9][9]Square
var Board board
// Zero out the board
func init() {
    for i := 0; i < 9; i++ {
        var srow int
        switch {
            case i < 3:
                srow = 0
            case i > 5:
                srow = 2
            default:
                srow = 1
        }
        for j := 0; j < 9; j++ {
            var scol int
            switch {
                case j < 3:
                    scol = 0
                case j > 5:
                    scol = 2
                default:
                    scol = 1
                }
            Board[i][j] = Square{val: 0, row: i, col: j, srow: srow, scol: scol}
        }
    }
}

// Make a nice string representation of the board
func (b board) String() string {
    var bstring string
    var rowstr string
    for rowind, row := range b {
        rowstr = "|"
        for colind, square := range row {
            if (colind+1) % 3 == 0 {
                rowstr += fmt.Sprintf("%d|", square.val)
            }else{
                rowstr += fmt.Sprintf("%d", square.val)
            }
        }
        if rowind % 3 == 0 {
            bstring += strings.Repeat("-", 13) + "\n"
        }
        bstring += rowstr  + "\n"
    }
    bstring += strings.Repeat("-", 13) + "\n"
    return bstring
}

// Read a puzzle from a csv file
func (b *board) ReadFromFile(path string) {
    puzzle, err := os.Open(path)
    defer puzzle.Close()
    if err != nil {
        log.Fatal(err)
    }
    reader := csv.NewReader(puzzle)
    for rowind, row := range b {
        record, err := reader.Read()
		if err != nil {
			log.Fatal(err)
		}
        for colind, _ := range row {
            newval, err := strconv.Atoi(strings.TrimSpace(record[colind]))
            if err != nil {
                log.Fatal(err)
            }
            b[rowind][colind].val = newval
        }
    }
}

// Get all squares in a column
func (b *board) GetCol(colind int) [9]Square {
    var col [9]Square
    for ind, row := range b {
       col[ind] = row[colind]
    }
    return col
}

// Return all squares in a section
func(b *board) GetSection(srow int, scol int) [9]Square {
   var sect [9]Square
   colmin := 3*scol
   colmax := 3 + 3 * scol
   rowmin := 3*srow
   rowmax := 3 + 3 * srow
   count := 0
   for i := rowmin; i < rowmax; i++ {
       for j := colmin; j < colmax; j++ {
           sect[count] = b[i][j]
           count += 1
       }
   }
   return sect
}

// Get all the options for each square
func (b *board) GetOpts() {
    for i, row := range b {
        for j, thisSquare := range row {
            // If the square has a legit value, skip it
            if thisSquare.val != 0 {
                // fmt.Printf("Square has value of %d\n", thisSquare.val)
                continue
            }
            col := b.GetCol(j)
            section := b.GetSection(thisSquare.srow, thisSquare.scol)
            // We know there must be 8+8+8=24 other squares to check
            existing_vals := make([]int, 26)
            count := 0
            for _, sq := range row {
                // Don't check thisSquare
                if sq.row == thisSquare.row && sq.col == thisSquare.col {
                    continue
                }
                existing_vals[count] = sq.val
                count += 1
            }
            for _, sq := range col {
                if sq.row == thisSquare.row && sq.col == thisSquare.col {
                    continue
                }
                existing_vals[count] = sq.val
                count += 1
            }
            for _, sq := range section {
                if sq.row == thisSquare.row && sq.col == thisSquare.col {
                    continue
                }
                existing_vals[count] = sq.val
                count += 1
            }
            sort.Ints(existing_vals)
            // fmt.Println("Checking for vals")
            // fmt.Println(existing_vals)
            opts := make([]int, 0, 9)
            for num := 1; num < 10; num++ {
                insert := sort.SearchInts(existing_vals, num)
                if !(insert < len(existing_vals) && existing_vals[insert] == num) {
                    // fmt.Printf("Val %d is a valid option\n", num)
                    // thisSquare.opts = append(thisSquare.opts, num)
                    opts = append(opts, num)
                    // fmt.Println(thisSquare.opts)
                    // b[i][j] = thisSquare
                }
                // else {
                //     // fmt.Println(thisSquare.opts)
                //     fmt.Printf("Val %d exists. Not adding\n", num)
                // }
            }
            b[i][j].opts = opts
            // fmt.Println(b[i][j].opts)
        }
    }
}

func (b *board) EliminateOpts() {
    for i, row := range b {
        for j, sq := range row {
            // Determine if the square sq is the only location where a specific
            // option could be placed within its section
            section := b.GetSection(sq.srow, sq.scol)
            sect_possibilities := make([]int, 0, 81)
            for _, othersquare := range section {
                if (othersquare.row == sq.row && othersquare.col == sq.col) || sq.val > 0 {
                    continue
                }
                sect_possibilities = append(sect_possibilities, othersquare.opts...)
            }
            fmt.Printf("Section (%d, %d) possibilities:\n", sq.srow, sq.scol)
            fmt.Println(sect_possibilities)
            sort.Ints(sect_possibilities)
            for _, opt := range sq.opts {
                insert := sort.SearchInts(sect_possibilities, opt)
                if !(insert < len(sect_possibilities) && sect_possibilities[insert] == opt) {
                    // Set val to opt because this is the only place we can put
                    // it in the section, then clear the opts slice
                    fmt.Printf("Square (%d, %d) is the only place to put a %d", sq.row, sq.col, opt)
                    b[i][j].val = opt
                    b[i][j].opts = b[i][j].opts[:0]
                }
            }
        }
    }
}

func (b *board) SetVals() bool {
    solved := true
    for i, row := range b {
        for j, sq := range row {
            // fmt.Println(sq.opts)
            switch {
            case len(sq.opts) == 1:
                // fmt.Println("Setting val of square")
                // fmt.Println(sq.opts[0])
                b[i][j].val = sq.opts[0]
            case len(sq.opts) > 1:
                // fmt.Println("Not solved")
                // fmt.Println(sq.opts)
                solved = false
            }
        }
    }
    return solved
}
