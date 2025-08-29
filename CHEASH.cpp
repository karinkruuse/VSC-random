/*                     ___     __               _
   ___ _____ _____  __| _/____|  |_ _____ _____| | __
 _/ __\\__  \\_ __\/ __ |/  __/  | \\__  \\_   \ |/ /
 \  \__ / __ \| | / /_/ |\__ \|  _  \/ __ \| |\/   <
  \____(____  /_| \____ |/____)__|_ (____  /_| |_|_ \
            \/         \/          \/    \/        \/
  _   _  ____ ___  /\
 | \ | \/ __//   \/  \        25th   July   2025
 |  \|  | _|/ /\_/  \ \
 | _  _ |   \ \( \  _  )      V E R S I O N  1.0
 |_|\// /___|\___/\_|_ \
      \/              \/
*/
#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <map>
#include <math.h>
#include <iomanip>
#include <string>
#include <thread>  // for std::this_thread::sleep_for
#include <chrono>  // for std::chrono::seconds
#include <unordered_map>
#include <unordered_set>
#include <locale>
#include <tuple>
#include <set>

using namespace std;

#ifdef _WIN32
    #include <conio.h>  // for _kbhit() and _getch()
	#include <windows.h>  // Add this line for console API
#else
    #include <termios.h>
    #include <unistd.h>
#endif

string currentUI = ""; // save color setting for UI
string invertUI = ""; // reverse settings

// │─┤ ♣ test: symbols that the console needs to be capable to print

#ifdef _WIN32
    char readFirstCharacter() { // Windows version using _getch()
        return _getch();  // read single character without waiting for SPACE
    }
#else
    char readFirstCharacter() { // Linux version using termios to read the first character
        struct termios oldt, newt;
        char ch;

        // get current terminal settings
        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO); // disable canonical mode (line buffering) and echo
        tcsetattr(STDIN_FILENO, TCSANOW, &newt); // apply new settings
        ch = getchar();  // read single character without waiting for SPACE

        // restore original terminal settings (works surprisingly fluently in "quick spin mode")
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);

        return ch;
    }
#endif

enum HVcolor {
    c1,
    c2,
    c3,
    c4,
    c5
};

HVcolor colorsceme = c1;

enum COLOR {
    magenta,
    purple,
    blue,
    green,
    red,
    white,
    gray,
    mint,
    wario,
    vinyl,
    neww1,
    neww2,
    neww3,
    neww4
};

const char* toString(COLOR color) {
    switch (color) {
        case magenta: return "magenta";
        case purple: return "purple";
        case blue: return "blue";
        case green: return "green";
        case red: return "red";
        case white: return "white";
        case gray: return "gray";
        case mint: return "mint";
        case wario: return "Wario";
        case vinyl: return "vinyl";
        case neww1: return "Waluigi";
        case neww2: return "violet";
        case neww3: return "spring";
        case neww4: return "ocean";
        default: return "unknown";
    }
}

enum TSTYLE {
    knight,
    CardShark,
    slimShark,
    boxShark,
    boxSharky,
    shortFunk,
    CardKoi,
    original,
    box,
    abstract,
    funkShark,
    simply,
    simplest,
    Roman,
    Roman2,
    Roman3,
    modern,
    words,
    ghosty,
    curse,
    new1,
    new2,
    new3,
    new4,
    racing,
    monster
};

bool HVbox = true;
COLOR DEFAULT_COLOR = purple;
TSTYLE DEFAULT_STYLE;
bool FAT_UI = false;
int INITIAL_POINTS = 10000; // initial credit
int PRINTSCREEN = 200; // 999 <=> no screens printed during simulation
int FMODES = -1; // -1 <=> random choice during simulation
bool BONUSPRINT = false;
double games;
int animate = 1; // -1 <=> no animation

// set text color (platform-specific), works on (some) android systems too
void setTextColor(const std::string& colorCode, COLOR color, bool FAT_UI, bool HVbox) {
#ifdef _WIN32
HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
if (colorCode == "WIN"){
    SetConsoleTextAttribute(hConsole, BACKGROUND_RED | BACKGROUND_GREEN | BACKGROUND_BLUE | BACKGROUND_INTENSITY );
} else if (colorCode == "WI"){ // indicates 'passive' symbols on winning line
    SetConsoleTextAttribute(hConsole, BACKGROUND_RED | BACKGROUND_GREEN | BACKGROUND_BLUE );
} else if (colorCode == "TRG") {
    if (HVbox)
    SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_INTENSITY );
    else
    SetConsoleTextAttribute(hConsole, BACKGROUND_BLUE | BACKGROUND_INTENSITY );
} else if (colorCode == "WLD") {
	SetConsoleTextAttribute(hConsole, BACKGROUND_RED |
									FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
} else if (colorCode == "HV4") {
    if (HVbox)
	SetConsoleTextAttribute(hConsole, BACKGROUND_RED | BACKGROUND_BLUE |
                                     FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
    else
    SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_BLUE);
} else if (colorCode == "HV2") {
    if (HVbox)
	SetConsoleTextAttribute(hConsole, BACKGROUND_BLUE | BACKGROUND_INTENSITY |
                                     FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
    else
    SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_INTENSITY);
} else if (colorCode == "HV1") {
    if (HVbox)
    SetConsoleTextAttribute(hConsole, BACKGROUND_BLUE | BACKGROUND_GREEN |
                                     FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
    else
    SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_GREEN);
} else if (colorCode == "HV5") {
    if (HVbox)
    SetConsoleTextAttribute(hConsole, BACKGROUND_RED | BACKGROUND_BLUE | BACKGROUND_INTENSITY |
                                     FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
    else
    SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
} else if (colorCode == "HV3") {
    if (HVbox)
    SetConsoleTextAttribute(hConsole, BACKGROUND_BLUE | BACKGROUND_GREEN | BACKGROUND_INTENSITY |
                                     FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
    else
    SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY);

} else if (colorCode == "LV1" || colorCode == "LV2" || colorCode == "LV3") {
    SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
} else if (colorCode == "LV4" || colorCode == "LV5" || colorCode == "LV6" || colorCode == "LV7") {
    SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE);
} else if (colorCode == "$$") {
    SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN);
} else if (colorCode == "xx") {
    SetConsoleTextAttribute(hConsole, FOREGROUND_RED);
} else if (colorCode == "X7X") {
    if (HVbox)
    SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN | FOREGROUND_BLUE);
    else
    SetConsoleTextAttribute(hConsole, BACKGROUND_GREEN | BACKGROUND_BLUE);
} else // if (colorCode == "RESET") // not necessary
{
    if (color == magenta)
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
    else if (color == purple)
        SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | (FOREGROUND_GREEN | FOREGROUND_BLUE) | FOREGROUND_INTENSITY);
    else if (color == blue)
        SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE |
        BACKGROUND_RED | BACKGROUND_GREEN | BACKGROUND_BLUE );
    else if (color == green)
        SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN);
    else if (color == red)
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED);
    else if (color == white)
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
    else if (color == gray)
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE);
    else if (color == mint)
        SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_GREEN );
    else if (color == wario)
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN );
    else if (color == vinyl)
        SetConsoleTextAttribute(hConsole, BACKGROUND_RED | BACKGROUND_GREEN | BACKGROUND_BLUE);
    else // misc if not used under windows
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
}

#else
    if (colorCode == "WIN"){
        cout << "\033[1m\033[38;5;16m\033[48;5;15m";
    } else if (colorCode == "WI"){
        cout << "\033[22m\033[38;5;16m\033[48;5;248m";
    }
    else if (colorCode == "TRG")
    {
        if (HVbox){
            if (colorsceme == c1)
            cout << "\033[1m\033[38;5;38m";
            else if (colorsceme == c2)
            cout << "\033[1m\033[38;5;36m";
            else if (colorsceme == c4)
            cout << "\033[1m\033[38;5;222m";
            else if (colorsceme == c5)
            cout << "\033[22m\033[38;5;202m\033[48;5;54m";
            else
            cout << "\033[1m\033[38;5;27m";
        }else{
            if (colorsceme == c1)
            cout << "\033[1m\033[48;5;38m\033[38;5;16m";
            else if (colorsceme == c2)
            cout << "\033[1m\033[48;5;36m\033[38;5;16m";
            else if (colorsceme == c4)
            cout << "\033[1m\033[48;5;222m\033[38;5;16m";
            else if (colorsceme == c5)
            cout << "\033[22m\033[38;5;202m\033[48;5;54m";
            else
            cout << "\033[1m\033[48;5;27m\033[38;5;16m";
        }
    }
    else if (colorCode == "WLD")
    {
        if (colorsceme == c3) cout << "\033[1m\033[38;5;213m";
        else if (colorsceme == c2) cout << "\033[22m\033[48;5;93m\033[38;5;7m";
        else if (colorsceme == c4) cout << "\033[1m\033[38;5;203m";
        else if (colorsceme == c5) {
            if (HVbox)
            cout << "\033[22m\033[48;5;161m\033[38;5;17m";
            else
            cout << "\033[22m\033[38;5;161m";
        }
        else if ( DEFAULT_COLOR == red) cout << "\033[1m\033[48;5;124m\033[38;5;253m";
        else if ( DEFAULT_COLOR == mint) cout << "\033[1m\033[48;5;37m\033[38;5;124m";
        else if ( DEFAULT_COLOR == vinyl) cout << "\033[1m\033[48;5;159m\033[38;5;52m";
        else if ( DEFAULT_COLOR == white) cout << "\033[22m\033[48;5;253m\033[38;5;124m";
        else cout << "\033[22m\033[48;5;124m\033[38;5;253m";
    }
    else if (colorCode == "HV1") {
        if (HVbox){
            if (colorsceme == c1)      cout << "\033[1m\033[48;5;33m\033[38;5;16m";
            else if (colorsceme == c2) cout << "\033[22m\033[48;5;37m\033[38;5;16m";
            else if (colorsceme == c3) cout << "\033[1m\033[48;5;161m\033[38;5;16m";
            else if (colorsceme == c4) cout << "\033[1m\033[48;5;118m\033[38;5;16m";
            else cout << "\033[22m\033[38;5;15m\033[48;5;61m";
        }else{
            if (colorsceme == c1) cout << "\033[1m\033[38;5;33m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[38;5;140m";
            else if (colorsceme == c3) cout << "\033[1m\033[38;5;161m";
            else if (colorsceme == c4) cout << "\033[1m\033[38;5;118m";
            else cout << "\033[1m\033[48;5;252m\033[38;5;61m";
        }
    } else if (colorCode == "HV2") {
        if (HVbox){
            if (colorsceme == c1) cout << "\033[1m\033[48;5;57m\033[38;5;16m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[48;5;74m\033[38;5;16m";
            else if (colorsceme == c3) cout << "\033[1m\033[48;5;162m\033[38;5;16m";
            else if (colorsceme == c4) cout << "\033[1m\033[48;5;119m\033[38;5;16m";
            else cout << "\033[22m\033[38;5;15m\033[48;5;97m";
        }else{
            if (colorsceme == c1) cout << "\033[1m\033[38;5;57m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[38;5;147m";
            else if (colorsceme == c3) cout << "\033[1m\033[38;5;162m";
            else if (colorsceme == c4) cout << "\033[1m\033[38;5;119m";
            else cout << "\033[1m\033[48;5;252m\033[38;5;97m";
        }
    } else if (colorCode == "HV3") {
        if (HVbox){
            if (colorsceme == c1) cout << "\033[1m\033[48;5;92m\033[38;5;16m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[48;5;117m\033[38;5;16m";
            else if (colorsceme == c3) cout << "\033[1m\033[48;5;163m\033[38;5;16m";
            else if (colorsceme == c4) cout << "\033[1m\033[48;5;120m\033[38;5;16m";
            else cout << "\033[22m\033[38;5;15m\033[48;5;133m";
        }else{
            if (colorsceme == c1) cout << "\033[1m\033[38;5;92m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[38;5;117m";
            else if (colorsceme == c3) cout << "\033[1m\033[38;5;163m";
            else if (colorsceme == c4) cout << "\033[1m\033[38;5;120m";
            else cout << "\033[1m\033[48;5;252m\033[38;5;133m";
        }
    } else if (colorCode == "HV4") {
        if (HVbox){
            if (colorsceme == c1) cout << "\033[1m\033[48;5;165m\033[38;5;16m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[48;5;147m\033[38;5;16m";
            else if (colorsceme == c3) cout << "\033[1m\033[48;5;164m\033[38;5;16m";
            else if (colorsceme == c4) cout << "\033[1m\033[48;5;121m\033[38;5;16m";
            else cout << "\033[22m\033[38;5;15m\033[48;5;169m";
        }else{
            if (colorsceme == c1) cout << "\033[1m\033[38;5;165m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[38;5;74m";
            else if (colorsceme == c3) cout << "\033[1m\033[38;5;164m";
            else if (colorsceme == c4) cout << "\033[1m\033[38;5;121m";
            else cout << "\033[1m\033[48;5;252m\033[38;5;169m";
        }
    } else if (colorCode == "HV5") {
        if (HVbox){
            if (colorsceme == c1) cout << "\033[1m\033[48;5;162m\033[38;5;16m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[48;5;140m\033[38;5;16m";
            else if (colorsceme == c3) cout << "\033[1m\033[48;5;165m\033[38;5;16m";
            else if (colorsceme == c4) cout << "\033[1m\033[48;5;122m\033[38;5;16m";
            else cout << "\033[22m\033[38;5;15m\033[48;5;205m";
        }else{
            if (colorsceme == c1) cout << "\033[1m\033[38;5;162m"; // done
            else if (colorsceme == c2) cout << "\033[22m\033[38;5;37m";
            else if (colorsceme == c3) cout << "\033[1m\033[38;5;165m";
            else if (colorsceme == c4) cout << "\033[1m\033[38;5;122m";
            else cout << "\033[1m\033[48;5;252m\033[38;5;205m";
        }
    }
    else if (colorCode == "LV1") {
        if (DEFAULT_STYLE == box) { cout << "\033[22m\033[48;5;250m\033[38;5;16m"; }
        else { cout << "\033[22m\033[38;5;253m";
        if (DEFAULT_COLOR == mint || DEFAULT_COLOR == blue ) cout << "\033[38;5;245m"; }
    } else if (colorCode == "LV2") {
        if (DEFAULT_STYLE == box) { cout << "\033[22m\033[48;5;249m\033[38;5;16m"; }
        else { cout << "\033[22m\033[38;5;252m";
        if (DEFAULT_COLOR == mint || DEFAULT_COLOR == blue) cout << "\033[38;5;244m"; }
    } else if (colorCode == "LV3") {
        if (DEFAULT_STYLE == box) { cout << "\033[22m\033[48;5;248m\033[38;5;16m"; }
        else{ cout << "\033[22m\033[38;5;251m";
        if (DEFAULT_COLOR == mint || DEFAULT_COLOR == blue) cout << "\033[38;5;243m"; }
    } else if (colorCode == "LV4") {
        if (DEFAULT_STYLE == box) { cout << "\033[22m\033[48;5;247m\033[38;5;16m"; }
        else{ cout << "\033[22m\033[38;5;250m";
        if (DEFAULT_COLOR == mint || DEFAULT_COLOR == blue) cout << "\033[38;5;242m"; }
    } else if (colorCode == "LV5") {
        if (DEFAULT_STYLE == box) { cout << "\033[22m\033[48;5;246m\033[38;5;16m"; }
        else{ cout << "\033[22m\033[38;5;249m";
        if (DEFAULT_COLOR == mint || DEFAULT_COLOR == blue) cout << "\033[38;5;241m"; }
    } else if (colorCode == "LV6") {
        if (DEFAULT_STYLE == box) { cout << "\033[22m\033[48;5;245m\033[38;5;16m"; }
        else{ cout << "\033[22m\033[38;5;248m";
        if (DEFAULT_COLOR == mint || DEFAULT_COLOR == blue) cout << "\033[38;5;240m"; }
    } else if (colorCode == "LV7") {
        if (DEFAULT_STYLE == box) { cout << "\033[22m\033[48;5;244m\033[38;5;16m"; }
        else{ cout << "\033[22m\033[38;5;247m";
        if (DEFAULT_COLOR == mint || DEFAULT_COLOR == blue) cout << "\033[38;5;239m"; }
    } else if (colorCode == "$$") {
        cout << "\033[22m\033[38;5;70m";
    } else if (colorCode == "xx") {
        cout << "\033[22m\033[38;5;197m";
    }
    else if (colorCode == "X7X")
    {
        if (HVbox){
            if (colorsceme == c1) cout << "\033[1m\033[38;5;205m";
            else if (colorsceme == c2) cout << "\033[1m\033[38;5;207m";
            else if (colorsceme == c4) cout << "\033[1m\033[38;5;230m";
            else if (colorsceme == c5) cout << "\033[22m\033[48;5;202m\033[38;5;54m";
            else cout << "\033[1m\033[38;5;31m";
        }else{
            if (colorsceme == c1) cout << "\033[1m\033[48;5;205m\033[38;5;16m";
            else if (colorsceme == c2) cout << "\033[1m\033[48;5;207m\033[38;5;16m";
            else if (colorsceme == c4) cout << "\033[1m\033[48;5;230m\033[38;5;16m";
            else if (colorsceme == c5) cout << "\033[22m\033[48;5;202m\033[38;5;54m";
            else cout << "\033[1m\033[48;5;31m\033[38;5;16m";
        }
    }
    else // if (colorCode == "RESET") // not necessary
    {
        if (color == magenta)
            cout << "\033[22m\033[48;5;16m\033[38;5;206m";
        else if (color == purple)
            cout << "\033[22m\033[48;5;16m\033[38;5;129m";
        else if (color == blue)
            cout << "\033[22m\033[48;5;252m\033[38;5;27m";
        else if (color == green)
            cout << "\033[22m\033[48;5;16m\033[38;5;37m";
        else if (color == red)
            cout << "\033[22m\033[48;5;16m\033[38;5;1m";
        else if (color == white)
            cout << "\033[22m\033[48;5;16m\033[38;5;253m";
        else if (color == gray)
            cout << "\033[22m\033[48;5;16m\033[38;5;246m";
        else if (color == vinyl)
            cout << "\033[22m\033[48;5;52m\033[38;5;159m";
        else if (color == wario)
            cout << "\033[22m\033[48;5;16m\033[38;5;214m";
        else if (color == mint)
            cout << "\033[22m\033[48;5;15m\033[38;5;37m";
        else if (color == neww1)
            cout << "\033[22m\033[48;5;16m\033[38;5;93m";
        else if (color == neww2)
            cout << "\033[22m\033[48;5;16m\033[38;5;141m";
        else if (color == neww3)
            cout << "\033[22m\033[48;5;16m\033[38;5;158m";
        else if (color == neww4)
            cout << "\033[22m\033[48;5;16m\033[38;5;21m";

         if (FAT_UI) { cout << "\033[1m"; }
    }
#endif
}

const bool simpleT = true; // changes the win table slightly
const bool simple = false; // true: additional empty lines to better fit to on screen keyboards on mobile devices
const bool applyCOS = true; // set to false to play test with unmodified reel draws but equal win sizes
const bool simulateCOS = false; // simulate in !test_mode with all cosmetic changes being set before win calculation (yields same results, already verified)
const bool simulateLIM = true; // true: keep activated for stat output for win limited RtPs
const bool preMod = false; // additionally print the original grid in test_mode

const bool forceTANK = false;
const bool forceMEGA = false;

int longspin; // used to determine in a given spin whether NEARWIN becomes relevant (number size indicates impact)
bool NEARWIN = true; // determines whether reel 5 gets extra spin time in case of a 'decent match' if set to true and spinning==true
bool loanShark = false; // selectable in menu, keep set to false
int SPINS = 15;
const int wlLength = 241;
const int sim_risk = 2; // 0: normal, 1: risk, 2: shark
const int clear=10000; // number of skipped lines to get console ready

const int REEL_COUNT = 5; // dependant on the game this is not necessarily equivalent to COLUMN_COUNT
const int ROW_COUNT = 4;
const int COLUMN_COUNT = 5;
const double price = 20; // single (min.) game price for betFactor 1
int betFactor=1; //start with game price of 20
int fgwinsize[5] = {}; // track special feature win sizes

const int huge_win = 50000; // minimum free game win (at bet 100) to print a notification in !test_mode (50000: notify for "insane" wins)
const int BIG = 25, HUG = 50, ENO = 100, UNB = 200, INS = 500;

double Xi=0; int WINi=0; double Qi=0; double Sn=0; // for standard derivation
double approx_RTP = 0.97; // for the survival parameter, could also be auto calculated in a running simulation (with certain disadvantages)
double scale_param = 0.5 / approx_RTP; // simulate that the player gets half their bets back to estimate survival parameter
const double survInitial = 100; //number of bets that are used for survival estimation initially
int printWSIZE = 0; // print ~250 additional lines for detailled win distribution, changable in menu
int statinterval = 1000000; // frequency of simulation output
bool cheat = false; // gain additional luck when playing, yields much more than 100% RtP statistically

struct cosInfo {
    int win;
    vector<vector<string>> screen;
    int reel;
    int pos;
    string symbol;
};

struct reelMod {
    int reel;
    int pos;
    string symbol;

    // Equality operator needed for unordered_set
    bool operator==(const reelMod& other) const {
        return reel == other.reel && pos == other.pos && symbol == other.symbol;
    }
};

// Custom hash function for reelMod so it can be used as a key in unordered_set
namespace std {
    template <>
    struct hash<reelMod> {
        size_t operator()(const reelMod& mod) const {
            return hash<int>()(mod.reel) ^ hash<int>()(mod.pos) ^ hash<string>()(mod.symbol);
        }
    };
}

vector<string> symbols = {"LV1", "LV2", "LV3", "LV4", "LV5", "LV6", "LV7", "HV1", "HV2", "HV3", "HV4", "HV5", "WLD", "TRG", "X7X", "0"};

const vector<string> HVsymbols = { "HV1", "HV2", "HV3", "HV4", "HV5"};

double winLimit[241]; // to estimate RtP excluding wins of at least given numbers of bets

void makespinsconsistantlyquickviaprinting(){ // scrolls down the console screen for quick spin mode without unpleasant spin transitions
    for (int i=0; i<clear; i++){
        cout<< endl;
	}
}

double DiaUnit = 0.001;
void printDia(double rtpLimit){
    int bound = round(rtpLimit / DiaUnit);
    for (int i=0; i < std::min(bound, 32); i++ )
        cout << "■";
}


vector<vector<string>> reels1 = { //for first option on every reel
{
"LV3",
"LV3",
"LV3",
"HV1",
"HV1",
"HV1",
"HV1",
"LV7",
"LV4",
"LV4",
"LV5",
"LV7",
"LV1",
"HV4",
"LV4",
"HV4",
"HV4",
"HV4",
"LV6",
"LV6",
"LV2",
"LV2",
"LV2",
"WLD",
"LV6",
"LV7",
"HV3",
"HV3",
"LV1",
"HV3",
"LV6",
"HV3",
"HV3",
"HV3",
"LV5",
"HV2",
"HV2",
"LV7",
"LV3",
"HV2",
"HV2",
"LV5",
"HV5",
"LV5",
"HV5",
"HV5",
"HV5",
"LV2",
"HV5",
"LV4",
"HV5",
"LV1",
"LV1"
},
{
"HV1",
"LV4",
"HV1",
"HV1",
"LV3",
"HV1",
"HV1",
"LV5",
"LV1",
"LV1",
"LV1",
"LV3",
"HV3",
"LV2",
"HV3",
"HV3",
"LV5",
"HV3",
"LV6",
"HV5",
"LV2",
"HV5",
"LV5",
"LV5",
"HV5",
"HV5",
"LV1",
"LV6",
"WLD",
"LV3",
"WLD",
"LV3",
"HV4",
"HV4",
"LV7",
"HV4",
"HV4",
"LV2",
"LV2",
"LV2",
"LV4",
"LV4",
"LV4",
"WLD",
"LV4",
"HV2",
"LV6",
"LV3",
"LV6",
"HV2",
"LV7",
"LV6",
"HV2",
"LV7",
"HV2",
"LV7"
},
{
"HV1",
"LV3",
"HV1",
"LV5",
"HV1",
"LV6",
"HV5",
"LV2",
"HV5",
"LV2",
"HV5",
"LV4",
"HV5",
"LV3",
"LV4",
"LV6",
"LV1",
"LV1",
"LV1",
"WLD",
"HV2",
"LV3",
"LV3",
"HV2",
"HV2",
"HV2",
"HV2",
"LV7",
"LV6",
"HV2",
"LV5",
"HV3",
"LV5",
"HV3",
"LV5",
"LV2",
"HV3",
"LV7",
"HV3",
"LV7",
"LV7",
"LV1",
"LV4",
"LV4",
"LV4",
"LV6",
"LV2",
"HV4",
"LV2",
"HV4",
"HV4",
"HV4",
"LV6",
"HV4",
"HV4",
"LV3"
},
{
"LV5",
"HV1",
"LV4",
"HV1",
"LV2",
"HV1",
"LV4",
"HV1",
"LV7",
"LV7",
"LV1",
"X7X",
"LV5",
"LV6",
"HV3",
"HV3",
"LV3",
"HV3",
"HV3",
"LV6",
"LV1",
"LV1",
"WLD",
"WLD",
"LV1",
"HV2",
"LV5",
"HV2",
"HV2",
"LV3",
"HV2",
"HV2",
"LV3",
"HV5",
"HV5",
"LV5",
"HV5",
"HV5",
"LV2",
"LV5",
"LV2",
"LV4",
"HV4",
"HV4",
"LV6",
"HV4",
"HV4",
"LV4",
"HV4",
"LV1",
"LV3",
"WLD",
"LV7",
"LV7",
"LV7",
"LV2",
"TRG",
"LV6"
},
{
"LV6",
"LV5",
"LV5",
"HV1",
"LV7",
"HV1",
"HV1",
"LV6",
"LV6",
"HV1",
"LV1",
"TRG",
"LV2",
"LV2",
"HV2",
"HV2",
"HV2",
"HV2",
"LV1",
"LV1",
"X7X",
"LV1",
"LV5",
"LV4",
"LV4",
"HV4",
"LV3",
"HV4",
"HV4",
"LV5",
"HV4",
"LV6",
"WLD",
"LV4",
"HV5",
"LV7",
"HV5",
"LV7",
"HV5",
"HV5",
"HV5",
"LV2",
"LV2",
"LV3",
"LV3",
"LV3",
"LV4",
"HV3",
"HV3",
"HV3",
"HV3",
"LV7",
"HV3",
"LV7",
"LV7",
"LV1",
"LV1",
"LV5",
"LV5"
}
};

vector<vector<string>> reels2 = { //for second option on every reel
{
"LV4",
"HV1",
"LV6",
"LV6",
"HV1",
"LV2",
"HV1",
"LV2",
"HV1",
"LV7",
"HV4",
"HV4",
"HV4",
"HV4",
"LV2",
"HV3",
"HV3",
"LV3",
"LV1",
"HV3",
"HV3",
"LV5",
"HV3",
"HV3",
"LV4",
"LV4",
"LV1",
"LV1",
"LV1",
"LV4",
"HV2",
"LV5",
"HV2",
"WLD",
"HV2",
"HV2",
"LV6",
"LV7",
"LV7",
"LV7",
"LV3",
"LV5",
"LV5",
"LV3",
"LV2",
"LV3",
"HV5",
"LV6",
"HV5",
"HV5",
"HV5",
"HV5",
"HV5"
},
{
"LV5",
"LV3",
"LV5",
"HV1",
"HV1",
"LV4",
"HV1",
"LV3",
"HV1",
"LV6",
"LV6",
"HV1",
"LV7",
"HV3",
"LV1",
"LV5",
"HV3",
"HV3",
"LV5",
"WLD",
"HV3",
"LV6",
"HV5",
"HV5",
"HV5",
"LV6",
"HV5",
"LV3",
"HV4",
"LV2",
"LV4",
"HV4",
"LV1",
"HV4",
"LV4",
"HV4",
"LV1",
"HV2",
"LV3",
"HV2",
"HV2",
"LV7",
"HV2",
"LV7",
"LV7",
"LV2",
"LV2",
"LV2",
"WLD",
"WLD",
"LV4",
"LV1",
"LV4",
"LV6",
"LV2",
"LV3"
},
{
"HV1",
"HV1",
"HV1",
"WLD",
"LV2",
"LV4",
"HV5",
"HV5",
"HV5",
"HV5",
"LV2",
"LV2",
"LV2",
"HV2",
"LV1",
"LV1",
"HV2",
"LV3",
"HV2",
"LV3",
"HV2",
"HV2",
"LV6",
"HV2",
"LV5",
"LV5",
"LV5",
"LV7",
"HV3",
"HV3",
"LV4",
"LV7",
"HV3",
"LV4",
"HV3",
"LV7",
"HV4",
"LV1",
"LV1",
"HV4",
"LV7",
"LV4",
"HV4",
"LV5",
"LV6",
"HV4",
"HV4",
"HV4",
"LV6",
"LV6",
"LV3",
"LV3",
"LV3",
"LV4",
"LV6",
"LV2"
},
{
"HV1",
"X7X",
"LV5",
"HV1",
"HV1",
"HV1",
"LV2",
"LV2",
"LV2",
"LV7",
"LV1",
"LV3",
"LV4",
"LV1",
"HV3",
"HV3",
"LV7",
"HV3",
"LV6",
"HV3",
"LV1",
"HV2",
"LV1",
"HV2",
"HV2",
"LV2",
"LV7",
"HV2",
"HV2",
"LV4",
"WLD",
"LV6",
"LV6",
"WLD",
"LV6",
"LV3",
"HV5",
"HV5",
"LV1",
"HV5",
"LV7",
"LV3",
"HV5",
"LV5",
"LV5",
"TRG",
"LV7",
"WLD",
"HV4",
"LV5",
"HV4",
"LV5",
"HV4",
"LV4",
"LV3",
"HV4",
"HV4",
"LV4"
},
{
"LV7",
"LV7",
"LV7",
"LV2",
"LV3",
"HV1",
"LV1",
"HV1",
"HV1",
"LV7",
"HV1",
"LV3",
"HV2",
"LV3",
"LV2",
"HV2",
"LV1",
"LV2",
"HV2",
"LV6",
"LV5",
"HV2",
"LV6",
"HV4",
"HV4",
"HV4",
"HV4",
"LV1",
"LV4",
"TRG",
"LV6",
"LV6",
"HV5",
"HV5",
"LV3",
"HV5",
"WLD",
"HV5",
"LV4",
"HV5",
"LV4",
"X7X",
"LV2",
"LV4",
"LV1",
"HV3",
"LV1",
"HV3",
"HV3",
"HV3",
"HV3",
"LV5",
"LV5",
"LV5",
"LV7",
"LV7",
"LV1",
"LV5",
"LV5"
}
};

vector<vector<string>> reels3 = { //for third option on every reel
{
"LV2",
"LV2",
"LV7",
"LV7",
"HV1",
"HV1",
"LV3",
"HV1",
"HV1",
"LV4",
"WLD",
"LV2",
"HV4",
"LV6",
"HV4",
"LV2",
"HV4",
"LV5",
"HV4",
"LV4",
"LV4",
"LV4",
"HV3",
"HV3",
"HV3",
"HV3",
"LV3",
"HV3",
"LV1",
"HV3",
"LV1",
"HV2",
"HV2",
"LV3",
"HV2",
"LV6",
"LV6",
"HV2",
"LV6",
"LV5",
"LV5",
"LV7",
"HV5",
"HV5",
"LV3",
"HV5",
"LV1",
"LV1",
"HV5",
"HV5",
"LV5",
"HV5",
"LV7"
},
{
"LV4",
"LV6",
"HV1",
"LV6",
"LV6",
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"WLD",
"LV3",
"LV3",
"LV3",
"HV3",
"HV3",
"LV2",
"LV5",
"HV3",
"HV3",
"LV2",
"LV1",
"HV5",
"LV1",
"HV5",
"LV7",
"HV5",
"HV5",
"LV7",
"HV4",
"LV6",
"HV4",
"LV3",
"HV4",
"LV4",
"HV4",
"LV4",
"WLD",
"LV1",
"LV7",
"WLD",
"LV1",
"HV2",
"HV2",
"HV2",
"HV2",
"LV2",
"LV4",
"LV6",
"LV4",
"LV5",
"LV5",
"LV5",
"LV7",
"LV2",
"LV3"
},
{
"HV1",
"LV7",
"HV1",
"LV4",
"LV7",
"HV1",
"LV4",
"LV1",
"LV5",
"LV5",
"HV5",
"HV5",
"LV6",
"HV5",
"LV6",
"LV6",
"HV5",
"LV3",
"HV2",
"LV1",
"HV2",
"LV6",
"HV2",
"HV2",
"LV2",
"HV2",
"HV2",
"LV4",
"LV1",
"LV1",
"LV4",
"HV3",
"HV3",
"HV3",
"HV3",
"LV7",
"LV7",
"LV5",
"LV5",
"WLD",
"LV2",
"LV2",
"HV4",
"HV4",
"HV4",
"HV4",
"LV2",
"HV4",
"HV4",
"LV3",
"LV3",
"LV3",
"LV3",
"LV2",
"LV4",
"LV6"
},
{
"LV4",
"LV4",
"LV4",
"WLD",
"LV1",
"WLD",
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"HV3",
"HV3",
"HV3",
"WLD",
"LV5",
"HV3",
"LV3",
"TRG",
"LV1",
"HV2",
"LV7",
"LV7",
"HV2",
"HV2",
"HV2",
"LV6",
"HV2",
"LV2",
"LV3",
"LV3",
"LV3",
"HV5",
"LV7",
"HV5",
"LV6",
"HV5",
"LV6",
"HV5",
"LV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV2",
"LV2",
"X7X",
"LV1",
"LV6",
"LV5",
"LV5",
"LV5",
"LV5",
"LV7",
"LV7"
},
{
"LV1",
"HV1",
"HV1",
"HV1",
"LV4",
"HV1",
"LV7",
"WLD",
"HV2",
"LV3",
"HV2",
"LV7",
"HV2",
"HV2",
"LV1",
"LV1",
"X7X",
"LV1",
"LV1",
"LV5",
"LV5",
"LV5",
"LV2",
"LV2",
"LV2",
"LV6",
"LV5",
"LV7",
"LV7",
"LV6",
"LV6",
"LV7",
"HV4",
"HV4",
"LV4",
"LV4",
"HV4",
"LV3",
"LV3",
"HV4",
"LV2",
"HV5",
"LV5",
"HV5",
"HV5",
"HV5",
"LV1",
"HV5",
"LV4",
"HV3",
"LV7",
"LV5",
"HV3",
"LV3",
"HV3",
"LV6",
"TRG",
"HV3",
"HV3"
}
};

vector<vector<string>> reels4 = {
{
"LV1",
"LV3",
"LV3",
"LV3",
"HV1",
"HV1",
"HV1",
"HV1",
"LV7",
"WLD",
"WLD",
"LV4",
"LV4",
"LV5",
"LV7",
"HV4",
"LV1",
"LV4",
"HV4",
"HV4",
"HV4",
"HV4",
"LV6",
"LV6",
"LV6",
"LV3",
"LV2",
"LV2",
"LV2",
"WLD",
"LV6",
"LV7",
"HV3",
"LV1",
"HV3",
"LV6",
"HV3",
"HV3",
"LV5",
"HV3",
"LV5",
"HV2",
"HV2",
"LV7",
"HV2",
"LV3",
"HV2",
"HV2",
"LV5",
"HV5",
"LV1",
"HV5",
"HV5",
"LV2",
"HV5",
"HV5",
"LV4",
"LV4",
"LV2"
},
{
"HV1",
"LV4",
"HV1",
"HV1",
"LV3",
"HV1",
"LV5",
"HV1",
"LV1",
"LV1",
"LV1",
"LV1",
"LV5",
"LV7",
"LV3",
"HV3",
"LV2",
"HV3",
"HV3",
"LV5",
"HV3",
"LV6",
"HV5",
"LV2",
"HV5",
"HV5",
"LV5",
"LV5",
"HV5",
"LV1",
"LV6",
"WLD",
"LV3",
"LV3",
"HV4",
"LV7",
"HV4",
"HV4",
"LV2",
"LV2",
"HV4",
"LV6",
"LV4",
"LV4",
"LV4",
"HV2",
"LV7",
"HV2",
"LV6",
"LV7",
"HV2",
"HV2",
"LV7"
},
{
"HV1",
"LV3",
"LV5",
"HV1",
"HV1",
"LV6",
"HV5",
"LV2",
"HV5",
"LV2",
"HV5",
"HV5",
"LV4",
"LV1",
"HV5",
"LV1",
"LV1",
"WLD",
"LV3",
"LV3",
"HV2",
"HV2",
"HV2",
"HV2",
"LV7",
"LV6",
"HV2",
"LV5",
"HV3",
"LV5",
"HV3",
"LV5",
"LV2",
"HV3",
"HV3",
"HV3",
"LV7",
"LV7",
"LV7",
"LV5",
"LV7",
"LV1",
"LV3",
"LV6",
"WLD",
"LV1",
"LV4",
"WLD",
"LV4",
"LV4",
"HV4",
"LV2",
"HV4",
"HV4",
"HV4",
"HV4",
"LV6"
},
{
"LV5",
"HV1",
"LV4",
"HV1",
"LV2",
"HV1",
"LV4",
"HV1",
"LV7",
"LV6",
"HV3",
"HV3",
"LV3",
"HV3",
"LV6",
"HV3",
"LV1",
"HV3",
"LV1",
"LV1",
"LV5",
"HV2",
"HV2",
"X7X",
"LV3",
"HV2",
"HV2",
"LV3",
"HV5",
"HV5",
"LV5",
"HV5",
"HV5",
"HV5",
"LV2",
"LV5",
"LV2",
"LV4",
"HV4",
"HV4",
"LV6",
"HV4",
"HV4",
"LV4",
"LV1",
"LV3",
"WLD",
"LV7",
"TRG",
"LV7",
"LV7",
"LV2",
"LV2",
"LV3",
"LV4",
"LV6",
"LV6"
},
{
"LV6",
"LV5",
"LV5",
"TRG",
"HV1",
"LV7",
"HV1",
"LV6",
"HV1",
"LV6",
"HV1",
"LV1",
"LV2",
"LV2",
"HV2",
"HV2",
"HV2",
"HV2",
"LV1",
"HV2",
"HV2",
"LV1",
"LV1",
"LV6",
"LV6",
"LV2",
"LV2",
"LV5",
"LV3",
"LV5",
"HV4",
"HV4",
"LV4",
"LV4",
"HV4",
"HV4",
"HV4",
"HV4",
"LV6",
"WLD",
"LV4",
"HV5",
"LV7",
"HV5",
"LV7",
"HV5",
"HV5",
"X7X",
"LV2",
"LV2",
"LV3",
"LV3",
"WLD",
"WLD",
"LV3",
"HV3",
"HV3",
"LV4",
"HV3",
"HV3",
"LV7",
"LV3",
"LV3",
"LV4",
"LV4"
}
};

vector<vector<string>> reels5 = {
{
"LV4",
"HV1",
"LV6",
"LV6",
"HV1",
"HV1",
"LV2",
"LV2",
"HV1",
"LV7",
"HV4",
"HV4",
"LV3",
"HV4",
"HV4",
"HV4",
"LV2",
"HV3",
"HV3",
"LV3",
"LV1",
"HV3",
"HV3",
"HV3",
"LV5",
"WLD",
"LV4",
"WLD",
"LV5",
"LV4",
"LV1",
"LV1",
"LV1",
"HV2",
"LV4",
"HV2",
"LV5",
"HV2",
"WLD",
"HV2",
"LV6",
"HV2",
"LV7",
"LV7",
"LV7",
"LV3",
"LV5",
"LV3",
"LV2",
"LV2",
"LV3",
"LV4",
"HV5",
"LV6",
"LV6",
"HV5",
"HV5",
"HV5",
"HV5"
},
{
"LV5",
"HV1",
"LV3",
"LV5",
"HV1",
"LV4",
"LV3",
"HV1",
"LV6",
"LV6",
"HV1",
"HV1",
"LV7",
"HV3",
"LV1",
"LV5",
"HV3",
"HV3",
"WLD",
"HV3",
"LV6",
"HV5",
"HV5",
"HV5",
"HV5",
"LV6",
"LV3",
"HV4",
"HV4",
"LV2",
"LV4",
"HV4",
"LV1",
"LV4",
"HV4",
"LV1",
"HV2",
"LV3",
"HV2",
"HV2",
"HV2",
"LV7",
"LV7",
"LV7",
"LV7",
"LV2",
"LV2",
"LV2",
"LV4",
"LV1",
"LV1",
"LV5",
"LV5"
},
{
"HV1",
"HV1",
"HV1",
"LV2",
"WLD",
"LV4",
"HV5",
"HV5",
"HV5",
"HV5",
"HV5",
"LV2",
"LV2",
"LV2",
"HV2",
"LV1",
"LV1",
"HV2",
"LV3",
"HV2",
"LV3",
"HV2",
"HV2",
"LV6",
"WLD",
"WLD",
"LV5",
"LV5",
"LV5",
"LV7",
"LV5",
"LV7",
"LV1",
"HV3",
"HV3",
"LV4",
"HV3",
"LV7",
"HV3",
"LV4",
"HV3",
"LV7",
"HV4",
"LV1",
"LV1",
"HV4",
"LV7",
"LV4",
"HV4",
"LV5",
"LV6",
"HV4",
"HV4",
"LV6",
"LV6",
"LV3",
"LV3"
},
{
"HV1",
"LV5",
"HV1",
"HV1",
"HV1",
"LV2",
"LV2",
"LV2",
"HV3",
"LV3",
"LV4",
"HV3",
"LV7",
"HV3",
"LV1",
"LV6",
"HV3",
"HV3",
"LV1",
"HV2",
"LV1",
"HV2",
"HV2",
"LV7",
"HV2",
"LV4",
"WLD",
"LV6",
"LV6",
"LV6",
"LV2",
"LV2",
"LV6",
"X7X",
"LV4",
"LV3",
"LV3",
"HV5",
"HV5",
"LV1",
"HV5",
"HV5",
"LV7",
"HV5",
"LV3",
"LV5",
"TRG",
"LV7",
"HV4",
"LV5",
"LV5",
"HV4",
"LV4",
"LV3",
"HV4",
"HV4",
"LV4"
},
{
"LV7",
"LV7",
"WLD",
"LV7",
"LV2",
"WLD",
"X7X",
"LV3",
"HV1",
"LV1",
"HV1",
"HV1",
"LV7",
"HV1",
"LV3",
"HV2",
"LV3",
"LV2",
"HV2",
"LV1",
"LV2",
"HV2",
"LV6",
"HV2",
"LV5",
"HV2",
"HV2",
"LV6",
"HV4",
"HV4",
"HV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV4",
"LV3",
"LV6",
"LV6",
"HV5",
"HV5",
"TRG",
"LV2",
"HV5",
"WLD",
"HV5",
"LV4",
"LV4",
"LV4",
"LV1",
"HV3",
"HV3",
"HV3",
"HV3",
"LV5",
"LV5",
"LV5",
"LV4",
"LV4",
"LV2",
"LV2",
"LV3",
"LV6",
"LV3",
"LV6"
}
};

vector<vector<string>> reels6 = {
{
"LV2",
"LV2",
"LV7",
"LV7",
"HV1",
"HV1",
"LV3",
"HV1",
"HV1",
"LV4",
"WLD",
"LV1",
"HV4",
"LV2",
"HV4",
"LV6",
"LV2",
"HV4",
"HV4",
"LV5",
"HV4",
"LV4",
"LV4",
"LV4",
"HV3",
"HV3",
"HV3",
"LV3",
"HV3",
"HV3",
"LV1",
"HV2",
"HV2",
"LV3",
"HV2",
"LV6",
"HV2",
"LV6",
"HV2",
"LV5",
"LV5",
"WLD",
"LV6",
"LV5",
"WLD",
"LV7",
"HV5",
"LV7",
"HV5",
"LV4",
"HV5",
"LV1",
"LV1",
"HV5",
"HV5",
"LV6",
"LV2",
"LV3",
"LV3"
},
{
"LV4",
"LV6",
"LV6",
"LV6",
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"HV1",
"LV3",
"LV3",
"LV3",
"HV3",
"HV3",
"LV2",
"LV5",
"HV3",
"HV3",
"LV2",
"LV1",
"HV5",
"LV1",
"HV5",
"LV7",
"HV5",
"HV5",
"LV7",
"HV4",
"LV6",
"HV4",
"LV3",
"HV4",
"HV4",
"LV4",
"LV4",
"LV1",
"LV7",
"LV1",
"WLD",
"LV1",
"HV2",
"HV2",
"HV2",
"LV2",
"LV4",
"HV2",
"LV5",
"LV5",
"LV5",
"LV7",
"LV7",
"LV5"
},
{
"HV1",
"LV7",
"HV1",
"HV1",
"LV4",
"LV7",
"LV4",
"LV1",
"WLD",
"HV5",
"WLD",
"LV5",
"HV5",
"LV5",
"HV5",
"LV6",
"HV5",
"LV6",
"HV5",
"LV3",
"HV2",
"LV6",
"LV1",
"HV2",
"LV6",
"HV2",
"LV2",
"HV2",
"HV2",
"LV4",
"LV1",
"HV3",
"LV1",
"HV3",
"LV4",
"HV3",
"HV3",
"HV3",
"LV7",
"LV7",
"LV5",
"LV5",
"WLD",
"LV2",
"LV2",
"HV4",
"HV4",
"HV4",
"LV2",
"HV4",
"HV4",
"LV3",
"LV3",
"LV3",
"LV1",
"LV7",
"LV5"
},
{
"LV4",
"LV4",
"TRG",
"HV1",
"LV4",
"LV1",
"HV1",
"HV1",
"HV1",
"LV2",
"HV3",
"HV3",
"HV3",
"WLD",
"LV5",
"HV3",
"HV3",
"LV3",
"LV1",
"HV2",
"LV7",
"LV7",
"HV2",
"HV2",
"HV2",
"LV6",
"LV2",
"LV3",
"X7X",
"LV3",
"LV3",
"HV5",
"HV5",
"LV7",
"HV5",
"LV6",
"HV5",
"LV6",
"HV5",
"LV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV1",
"HV4",
"LV2",
"LV2",
"LV2",
"LV6",
"LV5",
"LV5",
"LV5",
"LV7",
"LV3",
"LV4",
"LV6"
},
{
"LV1",
"HV1",
"HV1",
"HV1",
"HV1",
"LV4",
"LV5",
"LV4",
"LV4",
"LV7",
"WLD",
"HV2",
"LV3",
"HV2",
"LV7",
"HV2",
"HV2",
"LV1",
"LV1",
"HV2",
"HV2",
"LV5",
"LV2",
"LV3",
"LV2",
"LV3",
"LV6",
"LV6",
"LV2",
"LV6",
"LV6",
"LV6",
"WLD",
"LV2",
"WLD",
"LV2",
"HV4",
"HV4",
"HV4",
"LV7",
"HV4",
"LV4",
"LV4",
"HV4",
"LV3",
"X7X",
"HV4",
"LV3",
"LV2",
"HV5",
"LV5",
"HV5",
"HV5",
"LV1",
"HV5",
"LV4",
"HV3",
"LV7",
"LV5",
"HV3",
"LV3",
"HV3",
"LV6",
"TRG",
"HV3"
}
};


vector<vector<string>> reels7 = { //for first option on every reel during x7 bonus
{
"LV1",
"LV3",
"LV3",
"LV3",
"HV1",
"HV1",
"HV1",
"LV7",
"HV1",
"HV1",
"LV4",
"LV4",
"LV5",
"LV7",
"HV4",
"LV1",
"LV4",
"HV4",
"HV4",
"LV6",
"HV4",
"HV4",
"LV6",
"LV2",
"LV2",
"LV2",
"WLD",
"LV6",
"LV7",
"HV3",
"LV1",
"HV3",
"LV6",
"HV3",
"HV3",
"LV5",
"HV3",
"HV3",
"HV3",
"LV5",
"LV5",
"LV1",
"LV7",
"HV2",
"HV2",
"HV2",
"HV2",
"LV7",
"LV3",
"HV2",
"LV5",
"HV5",
"LV5",
"HV5",
"HV5",
"LV2",
"HV5",
"LV4",
"HV5",
"LV1",
"HV5",
"HV5",
"LV1",
"LV7"
},
{
"HV1",
"LV4",
"HV1",
"HV1",
"HV1",
"HV1",
"LV3",
"HV1",
"LV5",
"HV1",
"LV1",
"LV1",
"WLD",
"LV1",
"LV3",
"HV3",
"HV3",
"LV2",
"HV3",
"HV3",
"LV5",
"HV3",
"HV3",
"LV6",
"HV5",
"LV2",
"HV5",
"LV5",
"HV5",
"HV5",
"LV5",
"HV5",
"HV5",
"LV1",
"WLD",
"LV6",
"LV3",
"WLD",
"LV3",
"HV4",
"LV7",
"HV4",
"HV4",
"LV2",
"HV4",
"LV2",
"LV2",
"HV4",
"HV4",
"LV4",
"LV4",
"LV4",
"LV4",
"LV6",
"LV3",
"HV2",
"LV7",
"LV6",
"HV2",
"HV2",
"HV2",
"LV6",
"HV2",
"LV7",
"HV2",
"LV7"
},
{
"HV1",
"LV3",
"HV1",
"HV1",
"LV5",
"HV1",
"LV6",
"HV5",
"LV2",
"HV5",
"LV2",
"HV5",
"LV4",
"LV3",
"HV5",
"LV4",
"HV5",
"LV3",
"LV4",
"LV6",
"WLD",
"LV1",
"LV1",
"LV1",
"WLD",
"HV2",
"LV3",
"LV3",
"HV2",
"HV2",
"HV2",
"LV7",
"LV6",
"HV2",
"HV2",
"HV2",
"LV5",
"HV3",
"LV5",
"HV3",
"LV5",
"LV2",
"HV3",
"LV7",
"LV7",
"HV3",
"HV3",
"LV7",
"LV1",
"LV4",
"LV4",
"LV4",
"LV6",
"LV6",
"HV4",
"HV4",
"LV2",
"LV2",
"HV4",
"LV2",
"HV4",
"HV4",
"HV4",
"LV6",
"HV4",
"LV3"
},
{
"LV5",
"HV1",
"LV4",
"HV1",
"LV2",
"HV1",
"HV1",
"LV4",
"HV1",
"LV7",
"HV1",
"HV1",
"LV7",
"LV1",
"LV5",
"HV3",
"LV6",
"HV3",
"HV3",
"HV3",
"HV3",
"LV3",
"HV3",
"WLD",
"HV3",
"LV6",
"LV1",
"LV1",
"WLD",
"LV1",
"HV2",
"HV2",
"HV2",
"LV5",
"HV2",
"HV2",
"LV3",
"HV2",
"HV2",
"HV2",
"LV3",
"HV5",
"HV5",
"LV5",
"HV5",
"HV5",
"HV5",
"LV2",
"HV5",
"HV5",
"LV5",
"LV2",
"LV4",
"HV4",
"HV4",
"LV6",
"HV4",
"HV4",
"LV4",
"HV4",
"LV1",
"HV4",
"LV3",
"HV4",
"HV4",
"LV7",
"LV7",
"WLD",
"LV7",
"LV2",
"LV6"
},
{
"LV6",
"LV5",
"LV5",
"HV1",
"LV7",
"HV1",
"HV1",
"LV6",
"LV6",
"HV1",
"LV1",
"HV1",
"HV1",
"LV2",
"LV2",
"HV2",
"HV2",
"HV2",
"HV2",
"LV1",
"LV1",
"HV2",
"HV2",
"LV1",
"LV5",
"LV4",
"HV4",
"HV4",
"LV4",
"HV4",
"LV3",
"HV4",
"HV4",
"LV5",
"HV4",
"LV6",
"WLD",
"LV4",
"HV5",
"HV5",
"LV7",
"HV5",
"HV5",
"HV5",
"LV2",
"LV2",
"HV5",
"HV5",
"LV3",
"LV3",
"HV3",
"LV3",
"HV3",
"LV4",
"HV3",
"HV3",
"LV7",
"HV3",
"LV7",
"HV3",
"HV3",
"LV7",
"LV1",
"LV5"
}
};

vector<vector<string>> reels8 = {
{
"LV4",
"HV1",
"LV6",
"LV6",
"HV1",
"HV1",
"HV1",
"LV2",
"LV2",
"HV1",
"LV7",
"HV4",
"HV4",
"HV4",
"HV4",
"LV3",
"HV4",
"LV2",
"HV3",
"HV3",
"LV3",
"LV1",
"HV3",
"HV3",
"LV5",
"HV3",
"LV4",
"LV5",
"HV3",
"HV3",
"LV4",
"LV1",
"LV1",
"LV1",
"LV1",
"LV4",
"HV2",
"LV5",
"HV2",
"LV7",
"HV2",
"LV5",
"HV2",
"WLD",
"HV2",
"LV6",
"LV7",
"LV7",
"LV7",
"LV7",
"LV3",
"LV5",
"LV5",
"LV3",
"LV2",
"LV1",
"HV5",
"LV6",
"HV5",
"HV5",
"HV5",
"HV5",
"HV5",
"HV5"
},
{
"LV5",
"HV1",
"LV3",
"LV5",
"HV1",
"HV1",
"HV1",
"LV4",
"HV1",
"LV3",
"HV1",
"LV6",
"LV6",
"HV1",
"LV7",
"HV3",
"LV1",
"LV5",
"HV3",
"HV3",
"HV3",
"HV3",
"LV5",
"HV3",
"LV6",
"HV5",
"HV5",
"HV5",
"LV6",
"HV5",
"HV5",
"HV5",
"WLD",
"LV3",
"HV4",
"LV2",
"LV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV4",
"HV4",
"HV4",
"LV1",
"HV2",
"LV3",
"HV2",
"HV2",
"LV7",
"LV7",
"HV2",
"LV7",
"HV2",
"HV2",
"LV2",
"LV2",
"LV2",
"WLD",
"LV4",
"LV1",
"LV4",
"LV6",
"WLD",
"LV2",
"LV3"
},
{
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"WLD",
"LV4",
"HV5",
"HV5",
"HV5",
"LV2",
"LV2",
"HV5",
"HV5",
"LV2",
"LV2",
"LV3",
"LV4",
"LV6",
"HV2",
"LV1",
"LV1",
"HV2",
"LV3",
"HV2",
"LV3",
"HV2",
"HV2",
"LV6",
"HV2",
"HV2",
"LV5",
"LV5",
"LV5",
"HV3",
"LV7",
"HV3",
"HV3",
"LV4",
"LV7",
"HV3",
"LV4",
"HV3",
"LV7",
"HV4",
"LV1",
"LV1",
"HV4",
"LV7",
"LV4",
"HV4",
"LV5",
"HV4",
"HV4",
"LV6",
"HV4",
"HV4",
"LV6",
"LV6",
"WLD",
"LV3",
"LV3",
"LV3",
"LV4",
"LV6",
"LV2"
},
{
"HV1",
"LV5",
"HV1",
"HV1",
"HV1",
"LV2",
"LV2",
"HV1",
"HV1",
"HV1",
"LV2",
"LV7",
"HV3",
"HV3",
"LV1",
"HV3",
"HV3",
"LV3",
"LV4",
"HV3",
"LV7",
"HV3",
"LV1",
"LV6",
"HV3",
"LV1",
"HV2",
"HV2",
"HV2",
"LV1",
"HV2",
"HV2",
"LV2",
"LV7",
"HV2",
"HV2",
"HV2",
"LV4",
"WLD",
"LV6",
"LV6",
"WLD",
"LV6",
"LV3",
"HV5",
"HV5",
"LV1",
"WLD",
"HV5",
"LV7",
"LV3",
"HV5",
"HV5",
"HV5",
"LV5",
"LV5",
"HV5",
"LV7",
"HV4",
"HV4",
"LV5",
"HV4",
"LV5",
"HV4",
"LV4",
"LV3",
"HV4",
"HV4",
"HV4",
"HV4",
"LV4"
},
{
"LV7",
"LV7",
"LV7",
"HV1",
"HV1",
"LV2",
"LV3",
"HV1",
"LV1",
"HV1",
"HV1",
"LV7",
"HV1",
"LV3",
"HV2",
"LV3",
"HV2",
"HV2",
"LV2",
"HV2",
"LV1",
"LV2",
"HV2",
"LV6",
"LV5",
"HV2",
"LV6",
"HV4",
"HV4",
"HV4",
"HV4",
"LV1",
"LV4",
"HV4",
"HV4",
"LV6",
"LV6",
"HV5",
"HV5",
"LV3",
"LV2",
"HV5",
"WLD",
"HV5",
"LV4",
"HV5",
"LV4",
"HV5",
"HV5",
"LV4",
"LV1",
"HV3",
"LV1",
"HV3",
"HV3",
"HV3",
"HV3",
"LV5",
"LV5",
"HV3",
"HV3",
"LV5",
"LV7",
"LV5"
}
};

vector<vector<string>> reels9 = {
{
"LV2",
"LV2",
"LV7",
"HV1",
"LV7",
"HV1",
"HV1",
"LV3",
"HV1",
"HV1",
"LV4",
"WLD",
"LV1",
"HV4",
"HV4",
"LV1",
"LV2",
"HV4",
"LV6",
"LV2",
"HV4",
"LV5",
"HV4",
"LV4",
"LV4",
"HV3",
"HV3",
"LV4",
"HV3",
"HV3",
"HV3",
"LV3",
"HV3",
"LV1",
"HV3",
"LV1",
"HV2",
"HV2",
"LV3",
"HV2",
"LV6",
"LV6",
"HV2",
"HV2",
"LV6",
"LV5",
"LV5",
"LV5",
"LV5",
"LV7",
"LV7",
"HV5",
"LV7",
"HV5",
"LV3",
"HV5",
"LV1",
"LV1",
"HV5",
"HV5",
"HV5",
"HV5",
"LV5",
"LV7"
},
{
"LV4",
"LV6",
"HV1",
"HV1",
"LV6",
"LV6",
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"HV1",
"LV3",
"LV3",
"HV3",
"LV3",
"HV3",
"HV3",
"HV3",
"LV2",
"LV5",
"HV3",
"HV3",
"LV2",
"LV1",
"HV5",
"HV5",
"LV1",
"HV5",
"HV5",
"LV7",
"HV5",
"HV5",
"LV7",
"HV4",
"HV4",
"LV6",
"HV4",
"LV4",
"HV4",
"HV4",
"LV4",
"HV4",
"WLD",
"LV3",
"LV1",
"LV7",
"WLD",
"LV1",
"HV2",
"HV2",
"HV2",
"LV2",
"HV2",
"LV4",
"LV6",
"HV2",
"HV2",
"LV4",
"LV5",
"LV5",
"LV5",
"WLD",
"LV7",
"LV2",
"LV3"
},
{
"HV1",
"LV7",
"HV1",
"LV4",
"HV1",
"LV7",
"LV4",
"HV1",
"LV1",
"LV5",
"HV5",
"HV5",
"LV5",
"HV5",
"LV6",
"HV5",
"LV6",
"LV6",
"HV5",
"LV3",
"HV2",
"LV1",
"HV2",
"LV6",
"HV2",
"HV2",
"LV2",
"HV2",
"LV4",
"HV2",
"HV2",
"LV4",
"LV1",
"WLD",
"HV3",
"HV3",
"LV1",
"LV4",
"HV3",
"HV3",
"HV3",
"LV7",
"LV7",
"LV5",
"LV5",
"WLD",
"LV2",
"LV2",
"HV4",
"HV4",
"HV4",
"LV2",
"HV4",
"HV4",
"LV3",
"LV3",
"HV4",
"LV3",
"HV4",
"LV3",
"LV2",
"LV4",
"LV6",
"LV6",
"LV2",
"LV3"
},
{
"LV4",
"WLD",
"LV4",
"LV4",
"HV1",
"WLD",
"HV1",
"HV1",
"LV1",
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"HV3",
"HV3",
"HV3",
"HV3",
"LV5",
"HV3",
"LV3",
"HV3",
"HV3",
"LV1",
"HV2",
"LV7",
"LV7",
"HV2",
"HV2",
"HV2",
"LV6",
"HV2",
"LV2",
"HV2",
"LV3",
"HV2",
"HV2",
"LV3",
"LV3",
"HV5",
"HV5",
"LV7",
"HV5",
"LV6",
"HV5",
"HV5",
"HV5",
"LV6",
"HV5",
"LV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV2",
"HV4",
"LV2",
"HV4",
"HV4",
"LV1",
"LV6",
"LV5",
"LV5",
"LV5",
"LV5",
"WLD",
"LV7",
"LV7"
},
{
"LV1",
"HV1",
"HV1",
"HV1",
"LV4",
"HV1",
"HV1",
"HV1",
"LV7",
"WLD",
"HV2",
"LV3",
"HV2",
"LV7",
"HV2",
"HV2",
"LV1",
"LV1",
"HV2",
"HV2",
"LV1",
"LV5",
"LV5",
"LV5",
"LV2",
"LV2",
"LV2",
"LV6",
"LV7",
"HV4",
"HV4",
"LV6",
"LV6",
"HV4",
"LV7",
"HV4",
"LV4",
"LV4",
"HV4",
"LV3",
"LV3",
"HV4",
"LV2",
"HV5",
"LV5",
"HV5",
"HV5",
"HV5",
"LV1",
"HV5",
"HV5",
"HV5",
"LV4",
"HV3",
"LV7",
"LV5",
"HV3",
"LV3",
"HV3",
"LV6",
"HV3",
"HV3",
"HV3",
"HV3"
}
};

vector<vector<string>> reels10 = {
{
"LV1",
"LV3",
"HV1",
"LV3",
"HV1",
"HV1",
"LV3",
"HV1",
"HV1",
"HV1",
"LV7",
"WLD",
"LV7",
"LV4",
"LV4",
"LV5",
"WLD",
"HV4",
"HV4",
"LV1",
"LV4",
"HV4",
"HV4",
"HV4",
"LV6",
"LV6",
"HV4",
"HV4",
"LV6",
"LV3",
"LV2",
"LV2",
"LV2",
"HV3",
"HV3",
"HV3",
"LV6",
"LV7",
"HV3",
"LV1",
"HV3",
"LV6",
"HV3",
"HV3",
"LV5",
"HV2",
"LV5",
"HV2",
"HV2",
"HV2",
"LV7",
"HV2",
"LV3",
"HV2",
"HV2",
"LV5",
"HV5",
"LV1",
"HV5",
"HV5",
"LV2",
"HV5",
"HV5",
"HV5",
"HV5",
"WLD",
"LV4",
"LV4",
"LV2"
},
{
"HV1",
"LV4",
"HV1",
"HV1",
"LV3",
"HV1",
"LV5",
"LV1",
"HV1",
"HV1",
"LV1",
"LV1",
"LV1",
"LV5",
"LV1",
"LV7",
"LV5",
"LV7",
"HV3",
"HV3",
"LV3",
"LV2",
"HV3",
"HV3",
"LV5",
"HV3",
"LV6",
"HV5",
"LV2",
"HV5",
"LV5",
"HV5",
"HV5",
"LV5",
"HV5",
"LV1",
"LV6",
"WLD",
"LV3",
"LV3",
"HV4",
"LV7",
"HV4",
"HV4",
"LV2",
"LV2",
"HV4",
"HV4",
"LV6",
"LV4",
"LV4",
"LV4",
"HV2",
"LV7",
"HV2",
"LV6",
"HV2",
"HV2",
"LV7",
"HV2",
"LV7"
},
{
"HV1",
"HV1",
"HV1",
"LV3",
"LV5",
"HV1",
"HV1",
"LV6",
"HV5",
"LV2",
"HV5",
"LV2",
"HV5",
"LV4",
"LV1",
"HV5",
"HV5",
"LV1",
"LV1",
"HV5",
"HV5",
"LV1",
"LV7",
"LV5",
"LV3",
"LV3",
"HV2",
"HV2",
"HV2",
"HV2",
"LV7",
"HV2",
"HV2",
"LV6",
"HV2",
"LV5",
"HV3",
"LV5",
"HV3",
"LV5",
"LV2",
"HV3",
"HV3",
"HV3",
"LV7",
"HV3",
"LV7",
"HV3",
"LV7",
"LV5",
"LV7",
"WLD",
"LV1",
"LV3",
"WLD",
"LV6",
"LV1",
"LV4",
"LV4",
"HV4",
"HV4",
"WLD",
"LV4",
"HV4",
"HV4",
"LV2",
"HV4",
"HV4",
"HV4",
"LV6"
},
{
"LV5",
"HV1",
"LV4",
"HV1",
"LV2",
"HV1",
"LV4",
"HV1",
"HV1",
"HV1",
"LV7",
"LV6",
"HV3",
"HV3",
"LV3",
"HV3",
"LV6",
"HV3",
"LV1",
"HV3",
"HV3",
"HV3",
"LV1",
"LV1",
"HV2",
"HV2",
"LV5",
"HV2",
"HV2",
"LV3",
"HV2",
"HV2",
"LV3",
"HV5",
"HV5",
"LV5",
"HV5",
"HV5",
"HV5",
"WLD",
"LV2",
"HV5",
"HV5",
"LV5",
"LV2",
"LV4",
"LV6",
"HV4",
"HV4",
"HV4",
"HV4",
"LV4",
"HV4",
"HV4",
"LV1",
"LV3",
"LV7",
"LV7",
"LV7",
"LV2",
"LV2",
"LV3",
"LV4",
"LV6",
"LV6"
},
{
"LV6",
"HV1",
"HV1",
"LV5",
"LV5",
"HV1",
"HV1",
"LV7",
"HV1",
"LV6",
"HV1",
"LV6",
"HV1",
"LV1",
"LV2",
"LV2",
"HV2",
"HV2",
"HV2",
"HV2",
"LV1",
"HV2",
"HV2",
"HV2",
"HV2",
"HV2",
"LV1",
"LV1",
"LV6",
"LV6",
"WLD",
"LV2",
"LV2",
"LV5",
"HV4",
"HV4",
"LV4",
"HV4",
"HV4",
"LV4",
"HV4",
"HV4",
"LV3",
"HV4",
"HV4",
"LV5",
"HV4",
"LV6",
"HV5",
"LV4",
"LV7",
"HV5",
"LV7",
"HV5",
"HV5",
"HV5",
"LV2",
"HV5",
"LV2",
"LV3",
"HV5",
"LV3",
"WLD",
"LV4",
"LV3",
"HV3",
"HV3",
"WLD",
"HV3",
"HV3",
"LV7",
"HV3",
"LV3",
"LV3",
"HV3",
"HV3",
"LV4",
"LV4"
}
};

vector<vector<string>> reels11 = {
{
"LV4",
"HV1",
"HV1",
"LV6",
"HV1",
"HV1",
"LV6",
"HV1",
"LV2",
"LV2",
"HV1",
"LV7",
"HV4",
"HV4",
"HV4",
"LV3",
"HV4",
"HV4",
"HV4",
"HV4",
"LV2",
"HV3",
"HV3",
"LV3",
"LV1",
"HV3",
"HV3",
"HV3",
"LV5",
"HV3",
"HV3",
"WLD",
"LV4",
"LV5",
"LV4",
"LV1",
"LV1",
"WLD",
"LV1",
"LV4",
"LV6",
"LV5",
"HV2",
"HV2",
"HV2",
"HV2",
"HV2",
"LV7",
"HV2",
"HV2",
"LV7",
"LV7",
"LV3",
"WLD",
"LV5",
"LV3",
"LV2",
"LV2",
"HV5",
"HV5",
"LV3",
"LV4",
"HV5",
"LV6",
"LV6",
"HV5",
"HV5",
"HV5",
"HV5"
},
{
"LV5",
"HV1",
"LV3",
"LV5",
"HV1",
"LV4",
"HV1",
"HV1",
"LV3",
"HV1",
"LV6",
"LV6",
"HV1",
"LV7",
"HV3",
"HV3",
"HV3",
"LV1",
"LV5",
"HV3",
"LV5",
"WLD",
"HV3",
"LV6",
"HV5",
"HV5",
"HV5",
"HV5",
"HV5",
"LV6",
"LV3",
"HV4",
"LV2",
"HV4",
"HV4",
"LV4",
"HV4",
"LV1",
"LV4",
"HV4",
"LV1",
"HV2",
"LV3",
"HV2",
"HV2",
"LV7",
"LV7",
"HV2",
"HV2",
"LV7",
"LV7",
"LV2",
"LV2",
"LV2",
"LV4",
"LV1",
"LV1",
"LV1",
"LV5",
"LV5",
"LV7"
},
{
"HV1",
"HV1",
"HV1",
"LV2",
"HV1",
"HV1",
"LV4",
"HV5",
"HV5",
"HV5",
"HV5",
"HV5",
"HV5",
"LV2",
"LV2",
"HV5",
"LV2",
"LV1",
"LV1",
"HV2",
"HV2",
"LV1",
"WLD",
"HV2",
"LV3",
"HV2",
"HV2",
"LV3",
"HV2",
"HV2",
"WLD",
"LV6",
"LV5",
"WLD",
"LV5",
"LV5",
"LV7",
"LV5",
"LV5",
"LV7",
"LV7",
"LV1",
"HV3",
"HV3",
"HV3",
"HV3",
"LV4",
"HV3",
"LV7",
"HV3",
"LV4",
"HV3",
"LV7",
"HV4",
"LV1",
"LV1",
"HV4",
"LV7",
"LV4",
"HV4",
"LV5",
"LV6",
"HV4",
"HV4",
"LV6",
"HV4",
"HV4",
"LV6",
"LV3",
"LV3"
},
{
"HV1",
"LV5",
"HV1",
"HV1",
"HV1",
"LV2",
"HV1",
"LV2",
"HV1",
"LV2",
"HV3",
"HV3",
"HV3",
"LV3",
"LV4",
"HV3",
"LV7",
"HV3",
"LV1",
"LV6",
"HV3",
"HV3",
"LV1",
"HV2",
"LV1",
"HV2",
"HV2",
"LV2",
"LV7",
"HV2",
"LV4",
"HV2",
"HV2",
"LV6",
"LV6",
"LV6",
"LV2",
"WLD",
"LV6",
"LV4",
"LV3",
"LV3",
"HV5",
"HV5",
"LV1",
"HV5",
"HV5",
"LV7",
"LV3",
"HV5",
"HV5",
"HV5",
"LV5",
"LV7",
"HV4",
"LV5",
"HV4",
"LV5",
"HV4",
"LV4",
"HV4",
"LV3",
"HV4",
"HV4",
"LV4"
},
{
"LV7",
"LV7",
"WLD",
"LV7",
"LV2",
"WLD",
"LV3",
"HV1",
"HV1",
"HV1",
"LV1",
"HV1",
"HV1",
"LV7",
"HV1",
"HV1",
"LV3",
"HV2",
"HV2",
"HV2",
"LV3",
"LV2",
"HV2",
"LV1",
"HV2",
"LV2",
"HV2",
"LV6",
"HV2",
"LV5",
"HV2",
"HV2",
"LV6",
"HV4",
"HV4",
"HV4",
"HV4",
"LV1",
"HV4",
"HV4",
"HV4",
"HV4",
"LV4",
"LV3",
"HV4",
"LV6",
"LV6",
"WLD",
"HV5",
"HV5",
"LV2",
"HV5",
"HV5",
"LV4",
"HV5",
"HV5",
"HV5",
"LV4",
"LV4",
"LV1",
"HV3",
"HV3",
"HV3",
"HV3",
"HV3",
"HV3",
"LV5",
"HV3",
"LV5",
"LV5",
"LV4",
"LV4",
"LV2",
"LV2",
"LV3",
"LV6",
"LV3",
"LV6"
}
};

vector<vector<string>> reels12 = {
{
"LV2",
"WLD",
"LV2",
"HV1",
"HV1",
"HV1",
"LV7",
"LV7",
"HV1",
"LV3",
"HV1",
"HV1",
"LV4",
"LV1",
"HV4",
"HV4",
"LV2",
"HV4",
"LV6",
"LV2",
"HV4",
"HV4",
"HV4",
"LV5",
"HV4",
"LV4",
"HV3",
"HV3",
"LV4",
"HV3",
"LV4",
"HV3",
"HV3",
"HV3",
"LV3",
"HV3",
"LV1",
"HV2",
"HV2",
"LV3",
"HV2",
"LV6",
"HV2",
"HV2",
"LV6",
"HV2",
"LV5",
"HV2",
"LV5",
"WLD",
"LV6",
"LV5",
"WLD",
"LV7",
"HV5",
"LV7",
"HV5",
"LV4",
"HV5",
"LV1",
"HV5",
"HV5",
"LV1",
"HV5",
"LV6",
"HV5",
"LV2",
"LV3",
"LV3"
},
{
"LV4",
"LV6",
"HV1",
"HV1",
"LV6",
"LV6",
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"LV3",
"HV3",
"LV3",
"HV3",
"LV3",
"HV3",
"LV2",
"LV5",
"HV3",
"HV3",
"LV2",
"LV1",
"HV5",
"HV5",
"HV5",
"LV1",
"LV7",
"HV5",
"HV5",
"LV7",
"HV4",
"LV6",
"HV4",
"LV3",
"HV4",
"LV4",
"LV4",
"HV4",
"HV4",
"LV1",
"LV1",
"LV7",
"LV1",
"WLD",
"LV1",
"HV2",
"HV2",
"HV2",
"LV2",
"LV4",
"HV2",
"LV5",
"HV2",
"LV5",
"LV5",
"LV7",
"LV7",
"LV7",
"LV5",
"LV5"
},
{
"HV1",
"LV7",
"HV1",
"HV1",
"LV4",
"LV7",
"HV1",
"LV4",
"HV1",
"LV1",
"WLD",
"LV5",
"HV5",
"WLD",
"LV5",
"HV5",
"HV5",
"HV5",
"LV6",
"HV5",
"HV5",
"HV5",
"LV6",
"HV2",
"LV3",
"HV2",
"LV6",
"LV1",
"HV2",
"HV2",
"HV2",
"LV6",
"HV2",
"LV2",
"HV2",
"LV4",
"LV1",
"LV1",
"HV3",
"HV3",
"HV3",
"LV4",
"HV3",
"HV3",
"HV3",
"LV7",
"LV7",
"HV3",
"LV5",
"LV5",
"WLD",
"LV2",
"LV2",
"HV4",
"HV4",
"HV4",
"LV2",
"HV4",
"HV4",
"LV3",
"HV4",
"HV4",
"LV3",
"LV3",
"LV1",
"LV7",
"LV5",
"LV5",
"LV7",
"LV1"
},
{
"LV4",
"LV4",
"HV1",
"LV4",
"LV1",
"HV1",
"HV1",
"HV1",
"HV1",
"HV1",
"LV2",
"HV3",
"HV3",
"HV3",
"LV5",
"HV3",
"HV3",
"HV3",
"HV3",
"LV3",
"LV1",
"HV2",
"LV7",
"HV2",
"LV7",
"HV2",
"HV2",
"HV2",
"LV6",
"HV2",
"LV2",
"WLD",
"LV3",
"HV5",
"LV3",
"HV5",
"LV3",
"HV5",
"LV7",
"HV5",
"HV5",
"LV6",
"HV5",
"LV6",
"HV5",
"LV4",
"HV4",
"LV1",
"HV4",
"HV4",
"LV1",
"HV4",
"LV2",
"LV2",
"HV4",
"LV2",
"HV4",
"LV6",
"LV5",
"LV5",
"LV5",
"LV7",
"LV3",
"LV4",
"LV6"
},
{
"LV1",
"HV1",
"HV1",
"HV1",
"HV1",
"LV4",
"HV1",
"LV5",
"HV1",
"LV4",
"HV1",
"LV4",
"WLD",
"LV7",
"HV2",
"LV3",
"HV2",
"LV7",
"HV2",
"HV2",
"LV1",
"LV1",
"HV2",
"HV2",
"LV5",
"HV2",
"HV2",
"LV2",
"HV2",
"LV3",
"LV2",
"WLD",
"LV3",
"LV6",
"LV6",
"LV2",
"LV2",
"WLD",
"LV2",
"HV4",
"LV6",
"HV4",
"LV6",
"LV6",
"HV4",
"LV7",
"HV4",
"LV4",
"LV4",
"HV4",
"HV4",
"HV4",
"HV4",
"LV3",
"LV3",
"HV4",
"LV2",
"HV5",
"LV5",
"HV5",
"HV5",
"HV5",
"HV5",
"LV1",
"HV5",
"HV5",
"LV4",
"HV3",
"HV3",
"LV7",
"HV3",
"LV5",
"HV3",
"LV3",
"HV3",
"LV6",
"HV3",
"HV3"
}
};


vector<vector<string>> reelsfree1 = { //first FG reels
{
"HV1",
"0",
"0",
"LV5",
"0",
"HV3",
"0",
"LV2",
"0",
"LV7",
"0",
"HV4",
"0",
"LV3",
"0",
"HV5",
"0",
"0",
"0",
"LV6",
"0",
"HV2",
"0",
"LV4",
"0",
"LV1",
"0"
},
{
"LV2",
"0",
"HV5",
"0",
"LV4",
"0",
"0",
"0",
"HV3",
"0",
"LV3",
"0",
"HV2",
"0",
"LV5",
"0",
"HV4",
"0",
"0",
"LV6",
"0",
"HV1",
"0",
"LV7",
"0",
"LV1",
"0"
},
{
"HV1",
"0",
"LV5",
"0",
"HV4",
"0",
"LV2",
"0",
"0",
"LV7",
"0",
"HV3",
"0",
"LV4",
"0",
"HV5",
"0",
"LV6",
"0",
"0",
"0",
"HV2",
"0",
"LV3",
"0",
"LV1",
"0"
},
{
"0",
"WLD",
"0",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"WLD",
"0",
"0"
}, // #0: 19, #WLD: 6
{
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"0",
"0",
"0"
} // #0: 42, #WLD: 9
};

vector<vector<string>> reelsfree2 = { //second FG reels
{
"HV1",
"0",
"LV5",
"0",
"HV2",
"0",
"LV6",
"0",
"LV7",
"0",
"HV3",
"0",
"LV4",
"0",
"HV5",
"0",
"LV3",
"0",
"0",
"HV4",
"0",
"0",
"LV1",
"0",
"LV2",
"0",
"0"
},
{
"LV6",
"0",
"HV5",
"0",
"0",
"LV4",
"0",
"0",
"HV3",
"0",
"LV5",
"0",
"HV4",
"0",
"LV2",
"0",
"HV2",
"0",
"0",
"LV3",
"0",
"HV1",
"0",
"LV7",
"0",
"LV1",
"0"
},
{
"HV1",
"0",
"0",
"LV5",
"0",
"HV3",
"0",
"LV6",
"0",
"LV7",
"0",
"HV2",
"0",
"LV2",
"0",
"HV5",
"0",
"0",
"0",
"LV3",
"0",
"HV4",
"0",
"LV4",
"0",
"LV1",
"0"
},
{
"0",
"WLD",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"WLD",
"0",
"0"
}, // #0: 19, #WLD: 6
{
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"WLD",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"WLD",
"0",
"0",
"0",
"0",
"0",
"0",
"0"
} // #0: 42, #WLD: 9
};


void info(){ // customizable info sheet for the current game version
    cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl;
    cout <<  " _______                                         " << endl;
    cout <<  " \\___ O \\                                      " << endl;
    cout <<  "  Vvw)   \\___                                   " << endl;
    cout <<  "    \\       _\\                                 " << endl;
    cout <<  "    /   ))) \\────────────────────────────────────────┐" << endl;
    cout <<  "   /__                                               │" << endl;
    cout <<  "    │  this game is played with all 178 connected    │" << endl;
    cout <<  "    │  winning lines from left to right, except for  │" << endl;
    cout <<  "    │  the Mega Reels which use 421 lines instead.   │" << endl;
    cout <<  "    │                                                │" << endl;
    cout <<  "    │  there are 2 features each triggered by two    │" << endl;
    cout <<  "    │    identical trigger symbols on reels 4 and 5  │" << endl;
    cout <<  "    │                                                │" << endl;
    cout <<  "    │   with each feature entry the player selects   │" << endl;
    cout <<  "    │ one of 3 modes to choose the volatility of the │" << endl;
    cout <<  "    │  next game part individually on each occasion  │" << endl;
    cout <<  "    │                                                │" << endl;
    cout <<  "    │ pressing and holding SPACE or DELETE on mobile │" << endl;
    cout <<  "    │ devices yields quick spin mode (~25 spins/sec) │" << endl;
    cout <<  "    │                                                │" << endl;
    cout <<  "    │  before quick spins set reel spinning to [OFF] │" << endl;
    cout <<  "    └────────────────────────────────────────────────┘" << endl;

    cout << endl << endl<<endl<< "          press SPACE to continue"<< endl;
    if (simple) {cout << endl;} // this is never called in !test_mode anyways
    while (true) {
            char key = readFirstCharacter();
            if (key == '*') { cheat = !cheat; }
            if (key == '#') { exit(0); }
            else { break; }
    }
    if (simple) {cout << endl << endl << endl;} // ditto
    cout << endl<< endl<< endl<< endl<<endl<<endl << endl<< endl<< endl<< endl<<endl<<endl;
}

void controls(){
    cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl;
    cout << " "<< invertUI <<" H A N D B O O K (1) :  P L A Y I N G  T H E  G A M E "<< currentUI << endl;
    cout << "                                                        " << endl;
    cout << " To start playing slots with the current settings press " << endl;
    cout << " SPACE or any otherwise unused key. To play test faster " << endl;
    cout << " the duration between single images during reel spins   " << endl;
    cout << " can be increased or even set to zero by deactivating   " << endl;
	cout << " the spin entirely. When the reel spin is set to [OFF]  " << endl;
    cout << " instead of individually pressing it SPACE or other     " << endl;
    cout << " keys can be held down to speed up the casino visit     " << endl;
    cout << " drastically. Inpependantly of spin settings loan shark " << endl;
    cout << " mode allows the player to start without credits and    " << endl;
    cout << " accumulate debts instead. If set to [ON] spin mods de- " << endl;
    cout << " tect near win events and slow down the last reel.      " << endl;
    cout << "                                                        " << endl;
    cout << " In order just to gamble the most important keys are:   " << endl;
    cout << "                                                        " << endl;
    cout << " SPACE                                                  " << endl;
    cout << "   continue the game (unless stated otherwise)          " << endl;
    cout << " 'c'                                                    " << endl;
    cout << "   continue to next game event, required as a break     " << endl;
    cout << "   point to avoid missing important events              " << endl;
    cout << " 'n' / 'r' / 's'                                        " << endl;
    cout << "   select between feature modes with varying volatility " << endl;
    cout << " 'b' / 'd'                                              " << endl;
    cout << "   in-/decrease the current bet cyclically              " << endl;
    cout << " 'q'                                                    " << endl;
    cout << "   quit directly to the main menu (outside features)    " << endl;
    cout << " '#'                                                    " << endl;
    cout << "   BE CAREFUL - ends the entire program immediately     " << endl;
    cout << "                                                        " << endl;
    cout << "         press SPACE to go to the next page" << endl;
    if (simple) {cout << endl;}
    char mode = readFirstCharacter();
    if (mode == '*') { cheat = !cheat; }
    if (mode == 'q') return;
        cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl;
    cout << " "<< invertUI <<" H A N D B O O K (2)  :  S  I  M  U  L  A  T  I  N  G "<< currentUI << endl;
    cout << "                                                        " << endl;
    cout << " Pressing '0' starts simulation mode with the current   " << endl;
    cout << " simulation settings (bottom block in the main menu).   " << endl;
    cout << " As a preventive meassure against information loss the  " << endl;
	cout << " full RtP distribution and win group stats are always   " << endl;
    cout << " printed at the end of any simulation of at least 10e8  " << endl;
    cout << " games.                                                 " << endl;
    cout << "                                                        " << endl;
    cout << " At this point the reader is invited to experiment to   " << endl;
    cout << " find out more details...                               " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
	cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "                                                        " << endl;
    cout << "         press SPACE to go back to the main menu" << endl;

    if (simple) {cout << endl;}
    mode = readFirstCharacter();
    if (mode == '*') { cheat = !cheat; }

    if (simple) {cout << endl << endl << endl;} // these aren't called in !test_mode either
}

void stats(){ // summary of the game stats
    cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl
    << endl<< endl<< endl;
    cout << " "<< invertUI <<" S T A T I S T I C S  :  C A R D  S H A R K  M E G A "<< currentUI << endl << endl;
    cout << " return to player WITHOUT features:              62.75%" << endl;
    cout << " Shark Tank RtP:                 (avg ~ 48 bets) 17.13%" << endl;
    cout << " Mega Reels RtP:                 (avg ~ 48 bets) 17.13%" << endl;
    cout << "                                             _  __     " << endl;
    cout << " guaranteed TOTAL return to player:         (_)  / o / " << endl;
    cout << "                                          >  /  /   / o" << endl << endl;
    cout << " std deriv / volatility:          (very high)    ~10.14" << endl;
    cout << " surv param at 100 bets: (fairly optimal at vol) ~ 8.41" << endl << endl;

    cout << " hit rate (excluding feature wins):              15.42%" << endl;
    cout << " individual / total feature frequency:    279.3 / 139.7" << endl;
    cout << " ──────────────────────────────────────────────────────" << endl << endl;
    cout << "    simulated stats for important Shark Tank cases:    " << endl << endl;
    cout << " final count   length 3  length 4  length 5   case odds" << endl;
    cout << " ────────────┼──────────┼─────────┼──────────┼─────────" << endl;
    cout << "  [$$] × 15  │   2.414  │  2.407  │  2.195   │ 11.721%" << endl;
    cout << "  [$$] × 16  │   2.450  │  2.558  │  2.561   │  9.762%" << endl;
    cout << "  [$$] × 17  │   2.453  │  2.680  │  3.002   │  6.811%" << endl;
    cout << "  [$$] × 18  │   2.427  │  2.756  │  3.536   │  3.681%" << endl;
    cout << "  [$$] × 19  │   2.381  │  2.738  │  4.195   │  1.340%" << endl;
    cout << "  [$$] × 20  │   1.962  │  2.242  │  4.732   │  0.235%" << endl;
    cout << "             │    average successful spins   │        " << endl;
    cout << "               with given maximum win length    " << endl << endl<< endl;
    cout << "         press SPACE to go back to the main menu" << endl; //, 'i' for info about the survival parameter
    if (simple) {cout << endl;}
    char mode = readFirstCharacter();
    if (mode == '*') { cheat = !cheat; }
    if (simple) {cout << endl << endl << endl;} // these aren't called in !test_mode either
}


const char* toString(TSTYLE style) {
    switch (style) {
        case knight: return "knight";
        case box: return "cards";
        case funkShark: return "funk shark";
        case shortFunk: return "short funk";
        case boxSharky: return "small funk";
        case CardShark: return "card shark";
        case slimShark: return "slim shark";
        case boxShark: return "box shark";
        case CardKoi: return "card koi";
        case original: return "developer";
        case ghosty: return "ghosty";
        case words: return "split";
        case abstract: return "why not";
        case simply: return "simple";
        case simplest: return "simplest";
        case Roman: return "Roman I";
        case Roman2: return "Roman II";
        case Roman3: return "Roman iii";
        case modern: return "modern";
        case new1: return "snow flake";
        case new2: return "nuclear";
        case new3: return "circus";
        case new4: return "double dip";
        case racing: return "racing";
        case monster: return "funkiest";
        case curse: return "nsfw";
        default: return "unknown";
    }
}

map<string, string> symbolTranslator;

pair <TSTYLE, map<string, string>> changeTranslator(TSTYLE DEFAULT_STYLE){

         if (DEFAULT_STYLE == CardKoi)    DEFAULT_STYLE = CardShark;
    else if (DEFAULT_STYLE == CardShark)  DEFAULT_STYLE = funkShark;
    else if (DEFAULT_STYLE == funkShark)  DEFAULT_STYLE = slimShark;
    else if (DEFAULT_STYLE == slimShark)  DEFAULT_STYLE = shortFunk;
    else if (DEFAULT_STYLE == shortFunk)  DEFAULT_STYLE = boxSharky;
    else if (DEFAULT_STYLE == boxSharky)  DEFAULT_STYLE = boxShark;
    else if (DEFAULT_STYLE == boxShark)   DEFAULT_STYLE = new1;
    else if (DEFAULT_STYLE == new1)       DEFAULT_STYLE = new2;
    else if (DEFAULT_STYLE == new2)       DEFAULT_STYLE = new3;
    else if (DEFAULT_STYLE == new3)       DEFAULT_STYLE = new4;
    else if (DEFAULT_STYLE == new4)       DEFAULT_STYLE = racing;
    else if (DEFAULT_STYLE == racing)     DEFAULT_STYLE = box;
    else if (DEFAULT_STYLE == box)        DEFAULT_STYLE = abstract;
    else if (DEFAULT_STYLE == abstract)   DEFAULT_STYLE = original;
    else if (DEFAULT_STYLE == original)   DEFAULT_STYLE = simply;
    else if (DEFAULT_STYLE == simply)     DEFAULT_STYLE = simplest;
    else if (DEFAULT_STYLE == simplest)   DEFAULT_STYLE = Roman;
    else if (DEFAULT_STYLE == Roman)      DEFAULT_STYLE = Roman2;
    else if (DEFAULT_STYLE == Roman2)     DEFAULT_STYLE = Roman3;
    else if (DEFAULT_STYLE == Roman3)     DEFAULT_STYLE = modern;
    else if (DEFAULT_STYLE == modern)     DEFAULT_STYLE = knight;
    else if (DEFAULT_STYLE == knight)     DEFAULT_STYLE = words;
    else if (DEFAULT_STYLE == words)      DEFAULT_STYLE = ghosty;
    else if (DEFAULT_STYLE == ghosty)     DEFAULT_STYLE = monster;
    else if (DEFAULT_STYLE == monster)     DEFAULT_STYLE = curse;
    else if (DEFAULT_STYLE == curse)      DEFAULT_STYLE = CardKoi;

    symbolTranslator = {
        {"LV1", ""},
        {"LV2", ""},
        {"LV3", ""},
        {"LV4", ""},
        {"LV5", ""},
        {"LV6", ""},
        {"LV7", ""},
        {"HV1", ""},
        {"HV2", ""},
        {"HV3", ""},
        {"HV4", ""},
        {"HV5", ""},
        {"WLD", ""},
        {"TRG", ""},
        {"X7X", ""},
        {"0",   ""}
    };

    if (DEFAULT_STYLE == original)
    {
    symbolTranslator = {
        {"LV1", " L1 "},
        {"LV2", " L2 "},
        {"LV3", " L3 "},
        {"LV4", " L4 "},
        {"LV5", " L5 "},
        {"LV6", " L6 "},
        {"LV7", " L7 "},
        {"HV1", "{H1}"},
        {"HV2", "[H2]"},
        {"HV3", "[H3]"},
        {"HV4", "[H4]"},
        {"HV5", "[H5]"},
        {"WLD", "WILD"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    }
    else if (DEFAULT_STYLE == CardShark)
    {
    #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9\u2666 "},
        {"LV2", " 8\u2663 "},
        {"LV3", " 6\u2660 "},
        {"LV4", " 5\u2666 "},
        {"LV5", " 4\u2663 "},
        {"LV6", " 3\u2665 "},
        {"LV7", " 2\u2660 "},
        {"HV1", " A\u2660 "},
        {"HV2", " K\u2666 "},
        {"HV3", " Q\u2663 "},
        {"HV4", " J\u2665 "},
        {"HV5", " 1o "},
        {"WLD", "W7\u2665D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9♦ "},
        {"LV2", " 8♣ "},
        {"LV3", " 6♠ "},
        {"LV4", " 5♦ "},
        {"LV5", " 4♣ "},
        {"LV6", " 3♥ "},
        {"LV7", " 2♠ "},
        {"HV1", " A♠ "},
        {"HV2", " K♦ "},
        {"HV3", " Q♣ "},
        {"HV4", " J♥ "},
        {"HV5", " 1o "},
        {"WLD", "W7♥D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == slimShark)
    {
    #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9\u2666 "},
        {"LV2", " 8\u2663 "},
        {"LV3", " 6\u2660 "},
        {"LV4", " 5\u2666 "},
        {"LV5", " 4\u2663 "},
        {"LV6", " 3\u2665 "},
        {"LV7", " 2\u2660 "},
        {"HV1", "▀A\u2660▄"},
        {"HV2", "▀K\u2666▄"},
        {"HV3", "▀Q\u2663▄"},
        {"HV4", "▀J\u2665▄"},
        {"HV5", "▀1o▄"},
        {"WLD", "W7\u2665D"},
        {"TRG", "TanK"},
        {"X7X", "MeGa"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9♦ "},
        {"LV2", " 8♣ "},
        {"LV3", " 6♠ "},
        {"LV4", " 5♦ "},
        {"LV5", " 4♣ "},
        {"LV6", " 3♥ "},
        {"LV7", " 2♠ "},
        {"HV1", "▀A♠▄"},
        {"HV2", "▀K♦▄"},
        {"HV3", "▀Q♣▄"},
        {"HV4", "▀J♥▄"},
        {"HV5", "▀1o▄"},
        {"WLD", "W7♥D"},
        {"TRG", "TanK"},
        {"X7X", "MeGa"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == shortFunk)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", "9\u2666  "},
        {"LV2", "8\u2663  "},
        {"LV3", "6\u2660  "},
        {"LV4", "5\u2666  "},
        {"LV5", "4\u2663  "},
        {"LV6", "3\u2665  "},
        {"LV7", "2\u2660  "},
        {"HV1", "A\u2660\u2660 "},
        {"HV2", "K\u2666\u2666 "},
        {"HV3", "Q\u2663\u2663 "},
        {"HV4", "J\u2665\u2665 "},
        {"HV5", "T\u2660\u2660 "},
        {"WLD", "7\u2665\u2665\u2665"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", "9♦  "},
        {"LV2", "8♣  "},
        {"LV3", "6♠  "},
        {"LV4", "5♦  "},
        {"LV5", "4♣  "},
        {"LV6", "3♥  "},
        {"LV7", "2♠  "},
        {"HV1", "A♠♠ "},
        {"HV2", "K♦♦ "},
        {"HV3", "Q♣♣ "},
        {"HV4", "J♥♥ "},
        {"HV5", "T♠♠ "},
        {"WLD", "7♥♥♥"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == boxShark)
    {
    #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9\u2666 "},
        {"LV2", " 8\u2663 "},
        {"LV3", " 6\u2660 "},
        {"LV4", " 5\u2666 "},
        {"LV5", " 4\u2663 "},
        {"LV6", " 3\u2665 "},
        {"LV7", " 2\u2660 "},
        {"HV1", "{A\u2660}"},
        {"HV2", "[K\u2666]"},
        {"HV3", "[Q\u2663]"},
        {"HV4", "[J\u2665]"},
        {"HV5", "[1o]"},
        {"WLD", "W7\u2665D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9♦ "},
        {"LV2", " 8♣ "},
        {"LV3", " 6♠ "},
        {"LV4", " 5♦ "},
        {"LV5", " 4♣ "},
        {"LV6", " 3♥ "},
        {"LV7", " 2♠ "},
        {"HV1", "{A♠}"},
        {"HV2", "[K♦]"},
        {"HV3", "[Q♣]"},
        {"HV4", "[J♥]"},
        {"HV5", "[1o]"},
        {"WLD", "W7♥D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == boxSharky)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " \u26669 "},
        {"LV2", " \u26638 "},
        {"LV3", " \u26606 "},
        {"LV4", " \u26665 "},
        {"LV5", " \u26634 "},
        {"LV6", " \u26653 "},
        {"LV7", " \u26602 "},
        {"HV1", "A\u2660E "},
        {"HV2", "K\u2666G "},
        {"HV3", "Q\u2663N "},
        {"HV4", "J\u2665K "},
        {"HV5", "I\u2660O "},
        {"WLD", "W\u2665D "},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " ♦9 "},
        {"LV2", " ♣8 "},
        {"LV3", " ♠6 "},
        {"LV4", " ♦5 "},
        {"LV5", " ♣4 "},
        {"LV6", " ♥3 "},
        {"LV7", " ♠2 "},
        {"HV1", "A♠E "},
        {"HV2", "K♦G "},
        {"HV3", "Q♣N "},
        {"HV4", "J♥K "},
        {"HV5", "I♠O "},
        {"WLD", "W♥D "},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == abstract)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9  "},
        {"LV2", "  8 "},
        {"LV3", "  6 "},
        {"LV4", " 5  "},
        {"LV5", "  4 "},
        {"LV6", " 3  "},
        {"LV7", "  2 "},
        {"HV1", "\u2660A\u2660\u2660"},
        {"HV2", "\u2666\u2666K\u2666"},
        {"HV3", "\u2663Q\u2663\u2663"},
        {"HV4", "\u2665\u2665J\u2665"},
        {"HV5", "\u2660T\u2660\u2660"},
        {"WLD", "\u26657\u2665\u2665"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9  "},
        {"LV2", "  8 "},
        {"LV3", "  6 "},
        {"LV4", " 5  "},
        {"LV5", "  4 "},
        {"LV6", " 3  "},
        {"LV7", "  2 "},
        {"HV1", "♠A♠♠"},
        {"HV2", "♦♦K♦"},
        {"HV3", "♣Q♣♣"},
        {"HV4", "♥♥J♥"},
        {"HV5", "♠T♠♠"},
        {"WLD", "♥7♥♥"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == new1)
    {
    #ifdef _WIN32
    symbolTranslator = {
        {"LV1", "«9\u2666»"},
        {"LV2", "«8\u2663»"},
        {"LV3", "«6\u2660»"},
        {"LV4", "«5\u2666»"},
        {"LV5", "«4\u2663»"},
        {"LV6", "«3\u2665»"},
        {"LV7", "«2\u2660»"},
        {"HV1", "⟪A\u2660⟫"},
        {"HV2", "⟪K\u2666⟫"},
        {"HV3", "⟪Q\u2663⟫"},
        {"HV4", "⟪J\u2665⟫"},
        {"HV5", "⟪1o⟫"},
        {"WLD", "W7\u2665D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", "«9♦»"},
        {"LV2", "«8♣»"},
        {"LV3", "«6♠»"},
        {"LV4", "«5♦»"},
        {"LV5", "«4♣»"},
        {"LV6", "«3♥»"},
        {"LV7", "«2♠»"},
        {"HV1", "⟪A♠⟫"},
        {"HV2", "⟪K♦⟫"},
        {"HV3", "⟪Q♣⟫"},
        {"HV4", "⟪J♥⟫"},
        {"HV5", "⟪1o⟫"},
        {"WLD", "W7♥D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == new2)
    {
        symbolTranslator = {
        {"LV1", " 9☣ "},
        {"LV2", " 8☣ "},
        {"LV3", " 6☣ "},
        {"LV4", " 5☣ "},
        {"LV5", " 4☣ "},
        {"LV6", " 3☣ "},
        {"LV7", " 2☣ "},
        {"HV1", "▛A☠▟"},
        {"HV2", "▛K☢▟"},
        {"HV3", "▛Q☢▟"},
        {"HV4", "▛J☢▟"},
        {"HV5", "▛1☢▟"},
        {"WLD", "W7☠D"},
        {"TRG", "ta☣k"},
        {"X7X", "me☣a"},
        { "0" , "    "}
        };

    }
    else if (DEFAULT_STYLE == racing)
    {
    #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9\u2666 "},
        {"LV2", " 8\u2663 "},
        {"LV3", " 6\u2660 "},
        {"LV4", " 5\u2666 "},
        {"LV5", " 4\u2663 "},
        {"LV6", " 3\u2665 "},
        {"LV7", " 2\u2660 "},
        {"HV1", "░A\u2660░"},
        {"HV2", "░K\u2666░"},
        {"HV3", "░Q\u2663░"},
        {"HV4", "░J\u2665░"},
        {"HV5", "░1o░"},
        {"WLD", "╳7\u2665╳"},
        {"TRG", "▞TK▞"},
        {"X7X", "▚MG▚"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9♦ "},
        {"LV2", " 8♣ "},
        {"LV3", " 6♠ "},
        {"LV4", " 5♦ "},
        {"LV5", " 4♣ "},
        {"LV6", " 3♥ "},
        {"LV7", " 2♠ "},
        {"HV1", "░A♠░"},
        {"HV2", "░K♦░"},
        {"HV3", "░Q♣░"},
        {"HV4", "░J♥░"},
        {"HV5", "░1o░"},
        {"WLD", "╳7♥╳"},
        {"TRG", "▞TK▞"},
        {"X7X", "▚MG▚"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == new3)
    {
        symbolTranslator = {
        {"LV1", " 9  "},
        {"LV2", "  8 "},
        {"LV3", " 6  "},
        {"LV4", "  5 "},
        {"LV5", " 4  "},
        {"LV6", " 3  "},
        {"LV7", "  2 "},
        {"HV1", " ░A░"},
        {"HV2", "░K░ "},
        {"HV3", " ░Q░"},
        {"HV4", "░J░ "},
        {"HV5", " ░T░"},
        {"WLD", "7777"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };

    }
    else if (DEFAULT_STYLE == new4)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9\u2666 "},
        {"LV2", " 8\u2663 "},
        {"LV3", " 6\u2660 "},
        {"LV4", " 5\u2666 "},
        {"LV5", " 4\u2663 "},
        {"LV6", " 3\u2665 "},
        {"LV7", " 2\u2660 "},
        {"HV1", "►A\u2660◄"},
        {"HV2", "►K\u2666◄"},
        {"HV3", "►Q\u2663◄"},
        {"HV4", "►J\u2665◄"},
        {"HV5", "►1o◄"},
        {"WLD", "►7\u2665◄"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9♦ "},
        {"LV2", " 8♣ "},
        {"LV3", " 6♠ "},
        {"LV4", " 5♦ "},
        {"LV5", " 4♣ "},
        {"LV6", " 3♥ "},
        {"LV7", " 2♠ "},
        {"HV1", "►A♠◄"},
        {"HV2", "►K♦◄"},
        {"HV3", "►Q♣◄"},
        {"HV4", "►J♥◄"},
        {"HV5", "►1o◄"},
        {"WLD", "►7♥◄"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };
    #endif
    }
    else if (DEFAULT_STYLE == CardKoi)
    {
        symbolTranslator = {
        {"LV1", " 9• "},
        {"LV2", " 8• "},
        {"LV3", " 6• "},
        {"LV4", " 5• "},
        {"LV5", " 4• "},
        {"LV6", " 3• "},
        {"LV7", " 2• "},
        {"HV1", " A‡ "},
        {"HV2", " K† "},
        {"HV3", " Q† "},
        {"HV4", " J† "},
        {"HV5", " 1o "},
        {"WLD", "w7ld"},
        {"TRG", "TanK"},
        {"X7X", "MeGa"},
        { "0" , "    "}
        };

    }
    else if (DEFAULT_STYLE == simply)
    {
        symbolTranslator = {
        {"LV1", " 9  "},
        {"LV2", " 8  "},
        {"LV3", " 6  "},
        {"LV4", " 5  "},
        {"LV5", " 4  "},
        {"LV6", " 3  "},
        {"LV7", " 2  "},
        {"HV1", "ACE "},
        {"HV2", "KING"},
        {"HV3", "QUEN"},
        {"HV4", "JACK"},
        {"HV5", " 1O "},
        {"WLD", "WILD"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };
    }
    else if (DEFAULT_STYLE == simplest)
    {
        symbolTranslator = {
        {"LV1", " 9  "},
        {"LV2", " 8  "},
        {"LV3", " 6  "},
        {"LV4", " 5  "},
        {"LV5", " 4  "},
        {"LV6", " 3  "},
        {"LV7", " 2  "},
        {"HV1", " A  "},
        {"HV2", " K  "},
        {"HV3", " Q  "},
        {"HV4", " J  "},
        {"HV5", " 1  "},
        {"WLD", " W  "},
        {"TRG", " T  "},
        {"X7X", " M  "},
        { "0" , "    "}
        };
    }
    else if (DEFAULT_STYLE == curse)
    {
        symbolTranslator = {
        {"LV1", "grr "},
        {"LV2", "hmm "},
        {"LV3", "oof "},
        {"LV4", "meh "},
        {"LV5", "bah "},
        {"LV6", "ick "},
        {"LV7", "eew "},
        {"HV1", "FUCK"},
        {"HV2", "Poop"},
        {"HV3", "Damn"},
        {"HV4", "Shit"},
        {"HV5", "Dirt"},
        {"WLD", "S7UT"},
        {"TRG", "WET!"},
        {"X7X", "FAT!"},
        { "0" , "    "}
        };
    }
    else if (DEFAULT_STYLE == Roman)
    {
        symbolTranslator = {
        {"LV1", " IX "},
        {"LV2", "VIII"},
        {"LV3", " VI "},
        {"LV4", " V  "},
        {"LV5", " IV "},
        {"LV6", "III "},
        {"LV7", " II "},
        {"HV1", " A  "},
        {"HV2", " K  "},
        {"HV3", " Q  "},
        {"HV4", " J  "},
        {"HV5", " X  "},
        {"WLD", "WILD"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };
    }
    else if (DEFAULT_STYLE == Roman2)
    {
        symbolTranslator = {
        {"LV1", " IX "},
        {"LV2", "VIII"},
        {"LV3", " VI "},
        {"LV4", " V  "},
        {"LV5", " IV "},
        {"LV6", "III "},
        {"LV7", " II "},
        {"HV1", "ACE "},
        {"HV2", "KING"},
        {"HV3", "QUEN"},
        {"HV4", "JACK"},
        {"HV5", "TEN "},
        {"WLD", "WILD"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };
    }
    else if (DEFAULT_STYLE == Roman3)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", "\u2666ix\u2666"},
        {"LV2", "iix\u2663"},
        {"LV3", "\u2660vi\u2660"},
        {"LV4", "\u2666\u2666v\u2666"},
        {"LV5", "\u2663iv\u2663"},
        {"LV6", "iii\u2665"},
        {"LV7", "\u2660ii\u2660"},
        {"HV1", "\u2660\u2660A\u2660"},
        {"HV2", "\u2666\u2666K\u2666"},
        {"HV3", "\u2663\u2663Q\u2663"},
        {"HV4", "\u2665\u2665J\u2665"},
        {"HV5", "\u2660\u2660X\u2660"},
        {"WLD", "vii\u2665"},
        {"TRG", "TAN\u2665"},
        {"X7X", "MEG\u2660"},
        { "0" , "    "}
        };
    #else
    symbolTranslator = {
        {"LV1", "♦ix♦"},
        {"LV2", "iix♣"},
        {"LV3", "♠vi♠"},
        {"LV4", "♦♦v♦"},
        {"LV5", "♣iv♣"},
        {"LV6", "iii♥"},
        {"LV7", "♠ii♠"},
        {"HV1", "♠♠A♠"},
        {"HV2", "♦♦K♦"},
        {"HV3", "♣♣Q♣"},
        {"HV4", "♥♥J♥"},
        {"HV5", "♠♠X♠"},
        {"WLD", "vii♥"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };
    #endif
    }
    else if (DEFAULT_STYLE == funkShark)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9\u2666 "},
        {"LV2", " \u26638 "},
        {"LV3", " 6\u2660 "},
        {"LV4", " \u26665 "},
        {"LV5", " 4\u2663 "},
        {"LV6", " 3\u2665 "},
        {"LV7", " \u26602 "},
        {"HV1", "A\u2660CE"},
        {"HV2", "K\u2666NG"},
        {"HV3", "QU\u2663N"},
        {"HV4", "J\u2665CK"},
        {"HV5", "TE\u2660N"},
        {"WLD", "W7\u2665D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9♦ "},
        {"LV2", " ♣8 "},
        {"LV3", " 6♠ "},
        {"LV4", " ♦5 "},
        {"LV5", " 4♣ "},
        {"LV6", " 3♥ "},
        {"LV7", " ♠2 "},
        {"HV1", "A♠CE"},
        {"HV2", "K♦NG"},
        {"HV3", "QU♣N"},
        {"HV4", "J♥CK"},
        {"HV5", "TE♠N"},
        {"WLD", "W7♥D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == box)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", "█9\u2666█"},
        {"LV2", "█8\u2663█"},
        {"LV3", "█6\u2660█"},
        {"LV4", "█5\u2666█"},
        {"LV5", "█4\u2663█"},
        {"LV6", "█3\u2665█"},
        {"LV7", "█2\u2660█"},
        {"HV1", "►A\u2660◄"},
        {"HV2", "►K\u2666◄"},
        {"HV3", "►Q\u2663◄"},
        {"HV4", "►J\u2665◄"},
        {"HV5", "►1o◄"},
        {"WLD", "W7\u2665D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", "█9♦█"},
        {"LV2", "█8♣█"},
        {"LV3", "█6♠█"},
        {"LV4", "█5♦█"},
        {"LV5", "█4♣█"},
        {"LV6", "█3♥█"},
        {"LV7", "█2♠█"},
        {"HV1", "►A♠◄"},
        {"HV2", "►K♦◄"},
        {"HV3", "►Q♣◄"},
        {"HV4", "►J♥◄"},
        {"HV5", "►1o◄"},
        {"WLD", "W7♥D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };
    #endif
    }
    else if (DEFAULT_STYLE == words)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", "\u26669  "},
        {"LV2", "\u26638  "},
        {"LV3", "\u26606  "},
        {"LV4", "\u26665  "},
        {"LV5", "\u26634  "},
        {"LV6", "\u26653  "},
        {"LV7", "\u26602  "},
        {"HV1", "██A\u2660"},
        {"HV2", "██K\u2666"},
        {"HV3", "██Q\u2663"},
        {"HV4", "██J\u2665"},
        {"HV5", "██1o"},
        {"WLD", "\u26657LD"},
        {"TRG", "T\u2660N\u2663"},
        {"X7X", "M\u2665G\u2666"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", "♦9  "},
        {"LV2", "♣8  "},
        {"LV3", "♠6  "},
        {"LV4", "♦5  "},
        {"LV5", "♣4  "},
        {"LV6", "♥3  "},
        {"LV7", "♠2  "},
        {"HV1", "██A♠"},
        {"HV2", "██K♦"},
        {"HV3", "██Q♣"},
        {"HV4", "██J♥"},
        {"HV5", "██1o"},
        {"WLD", "♥7LD"},
        {"TRG", "T♠K♣"},
        {"X7X", "M♥G♦"},
        { "0" , "    "}
    };
    #endif
    }
    else if (DEFAULT_STYLE == modern)
    {
        symbolTranslator = {
        {"LV1", "▓▒░2"},
        {"LV2", "▓▒░3"},
        {"LV3", "▓▒░4"},
        {"LV4", "▓▒░5"},
        {"LV5", "▓▒░6"},
        {"LV6", "▓▒░8"},
        {"LV7", "▓▒░9"},
        {"HV1", "A░▒▓"},
        {"HV2", "K░▒▓"},
        {"HV3", "Q░▒▓"},
        {"HV4", "J░▒▓"},
        {"HV5", "1░▒▓"},
        {"WLD", "▓▒░7"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
        };
    }
    else if (DEFAULT_STYLE == knight)
    {
        symbolTranslator = {
            {"LV1", " 9† "},
            {"LV2", " 8• "},
            {"LV3", " 6• "},
            {"LV4", " 5† "},
            {"LV5", " 4• "},
            {"LV6", " 3† "},
            {"LV7", " 2• "},
            {"HV1", " A‡E"},
            {"HV2", " K┼G"},
            {"HV3", " Q┼N"},
            {"HV4", " J┼K"},
            {"HV5", " I┼O"},
            {"WLD", "W7╬D"},
            {"TRG", "TA‡K"},
            {"X7X", "ME‡A"},
            { "0" , "    "}
        };
    }
    else if (DEFAULT_STYLE == ghosty)
    {
        symbolTranslator = {
        {"LV1", "    "},
        {"LV2", "    "},
        {"LV3", "    "},
        {"LV4", "    "},
        {"LV5", "    "},
        {"LV6", "    "},
        {"LV7", "    "},
        {"HV1", "    "},
        {"HV2", "    "},
        {"HV3", "    "},
        {"HV4", "    "},
        {"HV5", "    "},
        {"WLD", "    "},
        {"TRG", "    "},
        {"X7X", "    "},
        { "0" , "    "}
        };

    }
    else if (DEFAULT_STYLE == monster)
    {
        #ifdef _WIN32
    symbolTranslator = {
        {"LV1", " 9\u2666 "},
        {"LV2", " 8\u2663 "},
        {"LV3", " 6\u2660 "},
        {"LV4", " 5\u2666 "},
        {"LV5", " 4\u2663 "},
        {"LV6", " 3\u2665 "},
        {"LV7", " 2\u2660 "},
        {"HV1", "AC\u2660E"},
        {"HV2", "KI\u2666G"},
        {"HV3", "QU\u2663N"},
        {"HV4", "JA\u2665K"},
        {"HV5", "TE\u2660N"},
        {"WLD", "W7♥D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #else
    symbolTranslator = {
        {"LV1", " 9♦ "},
        {"LV2", " 8♣ "},
        {"LV3", " 6♠ "},
        {"LV4", " 5♦ "},
        {"LV5", " 4♣ "},
        {"LV6", " 3♥ "},
        {"LV7", " 2♠ "},
        {"HV1", "AC♠E"},
        {"HV2", "KI♦G"},
        {"HV3", "QU♣N"},
        {"HV4", "JA♥K"},
        {"HV5", "TE♠N"},
        {"WLD", "W7♥D"},
        {"TRG", "TANK"},
        {"X7X", "MEGA"},
        { "0" , "    "}
    };
    #endif
    }

    return {DEFAULT_STYLE,symbolTranslator};
}

int TWC = 0;
void printTWC(map<string, int>& totalWinCounts){
    if (!totalWinCounts.empty() && TWC==1){
        cout << endl << "Total number of hits by win combination: " << endl;
        for (const auto& entry : totalWinCounts) {

            cout << setw(10) << right << entry.second  << " │ " << entry.first << endl;
        }
    }
}

void printTestSymbols(){

    int random = (rand() % 5) + 1;

    string symbol = "HV" + to_string(random);
    string translatedSymbol = symbolTranslator.count(symbol) > 0
                                      ? symbolTranslator[symbol]
                                      : symbol; // Fallback to original
    setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox); // Set color based on symbol
    cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);cout << " │ ";

    random = (rand() % 7) + 1;

    symbol = "LV" + to_string(random);
    translatedSymbol = symbolTranslator.count(symbol) > 0
                                      ? symbolTranslator[symbol]
                                      : symbol; // Fallback to original
    setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox); // Set color based on symbol
    cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);cout << " │ ";

    random = rand() % 2;
    if (random < 1) symbol = "TRG"; else symbol = "X7X";
    translatedSymbol = symbolTranslator.count(symbol) > 0
                                      ? symbolTranslator[symbol]
                                      : symbol; // Fallback to original
    setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox); // Set color based on symbol
    cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);cout << " │ ";

    symbol = "WLD";
    translatedSymbol = symbolTranslator.count(symbol) > 0
                                      ? symbolTranslator[symbol]
                                      : symbol; // Fallback to original
    setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox); // Set color based on symbol
    cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);

}

void colorDemo(){
    setTextColor("HV1", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("HV2", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("HV3", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("HV4", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("HV5", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << "   ";
    setTextColor("LV1", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("LV2", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("LV3", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("LV4", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("LV5", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("LV6", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("LV7", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << "   ";
    setTextColor("TRG", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("X7X", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " ";
    setTextColor("WLD", DEFAULT_COLOR, FAT_UI, HVbox); cout << "$";
    setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
}

map<string, vector<int>> winTable = { // at betFactor = 1 (one game costing price = 20)
    {"LV1", {1, 10, 100}},
    {"LV2", {1, 10, 100}},
    {"LV3", {1, 10, 100}},
    {"LV4", {1, 10, 100}},
    {"LV5", {1, 10, 100}},
    {"LV6", {1, 10, 100}},
    {"LV7", {1, 10, 100}},
    {"HV1", {3, 30, 300}},
    {"HV2", {2, 20, 200}},
    {"HV3", {2, 20, 200}},
    {"HV4", {2, 20, 200}},
    {"HV5", {2, 20, 200}},
    {"WLD", {100, 2000, 50000}},
    {"TRG", {0, 0, 0}},
	{"X7X", {0, 0, 0}},
};

void print(const map<string, vector<int>>& winTable, int betFactor, bool fg, bool x7, bool loanShark, int lgames, bool simple) { // prints win table, gives option to change bet if there is no feature following
    cout << left << setw(10)<<   "       ┌────────────────────────────────────────┐ 178WL" << endl;
    cout <<                      "       │             ×3       ×4       ×5       │" << endl;
    cout << "       │  " << setw(10) << " W7LD      "
         << setw(9) << winTable.at("WLD")[0] * betFactor
         << setw(9) << winTable.at("WLD")[1] * betFactor
         << setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
    cout << "       │  ";
    if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
         cout << setw(9) << winTable.at("HV1")[0] * betFactor
         << setw(9) << winTable.at("HV1")[1] * betFactor
         << setw(9) << winTable.at("HV1")[2] * betFactor
         << "│ ";if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
    cout << "       │  ";
    if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
         cout << setw(9) << winTable.at("HV2")[0] * betFactor
         << setw(9) << winTable.at("HV2")[1] * betFactor
         << setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
    cout << "       │  " << setw(10) << "  2-9      "
         << setw(9) << winTable.at("LV1")[0] * betFactor
         << setw(9) << winTable.at("LV1")[1] * betFactor
         << setw(9) << winTable.at("LV1")[2] * betFactor
         << "│ ";
         if (!fg && !x7) { cout << "cycle";} cout << endl;
    cout << "       │                                        │ "; if (!fg && !x7) { cout << "'b/d'";} cout << endl;
    cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
         << " │  "; cout << endl;
		 cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
         << " │  ";
		 if (loanShark){cout << "game";
		 }
		 cout << endl;
    cout << "       └────────────────────────────────────────┘  ";
	if (loanShark){
		cout << lgames;
	}
	cout << endl;
}

void print7(const map<string, vector<int>>& winTable, int betFactor, int spins, bool simple) { // prints win table, gives option to change bet if there is no feature following
    cout << left << setw(10) <<  "       ┌────────────────────────────────────────┐ 421WL" << endl;
    cout <<                      "       │             ×3       ×4       ×5       │" << endl;
    cout << "       │  " << setw(10) << " W7LD      "
         << setw(9) << winTable.at("WLD")[0] * betFactor
         << setw(9) << winTable.at("WLD")[1] * betFactor
         << setw(9) << winTable.at("WLD")[2] * betFactor << "│"; if (spins != -1) {cout << " spins";} cout << endl;
    cout << "       │  ";
    if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
         cout << setw(9) << winTable.at("HV1")[0] * betFactor
         << setw(9) << winTable.at("HV1")[1] * betFactor
         << setw(9) << winTable.at("HV1")[2] * betFactor
         << "│"; if (spins != -1) {cout << " left";} cout << endl;
    cout << "       │  ";
    if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
         cout << setw(9) << winTable.at("HV2")[0] * betFactor
         << setw(9) << winTable.at("HV2")[1] * betFactor
         << setw(9) << winTable.at("HV2")[2] * betFactor << "│  "; if (spins != -1) {cout << setw(2) << spins;} cout << endl;
    cout << "       │  " << setw(10) << "  2-9      "
         << setw(9) << winTable.at("LV1")[0] * betFactor
         << setw(9) << winTable.at("LV1")[1] * betFactor
         << setw(9) << winTable.at("LV1")[2] * betFactor
         << "│ ";
         cout << endl;
    cout << "       └────────────────────────────────────────┘";
}

vector<vector<pair<int, int>>> winningLines7 = { // defines the winning lines for the x7 bonus (421)
{{0, 0}, {1, 0}, {2, 0}, {3, 0}, {4, 0}},
{{0, 0}, {1, 0}, {2, 0}, {3, 0}, {4, 1}},
{{0, 0}, {1, 0}, {2, 0}, {3, 1}, {4, 0}},
{{0, 0}, {1, 0}, {2, 0}, {3, 1}, {4, 1}},
{{0, 0}, {1, 0}, {2, 0}, {3, 1}, {4, 2}},
{{0, 0}, {1, 0}, {2, 1}, {3, 0}, {4, 0}},
{{0, 0}, {1, 0}, {2, 1}, {3, 0}, {4, 1}},
{{0, 0}, {1, 0}, {2, 1}, {3, 1}, {4, 0}},
{{0, 0}, {1, 0}, {2, 1}, {3, 1}, {4, 1}},
{{0, 0}, {1, 0}, {2, 1}, {3, 1}, {4, 2}},
{{0, 0}, {1, 0}, {2, 1}, {3, 2}, {4, 1}},
{{0, 0}, {1, 0}, {2, 1}, {3, 2}, {4, 2}},
{{0, 0}, {1, 0}, {2, 1}, {3, 2}, {4, 3}},
{{0, 0}, {1, 1}, {2, 0}, {3, 0}, {4, 0}},
{{0, 0}, {1, 1}, {2, 0}, {3, 0}, {4, 1}},
{{0, 0}, {1, 1}, {2, 0}, {3, 1}, {4, 0}},
{{0, 0}, {1, 1}, {2, 0}, {3, 1}, {4, 1}},
{{0, 0}, {1, 1}, {2, 0}, {3, 1}, {4, 2}},
{{0, 0}, {1, 1}, {2, 1}, {3, 0}, {4, 0}},
{{0, 0}, {1, 1}, {2, 1}, {3, 0}, {4, 1}},
{{0, 0}, {1, 1}, {2, 1}, {3, 1}, {4, 0}},
{{0, 0}, {1, 1}, {2, 1}, {3, 1}, {4, 1}},
{{0, 0}, {1, 1}, {2, 1}, {3, 1}, {4, 2}},
{{0, 0}, {1, 1}, {2, 1}, {3, 2}, {4, 1}},
{{0, 0}, {1, 1}, {2, 1}, {3, 2}, {4, 2}},
{{0, 0}, {1, 1}, {2, 1}, {3, 2}, {4, 3}},
{{0, 0}, {1, 1}, {2, 2}, {3, 1}, {4, 0}},
{{0, 0}, {1, 1}, {2, 2}, {3, 1}, {4, 1}},
{{0, 0}, {1, 1}, {2, 2}, {3, 1}, {4, 2}},
{{0, 0}, {1, 1}, {2, 2}, {3, 2}, {4, 1}},
{{0, 0}, {1, 1}, {2, 2}, {3, 2}, {4, 2}},
{{0, 0}, {1, 1}, {2, 2}, {3, 2}, {4, 3}},
{{0, 0}, {1, 1}, {2, 2}, {3, 3}, {4, 2}},
{{0, 0}, {1, 1}, {2, 2}, {3, 3}, {4, 3}},
{{0, 0}, {1, 1}, {2, 2}, {3, 3}, {4, 4}},
{{0, 1}, {1, 0}, {2, 0}, {3, 0}, {4, 0}},
{{0, 1}, {1, 0}, {2, 0}, {3, 0}, {4, 1}},
{{0, 1}, {1, 0}, {2, 0}, {3, 1}, {4, 0}},
{{0, 1}, {1, 0}, {2, 0}, {3, 1}, {4, 1}},
{{0, 1}, {1, 0}, {2, 0}, {3, 1}, {4, 2}},
{{0, 1}, {1, 0}, {2, 1}, {3, 0}, {4, 0}},
{{0, 1}, {1, 0}, {2, 1}, {3, 0}, {4, 1}},
{{0, 1}, {1, 0}, {2, 1}, {3, 1}, {4, 0}},
{{0, 1}, {1, 0}, {2, 1}, {3, 1}, {4, 1}},
{{0, 1}, {1, 0}, {2, 1}, {3, 1}, {4, 2}},
{{0, 1}, {1, 0}, {2, 1}, {3, 2}, {4, 1}},
{{0, 1}, {1, 0}, {2, 1}, {3, 2}, {4, 2}},
{{0, 1}, {1, 0}, {2, 1}, {3, 2}, {4, 3}},
{{0, 1}, {1, 1}, {2, 0}, {3, 0}, {4, 0}},
{{0, 1}, {1, 1}, {2, 0}, {3, 0}, {4, 1}},
{{0, 1}, {1, 1}, {2, 0}, {3, 1}, {4, 0}},
{{0, 1}, {1, 1}, {2, 0}, {3, 1}, {4, 1}},
{{0, 1}, {1, 1}, {2, 0}, {3, 1}, {4, 2}},
{{0, 1}, {1, 1}, {2, 1}, {3, 0}, {4, 0}},
{{0, 1}, {1, 1}, {2, 1}, {3, 0}, {4, 1}},
{{0, 1}, {1, 1}, {2, 1}, {3, 1}, {4, 0}},
{{0, 1}, {1, 1}, {2, 1}, {3, 1}, {4, 1}},
{{0, 1}, {1, 1}, {2, 1}, {3, 1}, {4, 2}},
{{0, 1}, {1, 1}, {2, 1}, {3, 2}, {4, 1}},
{{0, 1}, {1, 1}, {2, 1}, {3, 2}, {4, 2}},
{{0, 1}, {1, 1}, {2, 1}, {3, 2}, {4, 3}},
{{0, 1}, {1, 1}, {2, 2}, {3, 1}, {4, 0}},
{{0, 1}, {1, 1}, {2, 2}, {3, 1}, {4, 1}},
{{0, 1}, {1, 1}, {2, 2}, {3, 1}, {4, 2}},
{{0, 1}, {1, 1}, {2, 2}, {3, 2}, {4, 1}},
{{0, 1}, {1, 1}, {2, 2}, {3, 2}, {4, 2}},
{{0, 1}, {1, 1}, {2, 2}, {3, 2}, {4, 3}},
{{0, 1}, {1, 1}, {2, 2}, {3, 3}, {4, 2}},
{{0, 1}, {1, 1}, {2, 2}, {3, 3}, {4, 3}},
{{0, 1}, {1, 1}, {2, 2}, {3, 3}, {4, 4}},
{{0, 1}, {1, 2}, {2, 1}, {3, 0}, {4, 0}},
{{0, 1}, {1, 2}, {2, 1}, {3, 0}, {4, 1}},
{{0, 1}, {1, 2}, {2, 1}, {3, 1}, {4, 0}},
{{0, 1}, {1, 2}, {2, 1}, {3, 1}, {4, 1}},
{{0, 1}, {1, 2}, {2, 1}, {3, 1}, {4, 2}},
{{0, 1}, {1, 2}, {2, 1}, {3, 2}, {4, 1}},
{{0, 1}, {1, 2}, {2, 1}, {3, 2}, {4, 2}},
{{0, 1}, {1, 2}, {2, 1}, {3, 2}, {4, 3}},
{{0, 1}, {1, 2}, {2, 2}, {3, 1}, {4, 0}},
{{0, 1}, {1, 2}, {2, 2}, {3, 1}, {4, 1}},
{{0, 1}, {1, 2}, {2, 2}, {3, 1}, {4, 2}},
{{0, 1}, {1, 2}, {2, 2}, {3, 2}, {4, 1}},
{{0, 1}, {1, 2}, {2, 2}, {3, 2}, {4, 2}},
{{0, 1}, {1, 2}, {2, 2}, {3, 2}, {4, 3}},
{{0, 1}, {1, 2}, {2, 2}, {3, 3}, {4, 2}},
{{0, 1}, {1, 2}, {2, 2}, {3, 3}, {4, 3}},
{{0, 1}, {1, 2}, {2, 2}, {3, 3}, {4, 4}},
{{0, 1}, {1, 2}, {2, 3}, {3, 2}, {4, 1}},
{{0, 1}, {1, 2}, {2, 3}, {3, 2}, {4, 2}},
{{0, 1}, {1, 2}, {2, 3}, {3, 2}, {4, 3}},
{{0, 1}, {1, 2}, {2, 3}, {3, 3}, {4, 2}},
{{0, 1}, {1, 2}, {2, 3}, {3, 3}, {4, 3}},
{{0, 1}, {1, 2}, {2, 3}, {3, 3}, {4, 4}},
{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 3}},
{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 4}},
{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}},
{{0, 2}, {1, 1}, {2, 0}, {3, 0}, {4, 0}},
{{0, 2}, {1, 1}, {2, 0}, {3, 0}, {4, 1}},
{{0, 2}, {1, 1}, {2, 0}, {3, 1}, {4, 0}},
{{0, 2}, {1, 1}, {2, 0}, {3, 1}, {4, 1}},
{{0, 2}, {1, 1}, {2, 0}, {3, 1}, {4, 2}},
{{0, 2}, {1, 1}, {2, 1}, {3, 0}, {4, 0}},
{{0, 2}, {1, 1}, {2, 1}, {3, 0}, {4, 1}},
{{0, 2}, {1, 1}, {2, 1}, {3, 1}, {4, 0}},
{{0, 2}, {1, 1}, {2, 1}, {3, 1}, {4, 1}},
{{0, 2}, {1, 1}, {2, 1}, {3, 1}, {4, 2}},
{{0, 2}, {1, 1}, {2, 1}, {3, 2}, {4, 1}},
{{0, 2}, {1, 1}, {2, 1}, {3, 2}, {4, 2}},
{{0, 2}, {1, 1}, {2, 1}, {3, 2}, {4, 3}},
{{0, 2}, {1, 1}, {2, 2}, {3, 1}, {4, 0}},
{{0, 2}, {1, 1}, {2, 2}, {3, 1}, {4, 1}},
{{0, 2}, {1, 1}, {2, 2}, {3, 1}, {4, 2}},
{{0, 2}, {1, 1}, {2, 2}, {3, 2}, {4, 1}},
{{0, 2}, {1, 1}, {2, 2}, {3, 2}, {4, 2}},
{{0, 2}, {1, 1}, {2, 2}, {3, 2}, {4, 3}},
{{0, 2}, {1, 1}, {2, 2}, {3, 3}, {4, 2}},
{{0, 2}, {1, 1}, {2, 2}, {3, 3}, {4, 3}},
{{0, 2}, {1, 1}, {2, 2}, {3, 3}, {4, 4}},
{{0, 2}, {1, 2}, {2, 1}, {3, 0}, {4, 0}},
{{0, 2}, {1, 2}, {2, 1}, {3, 0}, {4, 1}},
{{0, 2}, {1, 2}, {2, 1}, {3, 1}, {4, 0}},
{{0, 2}, {1, 2}, {2, 1}, {3, 1}, {4, 1}},
{{0, 2}, {1, 2}, {2, 1}, {3, 1}, {4, 2}},
{{0, 2}, {1, 2}, {2, 1}, {3, 2}, {4, 1}},
{{0, 2}, {1, 2}, {2, 1}, {3, 2}, {4, 2}},
{{0, 2}, {1, 2}, {2, 1}, {3, 2}, {4, 3}},
{{0, 2}, {1, 2}, {2, 2}, {3, 1}, {4, 0}},
{{0, 2}, {1, 2}, {2, 2}, {3, 1}, {4, 1}},
{{0, 2}, {1, 2}, {2, 2}, {3, 1}, {4, 2}},
{{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 1}},
{{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 2}},
{{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 3}},
{{0, 2}, {1, 2}, {2, 2}, {3, 3}, {4, 2}},
{{0, 2}, {1, 2}, {2, 2}, {3, 3}, {4, 3}},
{{0, 2}, {1, 2}, {2, 2}, {3, 3}, {4, 4}},
{{0, 2}, {1, 2}, {2, 3}, {3, 2}, {4, 1}},
{{0, 2}, {1, 2}, {2, 3}, {3, 2}, {4, 2}},
{{0, 2}, {1, 2}, {2, 3}, {3, 2}, {4, 3}},
{{0, 2}, {1, 2}, {2, 3}, {3, 3}, {4, 2}},
{{0, 2}, {1, 2}, {2, 3}, {3, 3}, {4, 3}},
{{0, 2}, {1, 2}, {2, 3}, {3, 3}, {4, 4}},
{{0, 2}, {1, 2}, {2, 3}, {3, 4}, {4, 3}},
{{0, 2}, {1, 2}, {2, 3}, {3, 4}, {4, 4}},
{{0, 2}, {1, 2}, {2, 3}, {3, 4}, {4, 5}},
{{0, 2}, {1, 3}, {2, 2}, {3, 1}, {4, 0}},
{{0, 2}, {1, 3}, {2, 2}, {3, 1}, {4, 1}},
{{0, 2}, {1, 3}, {2, 2}, {3, 1}, {4, 2}},
{{0, 2}, {1, 3}, {2, 2}, {3, 2}, {4, 1}},
{{0, 2}, {1, 3}, {2, 2}, {3, 2}, {4, 2}},
{{0, 2}, {1, 3}, {2, 2}, {3, 2}, {4, 3}},
{{0, 2}, {1, 3}, {2, 2}, {3, 3}, {4, 2}},
{{0, 2}, {1, 3}, {2, 2}, {3, 3}, {4, 3}},
{{0, 2}, {1, 3}, {2, 2}, {3, 3}, {4, 4}},
{{0, 2}, {1, 3}, {2, 3}, {3, 2}, {4, 1}},
{{0, 2}, {1, 3}, {2, 3}, {3, 2}, {4, 2}},
{{0, 2}, {1, 3}, {2, 3}, {3, 2}, {4, 3}},
{{0, 2}, {1, 3}, {2, 3}, {3, 3}, {4, 2}},
{{0, 2}, {1, 3}, {2, 3}, {3, 3}, {4, 3}},
{{0, 2}, {1, 3}, {2, 3}, {3, 3}, {4, 4}},
{{0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 3}},
{{0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 4}},
{{0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 5}},
{{0, 2}, {1, 3}, {2, 4}, {3, 3}, {4, 2}},
{{0, 2}, {1, 3}, {2, 4}, {3, 3}, {4, 3}},
{{0, 2}, {1, 3}, {2, 4}, {3, 3}, {4, 4}},
{{0, 2}, {1, 3}, {2, 4}, {3, 4}, {4, 3}},
{{0, 2}, {1, 3}, {2, 4}, {3, 4}, {4, 4}},
{{0, 2}, {1, 3}, {2, 4}, {3, 4}, {4, 5}},
{{0, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 4}},
{{0, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 5}},
{{0, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 6}},
{{0, 3}, {1, 2}, {2, 1}, {3, 0}, {4, 0}},
{{0, 3}, {1, 2}, {2, 1}, {3, 0}, {4, 1}},
{{0, 3}, {1, 2}, {2, 1}, {3, 1}, {4, 0}},
{{0, 3}, {1, 2}, {2, 1}, {3, 1}, {4, 1}},
{{0, 3}, {1, 2}, {2, 1}, {3, 1}, {4, 2}},
{{0, 3}, {1, 2}, {2, 1}, {3, 2}, {4, 1}},
{{0, 3}, {1, 2}, {2, 1}, {3, 2}, {4, 2}},
{{0, 3}, {1, 2}, {2, 1}, {3, 2}, {4, 3}},
{{0, 3}, {1, 2}, {2, 2}, {3, 1}, {4, 0}},
{{0, 3}, {1, 2}, {2, 2}, {3, 1}, {4, 1}},
{{0, 3}, {1, 2}, {2, 2}, {3, 1}, {4, 2}},
{{0, 3}, {1, 2}, {2, 2}, {3, 2}, {4, 1}},
{{0, 3}, {1, 2}, {2, 2}, {3, 2}, {4, 2}},
{{0, 3}, {1, 2}, {2, 2}, {3, 2}, {4, 3}},
{{0, 3}, {1, 2}, {2, 2}, {3, 3}, {4, 2}},
{{0, 3}, {1, 2}, {2, 2}, {3, 3}, {4, 3}},
{{0, 3}, {1, 2}, {2, 2}, {3, 3}, {4, 4}},
{{0, 3}, {1, 2}, {2, 3}, {3, 2}, {4, 1}},
{{0, 3}, {1, 2}, {2, 3}, {3, 2}, {4, 2}},
{{0, 3}, {1, 2}, {2, 3}, {3, 2}, {4, 3}},
{{0, 3}, {1, 2}, {2, 3}, {3, 3}, {4, 2}},
{{0, 3}, {1, 2}, {2, 3}, {3, 3}, {4, 3}},
{{0, 3}, {1, 2}, {2, 3}, {3, 3}, {4, 4}},
{{0, 3}, {1, 2}, {2, 3}, {3, 4}, {4, 3}},
{{0, 3}, {1, 2}, {2, 3}, {3, 4}, {4, 4}},
{{0, 3}, {1, 2}, {2, 3}, {3, 4}, {4, 5}},
{{0, 3}, {1, 3}, {2, 2}, {3, 1}, {4, 0}},
{{0, 3}, {1, 3}, {2, 2}, {3, 1}, {4, 1}},
{{0, 3}, {1, 3}, {2, 2}, {3, 1}, {4, 2}},
{{0, 3}, {1, 3}, {2, 2}, {3, 2}, {4, 1}},
{{0, 3}, {1, 3}, {2, 2}, {3, 2}, {4, 2}},
{{0, 3}, {1, 3}, {2, 2}, {3, 2}, {4, 3}},
{{0, 3}, {1, 3}, {2, 2}, {3, 3}, {4, 2}},
{{0, 3}, {1, 3}, {2, 2}, {3, 3}, {4, 3}},
{{0, 3}, {1, 3}, {2, 2}, {3, 3}, {4, 4}},
{{0, 3}, {1, 3}, {2, 3}, {3, 2}, {4, 1}},
{{0, 3}, {1, 3}, {2, 3}, {3, 2}, {4, 2}},
{{0, 3}, {1, 3}, {2, 3}, {3, 2}, {4, 3}},
{{0, 3}, {1, 3}, {2, 3}, {3, 3}, {4, 2}},
{{0, 3}, {1, 3}, {2, 3}, {3, 3}, {4, 3}},
{{0, 3}, {1, 3}, {2, 3}, {3, 3}, {4, 4}},
{{0, 3}, {1, 3}, {2, 3}, {3, 4}, {4, 3}},
{{0, 3}, {1, 3}, {2, 3}, {3, 4}, {4, 4}},
{{0, 3}, {1, 3}, {2, 3}, {3, 4}, {4, 5}},
{{0, 3}, {1, 3}, {2, 4}, {3, 3}, {4, 2}},
{{0, 3}, {1, 3}, {2, 4}, {3, 3}, {4, 3}},
{{0, 3}, {1, 3}, {2, 4}, {3, 3}, {4, 4}},
{{0, 3}, {1, 3}, {2, 4}, {3, 4}, {4, 3}},
{{0, 3}, {1, 3}, {2, 4}, {3, 4}, {4, 4}},
{{0, 3}, {1, 3}, {2, 4}, {3, 4}, {4, 5}},
{{0, 3}, {1, 3}, {2, 4}, {3, 5}, {4, 4}},
{{0, 3}, {1, 3}, {2, 4}, {3, 5}, {4, 5}},
{{0, 3}, {1, 3}, {2, 4}, {3, 5}, {4, 6}},
{{0, 3}, {1, 4}, {2, 3}, {3, 2}, {4, 1}},
{{0, 3}, {1, 4}, {2, 3}, {3, 2}, {4, 2}},
{{0, 3}, {1, 4}, {2, 3}, {3, 2}, {4, 3}},
{{0, 3}, {1, 4}, {2, 3}, {3, 3}, {4, 2}},
{{0, 3}, {1, 4}, {2, 3}, {3, 3}, {4, 3}},
{{0, 3}, {1, 4}, {2, 3}, {3, 3}, {4, 4}},
{{0, 3}, {1, 4}, {2, 3}, {3, 4}, {4, 3}},
{{0, 3}, {1, 4}, {2, 3}, {3, 4}, {4, 4}},
{{0, 3}, {1, 4}, {2, 3}, {3, 4}, {4, 5}},
{{0, 3}, {1, 4}, {2, 4}, {3, 3}, {4, 2}},
{{0, 3}, {1, 4}, {2, 4}, {3, 3}, {4, 3}},
{{0, 3}, {1, 4}, {2, 4}, {3, 3}, {4, 4}},
{{0, 3}, {1, 4}, {2, 4}, {3, 4}, {4, 3}},
{{0, 3}, {1, 4}, {2, 4}, {3, 4}, {4, 4}},
{{0, 3}, {1, 4}, {2, 4}, {3, 4}, {4, 5}},
{{0, 3}, {1, 4}, {2, 4}, {3, 5}, {4, 4}},
{{0, 3}, {1, 4}, {2, 4}, {3, 5}, {4, 5}},
{{0, 3}, {1, 4}, {2, 4}, {3, 5}, {4, 6}},
{{0, 3}, {1, 4}, {2, 5}, {3, 4}, {4, 3}},
{{0, 3}, {1, 4}, {2, 5}, {3, 4}, {4, 4}},
{{0, 3}, {1, 4}, {2, 5}, {3, 4}, {4, 5}},
{{0, 3}, {1, 4}, {2, 5}, {3, 5}, {4, 4}},
{{0, 3}, {1, 4}, {2, 5}, {3, 5}, {4, 5}},
{{0, 3}, {1, 4}, {2, 5}, {3, 5}, {4, 6}},
{{0, 3}, {1, 4}, {2, 5}, {3, 6}, {4, 5}},
{{0, 3}, {1, 4}, {2, 5}, {3, 6}, {4, 6}},
{{0, 4}, {1, 3}, {2, 2}, {3, 1}, {4, 0}},
{{0, 4}, {1, 3}, {2, 2}, {3, 1}, {4, 1}},
{{0, 4}, {1, 3}, {2, 2}, {3, 1}, {4, 2}},
{{0, 4}, {1, 3}, {2, 2}, {3, 2}, {4, 1}},
{{0, 4}, {1, 3}, {2, 2}, {3, 2}, {4, 2}},
{{0, 4}, {1, 3}, {2, 2}, {3, 2}, {4, 3}},
{{0, 4}, {1, 3}, {2, 2}, {3, 3}, {4, 2}},
{{0, 4}, {1, 3}, {2, 2}, {3, 3}, {4, 3}},
{{0, 4}, {1, 3}, {2, 2}, {3, 3}, {4, 4}},
{{0, 4}, {1, 3}, {2, 3}, {3, 2}, {4, 1}},
{{0, 4}, {1, 3}, {2, 3}, {3, 2}, {4, 2}},
{{0, 4}, {1, 3}, {2, 3}, {3, 2}, {4, 3}},
{{0, 4}, {1, 3}, {2, 3}, {3, 3}, {4, 2}},
{{0, 4}, {1, 3}, {2, 3}, {3, 3}, {4, 3}},
{{0, 4}, {1, 3}, {2, 3}, {3, 3}, {4, 4}},
{{0, 4}, {1, 3}, {2, 3}, {3, 4}, {4, 3}},
{{0, 4}, {1, 3}, {2, 3}, {3, 4}, {4, 4}},
{{0, 4}, {1, 3}, {2, 3}, {3, 4}, {4, 5}},
{{0, 4}, {1, 3}, {2, 4}, {3, 3}, {4, 2}},
{{0, 4}, {1, 3}, {2, 4}, {3, 3}, {4, 3}},
{{0, 4}, {1, 3}, {2, 4}, {3, 3}, {4, 4}},
{{0, 4}, {1, 3}, {2, 4}, {3, 4}, {4, 3}},
{{0, 4}, {1, 3}, {2, 4}, {3, 4}, {4, 4}},
{{0, 4}, {1, 3}, {2, 4}, {3, 4}, {4, 5}},
{{0, 4}, {1, 3}, {2, 4}, {3, 5}, {4, 4}},
{{0, 4}, {1, 3}, {2, 4}, {3, 5}, {4, 5}},
{{0, 4}, {1, 3}, {2, 4}, {3, 5}, {4, 6}},
{{0, 4}, {1, 4}, {2, 3}, {3, 2}, {4, 1}},
{{0, 4}, {1, 4}, {2, 3}, {3, 2}, {4, 2}},
{{0, 4}, {1, 4}, {2, 3}, {3, 2}, {4, 3}},
{{0, 4}, {1, 4}, {2, 3}, {3, 3}, {4, 2}},
{{0, 4}, {1, 4}, {2, 3}, {3, 3}, {4, 3}},
{{0, 4}, {1, 4}, {2, 3}, {3, 3}, {4, 4}},
{{0, 4}, {1, 4}, {2, 3}, {3, 4}, {4, 3}},
{{0, 4}, {1, 4}, {2, 3}, {3, 4}, {4, 4}},
{{0, 4}, {1, 4}, {2, 3}, {3, 4}, {4, 5}},
{{0, 4}, {1, 4}, {2, 4}, {3, 3}, {4, 2}},
{{0, 4}, {1, 4}, {2, 4}, {3, 3}, {4, 3}},
{{0, 4}, {1, 4}, {2, 4}, {3, 3}, {4, 4}},
{{0, 4}, {1, 4}, {2, 4}, {3, 4}, {4, 3}},
{{0, 4}, {1, 4}, {2, 4}, {3, 4}, {4, 4}},
{{0, 4}, {1, 4}, {2, 4}, {3, 4}, {4, 5}},
{{0, 4}, {1, 4}, {2, 4}, {3, 5}, {4, 4}},
{{0, 4}, {1, 4}, {2, 4}, {3, 5}, {4, 5}},
{{0, 4}, {1, 4}, {2, 4}, {3, 5}, {4, 6}},
{{0, 4}, {1, 4}, {2, 5}, {3, 4}, {4, 3}},
{{0, 4}, {1, 4}, {2, 5}, {3, 4}, {4, 4}},
{{0, 4}, {1, 4}, {2, 5}, {3, 4}, {4, 5}},
{{0, 4}, {1, 4}, {2, 5}, {3, 5}, {4, 4}},
{{0, 4}, {1, 4}, {2, 5}, {3, 5}, {4, 5}},
{{0, 4}, {1, 4}, {2, 5}, {3, 5}, {4, 6}},
{{0, 4}, {1, 4}, {2, 5}, {3, 6}, {4, 5}},
{{0, 4}, {1, 4}, {2, 5}, {3, 6}, {4, 6}},
{{0, 4}, {1, 5}, {2, 4}, {3, 3}, {4, 2}},
{{0, 4}, {1, 5}, {2, 4}, {3, 3}, {4, 3}},
{{0, 4}, {1, 5}, {2, 4}, {3, 3}, {4, 4}},
{{0, 4}, {1, 5}, {2, 4}, {3, 4}, {4, 3}},
{{0, 4}, {1, 5}, {2, 4}, {3, 4}, {4, 4}},
{{0, 4}, {1, 5}, {2, 4}, {3, 4}, {4, 5}},
{{0, 4}, {1, 5}, {2, 4}, {3, 5}, {4, 4}},
{{0, 4}, {1, 5}, {2, 4}, {3, 5}, {4, 5}},
{{0, 4}, {1, 5}, {2, 4}, {3, 5}, {4, 6}},
{{0, 4}, {1, 5}, {2, 5}, {3, 4}, {4, 3}},
{{0, 4}, {1, 5}, {2, 5}, {3, 4}, {4, 4}},
{{0, 4}, {1, 5}, {2, 5}, {3, 4}, {4, 5}},
{{0, 4}, {1, 5}, {2, 5}, {3, 5}, {4, 4}},
{{0, 4}, {1, 5}, {2, 5}, {3, 5}, {4, 5}},
{{0, 4}, {1, 5}, {2, 5}, {3, 5}, {4, 6}},
{{0, 4}, {1, 5}, {2, 5}, {3, 6}, {4, 5}},
{{0, 4}, {1, 5}, {2, 5}, {3, 6}, {4, 6}},
{{0, 4}, {1, 5}, {2, 6}, {3, 5}, {4, 4}},
{{0, 4}, {1, 5}, {2, 6}, {3, 5}, {4, 5}},
{{0, 4}, {1, 5}, {2, 6}, {3, 5}, {4, 6}},
{{0, 4}, {1, 5}, {2, 6}, {3, 6}, {4, 5}},
{{0, 4}, {1, 5}, {2, 6}, {3, 6}, {4, 6}},
{{0, 5}, {1, 4}, {2, 3}, {3, 2}, {4, 1}},
{{0, 5}, {1, 4}, {2, 3}, {3, 2}, {4, 2}},
{{0, 5}, {1, 4}, {2, 3}, {3, 2}, {4, 3}},
{{0, 5}, {1, 4}, {2, 3}, {3, 3}, {4, 2}},
{{0, 5}, {1, 4}, {2, 3}, {3, 3}, {4, 3}},
{{0, 5}, {1, 4}, {2, 3}, {3, 3}, {4, 4}},
{{0, 5}, {1, 4}, {2, 3}, {3, 4}, {4, 3}},
{{0, 5}, {1, 4}, {2, 3}, {3, 4}, {4, 4}},
{{0, 5}, {1, 4}, {2, 3}, {3, 4}, {4, 5}},
{{0, 5}, {1, 4}, {2, 4}, {3, 3}, {4, 2}},
{{0, 5}, {1, 4}, {2, 4}, {3, 3}, {4, 3}},
{{0, 5}, {1, 4}, {2, 4}, {3, 3}, {4, 4}},
{{0, 5}, {1, 4}, {2, 4}, {3, 4}, {4, 3}},
{{0, 5}, {1, 4}, {2, 4}, {3, 4}, {4, 4}},
{{0, 5}, {1, 4}, {2, 4}, {3, 4}, {4, 5}},
{{0, 5}, {1, 4}, {2, 4}, {3, 5}, {4, 4}},
{{0, 5}, {1, 4}, {2, 4}, {3, 5}, {4, 5}},
{{0, 5}, {1, 4}, {2, 4}, {3, 5}, {4, 6}},
{{0, 5}, {1, 4}, {2, 5}, {3, 4}, {4, 3}},
{{0, 5}, {1, 4}, {2, 5}, {3, 4}, {4, 4}},
{{0, 5}, {1, 4}, {2, 5}, {3, 4}, {4, 5}},
{{0, 5}, {1, 4}, {2, 5}, {3, 5}, {4, 4}},
{{0, 5}, {1, 4}, {2, 5}, {3, 5}, {4, 5}},
{{0, 5}, {1, 4}, {2, 5}, {3, 5}, {4, 6}},
{{0, 5}, {1, 4}, {2, 5}, {3, 6}, {4, 5}},
{{0, 5}, {1, 4}, {2, 5}, {3, 6}, {4, 6}},
{{0, 5}, {1, 5}, {2, 4}, {3, 3}, {4, 2}},
{{0, 5}, {1, 5}, {2, 4}, {3, 3}, {4, 3}},
{{0, 5}, {1, 5}, {2, 4}, {3, 3}, {4, 4}},
{{0, 5}, {1, 5}, {2, 4}, {3, 4}, {4, 3}},
{{0, 5}, {1, 5}, {2, 4}, {3, 4}, {4, 4}},
{{0, 5}, {1, 5}, {2, 4}, {3, 4}, {4, 5}},
{{0, 5}, {1, 5}, {2, 4}, {3, 5}, {4, 4}},
{{0, 5}, {1, 5}, {2, 4}, {3, 5}, {4, 5}},
{{0, 5}, {1, 5}, {2, 4}, {3, 5}, {4, 6}},
{{0, 5}, {1, 5}, {2, 5}, {3, 4}, {4, 3}},
{{0, 5}, {1, 5}, {2, 5}, {3, 4}, {4, 4}},
{{0, 5}, {1, 5}, {2, 5}, {3, 4}, {4, 5}},
{{0, 5}, {1, 5}, {2, 5}, {3, 5}, {4, 4}},
{{0, 5}, {1, 5}, {2, 5}, {3, 5}, {4, 5}},
{{0, 5}, {1, 5}, {2, 5}, {3, 5}, {4, 6}},
{{0, 5}, {1, 5}, {2, 5}, {3, 6}, {4, 5}},
{{0, 5}, {1, 5}, {2, 5}, {3, 6}, {4, 6}},
{{0, 5}, {1, 5}, {2, 6}, {3, 5}, {4, 4}},
{{0, 5}, {1, 5}, {2, 6}, {3, 5}, {4, 5}},
{{0, 5}, {1, 5}, {2, 6}, {3, 5}, {4, 6}},
{{0, 5}, {1, 5}, {2, 6}, {3, 6}, {4, 5}},
{{0, 5}, {1, 5}, {2, 6}, {3, 6}, {4, 6}},
{{0, 5}, {1, 6}, {2, 5}, {3, 4}, {4, 3}},
{{0, 5}, {1, 6}, {2, 5}, {3, 4}, {4, 4}},
{{0, 5}, {1, 6}, {2, 5}, {3, 4}, {4, 5}},
{{0, 5}, {1, 6}, {2, 5}, {3, 5}, {4, 4}},
{{0, 5}, {1, 6}, {2, 5}, {3, 5}, {4, 5}},
{{0, 5}, {1, 6}, {2, 5}, {3, 5}, {4, 6}},
{{0, 5}, {1, 6}, {2, 5}, {3, 6}, {4, 5}},
{{0, 5}, {1, 6}, {2, 5}, {3, 6}, {4, 6}},
{{0, 5}, {1, 6}, {2, 6}, {3, 5}, {4, 4}},
{{0, 5}, {1, 6}, {2, 6}, {3, 5}, {4, 5}},
{{0, 5}, {1, 6}, {2, 6}, {3, 5}, {4, 6}},
{{0, 5}, {1, 6}, {2, 6}, {3, 6}, {4, 5}},
{{0, 5}, {1, 6}, {2, 6}, {3, 6}, {4, 6}},
{{0, 6}, {1, 5}, {2, 4}, {3, 3}, {4, 2}},
{{0, 6}, {1, 5}, {2, 4}, {3, 3}, {4, 3}},
{{0, 6}, {1, 5}, {2, 4}, {3, 3}, {4, 4}},
{{0, 6}, {1, 5}, {2, 4}, {3, 4}, {4, 3}},
{{0, 6}, {1, 5}, {2, 4}, {3, 4}, {4, 4}},
{{0, 6}, {1, 5}, {2, 4}, {3, 4}, {4, 5}},
{{0, 6}, {1, 5}, {2, 4}, {3, 5}, {4, 4}},
{{0, 6}, {1, 5}, {2, 4}, {3, 5}, {4, 5}},
{{0, 6}, {1, 5}, {2, 4}, {3, 5}, {4, 6}},
{{0, 6}, {1, 5}, {2, 5}, {3, 4}, {4, 3}},
{{0, 6}, {1, 5}, {2, 5}, {3, 4}, {4, 4}},
{{0, 6}, {1, 5}, {2, 5}, {3, 4}, {4, 5}},
{{0, 6}, {1, 5}, {2, 5}, {3, 5}, {4, 4}},
{{0, 6}, {1, 5}, {2, 5}, {3, 5}, {4, 5}},
{{0, 6}, {1, 5}, {2, 5}, {3, 5}, {4, 6}},
{{0, 6}, {1, 5}, {2, 5}, {3, 6}, {4, 5}},
{{0, 6}, {1, 5}, {2, 5}, {3, 6}, {4, 6}},
{{0, 6}, {1, 5}, {2, 6}, {3, 5}, {4, 4}},
{{0, 6}, {1, 5}, {2, 6}, {3, 5}, {4, 5}},
{{0, 6}, {1, 5}, {2, 6}, {3, 5}, {4, 6}},
{{0, 6}, {1, 5}, {2, 6}, {3, 6}, {4, 5}},
{{0, 6}, {1, 5}, {2, 6}, {3, 6}, {4, 6}},
{{0, 6}, {1, 6}, {2, 5}, {3, 4}, {4, 3}},
{{0, 6}, {1, 6}, {2, 5}, {3, 4}, {4, 4}},
{{0, 6}, {1, 6}, {2, 5}, {3, 4}, {4, 5}},
{{0, 6}, {1, 6}, {2, 5}, {3, 5}, {4, 4}},
{{0, 6}, {1, 6}, {2, 5}, {3, 5}, {4, 5}},
{{0, 6}, {1, 6}, {2, 5}, {3, 5}, {4, 6}},
{{0, 6}, {1, 6}, {2, 5}, {3, 6}, {4, 5}},
{{0, 6}, {1, 6}, {2, 5}, {3, 6}, {4, 6}},
{{0, 6}, {1, 6}, {2, 6}, {3, 5}, {4, 4}},
{{0, 6}, {1, 6}, {2, 6}, {3, 5}, {4, 5}},
{{0, 6}, {1, 6}, {2, 6}, {3, 5}, {4, 6}},
{{0, 6}, {1, 6}, {2, 6}, {3, 6}, {4, 5}},
{{0, 6}, {1, 6}, {2, 6}, {3, 6}, {4, 6}}
};

vector<vector<pair<int, int>>> winningLines = { // defines the winning lines (178)
	{{0, 0}, {1, 0}, {2, 0}, {3, 0}, {4, 0}, },
	{{0, 0}, {1, 0}, {2, 0}, {3, 0}, {4, 1}, },
	{{0, 0}, {1, 0}, {2, 0}, {3, 1}, {4, 0}, },
	{{0, 0}, {1, 0}, {2, 0}, {3, 1}, {4, 1}, },
	{{0, 0}, {1, 0}, {2, 0}, {3, 1}, {4, 2}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 0}, {1, 0}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 0}, {1, 1}, {2, 0}, {3, 0}, {4, 0}, },
	{{0, 0}, {1, 1}, {2, 0}, {3, 0}, {4, 1}, },
	{{0, 0}, {1, 1}, {2, 0}, {3, 1}, {4, 0}, },
	{{0, 0}, {1, 1}, {2, 0}, {3, 1}, {4, 1}, },
	{{0, 0}, {1, 1}, {2, 0}, {3, 1}, {4, 2}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 0}, {1, 1}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 0}, {1, 1}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 1}, {1, 0}, {2, 0}, {3, 0}, {4, 0}, },
	{{0, 1}, {1, 0}, {2, 0}, {3, 0}, {4, 1}, },
	{{0, 1}, {1, 0}, {2, 0}, {3, 1}, {4, 0}, },
	{{0, 1}, {1, 0}, {2, 0}, {3, 1}, {4, 1}, },
	{{0, 1}, {1, 0}, {2, 0}, {3, 1}, {4, 2}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 1}, {1, 0}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 1}, {1, 1}, {2, 0}, {3, 0}, {4, 0}, },
	{{0, 1}, {1, 1}, {2, 0}, {3, 0}, {4, 1}, },
	{{0, 1}, {1, 1}, {2, 0}, {3, 1}, {4, 0}, },
	{{0, 1}, {1, 1}, {2, 0}, {3, 1}, {4, 1}, },
	{{0, 1}, {1, 1}, {2, 0}, {3, 1}, {4, 2}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 1}, {1, 1}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 1}, {1, 1}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 1}, {1, 2}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 1}, {1, 2}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 1}, {1, 2}, {2, 3}, {3, 2}, {4, 1}, },
	{{0, 1}, {1, 2}, {2, 3}, {3, 2}, {4, 2}, },
	{{0, 1}, {1, 2}, {2, 3}, {3, 2}, {4, 3}, },
	{{0, 1}, {1, 2}, {2, 3}, {3, 3}, {4, 2}, },
	{{0, 1}, {1, 2}, {2, 3}, {3, 3}, {4, 3}, },
	{{0, 2}, {1, 1}, {2, 0}, {3, 0}, {4, 0}, },
	{{0, 2}, {1, 1}, {2, 0}, {3, 0}, {4, 1}, },
	{{0, 2}, {1, 1}, {2, 0}, {3, 1}, {4, 0}, },
	{{0, 2}, {1, 1}, {2, 0}, {3, 1}, {4, 1}, },
	{{0, 2}, {1, 1}, {2, 0}, {3, 1}, {4, 2}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 2}, {1, 1}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 2}, {1, 1}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 2}, {1, 2}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 2}, {1, 2}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 2}, {1, 2}, {2, 3}, {3, 2}, {4, 1}, },
	{{0, 2}, {1, 2}, {2, 3}, {3, 2}, {4, 2}, },
	{{0, 2}, {1, 2}, {2, 3}, {3, 2}, {4, 3}, },
	{{0, 2}, {1, 2}, {2, 3}, {3, 3}, {4, 2}, },
	{{0, 2}, {1, 2}, {2, 3}, {3, 3}, {4, 3}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 2}, {1, 3}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 2}, {1, 3}, {2, 3}, {3, 2}, {4, 1}, },
	{{0, 2}, {1, 3}, {2, 3}, {3, 2}, {4, 2}, },
	{{0, 2}, {1, 3}, {2, 3}, {3, 2}, {4, 3}, },
	{{0, 2}, {1, 3}, {2, 3}, {3, 3}, {4, 2}, },
	{{0, 2}, {1, 3}, {2, 3}, {3, 3}, {4, 3}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 0}, {4, 0}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 0}, {4, 1}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 1}, {4, 0}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 1}, {4, 1}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 1}, {4, 2}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 2}, {4, 1}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 2}, {4, 2}, },
	{{0, 3}, {1, 2}, {2, 1}, {3, 2}, {4, 3}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 3}, {1, 2}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 3}, {1, 2}, {2, 3}, {3, 2}, {4, 1}, },
	{{0, 3}, {1, 2}, {2, 3}, {3, 2}, {4, 2}, },
	{{0, 3}, {1, 2}, {2, 3}, {3, 2}, {4, 3}, },
	{{0, 3}, {1, 2}, {2, 3}, {3, 3}, {4, 2}, },
	{{0, 3}, {1, 2}, {2, 3}, {3, 3}, {4, 3}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 1}, {4, 0}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 1}, {4, 1}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 1}, {4, 2}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 2}, {4, 1}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 2}, {4, 2}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 2}, {4, 3}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 3}, {4, 2}, },
	{{0, 3}, {1, 3}, {2, 2}, {3, 3}, {4, 3}, },
	{{0, 3}, {1, 3}, {2, 3}, {3, 2}, {4, 1}, },
	{{0, 3}, {1, 3}, {2, 3}, {3, 2}, {4, 2}, },
	{{0, 3}, {1, 3}, {2, 3}, {3, 2}, {4, 3}, },
	{{0, 3}, {1, 3}, {2, 3}, {3, 3}, {4, 2}, },
	{{0, 3}, {1, 3}, {2, 3}, {3, 3}, {4, 3}, }
};

int reelWcount(int a, vector<vector<string>>& grid, string sym){
	int count = 0;
	for (int j = 0; j < grid[a].size(); j++) {
        const string& cell = grid[a][j];

		if (cell == sym ) { // at most 2 spaces away (relevant for vis > 4)
            count++;
		}
	}
	return count;
}

vector<vector<string>> generateGrid(vector<vector<string>> reels1, vector<vector<string>> reels2, vector<vector<string>> reels3, vector<vector<string>> reelsref, int ROW_COUNT) { //draws stop positions, chooses reel options individually and returns playing field
    vector<vector<string>> grid(REEL_COUNT, vector<string>(ROW_COUNT));
    for (int i = 0; i < REEL_COUNT; i++) {
        int randomreels = rand() % 3;
        int randomIndex = rand() % reelsref[i].size();
        if (randomreels < 1) { //choose first option for reel j
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels1[i][(randomIndex + j) % reelsref[i].size()];
            }
        } else if (randomreels < 2) { //choose second option for reel j
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels2[i][(randomIndex + j) % reelsref[i].size()];
            }
        } else { //choose third option for reel j
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels3[i][(randomIndex + j) % reelsref[i].size()];
            }

        }
    }
    return grid;
}

pair <vector<vector<string>>, vector<int>> generateGridInfo(vector<vector<string>> reels1, vector<vector<string>> reels2, vector<vector<string>> reels3, vector<vector<string>> reelsref, int ROW_COUNT) { //draws stop positions, chooses reel options individually and returns playing field
    vector<vector<string>> grid(REEL_COUNT, vector<string>(ROW_COUNT));
	vector<int> stopinfo(2 * REEL_COUNT + 1);
    for (int i = 0; i < REEL_COUNT; i++) {
		int randomreels = rand() % 3; stopinfo[i] = randomreels;
		int randomIndex = rand() % reelsref[i].size(); stopinfo[5+i] = randomIndex;
        if (randomreels < 1) { //choose first option for reel j
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels1[i][(randomIndex + j) % reelsref[i].size()];
            }
        } else if (randomreels < 2) { //choose second option for reel j
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels2[i][(randomIndex + j) % reelsref[i].size()];
            }
        } else { //choose third option for reel j
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels3[i][(randomIndex + j) % reelsref[i].size()];
            }

        }
    }
    return {grid, stopinfo};
}

vector<vector<string>> shiftedGrid(int buffer, vector<int> info, vector<vector<string>> reels1, vector<vector<string>> reels2, vector<vector<string>> reels3, vector<vector<string>> reelsref, int ROW_COUNT,
int step, int stoppedreels, int stepsNextStop, unordered_set<reelMod> MOD, int longspinOffset=0 ) {
    vector<vector<string>> grid(5, vector<string>(ROW_COUNT));

	int shiftPos[5];

	int offset = 2;

	shiftPos[4] = 5 * stepsNextStop - (step + stepsNextStop * stoppedreels) + offset + buffer + longspinOffset;

	for (int p = 0; p < 4; p++){
		if ( stoppedreels >= p+1 ){ shiftPos[p] = 0 + offset + buffer; } // reel has stopped, duh
		else {
			shiftPos[p] = stepsNextStop * (p+1) - (step + stepsNextStop * stoppedreels) + buffer + offset;
		}
	}

	int unrandomreels;
	int unrandomIndex;
    for (int i = 0; i < 5; i++) {

        unrandomreels = info[i];
        unrandomIndex = info[i+5] + shiftPos[i] % reelsref[i].size();
        if (unrandomreels < 1) {
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels1[i][(unrandomIndex + j) % reelsref[i].size()];
            }
        } else if (unrandomreels < 2) {
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels2[i][(unrandomIndex + j) % reelsref[i].size()];
            }
        } else {
            for (int j = 0; j < ROW_COUNT; j++) {
                grid[i][j] = reels3[i][(unrandomIndex + j) % reelsref[i].size()];
            }

        }
    }

    for (const auto& change : MOD) {
        if (change.reel < stoppedreels){
            grid[change.reel][change.pos] = change.symbol;
        } else if (shiftPos[change.reel] <= change.pos) {
            grid[change.reel][change.pos - shiftPos[change.reel]] = change.symbol;
        }
    }

    return grid;
}

void printGrid(const vector<vector<string>>& grid, int ROW_COUNT, bool game = true) {
    int m = 1; // For row formatting

    cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

    for (int row = 0; row < ROW_COUNT; ++row) {
        cout << "          │ ";
        for (int col = 0; col < REEL_COUNT; ++col) {
            // Translate symbols and handle color
            string symbol = grid[col][row];
            string translatedSymbol = symbolTranslator.count(symbol) > 0
                                      ? symbolTranslator[symbol]
                                      : symbol; // Fallback to original if not found
            // Apply color
            setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox); // Set color based on symbol
            cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
        }

        if (m < ROW_COUNT && game) {
            cout << endl << "          │      │      │      │      │      │" << endl;
        } else {
            cout << endl;
        }
        m++;
    }

    cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;
}

void winWait(int length){
    if (length==3)
    {
        if (animate == 0)
        #ifdef _WIN32
            Sleep( 91 );
        #else
            usleep( 91 * 1000 );
        #endif
        else if (animate == 1)
        #ifdef _WIN32
            Sleep( 152 );
        #else
            usleep( 152 * 1000 );
        #endif
        else
        #ifdef _WIN32
            Sleep( 333 );
        #else
            usleep( 333 * 1000 );
        #endif
    }
    else if (length==4)
    {
        if (animate == 0)
        #ifdef _WIN32
            Sleep( 171 );
        #else
            usleep( 171 * 1000 );
        #endif
        else if (animate == 1)
        #ifdef _WIN32
            Sleep( 284 );
        #else
            usleep( 284 * 1000 );
        #endif
        else
        #ifdef _WIN32
            Sleep( 710 );
        #else
            usleep( 710 * 1000 );
        #endif
    }
    else if (length==5)
    {
        if (animate == 0)
        #ifdef _WIN32
            Sleep( 277 );
        #else
            usleep( 277 * 1000 );
        #endif
        else if (animate == 1)
        #ifdef _WIN32
            Sleep( 510 );
        #else
            usleep( 510 * 1000 );
        #endif
        else
        #ifdef _WIN32
            Sleep( 1275 );
        #else
            usleep( 1275 * 1000 );
        #endif
    }
}

struct WinInfo {
    vector<pair<int, int>> line;
    int length;

    // Needed to allow use in set
    bool operator<(const WinInfo& other) const {
        return line < other.line || (line == other.line && length < other.length);
    }
};

struct WinsByLength {
    set<WinInfo> wins3;
    set<WinInfo> wins4;
    set<WinInfo> wins5;
};

WinsByLength collectWinsByLength(const vector<vector<string>>& grid, const vector<vector<pair<int, int>>>& winningLines) {
    WinsByLength result;

    for (const auto& line : winningLines) {
        string firstSymbol = grid[line[0].first][line[0].second];
        if (firstSymbol.empty() || firstSymbol == "0") continue;

        int wildWin = 0;
        int substitutedWin = 0;
        int wldCount = 0;
        int matchCount = 0;
        string substitutedSymbol = firstSymbol;
        bool foundNonWild = false;

        // Wild win
        if (firstSymbol == "WLD") {
            wldCount = 1;
            for (size_t i = 1; i < line.size(); ++i) {
                string currentSymbol = grid[line[i].first][line[i].second];
                if (currentSymbol == "WLD") {
                    wldCount++;
                } else {
                    break;
                }
            }
        }

        // Substituted win
        for (size_t i = 0; i < line.size(); ++i) {
            string currentSymbol = grid[line[i].first][line[i].second];

            if (currentSymbol == "WLD") {
                matchCount++;
            } else if (!foundNonWild) {
                substitutedSymbol = currentSymbol;
                foundNonWild = true;
                matchCount++;
            } else if (currentSymbol == substitutedSymbol) {
                matchCount++;
            } else {
                break;
            }
        }

        // Determine best match length
        int effectiveLength = 0;
        if (wldCount >= 3) {
            effectiveLength = wldCount;
        }
        if (matchCount >= 3 && matchCount > effectiveLength) {
            effectiveLength = matchCount;
        }

        // Store if it's a valid win
        if (effectiveLength >= 3) {
            WinInfo winInfo{line, effectiveLength};

            switch (effectiveLength) {
                case 3: result.wins3.insert(winInfo); break;
                case 4: result.wins4.insert(winInfo); break;
                case 5: result.wins5.insert(winInfo); break;
                default: break; // Ignore wins longer than 5
            }
        }
    }

    return result;
}


int calculateWins(const vector<vector<string>>& grid, bool test_mode, map<string, int>& totalWinCounts, int betFactor, vector<vector<pair<int, int>>> winningLines,bool print) { // line win detection handling substituted- and direct wild wins individually
    int totalWin = 0;

    // store win counts
    std::map<std::string, int> winCounts;

    if (test_mode) {
        winCounts.clear();  // clear win counts before each spin in test mode
    }

    // iterate over all winning lines
    for (const auto& line : winningLines) {
        string firstSymbol = grid[line[0].first][line[0].second];
        if (firstSymbol.empty()) { continue;}

        int wildWin = 0;
        int substitutedWin = 0;

        std::string wildDescription;
        std::string substitutedDescription;
        std::string substitutedSymbol = firstSymbol;  // track substituted symbol

        // part 1: wild win detection (at least 3 consecutive wilds from the left)
        if (firstSymbol == "WLD") {
            int wldCount = 1;

            // count consecutive wilds
            for (size_t i = 1; i < line.size(); ++i) {
                string currentSymbol = grid[line[i].first][line[i].second];
                if (currentSymbol == "WLD") {
                    wldCount++;
                } else {
                    break;
                }
            }

            if (wldCount >= 3) { // 3 symbols are minimally required for a wild win on any line
                wildWin = winTable["WLD"][wldCount - 3];
                wildDescription = std::to_string(wldCount) + "×" + symbolTranslator["WLD"];
            }
        }

        // part 2: substituted win detection (treat wilds as matching)
        int matchCount = 0;
        bool foundNonWild = false;

        // count matching symbols, treat wilds as matching, replace them with first non-wild
        for (size_t i = 0; i < line.size(); ++i) {
            string currentSymbol = grid[line[i].first][line[i].second];

            // if current symbol is wild, treat it as match and continue
            if (currentSymbol == "WLD") {
                matchCount++;
            } else if (currentSymbol != "WLD" && !foundNonWild) {
                // set substituted symbol
                substitutedSymbol = currentSymbol;
                foundNonWild = true;
                matchCount++;  // count first non-wild as part of the match
            } else if (currentSymbol == substitutedSymbol) {
                // if current symbol matches substituted symbol, count it
                matchCount++;
            } else {
                break; // stop if there is a non-match
            }
        }

        if (matchCount >= 3 && foundNonWild) { // 3 symbols are minimally required for a win on any line
            substitutedWin = winTable[substitutedSymbol][matchCount - 3];
            // translate substituted symbol using the translator
            substitutedDescription = std::to_string(matchCount) + "×" + symbolTranslator[substitutedSymbol];
        }

        // compare wild- and substituted win
        int lineWin = std::max(wildWin, substitutedWin);

		totalWin += lineWin * betFactor;

        if (lineWin > 0 && print) {

            std::string description = (wildWin >= substitutedWin) ? wildDescription : substitutedDescription;

            winCounts[description]++;

            totalWinCounts[description]++;
        }
    }

    // in test mode print current spin's win counts
    if (test_mode && print) {
        int t = 0;
        cout << "    ";
        for (const auto& entry : winCounts) {
            if (t == 3) {
                t = 0;
                cout << endl << "    ";
            }
            t++;
            // translate win description
            string translatedDescription = entry.first;
            for (const auto& trans : symbolTranslator) {
                size_t pos = translatedDescription.find(trans.first);
                while (pos != string::npos) {
                    translatedDescription.replace(pos, trans.first.length(), trans.second);
                    pos = translatedDescription.find(trans.first, pos + trans.second.length());
                }
            }
            if (entry.second < 10) { cout << " "; }
            cout << entry.second;
            cout << " time";
            if (entry.second > 1) { cout << "s "; }
            else { cout << "  "; }
            cout << translatedDescription << "  ";
        }
    }

    return totalWin;
}

vector<vector<bool>> generateWinMask(const WinInfo& win, int reelCount, int rowCount) {
    vector<vector<bool>> mask(reelCount, vector<bool>(rowCount, false));

    for (const auto& pos : win.line) {
        int col = pos.first;
        int row = pos.second;
        if (col >= 0 && col < reelCount && row >= 0 && row < rowCount) {
            mask[col][row] = true;
        }
    }
    return mask;
}

void winAnimationBG(vector<vector<string>>& grid, int ROW_COUNT, const map<string, vector<int>>& winTable,
int betFactor, bool fg, bool x7, bool loanShark, int lgames, bool simple, int points, vector<int> info, bool rSet, int wait, int longspin){

auto winResults = collectWinsByLength(grid, winningLines);
    if (!winResults.wins3.empty() || !winResults.wins4.empty() || !winResults.wins5.empty())
    {
    #ifdef _WIN32
        Sleep( wait );
    #else
        usleep( wait * 1000 );
    #endif
    cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10) <<  "       ┌────────────────────────────────────────┐ 178WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
				<< setw(9) << winTable.at("WLD")[0] * betFactor
				<< setw(9) << winTable.at("WLD")[1] * betFactor
				<< setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
				cout << setw(9) << winTable.at("HV1")[0] * betFactor
				<< setw(9) << winTable.at("HV1")[1] * betFactor
				<< setw(9) << winTable.at("HV1")[2] * betFactor
				<< "│ ";if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
				<< setw(9) << winTable.at("HV2")[1] * betFactor
				<< setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
				cout << "       │  " << setw(10) << "  2-9      "
				<< setw(9) << winTable.at("LV1")[0] * betFactor
				<< setw(9) << winTable.at("LV1")[1] * betFactor
				<< setw(9) << winTable.at("LV1")[2] * betFactor
				<< "│ "<< endl;
				cout << "       │                                        │ "; cout << endl;
				cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
				<< " │  "; cout << endl;
				cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
				<< " │  ";
				if (loanShark){
				cout << "game";
				}
				cout << endl;
				cout << "       └────────────────────────────────────────┘  ";
				if (loanShark){
					cout << lgames;
				}
				cout << endl;
                if (!loanShark){
                    cout << "              C A R D   S H A R K   M E G A " << endl;
                } else {
                    cout << "              L O A N   S H A R K   M E G A " << endl;
                }

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
                    setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::setw(7) << std::left << "        credit: " <<
				std::setw(8) << points << "                  ? :win";
				cout << endl << endl << endl;
        #ifdef _WIN32
            Sleep( wait * 2 + 300 );
        #else
            usleep( wait * 2 + 300000 );
        #endif
    }

    for (const auto& win : winResults.wins3) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10) <<  "       ┌────────────────────────────────────────┐ 178WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
				<< setw(9) << winTable.at("WLD")[0] * betFactor
				<< setw(9) << winTable.at("WLD")[1] * betFactor
				<< setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
				cout << setw(9) << winTable.at("HV1")[0] * betFactor
				<< setw(9) << winTable.at("HV1")[1] * betFactor
				<< setw(9) << winTable.at("HV1")[2] * betFactor
				<< "│ ";if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
				<< setw(9) << winTable.at("HV2")[1] * betFactor
				<< setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
				cout << "       │  " << setw(10) << "  2-9      "
				<< setw(9) << winTable.at("LV1")[0] * betFactor
				<< setw(9) << winTable.at("LV1")[1] * betFactor
				<< setw(9) << winTable.at("LV1")[2] * betFactor
				<< "│ "<< endl;
				cout << "       │                                        │ "; cout << endl;
				cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
				<< " │  "; cout << endl;
				cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
				<< " │  ";
				if (loanShark){
				cout << "game";
				}
				cout << endl;
				cout << "       └────────────────────────────────────────┘  ";
				if (loanShark){
					cout << lgames;
				}
				cout << endl;
                if (!loanShark){
                    cout << "              C A R D   S H A R K   M E G A " << endl;
                } else {
                    cout << "              L O A N   S H A R K   M E G A " << endl;
                }

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        if (col<3)
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                        else
                        setTextColor("WI", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::setw(7) << std::left << "        credit: " <<
				std::setw(8) << points << "                  ? :win";
				cout << endl << endl << endl;
                winWait(3);
    }
    for (const auto& win : winResults.wins4) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10) <<  "       ┌────────────────────────────────────────┐ 178WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
				<< setw(9) << winTable.at("WLD")[0] * betFactor
				<< setw(9) << winTable.at("WLD")[1] * betFactor
				<< setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
				cout << setw(9) << winTable.at("HV1")[0] * betFactor
				<< setw(9) << winTable.at("HV1")[1] * betFactor
				<< setw(9) << winTable.at("HV1")[2] * betFactor
				<< "│ ";if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
				<< setw(9) << winTable.at("HV2")[1] * betFactor
				<< setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
				cout << "       │  " << setw(10) << "  2-9      "
				<< setw(9) << winTable.at("LV1")[0] * betFactor
				<< setw(9) << winTable.at("LV1")[1] * betFactor
				<< setw(9) << winTable.at("LV1")[2] * betFactor
				<< "│ "<< endl;
				cout << "       │                                        │ "; cout << endl;
				cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
				<< " │  "; cout << endl;
				cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
				<< " │  ";
				if (loanShark){
				cout << "game";
				}
				cout << endl;
				cout << "       └────────────────────────────────────────┘  ";
				if (loanShark){
					cout << lgames;
				}
				cout << endl;
                if (!loanShark){
                    cout << "              C A R D   S H A R K   M E G A " << endl;
                } else {
                    cout << "              L O A N   S H A R K   M E G A " << endl;
                }

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
                    if (winMask[col][row]) {
                        if (col<4)
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                        else
                        setTextColor("WI", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::setw(7) << std::left << "        credit: " <<
				std::setw(8) << points << "                  ? :win";
				cout << endl << endl << endl;
                winWait(4);
    }
    for (const auto& win : winResults.wins5) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10) <<  "       ┌────────────────────────────────────────┐ 178WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
				<< setw(9) << winTable.at("WLD")[0] * betFactor
				<< setw(9) << winTable.at("WLD")[1] * betFactor
				<< setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
				cout << setw(9) << winTable.at("HV1")[0] * betFactor
				<< setw(9) << winTable.at("HV1")[1] * betFactor
				<< setw(9) << winTable.at("HV1")[2] * betFactor
				<< "│ ";if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
				<< setw(9) << winTable.at("HV2")[1] * betFactor
				<< setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
				cout << "       │  " << setw(10) << "  2-9      "
				<< setw(9) << winTable.at("LV1")[0] * betFactor
				<< setw(9) << winTable.at("LV1")[1] * betFactor
				<< setw(9) << winTable.at("LV1")[2] * betFactor
				<< "│ "<< endl;
				cout << "       │                                        │ "; cout << endl;
				cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
				<< " │  "; cout << endl;
				cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
				<< " │  ";
				if (loanShark){
				cout << "game";
				}
				cout << endl;
				cout << "       └────────────────────────────────────────┘  ";
				if (loanShark){
					cout << lgames;
				}
				cout << endl;
                if (!loanShark){
                    cout << "              C A R D   S H A R K   M E G A " << endl;
                } else {
                    cout << "              L O A N   S H A R K   M E G A " << endl;
                }

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::setw(7) << std::left << "        credit: " <<
				std::setw(8) << points << "                  ? :win";
				cout << endl << endl << endl;
                winWait(5);
    }
}

void winAnimationTANK(vector<vector<string>>& grid, vector<vector<int>>& fgrid, int ROW_COUNT, const map<string, vector<int>>& winTable,
int betFactor, bool loanShark, bool simple, int wait, int longspin, int markedSpots, int multiplier, int totalWin, int risk){

auto winResults = collectWinsByLength(grid, winningLines);
    if (!winResults.wins3.empty() || !winResults.wins4.empty() || !winResults.wins5.empty())
    {
    #ifdef _WIN32
        Sleep( wait );
    #else
        usleep( wait * 1000 );
    #endif
    cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl<< endl<< endl;

				int u = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
				for (const auto& row : fgrid) {
				cout << "          │";
					for (int cell : row) {
						if ( cell == 1 ) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "  $$  ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
						else if ( cell == 0) {
							cout << "      │";
						}
						else if ( cell == 3) {
							setTextColor("xx", DEFAULT_COLOR, FAT_UI, HVbox);
							if (!simple) {cout << "   x  ";}
							else         {cout << "  x   ";}
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "│";
						}
						else if ( cell == 2) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << " [$$] ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
					}
					if (u < 4) {
						cout << endl << "          │      │      │      │      │      │";
						u++;
					}
					cout << '\n';
				}
				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;


				cout << "      S  ──────────────────────────────────────  T" << endl;
				cout << "      H   [$$] reached:   " << std:: right<< std::setw(2)<< markedSpots
				<< "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
				cout << "      A   current win:     ?                     N" <<endl;
				cout << "      R   win sum:  " << std::right << std::setw(8) << totalWin;
				if (risk == 0)      {cout <<   "    [normal mode]    K" << endl;}
				else if (risk == 1) {cout <<   "    [risk mode]      K" << endl;}
				else                {cout <<   "    [shark mode]     K" << endl;}
				cout << "      K  ──────────────────────────────────────  !" << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << endl << endl<< endl;
        #ifdef _WIN32
            Sleep( wait * 2 + 300 );
        #else
            usleep( wait * 2 + 300000 );
        #endif
    }

    for (const auto& win : winResults.wins3) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl<< endl<< endl;

				int u = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
				for (const auto& row : fgrid) {
				cout << "          │";
					for (int cell : row) {
						if ( cell == 1 ) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "  $$  ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
						else if ( cell == 0) {
							cout << "      │";
						}
						else if ( cell == 3) {
							setTextColor("xx", DEFAULT_COLOR, FAT_UI, HVbox);
							if (!simple) {cout << "   x  ";}
							else         {cout << "  x   ";}
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "│";
						}
						else if ( cell == 2) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << " [$$] ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
					}
					if (u < 4) {
						cout << endl << "          │      │      │      │      │      │";
						u++;
					}
					cout << '\n';
				}
				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;


				cout << "      S  ──────────────────────────────────────  T" << endl;
				cout << "      H   [$$] reached:   " << std:: right<< std::setw(2)<< markedSpots
				<< "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
				cout << "      A   current win:     ?                     N" <<endl;
				cout << "      R   win sum:  " << std::right << std::setw(8) << totalWin;
				if (risk == 0)      {cout <<   "    [normal mode]    K" << endl;}
				else if (risk == 1) {cout <<   "    [risk mode]      K" << endl;}
				else                {cout <<   "    [shark mode]     K" << endl;}
				cout << "      K  ──────────────────────────────────────  !" << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        if (col<3)
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                        else
                        setTextColor("WI", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << endl << endl<< endl;
                winWait(3);
    }
    for (const auto& win : winResults.wins4) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl<< endl<< endl;

				int u = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
				for (const auto& row : fgrid) {
				cout << "          │";
					for (int cell : row) {
						if ( cell == 1 ) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "  $$  ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
						else if ( cell == 0) {
							cout << "      │";
						}
						else if ( cell == 3) {
							setTextColor("xx", DEFAULT_COLOR, FAT_UI, HVbox);
							if (!simple) {cout << "   x  ";}
							else         {cout << "  x   ";}
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "│";
						}
						else if ( cell == 2) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << " [$$] ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
					}
					if (u < 4) {
						cout << endl << "          │      │      │      │      │      │";
						u++;
					}
					cout << '\n';
				}
				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;


				cout << "      S  ──────────────────────────────────────  T" << endl;
				cout << "      H   [$$] reached:   " << std:: right<< std::setw(2)<< markedSpots
				<< "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
				cout << "      A   current win:     ?                     N" <<endl;
				cout << "      R   win sum:  " << std::right << std::setw(8) << totalWin;
				if (risk == 0)      {cout <<   "    [normal mode]    K" << endl;}
				else if (risk == 1) {cout <<   "    [risk mode]      K" << endl;}
				else                {cout <<   "    [shark mode]     K" << endl;}
				cout << "      K  ──────────────────────────────────────  !" << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        if (col<4)
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                        else
                        setTextColor("WI", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << endl << endl<< endl;
                winWait(4);
    }
    for (const auto& win : winResults.wins5) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl<< endl<< endl;

				int u = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
				for (const auto& row : fgrid) {
				cout << "          │";
					for (int cell : row) {
						if ( cell == 1 ) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "  $$  ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
						else if ( cell == 0) {
							cout << "      │";
						}
						else if ( cell == 3) {
							setTextColor("xx", DEFAULT_COLOR, FAT_UI, HVbox);
							if (!simple) {cout << "   x  ";}
							else         {cout << "  x   ";}
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "│";
						}
						else if ( cell == 2) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << " [$$] ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
					}
					if (u < 4) {
						cout << endl << "          │      │      │      │      │      │";
						u++;
					}
					cout << '\n';
				}
				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;


				cout << "      S  ──────────────────────────────────────  T" << endl;
				cout << "      H   [$$] reached:   " << std:: right<< std::setw(2)<< markedSpots
				<< "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
				cout << "      A   current win:     ?                     N" <<endl;
				cout << "      R   win sum:  " << std::right << std::setw(8) << totalWin;
				if (risk == 0)      {cout <<   "    [normal mode]    K" << endl;}
				else if (risk == 1) {cout <<   "    [risk mode]      K" << endl;}
				else                {cout <<   "    [shark mode]     K" << endl;}
				cout << "      K  ──────────────────────────────────────  !" << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << endl << endl<< endl;
                winWait(5);
    }
}

void winAnimationMEGA(vector<vector<string>>& grid, int ROW_COUNT, const map<string, vector<int>>& winTable,
int betFactor, bool loanShark, bool simple, int wait, int longspin, int spins, int totalWin){ // TANK really doesn't need any animation at least...

auto winResults = collectWinsByLength(grid, winningLines7);
    if (!winResults.wins3.empty() || !winResults.wins4.empty() || !winResults.wins5.empty())
    {
        #ifdef _WIN32
            Sleep( wait + 350 );
        #else
            usleep( wait + 350000 );
        #endif
    }

    for (const auto& win : winResults.wins3) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
				<< endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10)  << "       ┌────────────────────────────────────────┐ 421WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
					<< setw(9) << winTable.at("WLD")[0] * betFactor
					<< setw(9) << winTable.at("WLD")[1] * betFactor
					<< setw(9) << winTable.at("WLD")[2] * betFactor << "│"; if (spins != -1) {cout << " spins";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
					cout << setw(9) << winTable.at("HV1")[0] * betFactor
					<< setw(9) << winTable.at("HV1")[1] * betFactor
					<< setw(9) << winTable.at("HV1")[2] * betFactor
					<< "│"; if (spins != -1) {cout << " left";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
					<< setw(9) << winTable.at("HV2")[1] * betFactor
					<< setw(9) << winTable.at("HV2")[2] * betFactor << "│  "; if (spins != -1) {cout << setw(2) << spins;} cout << endl;
				cout << "       │  " << setw(10) << "  2-9      "
					<< setw(9) << winTable.at("LV1")[0] * betFactor
					<< setw(9) << winTable.at("LV1")[1] * betFactor
					<< setw(9) << winTable.at("LV1")[2] * betFactor
					<< "│ ";
					cout << endl;
				cout << "       └────────────────────────────────────────┘";

				cout << endl;

				cout << "               M  E  G  A   R  E  E  L  S   " << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        if (col<3)
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                        else
                        setTextColor("WI", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::left << "        total win: " <<
				std::setw(8) << totalWin << "               ? :win";
				cout << endl << endl << endl;
                winWait(3);
    }
    for (const auto& win : winResults.wins4) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
				<< endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10)  << "       ┌────────────────────────────────────────┐ 421WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
					<< setw(9) << winTable.at("WLD")[0] * betFactor
					<< setw(9) << winTable.at("WLD")[1] * betFactor
					<< setw(9) << winTable.at("WLD")[2] * betFactor << "│"; if (spins != -1) {cout << " spins";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
					cout << setw(9) << winTable.at("HV1")[0] * betFactor
					<< setw(9) << winTable.at("HV1")[1] * betFactor
					<< setw(9) << winTable.at("HV1")[2] * betFactor
					<< "│"; if (spins != -1) {cout << " left";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
					<< setw(9) << winTable.at("HV2")[1] * betFactor
					<< setw(9) << winTable.at("HV2")[2] * betFactor << "│  "; if (spins != -1) {cout << setw(2) << spins;} cout << endl;
				cout << "       │  " << setw(10) << "  2-9      "
					<< setw(9) << winTable.at("LV1")[0] * betFactor
					<< setw(9) << winTable.at("LV1")[1] * betFactor
					<< setw(9) << winTable.at("LV1")[2] * betFactor
					<< "│ ";
					cout << endl;
				cout << "       └────────────────────────────────────────┘";

				cout << endl;

				cout << "               M  E  G  A   R  E  E  L  S   " << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        if (col<3)
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                        else
                        setTextColor("WI", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::left << "        total win: " <<
				std::setw(8) << totalWin << "               ? :win";
				cout << endl << endl << endl;
                winWait(4);
    }
    for (const auto& win : winResults.wins5) {
        vector<vector<bool>> winMask = generateWinMask(win, REEL_COUNT, ROW_COUNT);
        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
				<< endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10)  << "       ┌────────────────────────────────────────┐ 421WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
					<< setw(9) << winTable.at("WLD")[0] * betFactor
					<< setw(9) << winTable.at("WLD")[1] * betFactor
					<< setw(9) << winTable.at("WLD")[2] * betFactor << "│"; if (spins != -1) {cout << " spins";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
					cout << setw(9) << winTable.at("HV1")[0] * betFactor
					<< setw(9) << winTable.at("HV1")[1] * betFactor
					<< setw(9) << winTable.at("HV1")[2] * betFactor
					<< "│"; if (spins != -1) {cout << " left";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
					<< setw(9) << winTable.at("HV2")[1] * betFactor
					<< setw(9) << winTable.at("HV2")[2] * betFactor << "│  "; if (spins != -1) {cout << setw(2) << spins;} cout << endl;
				cout << "       │  " << setw(10) << "  2-9      "
					<< setw(9) << winTable.at("LV1")[0] * betFactor
					<< setw(9) << winTable.at("LV1")[1] * betFactor
					<< setw(9) << winTable.at("LV1")[2] * betFactor
					<< "│ ";
					cout << endl;
				cout << "       └────────────────────────────────────────┘";

				cout << endl;

				cout << "               M  E  G  A   R  E  E  L  S   " << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					if (winMask[col][row]) {
                        setTextColor("WIN", DEFAULT_COLOR, FAT_UI, HVbox);  // highlight
                    } else {
                        setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
                    }
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::left << "        total win: " <<
				std::setw(8) << totalWin << "               ? :win";
				cout << endl << endl << endl;
                winWait(5);
    }
}


std::tuple<int, vector<pair<int, int>>, bool> calculateWinsFG(const vector<vector<string>>& grid, bool test_mode, int betFactor, bool print) { // adapted win detection for the feature

    int totalWin = 0;
    bool accept = false;

    std::map<std::string, int> winCounts;
    vector<pair<int, int>> longestLine;  // store the geometry of the longest winning line
    int longestMatchCount = 0;  // track the length of the longest match

    if (test_mode) {
        winCounts.clear();  // clear win counts before the start of each spin in test mode
    }

    for (const auto& line : winningLines) {
        string firstSymbol = grid[line[0].first][line[0].second];
        if (firstSymbol.empty()) continue;

        int substitutedWin = 0;  // no wild wins in FG
        std::string substitutedDescription;

        int matchCount = 0;
        vector<pair<int, int>> currentLine;  // to store the current line of matching symbols

        // save time in the case "0"
        if (firstSymbol != "0") {
            string currentSymbol = firstSymbol;
            matchCount++;
            currentLine.push_back(line[0]);  // start a try to obtain a new longest line

            // check subsequent symbols for matches
            for (size_t i = 1; i < line.size(); ++i) {
                string currentSymbolAtPos = grid[line[i].first][line[i].second];

                if (currentSymbolAtPos == "WLD") {
                    matchCount++;
                    currentLine.push_back(line[i]);
                } else if (currentSymbolAtPos == currentSymbol) {
                    matchCount++;
                    currentLine.push_back(line[i]);
                } else {
                    break; // no match
                }
            }

            // if there is one, calculate the win
            if (matchCount >= 3) {
                substitutedWin = winTable[currentSymbol][matchCount - 3];
                substitutedDescription = std::to_string(matchCount) + "×" + currentSymbol;
            }

            if (substitutedWin > 0) {
                totalWin += substitutedWin * betFactor;
                winCounts[substitutedDescription]++;

                if (matchCount > longestMatchCount) { // longer line might have been found
                    longestMatchCount = matchCount;
                    longestLine = currentLine; // if the previously longest line is replaced the new line contains all entries of the old one as well
                }
            }
        }
    }

    if (test_mode) {
        int accepting = rand() % 200;
        if (accepting >= 197 || totalWin > 0) { accept = true;}
    }

    if (test_mode && accept && print)
    {
        cout << endl<< endl<< endl<< endl<< endl << "    ";
        for (const auto& entry : winCounts) {
            std::string translatedDescription = entry.first;

            for (const auto& trans : symbolTranslator) {
                size_t pos = translatedDescription.find(trans.first);
                while (pos != string::npos) {
                    translatedDescription.replace(pos, trans.first.length(), trans.second);
                    pos = translatedDescription.find(trans.first, pos + trans.second.length());
                }
            }

            if (entry.second < 10) { cout << " "; }
            cout << entry.second;
            cout << " time"; if (entry.second > 1) { cout << "s "; } else { cout << "  "; }
            cout << translatedDescription << "  ";
        }
    }

    return {totalWin, longestLine, accept};
}


bool checkTRG(const vector<vector<string>>& grid) { // determines whether feature is triggered
    int trgCount = 0;

    // iterate over the 20 visible symbols
    for (size_t row = 0; row < grid.size(); ++row) {
        for (size_t col = 0; col < grid[row].size(); ++col) {
            if (grid[row][col] == "TRG") {
                trgCount++;
            }
            if (trgCount >= 2) { // only whether a trigger occurs is relevant
                return true;
            }
        }
    }
    return false;
}

bool check7(const vector<vector<string>>& grid) { // determines whether feature is triggered
    int trgCount = 0;

    // iterate over the 20 visible symbols
    for (size_t row = 0; row < grid.size(); ++row) {
        for (size_t col = 0; col < grid[row].size(); ++col) {
            if (grid[row][col] == "X7X") {
                trgCount++;
            }
            if (trgCount >= 2) { // only whether a trigger occurs is relevant
                return true;
            }
        }
    }
    return false;
}


int nearWin(const vector<vector<string>>& grid,const vector<vector<pair<int, int>>>& winningLines,const vector<string>& HVsymbols) {

    std::set<string> hvSet(HVsymbols.begin(), HVsymbols.end());
    int hvLineCount = 0;

    for (const auto& line : winningLines) {
        string firstSymbol = grid[line[0].first][line[0].second];

        // Check for at least 4 consecutive wilds from the left
        if (firstSymbol == "WLD") {
            int wldCount = 1;
            for (size_t i = 1; i < line.size(); ++i) {
                if (grid[line[i].first][line[i].second] == "WLD") {
                    wldCount++;
                } else {
                    break;
                }
            }
            if (wldCount >= 4) {
                return 3;
            }
        }

        // HV match with wilds substitution
        int matchCount = 0;
        bool foundHV = false;
        string targetSymbol;

        for (size_t i = 0; i < line.size(); ++i) {
            string current = grid[line[i].first][line[i].second];

            if (current == "WLD") {
                matchCount++;
            } else if (!foundHV) {
                if (hvSet.count(current)) {
                    targetSymbol = current;
                    foundHV = true;
                    matchCount++;
                } else {
                    break;  // not a high-value symbol — skip this line
                }
            } else if (current == targetSymbol) {
                matchCount++;
            } else {
                break;
            }
        }

        if (foundHV && (matchCount == 4 || matchCount == 5)) {
            hvLineCount++;
        }
    }

    if (hvLineCount > 0) return (2 + hvLineCount*10);

    for (size_t row = 0; row < 4; ++row) { // possible trigger
        if (grid[3][row] == "TRG" || grid[3][row] == "X7X")
            return 1;
    }

    return -1;  // neither condition met
}

tuple<int, string> countHVSymbols(const vector<vector<string>>& grid) { //return HV that appears most often after quantity
    int count; int maxc = 0;

	string curmaxHV = "HV1";

    // Count occurrences of "HVx" symbols
	for (const auto& HV : HVsymbols){
		count = 0;
		for (const auto& reel : grid) {
			for (const auto& symbol : reel) {
				if (symbol == HV) {
					count++;
				}
				if (count > maxc) {
					curmaxHV = symbol;
					maxc = count;
				}
			}
		}
	}

    return {maxc, curmaxHV};
}

void printFGrid(const vector<vector<int>>& grid, int fwin, bool play=true) { // prints overview of already marked positions during feature

    int u = 1;

    cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
    for (const auto& row : grid) {
        cout << "          │";
        for (int cell : row) {
            if ( cell == 1 ) {
                setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
                cout << "  $$  ";
                setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
                cout <<"│";
            }
            else if ( cell == 0) {
                cout << "      │";
            }
			else if ( cell == 3) {
                setTextColor("xx", DEFAULT_COLOR, FAT_UI, HVbox);
				if (!simple) {cout << "   x  ";}
				else         {cout << "  x   ";}
				setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
				cout << "│";
			}
            else if ( cell == 2) {
                setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
                cout << " [$$] ";
                setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
                cout <<"│";
            }
        }
        if (u < 4 && play) {
            cout << endl << "          │      │      │      │      │      │";
            u++;
        }
        cout << '\n';
    }
    cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;
}

bool isTouching(int row1, int row2) { // this was used to generate all connected lines that are relevant here
    return abs(row1 - row2) <= 1;
}

cosInfo addCosmetic( int a, int b, vector<vector<string>>& grid, int betFactor, int reels, int vis, vector<vector<pair<int, int>>>& winningLines, string sym) {

    cosInfo results = { 0, grid, -1, -1, sym};

    // Copy the original grid to work on
    vector<vector<string>> gridW(grid.size(), vector<string>(grid[0].size()));
	for (int i = 0; i<reels; i++) {
        for (int j = 0; j<vis; j++) {
			gridW[i][j] = grid[i][j];
		}
	}

	int newWin = 0;
	int Win = 0;

    if ((grid[a][b] != "TRG" && grid[a][b] != "X7X" && grid[a][b] != "WLD" && grid[a][b] != sym) && ( vis < 6 || reelWcount(a, grid, sym) < 6)) {

        map<string, int> cosmeticWinCounts;
        Win = calculateWins(grid, false, cosmeticWinCounts, betFactor, winningLines, false);

        gridW[a][b] = sym;  // modify the copy (possibly only) temporarily

        newWin = calculateWins(gridW, false, cosmeticWinCounts, betFactor, winningLines, false);

        //  O N L Y  E V E R  return gridW if the win amount remains the same, the description is redone as it could change, but the win amount never does
        if (newWin == Win) {
            results.screen = gridW;
            results.reel = a;
            results.pos = b;
        }
    }

    return results;  // else change nothing
}

int changeBet(int betFactor, int points, bool forw, bool loanShark, int lgames, bool simple) { // cycles through bet factors and prints a placeholder playing field
    if (forw){
        if (betFactor == 1) {
            betFactor = 2;
        } else if (betFactor == 2) {
            betFactor = 3;
        } else if (betFactor == 3) {
            betFactor = 4;
        } else if (betFactor == 4) {
            betFactor = 5;
        } else if (betFactor == 5) {
            betFactor = 7;
        } else if (betFactor == 7) {
            betFactor = 10;
        } else if (betFactor == 10) {
            betFactor = 11;
        } else if (betFactor == 11) {
            betFactor = 15;
        } else if (betFactor == 15) {
            betFactor = 20;
        } else if (betFactor == 20) {
            betFactor = 25;
        } else if (betFactor == 25) {
            betFactor = 50;
        } else if (betFactor == 50) {
            betFactor = 70;
        } else if (betFactor == 70) {
            betFactor = 100;
        } else if (betFactor == 100) {
            betFactor = 1;
        }
    } else {
        if (betFactor == 70) {
            betFactor = 50;
        } else if (betFactor == 50) {
            betFactor = 25;
        } else if (betFactor == 25) {
            betFactor = 20;
        } else if (betFactor == 20) {
            betFactor = 15;
        } else if (betFactor == 15) {
            betFactor = 11;
        } else if (betFactor == 11) {
            betFactor = 10;
        } else if (betFactor == 10) {
            betFactor = 7;
        } else if (betFactor == 7) {
            betFactor = 5;
        } else if (betFactor == 5) {
            betFactor = 4;
        } else if (betFactor == 4) {
            betFactor = 3;
        } else if (betFactor == 3) {
            betFactor = 2;
        } else if (betFactor == 2) {
            betFactor = 1;
        } else if (betFactor == 1) {
            betFactor = 100;
        } else if (betFactor == 100) {
            betFactor = 70;
        }
    }

    cout << endl << endl<< endl << endl<< endl << endl<< endl << endl<< endl << endl<< endl << endl<< endl << endl<< endl << endl;
    print(winTable, betFactor, false, false, loanShark, lgames, simple);
	if (loanShark) {
			cout << "              L O A N   S H A R K   M E G A \n";
			} else {
            cout << "              C A R D   S H A R K   M E G A \n";
			}
    cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
    cout << "          │      │       /\\    │      │      │" << endl;
    cout << "          │      │      /  \\   │      │      │" << endl;
    cout << "          │      │     /,  ,\\         │      │" << endl;
    cout << "          │      │    /      \\        │      │" << endl;
    cout << "          │      │   / ______ \\       │      │" << endl;
    cout << "          │      │  / /wVvVwV\\ \\      │      │" << endl;
    cout << "          │      │  | \\ (()) / |      │      │" << endl;
    cout << "          └──────┴──┘  ^^^^^^  └──────┴──────┘" << endl;
    cout << "        credit: " << points << endl;

    cout << endl << "      press SPACE to continue" << endl;
    if (simple) {cout << endl;}
    return betFactor;
}

bool isValidPosition(int a, int b, const vector<vector<string>>& grid, const string& symbol) {

    bool symbolFound = false;
	string test ="";
    int numReels = grid.size(); // Number of vertical reels
    bool first = true;

    vector<pair<int, int>> symbolPositions; // Store positions of `symbol`

        for (int j = 0; j < grid[a].size(); j++) {
            const string& cell = grid[a][j];

            if (cell == symbol && abs(b-j) <= 3 ) { // at most 2 spaces away (relevant for vis > 4)
                symbolFound = true;
            }

			if (j >= 2 ) { // at most 2 spaces away (relevant for vis > 4)
				if( (grid[a][j-1] == "TRG" && grid[a][j-2] == cell ) || (grid[a][j-1] == "X7X" && grid[a][j-2] == cell ) ) {
					return false;
				}
            } else if ( j <= grid[a].size()-3 ) { // at most 2 spaces away (relevant for vis > 4)
				if( (grid[a][j+1] == "TRG" && grid[a][j+2] == cell ) || (grid[a][j+1] == "X7X" && grid[a][j+2] == cell ) ) {
					return false;
				}
            }

            // Invalid conditions
            if (cell.size() == 3 && cell.substr(0, 2) == "HV" && cell[2] >= '1' && cell[2] <= '5' && cell != symbol) {
				if (first || cell == test) { // check: max. one other HV
					first = false;
					test = cell;
					if (j == b-1 || j == b || j == b+1) { return false; } // check: one space before any other HV
				} else {
					return false; // Found an invalid symbol
				}
			}
		}

		if (!symbolFound ) {
			return false; // Invalid if no `symbol` or invalid symbol present
		}

    return true; // No valid nearby symbol found
}

pair <vector<vector<string>>, reelMod> attemptAddWild(vector<vector<string>> reels, int betFactor){

    reelMod mod = {-1,-1,"WLD"};

    int random = rand() % 100;

    if (random < 52){
        int initialWin = std::get<0>(calculateWinsFG(reels, false, betFactor,false));
        random = rand() % 2;
        bool reelEmpty = true;
        int chosen;

        if (random == 0){
            chosen = 3; // consider reel 4(-1)
            for (int e = 0; e < ROW_COUNT; e++){
                if (reels[3][e] == "WLD") { reelEmpty = false; }
            }
        } else {
            chosen = 4;
            for (int e = 0; e < ROW_COUNT; e++){
                if (reels[3][e] == "WLD") { reelEmpty = false; }
            }
        }

        if (reelEmpty){
            vector<vector<string>> reelsCos(REEL_COUNT, vector<string>(ROW_COUNT));
            for (int reel = 0; reel < REEL_COUNT; reel++){
                for (int pos = 0; pos < ROW_COUNT; pos++){
                    reelsCos[reel][pos] = reels[reel][pos];
                }
            }
            random = rand() % 4;
            reelsCos[chosen][random] = "WLD";
            int cosWin = std::get<0>(calculateWinsFG(reelsCos, false, betFactor, false));

            if (cosWin == initialWin){
                mod.reel = chosen;
                mod.pos = random;
                return {reelsCos, mod};
            }
        }
    }

    return {reels, mod};

}


void spinReelsBG( vector<vector<string>>& grid, int ROW_COUNT, const map<string, vector<int>>& winTable,
int betFactor, bool fg, bool x7, bool loanShark, int lgames, bool simple, int points, vector<int> info, bool rSet, int wait, unordered_set<reelMod> MOD, int longspin)
{
    vector<vector<string>> Ogrid = grid;
    double slower = 1.0;
    double fact = 1.13;
    int longspinOffset = 0;

    if (longspin != -1) // just a bookmark ! ! ! ! ! ! !
    {
        if (longspin == 1)           longspinOffset =  9 + rand() %   7;
        else if (longspin % 10 == 2) longspinOffset = 10 + rand() % std::min(static_cast<int>(6 + ((longspin-2)*0.06)), 17);
        else if (longspin == 3)      longspinOffset = 19 + rand() %  12;
    }

	int stepsNextStop = 7;

	bool first = true;
    int firstWave = -1; // IMPORTANT: for the spinning animation to make sence always ensure buffer >(=) visiblePos - firstWave

    int buffer = ROW_COUNT - firstWave + 1;
	buffer += rand() % 7;

	for (int stoppedreels = 0; stoppedreels < 5; stoppedreels++){
		for (int step = 0; step < stepsNextStop; step++){
			do {

				if (buffer > 0) {buffer--; }
				if (!first){
			#ifdef _WIN32
				Sleep(wait );  // Windows (milliseconds)
			#else
				usleep( wait * 1000 ); // Linux/Mac (microseconds, so 1000 means 1ms)
			#endif
				} else {
					first = false;
				}

				if (rSet){	grid = shiftedGrid(buffer-2, info, reels1, reels2, reels3, reels1, ROW_COUNT, step, stoppedreels, stepsNextStop, MOD, longspinOffset ); }
				else {	grid = shiftedGrid(buffer-2, info, reels4, reels5, reels6, reels4, ROW_COUNT, step, stoppedreels, stepsNextStop, MOD, longspinOffset ); }

                for (int i = std::max(0,firstWave); i < ROW_COUNT ; i++){
                    for (int j = 0; j < 5; j++){
                        grid[j][i] = "    ";
                    }
                }

				cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10) <<  "       ┌────────────────────────────────────────┐ 178WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
				<< setw(9) << winTable.at("WLD")[0] * betFactor
				<< setw(9) << winTable.at("WLD")[1] * betFactor
				<< setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
				cout << setw(9) << winTable.at("HV1")[0] * betFactor
				<< setw(9) << winTable.at("HV1")[1] * betFactor
				<< setw(9) << winTable.at("HV1")[2] * betFactor
				<< "│ ";if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
				<< setw(9) << winTable.at("HV2")[1] * betFactor
				<< setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
				cout << "       │  " << setw(10) << "  2-9      "
				<< setw(9) << winTable.at("LV1")[0] * betFactor
				<< setw(9) << winTable.at("LV1")[1] * betFactor
				<< setw(9) << winTable.at("LV1")[2] * betFactor
				<< "│ "<< endl;
				cout << "       │                                        │ "; cout << endl;
				cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
				<< " │  "; cout << endl;
				cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
				<< " │  ";
				if (loanShark){
				cout << "game";
				}
				cout << endl;
				cout << "       └────────────────────────────────────────┘  ";
				if (loanShark){
					cout << lgames;
				}
				cout << endl;
                if (!loanShark){
                    cout << "              C A R D   S H A R K   M E G A " << endl;
                } else {
                    cout << "              L O A N   S H A R K   M E G A " << endl;
                }

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::setw(7) << std::left << "        credit: " <<
				std::setw(8) << points << "                  ? :win";
				cout << endl << endl << endl;
				if (simple ) {cout << endl;}

				firstWave++;
			} while ( buffer > 0 );
		}
	}

	while ( longspinOffset > 0 )
    {
        fact = std::max(0.99*fact, 1.02);
        slower = std::min( fact*slower, 2.22);
        #ifdef _WIN32
			Sleep(wait *slower);  // Windows (milliseconds)
		#else
			usleep( wait * 1000 *slower); // Linux/Mac (microseconds, 1000 <-> 1ms)
		#endif

		if (rSet){	grid = shiftedGrid(buffer-2, info, reels1, reels2, reels3, reels1, ROW_COUNT, stepsNextStop, 4, stepsNextStop, MOD, longspinOffset ); }
        else {	grid = shiftedGrid(buffer-2, info, reels4, reels5, reels6, reels4, ROW_COUNT, stepsNextStop, 4, stepsNextStop, MOD, longspinOffset ); }
			cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

			cout << left << setw(10) <<  "       ┌────────────────────────────────────────┐ 178WL" << endl;
			cout <<                      "       │             ×3       ×4       ×5       │" << endl;
			cout << "       │  " << setw(10) << " W7LD      "
			<< setw(9) << winTable.at("WLD")[0] * betFactor
			<< setw(9) << winTable.at("WLD")[1] * betFactor
			<< setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
			cout << "       │  ";
			if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
			cout << setw(9) << winTable.at("HV1")[0] * betFactor
				<< setw(9) << winTable.at("HV1")[1] * betFactor
				<< setw(9) << winTable.at("HV1")[2] * betFactor
				<< "│ ";if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
				<< setw(9) << winTable.at("HV2")[1] * betFactor
				<< setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
				cout << "       │  " << setw(10) << "  2-9      "
				<< setw(9) << winTable.at("LV1")[0] * betFactor
				<< setw(9) << winTable.at("LV1")[1] * betFactor
				<< setw(9) << winTable.at("LV1")[2] * betFactor
				<< "│ "<< endl;
				cout << "       │                                        │ "; cout << endl;
				cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
				<< " │  "; cout << endl;
				cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
				<< " │  ";
				if (loanShark){
				cout << "game";
				}
				cout << endl;
				cout << "       └────────────────────────────────────────┘  ";
				if (loanShark){
					cout << lgames;
				}
				cout << endl;
                if (!loanShark){
                    cout << "              C A R D   S H A R K   M E G A " << endl;
                } else {
                    cout << "              L O A N   S H A R K   M E G A " << endl;
                }

        int m = 1;

        cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

        for (int row = 0; row < ROW_COUNT; ++row) {
            cout << "          │ ";
            for (int col = 0; col < REEL_COUNT; ++col) {
            string symbol = grid[col][row];
            string translatedSymbol = symbolTranslator.count(symbol) > 0
                                ? symbolTranslator[symbol]
                                : symbol;
            setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
            cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
        }

        if (m < ROW_COUNT) {
            cout << endl << "          │      │      │      │      │      │" << endl;
        } else {
            cout << endl;
        }
        m++;
        }

        cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
        cout << std::setw(7) << std::left << "        credit: " <<
        std::setw(8) << points << "                  ? :win";
        cout << endl << endl << endl;
        if (simple ) {cout << endl;}
        longspinOffset--;
    }

	#ifdef _WIN32
		Sleep(wait * 0.9*slower);  // Windows (milliseconds)
    #else
		usleep( wait * 1000 * 0.9*slower); // Linux/Mac (microseconds, so 1000 means 1ms)
    #endif
    if (animate != -1) winAnimationBG( Ogrid, ROW_COUNT, winTable, betFactor, fg,  x7, loanShark, lgames, simple, points, info, rSet, wait, longspin);
	cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl ;
}

void spinReelsMEGA( vector<vector<string>>& grid, int ROW_COUNT, const map<string, vector<int>>& winTable,
int betFactor, bool loanShark, bool simple, vector<int> info, bool rSet, int wait, int totalWin, int risk, int spins, unordered_set<reelMod> MOD, int multiplier)
{

	int stepsNextStop = 7;

	bool first = true;
    int firstWave = -1;

    int buffer = 7 - firstWave + 1; // adapted formula with ROW_COUNT = 7
	buffer += rand() % 7;

    double tempo = 1;
    if (multiplier == 1){
        tempo = 0.75;
    } else if ( multiplier == 2) {
        tempo = 0.95;
    } else if ( multiplier == 3) {
        tempo = 1.2;
    } else if ( multiplier == 4) {
        tempo = 1.45;
    } else if ( multiplier == 5) {
        tempo = 1.7;
    }

	for (int stoppedreels = 0; stoppedreels < 5; stoppedreels++){
		for (int step = 0; step < stepsNextStop; step++){
			do {
				if (buffer > 0) {buffer--; }
				if (!first){
                #ifdef _WIN32
				if (risk == 0){
					Sleep(wait * tempo);  // Windows (milliseconds)
				} else if ( risk == 1) {
					Sleep(wait * tempo);  // Windows (milliseconds)
				} else {
					Sleep(wait * tempo);  // Windows (milliseconds)
				}
                #else
				if (risk == 0){
					usleep( wait * 1000 * tempo); // Linux/Mac (microseconds, so 1000 means 1ms)
				} else if ( risk == 1) {
					usleep( wait * 1000 * tempo); // Linux/Mac (microseconds, so 1000 means 1ms)
				} else {
					usleep( wait * 1000 * tempo); // Linux/Mac (microseconds, so 1000 means 1ms)
				}
                #endif
				} else {
					first = false;
				}

				if (rSet){	grid = shiftedGrid(buffer-2, info, reels7, reels8, reels9, reels7, 7, step, stoppedreels, stepsNextStop, MOD ); }
				else {	grid = shiftedGrid(buffer-2, info, reels10, reels11, reels12, reels10, 7, step, stoppedreels, stepsNextStop, MOD ); }

                for (int i = std::max(0,firstWave); i < 7 ; i++){
                    for (int j = 0; j < 5; j++){
                        grid[j][i] = "    ";
                    }
                }

				cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
				<< endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10)  << "       ┌────────────────────────────────────────┐ 421WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
					<< setw(9) << winTable.at("WLD")[0] * betFactor
					<< setw(9) << winTable.at("WLD")[1] * betFactor
					<< setw(9) << winTable.at("WLD")[2] * betFactor << "│"; if (spins != -1) {cout << " spins";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
					cout << setw(9) << winTable.at("HV1")[0] * betFactor
					<< setw(9) << winTable.at("HV1")[1] * betFactor
					<< setw(9) << winTable.at("HV1")[2] * betFactor
					<< "│"; if (spins != -1) {cout << " left";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
					<< setw(9) << winTable.at("HV2")[1] * betFactor
					<< setw(9) << winTable.at("HV2")[2] * betFactor << "│  "; if (spins != -1) {cout << setw(2) << spins;} cout << endl;
				cout << "       │  " << setw(10) << "  2-9      "
					<< setw(9) << winTable.at("LV1")[0] * betFactor
					<< setw(9) << winTable.at("LV1")[1] * betFactor
					<< setw(9) << winTable.at("LV1")[2] * betFactor
					<< "│ ";
					cout << endl;
				cout << "       └────────────────────────────────────────┘";

				cout << endl;

				cout << "               M  E  G  A   R  E  E  L  S   " << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::left << "        total win: " <<
				std::setw(8) << totalWin << "               ? :win";
				cout << endl << endl << endl;
				if (simple ) {cout << endl;}

				firstWave++;
			} while ( buffer > 0 );
		}
	}
	#ifdef _WIN32
		Sleep(wait * 0.85);  // Windows (milliseconds)
    #else
		usleep( wait * 1000 * 0.85); // Linux/Mac (microseconds, so 1000 means 1ms)
    #endif
    if (animate != -1) winAnimationMEGA(grid, ROW_COUNT, winTable, betFactor, loanShark, simple, wait, longspin, spins, totalWin);
    cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
	<< endl << endl << endl << endl << endl << endl << endl << endl;
}

void spinReelsTANK( vector<vector<string>>& reels, vector<vector<int>>& fgrid, int ROW_COUNT, const map<string, vector<int>>& winTable,
int betFactor, bool loanShark, bool simple, int points, vector<int> info, bool rSet, int wait,
int markedSpots, int multiplier, int currentWin, int totalWin, int risk, unordered_set<reelMod> MOD )
{
	vector<vector<string>> grid;

    double slower = 1;

    int stepsNextStop = 7;

	bool first = true;
    int firstWave = -1; // IMPORTANT: for the spinning animation to make sence always ensure buffer >(=) visiblePos - firstWave

    int buffer = ROW_COUNT - firstWave + 1;

	buffer += rand() % static_cast<int>( max(4, markedSpots)/2.097 );
    if ((risk==0 && markedSpots>13) || (risk==1 && markedSpots>15) || (risk==2 && markedSpots>17)) buffer += rand() % 3;

    if (markedSpots==13){
        slower = 1.1;
    } else if (markedSpots==14){
        slower = 1.25;
    } else if (markedSpots==15){
        slower = 1.4;
    } else if (markedSpots==16){
        slower = 1.57;
    } else if (markedSpots==17){
        slower = 1.76;
    } else if (markedSpots==18){
        slower = 1.95;
    } else if (markedSpots==19){
        slower = 2.17;
    }

	for (int stoppedreels = 0; stoppedreels < 5; stoppedreels++){
		for (int step = 0; step < stepsNextStop; step++){
			do {
				if (buffer > 0) {buffer--; }
				if (!first){
			#ifdef _WIN32
				Sleep(wait * slower);  // Windows (milliseconds)
			#else
				usleep( wait * 1000 * slower); // Linux/Mac (microseconds, so 1000 means 1ms)
			#endif
				} else {
					first = false;
				}

				if (rSet){	grid = shiftedGrid(buffer-2, info, reelsfree1, reelsfree1, reelsfree1, reelsfree1, ROW_COUNT, step, stoppedreels, stepsNextStop, MOD ); }
				else {	grid = shiftedGrid(buffer-2, info, reelsfree2, reelsfree2, reelsfree2, reelsfree2, ROW_COUNT, step, stoppedreels, stepsNextStop, MOD); }

                for (int i = std::max(0,firstWave); i < ROW_COUNT ; i++){
                    for (int j = 0; j < 5; j++){
                        grid[j][i] = "    ";
                    }
                }

				cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl<< endl<< endl;

				int u = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
				for (const auto& row : fgrid) {
				cout << "          │";
					for (int cell : row) {
						if ( cell == 1 ) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "  $$  ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
						else if ( cell == 0) {
							cout << "      │";
						}
						else if ( cell == 3) {
							setTextColor("xx", DEFAULT_COLOR, FAT_UI, HVbox);
							if (!simple) {cout << "   x  ";}
							else         {cout << "  x   ";}
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "│";
						}
						else if ( cell == 2) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << " [$$] ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
					}
					if (u < 4) {
						cout << endl << "          │      │      │      │      │      │";
						u++;
					}
					cout << '\n';
				}
				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;


				cout << "      S  ──────────────────────────────────────  T" << endl;
				cout << "      H   [$$] reached:   " << std:: right<< std::setw(2)<< markedSpots
				<< "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
				cout << "      A   current win:     ?                     N" <<endl;
				cout << "      R   win sum:  " << std::right << std::setw(8) << totalWin;
				if (risk == 0)      {cout <<   "    [normal mode]    K" << endl;}
				else if (risk == 1) {cout <<   "    [risk mode]      K" << endl;}
				else                {cout <<   "    [shark mode]     K" << endl;}
				cout << "      K  ──────────────────────────────────────  !" << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << endl << endl<< endl;
				if (simple ) {cout << endl;}

				firstWave++;
			} while ( buffer > 0 );
		}
	}
	#ifdef _WIN32
		Sleep(wait);  // Windows (milliseconds)
    #else
		usleep( wait * 1000); // Linux/Mac (microseconds, so 1000 means 1ms)
    #endif
    if (animate != -1) winAnimationTANK(reels, fgrid, ROW_COUNT, winTable, betFactor, loanShark, simple, wait, longspin, markedSpots, multiplier, totalWin, risk);
	cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
	<< endl << endl << endl << endl << endl << endl << endl << endl;
}


void prespinBG(vector<vector<string>> grid, int betFactor, int ROW_COUNT, int wait, int lgames, int points){

	bool first = true;

	for (int water = 0; water < ROW_COUNT; water++){

				if (!first){
			#ifdef _WIN32
				Sleep(wait );  // Windows (milliseconds)
			#else
				usleep( wait * 1000 ); // Linux/Mac (microseconds, so 1000 means 1ms)
			#endif
				} else {
					first = false;
				}

				for (int i = ROW_COUNT-1; i > 0; i--){
                    for (int j = 0; j < 5; j++){
                        grid[j][i] = grid[j][i-1];
                    }
                }

                for (int j = 0; j < 5; j++){
                    grid[j][0] = "    ";
                }

				cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10)  << "       ┌────────────────────────────────────────┐ 178WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
				<< setw(9) << winTable.at("WLD")[0] * betFactor
				<< setw(9) << winTable.at("WLD")[1] * betFactor
				<< setw(9) << winTable.at("WLD")[2] * betFactor << "│  bet" << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
				cout << setw(9) << winTable.at("HV1")[0] * betFactor
				<< setw(9) << winTable.at("HV1")[1] * betFactor
				<< setw(9) << winTable.at("HV1")[2] * betFactor
				<< "│ ";
                if (price * betFactor<1000) cout << " "; cout << fixed << setprecision(0) << price * betFactor << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
				<< setw(9) << winTable.at("HV2")[1] * betFactor
				<< setw(9) << winTable.at("HV2")[2] * betFactor << "│" << endl;
				cout << "       │  " << setw(10) << "  2-9      "
				<< setw(9) << winTable.at("LV1")[0] * betFactor
				<< setw(9) << winTable.at("LV1")[1] * betFactor
				<< setw(9) << winTable.at("LV1")[2] * betFactor
				<< "│ "<< endl;
				cout << "       │                                        │ "; cout << endl;
				cout << "       │  " << setw(10) << " TANK   on       4    :   Shark Tank "
				<< " │  "; cout << endl;
				cout << "       │  " << setw(10) << " MEGA      reels   5  :   Mega Reels "
				<< " │  ";
				if (loanShark){
				cout << "game";
				}
				cout << endl;
				cout << "       └────────────────────────────────────────┘  ";
				if (loanShark){
					cout << lgames;
				}
				cout << endl;
                if (!loanShark){
                    cout << "              C A R D   S H A R K   M E G A " << endl;
                } else {
                    cout << "              L O A N   S H A R K   M E G A " << endl;
                }

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;
				cout << std::setw(7) << std::left << "        credit: " <<
				std::setw(8) << points << "                  ? :win";
				cout << endl << endl << endl;
				if (simple ) {cout << endl;}
    }

	#ifdef _WIN32
		Sleep(wait);  // Windows (milliseconds)
    #else
		usleep( wait * 1000); // Linux/Mac (microseconds, so 1000 means 1ms)
    #endif

	cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
	<< endl << endl << endl << endl << endl << endl << endl << endl;
}

void prespinMEGA(vector<vector<string>> grid, int betFactor, int ROW_COUNT, int wait, int lgames, int points, int spins, int totWin, bool simple, int multiplier){

	bool first = true;

    double tempo = 1;
    if (multiplier == 1){
        tempo = 0.75;
    } else if ( multiplier == 2) {
        tempo = 0.95;
    } else if ( multiplier == 3) {
        tempo = 1.2;
    } else if ( multiplier == 4) {
        tempo = 1.45;
    } else if ( multiplier == 5) {
        tempo = 1.7;
    }

	for (int water = 0; water < ROW_COUNT; water++){

				if (!first){
			#ifdef _WIN32
				Sleep(wait * tempo);  // Windows (milliseconds)
			#else
				usleep( wait * 1000 * tempo); // Linux/Mac (microseconds, so 1000 means 1ms)
			#endif
				} else {
					first = false;
				}

				for (int i = ROW_COUNT-1; i > 0; i--){
                    for (int j = 0; j < 5; j++){
                        grid[j][i] = grid[j][i-1];
                    }
                }

                for (int j = 0; j < 5; j++){
                    grid[j][0] = "    ";
                }

				cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
				<< endl << endl << endl << endl << endl << endl << endl << endl;

				cout << left << setw(10)  << "       ┌────────────────────────────────────────┐ 421WL" << endl;
				cout <<                      "       │             ×3       ×4       ×5       │" << endl;
				cout << "       │  " << setw(10) << " W7LD      "
					<< setw(9) << winTable.at("WLD")[0] * betFactor
					<< setw(9) << winTable.at("WLD")[1] * betFactor
					<< setw(9) << winTable.at("WLD")[2] * betFactor << "│"; if (spins != -1) {cout << " spins";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << setw(10) << "   A       ";} else { cout << setw(10) << "  Ace      ";}
					cout << setw(9) << winTable.at("HV1")[0] * betFactor
					<< setw(9) << winTable.at("HV1")[1] * betFactor
					<< setw(9) << winTable.at("HV1")[2] * betFactor
					<< "│"; if (spins != -1) {cout << " left";} cout << endl;
				cout << "       │  ";
				if (!simpleT) { cout << " 1o-K      ";} else { cout << "1o-King    ";}
				cout << setw(9) << winTable.at("HV2")[0] * betFactor
					<< setw(9) << winTable.at("HV2")[1] * betFactor
					<< setw(9) << winTable.at("HV2")[2] * betFactor << "│  "; if (spins != -1) {cout << setw(2) << spins;} cout << endl;
				cout << "       │  " << setw(10) << "  2-9      "
					<< setw(9) << winTable.at("LV1")[0] * betFactor
					<< setw(9) << winTable.at("LV1")[1] * betFactor
					<< setw(9) << winTable.at("LV1")[2] * betFactor
					<< "│ ";
					cout << endl;
				cout << "       └────────────────────────────────────────┘";

				cout << endl;

				cout << "               M  E  G  A   R  E  E  L  S   " << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = grid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘"  << endl;
				cout << std::left << "        total win: " <<
				std::setw(8) << totWin << "               ? :win";
				cout << endl << endl << endl;
				if (simple ) {cout << endl;}
    }

	#ifdef _WIN32
		Sleep(wait * tempo);  // Windows (milliseconds)
    #else
		usleep( wait * 1000 * tempo); // Linux/Mac (microseconds, so 1000 means 1ms)
    #endif

	cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
	<< endl << endl << endl << endl << endl << endl << endl << endl;
}

void prespinTANK(vector<vector<string>> fgrid, vector<vector<int>> grid, int ROW_COUNT, int betFactor, bool loanShark, bool simple, int points, int wait,
int markedSpots, int multiplier, int currentWin, int totalWin, int risk){

	bool first = true;

    double slower = 1;
    if (markedSpots==13){
        slower = 1.1;
    } else if (markedSpots==14){
        slower = 1.25;
    } else if (markedSpots==15){
        slower = 1.4;
    } else if (markedSpots==16){
        slower = 1.57;
    } else if (markedSpots==17){
        slower = 1.76;
    } else if (markedSpots==18){
        slower = 1.95;
    } else if (markedSpots==19){
        slower = 2.17;
    }

	for (int water = 0; water < ROW_COUNT; water++){

				if (!first){
			#ifdef _WIN32
				Sleep(wait * slower);  // Windows (milliseconds)
			#else
				usleep( wait * 1000 * slower); // Linux/Mac (microseconds, so 1000 means 1ms)
			#endif
				} else {
					first = false;
				}

				for (int i = ROW_COUNT-1; i > 0; i--){
                    for (int j = 0; j < 5; j++){
                        fgrid[j][i] = fgrid[j][i-1];
                    }
                }

                for (int j = 0; j < 5; j++){
                    fgrid[j][0] = "    ";
                }

				cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;

				int u = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
				for (const auto& row : grid) {
				cout << "          │";
					for (int cell : row) {
						if ( cell == 1 ) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "  $$  ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
						else if ( cell == 0) {
							cout << "      │";
						}
						else if ( cell == 3) {
							setTextColor("xx", DEFAULT_COLOR, FAT_UI, HVbox);
							if (!simple) {cout << "   x  ";}
							else         {cout << "  x   ";}
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << "│";
						}
						else if ( cell == 2) {
							setTextColor("$$", DEFAULT_COLOR, FAT_UI, HVbox);
							cout << " [$$] ";
							setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
							cout <<"│";
						}
					}
					if (u < 4) {
						cout << endl << "          │      │      │      │      │      │";
						u++;
					}
					cout << '\n';
				}
				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;



				cout << "      S  ──────────────────────────────────────  T" << endl;
				cout << "      H   [$$] reached:   " << std:: right<< std::setw(2)<< markedSpots
				<< "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
				cout << "      A   current win:     ?                     N" <<endl;
				cout << "      R   win sum:  " << std::right << std::setw(8) << totalWin;
				if (risk == 0)      {cout <<   "    [normal mode]    K" << endl;}
				else if (risk == 1) {cout <<   "    [risk mode]      K" << endl;}
				else                {cout <<   "    [shark mode]     K" << endl;}
				cout << "      K  ──────────────────────────────────────  !" << endl;

				int m = 1;

				cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;

				for (int row = 0; row < ROW_COUNT; ++row) {
					cout << "          │ ";
					for (int col = 0; col < REEL_COUNT; ++col) {
					string symbol = fgrid[col][row];
					string translatedSymbol = symbolTranslator.count(symbol) > 0
										? symbolTranslator[symbol]
										: symbol;
					setTextColor(symbol, DEFAULT_COLOR, FAT_UI, HVbox);
					cout << setw(4) << translatedSymbol; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); cout << " │ ";
				}

				if (m < ROW_COUNT) {
					cout << endl << "          │      │      │      │      │      │" << endl;
				} else {
					cout << endl;
				}
				m++;
				}

				cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl;
				cout << endl << endl<< endl;
				if (simple ) {cout << endl;}
    }

	#ifdef _WIN32
		Sleep(wait * slower);  // Windows (milliseconds)
    #else
		usleep( wait * 1000 * slower); // Linux/Mac (microseconds, so 1000 means 1ms)
    #endif

	cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
	<< endl << endl << endl << endl << endl << endl << endl << endl;
}


pair<int, int> simulateFG(bool spinning, char modee, int points, int rows, int cols, bool test_mode, int betFactor,
double tries, double successes, double totallines[], double markcount[], double lines3[], double lines4[],
double lines5[], double fwin[], double fun[], double averageline[], int li[], int modes[], int wait, int k) { // one complete feature process, returns the total win

    vector<vector<int>> grid(rows, vector<int>(cols, 0));
	vector<vector<int>> gridSPIN(rows, vector<int>(cols, 0));
    int markedSpots = 0;
    bool gameContinues = true;
    int totalWin = 0;
    double multiplier = 1.0;
    int rdmreels=0;
    bool randomFG = true;
    unordered_set<reelMod> MOD;

    vector<pair<int, int>> currentLine;
	vector<pair<int, int>> markline;
    int currentLineLength = 3;
    int risk = sim_risk;
	bool fp = true;
    bool entry = true;

    if (!test_mode && FMODES == -1) risk = rand() % 3;
    else if ( !test_mode && FMODES == 0 ) risk = 0;
    else if ( !test_mode && FMODES == 1 ) risk = 1;
    else if ( !test_mode && FMODES == 2 ) risk = 2;

     if ( risk == 0 ) {modes[0]++;}
     else if (risk == 1) {modes[1]++;}
     else if (risk == 2) {modes[2]++;}

    if (test_mode) {
        // header for mode selection
        cout << "       ┌────────────────────────────────────────┐  " << endl;
        cout << "       │  unlimited spins for as long as every  │ /\\" << endl;
        cout << "       │    win marks at least one new [$$]     │<\\ \\"<< endl;
        cout << "       │   and the Shark Tank is not full yet   /\\/ o\\" << endl;
        cout << "       │                                             |" << endl;
        cout << "       │   wins lying exclusively on already    \\ /  \\" << endl;
		cout << "       │  marked spaces end the feature   _      V  __\\" << endl;
		cout << "       │                                 /|/\\/\\   /" << endl;
        cout << "       │  multipliers for all wins up to  |\\/\\/  /" << endl;
        cout << "       └────────────────────────────────────────┘" <<  endl;
        cout << "              S  H  A  R  K     T  A  N  K   " << endl;
        cout << "          ┌──────────────────────────────────┐"<< endl;
        cout << "          │              normal  risk  shark │"<< endl;
        cout << "          │  20 × [$$]  .  10  .  27  . 100  │"<< endl;
        cout << "          │  19 × [$$]  .   7  .  10  .  27  │"<< endl;
        cout << "          │  18 × [$$]  .   5  .  7   .      │"<< endl;
        cout << "          │  17 × [$$]  .   4  .  5          │"<< endl;
        cout << "          │  16 × [$$]  .   3  .      times  │"<< endl;
        cout << "          │  15 × [$$]  .   2      all wins  │"<< endl;
        cout << "          └──────────────────────────────────┘" << endl;
        cout << "      "<< invertUI <<" !  C H O O S E    M U L T I P L I E R S  ! "<< currentUI;

    }

    if (test_mode) {
        cout <<endl<< endl << "      press the first letter of the desired mode"<< endl;
        if (simple && test_mode) {cout << endl;}

        while (true) {
            char key = readFirstCharacter();
            if (key == '*') { cheat = !cheat; }

            if (key == '#') { exit(0); }
            if (key == 'n') { risk = 0; break; }
            else if (key == 'r') { risk = 1; break; }
			else if (key == 's') { risk = 2; break; }
        }
        if (simple && test_mode) {cout << endl << endl << endl;}

        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl<< endl << endl << endl << endl << endl;
        //cout << "                  S  H  A  R  K     T  A  N  K   " << endl;

        cout << "          ┌──────────────────────────────────┐" << endl;
        cout << "          │                /\\                │" << endl;
        cout << "          │               /  \\               │" << endl;
        cout << "          │              /,  ,\\              │" << endl;
        cout << "          │             /      \\             │" << endl;
        cout << "          │            / ______ \\            │" << endl;
        cout << "          │           / /VwVvwV\\ \\           │" << endl;
        cout << "          │           | \\ (()) / |           │" << endl;
        cout << "          └─────────  |  ^^^^^^  |  ─────────┘" << endl;
        cout << "      S  ──────────────────────────────────────  T" << endl;
        cout << "      H       G   O   O   D        !             A" << endl;
        cout << "      A                                          N" << endl;
        cout << "      R             !        L   U   C   K       K" << endl;
        cout << "      K  ──────────────────────────────────────  !" << endl;
        cout << "          ┌──────┬──────┬──────┬──────┬──────┐" << endl;
        cout << "          │      │      │      │      │      │" << endl;
        cout << "          │      │      │      │      │      │" << endl;
        cout << "          │      │      │      │      │      │" << endl;
        cout << "          │      │      │      │      │      │" << endl;
        cout << "          │      │      │      │      │      │" << endl;
        cout << "          │      │      │      │      │      │" << endl;
        cout << "          │      │      │      │      │      │" << endl;
        cout << "          └──────┴──────┴──────┴──────┴──────┘" << endl<< endl<< endl;

        cout << "      press SPACE to start the first spin"<< endl;
            if (simple && test_mode) {cout << endl;}
            char keyy = readFirstCharacter();
            if (keyy == '*') { cheat = !cheat; }
            if (keyy == '#') { exit(0); }
            if (simple && test_mode) {cout << endl << endl << endl;}
    }

    int rando;
    vector<vector<string>> reels;
    tuple<int, vector<pair<int, int>>, bool> cur;

    int line3 = 0;
    int line4 = 0;
    int line5 = 0;

	int currentWin;

	int oldmarkedSpots;
	int oldmultiplier;
	int oldcurrentWin;
	int oldtotalWin;
    vector<vector<string>> oldGrid;

	bool rSet;
	vector<int> info(2 * REEL_COUNT + 1);

    if (test_mode){ cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl; }

    while (gameContinues) {
        bool newPositionMarked = false; // track if a new position has been marked
        multiplier = 1;
        currentLine.clear();  // reset line for next subgame
        currentLineLength = 0;

        while (true){

            tries++;

            rdmreels = rand() % 20;

            if (rdmreels < 10 ) {
				pair <vector<vector<string>>, vector<int>> outcome = generateGridInfo( reelsfree1, reelsfree1, reelsfree1, reelsfree1, ROW_COUNT);
				rSet = true;
				reels = outcome.first;
				info = outcome.second;
			} // spin the FG reels 1
            else
            {
				pair <vector<vector<string>>, vector<int>> outcome = generateGridInfo( reelsfree2, reelsfree2, reelsfree2, reelsfree2, ROW_COUNT);
				rSet = false;
				reels = outcome.first;
				info = outcome.second;
			} // spin the FG reels 2

			// TANK CHEAT
			if (cheat)
            {
                rdmreels = rand() % 100;

                if (rdmreels < 45)
                {
                    bool posTest = false;
                    cur = calculateWinsFG(reels, false, betFactor, false);
                    if (std::get<0>(cur) > 0)
                    {
                        for (const auto& pos : std::get<1>(cur))
                        {
                            if (grid[pos.second][pos.first] == 0) {
                                posTest = true;
                                break; // no drowning anyways
                            }
                        }

                        if (!posTest)
                        {
                            rdmreels = rand() % 2;

                            if (rdmreels == 0 ) {
                                pair <vector<vector<string>>, vector<int>> outcome = generateGridInfo( reelsfree1, reelsfree1, reelsfree1, reelsfree1, ROW_COUNT);
                                rSet = true;
                                reels = outcome.first;
                                info = outcome.second;
                            } // spin the FG reels 1 again
                            else
                            {
                                pair <vector<vector<string>>, vector<int>> outcome = generateGridInfo(  reelsfree2, reelsfree2, reelsfree2, reelsfree2, ROW_COUNT);
                                rSet = false;
                                reels = outcome.first;
                                info = outcome.second;
                            } // spin the FG reels 2 again
                        }
                    }
                }
            }

            if (simulateCOS && test_mode ){
                MOD.clear();
                pair <vector<vector<string>>, reelMod> modW = attemptAddWild(reels, betFactor);

                if (modW.first.size() > 0 && modW.second.reel >= 0) {  // Checking if the reel is valid
                    reels = modW.first;
                    MOD.insert(modW.second);  // Store the vector<vector<string>> associated with the reelMod key
                }

            }

            cur = calculateWinsFG(reels, test_mode, betFactor, !spinning); // calculate win and get the winning line if there is a win

            if( (std::get<1>(cur)).size() >= 3 ) { successes++;
                if( (std::get<1>(cur)).size() == 3 ) { totallines[0]++; }
                else if ( (std::get<1>(cur)).size() == 4 ) { totallines[1]++; }
                else if ( (std::get<1>(cur)).size() == 5 ) { totallines[2]++; }
            }

            if ( (std::get<0>(cur)) > 0  ) {break;} // win exists, therefore the spin must not be discarded
            else {
                if (std::get<2>(cur)==true) {break;} // calc wins function decided to accept irrelevant non win
            }

        }

		oldcurrentWin = currentWin;
		oldtotalWin = totalWin;
		oldmarkedSpots = markedSpots;
		if (risk==0) {
                if (markedSpots == 15) oldmultiplier = 2.0;
                else if (markedSpots == 16) oldmultiplier = 3.0;
                else if (markedSpots == 17) oldmultiplier = 4.0;
                else if (markedSpots == 18) oldmultiplier = 5.0;
                else if (markedSpots == 19) oldmultiplier = 7.0;
                else if (markedSpots == 20) oldmultiplier = 10.0;
				else {  oldmultiplier = 1.0; }
            } else if (risk==1){
                if (markedSpots == 17) oldmultiplier = 5.0;
                else if (markedSpots == 18) oldmultiplier = 7.0;
                else if (markedSpots == 19) oldmultiplier = 10.0;
                else if (markedSpots == 20) oldmultiplier = 27.0;
				else {  oldmultiplier = 1.0; }
            } else if (risk==2){
                if (markedSpots == 19) oldmultiplier = 27.0;
                else if (markedSpots == 20) oldmultiplier = 100.0;
				else {  oldmultiplier = 1.0; }
        }

        currentWin = std::get<0>(cur);

        markline = std::get<1>(cur);

		for (int i=0; i<5; i++) {
            for (int j=0; j<4; j++) {
				gridSPIN[j][i] = grid[j][i];
            }
        }

        for (int i=0; i<4; i++) {
            for (int j=0; j<5; j++) {
                if (grid[i][j] == 2) { // former new marks are not new anymore
                    grid[i][j] = 1;
					if (spinning) { gridSPIN[i][j] = 1; }
                }
            }
        }

        if (currentWin > 0) {
            for (const auto& pos : markline) {
                if (grid[pos.second][pos.first] == 0) { // careful with first/second
                    grid[pos.second][pos.first] = 2;
                    markedSpots++;
                    newPositionMarked = true;
                }
            }
        }

		// if no new position was marked stop the game
        if (!newPositionMarked && currentWin > 0) {
            gameContinues = false;
			for (const auto& pos : markline){
				grid[pos.second][pos.first] = 3;
			}
        }

		if (test_mode && spinning){
            if (!entry) { prespinTANK(oldGrid, gridSPIN, ROW_COUNT, betFactor, loanShark, simple, points, wait, oldmarkedSpots, oldmultiplier, oldcurrentWin, oldtotalWin, risk); }
            entry = false;
            oldGrid = reels;
			spinReelsTANK( reels, gridSPIN, ROW_COUNT, winTable, betFactor, loanShark, simple, points, info, rSet, wait,
			oldmarkedSpots, oldmultiplier, oldcurrentWin, oldtotalWin, risk, MOD);

            if (currentWin>0){
                tuple<int, vector<pair<int, int>>, bool> ir;
                ir = calculateWinsFG(reels, test_mode, betFactor, true);
            }
		}

        if (test_mode) { cout << endl; printFGrid(grid, 0); }

        totalWin += currentWin;
        if( (std::get<1>(cur)).size() == 3 ) { line3++; averageline[0] += currentWin; li[0]++;}
        else if ( (std::get<1>(cur)).size() == 4 ) { line4++; averageline[1] += currentWin; li[1]++;}
        else if ( (std::get<1>(cur)).size() == 5 ) { line5++; averageline[2] += currentWin; li[2]++;}


        if (markedSpots == 20) {
            gameContinues = false;
        }

        // print current status in test mode
        if (test_mode && gameContinues) {
            if (risk==0) {
                if (markedSpots == 15) multiplier = 2.0;
                else if (markedSpots == 16) multiplier = 3.0;
                else if (markedSpots == 17) multiplier = 4.0;
                else if (markedSpots == 18) multiplier = 5.0;
                else if (markedSpots == 19) multiplier = 7.0;
                else if (markedSpots == 20) multiplier = 10.0;
            } else if (risk==1){
                if (markedSpots == 17) multiplier = 5.0;
                else if (markedSpots == 18) multiplier = 7.0;
                else if (markedSpots == 19) multiplier = 10.0;
                else if (markedSpots == 20) multiplier = 27.0;
            } else if (risk==2){
                if (markedSpots == 19) multiplier = 27.0;
                else if (markedSpots == 20) multiplier = 100.0;
            }

            cout << "      S  ──────────────────────────────────────  T" << endl;
            cout << "      H   [$$] reached:   " << std:: right<< std::setw(2)<< markedSpots
            << "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
            cout << "      A   current win: " << std::right << std::setw(5)<< currentWin << "                     N" <<endl;
            cout << "      R   win sum:   " << std::setw(7) << totalWin;
            if (risk == 0)      {cout <<   "    [normal mode]    K" << endl;}
            else if (risk == 1) {cout <<   "    [risk mode]      K" << endl;}
            else                {cout <<   "    [shark mode]     K" << endl;}
            cout << "      K  ──────────────────────────────────────  !" << endl;

            printGrid(reels, ROW_COUNT);

            cout << endl;

            if (markedSpots == 19 && fp){
                cout << endl << "      press 'c' to try and get the last [$$]"<< endl;
				fp = false;
            } else {
                cout << endl << "      press SPACE to spin again"<< endl;
            }

            if (simple && test_mode) {cout << endl;}

            char keyy = 'x';
            if (markedSpots == 19 && fp){
                while (keyy != 'c'){
                    keyy = readFirstCharacter();
                    if (keyy == '*') { cheat = !cheat; }
                    if (keyy == '#') { exit(0); }
                }
            } else {
                char keyy = readFirstCharacter();
                if (keyy == '*') { cheat = !cheat; }
                if (keyy == '#') { exit(0); }
            }

            if (simple && test_mode) {cout << endl << endl << endl;}
            cout << endl << endl << endl << endl << endl << endl << endl << endl;
        }


        // set multiplier based on the total number of marked spaces
        if (gameContinues == false) {
            if (risk==0) {
                if (markedSpots == 15) multiplier = 2.0;
                else if (markedSpots == 16) multiplier = 3.0;
                else if (markedSpots == 17) multiplier = 4.0;
                else if (markedSpots == 18) multiplier = 5.0;
                else if (markedSpots == 19) multiplier = 7.0;
                else if (markedSpots == 20) multiplier = 10.0;
            } else if (risk==1){
                if (markedSpots == 17) multiplier = 5.0;
                else if (markedSpots == 18) multiplier = 7.0;
                else if (markedSpots == 19) multiplier = 10.0;
                else if (markedSpots == 20) multiplier = 27.0;
            } else if (risk==2){
                if (markedSpots == 19) multiplier = 27.0;
                else if (markedSpots == 20) multiplier = 100.0;
            }
            markcount[markedSpots-3]++;

            lines3[markedSpots-3]+= line3;
            lines4[markedSpots-3]+= line4;
            lines5[markedSpots-3]+= line5;

            fwin[markedSpots -3] += totalWin * multiplier;
			fun[markedSpots -3] += totalWin;
        }
    }

    if (test_mode && !gameContinues) {
        cout << "      S  ──────────────────────────────────────  T" << endl;
		cout << "      H   [$$] reached:   " << std::setw(2)<< markedSpots
            << "    multiplier:"<< std::setw(3) << multiplier << "   A" << endl;
        cout << "      A   current win: "<< std::right << std::setw(5)<< currentWin << "                     N" <<endl;
        cout << "      R   win sum:    " << std::setw(6) << fixed << setprecision(0) << totalWin;
		if (markedSpots<20) { cout << "     YOU DROWNED     K" << endl;}
        else {                cout << "   !!! MAX WIN !!!   K" << endl;}
        cout << "      K  ──────────────────────────────────────  !";

		cout << endl;
        printGrid(reels,ROW_COUNT);
        cout << endl;

        cout << endl << "      press SPACE to finish the feature"<< endl;
        if (simple && test_mode) {cout << endl;}
        char keyy = readFirstCharacter();
        if (keyy == '*') { cheat = !cheat; }
        if (keyy == '#') { exit(0); }
        if (simple && test_mode) {cout << endl << endl << endl;}
        cout << endl << endl << endl << endl;

    }

    if (test_mode){
        cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl << endl << endl
                << endl<< endl<< endl<< endl<< endl<< endl<< endl
				<< endl<< endl<< endl<< endl<< endl << endl<< endl;

		bool h = false;

			if ( totalWin * multiplier >= 100000 && totalWin * multiplier >= 1000 * price * betFactor )
            {
				h = true;

				cout << "      ─────────$$────$$──$$$$$$$$────────────┐" << endl;
				cout << "       ────$$$$$$$$$$$$$$$$$$/ \\$$─────────┐ │    " << endl;
				cout << "         $$$$$$$$$$$$$$$$$$$/ , \\$$        │ │    " << endl;
				cout << "       $$$$$$$$$$    $$  $$/     \\$$       │ │    " << endl;
				cout << "      $$$$$$   $$    $$   /       \\$       │ │    " << endl;
                cout << "     $$$$$     $$    $$  / ,0      \\       │ │     " << endl;
				cout << "    $$$$$      $$    $$ /        ,/\\       │ │  " << endl;
				cout << "    $$$$$      $$    $$/      ,,    |      │ │    " << endl;
				cout << "    $$$$$   ___$$____$/       \\\\\\  /       │ │     " << endl;
				cout << "     $$$$$  \\  $$    $         )) |        │ │   " << endl;
				cout << "      $$$$$$ \\ $$           __,   \\        │ │   " << endl;
				cout << "        $$$$$$\\$$          /       \\       │ │   " << endl;
				cout << "          $$$$$$$$        /   ______)      │ │     " << endl;
				cout << "            $$$$$$$$$$$$$/      /          │ │     " << endl;
				cout << "        ──────$$$$$$$$$$$$$────/───────────┘ │      " << endl;
				cout << "          ┌──────────────────────────────────┤" ;
            } else if ( totalWin* multiplier >= 100*betFactor*price ) {
                cout << "                          /\\   " << endl;
				cout << "                         /  \\  " << endl;
				cout << "                        /    \\  " << endl;
				cout << "                       /  ' ' \\ " << endl;
				cout << "               [$$]   /        \\   [$$]     " << endl;
				cout << "                     /  _______ \\            " << endl;
				cout << "            [$$]    /  /vVvVwvV\\ \\    [$$]  " << endl;
				cout << "                   0  /wV      V\\ \\         " << endl;
				cout << "         [$$]     /  /Vv ((())) V\\ \\     [$$]" << endl;
				cout << "                 /  (Vw_________v| |           " << endl;
				cout << "                /    \\ |       | / |          " << endl;
				cout << "                |     \\| $$$$$ |/  /          " << endl;
                cout << "          ┌─────┘                  └─────────┐" ;
            } else if ( totalWin* multiplier >= 50*betFactor*price ) {
                cout << "                              ________        " << endl;
                cout << "                     [$$]     \\    0  \\      " << endl;
                cout << "                               \\___    \\     " << endl;
                cout << "              [$$]              VwV)    \\__   " << endl;
                cout << "                          [$$]   \\  )))   _\\ " << endl;
                cout << "          ┌──────────────────────┘       └───┐";
            } else if ( totalWin* multiplier >= 10*betFactor*price ) {
                cout << "                               ________       " << endl;
                cout << "                               \\__  o  \\      " << endl;
                cout << "                                Vw)     \\_    " << endl;
                cout << "                                 \\  )))  _\\   " << endl;
                cout << "          ┌──────────────────────┘      └────┐";
            } else {
                cout << "                               ________       " << endl;
                cout << "                               \\__  x  \\      " << endl;
                cout << "                                vv)     \\_    " << endl;
                cout << "                                 \\   ))  _\\   " << endl;
                cout << "          ┌──────────────────────┘      └────┐";
            }

		if ( totalWin * multiplier >= 100*price*betFactor ){
            for (int i=0; i<4; i++) {
                for (int j=0; j<5; j++) {
                    if (grid[i][j] != 2 && grid[i][j] != 0) { // display all final [$$] with brackets, may be modified
                        grid[i][j] = 2;
                    }
                }
            }
        } else {
            for (int i=0; i<4; i++) {
                for (int j=0; j<5; j++) {
                    if (grid[i][j] == 2) { // display all final ' $$ ' without brackets
                        grid[i][j] = 1;
                    }
                }
            }
        }


		cout << endl;
		if ( !h ){
			cout << "          │ B  O  N  U  S   E  N  D  I  N  G │";
		} else {
			cout << "          │  C O N G R A T U L A T I O N S ! │";
		}
		cout<< endl << "          └──────────────────────────────────┘" << endl << "           F I N A L   W I N    :    ";
        if( totalWin < 1000 ){cout << "  ";}
        std::string str = std::to_string(totalWin*multiplier);
        for (char digit : str) {
            if (digit == '.'){break;}
            std::cout << digit << " ";
        }
        cout << endl;printFGrid(grid, totalWin * multiplier);
		cout << std::setw(7) << std::left << "        credit: " << points+totalWin*multiplier;
        if ( totalWin*multiplier >= 25 * price * betFactor ) {
                    if (totalWin*multiplier < 50 * price * betFactor) {
                        cout << "               ! BIG WIN ! ";
                    } else if ( totalWin*multiplier < 100 * price * betFactor ) {
                        cout << "             ! HUGE  WIN ! ";
                    } else if ( totalWin*multiplier < 200 * price * betFactor ) {
                        cout << "          ! ENORMOUS  WIN ! ";
                    } else if ( totalWin*multiplier < 500 * price * betFactor ) {
                        cout     << "      ! UNBELIEVABLE  WIN !";
                    } else {
						if ( !h ) {
							cout << "          ! INSANE  WIN !";
						} else {
							cout << "   YOU ARE A SUPER PLAYER !";
						}
                    }
        }
		cout << endl;
    }

    if (PRINTSCREEN % 100 == 0)
    {
    if (!test_mode && totalWin * multiplier >= 100 * price && totalWin * multiplier < 200 * price && PRINTSCREEN<=100) {
        printFGrid(grid, totalWin * multiplier,false);
        cout << "game "<< fixed << setprecision(0)<< k+1 <<" (TANK): "  << fixed << setprecision(0)
        << totalWin * 5 << " × "<< multiplier << " = " << totalWin * 5 * multiplier << " ↑"<< endl;
    }
    if (!test_mode && totalWin * multiplier >= 200 * price && totalWin * multiplier < 500 * price && PRINTSCREEN<=200) {
        printFGrid(grid, totalWin * multiplier,false);
        cout << "game "<< fixed << setprecision(0)<< k+1 <<" (TANK): " << fixed << setprecision(0)
        << totalWin * 5 << " × "<< multiplier << " = " << totalWin * 5 * multiplier << " ↑"<< endl;
    }
    if (!test_mode && totalWin * multiplier >= 500 * price && PRINTSCREEN<=500) {
        printFGrid(grid, totalWin * multiplier,false);
        cout << "game "<< fixed << setprecision(0)<< k+1 <<" (TANK): " << fixed << setprecision(0)
        << totalWin * 5 << " × "<< multiplier << " = " << totalWin * 5 * multiplier << " ↑"<< endl;
    }
    }

    return {totalWin * multiplier, risk};
}


pair <int, int> simulatex7(int wait, bool test_mode, int betFactor, map<string, int>& totalWinCounts, int points, bool loanShark, int lgames, bool spinning, int k){ //simulate single x7 entry
    int winAm = 0;
	int totWin = 0;
	int nu;
	bool rSet;
    bool entry = true;
    map<string, int> irrCounts;

    unordered_set<reelMod> MOD;
	vector<int> info(2 * REEL_COUNT + 1);
	vector<vector<string>> grid(REEL_COUNT, vector<string>(7));
    vector<vector<string>> oldGrid;

	if (test_mode){

	print7(winTable, betFactor*1, -1, simple);cout << endl;
    cout << "               M  E  G  A   R  E  E  L  S     \n";
	cout << "          ┌──────────────────────────────────┐" << endl;
	cout << "          │  play with a total of 421 lines  │" << endl;
	cout << "          │                                  │" << endl;
	cout << "          │           normal . risk . shark  │" << endl;
	cout << "          │ number           .      .        │" << endl;
    cout << "          │ of spins     25  .  12  .   7    │" << endl;
	cout << "          │                  .      .        │" << endl;
	cout << "          │ multiplier    1  .   *  .   4    │" << endl;
    cout << "          │                  .      .        │" << endl;
    cout << "          ├──────────────────────────────────┤" << endl;
    cout << "          │ * in risk mode multipliers vary: │" << endl;
	cout << "          │                                  │" << endl;
    cout << "          │  3 spins each with multipliers   │" << endl;
    cout << "          │         1,  2,  3,  and  4       │" << endl;
    cout << "          └──────────────────────────────────┘" << endl;
    cout << "      "<< invertUI <<" !  C H O O S E    M U L T I P L I E R S  ! "<< currentUI;
    cout << endl<< endl << "      press the first letter of the desired mode "<< endl;
    if (simple && test_mode) {cout << endl;}
    }
    int modd = 0;
	int winm = 1;

    if (!test_mode && FMODES == -1) modd = rand() % 3;
    else if ( !test_mode && FMODES == 0 ) modd = 0;
    else if ( !test_mode && FMODES == 1 ) modd = 1;
    else if ( !test_mode && FMODES == 2 ) modd = 2;

    if ( modd < 2 ) { winm = 1;} else { winm = 4;}

    while (true && test_mode) {
		char keey = readFirstCharacter();
        if (keey == '*') { cheat = !cheat; }

            if (keey == '#') {
				exit(0);
            } else if (keey == 'n') {
                cout << endl<< endl << endl << endl << endl << endl << endl << endl << endl<< endl << endl<< endl << endl<< endl << endl;
				modd = 0;
				winm = 1;
                break;
            } else if (keey == 'r') {
                cout << endl<< endl << endl << endl << endl << endl << endl << endl << endl<< endl << endl<< endl << endl<< endl << endl;
				modd = 1;
				winm = 1;
                break;
            } else if (keey == 's') {
                cout << endl<< endl << endl << endl << endl << endl << endl << endl << endl<< endl << endl<< endl << endl<< endl << endl;
				modd = 2;
				winm = 4;
                break;
            }
    }

	if (modd == 0){ SPINS = 25;}
	else if (modd == 1) {SPINS = 12;}
    else if (modd == 2) {SPINS = 7;}

	if (test_mode){
        if (simple && test_mode) {cout << endl << endl << endl;}

        print7(winTable, betFactor*winm, SPINS, simple);cout << endl;
        cout << "               M  E  G  A   R  E  E  L  S   \n";

        cout << "          ┌──────────────────────────────────┐" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │                                  │" << endl;
        cout << "          │              _________           │" << endl;
        cout << "          │              \\    ";
        if (modd == 0) { cout << "N";} else if (modd == 1){ cout << "R";} else {cout << "S";}
        cout << "   \\          │" << endl;
        cout << "          │               \\___     \\__       │" << endl;
        cout << "          │                Vvw)       \\      │" << endl;
        cout << "          │                 \\   )))   _\\     │" << endl;
        cout << "          └─────────────────┘        └───────┘" << endl;
        cout << "        !   G   O   O   D      L   U   C   K   !";
        cout << endl<< endl << "      press SPACE to start the first spin "<< endl;
        if (simple && test_mode) {cout << endl;}
        }
        while (true && test_mode) {
            char keey = readFirstCharacter();
            if (keey == '*') { cheat = !cheat; }

            if (keey == '#') {
				exit(0);
            } else {
                if (simple && test_mode) {cout << endl << endl << endl;}
                cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
				<< endl << endl;
                break;
            }
        }

        int reelset;
        int giveWin;
        int discardLimit;

        if (modd == 0)      { discardLimit =  4454; }
        else if (modd == 1) { discardLimit = 20379; }
        else                { discardLimit = 14691; }

        for (int i = 0; i < SPINS; i++){
            reelset = rand() % 10000;

            if ( modd == 1 && i == 3) { winm = 2;}
            else if ( modd == 1 && i == 6) { winm = 3;}
            else if ( modd == 1 && i == 9) { winm = 4;}

            giveWin = rand() % 100000;
            if (cheat) { giveWin = 97000; }

            if(giveWin < discardLimit)
            {
                do
                {
                    reelset = rand() % 100;

                    if (reelset < 50 ){ // The value to obtain exactly 97% RtP on paper lies at around 4669
                        rSet = true;
                        pair <vector<vector<string>>, vector<int>> draw = generateGridInfo(reels7, reels8, reels9, reels7, 7);
                        grid = draw.first;
                        info = draw.second;
                    } else {
                        rSet = false;
                        pair <vector<vector<string>>, vector<int>> draw = generateGridInfo(reels10, reels11, reels12, reels10, 7);
                        grid = draw.first;
                        info = draw.second;
                    }
                    winAm = calculateWins(grid, test_mode, irrCounts, betFactor, winningLines7, false);

                } while ( winAm > 0 ); // create non win
            }
            else
            {
                reelset = rand() % 100;
                if (reelset < 50 ){
                    pair <vector<vector<string>>, vector<int>> draw = generateGridInfo(reels7, reels8, reels9, reels7, 7);
                    grid = draw.first;
                    info = draw.second;
                    rSet = true;
                } else {
                    pair <vector<vector<string>>, vector<int>> draw = generateGridInfo(reels10, reels11, reels12, reels10, 7);
                    rSet = false;
                    grid = draw.first;
                    info = draw.second;
                }
            }

            // MEGA CHEAT
            if (cheat) // only visited if manually chosen in the main menu ! ! ! ! !
            {
                reelset = rand() % 100;
                if (reelset < 84)
                {
                    for (int i=1; i<3; i++)
                    {
                        winAm = calculateWins(grid, test_mode, irrCounts, betFactor, winningLines7, false);

                        if (winm == 1)
                            reelset = rand() % 93;
                        else if (winm == 2)
                            reelset = rand() % 75;
                        else if (winm == 3)
                            reelset = rand() % 61;
                        else
                            reelset = rand() % 49;

                        if (winAm > reelset * price * betFactor)
                        {
                            break;
                        }
                        else
                        {
                            reelset = rand() % 100;
                            if (reelset < 50 ){
                                pair <vector<vector<string>>, vector<int>> draw = generateGridInfo(reels7, reels8, reels9, reels7, 7);
                                grid = draw.first;
                                info = draw.second;
                                rSet = true;
                            } else {
                                pair <vector<vector<string>>, vector<int>> draw = generateGridInfo(reels10, reels11, reels12, reels10, 7);
                                rSet = false;
                                grid = draw.first;
                                info = draw.second;
                            }
                        }
                    }
                }
            }

			if (test_mode && preMod){printGrid(grid,7);} // for analysis/debugging

			if (test_mode) { MOD.clear(); }

			if ( (test_mode && applyCOS) || simulateCOS){

				int cont = rand() % 100;

				if (cont < 67) {

					tuple<int, string> testSet = countHVSymbols(grid);
					int rdddd = rand() % 100;

					if ( get<0>(testSet) >= 4 ) {
						int rd = rand() % 100;

						if (rdddd < 20 ){
							nu = 0;
						} else if (cont < 2) {
							nu = 7; // randomly maximize the odds for a "near miss/near larger win" screen from time to time
						} else {
							if ( get<0>(testSet) <= 5 ) {
								nu = (rd < 41) ? 5 : 2;
							} else if ( get<0>(testSet) <= 7 ) {
								nu = (rd < 43) ? 5 : 2;
							} else if ( get<0>(testSet) <= 9 ) {
								nu = (rd < 42) ? 6 : 2;
							} else if ( get<0>(testSet) <= 11 ) {
								nu = (rd < 52) ? 5 : 2;
							} else {
								nu = (rd < 47) ? 6 : 2;
							}
						}
					} else {
						nu = 0;
					}

					bool once = true;

					for (int i = 0; i < nu; i++){
						int a = rand() % 5;
						int b = rand() % 7;
						if ( isValidPosition( a,b, grid, get<1>(testSet) ) ){
							cosInfo tuple = addCosmetic( a,b, grid, betFactor, 5, 7, winningLines7, get<1>(testSet));
                            if (tuple.reel >= 0) {
                                grid = tuple.screen;
                                reelMod newmod = { tuple.reel, tuple.pos, tuple.symbol };
                                MOD.insert(newmod); // preserve info for (p)reconstructing spinning reels
                            }

                            if (once && tuple.reel >= 0) {
                                once = false;
                                if (tuple.win >= 50 * price *betFactor && tuple.reel >= 0){
                                    nu+=2;
                                } else if (tuple.win >= 20 * price *betFactor && tuple.reel >= 0){
                                    nu+=1;
                                } else if (tuple.win == 0 && tuple.reel >= 0){
                                    nu-=1;
                                }
                            }
						}
					}

				}
			}

			if ((test_mode && applyCOS) || simulateCOS){
                int coW = rand() % 200;
                int nu;
              if (coW < 100) {
                    nu = 0;
                } else if ( coW < 170 ){
                    nu = 1;
                } else if ( coW < 197 ){
                    nu = 2;
                } else {
                    nu = 3;
                }

                bool oncy = true;
                for (int i = 0; i < nu; i++){
					int a = rand() % 5;
					int b = rand() % 7;
					if ( reelWcount(a, grid, "WLD") < 3){
						cosInfo tupleW = addCosmetic( a,b, grid, betFactor, 5, 7, winningLines7, "WLD" );
                        if (tupleW.reel >= 0) {
                            grid = tupleW.screen;
                            reelMod newmod = { tupleW.reel, tupleW.pos, tupleW.symbol };
                            MOD.insert(newmod); // preserve info for (p)reconstructing spinning reels
                        }

                        if ( tupleW.win >= 50 * price *betFactor && oncy) {
                            oncy = false;
                            nu++; // gift more attempts in already successful spins
                        }
					}
				}
			}

			if (spinning && test_mode){
                if (!entry) { prespinMEGA(oldGrid, betFactor*winm, 7, wait, lgames, points, SPINS-1-i, totWin, simple, winm);}
                oldGrid = grid;
                entry = false;
				spinReelsMEGA( grid, 7, winTable, betFactor*winm, loanShark, simple, info, rSet, wait, totWin, modd, SPINS-1-i, MOD, winm);
			}

			map<string, int> irrWinCounts;
			winAm = calculateWins(grid, test_mode, irrWinCounts, betFactor*winm, winningLines7, true);
            totWin+= winAm;

            if (PRINTSCREEN % 100 == 0)
            {
            if (!test_mode && winAm >= 100 * price && winAm < 200 * price && PRINTSCREEN<=100) {
                printGrid(grid,7, false);
                cout << "game "<< fixed << setprecision(0)<< k+1 <<" (MEGA): " << fixed << setprecision(0)
                << winAm * 5 / winm << " × "<< winm << " = " << winAm * 5 << " ↑"<< endl;
            }
            if (!test_mode && winAm >= 200 * price && winAm < 500 * price && PRINTSCREEN<=200) {
                printGrid(grid,7,false);
                cout << "game "<< fixed << setprecision(0)<< k+1 <<" (MEGA): " << fixed << setprecision(0)
                << winAm * 5 / winm << " × "<< winm << " = " << winAm * 5 << " ↑"<< endl;
            }
            if (!test_mode && winAm >= 500 * price && PRINTSCREEN<=500) {
                printGrid(grid,7,false);
                cout << "game "<< fixed << setprecision(0)<< k+1 <<" (MEGA): " << fixed << setprecision(0)
                << winAm * 5 / winm << " × "<< winm << " = " << winAm * 5 << " ↑"<< endl;
            }
            }

            bool pressC = false;
            if (test_mode){
                cout << endl;
                print7(winTable, betFactor*winm, SPINS-1-i, simple);
                cout << endl;
                cout << "               M  E  G  A   R  E  E  L  S    \n";
                printGrid(grid,7);
                std::cout << std::setw(7) << std::left << "        total win: "
                      << std::setw(8) << totWin << "         "
                      << std::setw(7) << std::right
                      << std::fixed << std::setprecision(0) << winAm << " :win" << endl;
                if ( modd == 1 && (i==2 || i==5 || i==8) ){
                    if ( winAm >= 25*price*betFactor*std::min(winm,2) ){ // if multiplier is larger than 1 require pressing 'c' from 50*bet
                        cout <<  endl << "      good spin ! press 'c' to increase the win table"<< endl;
                        pressC = true;
                    } else {
                        cout <<  endl << "    press SPACE to increase the win table and continue"<< endl;
                    }
                } else if ( i == SPINS ) {
                    if ( winAm >= 25*price*betFactor*std::min(winm,2) ){
                        cout <<  endl << "      good spin ! press 'c' to finish the Mega Reels"<< endl;
                        pressC = true;
                    } else {
                        cout <<  endl << "      press SPACE to finish the Mega Reels"<< endl;
                    }
                } else {
                    if ( winAm >= 25*price*betFactor*std::min(winm,2) ){
                        cout <<  endl << "      good spin ! press 'c' to continue"<< endl;
                        pressC = true;
                    } else {
                        cout <<  endl << "      press SPACE to continue"<< endl;
                    }
                }

                if (simple && test_mode) {cout << endl;}
            }

            while (true && test_mode) {
                char keey = readFirstCharacter();
                if (keey == '*') { cheat = !cheat; }

                if (keey == '#') {
                    exit(0);
                } else if (!pressC || keey == 'c') {
                    cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl
					<< endl << endl;
                    break;
                }
            }
        }

        if (test_mode){
            if (simple && test_mode) {cout << endl << endl << endl;}
            cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl;



            cout << "          ┌──────────────────────────────────┐"<< endl;
            cout << "          │ B  O  N  U  S   E  N  D  I  N  G │"<< endl;
            cout << "          └──────────────────────────────────┘"<< endl;
            cout << "           F I N A L   W I N    :    ";
            if( totWin < 1000 ){cout << "  ";}
                std::string str = std::to_string(totWin);
            for (char digit : str) {
                if (digit == '.'){break;}
                std::cout << digit << " ";
            }
            cout << endl;

            if ( totWin >= 100*betFactor*price ) {
                cout << "          ┌──────────────────────────────────┐ " << endl;
                cout << "          │           /   '  ' \\             │" << endl;
                cout << "          │          /  _______ \\            │" << endl;
                cout << "          │  [$$]   /  /vVvVwvV\\ \\      [$$] │" << endl;
                cout << "          │        0  /wV      V\\ \\          │" << endl;
                cout << "          │ [$$]  /  /Vw ((())) V\\ \\ [$$]    │" << endl;
                cout << "          │      /  (Vv_________w| |         │" << endl;
                cout << "          │     /    \\ |       | / |   [$$]  │" << endl;
                cout << "          └─────┘     \\| $$$$$ |/  /─────────┘" << endl;
                } else if ( totWin >= 50*betFactor*price ) {
                cout << "          ┌──────────────────────────────────┐" << endl;
                cout << "          │                                  │" << endl;
                cout << "          │     [$$]                         │" << endl;
                cout << "          │                   ________       │" << endl;
                cout << "          │          [$$]     \\    0  \\      │" << endl;
                cout << "          │  [$$]              \\___    \\     │" << endl;
                cout << "          │                     VwV)    \\__  │" << endl;
                cout << "          │                [$$]  \\  )))   _\\ │" << endl;
                cout << "          └──────────────────────┘       └───┘" << endl;
            } else if ( totWin >= 10*betFactor*price ) {
                cout << "          ┌──────────────────────────────────┐" << endl;
                cout << "          │                                  │" << endl;
                cout << "          │             [$$]                 │" << endl;
                cout << "          │                                  │" << endl;
                cout << "          │                    ________      │" << endl;
                cout << "          │                    \\__  o  \\     │" << endl;
                cout << "          │     [$$]            Vw)     \\_   │" << endl;
                cout << "          │                      \\  )))  _\\  │" << endl;
                cout << "          └──────────────────────┘      └────┘" << endl;
            } else {
                cout << "          ┌──────────────────────────────────┐" << endl;
                cout << "          │                                  │" << endl;
                cout << "          │                                  │" << endl;
                cout << "          │                                  │" << endl;
                cout << "          │                    ________      │" << endl;
                cout << "          │                    \\__  x  \\     │" << endl;
                cout << "          │                     vv)     \\_   │" << endl;
                cout << "          │                      \\   ))  _\\  │" << endl;
                cout << "          └──────────────────────┘      └────┘" << endl;
            }

		cout << std::setw(7) << std::left << "        credit: " << points+totWin;
        if ( totWin >= 25 * price * betFactor ) {
                    if (totWin < 50 * price * betFactor) {
                        cout << "               ! BIG WIN ! ";
                    } else if ( totWin < 100 * price * betFactor ) {
                        cout << "             ! HUGE  WIN ! ";
                    } else if ( totWin < 200 * price * betFactor ) {
                        cout << "          ! ENORMOUS  WIN ! ";
                    } else if ( totWin < 500 * price * betFactor ) {
                        cout << "      ! UNBELIEVABLE  WIN !";
                    } else {
                        cout << "            ! INSANE  WIN !";
                    }
        }
		cout << endl<< endl << "      press SPACE to spin, 'b/d' to change the bet "<< endl;

		if (simple && test_mode) {cout << endl;}
	    bool betchanged = false;
        while (true) {
            char keey = readFirstCharacter();
            if (keey == '*') { cheat = !cheat; }
            if (keey == '#') { exit(0);}

            if (keey == 'b') {
                betchanged = true;

                betFactor = changeBet(betFactor, points+totWin, true, loanShark, lgames, simple);
            }
            else if (keey == 'd') {
                betchanged = true;

                betFactor = changeBet(betFactor, points+totWin, false, loanShark, lgames, simple);
            }
            else if (keey == 'c') {
                cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                break;
            }
            else {
                cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                break;
            }
        }
        if (simple && test_mode) {cout << endl << endl << endl;}
	}

    return {totWin, betFactor};
}


void SlotMachine(char modee, bool test_mode, map<string, int>& totalWinCounts, int betFactor, bool loanShark, char moddd, bool spinning, int wait) { // most central function

    bool freegameeverygame = false; // only for testing
    games = -1;
    double survWin; // current win (square root of the actual quantity of bets won)
    double survAvg; // used to compute the average number of games before survival credits are empty
    double survLength = 0; // used to save how long a survival game lasted
    double survCollect = 0; // used to collect data about how long the player survives
    int dead = 0; // tracks occurances of the credits reaching 0 and getting reset

    if (test_mode) { freegameeverygame = false;}

    int li[3]={};
    double averageline[3] = {};
    int FGcount = 0;
    double avgfg[6] = {}; // entries 0-2: total win in modes, 3-5: attempts in mode
    double totallines[3] = {}; // total numbers of length 3,4,5 lines in feature

    double lines3[18] = {}; // stores numbers of length 3 lines in each case 3-20 marked spaces
    double lines4[18] = {};
    double lines5[18] = {};

    double fwin[18] = {};
	double fun[18] = {};
    double markcount[18] = {};
    int hitfg[3] = {}; //0: number spins, 1: number wins, 2: number of shown draws (if redraw odds <100%)

    double tries = 0;// for fg reels hit rate
    double successes =0;
    int modes[3] = {};
    int winsize[5] = {}; // counts big, huge, enormous, unbelievable, insane wins

    double winsize2[7] = {}; // win sizes for x7, 0: zero win, 6: total entries
    double avg2 = 0;
	int nu;
	int lgames = 0; // games played in Loan Shark mode

    if (!test_mode) {
        betFactor = 1;
    }

    srand(time(0));
    int fgwin = 0; int fgwin2 = 0;
    int randomReels;

    int points = INITIAL_POINTS;

    double basewin = 0;
    double freewin = 0;
	double freewin2 = 0;
    double win = 0;
    double winAmount;
    double success = 0;

    double zero = 0;
    double winL[wlLength] = {0}; int kL[wlLength] = {0};

    if (!test_mode) {
        cout << endl << "    enter the number of simulated games: ";
        cin >> games;
        cout << endl;
    }

    bool fg = false;
	bool x7 = false;
    double k = 0;
    int fgmax = 0;
    int fgmax2 = 0;
    int million = 0;
    double fgcounter = 0;
    int reelset;
    int giveWin;
    map<string, int> irrCounts;

    double hitrate = success / games;
    double rtp = win / (games * price);
	bool rSet;
    unordered_set<reelMod> MOD;
    vector<vector<string>> oldGrid;
    bool spun = false;

    double survCredit = survInitial*price*betFactor; // tracks credits until they are empty and resets them in that case

    while ((test_mode && loanShark) || (points >= price * betFactor && test_mode) || (k < games && !test_mode)) { // runs until the simulation ends or the player is bankrupt

        WINi=0;
        survWin = 0;

        if (survCredit >= price*betFactor){
            survLength++;
        } else {
            survCredit = survInitial*price*betFactor;
            dead++;
            survCollect += sqrt(std::max(survLength - survInitial, zero )); //avoid numeric errors, in theory this root is always a real number
            survLength = 0;
        }

        survCredit -= price*betFactor;


        if (fg == true && test_mode) {
            cout << endl << "      press SPACE to spin, 'b/d' to change the bet"<< endl;
            if (simple && test_mode) {cout << endl;}
            while (true) {
                char keey = readFirstCharacter();
                if (keey == '*') { cheat = !cheat; }

	            if (keey == '#') { exit(0);}
				if (keey == 'q') { spun = false; return;}

                if ( keey == 'b') {
                    spun = false;
                    cout << endl;
                    betFactor = changeBet(betFactor, points, true, loanShark, lgames, simple);
                }
                else if ( keey == 'd') {
                    spun = false;
                    cout << endl;
                    betFactor = changeBet(betFactor, points, false, loanShark, lgames, simple);
                }
                else {
                    cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl<< endl << endl;
                    break;
                }
            }
            if (simple && test_mode) { cout << endl << endl << endl; }
        }

        if (test_mode) {
            points -= price * betFactor;
        }

        vector<vector<string>> grid;

        giveWin = rand() % 100;
		pair <vector<vector<string>>, vector<int>> draw;
		vector<int> info(2 * REEL_COUNT + 1);

        if (cheat) giveWin = 97;

        if(giveWin < 20)
        {
            do {
                reelset = rand() % 10000;

                if (reelset < 4370 ){
					rSet = true;
                    draw = generateGridInfo(reels1, reels2, reels3, reels1, ROW_COUNT);
					grid = draw.first;
					info = draw.second;
                } else {
					rSet = false;
                    draw = generateGridInfo(reels4, reels5, reels6, reels4, ROW_COUNT);
					grid = draw.first;
					info = draw.second;
                }
                winAmount = calculateWins(grid, test_mode, irrCounts, betFactor, winningLines, false);
                fg = checkTRG(grid);
                x7 = check7(grid);
            } while ( winAmount > 0 || fg || x7 ); // create non win, with original hit rate of ~22% unproblematic
        }
        else // regular spin with no discard or artificial non-win
        {
            reelset = rand() % 10000;

            if (reelset < 4370 ){
				rSet = true;
                draw = generateGridInfo(reels1, reels2, reels3, reels1, ROW_COUNT);
				grid = draw.first;
				info = draw.second;
            } else {
				rSet = false;
                draw = generateGridInfo(reels4, reels5, reels6, reels4, ROW_COUNT);
				grid = draw.first;
				info = draw.second;
			}
        }

        // BG CHEAT
        if (cheat) // only ever visited if manually chosen in the main menu ! ! ! ! !
        {
            for (int att = 1; att<4; att++)
            {
                winAmount = calculateWins(grid, test_mode, irrCounts, betFactor, winningLines, false);
                fg = checkTRG(grid);
                x7 = check7(grid);

                if (fg || x7)
                {
                    reelset = rand() % 100;
                    if (reelset < 77)
                        break;
                }

                if (winAmount > 0)
                {
                    reelset = rand() % 100;
                    if (winAmount > reelset * price * betFactor) break; // efficient but weird looking
                }

                reelset = rand() % 10000;
                if (reelset < 4370 ){
                    rSet = true;
                    draw = generateGridInfo(reels1, reels2, reels3, reels1, ROW_COUNT);
                    grid = draw.first;
                    info = draw.second;
                } else {
                    rSet = false;
                    draw = generateGridInfo(reels4, reels5, reels6, reels4, ROW_COUNT);
                    grid = draw.first;
                    info = draw.second;
                }
            }
        }

		if (test_mode && preMod){printGrid(grid,ROW_COUNT); readFirstCharacter(); } // for analysis/debugging

		if (test_mode) { MOD.clear(); }

        if ((test_mode && applyCOS ) || simulateCOS){

			tuple<int, string> testSet = countHVSymbols(grid);

			if (get<0>(testSet) >= 4 ){

				int rdd = rand() % 100;
				int rddd = rand() % 100;
				if ( rddd < 50 ){

					if ( get<0>(testSet) <= 5 ) {
						nu = (rdd < 31) ? 4 : 1;
					} else if ( get<0>(testSet) <= 6 ) {
						nu = (rdd < 41) ? 3 : 1;
					} else if ( get<0>(testSet) <= 7 ) {
						nu = (rdd < 32) ? 4 : 2;
					} else if ( get<0>(testSet) <= 9 ) {
						nu = (rdd < 29) ? 5 : 1;
					} else {
						nu = (rdd < 40) ? 4 : 2;
					}
				} else {
					nu = 0;
				}

				if ( rddd < 2 || rddd >= 98 ) { // 4% for random additional attempt
					nu += 1;
				}

				bool once = true;
				for (int i = 0; i < nu; i++){
					int a = rand() % 5;
					int b = rand() % 4;
					if ( isValidPosition( a,b, grid, get<1>(testSet) ) ){

                        cosInfo tuple = addCosmetic( a,b, grid, betFactor, 5, 4, winningLines, get<1>(testSet));
                        if (tuple.reel >= 0) {
                            grid = tuple.screen;
                            reelMod newmod = { tuple.reel, tuple.pos, tuple.symbol };
                            MOD.insert(newmod); // preserve info for (p)reconstructing spinning reels
                        }
                        if (once && tuple.reel >= 0) { // if the win is smaller than 5 bets and initially nu > 1, discard one cosmetic attempt
                            once = false;
                            if (tuple.win >= 125 * price *betFactor && tuple.reel >= 0) { //second condition is met only if the win did not change
                                nu+=2;
                            } else if (tuple.win >= 65 * price * betFactor && tuple.reel >= 0){
                                nu+=1;
                            } else if (tuple.win < 5 *price* betFactor && tuple.reel >= 0){
                                nu-=1;
                            }
                        }
					}
				}
			}
		}

		if ((test_mode && applyCOS ) || simulateCOS ){
			int coW = rand() % 100;
			int nu;
			if (coW < 87) {
				nu = 0;
			} else if ( coW < 99 ){
			    nu = 1;
			} else {
				nu = 2;
			}

			bool oncy = true;
			for (int i = 0; i < nu; i++){
                int a = rand() % 5;
                int b = rand() % 4;
                if ( reelWcount(a, grid, "WLD") < 2){ // avoid more than 3 visible wilds on any given reel
                    cosInfo tupleW = addCosmetic( a,b, grid, betFactor, 5, 4, winningLines, "WLD" );
                    if (tupleW.reel >= 0) {
                        grid = tupleW.screen;
                        reelMod newmod = { tupleW.reel, tupleW.pos, "WLD" };
                        MOD.insert(newmod);  // preserve info for (p)reconstructing spinning reels
                    }
                    if ( tupleW.win >= 100 * price *betFactor && oncy) {
                            oncy = false;
                            nu++; // gift more attempts in already successful spins
                    }
                }
            }
		}

		if (test_mode && spinning) {

            if(NEARWIN)
                longspin = nearWin( grid, winningLines, HVsymbols);
            else
                longspin = -1;

            if (spun) { prespinBG(oldGrid, betFactor, ROW_COUNT, wait, lgames, points); }
            vector<vector<string>> spinGrid = grid;
            oldGrid = grid;
			spinReelsBG( spinGrid, ROW_COUNT, winTable, betFactor, fg, x7, loanShark, lgames, simple, points, info, rSet, wait, MOD, longspin);
            spun = true;
		}

		// The win description needs to be recalculated here, the win didn't change but the types of wins might have
		winAmount = calculateWins(grid, test_mode, totalWinCounts, betFactor, winningLines, true);
        WINi+=winAmount;
        survWin+=winAmount;
        fg = checkTRG(grid);
        x7 = check7(grid);

        if (winAmount >= 25 * price * betFactor && !test_mode) { // tracks high win occurances, if desired prints out valuable reel screens during simulation
            if (winAmount < 50 * price * betFactor) { winsize[0]++;}
            else if (winAmount < 100 * price * betFactor) { winsize[1]++;}
            else if (winAmount < 200 * price * betFactor) {
                winsize[2]++;
                if (PRINTSCREEN <= 100) {printGrid(grid,ROW_COUNT,false); cout << "game "<< fixed << setprecision(0)<< k+1 <<" (base game): " << fixed << setprecision(0) << winAmount*5 << " ↑"<< endl;}
            }
            else if (winAmount < 500 * price * betFactor) {
                winsize[3]++;
                if (PRINTSCREEN <= 200) {printGrid(grid,ROW_COUNT,false); cout << "game "<< fixed << setprecision(0)<< k+1 <<" (base game): "  << fixed << setprecision(0) << winAmount*5 << " ↑"<< endl;}
            }
            else {
                winsize[4]++;
                if (PRINTSCREEN <= 500) {printGrid(grid,ROW_COUNT,false); cout << "game "<< fixed << setprecision(0)<< k+1 <<" (base game): "  << fixed << setprecision(0) << winAmount*5 << " ↑"<< endl;}
            }
        }

        if (test_mode) {
            points += winAmount;
            cout << endl;
			lgames++;
            print(winTable, betFactor, fg, x7, loanShark, lgames, simple);
        }

        if (forceTANK && test_mode)      { fg = true; x7 = false;}
        else if (forceMEGA && test_mode) { x7 = true; fg = false;}

        if (test_mode) {
            if (fg == true) {
                spun = false;
                cout << "        "<<invertUI<<" Y O U  W O N  T H E  S H A R K  T A N K" << currentUI << endl;
                printGrid(grid,ROW_COUNT);
            } else if (x7 == true){
                spun = false;
				cout << "        "<<invertUI<<" Y O U  W O N  T H E  M E G A  R E E L S" << currentUI  << endl;
                printGrid(grid,ROW_COUNT);
			}
        }

        // print playing field
        if (test_mode && fg == false && x7 == false) {
			if (loanShark) {
			cout << "              L O A N   S H A R K   M E G A \n";
			} else {
            cout << "              C A R D   S H A R K   M E G A \n";
			}
            printGrid(grid,ROW_COUNT);
        }

        win += winAmount;
        basewin += winAmount;

        if (test_mode) {
            // Print results
            std::cout << std::setw(7) << std::left << "        credit: "
                      << std::setw(8) << points << "            "
                      << std::setw(7) << std::right
                      << std::fixed << std::setprecision(0) << winAmount << " :win" << endl;

            if (winAmount < 25 * price * betFactor){

                if (!fg && !x7){ // just for readability
                    cout << endl << "      press SPACE to continue"<< endl;
                    if (simple && test_mode) {cout << endl;}
                    while (true) {
                        char keey = readFirstCharacter();
                        if (keey == '*') { cheat = !cheat; }

                        if (keey == '#') { exit(0);}
						if (keey == 'q') { spun = false; return;}
                        if ( keey == 'b' && !fg ) {
                            spun = false;

                            betFactor = changeBet(betFactor, points, true, loanShark, lgames, simple);
                        } else if ( keey == 'd' && !fg ) {
                            spun = false;

                            betFactor = changeBet(betFactor, points, false, loanShark, lgames, simple);
                        }
                        else {
                            cout << endl << endl << endl << endl << endl << endl << endl
                            << endl << endl << endl << endl << endl << endl << endl << endl;
                            break;
                       }
                   }
                   if (simple && test_mode) {cout << endl << endl << endl;}

                } else {
                    cout << endl << "      press 'c' to continue"<< endl;
                    if (simple && test_mode) {cout << endl;}

                    while (true) {
                        char keey = readFirstCharacter();
                        if (keey == '*') { cheat = !cheat; }

						if (keey == 'q') { spun = false; return;}
                        if (keey == '#') { exit(0);}
                        if (keey == 'c') {
                            cout << endl << endl << endl << endl << endl << endl << endl << endl << endl
                            << endl << endl << endl << endl << endl << endl << endl << endl;
                            break;
                       }
                   }
                   if (simple && test_mode) {cout << endl << endl << endl;}

                }
            } else {

                if (winAmount < 50 * price * betFactor) {                                        //bet 100: win >=  2500
                    cout << endl << "      BIG WIN ! press 'c' to continue playing" << endl;
                } else if (winAmount < 100 * price * betFactor) {                                 //bet 100: win >= 5000
                    cout << endl << "     HUGE WIN ! ! press 'c' to continue playing" << endl;
                } else if (winAmount < 200 * price * betFactor) {                                //bet 100: win >= 10000
                    cout << endl << "   ENORMOUS WIN ! ! ! press 'c' to continue playing" << endl;
                } else if (winAmount < 500 * price * betFactor) {                                //bet 100: win >= 20000
                    cout << endl << " UNBELIEVABLE WIN ! ! ! ! press 'c' to continue playing" << endl;
                } else {                                                                          //bet 100: win >= 50000
                    cout << endl << "  INSANE WIN ! ! ! ! ! press 'c' to continue playing" << endl;
                }

                bool betchanged = false;
                if (simple && test_mode) {cout << endl;}

                while (true) {
                    char keey = readFirstCharacter();
                    if (keey == '*') { cheat = !cheat; }

	                if (keey == '#') { exit(0);}
					if (keey == 'q') { spun = false; return;}

                    if (keey == 'b' && !fg) {
                        spun = false;
                        betchanged = true;
                        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                        betFactor = changeBet(betFactor, points, true, loanShark, lgames, simple);
                    } else if (keey == 'd' && !fg) {
                        spun = false;
                        betchanged = true;
                        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                        betFactor = changeBet(betFactor, points, false, loanShark, lgames, simple);
                    }
                    else if (keey == 'c') {
                        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                        break;
                    }
                    else if (betchanged){
                        cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                        break;
                    }
                }
                if (simple && test_mode) {cout << endl << endl << endl;}
            }
        }

        if ( freegameeverygame == true){ fg=true;}

        if (fg) {

            FGcount++;
            pair<int, int> res;
            res = simulateFG(spinning, modee, points, ROW_COUNT, COLUMN_COUNT, test_mode, betFactor, tries, successes,
			totallines, markcount, lines3, lines4, lines5, fwin, fun, averageline, li, modes, wait, k);
            fgwin = res.first;
            freewin += fgwin;
            points += fgwin;
            if ( res.second == 0 ){
                avgfg[0] += fgwin; avgfg[3]++;
            } else if ( res.second == 1 ){
                avgfg[1] += fgwin; avgfg[4]++;
            } else if ( res.second == 2 ){
                avgfg[2] += fgwin; avgfg[5]++;
            }

        } else if (x7){
            map<string, int> irrlvWinCounts;
            pair <int, int> result;
            result = simulatex7(wait, test_mode, betFactor, irrlvWinCounts, points, loanShark, lgames, spinning, k);
            fgwin2 = result.first;
            betFactor = result.second;
            points += fgwin2;
            freewin2 += fgwin2;
		}
		if (!fg){fgwin = 0;}
		if (!x7){fgwin2 = 0;}

        if(fg || x7){
            WINi+=fgwin+fgwin2;
            survWin+= fgwin+fgwin2;

            win += fgwin+fgwin2;

            if (BONUSPRINT)
            {
            if (fgwin > fgmax && !test_mode) {
                cout <<"game " << fixed << setprecision(0) << k+1 <<" (HIGHEST TANK): " << fixed << setprecision(0) << fgwin*5 << endl;
                // values for bet 100 ('*5')
                fgmax = fgwin;

            } else if (fgwin * 5 >= huge_win && !test_mode) {
                cout << "game " << fixed << setprecision(0) << k+1 <<" (INSANE TANK): " << fixed << setprecision(0) << k + 1 << ": " << fgwin*5 << endl;
            }
            if (fgwin2 > fgmax2 && !test_mode) {
                cout <<"game " << fixed << setprecision(0) << k+1 <<" (HIGHEST MEGA): " << fixed << setprecision(0) << fgwin2*5 << endl;
                // values for bet 100 ('*5')
                fgmax2 = fgwin2;

            } else if (fgwin2 * 5 >= huge_win && !test_mode) {
                cout << "game " << fixed << setprecision(0) << k+1 <<" (INSANE MEGA): " << fixed << setprecision(0) << k + 1 << ": " << fgwin2*5 << endl;
            }
            }

        }

        if (!test_mode){
            for (int i=0; i < wlLength-2; i++){
                if (fgwin+fgwin2+winAmount <= winLimit[i]*price && fgwin+fgwin2+winAmount > winLimit[i-1]*price ){
                    winL[i]+= fgwin+fgwin2+winAmount;
                    kL[i]++;
                    break;
                }
            }
            if (fgwin+fgwin2+winAmount > winLimit[wlLength-1]*price ) { // wins larger than 10000 bets
                winL[wlLength-1]+= fgwin+fgwin2+winAmount;
                kL[wlLength-1]++;
            }
        }

        if (survWin > 0){
            survWin *= scale_param;
            survCredit+=survWin;
        }

        if (winAmount > 0) { // this determines only the base game hit rate, as the (TANK) feature always guarantees a win and the triggers have no impact on whether there is a win (on reels 4,5), the exact hit rate with only the Shark Tank can be computed most precisely as 1-(1-p(basewin))*(1-p(feature))
            success++;
        }

        if (fg) {

            if (fg) { fgcounter++; }

            if (fgwin >= 25 * price * betFactor && !test_mode) { // track high feature win occurances
                if (fgwin < 50 * price * betFactor) { fgwinsize[0]++;}
                else if (fgwin < 100 * price * betFactor) { fgwinsize[1]++;}
                else if (fgwin < 200 * price * betFactor) { fgwinsize[2]++;}
                else if (fgwin < 500 * price * betFactor) { fgwinsize[3]++;}
                else { fgwinsize[4]++;}
            }
        }

        if (x7 && !test_mode) {
            points += fgwin2;
            avg2 += fgwin2;

            if (fgwin2 == 0) { winsize2[0]++; }// track high feature win occurances

            if (fgwin2 >= 25 * price * betFactor){
                if      (fgwin2 < 50 * price * betFactor)  { winsize2[1]++;}
                else if (fgwin2 < 100 * price * betFactor) { winsize2[2]++;}
                else if (fgwin2 < 200 * price * betFactor) { winsize2[3]++;}
                else if (fgwin2 < 500 * price * betFactor) { winsize2[4]++;}
                else                                       { winsize2[5]++;}
            }
            winsize2[6]++;
        }

        Xi+=WINi;
        Qi+=WINi*WINi;

        k++;
        million++;
        if ((million == statinterval && !test_mode && k < games) || k == games ) {
            million = 0;
            Sn = sqrt(Qi/((k-1)*(price*betFactor)*(price*betFactor)) - Qi/(k*(k-1)*(price*betFactor)*(price*betFactor)));
            cout << "________________________________________________________"<< endl;
            if (k == games) { cout << "Final"; } else { cout << "Current"; }
            cout << " values after " << fixed << setprecision(0) << k;
            if (cheat) cout << " CHEATED";
            cout << " games: " << endl << endl;

            hitrate = success / k;
            rtp = win / (k * price);
            double rtpLimit;

            cout << "Return to player:     " << fixed << setprecision(6) << rtp << endl;

            cout << "Base game RtP:        " << fixed << setprecision(6) << basewin / (k * price) << endl;
            cout << "Shark Tank RtP:       " << fixed << setprecision(6) << freewin / (k * price) << endl;
			cout << "Mega Reels RtP:       " << fixed << setprecision(6) << freewin2 / (k * price) << endl<< endl;
            cout << "Hit rate (base game): " << fixed << setprecision(6) << hitrate << endl;

            cout <<     "Standard derivation:  " << fixed << setprecision(6) << Sn;
            if (Sn < 2.5)       {cout << " (very low)" << endl;}
            else if (Sn < 5)    {cout << " (low)" << endl;}
            else if (Sn < 6.5)  {cout << " (medium)" << endl;}
            else if (Sn < 9)    {cout << " (high)" << endl;}
            else {cout << " (very high)" << endl;}
            cout << endl;

			if (dead > 0){
            cout << "Surv param " << fixed << setprecision(0) << setw(3) << survInitial << " bets:  "
            << fixed << setprecision(6) << survCollect / dead << endl << endl;
			}

			if (fgcounter > 0){
            cout << "Feature frequency:  " << fixed << setprecision(6) << k / fgcounter << endl<< endl;
			}
            cout << "Big wins:              " << std::setw(6) << std::right << winsize[0] << "   (25-49.99 bets)" << endl;
            cout << "Huge wins:             " << std::setw(6) << std::right << winsize[1] << "   (50-99.99 bets)" << endl;
            cout << "Enormous wins:         " << std::setw(6) << std::right << winsize[2] << "  (100-199.99 bets)" << endl;
            cout << "Unbelievable wins:     " << std::setw(6) << std::right << winsize[3] << "  (200-499.99 bets)" << endl;
            cout << "Insane wins:           " << std::setw(6) << std::right << winsize[4] << "    (500+ bets)" << endl<< endl;

            cout << "Mega Reels (with random modes of equal value): " << endl;
            cout << "zero wins:             " << std::setw(6) << std::right<< fixed << setprecision(0) << std::right << winsize2[0] << "        (0)" << endl;
            cout << "small wins:            " << std::setw(6) << std::right<< fixed << setprecision(0) << std::right
            << winsize2[6] - winsize2[0] - winsize2[1] - winsize2[2] - winsize2[3] - winsize2[4] - winsize2[5]
            << "  (0.01-24.99 bets)" << endl;
            cout << "Big wins:              " << std::setw(6) << std::right<< fixed << setprecision(0) << winsize2[1] << "   (25-49.99 bets)" << endl;
            cout << "Huge wins:             " << std::setw(6) << std::right<< fixed << setprecision(0) << winsize2[2] << "   (50-99.99 bets)" << endl;
            cout << "Enormous wins:         " << std::setw(6) << std::right<< fixed << setprecision(0) << winsize2[3] << "  (100-199.99 bets)" << endl;
            cout << "Unbelievable wins:     " << std::setw(6) << std::right<< fixed << setprecision(0) << winsize2[4] << "  (200-499.99 bets)" << endl;
            cout << "Insane wins:           " << std::setw(6) << std::right<< fixed << setprecision(0) << winsize2[5] << "    (500+ bets)" << endl;
            if (avg2 > 0) {cout << "avg Mega Reels win:    " << std::setw(6) << std::right<< fixed << setprecision(2) << avg2 / winsize2[6] * 5 << "  (at bet 100)" << endl;} // at bet 100
            cout << endl;

            cout << "Shark Tank: " << endl;
            cout << "Big wins:              " << std::setw(6) << std::right << fgwinsize[0] << "   (25-49.99 bets)" << endl;
            cout << "Huge wins:             " << std::setw(6) << std::right << fgwinsize[1] << "   (50-99.99 bets)" << endl;
            cout << "Enormous wins:         " << std::setw(6) << std::right << fgwinsize[2] << "  (100-199.99 bets)" << endl;
            cout << "Unbelievable wins:     " << std::setw(6) << std::right << fgwinsize[3] << "  (200-499.99 bets)" << endl;
            cout << "Insane wins:           " << std::setw(6) << std::right << fgwinsize[4] << "    (500+ bets)" << endl;
			if (fgcounter > 0){
            cout << "avg Shark Tank win:    " << fixed << setprecision(2) << (avgfg[0]+avgfg[1]+avgfg[2]) / (avgfg[3]+avgfg[4]+avgfg[5]) * 5 << "  (at bet 100)" << endl; // at bet 100
			}
			if (avgfg[3] > 0){
            cout << "      in normal mode:  " << fixed << setprecision(2) << avgfg[0] / avgfg[3] * 5  << endl; // at bet 100
			}
			if (avgfg[4] > 0){
            cout << "        in risk mode:  " << fixed << setprecision(2) << avgfg[1] / avgfg[4] * 5  << endl; // at bet 100
			}
			if (avgfg[5] > 0){
            cout << "       in shark mode:  " << fixed << setprecision(2) << avgfg[2] / avgfg[5] * 5  << endl; // at bet 100
			}

			if (fgcounter > 0){
            cout << endl << "Stats after " <<  setprecision(0) << fgcounter << " Shark Tank entries: " << endl;
			cout << "Lines of ";
			}
			if (totallines[0] > 0){
            cout << "length 3: " << fixed << setprecision(2) << totallines[0] / ( totallines[0]+ totallines[1]+ totallines[2]) * 100 << "%";
			}
			if (totallines[1] > 0){
            cout << ", 4: " << fixed << setprecision(2) << totallines[1] / ( totallines[0]+ totallines[1]+ totallines[2]) * 100 << "%";
			}
			if (totallines[2] > 0){
            cout << ", 5: " << fixed << setprecision(2) << totallines[2] / ( totallines[0]+ totallines[1]+ totallines[2]) * 100 << "%" << endl;
			}
            cout << "normal mode: " << modes[0] <<", risk: " << modes[1] << ", shark: " << modes[2] << endl << endl;

			if (fgcounter > 0){
            cout << "[$$]│ avg3 │ avg4 │ avg5 │  case  │ case win│ unmult" << endl;
            for (int m = 0; m < 18; m++)
            {
			if (fwin[m] > 0){
                cout << " " << std::setw(2)<< m+3
                << " │ " << std::setw(2)<<      fixed << setprecision(3) << lines3[m] / markcount[m]
                << "│ "      << std::setw(2)<< fixed << setprecision(3) << lines4[m] / markcount[m]
                << "│ "      << std::setw(2)<< fixed << setprecision(3) << lines5[m] / markcount[m]
                << "│ "      << std::setw(6)<< fixed << setprecision(3) << markcount[m] / FGcount * 100 << "%"
                << "│ "     << fixed << setprecision(1) << std::setw(8) << fwin[m] / markcount[m] * 5 << "│" << fixed << setprecision(2) << setw(8) << right << fun[m] / markcount[m] * 5   << endl; // wins at bet 100
			}
            }
            cout << endl << "Avg win at line length 3:" << std::setw(6)<< fixed << setprecision(2) << averageline[0] / li[0] *5 << ", 4: "
                                                                       << std::setw(6)<< fixed << setprecision(2) << averageline[1] / li[1] *5 << ", 5: "
                                                                       << std::setw(6)<< fixed << setprecision(2) << averageline[2] / li[2] *5 << endl;
			}
            if (( (simulateLIM && printWSIZE==1 ) || (simulateLIM && printWSIZE==2 && k == games) || (k == games && games >= 100000000) ) && win > 0){
                cout << endl << "RtP distribution by upper bound in #bets ('■' = 0.1%):" << endl;

                int max = 0;
                for (int i = 0; i < wlLength-2; i++){
                    if (kL[i]>0) max = i+1;
                }
                for (int i = 0; i < max; i++){
                    rtpLimit = winL[i] / (k * price);
                    cout << fixed << setprecision(0) << setw(4) << winLimit[i] <<"│" << fixed << setprecision(3) << setw(6) << rtpLimit*100 << "% ";
                    if (kL[i]>0) { printDia(rtpLimit); cout << " " << kL[i]; }
                    cout << endl;
                }
                rtpLimit = winL[wlLength-1] / (k * price);

                if (max != wlLength-1) cout << " ...│ ......  0" << endl;
                cout << "10k+│" << fixed << setprecision(3) << setw(6) << rtpLimit*100 << "% "; if (kL[wlLength-1]>0) { printDia(rtpLimit); cout << " " << kL[wlLength-1];}
                cout << endl;
            }
            printTWC(totalWinCounts); // only prints if selected in the main menu
        }
    }

    if (test_mode) {
        cout << endl << endl << endl << endl << endl << endl << endl << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< "                       GAME OVER!"
        << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl;

        cout << "         press 'c' to go back to the main menu" << endl << endl;
        if (simple && test_mode) {cout << endl;}

        while (true) {
            char keey = readFirstCharacter();
            if (keey == '*') { cheat = !cheat; }

            if (keey == '#') { exit(0);}

            else if (keey == 'c') {
                cout << endl << endl << endl << endl << endl;
                break;
            }
        }
        if (simple && test_mode) {cout << endl << endl << endl;}
    }
}


int main() { // enter the slot machine either in test_mode or !test_mode from the main menu

    setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
	bool spinning = true;

    #ifdef _WIN32
		SetConsoleOutputCP(CP_UTF8);
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
		SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
		// SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_BLUE);
    #else
        // Set color for Unix-like systems (Linux/macOS): Magenta text on Black background
        cout << "\033[48;5;0m\033[38;5;206m"; // black background, purple foreground
    #endif

    map<string, int> totalWinCounts;
    bool test_mode = false;

    winLimit[240] = 10000; // everything above 10000 bets
    for (int w=1; w < 51; w++ ){
        winLimit[w-1] = w; // set values 0,1,...,50
    }
    for (int w=1; w < 26; w++ ){
        winLimit[w-1+50] = 50 + 2*w; // set values 52,54,...,100
    }
    for (int w=1; w < 26; w++ ){
        winLimit[w-1+75] = 100 + 4*w; // set values 104,108,...,200
    }
    for (int w=1; w < 21; w++ ){
        winLimit[w-1+100] = 200 + 5*w; // set values 205,210,...,300
    }
    for (int w=1; w < 21; w++ ){
        winLimit[w-1+120] = 300 + 10*w; // set values 310,320,...,500
    }
    for (int w=1; w < 26; w++ ){
        winLimit[w-1+140] = 500 + 20*w; // set values 520,540,...,1000
    }
    for (int w=1; w < 31; w++ ){
        winLimit[w-1+165] = 1000 + 50*w; // set values 1050,1100,...,2500
    }
    for (int w=1; w < 26; w++ ){
        winLimit[w-1+195] = 2500 + 100*w; // set values 2600,2700,...,5000
    }
    for (int w=1; w < 21; w++ ){
        winLimit[w-1+220] = 5000 + 250*w; // set values 5250,5500,...,10000 = max
    }

	char mode;

	int wait = 50;
	int wsize = 16;
    int statoptionssize = 9;
	int waitmodes[16] = {10,17,22,27,31,35,40,45,50,55,60,65,70,77,100,250};
    int statoptions[9] = {10000, 50000, 100000, 250000, 500000, 1000000, 5000000, 10000000, -1};

    makespinsconsistantlyquickviaprinting();

    pair <TSTYLE, map<string, string>> innit;
    innit = changeTranslator(CardKoi);
    DEFAULT_STYLE = innit.first;
    symbolTranslator = innit.second;

    char key_handbook =    'g';
    char key_stats =       'i';
    char key_color =       'h';
    char key_ui =          'u';
    char key_symbol =      'd';
    char key_fat =         'f';
    char key_boxed =       'b';
    char key_loan =        'l';
    char key_credit =      'm';
    char key_spinning =    'r';
    char key_velocity =    'v'; char key_Mvelocity = 'x';
    char key_spinmod =     's';
    char key_animation =   'a';
    char key_cheats =      'c';

    char key_simulate =    '0';
    char key_interval =    '1';
    char key_strategy =    '2';
    char key_screenprint = '3';
    char key_notes =       '4';
    char key_RtP =         '5';
    char key_winstats =    '6';

    while (true) {

		mode = 'i';
		while ( mode == key_handbook || mode == key_stats ||  mode == key_color ||  mode == key_ui
            ||  mode == key_symbol ||  mode == key_fat ||  mode == key_boxed ||  mode == key_loan
            ||  mode == key_credit ||  mode == key_spinning ||  mode == key_velocity || mode == key_Mvelocity ||  mode == key_spinmod
            ||  mode == key_animation ||  mode == key_interval ||  mode == key_strategy ||  mode == key_screenprint
            ||  mode == key_notes ||  mode == key_RtP ||  mode == key_winstats || mode == key_cheats || mode == 'q')
        {

        if (loanShark) {INITIAL_POINTS = 0;}
        #ifdef _WIN32
        #else
        if (DEFAULT_COLOR == magenta){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;206m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;206m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;206m";
        } else if (DEFAULT_COLOR == purple){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;129m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;129m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;129m";
        } else if (DEFAULT_COLOR == blue){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;252m\033[38;5;27m";
            else
                currentUI = "\033[22m\033[48;5;252m\033[38;5;27m";
            invertUI = "\033[1m\033[38;5;252m\033[48;5;27m";
        } else if (DEFAULT_COLOR == green){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;37m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;37m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;37m";
        } else if (DEFAULT_COLOR == red){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;1m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;1m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;1m";
        } else if (DEFAULT_COLOR == white){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;253m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;253m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;253m";
        } else if (DEFAULT_COLOR == gray){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;246m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;246m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;246m";
        } else if (DEFAULT_COLOR == vinyl){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;52m\033[38;5;159m";
            else
                currentUI = "\033[22m\033[48;5;52m\033[38;5;159m";
            invertUI = "\033[1m\033[38;5;52m\033[48;5;159m";
        } else if (DEFAULT_COLOR == wario){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;214m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;214m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;214m";
        } else if (DEFAULT_COLOR == mint){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;15m\033[38;5;37m";
            else
                currentUI = "\033[22m\033[48;5;15m\033[38;5;37m";
            invertUI = "\033[1m\033[38;5;15m\033[48;5;37m";
        } else if (DEFAULT_COLOR == neww1){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;93m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;93m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;93m";
        } else if (DEFAULT_COLOR == neww2){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;141m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;141m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;141m";
        } else if (DEFAULT_COLOR == neww3){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;158m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;158m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;158m";
        } else if (DEFAULT_COLOR == neww4){
            if (FAT_UI)
                currentUI = "\033[1m\033[48;5;16m\033[38;5;21m";
            else
                currentUI = "\033[22m\033[48;5;16m\033[38;5;21m";
            invertUI = "\033[1m\033[38;5;16m\033[48;5;21m";
        }
        #endif

        setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
        cout << endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl<< endl
		<< endl<< endl;

        cout << "    adjust the console such that the outer rectangle"<< endl;
        cout << "    around the main menu is fully visible (not this)"<< endl<< endl;
        cout << "┌──────────────────────────┬──────┬──────┬──────┬──────┐"<< endl;
        cout << "│  ";colorDemo();cout << "  │ ";
        printTestSymbols();
        cout <<" │"<< endl;
        cout << "├──────────────────────────┴──────┴──────┴──────┴──────┤"<< endl;
        for (int scr = 0; scr<0; scr++){ //just for quick changes
            cout << "│                                                      │"<< endl;
        }
        #ifdef _WIN32
        cout << "│                       ___     __               _     │"<< endl;
        cout << "│   ___ _____ _____  __| _/____|  |_ _____ _____| | __ │"<< endl;
        cout << "│ _/ __\\\\__  \\\\_ _ \\/ __ |/  __/  | \\\\__  \\\\_   \\ |/ / │"<< endl;
        cout << "│ \\  \\__ / __ \\| |\\/ /_/ |\\__ \\|  _  \\/ __ \\| |\\/   <  │"<< endl;
        cout << "│  \\____(____  /_| \\____ |/____)__|__(______/_| |_|_ \\ │"<< endl;
        cout << "│            \\/         \\/     _   _  ____ ___  __  \\/ │"<< endl;
        #else
        cout << "│\033[1m                       ___     __               _     "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│\033[1m   ___ _____ _____  __| _/____|  |_ _____ _____| | __ "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│\033[1m _/ __\\\\__  \\\\_ _ \\/ __ |/  __/  | \\\\__  \\\\_   \\ |/ / "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│\033[1m \\  \\__ / __ \\| |\\/ /_/ |\\__ \\|  _  \\/ __ \\| |\\/   <  "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│\033[1m  \\____(____  /_| \\____ |/____)__|__(______/_| |_|_ \\ "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│\033[1m            \\/         \\/     _   _  ____ ___  __  \\/ "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        #endif
        cout << "│  SPACE  »    ";
        #ifdef _WIN32
        #else
        cout << invertUI;
        #endif
        cout << " P L A Y ";
        #ifdef _WIN32
        #else
        cout << currentUI;
        #endif
        #ifdef _WIN32
        cout <<"      | \\ | \\/ __//   \\/  \\    │"<< endl;
        cout << "│   '"<< key_handbook <<"'   »  show user guide  |  \\|  | _|/ /\\_/  \\ \\   │"<< endl;
        cout << "│   '"<< key_stats <<"'   »  show math info   | _  _ |   \\ \\( \\  _  )  │"<< endl;
        cout << "│   '#'   »  exit program     |_|\\// /___|\\___/\\_|_ \\  │"<< endl;
		cout << "│   '"<< key_color <<"'   »  cycle HV colors       \\/              \\/  │"<< endl;
        #else
        cout <<"\033[1m      | \\ | \\/ __//   \\/  \\    "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│   '"<< key_handbook <<"'   »  show user guide  \033[1m|  \\|  | _|/ /\\_/  \\ \\   "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│   '"<< key_stats <<"'   »  show math info   \033[1m| _  _ |   \\ \\( \\  _  )  "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        cout << "│   '#'   »  exit program     \033[1m|_|\\// /___|\\___/\\_|_ \\  "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
		cout << "│   '"<< key_color <<"'   »  cycle HV colors       \033[1m\\/              \\/  "; if (!FAT_UI) cout << "\033[22m"; cout<<"│"<< endl;
        #endif
        cout << "│   '"<< key_ui <<"'   »  cycle UI colors            ";
        string dc = "["s + toString(DEFAULT_COLOR) + "]";
        cout << left << setw(9) << dc;
        cout << "      │"<< endl;
        cout << "│   '"<< key_symbol <<"'   »  cycle symbol designs       ";
        string ds = "["s + toString(DEFAULT_STYLE) + "]";
        cout << left << setw(12) << ds;
        cout << "   │"<< endl;
        cout << "│   '"<< key_fat <<"'   »  toggle fat UI              ";
        if (FAT_UI){ cout << "[ON] ";} else { cout << "[OFF]";}
		cout << "          │"<< endl;
        cout << "│   '"<< key_boxed <<"'   »  toggle boxed HV design     ";
        if (HVbox){ cout << "[ON] ";} else { cout << "[OFF]";}
        cout << "          │"<< endl;
        cout << "│   '"<< key_loan <<"'   »  toggle loan shark mode     ";
        if (loanShark){ cout << "[ON] ";} else { cout << "[OFF]";}
        cout << "          │"<< endl;
		cout << "│   '"<< key_credit <<"'   »  cycle deposited money      ";
        ostringstream oss;
        oss << "[" << INITIAL_POINTS << "]";
        string sc = oss.str();
        cout << left << setw(9) << sc;
		cout << "      │"<< endl;
		cout << "│   '"<< key_spinning <<"'   »  toggle reel spinning       ";
		if (spinning){ cout << "[ON] ";} else { cout << "[OFF]";}
		cout << "          │"<< endl;
		cout << "│   '"<< key_velocity <<"'   »  cycle reel spin velocity   ";
		cout << "[" << wait << "] "; if (wait < 100) cout << " ";if (wait < 10) cout << " "; cout << "         │"<< endl;
        cout << "│   '"<< key_spinmod <<"'   »  toggle spin mods           ";
        if (NEARWIN){ cout << "[ON] ";} else { cout << "[OFF]";}
        cout << "          │"<< endl;
		cout << "│   '"<< key_animation <<"'   »  change win animations      ";
        if (animate == 0) cout <<      "[fast]   ";
        else if (animate == 1) cout << "[medium] ";
        else if (animate == 2) cout << "[slow]   ";
        else                   cout << "[OFF]    ";
        cout << "      │"<< endl;
        cout << "│   '"<< key_cheats <<"'   »  toggle cheats           ";
        if (cheat){ cout << "!  [ON] ";} else { cout << "   [OFF]";}
        cout << "          │"<< endl;
        cout << "│   '"<< key_simulate <<"'   »    ";
        #ifdef _WIN32
        #else
        cout << invertUI;
        #endif
        cout << " S I M U L A T E ";
        #ifdef _WIN32
        #else
        cout << currentUI;
        #endif
        cout << "                       │"<< endl;
        cout << "│   '"<< key_interval <<"'   »  change output intervals    ";
        if (statinterval != -1){
        ostringstream osss;
        osss << "[" << statinterval << "]";
        string oi = osss.str();
        cout << left << setw(10) << oi;
        } else cout << "[infinity]"; cout << "     │"<< endl;
        cout << "│   '"<< key_strategy <<"'   »  change feature strategy    ";
        if (FMODES == -1) cout <<     "[random] ";
        else if (FMODES == 0) cout << "[normal] ";
        else if (FMODES == 1) cout << "[risk]   ";
        else if (FMODES == 2) cout << "[shark]  ";
        cout << "      │" << endl;
        cout << "│   '"<< key_screenprint <<"'   »  change screen prints       ";
        if (PRINTSCREEN == 999) cout <<      "[never]      ";
        else if (PRINTSCREEN == 100) cout << "[100 × bet]  ";
        else if (PRINTSCREEN == 200) cout << "[200 × bet]  ";
        else if (PRINTSCREEN == 500) cout << "[500 × bet]  ";
        else if (PRINTSCREEN ==  99) cout << "[100 only BG]";
        else if (PRINTSCREEN == 199) cout << "[200 only BG]";
        else if (PRINTSCREEN == 499) cout << "[500 only BG]";
        cout << "  │"<< endl;
        cout << "│   '"<< key_notes <<"'   »  toggle feature win notes   ";
        if (BONUSPRINT) cout << "[ON] "; else  cout << "[OFF]";
        cout << "          │"<< endl;
        cout << "│   '"<< key_RtP <<"'   »  change RtP distribution    ";
        if (printWSIZE == 2) cout <<      "[at the end]";
        else if (printWSIZE == 1) cout << "[always]    ";
        else if (printWSIZE == 0) cout << "[never]     ";
        cout << "   │"<< endl;
        cout << "│   '"<< key_winstats <<"'   »  change win stats print     ";
        if (TWC == 2) cout <<      "[at the end]";
        else if (TWC == 1) cout << "[always]    ";
        else if (TWC == 0) cout << "[never]     ";
        cout << "   │"<< endl;
        cout << "└──────────────────────────────────────────────────────"; // cursor stops here

        //if (simple && test_mode) {cout << endl;}

        mode = readFirstCharacter();

        if (mode == '#') { exit(0);}
        cout << endl;

        if (mode == key_stats) { stats(); }
        else if (mode == key_handbook) { controls(); }
        else if (mode == key_cheats) { cheat = !cheat; }
        else if (mode == key_screenprint) {
            if (PRINTSCREEN == 999)      PRINTSCREEN = 100;
            else if (PRINTSCREEN == 100) PRINTSCREEN = 200;
            else if (PRINTSCREEN == 200) PRINTSCREEN = 500;
            else if (PRINTSCREEN == 500) PRINTSCREEN =  99;
            else if (PRINTSCREEN ==  99) PRINTSCREEN = 199;
            else if (PRINTSCREEN == 199) PRINTSCREEN = 499;
            else if (PRINTSCREEN == 499) PRINTSCREEN = 999;
        }
        else if (mode == key_winstats) {
            if (TWC == 2)      TWC = 1;
            else if (TWC == 1) TWC = 0;
            else if (TWC == 0) TWC = 2;
        }
        else if (mode == key_strategy) {
            if (FMODES == -1)     FMODES = 0;
            else if (FMODES == 0) FMODES = 1;
            else if (FMODES == 1) FMODES = 2;
            else if (FMODES == 2) FMODES = -1;
        }
        else if (mode == key_color)
        {
            if (colorsceme == c1 ) colorsceme = c2;
            else if (colorsceme == c2 ) colorsceme = c3;
            else if (colorsceme == c3 ) colorsceme = c4;
            else if (colorsceme == c4 ) colorsceme = c5;
            else if (colorsceme == c5 ) colorsceme = c1;
        }
		else if (mode == key_spinning) { spinning = !spinning;
            if(spinning) wait = 50;
            else wait = 0;
            if(spinning) animate = 1;
            else animate = -1;
        }
        else if (mode == key_animation) {
            if (animate == 2 )      animate = 1;
            else if (animate == 1 ) animate = 0;
            else if (animate == 0 ) animate = -1;
            else if (animate == -1 ) animate = 2;
            spinning = true; // even if this 'g'-press deactivated the animation (-> -1) spinning must have been true anyways
            if (wait == 0) wait = 50;
        }
		else if (mode == key_boxed) { HVbox = !HVbox;}
		else if (mode == key_notes) { BONUSPRINT = !BONUSPRINT;}
		else if (mode == key_fat) { FAT_UI = !FAT_UI; setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);}
		else if (mode == key_symbol) {
            pair <TSTYLE, map<string, string>> result;
            result = changeTranslator(DEFAULT_STYLE);
            DEFAULT_STYLE = result.first;
            symbolTranslator = result.second;
        }
		else if (mode == key_ui) {
            if (DEFAULT_COLOR == purple) { DEFAULT_COLOR = magenta;}
            else if (DEFAULT_COLOR == magenta) { DEFAULT_COLOR = blue;}
            else if (DEFAULT_COLOR == blue) { DEFAULT_COLOR = green;}
            else if (DEFAULT_COLOR == green) { DEFAULT_COLOR = red;}
            else if (DEFAULT_COLOR == red) { DEFAULT_COLOR = white;}
            else if (DEFAULT_COLOR == white) { DEFAULT_COLOR = gray;}
            else if (DEFAULT_COLOR == gray) { DEFAULT_COLOR = mint;}
            else if (DEFAULT_COLOR == mint) { DEFAULT_COLOR = wario;}
            else if (DEFAULT_COLOR == wario) { DEFAULT_COLOR = vinyl;}
            else if (DEFAULT_COLOR == vinyl) { DEFAULT_COLOR = neww1;}
            else if (DEFAULT_COLOR == neww1) { DEFAULT_COLOR = neww2;}
            else if (DEFAULT_COLOR == neww2) { DEFAULT_COLOR = neww3;}
            else if (DEFAULT_COLOR == neww3) { DEFAULT_COLOR = neww4;}
            else if (DEFAULT_COLOR == neww4) { DEFAULT_COLOR = purple;}

            setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox);
        }
		else if (mode == key_interval) {
            int idx = 0;
			for (int i = 0; i < statoptionssize; i++) {
				if (statoptions[i] == statinterval) {
                    idx = i;
				}
			}
			statinterval = statoptions[(idx + 1) % statoptionssize];
        }
		else if (mode == key_RtP) {
            if (printWSIZE == 2)      printWSIZE = 1;
            else if (printWSIZE == 1) printWSIZE = 0;
            else if (printWSIZE == 0) printWSIZE = 2;
        }
		else if (mode == key_spinmod) { NEARWIN = !NEARWIN;}
		else if (mode == key_velocity) {
            if (wait == 0) spinning = true;

			int index = 0;
			for (int i = 0; i < wsize; i++) {
				if (waitmodes[i] == wait) {
                    index = i;
				}
			}
			wait = waitmodes[(index - 1 + wsize) % wsize];
		}
		else if (mode == key_Mvelocity) {
			int index = 0;
			for (int i = 0; i < wsize; i++) {
				if (waitmodes[i] == wait) {
                    index = i;
				}
			}
			wait = waitmodes[(index + 1) % wsize];
		}
		else if (mode == key_loan) { loanShark = !loanShark; INITIAL_POINTS = 10000; }
        else if (mode == key_credit)
        {
            if (INITIAL_POINTS == 500) { INITIAL_POINTS = 1000; }
            else if (INITIAL_POINTS == 1000) { INITIAL_POINTS = 2000; }
            else if (INITIAL_POINTS == 2000) { INITIAL_POINTS = 5000; }
            else if (INITIAL_POINTS == 5000) { INITIAL_POINTS = 10000; }
            else if (INITIAL_POINTS == 10000) { INITIAL_POINTS = 20000; }
            else if (INITIAL_POINTS == 20000) { INITIAL_POINTS = 50000; }
            else if (INITIAL_POINTS == 50000) { INITIAL_POINTS = 100000; }
            else if (INITIAL_POINTS == 100000) { INITIAL_POINTS = 1000000; }
            else if (INITIAL_POINTS == 1000000) { INITIAL_POINTS = 500; }
        }
		}

		setTextColor("RESET", DEFAULT_COLOR, FAT_UI, HVbox); // ensure that text is also displayed correctly outside of the slot machine

        if (mode != '0') {
            test_mode = true;
			if (loanShark) {INITIAL_POINTS = 0;}

            betFactor = 5; // start with bet 100 again
            cout << endl<< endl<< endl<< endl<< endl;

            info();
            if (simple && test_mode) {cout << endl << endl << endl;}

            cout << endl << endl << endl << endl;
            print(winTable, betFactor, false, false, false, 0, simple);
            if (!loanShark){
                cout << "            "<< invertUI << "  G  O  O  D     L  U  C  K   ! "<< currentUI << endl;
            }else{
                cout << "       "<< invertUI <<      "       G  O  O  D     L  U  C  K   !      "<< currentUI << endl;
                cout << "       "<< invertUI <<      " Y  O  U   W  I  L  L   N  E  E  D   I  T "<<currentUI << endl;
			}
			cout << "          ┌──────────────────────────────────┐" << endl;
			if (!loanShark) {
            cout << "          │  [$$]                [$$]        │" << endl;
			}
            cout << "          │                                  │" << endl;
            cout << "          │          [$$]                    │" << endl;
            cout << "          │                    _______  [$$] │" << endl;
            cout << "          │                    \\__ o  \\      │" << endl;

			if (loanShark){
			cout << "          │  more like          Vw)    \\__   │" << endl;
            cout << "          │   debts       [$$]   \\  )))  _\\  │" << endl;
            cout << "          V                      /      |────┘" << endl;
			} else {
            cout << "          │   [$$]              Vw)    \\__   │" << endl;
            cout << "          │                      \\  )))  _\\  │" << endl;
            cout << "          └──────────────────────┘      └────┘" << endl;
			}
            cout << "        credit: " << INITIAL_POINTS << endl;

            cout << endl << "      press SPACE to start the first spin" << endl;
            if (simple && test_mode) {cout << endl;}
            while (true) {
                char keyyy = readFirstCharacter();
                if (keyyy == '*') { cheat = !cheat; }
	            if (keyyy == '#') { exit(0);}
                if (keyyy == 'b') {
                    betFactor = changeBet(betFactor, INITIAL_POINTS, true, false, 0, simple);
                } else if (keyyy == 'd') {
                    betFactor = changeBet(betFactor, INITIAL_POINTS, false, false, 0, simple);
                } else {
                    cout << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                    break;
                }
            }
            if (simple && test_mode) {cout << endl << endl << endl;}
        } else { // reset stats where necessary
            totalWinCounts.clear();
            for (int i=0; i<4; i++){
                fgwinsize[i]=0;
            }
            test_mode = false;
            betFactor = 1;
        }

        SlotMachine(mode, test_mode, totalWinCounts, betFactor, loanShark, mode, spinning, wait);

        Qi = 0.0; // reset standard dervation

        if (!test_mode) { // only bother to print anything if there are wins at all

            if (!totalWinCounts.empty() && (TWC==2 || games >= 100000000)){
                cout << endl << "Total number of hits by win combination: " << endl;
                for (const auto& entry : totalWinCounts) {
                    cout << setw(10) << right << entry.second  << " │ " << entry.first << endl;
                }
            }
            cout << endl;

            cout << "      press 'c' to continue"<< endl;

            if (simple && test_mode) {cout << endl;}

            while (true) {
                char keey = readFirstCharacter();
                if (keey == '*') { cheat = !cheat; }

                if (keey == '#') { exit(0);}

                else if (keey == 'c') {
                    cout << endl << endl << endl << endl << endl << endl << endl << endl
                    << endl << endl << endl << endl << endl << endl << endl << endl << endl;
                    break;
                }
            }
        }
    }
    return 0;
}


/* ABOUT:

This simulation is designed as a simple tool to gather a quick overview of how often common game events occur,
how they feel like and what a typical player experience might look like early in development.
It runs both on Windows and Linux, while only the latter provides the full range of adjustment options.
While it also offers a simulation mode (!test_mode) the most important function of this code is to print out
live reel screens in adjustable frequency, up to around 25 spins a second dependant on the system it is run on.
This enables developers to play test much quicker and earlier in development than it would be possible if testing
was only done on slot machines with demo software. Pressing and holding any key (except '#') repeatedly spins the
reels to fast forward an otherwise longer testing session.
When special game events occur the simulation specifically asks the user to press 'c' to continue or 'n', 'r', 's'
to select a feature mode. This way the game's key behavior can be observed comparatively quickly. Optionally, the
reels can be set to spin at a chosen velocity. The reel screen is automatically cosmetically modified
before the spin animation starts.

*/

/* GAME INFO:

This is a variation of the game Card Shark which was developed to provide an example of a feature that embodies a
concept of collecting abstract entities on every single visible position of a reel screen but at the same time has
a much wider spread of (perceived) outcomes that can be geometrically interpreted to a deeper extent than typical
Super Spin games. At the same time larger wins are much easier to remember if they don't just occur as a single
random event but follow clear patterns, which allow the player to understand how (un)likely the current attempt
is to win considerable amounts (vaguely speaking 100-7000 bets). Additionally, much potential is wasted if the
player doesn't actively get the chance to see how close they came to a particulary appealing win. While this can
be established for any game concept, the way the Shark Tank feature does this incorporates multiple nuances from
a variety of already successfull games in a completely new way. All game parts use the set of all conected winning
lines from left to right, which in the case of the Mega Bonus means 421 instead of the regular 178 lines.

*/


/* MAIN STATS: (3.14 billion games)

Return to player:     0.972154
Base game RtP:        0.627505
Shark Tank RtP:       0.172176
Mega Reels RtP:       0.172473

Hit rate (base game): 0.154202
Standard derivation:  10.135444 (very high)

Surv param 100 bets:  8.407276

Feature frequency:  279.364128

Big wins:              8718169   (25-49.99 bets)
Huge wins:             3230937   (50-99.99 bets)
Enormous wins:         868396  (100-199.99 bets)
Unbelievable wins:     260947  (200-499.99 bets)
Insane wins:            29903    (500+ bets)

Mega Reels (with random modes of equal value):
zero wins:             560971        (0)
small wins:            5452360  (0.01-24.99 bets)
Big wins:              2412302   (25-49.99 bets)
Huge wins:             1604939   (50-99.99 bets)
Enormous wins:         772285  (100-199.99 bets)
Unbelievable wins:     359613  (200-499.99 bets)
Insane wins:            79460    (500+ bets)
avg Mega Reels win:    4817.37  (at bet 100)

Shark Tank:
Big wins:              2733823   (25-49.99 bets)
Huge wins:             629542   (50-99.99 bets)
Enormous wins:         584303  (100-199.99 bets)
Unbelievable wins:     354481  (200-499.99 bets)
Insane wins:            89352    (500+ bets)
avg Shark Tank win:    4809.98  (at bet 100)
      in normal mode:  4786.24
        in risk mode:  4784.99
       in shark mode:  4858.75

Stats after 11239811 Shark Tank entries:
Lines of length 3: 37.21%, 4: 33.79%, 5: 29.00%
normal mode: 3745698, risk: 3749536, shark: 3744577

[$$]│ avg3 │ avg4 │ avg5 │  case  │ case win│ unmult
  3 │ 2.000│ 0.000│ 0.000│  0.582%│     89.3│   89.31
  4 │ 0.977│ 1.139│ 0.000│  0.716%│    296.8│  296.78
  5 │ 1.419│ 0.411│ 0.622│  1.015%│    725.1│  725.09
  6 │ 2.085│ 0.849│ 0.172│  1.433%│    446.6│  446.60
  7 │ 1.775│ 1.122│ 0.388│  2.732%│    693.2│  693.19
  8 │ 1.783│ 1.158│ 0.667│  4.017%│    958.4│  958.44
  9 │ 1.910│ 1.388│ 0.790│  5.191%│   1130.1│ 1130.11
 10 │ 2.051│ 1.542│ 0.945│  6.913%│   1313.6│ 1313.61
 11 │ 2.121│ 1.724│ 1.131│  8.846%│   1528.1│ 1528.11
 12 │ 2.190│ 1.896│ 1.363│ 10.652%│   1780.3│ 1780.31
 13 │ 2.276│ 2.071│ 1.609│ 11.947%│   2045.4│ 2045.42
 14 │ 2.353│ 2.244│ 1.882│ 12.404%│   2335.1│ 2335.13
 15 │ 2.414│ 2.409│ 2.195│ 11.733%│   3538.8│ 2654.91
 16 │ 2.449│ 2.560│ 2.561│  9.747%│   5029.7│ 3019.20
 17 │ 2.455│ 2.680│ 3.003│  6.818%│  11470.9│ 3441.96
 18 │ 2.422│ 2.755│ 3.538│  3.681%│  17059.3│ 3934.52
 19 │ 2.376│ 2.742│ 4.195│  1.339%│  66290.6│ 4520.89
 20 │ 1.959│ 2.243│ 4.735│  0.234%│ 223972.0│ 4856.99

Avg win at line length 3: 47.92, 4: 224.59, 5: 911.47

*/

/* RTP DISTRIBUTION: (3.14 billion games)

RtP distribution by upper bound in #bets ('■' = 0.1%):
   1│ 3.567% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 213397143
   2│ 4.887% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 103135598
   3│ 3.446% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 43729572
   4│ 3.529% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 31705188
   5│ 1.824% ■■■■■■■■■■■■■■■■■■ 12552462
   6│ 2.217% ■■■■■■■■■■■■■■■■■■■■■■ 12707709
   7│ 2.846% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 13781282
   8│ 1.508% ■■■■■■■■■■■■■■■ 6272127
   9│ 0.942% ■■■■■■■■■ 3461346
  10│ 1.000% ■■■■■■■■■■ 3287248
  11│ 1.861% ■■■■■■■■■■■■■■■■■■■ 5545415
  12│ 1.484% ■■■■■■■■■■■■■■■ 4037894
  13│ 2.140% ■■■■■■■■■■■■■■■■■■■■■ 5374648
  14│ 1.079% ■■■■■■■■■■■ 2498269
  15│ 0.883% ■■■■■■■■■ 1909236
  16│ 1.141% ■■■■■■■■■■■ 2298602
  17│ 0.797% ■■■■■■■■ 1510995
  18│ 0.830% ■■■■■■■■ 1487776
  19│ 1.080% ■■■■■■■■■■■ 1826303
  20│ 0.675% ■■■■■■■ 1086351
  21│ 0.995% ■■■■■■■■■■ 1520903
  22│ 1.339% ■■■■■■■■■■■■■ 1955684
  23│ 0.951% ■■■■■■■■■■ 1320918
  24│ 1.014% ■■■■■■■■■■ 1355437
  25│ 1.302% ■■■■■■■■■■■■■ 1659803
  26│ 0.842% ■■■■■■■■ 1033825
  27│ 0.796% ■■■■■■■■ 942506
  28│ 0.694% ■■■■■■■ 791184
  29│ 0.688% ■■■■■■■ 757644
  30│ 0.482% ■■■■■ 512484
  31│ 0.748% ■■■■■■■ 768335
  32│ 0.780% ■■■■■■■■ 777203
  33│ 0.751% ■■■■■■■■ 726326
  34│ 0.630% ■■■■■■ 590497
  35│ 0.623% ■■■■■■ 565888
  36│ 0.496% ■■■■■ 438343
  37│ 0.561% ■■■■■■ 482582
  38│ 0.748% ■■■■■■■ 626874
  39│ 0.433% ■■■■ 352849
  40│ 0.346% ■■■ 275111
  41│ 0.439% ■■■■ 339434
  42│ 0.591% ■■■■■■ 447182
  43│ 0.986% ■■■■■■■■■■ 726454
  44│ 0.702% ■■■■■■■ 506379
  45│ 0.447% ■■■■ 314957
  46│ 0.516% ■■■■■ 355194
  47│ 0.613% ■■■■■■ 413833
  48│ 0.405% ■■■■ 267378
  49│ 0.465% ■■■■■ 300852
  50│ 0.496% ■■■■■ 314117
  52│ 0.703% ■■■■■■■ 432810
  54│ 0.732% ■■■■■■■ 432975
  56│ 0.557% ■■■■■■ 318233
  58│ 0.533% ■■■■■ 293193
  60│ 0.443% ■■■■ 235571
  62│ 0.662% ■■■■■■■ 340351
  64│ 0.633% ■■■■■■ 315162
  66│ 0.829% ■■■■■■■■ 401570
  68│ 0.477% ■■■■■ 223895
  70│ 0.567% ■■■■■■ 257156
  72│ 0.433% ■■■■ 191431
  74│ 0.428% ■■■■ 184042
  76│ 0.496% ■■■■■ 207600
  78│ 0.326% ■■■ 132759
  80│ 0.287% ■■■ 114102
  82│ 0.352% ■■■■ 136369
  84│ 0.498% ■■■■■ 188435
  86│ 0.589% ■■■■■■ 217417
  88│ 0.406% ■■■■ 146354
  90│ 0.281% ■■■ 98971
  92│ 0.346% ■■■ 119399
  94│ 0.384% ■■■■ 129471
  96│ 0.305% ■■■ 100589
  98│ 0.420% ■■■■ 135965
 100│ 0.314% ■■■ 99396
 104│ 0.592% ■■■■■■ 182098
 108│ 0.653% ■■■■■■■ 193007
 112│ 0.479% ■■■■■ 136874
 116│ 0.430% ■■■■ 118501
 120│ 0.420% ■■■■ 111677
 124│ 0.552% ■■■■■■ 141763
 128│ 0.472% ■■■■■ 117638
 132│ 0.581% ■■■■■■ 140712
 136│ 0.393% ■■■■ 92148
 140│ 0.382% ■■■■ 86868
 144│ 0.353% ■■■■ 78001
 148│ 0.366% ■■■■ 78641
 152│ 0.399% ■■■■ 83379
 156│ 0.342% ■■■ 69675
 160│ 0.314% ■■■ 62348
 164│ 0.377% ■■■■ 73099
 168│ 0.339% ■■■ 64195
 172│ 0.334% ■■■ 61671
 176│ 0.300% ■■■ 54141
 180│ 0.259% ■■■ 45673
 184│ 0.301% ■■■ 51903
 188│ 0.290% ■■■ 48890
 192│ 0.262% ■■■ 43365
 196│ 0.317% ■■■ 51331
 200│ 0.247% ■■ 39209
 205│ 0.322% ■■■ 49863
 210│ 0.306% ■■■ 46272
 215│ 0.327% ■■■ 48399
 220│ 0.273% ■■■ 39341
 225│ 0.295% ■■■ 41585
 230│ 0.283% ■■■ 39036
 235│ 0.256% ■■■ 34521
 240│ 0.272% ■■■ 35962
 245│ 0.282% ■■■ 36492
 250│ 0.252% ■■■ 31987
 255│ 0.236% ■■ 29382
 260│ 0.230% ■■ 28043
 265│ 0.205% ■■ 24528
 270│ 0.196% ■■ 23057
 275│ 0.196% ■■ 22533
 280│ 0.185% ■■ 20893
 285│ 0.171% ■■ 19018
 290│ 0.165% ■■ 18022
 295│ 0.159% ■■ 17054
 300│ 0.149% ■ 15696
 310│ 0.302% ■■■ 31082
 320│ 0.303% ■■■ 30141
 330│ 0.317% ■■■ 30669
 340│ 0.423% ■■■■ 39606
 350│ 0.401% ■■■■ 36541
 360│ 0.299% ■■■ 26488
 370│ 0.252% ■■■ 21647
 380│ 0.214% ■■ 17913
 390│ 0.192% ■■ 15639
 400│ 0.182% ■■ 14491
 410│ 0.172% ■■ 13350
 420│ 0.152% ■■ 11513
 430│ 0.141% ■ 10432
 440│ 0.142% ■ 10229
 450│ 0.131% ■ 9224
 460│ 0.128% ■ 8836
 470│ 0.120% ■ 8085
 480│ 0.113% ■ 7471
 490│ 0.105% ■ 6788
 500│ 0.096% ■ 6064
 520│ 0.195% ■■ 12030
 540│ 0.201% ■■ 11888
 560│ 0.161% ■■ 9188
 580│ 0.129% ■ 7118
 600│ 0.112% ■ 5954
 620│ 0.107% ■ 5527
 640│ 0.123% ■ 6112
 660│ 0.128% ■ 6175
 680│ 0.172% ■■ 8044
 700│ 0.114% ■ 5190
 720│ 0.086% ■ 3802
 740│ 0.072% ■ 3114
 760│ 0.069% ■ 2894
 780│ 0.070% ■ 2852
 800│ 0.066% ■ 2616
 820│ 0.062% ■ 2398
 840│ 0.060% ■ 2259
 860│ 0.062% ■ 2284
 880│ 0.062% ■ 2230
 900│ 0.063% ■ 2225
 920│ 0.066% ■ 2280
 940│ 0.070% ■ 2348
 960│ 0.069% ■ 2280
 980│ 0.069% ■ 2228
1000│ 0.070% ■ 2221
1050│ 0.189% ■■ 5789
1100│ 0.197% ■■ 5747
1150│ 0.189% ■■ 5291
1200│ 0.186% ■■ 4960
1250│ 0.187% ■■ 4795
1300│ 0.194% ■■ 4768
1350│ 0.188% ■■ 4458
1400│ 0.196% ■■ 4468
1450│ 0.178% ■■ 3930
1500│ 0.150% ■ 3186
1550│ 0.128% ■ 2635
1600│ 0.110% ■ 2202
1650│ 0.095% ■ 1839
1700│ 0.085% ■ 1586
1750│ 0.072% ■ 1310
1800│ 0.062% ■ 1093
1850│ 0.050% ■ 862
1900│ 0.044%  745
1950│ 0.036%  580
2000│ 0.028%  438
2050│ 0.026%  401
2100│ 0.021%  320
2150│ 0.017%  245
2200│ 0.015%  213
2250│ 0.013%  179
2300│ 0.012%  168
2350│ 0.009%  118
2400│ 0.008%  103
2450│ 0.005%  70
2500│ 0.007%  91
2600│ 0.010%  123
2700│ 0.214% ■■ 2523
2800│ 0.478% ■■■■■ 5429
2900│ 0.102% ■ 1134
3000│ 0.026%  277
3100│ 0.020%  203
3200│ 0.014%  141
3300│ 0.017%  164
3400│ 0.020%  185
3500│ 0.022%  200
3600│ 0.023%  204
3700│ 0.024%  205
3800│ 0.032%  268
3900│ 0.030%  241
4000│ 0.040%  318
4100│ 0.043%  335
4200│ 0.041%  312
4300│ 0.044%  324
4400│ 0.040%  291
4500│ 0.045%  318
4600│ 0.055% ■ 380
4700│ 0.048%  323
4800│ 0.046%  305
4900│ 0.047%  306
5000│ 0.050% ■ 318
5250│ 0.219% ■■ 1338
5500│ 0.253% ■■■ 1478
5750│ 0.204% ■■ 1148
6000│ 0.084% ■ 451
6250│ 0.069% ■ 355
6500│ 0.056% ■ 276
6750│ 0.046%  219
7000│ 0.034%  157
7250│ 0.026%  114
7500│ 0.023%  99
7750│ 0.011%  45
8000│ 0.007%  29
8250│ 0.007%  26
8500│ 0.016%  59
8750│ 0.005%  17
9000│ 0.003%  12
9250│ 0.001%  2
9500│ 0.001%  3
9750│ 0.000%  1
 ...│ ...... 0
10k+│ 0.151% ■■ 430

*/

/* WIN COUNTS: (3.14 billion games)

Total number of hits by win combination:
 643151086 │ 3× 1o
 595628608 │ 3× 2♠
 587526380 │ 3× 3♥
 595605556 │ 3× 4♣
 587414636 │ 3× 5♦
 587386180 │ 3× 6♠
 587446052 │ 3× 8♣
 595527190 │ 3× 9♦
 475596587 │ 3× A♠
 646047489 │ 3× J♥
 645897250 │ 3× K♦
 643114184 │ 3× Q♣
  15132991 │ 3×W7♥D
  72148473 │ 4× 1o
  60714598 │ 4× 2♠
  65493361 │ 4× 3♥
  60728381 │ 4× 4♣
  65491135 │ 4× 5♦
  65474431 │ 4× 6♠
  65449198 │ 4× 8♣
  60692068 │ 4× 9♦
  47235552 │ 4× A♠
  69145567 │ 4× J♥
  69094277 │ 4× K♦
  72080058 │ 4× Q♣
    391555 │ 4×W7♥D
   8632236 │ 5× 1o
   7682639 │ 5× 2♠
   8422588 │ 5× 3♥
   7673825 │ 5× 4♣
   8439177 │ 5× 5♦
   8424867 │ 5× 6♠
   8423079 │ 5× 8♣
   7669821 │ 5× 9♦
   5246245 │ 5× A♠
   8817375 │ 5× J♥
   8809008 │ 5× K♦
   8614846 │ 5× Q♣
     13243 │ 5×W7♥D

*/


/* SIMULATION WITH CHEATS ACTIVATED: (10 million games)

Return to player:     4.402940
Base game RtP:        1.471281
Shark Tank RtP:       1.457442
Mega Reels RtP:       1.474217

Hit rate (base game): 0.212531
Standard derivation:  33.707151 (very high)

Feature frequency:  69.056004

Big wins:               70111   (25-49.99 bets)
Huge wins:              38179   (50-99.99 bets)
Enormous wins:          13423  (100-199.99 bets)
Unbelievable wins:       4029  (200-499.99 bets)
Insane wins:              443    (500+ bets)

Mega Reels (with random modes of equal value):
zero wins:               2693        (0)
small wins:             42139  (0.01-24.99 bets)
Big wins:               29368   (25-49.99 bets)
Huge wins:              28776   (50-99.99 bets)
Enormous wins:          22534  (100-199.99 bets)
Unbelievable wins:      15452  (200-499.99 bets)
Insane wins:             3750    (500+ bets)
avg Mega Reels win:    10187.25  (at bet 100)

Shark Tank:
Big wins:               37692   (25-49.99 bets)
Huge wins:              10720   (50-99.99 bets)
Enormous wins:          12744  (100-199.99 bets)
Unbelievable wins:      10655  (200-499.99 bets)
Insane wins:             4146    (500+ bets)
avg Shark Tank win:    10064.51  (at bet 100)
      in normal mode:  7797.02
        in risk mode:  9146.39
       in shark mode:  13253.03

Stats after 144810 Shark Tank entries:
Lines of length 3: 35.28%, 4: 33.82%, 5: 30.89%
entries in normal mode: 48599, risk: 47867, shark: 48344

[$$]│ avg3 │ avg4 │ avg5 │  case  │ case win│ unmult
  3 │ 2.000│ 0.000│ 0.000│  0.322%│     89.6│   89.63
  4 │ 0.927│ 1.183│ 0.000│  0.397%│    309.9│  309.86
  5 │ 1.455│ 0.410│ 0.605│  0.547%│    712.7│  712.71
  6 │ 2.057│ 0.881│ 0.167│  0.790%│    459.1│  459.09
  7 │ 1.773│ 1.149│ 0.373│  1.646%│    683.0│  682.96
  8 │ 1.802│ 1.143│ 0.666│  2.438%│    958.8│  958.77
  9 │ 1.936│ 1.382│ 0.794│  3.157%│   1139.0│ 1139.01
 10 │ 2.093│ 1.571│ 0.921│  4.539%│   1301.1│ 1301.10
 11 │ 2.164│ 1.742│ 1.111│  6.131%│   1516.9│ 1516.89
 12 │ 2.256│ 1.932│ 1.330│  7.871%│   1759.4│ 1759.42
 13 │ 2.347│ 2.136│ 1.569│  9.686%│   2028.9│ 2028.93
 14 │ 2.447│ 2.301│ 1.854│ 11.603%│   2334.1│ 2334.07
 15 │ 2.534│ 2.490│ 2.162│ 12.758%│   3550.6│ 2658.22
 16 │ 2.591│ 2.674│ 2.512│ 12.961%│   5005.9│ 3016.17
 17 │ 2.610│ 2.838│ 2.955│ 11.461%│  11468.6│ 3447.24
 18 │ 2.614│ 2.941│ 3.499│  8.278%│  16986.7│ 3946.99
 19 │ 2.559│ 2.945│ 4.177│  4.355%│  67013.0│ 4562.58
 20 │ 2.156│ 2.409│ 4.793│  1.059%│ 234719.7│ 4976.11

Avg win at line length 3: 47.76, 4: 224.01, 5: 912.24

RtP distribution by upper bound in #bets ('■' = 0.1%):
   1│ 4.393% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 836440
   2│ 6.226% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 418237
   3│ 4.524% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 182797
   4│ 4.782% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 136768
   5│ 2.562% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 56122
   6│ 3.226% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 58895
   7│ 4.255% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 65622
   8│ 2.382% ■■■■■■■■■■■■■■■■■■■■■■■■ 31567
   9│ 1.625% ■■■■■■■■■■■■■■■■ 19004
  10│ 1.745% ■■■■■■■■■■■■■■■■■ 18270
  11│ 3.162% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 30008
  12│ 2.659% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 23040
  13│ 3.872% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 30962
  14│ 2.146% ■■■■■■■■■■■■■■■■■■■■■ 15824
  15│ 1.881% ■■■■■■■■■■■■■■■■■■■ 12953
  16│ 2.378% ■■■■■■■■■■■■■■■■■■■■■■■■ 15270
  17│ 1.820% ■■■■■■■■■■■■■■■■■■ 10995
  18│ 1.909% ■■■■■■■■■■■■■■■■■■■ 10889
  19│ 2.426% ■■■■■■■■■■■■■■■■■■■■■■■■ 13063
  20│ 1.710% ■■■■■■■■■■■■■■■■■ 8762
  21│ 2.371% ■■■■■■■■■■■■■■■■■■■■■■■■ 11538
  22│ 3.117% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 14498
  23│ 2.371% ■■■■■■■■■■■■■■■■■■■■■■■■ 10491
  24│ 2.555% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 10869
  25│ 3.198% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 12990
  26│ 2.252% ■■■■■■■■■■■■■■■■■■■■■■■ 8809
  27│ 2.192% ■■■■■■■■■■■■■■■■■■■■■■ 8264
  28│ 1.981% ■■■■■■■■■■■■■■■■■■■■ 7194
  29│ 2.030% ■■■■■■■■■■■■■■■■■■■■ 7117
  30│ 1.563% ■■■■■■■■■■■■■■■■ 5296
  31│ 2.166% ■■■■■■■■■■■■■■■■■■■■■■ 7088
  32│ 2.278% ■■■■■■■■■■■■■■■■■■■■■■■ 7224
  33│ 2.244% ■■■■■■■■■■■■■■■■■■■■■■ 6912
  34│ 1.969% ■■■■■■■■■■■■■■■■■■■■ 5873
  35│ 1.967% ■■■■■■■■■■■■■■■■■■■■ 5687
  36│ 1.697% ■■■■■■■■■■■■■■■■■ 4775
  37│ 1.844% ■■■■■■■■■■■■■■■■■■ 5050
  38│ 2.340% ■■■■■■■■■■■■■■■■■■■■■■■ 6241
  39│ 1.520% ■■■■■■■■■■■■■■■ 3945
  40│ 1.308% ■■■■■■■■■■■■■ 3309
  41│ 1.505% ■■■■■■■■■■■■■■■ 3708
  42│ 1.945% ■■■■■■■■■■■■■■■■■■■ 4685
  43│ 3.098% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 7272
  44│ 2.248% ■■■■■■■■■■■■■■■■■■■■■■ 5163
  45│ 1.582% ■■■■■■■■■■■■■■■■ 3553
  46│ 1.816% ■■■■■■■■■■■■■■■■■■ 3984
  47│ 2.088% ■■■■■■■■■■■■■■■■■■■■■ 4486
  48│ 1.457% ■■■■■■■■■■■■■■■ 3064
  49│ 1.625% ■■■■■■■■■■■■■■■■ 3349
  50│ 1.767% ■■■■■■■■■■■■■■■■■■ 3563
  52│ 2.653% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 5199
  54│ 2.847% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 5365
  56│ 2.278% ■■■■■■■■■■■■■■■■■■■■■■■ 4142
  58│ 2.223% ■■■■■■■■■■■■■■■■■■■■■■ 3897
  60│ 1.956% ■■■■■■■■■■■■■■■■■■■■ 3314
  62│ 2.575% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 4215
  64│ 2.597% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 4117
  66│ 3.378% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 5206
  68│ 2.079% ■■■■■■■■■■■■■■■■■■■■■ 3104
  70│ 2.465% ■■■■■■■■■■■■■■■■■■■■■■■■■ 3564
  72│ 1.976% ■■■■■■■■■■■■■■■■■■■■ 2782
  74│ 1.964% ■■■■■■■■■■■■■■■■■■■■ 2691
  76│ 2.237% ■■■■■■■■■■■■■■■■■■■■■■ 2982
  78│ 1.636% ■■■■■■■■■■■■■■■■ 2124
  80│ 1.511% ■■■■■■■■■■■■■■■ 1911
  82│ 1.842% ■■■■■■■■■■■■■■■■■■ 2271
  84│ 2.382% ■■■■■■■■■■■■■■■■■■■■■■■■ 2870
  86│ 2.925% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 3436
  88│ 2.124% ■■■■■■■■■■■■■■■■■■■■■ 2441
  90│ 1.575% ■■■■■■■■■■■■■■■■ 1769
  92│ 1.924% ■■■■■■■■■■■■■■■■■■■ 2112
  94│ 2.081% ■■■■■■■■■■■■■■■■■■■■■ 2236
  96│ 1.754% ■■■■■■■■■■■■■■■■■■ 1845
  98│ 2.208% ■■■■■■■■■■■■■■■■■■■■■■ 2276
 100│ 1.836% ■■■■■■■■■■■■■■■■■■ 1852
 104│ 3.563% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 3492
 108│ 3.873% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 3647
 112│ 3.088% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 2809
 116│ 2.793% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 2450
 120│ 2.769% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 2347
 124│ 3.482% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 2851
 128│ 3.022% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 2398
 132│ 3.745% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 2885
 136│ 2.689% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 2008
 140│ 2.650% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1919
 144│ 2.558% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 1801
 148│ 2.589% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 1773
 152│ 2.722% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1813
 156│ 2.629% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 1707
 160│ 2.388% ■■■■■■■■■■■■■■■■■■■■■■■■ 1511
 164│ 2.806% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1732
 168│ 2.485% ■■■■■■■■■■■■■■■■■■■■■■■■■ 1497
 172│ 2.566% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 1509
 176│ 2.249% ■■■■■■■■■■■■■■■■■■■■■■ 1292
 180│ 2.329% ■■■■■■■■■■■■■■■■■■■■■■■ 1308
 184│ 2.420% ■■■■■■■■■■■■■■■■■■■■■■■■ 1329
 188│ 2.309% ■■■■■■■■■■■■■■■■■■■■■■■ 1241
 192│ 2.150% ■■■■■■■■■■■■■■■■■■■■■ 1131
 196│ 2.357% ■■■■■■■■■■■■■■■■■■■■■■■■ 1215
 200│ 2.179% ■■■■■■■■■■■■■■■■■■■■■■ 1100
 205│ 2.574% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 1271
 210│ 2.737% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1319
 215│ 2.654% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1249
 220│ 2.396% ■■■■■■■■■■■■■■■■■■■■■■■■ 1101
 225│ 2.461% ■■■■■■■■■■■■■■■■■■■■■■■■■ 1106
 230│ 2.432% ■■■■■■■■■■■■■■■■■■■■■■■■ 1069
 235│ 2.316% ■■■■■■■■■■■■■■■■■■■■■■■ 996
 240│ 2.316% ■■■■■■■■■■■■■■■■■■■■■■■ 975
 245│ 2.395% ■■■■■■■■■■■■■■■■■■■■■■■■ 987
 250│ 2.335% ■■■■■■■■■■■■■■■■■■■■■■■ 943
 255│ 2.124% ■■■■■■■■■■■■■■■■■■■■■ 841
 260│ 2.106% ■■■■■■■■■■■■■■■■■■■■■ 818
 265│ 2.016% ■■■■■■■■■■■■■■■■■■■■ 768
 270│ 2.052% ■■■■■■■■■■■■■■■■■■■■■ 767
 275│ 2.003% ■■■■■■■■■■■■■■■■■■■■ 735
 280│ 2.001% ■■■■■■■■■■■■■■■■■■■■ 721
 285│ 1.876% ■■■■■■■■■■■■■■■■■■■ 664
 290│ 1.713% ■■■■■■■■■■■■■■■■■ 596
 295│ 1.600% ■■■■■■■■■■■■■■■■ 547
 300│ 1.660% ■■■■■■■■■■■■■■■■■ 558
 310│ 3.055% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1002
 320│ 3.050% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 967
 330│ 3.310% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1019
 340│ 3.613% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 1078
 350│ 3.253% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 943
 360│ 2.812% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 792
 370│ 2.727% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 747
 380│ 2.500% ■■■■■■■■■■■■■■■■■■■■■■■■■ 667
 390│ 2.337% ■■■■■■■■■■■■■■■■■■■■■■■ 607
 400│ 2.413% ■■■■■■■■■■■■■■■■■■■■■■■■ 611
 410│ 2.106% ■■■■■■■■■■■■■■■■■■■■■ 520
 420│ 2.100% ■■■■■■■■■■■■■■■■■■■■■ 506
 430│ 1.909% ■■■■■■■■■■■■■■■■■■■ 449
 440│ 1.771% ■■■■■■■■■■■■■■■■■■ 407
 450│ 1.731% ■■■■■■■■■■■■■■■■■ 389
 460│ 1.528% ■■■■■■■■■■■■■■■ 336
 470│ 1.437% ■■■■■■■■■■■■■■ 309
 480│ 1.397% ■■■■■■■■■■■■■■ 294
 490│ 1.329% ■■■■■■■■■■■■■ 274
 500│ 1.411% ■■■■■■■■■■■■■■ 285
 520│ 2.579% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 506
 540│ 2.332% ■■■■■■■■■■■■■■■■■■■■■■■ 440
 560│ 2.082% ■■■■■■■■■■■■■■■■■■■■■ 379
 580│ 1.818% ■■■■■■■■■■■■■■■■■■ 319
 600│ 1.747% ■■■■■■■■■■■■■■■■■ 296
 620│ 1.572% ■■■■■■■■■■■■■■■■ 258
 640│ 1.404% ■■■■■■■■■■■■■■ 223
 660│ 1.484% ■■■■■■■■■■■■■■■ 228
 680│ 1.669% ■■■■■■■■■■■■■■■■■ 249
 700│ 1.343% ■■■■■■■■■■■■■ 195
 720│ 1.043% ■■■■■■■■■■ 147
 740│ 0.884% ■■■■■■■■■ 121
 760│ 1.005% ■■■■■■■■■■ 134
 780│ 1.094% ■■■■■■■■■■■ 142
 800│ 0.894% ■■■■■■■■■ 113
 820│ 0.826% ■■■■■■■■ 102
 840│ 1.004% ■■■■■■■■■■ 121
 860│ 0.875% ■■■■■■■■■ 103
 880│ 1.107% ■■■■■■■■■■■ 127
 900│ 0.988% ■■■■■■■■■■ 111
 920│ 0.937% ■■■■■■■■■ 103
 940│ 0.939% ■■■■■■■■■ 101
 960│ 0.874% ■■■■■■■■■ 92
 980│ 1.038% ■■■■■■■■■■ 107
1000│ 0.871% ■■■■■■■■■ 88
1050│ 2.453% ■■■■■■■■■■■■■■■■■■■■■■■■■ 239
1100│ 2.785% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 259
1150│ 2.387% ■■■■■■■■■■■■■■■■■■■■■■■■ 212
1200│ 2.535% ■■■■■■■■■■■■■■■■■■■■■■■■■ 216
1250│ 2.618% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 214
1300│ 2.434% ■■■■■■■■■■■■■■■■■■■■■■■■ 191
1350│ 2.968% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 224
1400│ 2.419% ■■■■■■■■■■■■■■■■■■■■■■■■ 176
1450│ 2.546% ■■■■■■■■■■■■■■■■■■■■■■■■■ 179
1500│ 2.154% ■■■■■■■■■■■■■■■■■■■■■■ 146
1550│ 1.919% ■■■■■■■■■■■■■■■■■■■ 126
1600│ 1.417% ■■■■■■■■■■■■■■ 90
1650│ 1.431% ■■■■■■■■■■■■■■ 88
1700│ 1.087% ■■■■■■■■■■■ 65
1750│ 1.258% ■■■■■■■■■■■■■ 73
1800│ 0.797% ■■■■■■■■ 45
1850│ 0.932% ■■■■■■■■■ 51
1900│ 0.617% ■■■■■■ 33
1950│ 0.578% ■■■■■■ 30
2000│ 0.473% ■■■■■ 24
2050│ 0.344% ■■■ 17
2100│ 0.228% ■■ 11
2150│ 0.404% ■■■■ 19
2200│ 0.239% ■■ 11
2250│ 0.178% ■■ 8
2300│ 0.113% ■ 5
2350│ 0.163% ■■ 7
2400│ 0.166% ■■ 7
2450│ 0.024%  1
2500│ 0.049%  2
2600│ 0.128% ■ 5
2700│ 1.196% ■■■■■■■■■■■■ 45
2800│ 2.710% ■■■■■■■■■■■■■■■■■■■■■■■■■■■ 98
2900│ 0.594% ■■■■■■ 21
3000│ 0.175% ■■ 6
3100│ 0.304% ■■■ 10
3200│ 0.251% ■■■ 8
3300│ 0.194% ■■ 6
3400│ 0.301% ■■■ 9
3500│ 0.345% ■■■ 10
3600│ 0.357% ■■■■ 10
3700│ 0.437% ■■■■ 12
3800│ 0.675% ■■■■■■■ 18
3900│ 0.731% ■■■■■■■ 19
4000│ 0.555% ■■■■■■ 14
4100│ 0.365% ■■■■ 9
4200│ 0.706% ■■■■■■■ 17
4300│ 0.725% ■■■■■■■ 17
4400│ 0.956% ■■■■■■■■■■ 22
4500│ 0.936% ■■■■■■■■■ 21
4600│ 1.319% ■■■■■■■■■■■■■ 29
4700│ 0.745% ■■■■■■■ 16
4800│ 1.045% ■■■■■■■■■■ 22
4900│ 0.969% ■■■■■■■■■■ 20
5000│ 0.894% ■■■■■■■■■ 18
5250│ 2.614% ■■■■■■■■■■■■■■■■■■■■■■■■■■ 51
5500│ 3.602% ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ 67
5750│ 2.350% ■■■■■■■■■■■■■■■■■■■■■■■■ 42
6000│ 1.299% ■■■■■■■■■■■■■ 22
6250│ 1.105% ■■■■■■■■■■■ 18
6500│ 1.149% ■■■■■■■■■■■ 18
6750│ 1.450% ■■■■■■■■■■■■■■ 22
7000│ 0.410% ■■■■ 6
7250│ 0.571% ■■■■■■ 8
7500│ 0.734% ■■■■■■■ 10
7750│ 0.304% ■■■ 4
8000│ 0.316% ■■■ 4
8250│ 0.322% ■■■ 4
8500│ 0.167% ■■ 2
8750│ 0.173% ■■ 2
 ...│ ......  0
10k+│ 1.219% ■■■■■■■■■■■■ 11

Total number of hits by win combination:
   2589749 │ 3× 3♥
   2645970 │ 3× 4♣
   2576982 │ 3× 6♠
   2667015 │ 3× 9♦
   2563803 │ 3× ♠2
   2570300 │ 3× ♣8
   2593249 │ 3× ♦5
   2296893 │ 3×A♠CE
   2982491 │ 3×J♥CK
   3015172 │ 3×K♦NG
   3012471 │ 3×QU♣N
   2999689 │ 3×TE♠N
    159333 │ 3×W7♥D
    326293 │ 4× 3♥
    313527 │ 4× 4♣
    330587 │ 4× 6♠
    315880 │ 4× 9♦
    301400 │ 4× ♠2
    336844 │ 4× ♣8
    330016 │ 4× ♦5
    350561 │ 4×A♠CE
    432110 │ 4×J♥CK
    454712 │ 4×K♦NG
    475795 │ 4×QU♣N
    463865 │ 4×TE♠N
      6009 │ 4×W7♥D
     58403 │ 5× 3♥
     54334 │ 5× 4♣
     58024 │ 5× 6♠
     54017 │ 5× 9♦
     49974 │ 5× ♠2
     61404 │ 5× ♣8
     58384 │ 5× ♦5
     65775 │ 5×A♠CE
     97079 │ 5×J♥CK
     98056 │ 5×K♦NG
     99240 │ 5×QU♣N
     98420 │ 5×TE♠N
       197 │ 5×W7♥D

*/

/* just helpful to have flying around over here:
#ifdef _WIN32
#else

#endif
*/
