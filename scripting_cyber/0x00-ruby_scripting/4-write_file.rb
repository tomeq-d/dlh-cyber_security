#!/usr/bin/env ruby

require 'json'

# merge_json_files - merges the JSON array from file1_path into the
# JSON array stored in file2_path, then writes the combined result
# back to file2_path
# @file1_path: path to the JSON file whose records get merged in
# @file2_path: path to the JSON file that receives the merged records
def merge_json_files(file1_path, file2_path)
  source = JSON.parse(File.read(file1_path))
  destination = JSON.parse(File.read(file2_path))
  merged = destination + source
  File.write(file2_path, JSON.pretty_generate(merged) + "\n")
end
