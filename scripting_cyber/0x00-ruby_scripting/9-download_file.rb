#!/usr/bin/env ruby

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
