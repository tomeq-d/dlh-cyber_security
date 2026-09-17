#!/usr/bin/env ruby

require 'json'

# count_user_ids - reads a JSON file and counts how many records
# belong to each userId, then prints the totals sorted by userId
# @path: path to the JSON file to read
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
