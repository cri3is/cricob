import argparse
import itertools
import string
import sys
import math
from datetime import datetime

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
	sys.exit()

non_mode_args = {"output", "min_len", "max_len", "base_chars"}
active_modes = [
	value for key, value in vars(args).items()
	if key not in non_mode_args and value
]

custom_range_mode = args.min_len is not None and args.max_len is not None and args.base_chars is not None

if not active_modes and not custom_range_mode:
	print("[!] Error: No operational mode selected.\n")
	parser.print_help()
	sys.exit()

mask_map = {
	"?d": string.digits, #0-9
	"?l": string.ascii_lowercase, #a-z
	"?u": string.ascii_uppercase, #A-Z
	"?s": "!@#$%^&*",
}

seen = set()
output_file = open(args.output, "w", encoding="utf-8") if args.output else None

def unique_print(text):
	if text not in seen:
		seen.add(text)
		if output_file:
			output_file.write(text + "\n")
		else:
			print(text)

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
		choice = input("[!] Generation count is above 500 000. Do you want to continue? (y/n): ").strip().lower()
		if choice != "y":
			print("[-] Operation is canceled by user")
			if output_file:
				output_file.close()
			sys.exit(0)

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
		user_pattern_input = input("Type pattern (example: ?uadmin?s): ").strip()

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
		user_name = input("Name: ").strip()

		if not user_name:
			break

		if user_name.isdigit():
			print("[!] The name can't be a number")
			continue

		break

	while True:
		user_surname = input("Surname: ")

		if not user_surname:
			break

		if user_surname.isdigit():
			print("[!] The surname can't be a number")
			continue

		break

	user_username = input("Username: ")
	user_company_name = input("Company name: ")
	user_pet_name = input("Pet name: ")

	while True:
		user_birthday = input("Birthday (DD.MM.YYYY): ").strip()

		if not user_birthday:
			user_birthday_dot = ""
			user_birthday_clean = ""
			user_birthday_year = ""
			user_birthday_day_month_dot = ""
			user_birthday_day_month = ""
			break

		parsed_data = None
			
		try:
			parsed_data = datetime.strptime(user_birthday, "%d.%m.%Y")
		except ValueError:
			try:
				parsed_data = datetime.strptime(user_birthday, "%d%m%Y")
			except ValueError:
				try:
					parsed_data = datetime.strptime(user_birthday, "%Y")
				except ValueError:
					print("[!] Wrong birthday format. Use DD.MM.YYYY (DDMMYYYY; YYYY)")
					continue

		user_birthday_dot = parsed_data.strftime("%d.%m.%Y")
		user_birthday_clean = parsed_data.strftime("%d%m%Y")
		user_birthday_year = parsed_data.strftime("%Y")
		user_birthday_day_month_dot = parsed_data.strftime("%d.%m")
		user_birthday_day_month = parsed_data.strftime("%d%m")
		break
	

	while True:
		user_favourite_number = input("Favourite number: ")

		if not user_favourite_number:
			break

		if not user_favourite_number.isdigit():
			print("[!] This field only accepts number")
			continue

		break

	leet_mode = input("Enable leet mode? (yes/no): ").strip().lower()

	print()

	base_items = [user_name, user_surname, user_pet_name, user_username, user_company_name, user_favourite_number]
	base_items = [item for item in base_items if item]

	birthday_items = [user_birthday_dot, user_birthday_year, user_birthday_clean, user_birthday_day_month, user_birthday_day_month_dot]
	birthday_items = [item for item in birthday_items if item]
	birthday_items_without_full_birthday = [user_birthday_year, user_birthday_day_month, user_birthday_day_month_dot]
	birthday_items_without_full_birthday = [item for item in birthday_items_without_full_birthday if item]

	items = base_items + birthday_items
	items_for_leet = base_items + birthday_items_without_full_birthday

	years = [year for year in range(1950, 2027)]
	special_symbols = ["!", "@", "$", "%", "^", "&", "*"]
	years_count = len(range(1950, 2027))
	symbols_count = 7

	estimated_variations = (
		len(items) +
		(len(items) ** 2) +
		(len(items) * years_count * 2) +
		(len(items) * symbols_count) +
		(len(items)**2 * years_count * 2) +
		(len(items)**2 * symbols_count)
	)

	if leet_mode == "yes":
		leet_count = len(base_items) + (len(items) ** 2)
		estimated_variations += leet_count * 4

	confirm_generation(estimated_variations)
	print()

	combinations = []
	combinations_for_leet = []

	for item in items:
		unique_print(item)

	for combination in itertools.product(items, repeat=2):
		combinations.append("".join(combination))

	for combination in itertools.product(items_for_leet, repeat=2):
		combinations_for_leet.append("".join(combination))

	if user_name and user_birthday:
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
	print(f"\n[+] Wordlist successfully saved to {args.output}. Total unique combinations: {len(seen)}")