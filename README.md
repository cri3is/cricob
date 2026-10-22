# cricob

"cricob" - Wordlist Generator 🔑


Interactive wordlist generator written in Python. Designed for security testing, penetration testing, and OSINT-based password auditing.


🚀 Features

-Interactive Mode (-i/--interactive): Builds customized wordlists based on target personal info (name, surname, birthday, pet name, etc.), year ranges, special symbols, and 
optional Leet speak (l33t) variations.

Example:

python cricob.py -i

-Pattern Mode (-p/--pattern): Generates wordlists using custom masks ('?d', '?l', '?u', '?s'). Where '?d': 1-9; '?l': a-z; '?u': A-Z; ?s: !@#$%^&*

Example:

python cricob.py -p ?dadmin?s

-Custom Range Mode: Generates combinations based on custom character sets and a length range.

Example:

python cricob.py 4 4 123456890

pythoh cricob.py 1 3 Abc123

-Smart Deduplication & Safety Checks: Automatically filters out duplicate entries and prompts a warning if the estimated combination count exceeds 500,000 to prevent accidental system overload.

-File Output (-o/--output): Saves the generated wordlist directly to a file(default wordlist.txt) or prints it to the console.

Example:

python cricob.py -i -o wordlist.txt


📋 Requirements

Python 3.x (No external third-party libraries required; uses only standard Python libraries).


⚙️ Installation & Usage

Clone the repository and run the script with Python:

```bash
https://github.com/cri3is/cricob.git
cd cricob
python cricob.py -h
