#!/usr/bin/env ruby

# print_arguments - prints each command-line argument passed to the
# script, numbered from 1, or a message if none were provided
def print_arguments
  if ARGV.empty?
    puts 'No arguments provided.'
  else
    puts 'Arguments:'
    ARGV.each_with_index { |arg, index| puts "#{index + 1}. #{arg}" }
  end
end
