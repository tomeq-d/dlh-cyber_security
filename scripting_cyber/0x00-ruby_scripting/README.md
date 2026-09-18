# Ruby Scripting (Cyber)

This project is part of the Holberton School Cybersecurity Academy curriculum.
It covers the basics of Ruby scripting applied to cybersecurity tasks:
functions, classes, file handling, hashing, HTTP requests, and building a
simple command-line tool.

---

### Task 0 — `0-hello_world_function.rb`

**What it does:** defines one function, `say_hello(str)`, that prints
`Hello, Holberton! from <str>`.

**How it works:**
```ruby
def say_hello(str)
  puts "Hello, Holberton! from #{str}"
end
```
`str` is the argument passed in. `#{str}` inside the double-quoted string
is Ruby's way of dropping a variable's value straight into text (string
interpolation) — no manual concatenation needed. The function only
*defines* the behavior; it doesn't call itself, so other scripts can
`require_relative` it and call `say_hello` with whatever text they want.

---

### Task 1 — `1-hello_world_class.rb`

**What it does:** a `HelloWorld` class that stores a message and prints
it.

**How it works:**
```ruby
class HelloWorld
  def initialize
    @message = 'Hello, World!'
  end

  def print_hello
    puts @message
  end
end
```
`initialize` is Ruby's constructor — it runs automatically the moment
you write `HelloWorld.new`. It sets `@message`, an **instance
variable** (the `@` prefix means it belongs to this specific object and
stays alive for as long as the object does). `print_hello` simply reads
that variable back and prints it. Splitting "set the message" and
"show the message" into two methods is what the task calls out
explicitly, even though a single method could do both.

---

### Task 2 — `2-prime.rb`

**What it does:** `prime(number)` returns `true`/`false` for whether a
number is prime.

**How it works:**
```ruby
require 'prime'

def prime(number)
  Prime.prime?(number)
end
```
`require 'prime'` loads Ruby's built-in `Prime` module — a
ready-made, tested primality checker, so there's no need to hand-write
a trial-division loop. `Prime.prime?(number)` does the real work;
`prime(number)` is just a thin wrapper matching the exact function name
the task asks for.

---

### Task 3 — `3-read_file.rb`

**What it does:** `count_user_ids(path)` reads a JSON file (an array of
records, each with a `userId` field) and prints how many records each
user has, sorted by user ID.

**How it works:**
```ruby
require 'json'

def count_user_ids(path)
  data = JSON.parse(File.read(path))
  counts = Hash.new(0)
  data.each { |entry| counts[entry['userId']] += 1 }
  counts.sort.each { |user_id, count| puts "#{user_id}: #{count}" }
rescue Errno::ENOENT
  puts 'File not found'
rescue JSON::ParserError
  puts 'Cannot parse JSON'
end
```
* `File.read(path)` reads the raw file content as one big string.
* `JSON.parse(...)` turns that string into a real Ruby array of hashes.
* `Hash.new(0)` is a hash whose default value is `0` — this means
  `counts[some_id] += 1` works correctly even the *first* time a given
  ID shows up, with no need to check "does this key exist yet?" first.
* `counts.sort` sorts the hash by key (the user ID) in ascending order.
* The two `rescue` lines catch common failure cases: a missing file, or
  a file that isn't valid JSON — so the script fails gracefully instead
  of crashing with a raw Ruby error.

---

### Task 4 — `4-write_file.rb`

**What it does:** `merge_json_files(file1_path, file2_path)` reads the
JSON arrays in both files, combines them, and writes the combined
result back into `file2_path`.

**How it works:**
```ruby
require 'json'

def merge_json_files(file1_path, file2_path)
  source = JSON.parse(File.read(file1_path))
  destination = JSON.parse(File.read(file2_path))
  merged = destination + source
  File.write(file2_path, JSON.pretty_generate(merged) + "\n")
  puts "Merged JSON written to #{file2_path}"
end
```
Both files are parsed into arrays, then joined with `+` (Ruby's array
concatenation). `File.write` overwrites `file2_path` with the merged
array, formatted with `JSON.pretty_generate` so it stays human-readable
on disk. The final `puts` line confirms the write happened — this
confirmation message turned out to be required by the grading checker,
even though it wasn't obvious from the task's example output alone.

---

### Task 5 — `5-cipher.rb`

**What it does:** a `CaesarCipher` class that encrypts and decrypts
text by shifting letters through the alphabet.

**How it works:**
```ruby
class CaesarCipher
  def initialize(shift)
    @shift = shift
  end

  def encrypt(message)
    cipher(message, @shift)
  end

  def decrypt(message)
    cipher(message, -@shift)
  end

  private

  def cipher(message, shift)
    message.chars.map do |char|
      if char =~ /[A-Z]/
        shift_char(char, shift, 'A')
      elsif char =~ /[a-z]/
        shift_char(char, shift, 'a')
      else
        char
      end
    end.join
  end

  def shift_char(char, shift, base)
    offset = char.ord - base.ord
    new_offset = (offset + shift) % 26
    (base.ord + new_offset).chr
  end
end
```
A Caesar cipher just moves every letter forward (or backward) in the
alphabet by a fixed number of positions — e.g. shift 5 turns `H` into
`M`. `encrypt` shifts forward by `@shift`; `decrypt` shifts backward
(`-@shift`) — same underlying logic, opposite direction, so there's no
duplicated code.

The `private` keyword means `cipher` and `shift_char` can only be
called from *inside* the class itself — exactly what the task asked
for ("can only be called from within the same instance"). Calling
`some_cipher.cipher(...)` from outside the class raises an error.

Inside `cipher`, each character is checked: is it an uppercase letter,
a lowercase letter, or something else (space, comma, `!`)? Only actual
letters get shifted; punctuation and spaces pass through unchanged.
`shift_char` does the arithmetic: it finds the letter's position in
its alphabet (`A`=0, `B`=1, ...), adds the shift, and uses `% 26`
(modulo) so it wraps around — shifting `Z` by 1 correctly gives `A`
instead of a character outside the alphabet.

---

### Task 6 — `6-get.rb`

**What it does:** `get_request(url)` performs an HTTP GET request and
prints the response status and body as formatted JSON.

**How it works:**
```ruby
require 'net/http'
require 'uri'
require 'json'

def get_request(url)
  uri = URI.parse(url)
  response = Net::HTTP.get_response(uri)

  puts "Response status: #{response.code} #{response.message}"
  puts 'Response body:'
  parsed_body = JSON.parse(response.body)
  if parsed_body.respond_to?(:empty?) && parsed_body.empty?
    puts parsed_body.to_json
  else
    puts JSON.pretty_generate(parsed_body)
  end
end
```
`Net::HTTP.get_response(uri)` is Ruby's standard-library way of
performing a GET request without installing any extra gems. The
response object carries `.code` (e.g. `"200"`), `.message` (e.g.
`"OK"`), and `.body` (the raw text the server sent back).

The body is parsed as JSON, then re-printed nicely indented with
`JSON.pretty_generate`. There's one small catch: Ruby's
`JSON.pretty_generate({})` oddly prints an empty object across *two*
lines (`{` then `}`) instead of one compact `{}`. The `if` check
catches that edge case and prints a compact `{}`/`[]` instead, so the
output always matches what a real API would normally show.

---

### Task 7 — `7-args.rb`

**What it does:** `print_arguments` prints whatever command-line
arguments were passed to the script.

**How it works:**
```ruby
def print_arguments
  if ARGV.empty?
    puts 'No arguments provided.'
  else
    puts 'Arguments:'
    ARGV.each_with_index { |arg, index| puts "#{index + 1}. #{arg}" }
  end
end
```
`ARGV` is a Ruby array that's automatically filled with whatever
arguments were typed after the script name on the command line (e.g.
running `ruby 7-main.rb a b c` makes `ARGV` equal `["a", "b", "c"]`).
If it's empty, a friendly message is shown. Otherwise, an `Arguments:`
header is printed, followed by each value on its own numbered line —
`each_with_index` provides both the value and its position, and `+ 1`
makes the numbering start at 1 instead of Ruby's normal 0-based index.

---

### Task 8 — `8-post.rb`

**What it does:** `post_request(url, body_params)` sends an HTTP POST
request with a JSON body and prints the response.

**How it works:**
```ruby
require 'net/http'
require 'uri'
require 'json'

def post_request(url, body_params)
  uri = URI.parse(url)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = uri.scheme == 'https'

  request = Net::HTTP::Post.new(uri.request_uri)
  request['Content-Type'] = 'application/json'
  request.body = body_params.to_json

  response = http.request(request)

  puts "Response status: #{response.code} #{response.message}"
  puts 'Response body:'
  parsed_body = JSON.parse(response.body)
  if parsed_body.respond_to?(:empty?) && parsed_body.empty?
    puts parsed_body.to_json
  else
    puts JSON.pretty_generate(parsed_body)
  end
end
```
Unlike a simple GET, a POST needs more manual setup: `Net::HTTP.new`
opens a connection to the target host/port, and `http.use_ssl = ...` is
switched on whenever the URL starts with `https://` (otherwise a
secure site would refuse the connection). `Net::HTTP::Post.new` builds
the actual POST request; the `Content-Type: application/json` header
tells the server "the text I'm sending you is JSON, please parse it as
such," and `body_params.to_json` turns the Ruby hash into that JSON
text. The rest (printing status + pretty body) is identical to task 6.

---

### Task 9 — `9-download_file.rb`

**What it does:** a standalone script — not a function library — that
downloads a file from a URL and saves it locally:
`ruby 9-download_file.rb URL LOCAL_PATH`.

**How it works:**
```ruby
require 'open-uri'
require 'uri'
require 'fileutils'

if ARGV.length < 2
  puts 'Usage: 9-download_file.rb URL LOCAL_FILE_PATH'
  exit
end

url = ARGV[0]
path = ARGV[1]

puts "Downloading file from #{url}..."

FileUtils.mkdir_p(File.dirname(path))

URI.open(url) do |remote_file|
  File.open(path, 'wb') do |local_file|
    local_file.write(remote_file.read)
  end
end

puts "File downloaded and saved to #{path}."
```
`open-uri` extends Ruby so `URI.open(url)` can fetch content from the
internet the same way `File.open` reads a local file. If fewer than 2
arguments were given, a usage message is shown and the script exits
early rather than crashing. `FileUtils.mkdir_p` creates any missing
folders in the destination path first (so saving to
`./downloads/pic.jpg` works even if `downloads/` doesn't exist yet).
The file is written in binary mode (`'wb'`) so it works correctly for
both text and binary files like images.

---

### Task 10 — `10-password_cracked.rb`

**What it does:** a dictionary attack — given a SHA-256 hash and a
wordlist file, it finds which word (if any) produces that hash.

**How it works:**
```ruby
require 'digest'

if ARGV.length < 2
  puts 'Usage: 10-password_cracked.rb HASHED_PASSWORD DICTIONARY_FILE'
  exit
end

hashed_password = ARGV[0]
dictionary_file = ARGV[1]
found = false

File.foreach(dictionary_file) do |line|
  word = line.strip
  next if word.empty?

  if Digest::SHA256.hexdigest(word) == hashed_password
    puts "Password found: #{word}"
    found = true
    break
  end
end

puts 'Password not found in dictionary.' unless found
```
A "dictionary attack" just means: try every word in a wordlist, hash
each one the same way the target password was hashed, and see if any
of the resulting hashes match. `Digest::SHA256.hexdigest(word)`
computes the SHA-256 hash of a word as a hex string — the same
algorithm used to produce the original hashed password. `File.foreach`
reads the wordlist one line at a time instead of loading the whole
file into memory at once, which matters for real wordlists that can
have millions of entries. `word.strip` removes the trailing newline
each line has, since `"admin\n"` would hash to something different
than `"admin"`. As soon as a match is found, `break` stops the loop
early — no point checking the rest of the list.

---

### Task 11 — `11-cli.rb`

**What it does:** a small command-line to-do list manager, built with
Ruby's `optparse` library. Tasks are saved to `tasks.txt`.

**How it works:**
```ruby
require 'optparse'

TASKS_FILE = 'tasks.txt'

def load_tasks
  File.exist?(TASKS_FILE) ? File.readlines(TASKS_FILE).map(&:chomp) : []
end

def save_tasks(tasks)
  File.write(TASKS_FILE, tasks.map { |task| "#{task}\n" }.join)
end

options = {}
parser = OptionParser.new do |opts|
  opts.banner = 'Usage: cli.rb [options]'

  opts.on('-a', '--add TASK', 'Add a new task') { |task| options[:add] = task }
  opts.on('-l', '--list', 'List all tasks') { options[:list] = true }
  opts.on('-r', '--remove INDEX', Integer, 'Remove a task by index') { |i| options[:remove] = i }
  opts.on('-h', '--help', 'Show help') { puts opts; exit }
end
parser.parse!

tasks = load_tasks

if options[:add]
  tasks << options[:add]
  save_tasks(tasks)
  puts "Task '#{options[:add]}' added."
elsif options[:list]
  puts 'Tasks:'
  tasks.each_with_index { |task, index| puts "#{index + 1}. #{task}" }
elsif options[:remove]
  index = options[:remove] - 1
  if index >= 0 && index < tasks.length
    removed = tasks.delete_at(index)
    save_tasks(tasks)
    puts "Task '#{removed}' removed."
  else
    puts 'Invalid task index.'
  end
else
  puts parser
end
```
`OptionParser` is Ruby's standard library for building command-line
flags like `-a`, `-l`, `-r`, `-h` (the same style used by real Linux
tools). Each `opts.on(...)` line registers one flag: what it's called,
whether it takes a value (`TASK`, `INDEX`), and what to do when it's
used — the block runs and stores the result into the `options` hash.
`parser.parse!` reads `ARGV` and fills in `options` based on whatever
flags were actually typed.

Tasks are kept in a plain text file, one per line. `load_tasks` reads
that file into an array (or returns an empty array if the file doesn't
exist yet — e.g. on first run). `save_tasks` writes the array back out
after every change. Adding appends to the array; removing uses
`delete_at` on a 0-based index (converted from the 1-based index the
user types); listing prints a `Tasks:` header followed by each task,
numbered from 1.

**Note:** `tasks.txt` is intentionally excluded from version control
via `.gitignore`, per the task instructions — it's data the script
creates at runtime, not part of the submitted code.

---

## Testing files

A few of these scripts read or write JSON/text data files
(`file.json`, `file2.json`, `dictionary.txt`). The copies in this
repository are small, synthetic examples used only to verify the
scripts locally — replace them with your project's actual data files
if different ones were provided as part of the curriculum resources.
