import argparse
import itertools
import string
import sys
import math
import re
from datetime import datetime
import signal

EXIT_OK = 0
EXIT_CANCELLED = 1
EXIT_USAGE = 2
EXIT_INTERRUPTED = 130

parser = argparse.ArgumentParser(description="Wordlist Generator, with interactive and default modes")

parser.add_argument("-i", "--interactive", action="store_true", help="Interactive Mode")
parser.add_argument("-o", "--output", nargs="?", const="wordlist.txt", default=None, help="Path to save generated combinations")
parser.add_argument("-p", "--pattern", nargs="?", const=True, default=False, help='Pattern Mode. ?d: 1-9; ?l: a-z; ?u: A-Z; ?s: "!@#$%%^&*"')

parser.add_argument("min_len", nargs="?", type=int, help="Minimal length for custom range")
parser.add_argument("max_len", nargs="?", type=int, help="Maximal length for custom range")
parser.add_argument("base_chars", nargs="?", type=str, help="Base characters for custom range")

args = parser.parse_args()

if len(sys.argv) == 1:
	parser.print_help()
	sys.exit(EXIT_OK)

selected_modes = []

if args.interactive:
	selected_modes.append("interactive (-i)")

if args.pattern:
	selected_modes.append("pattern (-p)")

custom_range_args = [
	args.min_len is not None,
	args.max_len is not None,
	args.base_chars is not None,
]

if any(custom_range_args) and not all(custom_range_args):
	print("[!] Error: custom range mode needs all three values: min_len max_len base_chars", file=sys.stderr)
	print("    Example: python cricob.py 1 3 abc", file=sys.stderr)
	sys.exit(EXIT_USAGE)

custom_range_mode = all(custom_range_args)

if custom_range_mode:
	selected_modes.append("custom range")

if not selected_modes:
	print("[!] Error: No operational modes selected.\n", file=sys.stderr)
	parser.print_help()
	sys.exit(EXIT_USAGE)

if len(selected_modes) > 1:
	print(f"[!] Error: modes cannot be combined, got {', '.join(selected_modes)}", file=sys.stderr)
	print("    Choose exactly one of: -i, -p or positional 'min_len max_len base_chars'.", file=sys.stderr)
	sys.exit(EXIT_USAGE)

if custom_range_mode:
	if args.min_len < 0:
		print("[!] Error: min_len cannot be negative", file=sys.stderr)
		sys.exit(EXIT_USAGE)
	if args.min_len > args.max_len:
		print("[!] Error: min_len cannot be greater than max_len", file=sys.stderr)
		sys.exit(EXIT_USAGE)
	if not args.base_chars:
		print("[!] Error: base_chars cannot be empty", file=sys.stderr)
		sys.exit(EXIT_USAGE)

mask_map = {
	"?d": string.digits, #0-9
	"?l": string.ascii_lowercase, #a-z
	"?u": string.ascii_uppercase, #A-Z
	"?s": "!@#$%^&*",
}

output_file = None

def open_output():
	global output_file

	if output_file is not None or not args.output:
		return output_file

	try:
		output_file = open(args.output, "w", encoding="utf-8", newline="\n")
	except OSError as error:
		print(f"[!] Cannot create output file '{args.output}': {error}", file=sys.stderr)
		sys.exit(EXIT_USAGE)

	return output_file

def finish(code):
	if output_file:
		try:
			output_file.close()
		except OSError:
			pass
	sys.exit(code)

def ask(prompt):
	try:
		return input(prompt)
	except EOFError:
		print("\n[!] Input closed (EOF), exiting.", file=sys.stderr)
		finish(EXIT_INTERRUPTED)
	except KeyboardInterrupt:
		print("\n[-] Interrupted by user.", file=sys.stderr)
		finish(EXIT_INTERRUPTED)

def handle_interrupt(signum, frame):
	print("\n[-] Interrupted by user.", file=sys.stderr)
	finish(EXIT_INTERRUPTED)

signal.signal(signal.SIGINT, handle_interrupt)

MAX_DEDUP_ENTRIES = 2_000_000

seen_hashes = set()
written_count = 0
duplicate_count = 0
dedup_disabled = False

def unique_print(text, dedup=True):
	global dedup_disabled, written_count, duplicate_count

	if dedup and not dedup_disabled:
		key = hash(text)
		if key in seen_hashes:
			duplicate_count += 1
			return
		if len(seen_hashes) >= MAX_DEDUP_ENTRIES:
			dedup_disabled = True
			print(f"\n[!] Dedup limit reached ({MAX_DEDUP_ENTRIES}). Duplicates are no longer filtered.", file=sys.stderr)
		else:
			seen_hashes.add(key)

	written_count += 1
	if written_count % 1_000_000 == 0:
		print(f"[*] {written_count} lines generated...", file=sys.stderr)


	if args.output and output_file is None:
		open_output()

	if output_file:
		output_file.write(text + "\n")
	else:
		try:
			print(text)
		except BrokenPipeError:
			finish(EXIT_OK)

def pattern_func(pattern_str):
	options = []
	i = 0
	while i < len(pattern_str):
		if pattern_str[i] == "?" and i + 1 < len(pattern_str):
			token = pattern_str[i:i+2]
			if token in mask_map:
				options.append(list(mask_map[token]))
				i += 2
				continue
		options.append([pattern_str[i]])
		i += 1
	return options

def confirm_generation(estimated_count):
	print(f"\n[?] Warning! Estimated combinations count: ~{estimated_count}")
	if estimated_count > 500000:
		choice = ask("[!] Generation count is above 500 000. Do you want to continue? (y/n): ").strip().lower()
		if choice != "y":
			print("[-] Operation is canceled by user")
			finish(EXIT_CANCELLED)


if custom_range_mode:
	print(f"[+] Custom range mode: length from {args.min_len} to {args.max_len} using '{args.base_chars}'\n")
	
	total_combos = sum(len(args.base_chars) ** length for length in range(args.min_len, args.max_len + 1))

	confirm_generation(total_combos)
	print()

	for length in range(args.min_len, args.max_len + 1):
		for combo in itertools.product(args.base_chars, repeat=length):
			unique_print("".join(combo))

if args.pattern:
	if isinstance(args.pattern, str):
		user_pattern_input = args.pattern
	else:
		user_pattern_input = ask("Type pattern (example: ?uadmin?s): ").strip()

	print(f"[+] Using pattern: {user_pattern_input}\n")

	user_pattern_options = pattern_func(user_pattern_input)

	total_combos = math.prod(len(opt) for opt in user_pattern_options)
	confirm_generation(total_combos)
	print()

	for combo in itertools.product(*user_pattern_options):
		unique_print("".join(combo))

if args.interactive:
	print("Interactive mode\n")

	while True:
		user_name = ask("Name: ").strip()

		if not user_name:
			break

		if user_name.isdigit():
			print("[!] The name can't be a number")
			continue

		break

	while True:
		user_surname = ask("Surname: ")

		if not user_surname:
			break

		if user_surname.isdigit():
			print("[!] The surname can't be a number")
			continue

		break

	user_username = ask("Username: ")
	user_company_name = ask("Company name: ")
	user_pet_name = ask("Pet name: ")

	BIRTHDAY_PATTERNS = (
		re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$"),
		re.compile(r"^(\d{2})(\d{2})(\d{4})$"),
		re.compile(r"^(\d{4})$"),
	)

	MIN_BIRTHDAY_YEAR = 1900
	MAX_BIRTHDAY_YEAR = datetime.now().year

	user_birthday_dot = ""
	user_birthday_clean = ""
	user_birthday_year = ""
	user_birthday_day_month_dot = ""
	user_birthday_day_month = ""

	while True:
		raw_birthday = ask("Birthday (DD.MM.YYYY): ").strip()

		if not raw_birthday:
			break

		match = None
		for pattern in BIRTHDAY_PATTERNS:
			match = pattern.match(raw_birthday)
			if match:
				break

		if match is None:
			print("[!] Wrong birthday format. Use DD.MM.YYYY, DDMMYYYY or YYYY")
			continue

		groups = match.groups()

		if len(groups) == 1:
			year = int(groups[0])
			if not (MIN_BIRTHDAY_YEAR <= year <= MAX_BIRTHDAY_YEAR):
				print(f"[!] Year must be between {MIN_BIRTHDAY_YEAR} and {MAX_BIRTHDAY_YEAR}")
				continue
			user_birthday_year = f"{year:04d}"
			break

		day, month, year = int(groups[0]), int(groups[1]), int(groups[2])

		if not (MIN_BIRTHDAY_YEAR <= year <= MAX_BIRTHDAY_YEAR):
			print(f"[!] Year must be between {MIN_BIRTHDAY_YEAR} and {MAX_BIRTHDAY_YEAR}")
			continue

		try:
			parsed_data = datetime(year, month, day)
		except ValueError:
			print("[!] This data does not exist (check day and month)")
			continue

		user_birthday_dot = parsed_data.strftime("%d.%m.%Y")
		user_birthday_clean = parsed_data.strftime("%d%m%Y")
		user_birthday_year = parsed_data.strftime("%Y")
		user_birthday_day_month_dot = parsed_data.strftime("%d.%m")
		user_birthday_day_month = parsed_data.strftime("%d%m")
		break

	while True:
		user_favourite_number = ask("Favourite number: ")

		if not user_favourite_number:
			break

		if not user_favourite_number.isdigit():
			print("[!] This field only accepts number")
			continue

		break

	leet_mode = ask("Enable leet mode? (yes/no): ").strip().lower()

	print()

	base_items = [user_name, user_surname, user_pet_name, user_username, user_company_name, user_favourite_number]
	base_items = [item for item in base_items if item]

	birthday_items = [user_birthday_dot, user_birthday_year, user_birthday_clean, user_birthday_day_month, user_birthday_day_month_dot]
	birthday_items = [item for item in birthday_items if item]
	birthday_items_without_full_birthday = [user_birthday_year, user_birthday_day_month, user_birthday_day_month_dot]
	birthday_items_without_full_birthday = [item for item in birthday_items_without_full_birthday if item]

	items = base_items + birthday_items
	items_for_leet = base_items + birthday_items_without_full_birthday

	years = list(range(1950, datetime.now().year + 1))
	special_symbols = ["!", "@", "$", "%", "^", "&", "*"]

	years_count = len(years)
	symbols_count = len(special_symbols)
	birthday_count = len(birthday_items)

	leet_map = {
		'a': ['a', '@', '4'],
		'e': ['e', '3'],
		'i': ['i', '1', '!'],
		'o': ['o', '0', '()'],
		's': ['s', '$', '5'],
		't': ['t', '7'],
		'b': ['b', '8'],
		'g': ['g', '9'],
		'z': ['z', '2'],
		'l': ['l', '1'],
		'1': ['1', '!', 'i', 'l', '|'],
		'2': ['2', '@'],
		'3': ['3', 's', 'e'],
		'4': ['4', '$'],
		'5': ['5', '%'],
	}

	def leet_variations_count(word):
		count = 1
		for char in word:
			options = leet_map.get(char.lower())
			if options:
				count *= len(options)
		return count

	combinations = ["".join(pair) for pair in itertools.product(items, repeat=2)]
	combinations_for_leet = ["".join(pair) for pair in itertools.product(items_for_leet, repeat=2)]

	estimated_variations = (
		len(items)
		+ len(combinations)
		+ len(items) * years_count * 2
		+ len(combinations) * years_count * 2
		+ len(combinations) * symbols_count 
	)

	if user_name and user_birthday_year:
		estimated_variations += symbols_count

	if user_name and birthday_items:
		estimated_variations += 3 * birthday_count

	estimated_variations += 2 * birthday_count * symbols_count

	if leet_mode == "yes":
		estimated_variations += sum(
			leet_variations_count(word) for word in base_items + combinations_for_leet
		)

	confirm_generation(estimated_variations)
	print()

	for item in items:
		unique_print(item)


	if user_name and user_birthday_year:
		for symbol in special_symbols:
			unique_print(f"{user_name}{user_birthday_year}{symbol}")

	for words_common in combinations:
		unique_print(words_common)

	for item in items:
		for year in years:
			words_years = f"{item}{year}"
			unique_print(words_years)

	for item in items:
		for year in years:
			words_years_at_start = f"{year}{item}"
			unique_print(words_years_at_start)

	if user_name and birthday_items:
		for b_item in birthday_items:
			unique_print(f"{user_name}{b_item}")
			unique_print(f"{user_name}.{b_item}")
			unique_print(f"{user_name}_{b_item}")

	for b_item in birthday_items:
		for symbol in special_symbols:
			unique_print(f"{b_item}{symbol}")
			unique_print(f"{symbol}{b_item}")

	for words_common in combinations:
		for year in years:
			words_common_years = f"{words_common}{year}"
			unique_print(words_common_years)

	for words_common in combinations:
		for year in years:
			words_common_years_at_start = f"{year}{words_common}"
			unique_print(words_common_years_at_start)

	for words_symbols_for in combinations:
		for symbol in special_symbols:
			words_symbols = f"{words_symbols_for}{symbol}"
			unique_print(words_symbols)

	if leet_mode == "yes":
		for word in base_items + combinations_for_leet:
			options = []
			for char in word:
				lower_char = char.lower()
				if lower_char in leet_map:
					options.append(leet_map[lower_char])
				else:
					options.append([char])

			for leet_variant in itertools.product(*options):
				unique_print("".join(leet_variant))

if output_file:
	output_file.close()
	print(f"\n[+] Wordlist saved to {args.output}. Total lines: {written_count} (duplicates skipped: {duplicate_count})")
